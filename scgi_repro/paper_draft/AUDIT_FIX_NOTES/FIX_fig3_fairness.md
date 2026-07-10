# FIX P0-5: Fig. 3 fairness (budget, estimator, bootstrap clustering)

Status: fixed and re-run 2026-07-10. New authoritative result:
`results/paper_fig3_gain_error_r3_fair/` (20 seeds x 10 objects, 31,600 rows;
full old-vs-new tables in its `summary.md`). The published run
`results/paper_fig3_gain_error_e12_local_r1/` is untouched. No text in
`MANUSCRIPT_DRAFT.md` / `APPENDICES.md` / `latex/` was edited; ready-to-paste
sentences are at the bottom.

## Defect (a): budget mismatch behind a "matched-budget" claim — CONFIRMED

`build_fig3_arms` gave raw signed-Walsh arms num_frames = num_pixels = 1024
while every physical arm got 2048 frames; the abstract calls this
"matched-budget simulations".

**Fix.** `run_paper_fig3_gain_error.py` now accepts explicit-budget raw arms:
`hadamard_raw_ordered_2048` / `hadamard_raw_shuffled_2048` repeat the signed
Walsh sequence twice (ordered = two full passes; shuffled = permutation of the
full 2048-frame record) against the same 2048-frame drift trace as the physical
arms. Single-pass arms are kept as `hadamard_raw_ordered_1024` /
`hadamard_raw_shuffled_1024`, explicitly labelled diagnostics. Legacy bare
names still reproduce the old protocol.

**Result.** The mismatch did not drive the conclusion: median best-window error
moves from 0.896 (1024) to 0.899 (2048) for raw ordered and 0.788 to 0.794 for
raw shuffled. The published contrast was real; only the label was wrong.

## Defect (b): estimator mismatch vs Theorem B — CONFIRMED

The experiment scored only the ratio AGC `movmean(R,W)/mean(R)`
(`src/paper_experiments.py::mean_agc_gain`), while Theorem B analyzes windowed
means of log R.

**Fix.** New `src/paper_experiments.py::log_agc_gain`: gain_hat proportional to
exp(centered movmean(log R, W)), mean-normalized (Theorem B's centered log-gain
up to the global-scale gauge). Positivity guard = assumption (iv) taken
literally ("R_n > 0 on the analyzed record"): frames with R <= 0 are excluded
via a masked window mean, and the excluded fraction is emitted as
`frac_nonpos_carrier` (~0 for physical arms — only the exact-zero complementary
DC frame of paired Hadamard; 0.583 for the raw signed arms, which stay
diagnostic-only per bucket convention (i)). A hard log-floor was rejected: it
injects a log(eps) outlier at the DC-zero frame that assumption (iv) never
admits. Both errors are emitted per row (`gain_rel_err_ratio`,
`gain_rel_err_log`).

**Result (rho = 1e-3, 2048-frame budget, median best-window, two-way CI).**
Ratio vs log agree to ~2% on the arms Theorem B covers: SRHT 0.0077 vs 0.0079,
random_uniform 0.0113 vs 0.0113, random_binary 0.0150 vs 0.0150; permuted
paired Hadamard 0.0073 vs 0.0119. Raw ordered stays non-decaying under the log
estimator (0.708 [0.563, 0.840]); raw shuffled improves to 0.136 [0.083, 0.196]
under the masked log — still >= 12x above every randomized arm. Nuance:
naturally ordered paired Hadamard shows a shallow log-estimator decay (W<=16
slope -0.222 [-0.306, -0.054] two-way) where the ratio AGC shows none (+0.03,
CI straddles 0); both remain far outside the W^(-1/2) band.

## Defect (c): bootstrap treats 200 object x seed cells as independent — CONFIRMED

The published Table-1 CIs resample the 200 cells i.i.d., but the 20 drift seeds
are reused across all 10 objects (and objects across seeds). Reproduction check:
the naive scheme on the published CSV gives SRHT slope -0.575 [-0.602, -0.542],
matching the published -0.58 [-0.60, -0.54].

**Fix.** `bootstrap_arm_cis` in the runner reports every statistic under three
schemes (B = 2000, percentile): naive; seed_cluster (resample the 20 seeds,
keep all objects); two_way (crossed: resample seeds AND objects).
`fig3_bootstrap_cis.csv` (new run) and `fig3_bootstrap_cis_published_e12.csv`
(published data, identical machinery).

**Result.** Seed-only clustering *narrows* the CI (objects dominate the spread;
SRHT slope [-0.576, -0.565]); the conservative scheme is the two-way crossed
bootstrap: SRHT slope widens to -0.575 [-0.660, -0.415] (the audit's quoted
"[-0.662, -0.421]" is this crossed interval). All qualitative conclusions
survive: every randomized-arm slope CI stays clearly negative, ordered paired
straddles 0 under the ratio AGC, and no best-error CI crosses between the
randomized (<= 0.017) and raw (>= 0.56) regimes.

## Headline: does the paper's ordering survive?

Yes. Randomized << ordered raw under both estimators, both budgets, all three
CI schemes, both drift rates; SRHT and permuted paired Hadamard are
statistically tied at the top (as in the published data). The abstract's
"raw 0.96 vs randomized 0.02" survives with corrected numbers and an honest
label.

## Caption/abstract-ready sentences

Abstract (replaces "In matched-budget simulations, raw ordered Hadamard leaves
a non-decaying blind gain error near 0.96 where randomized arms reach 0.02"):

> "In frame-matched simulations (2048 frames per arm, identical drift traces),
> raw ordered Hadamard leaves a non-decaying blind gain error of 0.94-0.99
> across all averaging windows (0.90 at the best window), where randomized
> arms reach 0.007-0.015; under the log-domain estimator of Theorem B the raw
> ordered arm still cannot fall below 0.71 (descriptive medians on the
> simulation grid; seed-and-object clustered 95% CIs in Sec. 9)."

Fig. 3 caption addition:

> "Raw signed-Walsh arms are shown at the same 2048-frame budget as the
> physical arms (the sequence acquired twice); single-pass 1024-frame variants
> (diagnostic) are indistinguishable, so the raw-arm failure is a chronology
> effect, not a budget effect. Blind gain errors are reported for both the
> ratio AGC movmean(R,W)/mean(R) and the windowed log-domain estimator of
> Theorem B (masked to the R>0 record per assumption (iv)); the two agree to
> within ~2% on all stationary-carrier arms."

Table 1 CI-convention sentence (replaces "bootstrapped over object x seed
cells"):

> "Confidence intervals are two-way (seeds-and-objects) clustered bootstrap
> percentile intervals; because the 20 drift seeds and 10 objects are each
> reused across the full grid, an object x seed bootstrap that treats the 200
> cells as independent understates uncertainty (e.g. the SRHT slope CI widens
> from [-0.60, -0.54] to [-0.66, -0.41]); no qualitative conclusion changes."

Updated Table-1-style numbers (rho = 1e-3, ratio estimator, median W<=16 slope
with two-way CI): random binary -0.41 [-0.44, -0.37]; random uniform
-0.39 [-0.42, -0.31]; SRHT-paired -0.58 [-0.66, -0.41]; randomly permuted
paired Hadamard -0.62 [-0.67, -0.44]; ordered paired +0.03 [-0.06, +0.17]
(straddles zero); raw ordered (2048) best-window error 0.899 [0.892, 0.903].
