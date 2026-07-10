"""Companion to run_prop3_boundary.py: verdict tables for the Prop-3 audit fix.

Four zero-free-parameter checks, all against the published M2 dense grid
(`results/m2_hadamard_order_dense_r1_merged/phase_scan.csv`) and the constants
measured by run_prop3_boundary.py:

 A. SKELETON TEST (v = 0): ordered pairwise Hadamard vs ORACLE-gain random+DGI.
    Prediction r(rho*) = 2 (C0_pipe/N) / (K_eff D_H s^2), OU r = 1-exp(-rho).
 B. PAIR-ARM INGREDIENT (F.8): measured pairwise relMSE vs
    0.5 K_eff D_H s^2 (1-exp(-rho)) in the small-error regime.
 C. RANDOM-ARM DRIFT LEVERAGE: measured drift excess of the random arm vs the
    two candidate constants —
      as written in (F.11)/Prop 3:  (1+C0_pipe) v / N
      corrected leverage (F.10):    (1+C0_ideal) v / N,
        C0_ideal = K + beta4 - 2 + K_eff [K (mu/sigma)^2 + 2 gamma3 (mu/sigma)]
    evaluated at white drift (rho = 10, delta independent across frames, the
    cleanest case for the uncorrelated-residual hypothesis), with the
    scale-aligned metric mapping relMSE_aligned = e/(1+e).
 D. BLIND-ARM CROSSING CONSISTENCY: with the corrected leverage constant, the
    fixed-point equation has no solution (Q > r for all rho) at every grid
    (sigma, object) — consistent with the observed absence of any flip.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from run_mechanism_m1 import make_synthetic_objects
from src.paper_experiments import build_run_manifest

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "prop3_nofreeparam_r1"
N = 2048
K = 1024
CONFIG_SEED = 20240708


def first_crossing(rhos, margin):
    if margin[0] >= 0:
        return float(rhos[0]), "left_censored"
    for i in range(len(rhos) - 1):
        if margin[i] < 0.0 <= margin[i + 1]:
            lo, hi = math.log10(rhos[i]), math.log10(rhos[i + 1])
            return float(10 ** (lo + (0 - margin[i]) / (margin[i + 1] - margin[i]) * (hi - lo))), "observed"
    return float("nan"), "not_reached"


def main() -> None:
    scan = pd.read_csv(ROOT / "results/m2_hadamard_order_dense_r1_merged/phase_scan.csv")
    const = pd.read_csv(OUT / "prop3_constants.csv").set_index("object")
    curves = pd.read_csv(OUT / "prop3_curves_local.csv")

    # Pattern moments of the exact dense-run uniform basis (for C0_ideal, F.10).
    gen = torch.Generator(device="cpu"); gen.manual_seed(CONFIG_SEED)
    patterns = torch.rand((N, K), generator=gen, dtype=torch.float32).numpy().ravel()
    mu, sig = float(patterns.mean()), float(patterns.std())
    z = (patterns - mu) / sig
    gamma3, beta4 = float((z ** 3).mean()), float((z ** 4).mean())
    const["C0_ideal"] = (K + beta4 - 2.0
                         + const["K_eff"] * (K * (mu / sig) ** 2 + 2.0 * gamma3 * (mu / sig)))

    # ---------------- A. skeleton test (oracle random arm, v = 0) ----------------
    pair = (scan[(scan.basis == "hadamard_paired") & (scan.correction == "pairwise")]
            .groupby(["sigma_a", "object", "rho"], as_index=False).rel_mse.mean())
    orac = (scan[(scan.basis == "random_uniform") & (scan.correction == "oracle")]
            .groupby(["sigma_a", "object", "rho"], as_index=False).rel_mse.mean())
    rows = []
    for (s, o), g in pair.groupby(["sigma_a", "object"]):
        g = g.sort_values("rho")
        go = orac[(orac.sigma_a == s) & (orac.object == o)].sort_values("rho")
        m = g.merge(go, on="rho", suffixes=("_pair", "_orac"))
        margin = np.log10(m.rel_mse_pair.values) - np.log10(m.rel_mse_orac.values)
        emp, status = first_crossing(m.rho.values, margin)
        c0, keff, dh = const.loc[o, ["C0_pipeline", "K_eff", "D_H"]]
        q = 2.0 * (c0 / N) / (keff * dh * s * s)
        pred = -math.log(1.0 - q) if q < 1.0 else float("nan")
        rows.append(dict(sigma_a=s, object=int(o), rho_star_emp=emp, emp_status=status,
                         rho_star_pred=pred, Q=q,
                         log10_ratio=(math.log10(pred / emp)
                                      if status == "observed" and np.isfinite(pred)
                                      else float("nan"))))
    skel = pd.DataFrame(rows)
    skel.to_csv(OUT / "prop3_skeleton_oracle_test.csv", index=False)
    obs = skel[skel.emp_status == "observed"].log10_ratio.dropna()
    obs_main = skel[(skel.emp_status == "observed") & (skel.sigma_a >= 0.1)].log10_ratio.dropna()
    skel_summary = dict(
        n_cells=int(len(skel)), n_observed=int(len(obs)),
        median_log10_ratio=float(obs.median()),
        median_abs_log10_ratio=float(obs.abs().median()),
        factor_median=float(10 ** obs.abs().median()),
        frac_within_factor2=float((obs.abs() <= math.log10(2)).mean()),
        max_abs_log10_ratio=float(obs.abs().max()),
        n_observed_sigma_ge_0p1=int(len(obs_main)),
        median_abs_log10_ratio_sigma_ge_0p1=float(obs_main.abs().median()),
        factor_median_sigma_ge_0p1=float(10 ** obs_main.abs().median()),
        frac_within_factor2_sigma_ge_0p1=float((obs_main.abs() <= math.log10(2)).mean()),
        max_abs_log10_ratio_sigma_ge_0p1=float(obs_main.abs().max()),
    )

    # ---------------- B. pair-arm ingredient (F.8) ----------------
    ing = pd.read_csv(OUT / "prop3_pair_gain_ingredient.csv")
    reg = ing[(ing.pred_rel_mse > 1e-4) & (ing.pred_rel_mse < 0.2)]
    ing_summary = dict(
        n_cells=int(len(reg)),
        median_ratio_measured_over_pred=float(reg.ratio_measured_over_pred.median()),
        iqr_ratio=[float(reg.ratio_measured_over_pred.quantile(0.25)),
                   float(reg.ratio_measured_over_pred.quantile(0.75))],
        regime="predicted relMSE in (1e-4, 0.2)")

    # ---------------- C. random-arm drift leverage at white drift ----------------
    ru = (scan[scan.basis == "random_uniform"]
          .groupby(["correction", "sigma_a", "object", "rho"], as_index=False)
          .agg(rel_mse=("rel_mse", "mean"), gain_rel_mse=("gain_rel_mse", "mean")))
    white = ru[ru.rho == 10.0]
    rows = []
    for corr in ["none", "agc", "scgi_proxy"]:
        for (s, o), g in white[white.correction == corr].groupby(["sigma_a", "object"]):
            c0p, keff, c0i = const.loc[o, ["C0_pipeline", "K_eff", "C0_ideal"]]
            meas = float(g.rel_mse.iloc[0])
            # v: for 'none' the residual is the raw gain, delta = a-1, v = Var(a);
            # for blind arms use the measured residual (gain_rel_mse).
            if corr == "none":
                v = math.exp(s * s) * (math.exp(s * s) - 1.0)  # Var of lognormal, mean-normalized
            else:
                v = float(g.gain_rel_mse.iloc[0])
            e_pipe = c0p / N + (1.0 + c0p) * v / N
            e_ideal = c0p / N + (1.0 + c0i) * v / N
            rows.append(dict(correction=corr, sigma_a=s, object=int(o), v_used=v,
                             measured_aligned_rel_mse=meas,
                             pred_aligned_rel_mse_pipeC0=e_pipe / (1.0 + e_pipe),
                             pred_aligned_rel_mse_idealC0=e_ideal / (1.0 + e_ideal),
                             measured_unaligned_excess=(meas / (1.0 - meas) - c0p / N
                                                        if meas < 1 else float("nan")),
                             pred_excess_pipeC0=(1.0 + c0p) * v / N,
                             pred_excess_idealC0=(1.0 + c0i) * v / N))
    lev = pd.DataFrame(rows)
    lev["underprediction_factor_as_written"] = (lev.measured_unaligned_excess
                                                / lev.pred_excess_pipeC0)
    lev["ratio_measured_over_idealC0"] = (lev.measured_unaligned_excess
                                          / lev.pred_excess_idealC0)
    lev.to_csv(OUT / "prop3_random_arm_leverage_test.csv", index=False)
    lev_summary = {}
    for corr in ["none", "agc", "scgi_proxy"]:
        g = lev[lev.correction == corr]
        lev_summary[corr] = dict(
            median_underprediction_factor_as_written=float(
                g.underprediction_factor_as_written.median()),
            median_ratio_measured_over_idealC0=float(g.ratio_measured_over_idealC0.median()),
            median_abs_log10_aligned_err_idealC0=float(
                (np.log10(g.measured_aligned_rel_mse)
                 - np.log10(g.pred_aligned_rel_mse_idealC0)).abs().median()))

    # ---------------- D. corrected-constant no-flip consistency ----------------
    # With the corrected leverage, Q(rho) = 2[C0p/N + (1+C0i) v(rho)/N]/(Keff DH s^2).
    # Count grid (sigma, object, blind corr) cells where min_rho (Q - r) > 0
    # (prediction: no flip) vs the empirical status (all not_reached).
    vtab = (curves[curves.arm.str.startswith("random_uniform+")]
            .assign(correction=lambda d: d.arm.str.split("+").str[1]))
    rows = []
    for corr in ["agc", "scgi_proxy"]:
        for (s, o), g in vtab[vtab.correction == corr].groupby(["sigma_a", "object"]):
            g = g.sort_values("rho")
            c0p, keff, dh, c0i = const.loc[o, ["C0_pipeline", "K_eff", "D_H", "C0_ideal"]]
            r = 1.0 - np.exp(-g.rho.values)
            q = 2.0 * (c0p / N + (1.0 + c0i) * g.gain_rel_mse.values / N) / (keff * dh * s * s)
            rows.append(dict(correction=corr, sigma_a=s, object=int(o),
                             predicts_no_flip=bool(np.all(q > r)),
                             min_Q_minus_r=float(np.min(q - r))))
    noflip = pd.DataFrame(rows)
    noflip.to_csv(OUT / "prop3_correctedC0_noflip_consistency.csv", index=False)
    d_summary = dict(
        n_cells=int(len(noflip)),
        n_predict_no_flip=int(noflip.predicts_no_flip.sum()),
        n_empirical_no_flip=int(len(noflip)),  # every cell was not_reached (see main table)
    )

    summary = dict(
        pattern_moments=dict(mu=mu, sigma=sig, gamma3=gamma3, beta4=beta4),
        C0_ideal_range=[float(const.C0_ideal.min()), float(const.C0_ideal.max())],
        C0_pipeline_range=[float(const.C0_pipeline.min()), float(const.C0_pipeline.max())],
        A_skeleton_oracle=skel_summary,
        B_pair_ingredient_F8=ing_summary,
        C_random_arm_leverage_white_drift=lev_summary,
        D_correctedC0_noflip=d_summary,
    )
    (OUT / "prop3_verdict_summary.json").write_text(json.dumps(summary, indent=2),
                                                    encoding="utf-8")
    print(json.dumps(summary, indent=2))

    # Standard v2 provenance manifest. Written to a distinct filename so it does
    # not clobber run_prop3_boundary.py's run_manifest.json in the shared out dir.
    manifest = build_run_manifest(
        argparse.Namespace(N=N, K=K, config_seed=CONFIG_SEED),
        ROOT,
        extra=dict(
            script="run_prop3_verdict_tables.py",
            output_dir=str(OUT),
            inputs=[
                "results/m2_hadamard_order_dense_r1_merged/phase_scan.csv",
                "prop3_constants.csv",
                "prop3_curves_local.csv",
                "prop3_pair_gain_ingredient.csv",
            ],
            N=N, K=K, config_seed=CONFIG_SEED,
            pattern_moments=dict(mu=mu, sigma=sig, gamma3=gamma3, beta4=beta4),
        ),
        output_dir=OUT,
    )
    (OUT / "verdict_tables_run_manifest.json").write_text(
        json.dumps(manifest, indent=2, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
