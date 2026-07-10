# Fig. 3 fairness re-run (r3_fair) — audit blocker P0-5

Runner: `run_paper_fig3_gain_error.py` (r3 additions), 20 drift seeds x 10 objects,
rho in {0.001, 0.01}, s = 0.1, seed 20240708, 31,600 rows, runtime 153 s (single
process; no sharding needed). Authoritative predecessor:
`results/paper_fig3_gain_error_e12_local_r1` (untouched, read-only input).

Column naming: `gain_rel_err_ratio` / `gain_rel_err_log` are the two estimators'
scale-aligned relative gain errors (the task sheet's `relmae_ratio` / `relmae_log`).
`gain_rel_err` is kept as a legacy duplicate of the ratio column.

## What changed vs. the published e12 protocol

1. **Matched budget (defect a).** The published run gave raw signed-Walsh arms
   1024 frames while every physical arm got 2048, yet the abstract called the
   comparison "matched-budget". New arms `hadamard_raw_ordered_2048` /
   `hadamard_raw_shuffled_2048` repeat the signed Walsh sequence twice (two full
   passes / shuffled over the full 2048 record) against the *same* 2048-frame
   drift trace as the physical arms. The single-pass arms are retained, clearly
   labelled `*_1024`, as the diagnostic.
2. **Theorem-B estimator (defect b).** The published experiment scored only
   `movmean(R,W)/mean(R)` (ratio AGC), but Theorem B analyzes windowed means of
   log R. Added `log_agc_gain` (src/paper_experiments.py): gain_hat proportional
   to exp(centered movmean(log R, W)), mean-normalized. Positivity guard =
   Theorem B assumption (iv) taken literally: frames with R <= 0 are excluded
   from the analyzed record (masked window mean); `frac_nonpos_carrier` reports
   the excluded fraction (~0 for physical arms, 0.583 for raw signed arms, which
   remain diagnostic-only per the manuscript's bucket convention (i)).
3. **Clustered bootstrap (defect c).** The published CIs resampled the 200
   object x seed cells as independent ("naive"), but the 20 seeds are reused
   across all 10 objects and vice versa. `fig3_bootstrap_cis.csv` reports each
   statistic under naive / seed_cluster / two_way (crossed seeds-and-objects)
   percentile bootstrap (B = 2000, seed 20240708).
   `fig3_bootstrap_cis_published_e12.csv` applies the identical machinery to the
   published CSV. Note: seed-only clustering *narrows* the CI (objects dominate
   the spread); the honest conservative scheme is the two-way crossed bootstrap,
   whose SRHT slope CI [-0.660, -0.415] is what the audit quoted as
   "seed-clustered [-0.662, -0.421]".

Statistics below: per-(object,seed) cell values at slow drift (rho = 0.001);
"slope" = fixed W<=16 log-log slope of error vs W (manuscript Table 1
convention); "best err" = per-cell minimum over W. Reported: median with 95% CIs
as naive | seed_cluster | two_way.

## W<=16 slope, old vs new (rho = 0.001)

| Arm | Published (naive) | r3 ratio estimator | r3 log estimator |
|---|---|---|---|
| srht_paired | -0.58 [-0.60,-0.54] | -0.575 [-0.602,-0.542] \| [-0.576,-0.565] \| [-0.660,-0.415] | -0.569 [-0.591,-0.542] \| [-0.571,-0.561] \| [-0.643,-0.419] |
| hadamard_random_paired | -0.62 [-0.64,-0.61] | -0.615 [-0.637,-0.605] \| [-0.621,-0.610] \| [-0.668,-0.441] | -0.449 [-0.455,-0.435] \| [-0.451,-0.443] \| [-0.497,-0.360] |
| random_binary | -0.41 [-0.42,-0.41] | -0.414 [-0.420,-0.404] \| [-0.415,-0.411] \| [-0.440,-0.371] | -0.414 [-0.421,-0.405] \| [-0.417,-0.413] \| [-0.438,-0.366] |
| random_uniform | -0.39 [-0.40,-0.37] | -0.386 [-0.399,-0.372] \| [-0.390,-0.381] \| [-0.424,-0.311] | -0.387 [-0.401,-0.375] \| [-0.391,-0.382] \| [-0.425,-0.321] |
| hadamard_paired (ordered) | +0.03 [-0.01,+0.04] | +0.029 [-0.006,+0.039] \| [+0.006,+0.033] \| [-0.059,+0.167] | -0.222 [-0.228,-0.207] \| [-0.226,-0.215] \| [-0.306,-0.054] |
| hadamard_raw_ordered (1024 -> 2048) | +0.020 (1024) | +0.016 [+0.012,+0.025] \| [+0.015,+0.018] \| [+0.001,+0.034] | -0.089 [-0.093,-0.084] \| [-0.092,-0.087] \| [-0.128,-0.019] |
| hadamard_raw_shuffled (1024 -> 2048) | -0.022 (1024) | -0.024 [-0.027,-0.021] \| [-0.026,-0.020] \| [-0.030,-0.010] | -0.294 [-0.321,-0.265] \| [-0.316,-0.276] \| [-0.371,-0.153] |

## Best-window blind gain error (median over cells, rho = 0.001)

Linear-scale medians (from log10_best_err), two-way CI in brackets:

| Arm | Published headline | r3 ratio (2048 budget) | r3 log (2048 budget) |
|---|---|---|---|
| hadamard_raw_ordered | ~0.96 flat ("0.95 at W=4, 0.90 at W=512"), 1024 frames | 0.898 [0.892, 0.903]; per-W mean 0.939-0.989, 0.950 at W=512 | 0.708 [0.563, 0.840]; per-W mean 0.699-0.788, non-decaying |
| hadamard_raw_shuffled | ~0.86 | 0.794 [0.775, 0.816] | 0.136 [0.083, 0.196] |
| srht_paired | ~0.02 | 0.0077 [0.0066, 0.0083] | 0.0079 [0.0065, 0.0086] |
| hadamard_random_paired | ~0.02 | 0.0073 [0.0063, 0.0079] | 0.0119 [0.0090, 0.0133] |
| random_uniform | ~0.02 | 0.0113 [0.0093, 0.0118] | 0.0113 [0.0093, 0.0118] |
| random_binary | ~0.02 | 0.0150 [0.0130, 0.0165] | 0.0150 [0.0128, 0.0166] |
| hadamard_paired (ordered) | -- | 0.0168 [0.0143, 0.0176] | 0.0222 [0.0193, 0.0248] |

Budget effect on raw arms (ratio estimator, median best-window): ordered
0.896 (1024) -> 0.899 (2048); shuffled 0.788 (1024) -> 0.794 (2048). Doubling the
raw budget changes nothing at the third decimal: the published contrast was not
a budget artifact — but the "matched-budget" label is only now literally true.

## Verdict on the paper's qualitative claims

- **Randomized << ordered raw: SURVIVES**, under both estimators, both budgets,
  and all three CI schemes, at both drift rates. Worst case for the claim is the
  raw shuffled arm under the Theorem-B log estimator (0.136 [0.083, 0.196]),
  still >= 12x above every randomized arm (<= 0.015).
- **SRHT best: SURVIVES with a tie.** SRHT and randomly permuted paired Hadamard
  are statistically indistinguishable at the top (best-err two-way CIs overlap;
  ratio-estimator medians 0.0077 vs 0.0073) — same as in the published data.
- **One estimator-specific nuance:** naturally ordered *paired* Hadamard shows
  no decay under the ratio AGC (slope +0.03, CI straddles 0) but a shallow decay
  under the log estimator (-0.222 [-0.306,-0.054] two-way) — still far outside
  the W^(-1/2) band, so the "ordered chronology defeats the variance law"
  conclusion stands, but "no detectable decay" should be attributed to the
  ratio-AGC estimator specifically.
- **CI widths:** two-way clustered CIs are ~3-5x wider than naive (e.g. SRHT
  slope [-0.60,-0.54] -> [-0.66,-0.41]); no interval widens across a qualitative
  boundary.

Files: `fig3_gain_est_error.csv` (per-cell rows, both estimators),
`fig3_slope_fits.csv`, `fig3_bootstrap_cis.csv` (new run, 3 schemes),
`fig3_bootstrap_cis_published_e12.csv` (published data, 3 schemes),
`fig3_gain_error_summary.csv`, `fig3_caption.md`, plots, `run_manifest.json`.
