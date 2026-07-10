# Fig. 7 low-photon gain estimation (r4, carrier-aware calibrated soft-log) - native summary

Protocol: random_uniform basis, 10 objects, 5 seeds, W=64, alpha=0.5, rho=0.001, s=0.1, budgets=0.25,0.5,1,2,4,8,16,32,64,128; floor probe rho=0.0001. Rows: 2500.

`soft_log_calibrated_carrier` is Theorem C's estimator (Appendix D.4, carrier-aware form): with the per-frame carrier intensities b_k known (design values; dark counts d = 0 in this protocol), it solves per window (1/W) sum_k m_alpha(theta_hat * b_k) = (1/W) sum_k log(C_k + alpha) by monotone bisection on the exactly tabulated homogeneous curve m_alpha(lambda) = E[log(Poisson(lambda)+alpha)] (truncated Poisson sum, rigorous tail bound <= 3.49e-34 on a 3000-point log grid over lambda in [0.00025, 12800]), with theta_hat clamped to the tabulated range (the theorem's clamp; all-zero windows clamp to the lower end). `soft_log_calibrated` is the r3 mean-Poisson calibrated PROXY (homogeneous inversion that ignores the frame-varying carrier), kept for continuity; `soft_log` is the legacy uncalibrated proxy exp(movmean(log(C+alpha)) - mean), also unchanged.

METRICS. `log_gain_mse` (PRIMARY, Fisher-comparable) is Theorem C's loss: mean over frames of the squared centered-log-gain error, mean_n[((log ghat_n - mean log ghat) - (log g_n - mean log g))^2]. The local Fisher reference 1/(W*lambda) is the Cramer-Rao scale for LOG-intensity (Poisson information for log-intensity is lambda), so Fisher comparisons, sub-Fisher flags, and rate slopes are stated in this metric. `gain_rel_mse` (gain-domain scale-aligned relMSE) is retained for continuity with r2/r3 but is NOT Fisher-comparable. The centered moving-average window has odd effective width W+1=65 (moving_average_1d convention) while the Fisher reference uses the nominal W=64, a <=1.6% conservative slack in the reference.

## (a) Per-photon-level mean LOG-domain gain MSE by arm (primary, Fisher-comparable)

| photon_budget | anscombe | naive_log | soft_log | soft_log_calibrated | soft_log_calibrated_carrier | fisher_reference_mean |
|---|---|---|---|---|---|---|
| 0.25 | 0.007922 | 0.1395 | 0.005176 | 0.06952 | 0.0695 | 0.0625 |
| 0.5 | 0.0101 | 0.2046 | 0.006786 | 0.03811 | 0.03819 | 0.03125 |
| 1 | 0.01156 | 0.2446 | 0.009675 | 0.0222 | 0.02218 | 0.01562 |
| 2 | 0.008381 | 0.1439 | 0.008981 | 0.01166 | 0.01158 | 0.007812 |
| 4 | 0.004827 | 0.03449 | 0.005765 | 0.005864 | 0.005823 | 0.003906 |
| 8 | 0.00227 | 0.003199 | 0.00249 | 0.002482 | 0.002398 | 0.001953 |
| 16 | 0.00138 | 0.001522 | 0.001418 | 0.001417 | 0.001371 | 0.0009766 |
| 32 | 0.0007103 | 0.0007371 | 0.000722 | 0.0007219 | 0.0006836 | 0.0004883 |
| 64 | 0.0004605 | 0.0004733 | 0.0004669 | 0.0004669 | 0.00043 | 0.0002441 |
| 128 | 0.0002791 | 0.0002803 | 0.0002792 | 0.0002792 | 0.0002446 | 0.0001221 |

## (a') Per-photon-level mean gain-domain relMSE by arm (continuity with r3; not Fisher-comparable)

| photon_budget | anscombe | naive_log | soft_log | soft_log_calibrated | soft_log_calibrated_carrier |
|---|---|---|---|---|---|
| 0.25 | 0.008275 | 0.2482 | 0.005349 | 0.0646 | 0.06439 |
| 0.5 | 0.0103 | 0.2348 | 0.006944 | 0.03391 | 0.03388 |
| 1 | 0.01125 | 0.2192 | 0.009562 | 0.02049 | 0.02041 |
| 2 | 0.00788 | 0.1018 | 0.008447 | 0.01048 | 0.01038 |
| 4 | 0.004644 | 0.02586 | 0.005451 | 0.005511 | 0.005467 |
| 8 | 0.002263 | 0.003139 | 0.00248 | 0.002472 | 0.002383 |
| 16 | 0.001375 | 0.001506 | 0.001408 | 0.001407 | 0.001356 |
| 32 | 0.0006979 | 0.0007239 | 0.0007089 | 0.0007088 | 0.0006684 |
| 64 | 0.0004622 | 0.000474 | 0.0004678 | 0.0004678 | 0.0004284 |
| 128 | 0.0002777 | 0.0002789 | 0.0002778 | 0.0002777 | 0.0002415 |

## (b) Pairwise mean-MSE ratio tables (numerator/denominator as named)

Log-domain (primary):

| photon_budget | naive/soft | naive/anscombe | anscombe/soft | naive/carrier | anscombe/carrier | carrier/soft | meanpois/carrier |
|---|---|---|---|---|---|---|---|
| 0.25 | 26.94 | 17.6 | 1.531 | 2.007 | 0.114 | 13.43 | 1 |
| 0.5 | 30.15 | 20.26 | 1.488 | 5.359 | 0.2645 | 5.627 | 0.9979 |
| 1 | 25.29 | 21.17 | 1.195 | 11.03 | 0.5212 | 2.292 | 1.001 |
| 2 | 16.02 | 17.17 | 0.9333 | 12.43 | 0.7239 | 1.289 | 1.007 |
| 4 | 5.982 | 7.145 | 0.8373 | 5.923 | 0.829 | 1.01 | 1.007 |
| 8 | 1.284 | 1.409 | 0.9114 | 1.334 | 0.9464 | 0.9631 | 1.035 |
| 16 | 1.073 | 1.103 | 0.9732 | 1.11 | 1.006 | 0.9672 | 1.033 |
| 32 | 1.021 | 1.038 | 0.9838 | 1.078 | 1.039 | 0.9469 | 1.056 |
| 64 | 1.014 | 1.028 | 0.9862 | 1.101 | 1.071 | 0.921 | 1.086 |
| 128 | 1.004 | 1.004 | 0.9997 | 1.146 | 1.141 | 0.876 | 1.142 |

Gain-domain (continuity):

| photon_budget | naive/soft | naive/anscombe | anscombe/soft | naive/carrier | anscombe/carrier | carrier/soft | meanpois/carrier |
|---|---|---|---|---|---|---|---|
| 0.25 | 46.39 | 29.99 | 1.547 | 3.854 | 0.1285 | 12.04 | 1.003 |
| 0.5 | 33.82 | 22.79 | 1.484 | 6.931 | 0.3041 | 4.88 | 1.001 |
| 1 | 22.92 | 19.48 | 1.177 | 10.74 | 0.5514 | 2.134 | 1.004 |
| 2 | 12.05 | 12.91 | 0.9329 | 9.806 | 0.7593 | 1.229 | 1.01 |
| 4 | 4.744 | 5.569 | 0.852 | 4.731 | 0.8495 | 1.003 | 1.008 |
| 8 | 1.266 | 1.387 | 0.9123 | 1.317 | 0.9496 | 0.9607 | 1.038 |
| 16 | 1.07 | 1.095 | 0.9772 | 1.111 | 1.015 | 0.9631 | 1.038 |
| 32 | 1.021 | 1.037 | 0.9845 | 1.083 | 1.044 | 0.9429 | 1.06 |
| 64 | 1.013 | 1.026 | 0.988 | 1.107 | 1.079 | 0.9158 | 1.092 |
| 128 | 1.004 | 1.004 | 1 | 1.154 | 1.15 | 0.8697 | 1.15 |

Low-photon log-domain ranges (over budgets <= 1):
- naive/soft: 25.29-30.15x
- naive/anscombe: 17.60-21.17x
- anscombe/soft: 1.19-1.53x
- naive/carrier: 2.01-11.03x
- anscombe/carrier: 0.11-0.52x
- carrier/soft: 2.29-13.43x
- meanpois/carrier: 1.00-1.00x

## (c) Fitted log-log rate slopes of mean MSE vs photon budget (1/(W*lambda) law => slope -1)

| method | log-domain [2,32] | log-domain [1,16] | gain-domain [2,32] | gain-domain [1,16] |
|---|---|---|---|---|
| soft_log | -0.930 | -0.739 | -0.910 | -0.730 |
| soft_log_calibrated | -1.008 | -1.017 | -0.974 | -0.981 |
| soft_log_calibrated_carrier | -1.025 | -1.030 | -0.993 | -0.995 |
| naive_log | -1.972 | -2.015 | -1.837 | -1.939 |
| anscombe | -0.893 | -0.802 | -0.875 | -0.786 |

Slopes are fit on the discrete design column photon_budget (endpoints included); no post-hoc correction is needed.

## (d) Fisher-excess table (log-domain mean MSE / local Fisher reference, per budget)

| photon_budget | soft_log/fisher | soft_log_calibrated/fisher | soft_log_calibrated_carrier/fisher | anscombe/fisher |
|---|---|---|---|---|
| 0.25 | 0.08282 | 1.112 | 1.112 | 0.1268 |
| 0.5 | 0.2172 | 1.219 | 1.222 | 0.3232 |
| 1 | 0.6192 | 1.421 | 1.419 | 0.7397 |
| 2 | 1.15 | 1.492 | 1.482 | 1.073 |
| 4 | 1.476 | 1.501 | 1.491 | 1.236 |
| 8 | 1.275 | 1.271 | 1.228 | 1.162 |
| 16 | 1.452 | 1.451 | 1.404 | 1.413 |
| 32 | 1.479 | 1.478 | 1.4 | 1.455 |
| 64 | 1.913 | 1.913 | 1.761 | 1.886 |
| 128 | 2.287 | 2.287 | 2.004 | 2.286 |

## (e) Qualitative checks (log-domain metric)

- Carrier-aware calibrated soft-log beats Anscombe (lower mean log-domain MSE) at budgets: 16, 32, 64, 128; Anscombe is equal/better at: 0.25, 0.5, 1, 2, 4, 8.
- Log-domain MSE below the unbiased local Fisher reference 1/(W*lambda) (shrinkage-bias signature): soft_log at budgets 0.25, 0.5, 1; soft_log_calibrated at budgets none; soft_log_calibrated_carrier at budgets none.
- meanpois/carrier log-domain mean-MSE ratio spans 0.9979-1.1415 across all budgets (values near 1 mean the r3 mean-Poisson proxy and the true carrier-aware estimator agree numerically at this carrier CV; the carrier-aware arm is the one the theorem is about).
- carrier/soft log-domain mean-MSE ratio spans 0.876-13.428 across all budgets (> 1 means the calibrated estimator pays extra MSE over the biased proxy at that budget, < 1 that it gains).
- At the high-photon end (budget=128) the soft_log log-domain gain-MSE floor shrinks from 2.792e-04 (rho=0.001) to 1.726e-04 (rho=0.0001), confirming the floor is drift-limited.
- At the high-photon end (budget=128) the soft_log_calibrated log-domain gain-MSE floor shrinks from 2.792e-04 (rho=0.001) to 1.726e-04 (rho=0.0001), confirming the floor is drift-limited.
- At the high-photon end (budget=128) the soft_log_calibrated_carrier log-domain gain-MSE floor shrinks from 2.446e-04 (rho=0.001) to 1.362e-04 (rho=0.0001), confirming the floor is drift-limited.

