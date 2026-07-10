"""R13 raw-metric re-export for Prop 3 (raw vs scale-aligned floors and crossings).

Background (R13 metric re-audit, paper_draft/REVIEWS/GPT_R13_THEORY_PREWORK/
04_C0_METRIC_REAUDIT.md): the constant stored as ``C0_pipeline`` in
``results/prop3_nofreeparam_r1/prop3_constants.csv`` is a SCALE-ALIGNED
fixed-design floor (``N * e_align`` with the least-squares alignment of
``run_mechanism_m1.object_metrics``), whereas the raw reconstruction identity
of Appendix F (F.2/F.9) requires the RAW floor ``N * ||T_hat - T||^2 / ||T||^2``.
The raw/aligned floor ratio (median ~1.5399) almost exactly explains the
previously reported factor ~1.54 between the Prop-3 skeleton prediction and the
observed aligned crossings; it is a metric mismatch, not an O(Delta^3) effect.

This runner derives the raw quantities FROM THE SAME deterministic setup and
THE SAME OU gain paths as the authoritative Prop-3 run (no new physics, no new
randomness): objects/basis/seed identical to run_prop3_boundary.py, OU channel
seeds ``9000 + seed_idx`` identical to the dense grid. It writes a NEW
provenance-bearing result directory (default ``results/prop3_raw_metric_r1``)
and does NOT touch ``results/prop3_nofreeparam_r1``.

Outputs
-------
prop3_raw_constants.csv        per-object aligned floor, raw floor, ratio,
                               and the centered-moment prediction K+beta4-2
prop3_raw_scan.csv             per (arm, sigma_a, rho, object) seed-mean
                               aligned and raw relMSE curves (pair arm and
                               oracle-gain random arm)
aligned_reproduction_check.csv regenerated aligned pair/oracle curves versus
                               the published dense grid (phase_scan.csv)
prop3_raw_skeleton_test.csv    raw-vs-raw crossings against the raw-floor
                               skeleton prediction rho* = -log(1 - Q_raw)
prop3_raw_summary.json         headline numbers (floor ranges, ratio median,
                               crossing counts, median/max factors)
run_manifest.json              schema-v2 provenance manifest (output_dir-aware)

Usage:
  python run_prop3_raw_metric_export.py            # full export (~ minutes, CPU)
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from run_mechanism_m1 import make_synthetic_objects, object_metrics
from src.basis import basis_frame_budget, make_basis
from src.mechanisms import apply_correction, make_multiplicative_channel
from src.paper_experiments import build_run_manifest

ROOT = Path(__file__).resolve().parent
GRID_RHOS = [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0]
GRID_SIGMAS = [0.05, 0.10, 0.15, 0.30, 0.50]
CONFIG_SEED = 20240708  # config.yaml `seed`, used by the authoritative Prop-3 run
IMAGE_SIZE = 32
NUM_OBJECTS = 10
NUM_SEEDS = 5


def raw_rel_mse(reconstruction: torch.Tensor, target: torch.Tensor) -> float:
    """Raw (unaligned) relative MSE ||T_hat - T||^2 / ||T||^2 in float64."""
    x_hat = reconstruction.reshape(-1).detach().cpu().to(dtype=torch.float64)
    x = target.reshape(-1).detach().cpu().to(dtype=torch.float64)
    return float((x_hat - x).pow(2).sum() / x.pow(2).sum().clamp_min(1.0e-12))


def first_crossing(rhos: np.ndarray, margin: np.ndarray) -> tuple[float, str]:
    """First rho with margin >= 0, log-rho interpolation (dense-grid convention)."""
    if margin[0] >= 0:
        return float(rhos[0]), "left_censored"
    for i in range(len(rhos) - 1):
        if margin[i] < 0.0 <= margin[i + 1]:
            lo, hi = math.log10(rhos[i]), math.log10(rhos[i + 1])
            frac = (0.0 - margin[i]) / (margin[i + 1] - margin[i])
            return float(10 ** (lo + frac * (hi - lo))), "observed"
    return float("nan"), "not_reached"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase-dir", type=Path,
                        default=Path("results/m2_hadamard_order_dense_r1_merged"))
    parser.add_argument("--output-dir", type=Path,
                        default=Path("results/prop3_raw_metric_r1"))
    args = parser.parse_args()

    phase_dir = args.phase_dir if args.phase_dir.is_absolute() else ROOT / args.phase_dir
    out_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    print("[1/4] deterministic floors: aligned vs raw ...", flush=True)
    num_pixels = IMAGE_SIZE * IMAGE_SIZE
    frame_budget, _ = basis_frame_budget(num_pixels)
    n = float(frame_budget)
    objects = make_synthetic_objects(NUM_OBJECTS, IMAGE_SIZE, CONFIG_SEED)
    basis_random = make_basis("random_uniform", num_pixels=num_pixels,
                              num_frames=frame_budget, seed=CONFIG_SEED,
                              reconstruction="correlation")
    basis_hadamard = make_basis("hadamard_paired", num_pixels=num_pixels, seed=CONFIG_SEED)

    # Centered-moment consistency prediction for the raw fixed-design floor:
    # E_A C0_floor = K + beta4 - 2 for the centered/normalized correlator
    # (population raw-moment constant of F.10; mu/sigma removed by centering).
    gen = torch.Generator(device="cpu")
    gen.manual_seed(CONFIG_SEED)
    patterns = torch.rand((frame_budget, num_pixels), generator=gen, dtype=torch.float32).numpy().ravel()
    mu, sig = float(patterns.mean()), float(patterns.std())
    z = (patterns - mu) / sig
    gamma3, beta4 = float((z ** 3).mean()), float((z ** 4).mean())
    moment_prediction = num_pixels + beta4 - 2.0

    rows = []
    for idx, obj in enumerate(objects):
        t = obj.to(dtype=torch.float64)
        s1 = float(t.sum())
        s2 = float(t.pow(2).sum())
        k_eff = s1 * s1 / s2
        recon = basis_random.reconstruct(basis_random.measure(obj))
        c_align = float(object_metrics(recon, obj)["rel_mse"]) * n
        c_raw = raw_rel_mse(recon, obj) * n
        rows.append(dict(object=idx, K_eff=k_eff,
                         C0_floor_align_fix=c_align,
                         C0_floor_raw_fix=c_raw,
                         raw_over_aligned=c_raw / c_align))
    consts = pd.DataFrame(rows)
    consts["moment_prediction_K_beta4_minus_2"] = moment_prediction
    consts.to_csv(out_dir / "prop3_raw_constants.csv", index=False)
    print(consts.to_string(), flush=True)

    print("[2/4] regenerate the dense-grid scan in memory (same OU paths) ...", flush=True)
    ideal_r = [basis_random.measure(o) for o in objects]
    ideal_h = [basis_hadamard.measure(o) for o in objects]
    scan_rows = []
    for sigma in GRID_SIGMAS:
        for rho in GRID_RHOS:
            for seed_idx in range(NUM_SEEDS):
                channel = make_multiplicative_channel(
                    frame_budget, model="ou", rho=float(rho), sigma_a=float(sigma),
                    seed=9000 + seed_idx, device="cpu", dtype=ideal_r[0].dtype)
                gains = channel.gains
                for obj_idx, obj in enumerate(objects):
                    observed_h = ideal_h[obj_idx] * gains
                    corr_h = apply_correction(observed_h, "pairwise", paired=True)
                    recon_h = basis_hadamard.reconstruct(
                        corr_h.values, values_are_coefficients=True)
                    m_h = object_metrics(recon_h, obj)
                    scan_rows.append(dict(arm="hadamard_paired+pairwise", rho=rho,
                                          sigma_a=sigma, seed=seed_idx, object=obj_idx,
                                          rel_mse_aligned=m_h["rel_mse"],
                                          rel_mse_raw=raw_rel_mse(recon_h, obj)))
                    observed_r = ideal_r[obj_idx] * gains
                    corr_r = apply_correction(observed_r, "oracle", true_gains=gains,
                                              paired=False)
                    recon_r = basis_random.reconstruct(
                        corr_r.values, values_are_coefficients=False)
                    m_r = object_metrics(recon_r, obj)
                    scan_rows.append(dict(arm="random_uniform+oracle", rho=rho,
                                          sigma_a=sigma, seed=seed_idx, object=obj_idx,
                                          rel_mse_aligned=m_r["rel_mse"],
                                          rel_mse_raw=raw_rel_mse(recon_r, obj)))
    scan = pd.DataFrame(scan_rows)
    agg = (scan.groupby(["arm", "sigma_a", "object", "rho"], as_index=False)
           .agg(rel_mse_aligned=("rel_mse_aligned", "mean"),
                rel_mse_raw=("rel_mse_raw", "mean"),
                n=("rel_mse_raw", "size")))
    agg.to_csv(out_dir / "prop3_raw_scan.csv", index=False)

    print("[3/4] aligned reproduction check vs published dense grid ...", flush=True)
    grid = pd.read_csv(phase_dir / "phase_scan.csv")
    grid = grid[((grid.basis == "hadamard_paired") & (grid.correction == "pairwise"))
                | ((grid.basis == "random_uniform") & (grid.correction == "oracle"))].copy()
    grid["arm"] = np.where(grid["basis"] == "hadamard_paired",
                           "hadamard_paired+pairwise", "random_uniform+oracle")
    grid_agg = (grid.groupby(["arm", "sigma_a", "object", "rho"], as_index=False)
                .agg(rel_mse_grid=("rel_mse", "mean")))
    check = agg.merge(grid_agg, on=["arm", "sigma_a", "object", "rho"], how="inner")
    check["abs_diff"] = (check["rel_mse_aligned"] - check["rel_mse_grid"]).abs()
    check.to_csv(out_dir / "aligned_reproduction_check.csv", index=False)
    repro = dict(n_rows=int(len(check)),
                 max_abs_diff=float(check["abs_diff"].max()),
                 median_abs_diff=float(check["abs_diff"].median()))
    print(json.dumps(repro, indent=2), flush=True)

    print("[4/4] raw-vs-raw skeleton crossings ...", flush=True)
    pair = agg[agg.arm == "hadamard_paired+pairwise"]
    orac = agg[agg.arm == "random_uniform+oracle"]
    d_h = pd.read_csv(ROOT / "results/prop3_nofreeparam_r1/prop3_constants.csv")
    d_h = d_h.set_index("object")["D_H"]
    rows = []
    for (sigma, obj), g in pair.groupby(["sigma_a", "object"]):
        g = g.sort_values("rho")
        go = orac[(orac.sigma_a == sigma) & (orac.object == obj)].sort_values("rho")
        m = g.merge(go, on="rho", suffixes=("_pair", "_orac"))
        margin = (np.log10(m.rel_mse_raw_pair.values)
                  - np.log10(m.rel_mse_raw_orac.values))
        emp, status = first_crossing(m.rho.values.astype(float), margin)
        const = consts[consts.object == obj].iloc[0]
        q_raw = (2.0 * (const.C0_floor_raw_fix / n)
                 / (const.K_eff * float(d_h.loc[obj]) * sigma * sigma))
        pred = -math.log(1.0 - q_raw) if q_raw < 1.0 else float("nan")
        pred_status = "predicted" if q_raw < 1.0 else "Q_raw_ge_1_no_crossing"
        rows.append(dict(sigma_a=sigma, object=int(obj),
                         rho_star_emp_raw=emp, emp_status=status,
                         Q_raw=q_raw, rho_star_pred_raw=pred, pred_status=pred_status,
                         log10_ratio=(math.log10(pred / emp)
                                      if status == "observed" and np.isfinite(pred)
                                      else float("nan"))))
    skel = pd.DataFrame(rows)
    skel.to_csv(out_dir / "prop3_raw_skeleton_test.csv", index=False)

    main_band = skel[skel.sigma_a >= 0.1]
    obs_main = main_band[main_band.emp_status == "observed"].log10_ratio.dropna()
    summary = dict(
        pattern_moments=dict(mu=mu, sigma=sig, gamma3=gamma3, beta4=beta4),
        moment_prediction_K_beta4_minus_2=moment_prediction,
        aligned_floor_range=[float(consts.C0_floor_align_fix.min()),
                             float(consts.C0_floor_align_fix.max())],
        raw_floor_range=[float(consts.C0_floor_raw_fix.min()),
                         float(consts.C0_floor_raw_fix.max())],
        raw_floor_median=float(consts.C0_floor_raw_fix.median()),
        raw_floor_mean=float(consts.C0_floor_raw_fix.mean()),
        raw_over_aligned_ratio_median=float(consts.raw_over_aligned.median()),
        aligned_reproduction=repro,
        raw_skeleton_sigma_ge_0p1=dict(
            n_cells=int(len(main_band)),
            n_observed_crossings=int((main_band.emp_status == "observed").sum()),
            median_log10_ratio=float(obs_main.median()),
            median_abs_log10_ratio=float(obs_main.abs().median()),
            factor_median=float(10 ** obs_main.abs().median()),
            factor_max=float(10 ** obs_main.abs().max()),
            frac_within_factor2=float((obs_main.abs() <= math.log10(2)).mean()),
        ),
        sigma_0p05_cells=dict(
            n_cells=int((skel.sigma_a < 0.1).sum()),
            n_Q_raw_ge_1=int(((skel.sigma_a < 0.1) & (skel.Q_raw >= 1.0)).sum()),
            n_raw_crossing_observed=int(((skel.sigma_a < 0.1)
                                         & (skel.emp_status == "observed")).sum()),
        ),
        runtime_seconds=float(time.time() - t_start),
    )
    (out_dir / "prop3_raw_summary.json").write_text(json.dumps(summary, indent=2),
                                                    encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)

    manifest_extra = dict(
        script="run_prop3_raw_metric_export.py",
        purpose=("R13 raw-metric re-export: raw fixed-design floor and raw-vs-raw "
                 "Prop-3 skeleton crossings derived from the same deterministic "
                 "basis/objects and the same OU gain paths as the authoritative "
                 "aligned run (results/prop3_nofreeparam_r1); no new physics."),
        phase_dir=str(phase_dir), output_dir=str(out_dir),
        config_seed=CONFIG_SEED, image_size=IMAGE_SIZE, num_objects=NUM_OBJECTS,
        num_seeds=NUM_SEEDS, frame_budget=frame_budget,
        rho_values=GRID_RHOS, sigma_values=GRID_SIGMAS,
        channel=dict(model="ou", seed_rule="9000+seed_idx",
                     note="identical to run_prop3_boundary.py / run_phase_m2.py"),
        raw_metric="||T_hat - T||^2 / ||T||^2 (float64, no scale alignment)",
        aligned_metric="run_mechanism_m1.object_metrics rel_mse (least-squares scale)",
        inputs=[
            str(phase_dir / "phase_scan.csv"),
            "results/prop3_nofreeparam_r1/prop3_constants.csv (D_H only)",
        ],
    )
    manifest = build_run_manifest(args, ROOT, extra=manifest_extra, output_dir=out_dir)
    (out_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    print(f"[done] {time.time()-t_start:.1f}s -> {out_dir}", flush=True)


if __name__ == "__main__":
    main()
