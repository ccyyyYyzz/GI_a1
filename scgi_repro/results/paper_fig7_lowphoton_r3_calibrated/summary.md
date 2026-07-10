# Fig. 7 low-photon gain estimation (r3, calibrated soft-log) - native summary

Protocol: random_uniform basis, 10 objects, 5 seeds, W=64, alpha=0.5, rho=0.001, s=0.1, budgets=0.25,0.5,1,2,4,8,16,32,64,128; floor probe rho=0.0001. Rows: 2000.

`soft_log_calibrated` is the Theorem C estimator: per-window mean of log(C+alpha), inverted through the exactly tabulated calibration curve m_alpha(lambda) = E[log(Poisson(lambda)+alpha)] (truncated Poisson sum, rigorous tail bound <= 3.49e-34 on a 3000-point log grid over lambda in [0.00025, 12800]), then normalized by its mean (centered-log-gain gauge, same as every other arm). `soft_log` is the legacy uncalibrated proxy exp(movmean(log(C+alpha)) - mean), kept unchanged for comparison.

## (a) Per-photon-level mean gain relMSE by arm

| photon_budget | anscombe | naive_log | soft_log | soft_log_calibrated | fisher_reference_mean |
|---|---|---|---|---|---|
| 0.25 | 0.008275 | 0.2482 | 0.005349 | 0.0646 | 0.0625 |
| 0.5 | 0.0103 | 0.2348 | 0.006944 | 0.03391 | 0.03125 |
| 1 | 0.01125 | 0.2192 | 0.009562 | 0.02049 | 0.01562 |
| 2 | 0.00788 | 0.1018 | 0.008447 | 0.01048 | 0.007812 |
| 4 | 0.004644 | 0.02586 | 0.005451 | 0.005511 | 0.003906 |
| 8 | 0.002263 | 0.003139 | 0.00248 | 0.002472 | 0.001953 |
| 16 | 0.001375 | 0.001506 | 0.001408 | 0.001407 | 0.0009766 |
| 32 | 0.0006979 | 0.0007239 | 0.0007089 | 0.0007088 | 0.0004883 |
| 64 | 0.0004622 | 0.000474 | 0.0004678 | 0.0004678 | 0.0002441 |
| 128 | 0.0002777 | 0.0002789 | 0.0002778 | 0.0002777 | 0.0001221 |

## (b) Pairwise mean-MSE ratio table (numerator/denominator as named)

| photon_budget | naive/soft | naive/anscombe | anscombe/soft | naive/calibrated | anscombe/calibrated | calibrated/soft |
|---|---|---|---|---|---|---|
| 0.25 | 46.39 | 29.99 | 1.547 | 3.842 | 0.1281 | 12.08 |
| 0.5 | 33.82 | 22.79 | 1.484 | 6.925 | 0.3039 | 4.883 |
| 1 | 22.92 | 19.48 | 1.177 | 10.69 | 0.549 | 2.143 |
| 2 | 12.05 | 12.91 | 0.9329 | 9.712 | 0.752 | 1.241 |
| 4 | 4.744 | 5.569 | 0.852 | 4.692 | 0.8426 | 1.011 |
| 8 | 1.266 | 1.387 | 0.9123 | 1.27 | 0.9152 | 0.9968 |
| 16 | 1.07 | 1.095 | 0.9772 | 1.071 | 0.978 | 0.9992 |
| 32 | 1.021 | 1.037 | 0.9845 | 1.021 | 0.9846 | 0.9999 |
| 64 | 1.013 | 1.026 | 0.988 | 1.013 | 0.9881 | 1 |
| 128 | 1.004 | 1.004 | 1 | 1.004 | 1 | 1 |

Low-photon ranges (over budgets <= 1):
- naive/soft: 22.92-46.39x
- naive/anscombe: 19.48-29.99x
- anscombe/soft: 1.18-1.55x
- naive/calibrated: 3.84-10.69x
- anscombe/calibrated: 0.13-0.55x
- calibrated/soft: 2.14-12.08x

## (c) Fitted log-log rate slopes of mean MSE vs photon budget (1/(W*lambda) law => slope -1)

| method | slope over budgets [2,32] | slope over budgets [1,16] |
|---|---|---|
| soft_log | -0.910 | -0.730 |
| soft_log_calibrated | -0.974 | -0.981 |
| naive_log | -1.837 | -1.939 |
| anscombe | -0.875 | -0.786 |

Slopes are fit on the discrete design column photon_budget (endpoints included); no post-hoc correction is needed.

## (d) Qualitative checks

- Calibrated soft-log beats Anscombe (lower mean MSE) at budgets: none; Anscombe is equal/better at: 0.25, 0.5, 1, 2, 4, 8, 16, 32, 64, 128.
- MSE below the unbiased local Fisher reference 1/(W*lambda) (shrinkage-bias signature): soft_log at budgets 0.25, 0.5, 1; soft_log_calibrated at budgets none.
- calibrated/soft mean-MSE ratio spans 0.997-12.076 across all budgets (values near 1 mean calibration does not change the qualitative Fig. 7 story; values > 1 mean the calibrated estimator pays extra MSE at that budget, < 1 that it gains).
- At the high-photon end (budget=128) the soft_log gain-MSE floor shrinks from 2.778e-04 (rho=0.001) to 1.725e-04 (rho=0.0001), confirming the floor is drift-limited.
- At the high-photon end (budget=128) the soft_log_calibrated gain-MSE floor shrinks from 2.777e-04 (rho=0.001) to 1.725e-04 (rho=0.0001), confirming the floor is drift-limited.

