# Prop 3 no-free-parameter test + winner-map recount (audit fix P0-4)

Scripts: `run_prop3_boundary.py` (recount, constants, fine two-arm scan,
crossings, predictions) and `run_prop3_verdict_tables.py` (skeleton test,
ingredient checks, leverage diagnosis). Data: the published M2 dense grid
`results/m2_hadamard_order_dense_r1_merged/phase_scan.csv` plus a local fine-rho
rescan that reproduces the grid bit-exactly (`reproduction_check.csv`: local
rel_mse == Colab rel_mse to 6 decimals on all 48 spot-checked cells — objects,
patterns, channel seeds identical).

## 1. Corrected counts (recount; details in `winner_table.md`)

Equal-frame winner map: **45 cells (9 rho x 5 sigma), 29 above-floor
(relMSE < 0.5), 28 won by srht_paired+pairwise, 1 won by
hadamard_random_paired+scgi_proxy (rho=0.3, sigma=0.15), 16 at noise floor.**
The audit's 45/29/28/1/16 is CONFIRMED; the manuscript's "all 28 of 44" is wrong.
All-non-oracle scope: 31 above-floor, all srht_paired+reference_k2, 14 floor
(not budget-matched: reference arms use 3073 frames vs 2048).

## 2. Conventions and measured constants (zero fitted parameters)

- Simulator OU log-gain: AR(1) with phi = exp(-rho), stationary std sigma_a;
  hadamard_paired emits +/- masks on adjacent frames, so the simulator's rho IS
  Prop 3's rho_pair (adjacent-pair decorrelation), s = sigma_a, r(rho)=1-e^-rho.
  N = 2048 frames both arms, K = 1024, no read/Poisson noise (noise terms = 0).
- Per object (n=10): K_eff = 234-401, D_H = 0.9926-0.9961 (`prop3_constants.csv`).
- Pipeline C0 (definition F.9, clean-gain DGI relMSE x N with the exact
  dense-run basis): 624-715 across objects (C0/N = 0.30-0.35). The grid's
  oracle-corrected random arm sits at relMSE = 0.3286 flat across ALL
  (rho, sigma) — C0/N confirmed exactly.
- Raw-correlator constant (F.10 with measured pattern moments mu=0.4999,
  sigma=0.2887, gamma3=0.0002, beta4=1.800): C0_ideal = 7.2e5-1.2e6 per object.
- v_blind(rho, sigma) measured from the gain-estimator subsystem
  (`gain_rel_mse` of agc / scgi_proxy vs true gains), per (rho, sigma, object).

## 3. Results of the no-free-parameter test

**A. Skeleton test (the F.12 boundary with v = 0): VALIDATED within factor ~1.5.**
Ordered pairwise Hadamard (blind pairwise normalization) vs gain-known (oracle)
random+DGI, grid data. Prediction rho* = -log(1 - 2(C0/N)/(K_eff D_H s^2)).
42/50 (sigma, object) cells show an observed crossing; median
|log10(pred/emp)| = 0.187 -> **median agreement factor 1.54**, 95% within
factor 2. Restricted to sigma >= 0.1 (40 cells, small-drift regime intact):
**40/40 within factor 2**, max factor 1.73. Prediction is systematically EARLY
(median log-ratio -0.187), consistent with F.8's O(Delta^3) corrections and the
scale-aligned-metric compression near the crossing. Empirical sigma-scaling
exponent -2.11 (R^2 = 0.976) vs predicted -2.07 — the sigma^-2 leading-order
law is correct. At sigma = 0.05 the prediction Q = 0.68-1.12 is near-critical
and 8/10 cells are not_reached — qualitatively consistent censoring.
(`prop3_skeleton_oracle_test.csv`)

**B. Pair-arm ingredient (F.8): essentially exact.** Measured pairwise-Hadamard
relMSE vs (1/2) K_eff D_H s^2 (1-e^-rho): median measured/predicted = 0.997,
IQR [0.948, 1.017] over 639 cells with predicted relMSE in (1e-4, 0.2).
(`prop3_pair_gain_ingredient.csv`)

**C. Blind arm as written: FAILS, and the failure is localized to one constant.**
For the comparison Prop 3 addresses with a BLIND random arm (agc or scgi_proxy
windowed correction), the predicted flips (rho* = 0.007-0.33 for sigma >= 0.1)
NEVER occur: in all 100 (source x correction x sigma x object) cells, ordered
pairwise Hadamard stays strictly better than blind random+DGI over the entire
scanned range rho in [0.001, 20], sigma in [0.05, 0.5]
(`prop3_prediction_vs_empirical.csv`: emp_status = not_reached everywhere).
Diagnosis (white-drift rho=10 test, `prop3_random_arm_leverage_test.csv`): the
residual-gain term of (F.11), (1+C0_pipeline) v / N, underpredicts the measured
random-arm drift excess by a median factor **1364 (none) / 1527 (agc) / 1521
(scgi_proxy)**. Replacing the leverage constant with the raw-correlator
1 + C0_ideal of (F.10) — still measured, no fitted parameters — reproduces the
measured excess to 0.3-4.7% (median ratio 1.003 / 1.047 / 1.039; aligned-metric
error ~0.002-0.003 in log10). Mechanism: mean subtraction removes the
K_eff*K*(mu/sigma)^2 background penalty from the SAMPLING floor (hence
C0_pipeline ~ 675) but NOT from the DRIFT leverage — a time-varying gain
modulates the large DC bucket coherently, and the correlator pays the full
raw-correlator constant (~9.5e5). This is the asymmetry the paper's own F.3.3
warning ("mean subtraction ... changes the constant") fails to apply to the
gain term of (F.11).

**D. Corrected-constant consistency: 100/100.** With the corrected leverage,
Q(rho) > r(rho) for every rho at every grid (sigma, object) for both blind
corrections — the theory then predicts NO flip in range, exactly matching the
100/100 empirical no-flip. (`prop3_correctedC0_noflip_consistency.csv`)

## 4. Verdict

Mixed, and sharper than the three canned options:

- **(ii) for the boundary skeleton**: leading-order form right (sigma^-2
  scaling confirmed, exponent -2.11 vs -2.07), constant off by factor ~1.5
  (systematically early), validated with zero fitted parameters — but only for
  a gain-known (v = 0) random arm.
- **(iii) for the blind-arm claim as written**: the (1+C0)v_blind/N term uses
  the wrong constant (pipeline C0 instead of raw-correlator C0_ideal, a ~1.4e3x
  error). Consequently there is NO Prop-3 flip anywhere in the published Fig. 5
  data for the blind pipeline, and the crossings shown in Fig. 5 are
  SRHT-paired-vs-ordered-Hadamard — a comparison Prop 3 explicitly does not
  rank ("What Prop 3 does not claim") — summarized by free two-parameter
  power-law fits (exponents -0.94 to -1.93, not the sigma^-2 form).
  **The text MUST downgrade Fig. 5's boundary panel to "empirical SRHT
  crossover"** and may add the skeleton test (A) as the actual Prop-3
  validation. With the corrected leverage constant the no-flip observation is
  itself a confirmed prediction (D).

## 5. File inventory

- `winner_table.md`, `winner_table_cells.csv`, `recount_counts.json` — recount.
- `prop3_constants.csv` — per-object K_eff, D_H, C0_pipeline (+ clean floors).
- `prop3_curves_local.csv` — fine two-arm scan (33 rho x 5 sigma x 10 objects
  x 5 seeds), bit-compatible with the dense grid.
- `prop3_prediction_vs_empirical.csv` — per-cell predicted (full / v0 /
  leading-order) vs empirical crossing, both data sources, blind arms.
- `prop3_skeleton_oracle_test.csv` — the v=0 skeleton test (verdict A).
- `prop3_pair_gain_ingredient.csv` — F.8 check (verdict B).
- `prop3_random_arm_leverage_test.csv` — leverage diagnosis (verdict C).
- `prop3_correctedC0_noflip_consistency.csv` — corrected-constant check (D).
- `prop3_agreement_summary.csv`, `prop3_verdict_summary.json` — machine-readable
  agreement numbers.
- `reproduction_check.csv` — local-vs-Colab bit-compatibility.
- `run_manifest.json`, `run_log.txt` — provenance for the local compute.
