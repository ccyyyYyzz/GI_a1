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

---

# E1 (second-round audit): Theorem C chain repair — carrier-aware calibration, finite-W bound, log-domain metric

Date: 2026-07-10, Wave E1. Scope: `run_paper_fig7_lowphoton.py`, NEW results dir
`results/paper_fig7_lowphoton_r4_carrier/` (r3 dir untouched, archived), Appendix D.4
rewritten in `paper_draft/latex/appendix_body.tex` + `paper_draft/APPENDICES.md`, plus
the Prop 3 Q<=0 sign fix (F.4) in both. body.tex / supplement.tex / MANUSCRIPT_DRAFT.md
were NOT touched (owned by other agents); required edits there are listed in E1.5.

## E1.1 What was wrong (six audited findings, all verified)

1. **(F1) Calibration omitted the random carrier.** Theorem C's m_alpha takes the
   expectation over the carrier (and dark counts); the r3 `SoftLogCalibration` tabulated
   only homogeneous Poisson(lambda) (carrier == 1, d = 0) and applied the homogeneous
   inverse to frame-varying carriers. The r3 arm was therefore a "mean-Poisson calibrated
   proxy", not the theorem's estimator (numerical impact small at this carrier CV — see
   E1.3 — so r3 data is not invalidated, but the estimator identity claim was wrong).
2. **(F2) The finite-W risk bound (D.8) was FALSE as stated.** It used the SIGNED
   long-run variance sigma_{alpha,LR}^2 = sum_h gamma(h) as a finite-W variance bound.
   Counterexample: z_n = eps_n - eps_{n-1} has zero long-run variance but window-mean
   variance 2 sigma^2 / W^2 > 0. The signed sum is only the asymptotic (W -> infinity)
   constant; the valid finite-W constant is sigma_abs^2 = sum_h |gamma(h)| (absolutely
   summable autocovariances), exactly as Lemma D.1 already stated.
3. **(F3) beta > 1 composite-bias gap.** The proof transferred the W^beta window bias
   through the nonlinear m_alpha by Lipschitz continuity; that preserves only beta <= 1
   (the beta in (1,2] case of (D.1) relies on SIGNED cancellation in centered windows,
   which composition with m_alpha destroys). The statement admitted beta in (0,2].
4. **(F4) Truncation undefined.** The theory's inverse hits -infinity on all-zero
   windows; the code silently clamped via interpolation ends. The clamp was not part of
   the stated estimator and its probability/bias cost was not bounded.
5. **(F5) Metric mismatch.** Fig. 7 reported gain-domain scale-aligned relMSE but
   compared it to the LOG-intensity Fisher rate 1/(W*lambda). "Never sub-Fisher",
   "within 3-31%", and "minimax-rate-optimal" were stated across mismatched metrics.
6. **(F6) Prop 3 Q<=0 sign error (Appendix F.4).** With rho* = inf{rho : R_pair >=
   R_rand}, Q<=0 means the random arm is already AT LEAST AS GOOD at rho = 0, hence
   rho* = 0 (immediate flip); the text said "random already worse" — backwards.

## E1.2 What changed

Runner (`run_paper_fig7_lowphoton.py`; legacy arms verified bit-identical to r3,
max |r3-r4| mean gain relMSE = 0.0 over all 40 shared (arm, budget) cells):

- NEW arm `soft_log_calibrated_carrier` = Theorem C's estimator: per window solve
  (1/W) sum_k m_alpha(theta_hat * b_k) = (1/W) sum_k log(C_k + alpha) with the KNOWN
  per-frame carrier intensities b_k (design values; d = 0), by 60-step monotone
  bisection in log(theta) reusing the exact homogeneous table (key identity:
  E[log(Pois(theta*b)+alpha)] = m_alpha(theta*b), same curve). Window membership
  replicates `moving_average_1d` exactly (odd width 65, replicate padding; verified to
  1e-15). theta_hat is clamped to [lam_lo/max(b), lam_hi/min(b)] — the theorem's clamp;
  all-zero windows return the lower end. Unit checks: constant carrier reproduces the
  homogeneous inversion to 2e-7; varying-carrier variance matches the exact
  multiplicity-correct conditional prediction (0.0030 predicted vs 0.0026 empirical
  with centering; interior windows 0.00178 vs 0.00176).
- Previous `soft_log_calibrated` arm KEPT, relabeled mean-Poisson calibrated proxy.
- NEW primary metric `log_gain_mse` = mean_n[((log ghat - mean log ghat) -
  (log g - mean log g))^2] — Theorem C's centered-log-gain loss, the only metric
  comparable to 1/(W*lambda). All Fisher comparisons, sub-Fisher flags, slopes, and a
  new per-budget Fisher-excess table (`fig7_fisher_excess_logdomain.csv`) use it.
  `gain_rel_mse` kept as labeled continuity column; the gain-domain figure no longer
  draws the Fisher line. New primary figure `fig7_logMSE_vs_photon.png`.
- Full r3-protocol rerun -> `results/paper_fig7_lowphoton_r4_carrier/` (2500 rows +
  floor probe; run_manifest.json carries both slope sets, Fisher-excess, and the
  carrier-solver convention).

Appendix D.4 (both appendix_body.tex and APPENDICES.md), restated and re-proved:

- Estimator (D.8a) is now the carrier-aware window-calibration root WITH the clamp as
  part of the definition (generalized monotone inverse + clip to the operating range).
- (D.8) variance term now carries sigma_bar_alpha^2 (sup of Var log(Pois(lambda)+alpha)
  on the operating intensity range): with KNOWN carriers the counts are conditionally
  independent given the gain path, so Var(window mean) = W^-2 sum_k Var psi_alpha(C_k)
  <= sigma_bar_alpha^2 / W is a finite-W IDENTITY — no mixing, no long-run variance.
  (D.8) gains the explicit clamp term (theta_max-theta_min)^2 P(clamp).
- Remark D.4.3 handles the unknown-random-carrier variant: marginal calibration curve,
  finite-W bound via W^-1 sum_{|h|<W} (1-|h|/W) gamma(h) <= sigma_{psi,abs}^2 / W with
  absolute summability derived from the standing mixing assumptions via Davydov (the
  Poisson randomization is conditionally independent, so (B_n, C_n) inherits the
  carrier's mixing coefficients); the signed sigma_LR^2 is restated as the W->infinity
  asymptotic equality ONLY, with the eps-differencing counterexample recorded.
- Smoothness hypothesis restricted to beta in (0,1] with the POINTWISE Hoelder modulus;
  Remark D.4.2 explains why (triangle inequality cannot exploit sign cancellation
  through the nonlinear m_alpha) and labels any beta in (1,2] calibrated rate an open
  conjecture. Operative case beta = 1 unaffected.
- Remark D.4.4 bounds the clamp event: E_n^c subset {|y_n - M_n(ell_n)| >= kappa_min *
  Delta} (margin Delta), Chebyshev gives P <= (bias^2 + sigma_bar^2/W)/(kappa_min *
  Delta)^2 — same 1/W order, absorbed; exact all-zero-window probability
  exp(-sum_k lambda_k) <= exp(-W lambda_minus) ~ 1e-7 per window at the most starved
  grid point. Clamp bias contribution <= (theta_max-theta_min)^2 P(E_n^c).
- The theorem's loss is now EXPLICITLY the log-domain squared error, and the van Trees
  / minimax-order-sharpness sentence is stated in that loss only.
- Remark D.4.1 records the Fig. 7 instantiation (d = 0, known design carriers, gauge by
  record-mean centering) and names the r3 arm a mean-Poisson proxy.
- F6: the Q<=0 sentence in Prop 3 (F.4) now reads "random/DGI already at least as good
  at rho = 0 ... so rho* = 0 — the flip is immediate, not absent" (both files).

## E1.3 Old vs new numbers (r4; 10 objects x 5 seeds, W=64, alpha=0.5, rho=1e-3)

Proxy vs carrier-aware (log-domain mean-MSE ratio meanpois/carrier): 0.998-1.007 for
budgets <= 4 — the auditor's <0.3% impact estimate confirmed where photons are scarce —
growing to 1.06 / 1.09 / 1.14 at budgets 32 / 64 / 128: at the drift-limited floor the
carrier-aware estimator is strictly BETTER, because it deconvolves the known carrier
exactly instead of leaving a Jensen-gap floor (floor 2.446e-4 vs proxy 2.792e-4 at
rho=1e-3; 1.362e-4 vs 1.726e-4 at rho=1e-4 — floor remains drift-limited).

Gain-domain vs log-domain (the metric correction, carrier-aware arm):

| quantity | r3 claim (gain-domain, proxy arm) | r4 honest (log-domain, carrier arm) |
|---|---|---|
| Fisher excess, budgets <= 1 | "3-31% above" | 1.112-1.421x (11-42% above) |
| Fisher excess, [2,32] | "1.3-1.5x" | 1.228-1.492x |
| Fisher excess at 128 (drift floor) | 2.3x | 2.004x |
| sub-Fisher budgets (calibrated arm) | none | none (min excess 1.112) |
| slope [2,32] / [1,16] | -0.974 / -0.981 | -1.025 / -1.030 |
| naive/calibrated, budgets <= 1 | 3.8-10.7x | 2.01-11.03x |
| Anscombe/calibrated, budgets <= 1 | 0.13-0.55 | 0.114-0.521 |
| calibrated/soft, budgets <= 1 | 2.14-12.08x | 2.29-13.43x |

Unchanged qualitative story (all in the correct log-domain metric now): the calibrated
estimator is the only arm tracking the 1/(W*lambda) law across both fit windows
(-1.025/-1.030 vs soft-log proxy -0.930/-0.739, Anscombe -0.893/-0.802, naive
-1.97/-2.02); the uncalibrated proxy IS sub-Fisher at budgets 0.25/0.5/1 (log-domain
confirmed: 0.083/0.217/0.619x Fisher) — shrinkage bias, exactly as the Sec. 6 caveat
says; Anscombe beats the calibrated arm at budgets <= 8 (bias-bought) and loses to it
at budgets >= 16; all naive/soft/Anscombe ratios converge to 1 at high budgets.

## E1.4 Verification

- Unit: constant-carrier equivalence 2e-7; window-index mirror 1e-15; exact conditional
  variance match (interior 0.00178 pred vs 0.00176); all-zero record clamps finite.
- Reproduction: all 40 shared (arm, budget) mean-relMSE cells identical to r3 (diff 0.0).
- LaTeX: supplement.tex (which inputs appendix_body.tex) compiles clean (2 passes,
  exit 0). main.tex currently FAILS at an undefined macro \EEprobe at main.tex:62 —
  that line is a concurrent agent's in-flight probe edit in main.tex (not one of E1's
  files; appendix_body.tex is not input by main.tex). Final compile harmony is a later
  wave per the wave plan.

## E1.5 For the body.tex / supplement.tex owners (claims to DELETE and replacements)

body.tex Sec. 6 (Theorem C display, ~line 171): replace
sigma_{alpha,LR}^{4beta/(2beta+1)} by bar-sigma_alpha^{4beta/(2beta+1)} and "the
standard nonparametric rate in the effective per-frame noise sigma_{alpha,LR}" by "the
standard nonparametric rate in the effective per-frame noise bar-sigma_alpha
(operating-range bound on the per-count soft-log variance; Appendix D.4)". If the
main-text theorem states a smoothness range, restrict to beta in (0,1].

body.tex Sec. 9.5 "Low-photon robustness" paragraph (~line 304) — sentences to DELETE
and their replacements:

- DELETE "whereas the calibrated estimator is never sub-Fisher, staying within 3-31%
  above the reference at lambda_bar <= 1".
  REPLACE with: "whereas the calibrated estimator stays above the reference at every
  tested budget (no sub-Fisher cell on this grid), within 11-42% of it at
  lambda_bar <= 1 and within 23-49% through the variance regime lambda_bar in [2,32]
  (log-domain loss)."
- DELETE the slope sentence values "-0.974 / -0.981 vs -0.910 / -0.730"; REPLACE with
  "-1.025 over lambda_bar in [2,32] and -1.030 over [1,16], against -0.930 and -0.739
  for the proxy" (log-domain).
- DELETE "3.8-10.7x worse than the calibrated estimator"; REPLACE with "2.0-11.0x worse
  than the calibrated estimator". Also update naive/soft to 25.3-30.2x, naive/Anscombe
  to 17.6-21.2x, Anscombe-over-calibrated to 0.11-0.52 (i.e. Anscombe 1.9-8.8x better
  there), and proxy-over-Anscombe ("1.18-1.55x") to 1.19-1.53x — IF the paragraph
  adopts the log-domain metric, which it must for every Fisher-adjacent sentence;
  gain-domain versions may be quoted only if labeled "gain-domain (not
  Fisher-comparable)".
- DELETE the floor values "2.78e-4 -> 1.73e-4 identically for the proxy and the
  calibrated arm"; REPLACE with: "gain MSE 2.79e-4 at rho=1e-3 falling to 1.73e-4 at
  rho=1e-4 for the proxy arms, and 2.45e-4 falling to 1.36e-4 for the carrier-aware
  estimator, which sits ~12% below the proxies at the floor because it deconvolves the
  known carrier exactly (log-domain)."
- "minimax-rate-optimal" (conclusion + Theorem D sentence): keep ONLY with the two
  qualifiers "at rate level, in the log-domain loss" for anything referencing Theorem
  C / Fig. 7; the Theorems B-D windowed-estimator sentence itself is unaffected (linear
  theory), but must not be cited as covering the calibrated estimator for beta > 1.
- Estimator naming: the Fig. 7 arm to headline is now "the calibrated soft-log of
  Theorem C, solving (1/W) sum_k m_alpha(theta_hat b_k) = (1/W) sum_k psi_alpha(C_k)
  with known carriers b_k" (the old theta_hat = m_alpha^{-1}(mean_W psi_alpha) formula
  is the mean-Poisson proxy; if kept in text, label it as such).
- Figure asset: the primary panel should switch to
  `results/paper_fig7_lowphoton_r4_carrier/fig7_logMSE_vs_photon.png` (y-axis:
  centered-log-gain MSE; the Fisher dashed line is valid there); the gain-domain PNG no
  longer draws the Fisher line. `paper_draft/latex/figs/fig7_gainMSE_vs_photon.png` is
  the stale r3 asset.

supplement.tex (~line 123, Fig. S4(b) floor sentence): update the floor numbers as in
the floor bullet above and drop "identically for the uncalibrated proxy and the
calibrated soft-log estimator" (the carrier-aware arm's floor is ~12% lower, not
identical); data now at `results/paper_fig7_lowphoton_r4_carrier/`.

Caption-ready sentences (log-domain, carrier-aware arm) are in
`results/paper_fig7_lowphoton_r4_carrier/fig7_caption.md`.

---

# E5 (Wave E5a, R12 integration): edge-window fix, oracle relabel, local Fisher reference, safe bracket, measured eps_cal — Fig. 7 r5

Date: 2026-07-10, Wave E5a. Scope: `run_paper_fig7_lowphoton.py`, NEW results dir
`results/paper_fig7_lowphoton_r5_final/` (r4 dir untouched, archived), Appendix D.4
replaced per `paper_draft/REVIEWS/GPT_R12_appendixD_rederivation.md` (R12-A..E) in
`appendix_body.tex` + `APPENDICES.md`, Fig. 7 numbers resynced in body.tex Sec. 6/9.5 +
caption, MANUSCRIPT_DRAFT.md, supplement.tex S1/S4/S5, and the fig7/figS4 sections of
`paper_draft/latex/make_pub_figures.py` retargeted to r5 (fig7 log-domain panel now
emitted natively — closes the hand-copied-asset flag).

## E5.1 Code changes (all six R12 implementation flags)

1. **Replicate padding REMOVED** (R12 counterexample 1: a padded width-65 edge window
   is 33 copies of frame 0 + frames 1..32, effective size 65^2/(33^2+32) = 3.77, up to
   17.25x the claimed sigma^2/65 variance). ALL windowed arms (soft_log,
   soft_log_calibrated, naive_log, anscombe, and the carrier window solver) now use
   truncated, RENORMALIZED windows over distinct in-record frames (equal weights
   w_k = 1/|I_n|), via `moving_average_truncated` / `_window_membership`. Interior
   windows are computed from the identical member sets (bit-identical by construction —
   verified, see E5.3).
2. **Oracle relabel**: the carrier-aware arm is renamed
   `soft_log_calibrated_carrier_oracle`; summary/caption/manifest state the carriers
   are supplied from the SIMULATION TRUTH (flat-field-calibrated benchmark), not
   "programmed design intensities"; manifest carries `oracle_carrier: true`.
3. **Fisher reference is now LOCAL realized information**: per window
   I_n = sum_{k in I_n} lambda_k (d=0), reference = mean_n[1/I_n], computed over the
   same distinct members as the estimators; the old global nominal 1/(W*lambda_bar) is
   kept as the secondary column `fisher_reference_nominal` and a dotted line.
4. **Operating-range bracket fixed to the SAFE interval**
   [lam_lo/min(b), lam_hi/max(b)] per window (ALL bisection evaluations stay in-table;
   the old [lam_lo/max(b), lam_hi/min(b)] let extreme carriers evaluate the constant
   extension); clamp takes over outside; documented in the solver docstring.
5. **Interpolation acknowledged empirically**: eps_cal = max |m_alpha - interp| on the
   2999-midpoint dense check grid (exact truncated-Poisson recomputation as ground
   truth) = **1.64e-06** (near lambda = 0.92); bisection resolution eps_bis <=
   log(lam_hi/lam_lo) * 2^-60 = **1.54e-17** (log-theta units). Both printed into
   summary.md; the (eps_cal + eps_bis)^2 / kappa_lower^2 risk term and the
   eps_cal + eps_bis clamp-margin shrinkage are stated in Remark D.4.1 (quoting the
   measured value) — an empirical measurement honestly labeled, not a certified bound.
6. **alpha -> 0 non-uniformity** recorded in the low-photon corollary text (fixed-alpha
   theorem, not a triangular alpha -> 0 asymptotic).

## E5.2 Old (r4) -> new (r5) headline numbers (log-domain, 10 objects x 5 seeds)

Legacy arms change ONLY through the 64/2048 edge windows (3.1% of frames) and, for the
Fisher-relative quantities, through the new LOCAL reference.

| quantity | r4 (padded windows, nominal 1/(W*lambda)) | r5 (truncated windows, local mean_n[1/I_n]) |
|---|---|---|
| slope [2,32] / [1,16], oracle-carrier | -1.025 / -1.030 | **-1.000 / -1.002** |
| slope [2,32] / [1,16], mean-Poisson proxy | -1.008 / -1.017 | -0.986 / -0.992 |
| slope [2,32] / [1,16], uncalibrated proxy | -0.930 / -0.739 | -0.920 / -0.732 |
| slope [2,32] / [1,16], Anscombe | -0.893 / -0.802 | -0.882 / -0.797 |
| slope [2,32] / [1,16], naive | -1.972 / -2.015 | -1.963 / -2.001 |
| naive/soft, budgets <= 1 | 25.3-30.2x | 24.9-28.7x |
| naive/Anscombe, budgets <= 1 | 17.6-21.2x | 16.3-21.0x |
| naive/carrier, budgets <= 1 | 2.0-11.0x | 1.8-11.4x |
| Anscombe/carrier, budgets <= 1 | 0.11-0.52 | 0.11-0.54 (Anscombe 1.8-8.9x better) |
| carrier/soft, budgets <= 1 | 2.29-13.43x | 2.19-13.67x |
| meanpois/carrier, budgets <= 1 | 0.998-1.001 | 0.999-1.004 |
| Fisher excess (carrier), budgets <= 1 | 1.112-1.421x (11-42%) | **1.023-1.184x (2-18%)** |
| Fisher excess (carrier), [2,32] | 1.228-1.492x (23-49%) | **1.138-1.311x (14-31%)** |
| Fisher excess (carrier) at 128 (drift floor) | 2.004x | 1.776x |
| sub-Fisher budgets, carrier arm | none | none (min excess 1.023) |
| sub-Fisher budgets, uncalibrated proxy | 0.25/0.5/1 | 0.25/0.5/1/2 (vs the larger local ref.) |
| carrier overtakes Anscombe at | >= 16 | >= 32 |
| drift floor, proxy arms (rho 1e-3 -> 1e-4) | 2.79e-4 -> 1.73e-4 | 2.43e-4 -> 1.41e-4 |
| drift floor, carrier arm (rho 1e-3 -> 1e-4) | 2.45e-4 -> 1.36e-4 (~12% lower) | 2.17e-4 -> 1.13e-4 (~11% lower) |

The floor drop (2.79e-4 -> 2.43e-4 for the proxies) is the edge-window repair itself:
replicate-padded edge windows carried up to 17x the interior variance and inflated the
frame-averaged MSE; truncating and renormalizing them removes that inflation. The
Fisher-excess tightening (11-42% -> 2-18%) has two causes: the local reference
mean_n[1/I_n] is slightly LARGER than nominal 1/(64*lambda_bar) (65 distinct interior
members + Jensen), and the edge windows no longer pay the padding variance penalty.
The "65 vs 64 = <=1.6% slack" note is retired (the reference is now exact per window).

## E5.3 Edge-vs-interior effect (measured, first object/seed, all budgets)

- Interior windows: max |smoothed_r4 - smoothed_r5| = **0.0** — bit-identical, as
  designed (the truncated smoother reuses the padded convolution on the interior).
- Boundary windows (64 of 2048 per record, 3.12%): max |delta| = **3.46e-01**, mean
  **7.32e-02** (soft-log transform units) — the expected, intended change.

## E5.4 Files

- Runner (modified): `run_paper_fig7_lowphoton.py`
- New results: `results/paper_fig7_lowphoton_r5_final/` (2500 rows + floor probe;
  manifest carries `oracle_carrier`, `window_semantics`, eps_cal/eps_bis, and the
  edge-effect probe)
- Figures: `paper_draft/latex/figs/fig7_logMSE_vs_photon.png` now emitted natively by
  `make_pub_figures.py` from r5 (stale hand-copied r4 asset replaced;
  `fig7_gainMSE_vs_photon.png` deleted — no TeX references it);
  `figS4_flip_floorprobe.png` retargeted to r5 (log-domain, oracle-carrier arm).
- Archived (untouched): `results/paper_fig7_lowphoton_r4_carrier/`, `..._r3_calibrated/`.
