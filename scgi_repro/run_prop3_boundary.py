"""No-free-parameter test of Prop 3 (finite-N flip boundary) — audit fix P0-4.

Prop 3 (Appendix F.4) predicts the flip boundary between ORDERED PAIRWISE
HADAMARD (pairwise-normalized) and BLIND RANDOM + DGI under OU gain drift:

    r(rho*) = 2 * [ C0/N + (1+C0) * v_blind(rho*, N)/N ] / (K_eff * D_H * s^2)
    with r(rho) = 1 - exp(-rho)  (OU adjacent-pair decorrelation),

and the leading-order engineering rule (F.13): rho* ~= 2*C0 / (N * K_eff * s^2).

This runner:
  1. RECOUNTS the M2 dense winner map from `phase_scan.csv` (authoritative
     winner table, replicated independently of run_m2_boundary_audit.py).
  2. MEASURES the pipeline constants with zero fitted parameters:
     per-object K_eff, D_H(T), and the pipeline C0 (definition F.9: clean-gain
     DGI relMSE * N with the exact dense-run basis), plus the blind residual
     gain variance v_blind(rho, sigma) of the agc / scgi_proxy estimators.
  3. RUNS the two Prop-3 arms (hadamard_paired+pairwise vs random_uniform+
     {agc, scgi_proxy}) on a fine rho grid with the dense run's exact seeds,
     objects, basis, and channel conventions; extracts empirical crossings.
  4. Compares predicted vs empirical rho* per (sigma, object) and reports the
     agreement factor  median |log10(rho*_pred / rho*_emp)|.

Everything on the prediction side is measured or declared (N, K_eff, D_H, C0,
sigma_a, OU r(.), v_blind measured from the gain-estimator subsystem);
nothing is fitted to the crossing data.

Usage:
  python run_prop3_boundary.py --precheck          # constants + reproduction check only
  python run_prop3_boundary.py                     # full scan + analysis
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
from src.basis import basis_frame_budget, hadamard_matrix, make_basis
from src.mechanisms import apply_correction, gain_error_stats, make_multiplicative_channel

ROOT = Path(__file__).resolve().parent
GRID_RHOS = [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0]
GRID_SIGMAS = [0.05, 0.10, 0.15, 0.30, 0.50]
ABOVE_FLOOR_REL_MSE = 0.5
CONFIG_SEED = 20240708  # config.yaml `seed`, used by the dense run
IMAGE_SIZE = 32
NUM_OBJECTS = 10
NUM_SEEDS = 5
RAND_CORRECTIONS = ["agc", "scgi_proxy"]


# ----------------------------------------------------------------------------------
# Part 1: recount the winner map (independent re-implementation of the audit rules)
# ----------------------------------------------------------------------------------

def recount_winner_map(scan: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    summary = (
        scan.groupby(["rho", "sigma_a", "basis", "correction"], as_index=False)
        .agg(
            psnr_mean=("psnr", "mean"),
            rel_mse_mean=("rel_mse", "mean"),
            num_frames=("num_frames", "first"),
            total_physical_frames=("total_physical_frames", "first"),
        )
    )
    blind = summary[summary["correction"] != "oracle"].copy()
    equal_frame = blind[blind["total_physical_frames"] == blind["num_frames"]].copy()
    scopes = {"all_non_oracle": blind, "equal_frame_non_oracle": equal_frame}
    rows = []
    for scope, table in scopes.items():
        for (rho, sigma), group in table.groupby(["rho", "sigma_a"], sort=True):
            above = group[group["rel_mse_mean"] < ABOVE_FLOOR_REL_MSE]
            if above.empty:
                best = group.sort_values("psnr_mean", ascending=False).iloc[0]
                rows.append(
                    dict(scope=scope, rho=rho, sigma_a=sigma, winner_basis="noise_floor",
                         winner_correction="noise_floor", above_floor=False,
                         above_floor_candidates=0,
                         best_sub_floor=f"{best['basis']}+{best['correction']}",
                         winner_psnr=float(best["psnr_mean"]),
                         winner_rel_mse=float(best["rel_mse_mean"])))
            else:
                best = above.sort_values("psnr_mean", ascending=False).iloc[0]
                rows.append(
                    dict(scope=scope, rho=rho, sigma_a=sigma, winner_basis=str(best["basis"]),
                         winner_correction=str(best["correction"]), above_floor=True,
                         above_floor_candidates=int(len(above)), best_sub_floor="",
                         winner_psnr=float(best["psnr_mean"]),
                         winner_rel_mse=float(best["rel_mse_mean"])))
    winners = pd.DataFrame(rows)
    counts = {}
    for scope in scopes:
        w = winners[winners["scope"] == scope]
        by_arm = (
            w.groupby(["winner_basis", "winner_correction"]).size().sort_values(ascending=False)
        )
        counts[scope] = {
            "total_cells": int(len(w)),
            "above_floor_cells": int(w["above_floor"].sum()),
            "noise_floor_cells": int((~w["above_floor"]).sum()),
            "winners": {f"{b}+{c}": int(n) for (b, c), n in by_arm.items()},
        }
    return winners, summary, counts


# ----------------------------------------------------------------------------------
# Part 2: measured constants (zero fitted parameters)
# ----------------------------------------------------------------------------------

def measure_constants(objects: list[torch.Tensor], basis_random, basis_hadamard,
                      n_frames: int) -> pd.DataFrame:
    k = objects[0].numel()
    h_full = hadamard_matrix(k, dtype=torch.float64)
    rows = []
    for idx, obj in enumerate(objects):
        t = obj.to(dtype=torch.float64)
        s1 = float(t.sum())
        s2 = float(t.pow(2).sum())
        k_eff = s1 * s1 / s2
        coeffs = h_full @ t
        x = coeffs / s1
        d_h = float(((1.0 - x.pow(2)).pow(2)).mean())
        # Pipeline C0 (definition F.9): clean-gain DGI relMSE * N with the exact
        # dense-run random_uniform basis and the exact pipeline metric.
        ideal = basis_random.measure(obj)
        recon = basis_random.reconstruct(ideal)
        m = object_metrics(recon, obj)
        c0 = float(m["rel_mse"]) * float(n_frames)
        # Clean pairwise-Hadamard floor (should be ~0 without noise/drift).
        ideal_h = basis_hadamard.measure(obj)
        corr = apply_correction(ideal_h, "pairwise", paired=True)
        recon_h = basis_hadamard.reconstruct(corr.values, values_are_coefficients=True)
        m_h = object_metrics(recon_h, obj)
        rows.append(
            dict(object=idx, S1=s1, S2=s2, K_eff=k_eff, D_H=d_h, C0_pipeline=c0,
                 dgi_clean_rel_mse=float(m["rel_mse"]),
                 pairwise_clean_rel_mse=float(m_h["rel_mse"])))
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------------
# Part 3: the two Prop-3 arms over a (rho, sigma) scan
# ----------------------------------------------------------------------------------

def run_scan(objects, basis_random, basis_hadamard, rho_values, sigma_values,
             seeds, agc_window, log_every=200) -> pd.DataFrame:
    ideal_r = [basis_random.measure(o) for o in objects]
    ideal_h = [basis_hadamard.measure(o) for o in objects]
    n_frames = basis_random.num_frames
    rows = []
    t0 = time.time()
    n_units = 0
    total = len(sigma_values) * len(rho_values) * seeds * len(objects)
    for sigma in sigma_values:
        for rho in rho_values:
            for seed_idx in range(seeds):
                channel = make_multiplicative_channel(
                    n_frames, model="ou", rho=float(rho), sigma_a=float(sigma),
                    seed=9000 + seed_idx, device="cpu", dtype=ideal_r[0].dtype)
                gains = channel.gains
                for obj_idx, obj in enumerate(objects):
                    # Arm 1: ordered pairwise Hadamard, pairwise normalization.
                    observed_h = ideal_h[obj_idx] * gains
                    corr_h = apply_correction(observed_h, "pairwise", paired=True)
                    recon_h = basis_hadamard.reconstruct(
                        corr_h.values, values_are_coefficients=True)
                    m_h = object_metrics(recon_h, obj)
                    rows.append(dict(arm="hadamard_paired+pairwise", rho=rho, sigma_a=sigma,
                                     seed=seed_idx, object=obj_idx,
                                     rel_mse=m_h["rel_mse"], psnr=m_h["psnr"],
                                     gain_rel_mse=np.nan))
                    # Arm 2: random uniform + DGI with blind gain correction.
                    observed_r = ideal_r[obj_idx] * gains
                    for correction in RAND_CORRECTIONS:
                        corr_r = apply_correction(
                            observed_r, correction, true_gains=gains, paired=False,
                            agc_window=agc_window)
                        recon_r = basis_random.reconstruct(
                            corr_r.values,
                            values_are_coefficients=corr_r.values_are_coefficients)
                        m_r = object_metrics(recon_r, obj)
                        g = gain_error_stats(corr_r.gain_hat, gains)
                        rows.append(dict(arm=f"random_uniform+{correction}", rho=rho,
                                         sigma_a=sigma, seed=seed_idx, object=obj_idx,
                                         rel_mse=m_r["rel_mse"], psnr=m_r["psnr"],
                                         gain_rel_mse=g["gain_rel_mse"]))
                    n_units += 1
                    if n_units % log_every == 0:
                        el = time.time() - t0
                        print(f"[scan] {n_units}/{total} units, {el:.1f}s elapsed", flush=True)
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------------
# Part 4: crossings and predictions
# ----------------------------------------------------------------------------------

def first_crossing(rhos: np.ndarray, margin: np.ndarray) -> tuple[float, str, int]:
    """First rho where margin >= 0 (pair relMSE >= rand relMSE), log-rho interp."""
    order = np.argsort(rhos)
    rhos, margin = rhos[order], margin[order]
    ok = np.isfinite(rhos) & np.isfinite(margin)
    rhos, margin = rhos[ok], margin[ok]
    if len(rhos) == 0:
        return float("nan"), "missing", 0
    signs = margin >= 0.0
    n_cross = int(np.sum(signs[1:] != signs[:-1]))
    if signs[0]:
        return float(rhos[0]), "left_censored", n_cross
    for i in range(len(rhos) - 1):
        if margin[i] < 0.0 <= margin[i + 1]:
            lo, hi = math.log10(rhos[i]), math.log10(rhos[i + 1])
            frac = (0.0 - margin[i]) / (margin[i + 1] - margin[i])
            return float(10 ** (lo + frac * (hi - lo))), "observed", n_cross
    return float("nan"), "not_reached", n_cross


def predict_rho_star(c0: float, k_eff: float, d_h: float, sigma: float, n: float,
                     v_rho: np.ndarray | None, v_val: np.ndarray | None,
                     use_v: bool, use_dh: bool, ou_invert: bool) -> tuple[float, str, float]:
    """Solve r(rho*) = 2*[C0/N + (1+C0) v(rho*)/N] / (K_eff*D_H*sigma^2)."""
    denom = k_eff * (d_h if use_dh else 1.0) * sigma * sigma
    if not ou_invert:
        # F.13 exactly as written: r(rho)=rho, D_H=1, v=0.
        return 2.0 * c0 / (n * k_eff * sigma * sigma), "leading_order", 2.0 * c0 / (n * denom)

    rho_grid = np.geomspace(1e-6, 100.0, 6000)
    if use_v and v_rho is not None and len(v_rho) >= 2:
        lv = np.interp(np.log10(rho_grid), np.log10(v_rho), np.log10(np.maximum(v_val, 1e-12)))
        v = 10.0 ** lv
    else:
        v = np.zeros_like(rho_grid)
    q = 2.0 * (c0 / n + (1.0 + c0) * v / n) / denom
    f = (1.0 - np.exp(-rho_grid)) - q
    if f[0] >= 0:
        return float(rho_grid[0]), "left_censored_pred", float(q[0])
    idx = np.where((f[:-1] < 0) & (f[1:] >= 0))[0]
    if len(idx) == 0:
        return float("nan"), "never_flips_pred", float(q[-1])
    i = int(idx[0])
    lo, hi = math.log10(rho_grid[i]), math.log10(rho_grid[i + 1])
    frac = (0.0 - f[i]) / (f[i + 1] - f[i])
    rho_star = float(10 ** (lo + frac * (hi - lo)))
    q_at = float(np.interp(math.log10(rho_star), np.log10(rho_grid), q))
    return rho_star, "observed", q_at


def analyze(curves: pd.DataFrame, constants: pd.DataFrame, n_frames: int,
            source_label: str) -> pd.DataFrame:
    """Per (sigma, object, correction): empirical crossing + predictions."""
    out = []
    agg = (curves.groupby(["arm", "sigma_a", "object", "rho"], as_index=False)
           .agg(rel_mse=("rel_mse", "mean"), gain_rel_mse=("gain_rel_mse", "mean")))
    for sigma in sorted(agg["sigma_a"].unique()):
        for obj in sorted(agg["object"].unique()):
            const = constants[constants["object"] == obj].iloc[0]
            pair = agg[(agg["arm"] == "hadamard_paired+pairwise")
                       & (agg["sigma_a"] == sigma) & (agg["object"] == obj)].sort_values("rho")
            for correction in RAND_CORRECTIONS:
                rand = agg[(agg["arm"] == f"random_uniform+{correction}")
                           & (agg["sigma_a"] == sigma) & (agg["object"] == obj)].sort_values("rho")
                if pair.empty or rand.empty:
                    continue
                merged = pair.merge(rand, on="rho", suffixes=("_pair", "_rand"))
                margin = (np.log10(merged["rel_mse_pair"].to_numpy())
                          - np.log10(merged["rel_mse_rand"].to_numpy()))
                rho_emp, status_emp, n_cross = first_crossing(
                    merged["rho"].to_numpy(dtype=float), margin)
                # relMSE context at the crossing (floor check)
                if np.isfinite(rho_emp):
                    rel_at = float(np.interp(math.log10(rho_emp),
                                             np.log10(merged["rho"].to_numpy(dtype=float)),
                                             np.log10(merged["rel_mse_rand"].to_numpy())))
                    rel_at = 10 ** rel_at
                else:
                    rel_at = float("nan")
                v_rho = merged["rho"].to_numpy(dtype=float)
                v_val = merged["gain_rel_mse_rand"].to_numpy(dtype=float)
                keep = np.isfinite(v_val) & (v_val > 0)
                pred_full, st_full, q_full = predict_rho_star(
                    const["C0_pipeline"], const["K_eff"], const["D_H"], sigma, n_frames,
                    v_rho[keep], v_val[keep], use_v=True, use_dh=True, ou_invert=True)
                pred_nov, st_nov, q_nov = predict_rho_star(
                    const["C0_pipeline"], const["K_eff"], const["D_H"], sigma, n_frames,
                    None, None, use_v=False, use_dh=True, ou_invert=True)
                pred_lead, _, _ = predict_rho_star(
                    const["C0_pipeline"], const["K_eff"], const["D_H"], sigma, n_frames,
                    None, None, use_v=False, use_dh=False, ou_invert=False)
                row = dict(source=source_label, sigma_a=sigma, object=int(obj),
                           rand_correction=correction,
                           K_eff=float(const["K_eff"]), D_H=float(const["D_H"]),
                           C0_pipeline=float(const["C0_pipeline"]), N=n_frames,
                           rho_star_emp=rho_emp, emp_status=status_emp,
                           emp_n_sign_changes=n_cross, rel_mse_at_crossing=rel_at,
                           above_floor_at_crossing=bool(np.isfinite(rel_at)
                                                        and rel_at < ABOVE_FLOOR_REL_MSE),
                           rho_star_pred_full=pred_full, pred_full_status=st_full,
                           Q_at_pred_full=q_full,
                           rho_star_pred_v0=pred_nov, pred_v0_status=st_nov,
                           rho_star_pred_leading=pred_lead)
                for name in ["full", "v0", "leading"]:
                    p = row[f"rho_star_pred_{name}"]
                    row[f"log10_ratio_{name}"] = (
                        math.log10(p / rho_emp)
                        if (np.isfinite(p) and np.isfinite(rho_emp) and rho_emp > 0
                            and status_emp == "observed") else float("nan"))
                out.append(row)
    return pd.DataFrame(out)


def ingredient_check(curves: pd.DataFrame, constants: pd.DataFrame) -> pd.DataFrame:
    """F.8 ingredient: measured pairwise relMSE vs 0.5*K_eff*D_H*s^2*(1-e^-rho)."""
    pair = (curves[curves["arm"] == "hadamard_paired+pairwise"]
            .groupby(["sigma_a", "object", "rho"], as_index=False)
            .agg(rel_mse=("rel_mse", "mean")))
    pair = pair.merge(constants[["object", "K_eff", "D_H"]], on="object")
    pair["pred_rel_mse"] = (0.5 * pair["K_eff"] * pair["D_H"] * pair["sigma_a"] ** 2
                            * (1.0 - np.exp(-pair["rho"])))
    pair["ratio_measured_over_pred"] = pair["rel_mse"] / pair["pred_rel_mse"]
    return pair


# ----------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase-dir", type=Path,
                        default=Path("results/m2_hadamard_order_dense_r1_merged"))
    parser.add_argument("--output-dir", type=Path,
                        default=Path("results/prop3_nofreeparam_r1"))
    parser.add_argument("--precheck", action="store_true",
                        help="constants + grid-reproduction check only (fast)")
    parser.add_argument("--fine-rho-points", type=int, default=24)
    args = parser.parse_args()

    phase_dir = args.phase_dir if args.phase_dir.is_absolute() else ROOT / args.phase_dir
    out_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    print("[1/5] recount winner map ...", flush=True)
    scan = pd.read_csv(phase_dir / "phase_scan.csv")
    winners, summary, counts = recount_winner_map(scan)
    winners.to_csv(out_dir / "winner_table_cells.csv", index=False)
    (out_dir / "recount_counts.json").write_text(json.dumps(counts, indent=2), encoding="utf-8")
    print(json.dumps(counts, indent=2), flush=True)

    print("[2/5] build objects and measure constants ...", flush=True)
    num_pixels = IMAGE_SIZE * IMAGE_SIZE
    frame_budget, _ = basis_frame_budget(num_pixels)
    objects = make_synthetic_objects(NUM_OBJECTS, IMAGE_SIZE, CONFIG_SEED)
    basis_random = make_basis("random_uniform", num_pixels=num_pixels,
                              num_frames=frame_budget, seed=CONFIG_SEED,
                              reconstruction="correlation")
    basis_hadamard = make_basis("hadamard_paired", num_pixels=num_pixels, seed=CONFIG_SEED)
    constants = measure_constants(objects, basis_random, basis_hadamard, frame_budget)
    constants.to_csv(out_dir / "prop3_constants.csv", index=False)
    print(constants.to_string(), flush=True)

    print("[3/5] reproduction check vs dense grid ...", flush=True)
    agc_window = max(9, int(0.05 * frame_budget))
    check_rows = []
    for rho in [0.01, 1.0]:
        for sigma in [0.1, 0.3]:
            for seed_idx in [0, 1]:
                channel = make_multiplicative_channel(frame_budget, model="ou", rho=rho,
                                                      sigma_a=sigma, seed=9000 + seed_idx,
                                                      device="cpu", dtype=torch.float32)
                for obj_idx in [0, 5]:
                    obj = objects[obj_idx]
                    for basis, bname, corr_name in [
                            (basis_hadamard, "hadamard_paired", "pairwise"),
                            (basis_random, "random_uniform", "agc"),
                            (basis_random, "random_uniform", "scgi_proxy")]:
                        observed = basis.measure(obj) * channel.gains
                        corr = apply_correction(observed, corr_name,
                                                true_gains=channel.gains,
                                                paired=basis.paired, agc_window=agc_window)
                        recon = basis.reconstruct(
                            corr.values,
                            values_are_coefficients=corr.values_are_coefficients)
                        m = object_metrics(recon, obj)
                        g = scan[(scan.basis == bname) & (scan.correction == corr_name)
                                 & (scan.rho == rho) & (scan.sigma_a == sigma)
                                 & (scan.seed == seed_idx) & (scan.object == obj_idx)]
                        grid_rel = float(g["rel_mse"].iloc[0]) if len(g) else float("nan")
                        check_rows.append(dict(
                            basis=bname, correction=corr_name, rho=rho, sigma_a=sigma,
                            seed=seed_idx, object=obj_idx, local_rel_mse=m["rel_mse"],
                            grid_rel_mse=grid_rel,
                            ratio=m["rel_mse"] / grid_rel if grid_rel else float("nan")))
    check = pd.DataFrame(check_rows)
    check.to_csv(out_dir / "reproduction_check.csv", index=False)
    with pd.option_context("display.width", 200):
        print(check.to_string(), flush=True)

    if args.precheck:
        print(f"[precheck done] {time.time()-t_start:.1f}s", flush=True)
        return

    print("[4/5] fine (rho, sigma) scan of the two Prop-3 arms ...", flush=True)
    fine = np.geomspace(0.002, 20.0, args.fine_rho_points)
    rho_values = sorted(set(GRID_RHOS) | set(float(f"{r:.6g}") for r in fine))
    curves = run_scan(objects, basis_random, basis_hadamard, rho_values, GRID_SIGMAS,
                      NUM_SEEDS, agc_window)
    curves_agg = (curves.groupby(["arm", "sigma_a", "rho", "object"], as_index=False)
                  .agg(rel_mse=("rel_mse", "mean"), psnr=("psnr", "mean"),
                       gain_rel_mse=("gain_rel_mse", "mean"),
                       n=("rel_mse", "size")))
    curves_agg.to_csv(out_dir / "prop3_curves_local.csv", index=False)

    print("[5/5] crossings, predictions, agreement ...", flush=True)
    result_local = analyze(curves, constants, frame_budget, "local_fine_scan")

    # Independent empirical crossing from the published dense grid (Colab data).
    grid_curves = scan[((scan.basis == "hadamard_paired") & (scan.correction == "pairwise"))
                       | ((scan.basis == "random_uniform")
                          & (scan.correction.isin(RAND_CORRECTIONS)))].copy()
    grid_curves["arm"] = np.where(
        grid_curves["basis"] == "hadamard_paired", "hadamard_paired+pairwise",
        "random_uniform+" + grid_curves["correction"])
    result_grid = analyze(grid_curves, constants, frame_budget, "colab_dense_grid")

    result = pd.concat([result_local, result_grid], ignore_index=True)
    result.to_csv(out_dir / "prop3_prediction_vs_empirical.csv", index=False)

    ing = ingredient_check(curves, constants)
    ing.to_csv(out_dir / "prop3_pair_gain_ingredient.csv", index=False)

    # Agreement summary
    lines = []
    for source in result["source"].unique():
        for correction in RAND_CORRECTIONS:
            sub = result[(result["source"] == source)
                         & (result["rand_correction"] == correction)]
            obs = sub[sub["emp_status"] == "observed"]
            for name in ["full", "v0", "leading"]:
                r = obs[f"log10_ratio_{name}"].dropna()
                if len(r):
                    lines.append(dict(source=source, rand_correction=correction,
                                      prediction=name, n_cells=int(len(r)),
                                      median_abs_log10_ratio=float(r.abs().median()),
                                      median_log10_ratio=float(r.median()),
                                      max_abs_log10_ratio=float(r.abs().max()),
                                      factor_median=float(10 ** r.abs().median()),
                                      frac_within_factor2=float((r.abs() <= math.log10(2)).mean()),
                                      frac_within_factor3=float((r.abs() <= math.log10(3)).mean())))
    agreement = pd.DataFrame(lines)
    agreement.to_csv(out_dir / "prop3_agreement_summary.csv", index=False)
    with pd.option_context("display.width", 250):
        print(agreement.to_string(), flush=True)

    manifest = dict(
        script="run_prop3_boundary.py",
        phase_dir=str(phase_dir), output_dir=str(out_dir),
        config_seed=CONFIG_SEED, image_size=IMAGE_SIZE, num_objects=NUM_OBJECTS,
        num_seeds=NUM_SEEDS, frame_budget=frame_budget, agc_window=agc_window,
        rho_values=rho_values, sigma_values=GRID_SIGMAS,
        rand_corrections=RAND_CORRECTIONS,
        channel=dict(model="ou", seed_rule="9000+seed_idx",
                     note="log-gain AR(1), phi=exp(-rho), stationary std sigma_a, "
                          "demeaned, exp, mean-normalized; identical to run_phase_m2.py"),
        above_floor_rel_mse=ABOVE_FLOOR_REL_MSE,
        runtime_seconds=float(time.time() - t_start),
        torch_version=torch.__version__,
    )
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[done] {time.time()-t_start:.1f}s -> {out_dir}", flush=True)


if __name__ == "__main__":
    main()
