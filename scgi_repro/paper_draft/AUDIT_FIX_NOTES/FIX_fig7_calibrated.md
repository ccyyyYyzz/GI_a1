# FIX (audit blocker P0-3): Fig. 7 now tests Theorem C's calibrated soft-log estimator

Date: 2026-07-10. Scope: `run_paper_fig7_lowphoton.py` + new results dir
`results/paper_fig7_lowphoton_r3_calibrated/`. No manuscript/LaTeX text was edited;
`results/paper_fig7_lowphoton_r2/` is preserved unchanged for provenance.

## 1. What Theorem C's estimator actually is

Sec. 6 of `MANUSCRIPT_DRAFT.md` and Appendix D.4 analyze the *calibrated* windowed
soft-log: average psi_alpha(c) = log(c + alpha) over a window W and **invert the
calibration curve**, theta_hat_n = m_alpha^{-1}(mean_W psi_alpha), where
m_alpha(theta) = E[log(C + alpha)] for C ~ Pois(lambda(theta)). The rate constants
kappa_min <= m_alpha'(theta) <= kappa_max in Theorem C / (D.8)-(D.9) are properties of
this calibration curve; without the inversion they have nothing to attach to.
Equivalently in the lambda parametrization: invert m_alpha(lambda) =
E[log(Poisson(lambda) + alpha)] to get a lambda-profile, take its log, and remove the
mean (the centered-log-gain gauge). The mean-normalization absorbs the additive gauge
constant, so inverting in lambda and normalizing is exactly the theorem's estimator up
to the global-scale gauge the paper already declares unrecoverable.

## 2. What was wrong (audit confirmed on all points)

1. `run_paper_fig7_lowphoton.py::estimate_from_counts` implemented only an
   **uncalibrated proxy**: `soft_log = exp(movmean(log(C+alpha)) - mean(...))`, with no
   m_alpha^{-1} anywhere in the repo's Fig. 7 path. Published Fig. 7 (r2) therefore did
   not test Theorem C's estimator.
2. Ratio bookkeeping: the correct r2 ratios are naive/soft = 22.92-46.39x,
   naive/Anscombe = 19.48-29.99x, Anscombe/soft = 1.18-1.55x (budgets <= 1). Any
   caption implying soft/Anscombe ~ 19.5-30x is wrong: 19.5-30x is
   **naive-over-Anscombe**; soft-log beats Anscombe by only 1.18-1.55x, and that
   margin is itself a shrinkage-bias artifact (see 4c below).
3. `results/paper_fig7_lowphoton_r2/fig7_caption.md` carried a "[Post-hoc correction,
   no rerun]" note because the runner's `fisher_slope()` filtered on the realized
   `lambda_bar_mean`, silently dropping the budget=16/32 endpoints (native -0.89/-0.65
   vs corrected -0.91/-0.73).

## 3. What was implemented

In `run_paper_fig7_lowphoton.py` (legacy arms bit-identical, checked against r2):

- **`SoftLogCalibration`**: m_alpha(lambda) = E[log(Poisson(lambda)+alpha)] tabulated
  **exactly** (truncated Poisson sum, no Monte Carlo) on a 3000-point log grid over
  lambda in [2.5e-4, 1.28e4] (experiment range 0.25-128 with >=2 decades margin each
  side). Rigorous truncation: for Cmax >= lambda, P(c+1)/P(c) <= r = lambda/(Cmax+1)
  and log(c+alpha) <= log(Cmax+alpha) + (c-Cmax)/(Cmax+alpha) bound the neglected tail
  by P(Cmax)[log(Cmax+alpha) r/(1-r) + r/((Cmax+alpha)(1-r)^2)]; Cmax grows until this
  is < 1e-12 (achieved max bound 3.5e-34). Strict monotonicity is asserted; inversion
  is monotone interpolation of log(lambda) vs m. Unit checks: matches 4M-sample Monte
  Carlo within MC error at lambda in {0.1,...,500}; round-trip error 1.1e-14.
- **`soft_log_calibrated` arm**: per-window mean of log(C+alpha) -> m_alpha^{-1} ->
  lambda-profile -> normalized by its mean, identical post-processing to all other arms.
- **Native honest reporting**: `fisher_slope()` now filters on the nominal
  `photon_budget` design column (endpoints included) — the r3 native soft_log slopes
  (-0.910 / -0.730) equal r2's post-hoc-corrected values to 13 digits, so no post-hoc
  note is needed. The runner also emits `fig7_ratio_table.csv` (all six named pairwise
  ratios per budget), `m_alpha_calibration_table.csv`, and a native `summary.md`.
- Default output dir changed to `results/paper_fig7_lowphoton_r3_calibrated` so a bare
  rerun can never clobber the archived r2.

Full protocol rerun with the exact r2 manifest args (10 objects, 5 seeds, seed
20240708, rho=1e-3, s=0.1, W=64, alpha=0.5, budgets 0.25..128, floor-probe
rho=1e-4), 2000 rows + floorprobe: `results/paper_fig7_lowphoton_r3_calibrated/`.

## 4. New numbers (r3, mean gain relMSE over 10 objects x 5 seeds)

(a) Per-budget MSE, all arms: see `summary.md` section (a). Highlights (budget: calibrated
vs Fisher reference 1/(W lambda)): 0.25: 6.46e-2 vs 6.25e-2 (1.03x); 0.5: 3.39e-2 vs
3.13e-2 (1.09x); 1: 2.05e-2 vs 1.56e-2 (1.31x); 128: 2.78e-4 (drift-limited floor,
falls to 1.73e-4 at rho=1e-4, same as the proxy).

(b) Pairwise mean-MSE ratios over budgets <= 1 (numerator/denominator as named):

| pair | range (budgets <= 1) |
|---|---|
| naive/soft | 22.92-46.39x |
| naive/Anscombe | 19.48-29.99x |
| Anscombe/soft | 1.18-1.55x |
| naive/calibrated | 3.84-10.69x |
| Anscombe/calibrated | 0.13-0.55x (i.e. Anscombe is 1.8-7.8x BETTER than calibrated here) |
| calibrated/soft | 2.14-12.08x (calibrated pays this over the biased proxy here) |

All six converge to 1.00 (within +-4%) for budgets >= 32. Full table: `fig7_ratio_table.csv`.

(c) Fitted log-log slopes of MSE vs budget (1/(W lambda) law => -1):

| arm | budgets [2,32] | budgets [1,16] |
|---|---|---|
| soft_log (proxy) | -0.910 | -0.730 |
| soft_log_calibrated | -0.974 | -0.981 |
| naive_log | -1.837 | -1.939 |
| anscombe | -0.875 | -0.786 |

The calibrated estimator is the only arm whose slope stays ~ -1 across both fit
windows: the proxy's shallowing to -0.73 on [1,16] was contamination by its own
bias transition, which calibration removes.

(d) Qualitative conclusions that change:

- **Calibrated soft-log does NOT beat Anscombe** in mean MSE at any tested budget; at
  budgets <= 1 Anscombe is 1.8-7.8x better. The old "soft-log beats Anscombe" reading
  (1.18-1.55x, proxy arm) was a shrinkage-bias artifact, not an efficiency gain.
- **Shrinkage bias relocates exactly as Sec. 6's caveat predicts.** The proxy sits
  BELOW the unbiased local Fisher reference at budgets 0.25/0.5/1 (bias, not
  super-efficiency); the calibrated estimator is never sub-Fisher — it tracks the
  Fisher curve from above within 3-31% for budgets <= 1, within 1.3-1.5x through the
  variance regime [2,32], with the excess growing to 2.3x only at budget 128 where the
  drift-limited floor takes over. Anscombe is the most bias-dominated arm at 0.25
  (0.13x Fisher).
- **Theorem C's variance story is confirmed, and cleanly, by its own estimator**: slope
  -0.97/-0.98 vs the -1 law, with no bias crossover to excuse. What the calibrated
  estimator gives up is the (uncontrolled, bias-driven) low-count MSE discount of the
  proxy and of Anscombe — the "honest accounting" the manuscript already promises.

## 5. Caption-ready sentences for the revised Fig. 7

1. "At mean counts lambda_bar <= 1, the naive clipped log is 23-46x worse than the
   uncalibrated soft-log proxy, 19.5-30x worse than Anscombe, and 3.8-10.7x worse than
   the calibrated soft-log of Theorem C (all ratios are naive-over-method mean MSE)."
2. "The calibrated estimator m_alpha^{-1}(mean_W log(C+alpha)) is the only arm that
   tracks the Fisher-matched 1/(W lambda) law across the full variance regime (fitted
   log-log slope -0.97 on lambda_bar in [2,32] and -0.98 on [1,16], against -0.91 and
   -0.73 for the uncalibrated proxy, whose [1,16] fit is contaminated by its bias
   transition)."
3. "Below lambda_bar ~ 1 the uncalibrated proxy and Anscombe fall below the unbiased
   local Fisher reference — a shrinkage-bias signature, not super-efficiency — whereas
   the calibrated estimator stays within 3-31% above it; consequently Anscombe's
   1.8-7.8x mean-MSE advantage over the calibrated estimator in this regime is
   bias-bought, exactly the trade-off the Sec. 6 caveat describes."
4. "At the high-photon end all soft-log arms meet a drift-limited floor (gain MSE
   2.78e-4 at rho = 1e-3, falling to 1.73e-4 at rho = 1e-4), unchanged by calibration."

## 6. Files

- Runner (modified): `run_paper_fig7_lowphoton.py`
- New results: `results/paper_fig7_lowphoton_r3_calibrated/{fig7_lowphoton.csv,
  fig7_lowphoton_floorprobe.csv, fig7_lowphoton_summary.csv, fig7_ratio_table.csv,
  m_alpha_calibration_table.csv, fig7_gainMSE_vs_photon.png, fig7_caption.md,
  summary.md, run_manifest.json}`
- Archived (untouched): `results/paper_fig7_lowphoton_r2/`
