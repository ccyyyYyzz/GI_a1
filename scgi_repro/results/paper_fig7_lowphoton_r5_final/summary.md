# Fig. 7 low-photon gain estimation (r5, oracle-known-carrier calibrated soft-log) - native summary

Protocol: random_uniform basis, 10 objects, 5 seeds, W=64, alpha=0.5, rho=0.001, s=0.1, budgets=0.25,0.5,1,2,4,8,16,32,64,128; floor probe rho=0.0001. Rows: 2500.

`soft_log_calibrated_carrier_oracle` is Theorem C's estimator (Appendix D.4, weighted known-carrier form) run as an ORACLE-KNOWN-CARRIER / flat-field-calibrated BENCHMARK: the per-frame carrier intensities b_k are supplied from the SIMULATION TRUTH (the noiseless bucket carrier of the simulated object, times the photon budget), NOT programmed design intensities. With b_k known (d = 0 in this protocol) it solves per window sum_k w_k m_alpha(theta_hat * b_k) = sum_k w_k log(C_k + alpha) over the window's distinct members (equal weights w_k = 1/|I_n|) by monotone bisection on the exactly tabulated homogeneous curve m_alpha(lambda) = E[log(Poisson(lambda)+alpha)] (truncated Poisson sum, rigorous tail bound <= 3.49e-34 on a 3000-point log grid over lambda in [0.00025, 12800]), with theta_hat clamped to the SAFE per-window operating bracket [lam_lo/min(b), lam_hi/max(b)] (all bisection evaluations in-table; all-zero windows clamp to the lower end). `soft_log_calibrated` is the r3 mean-Poisson calibrated PROXY (homogeneous inversion that ignores the frame-varying carrier), kept for continuity; `soft_log` is the legacy uncalibrated proxy exp(movmean(log(C+alpha)) - mean).

WINDOW SEMANTICS (changed in r5). ALL windowed arms use centered odd-width windows over DISTINCT in-record frames, truncated and renormalized at the record boundaries -- replicate padding removed (a padded width-65 edge window aggregates to effective size 65^2/(33^2+32) = 3.77 and falsified the sigma^2/W claim there). Interior windows are unchanged; only the 2*(W_eff//2) boundary windows differ from r4. See the edge-vs-interior probe below.

METRICS. `log_gain_mse` (PRIMARY, Fisher-comparable) is Theorem C's loss: mean over frames of the squared centered-log-gain error, mean_n[((log ghat_n - mean log ghat) - (log g_n - mean log g))^2]. The LOCAL realized Fisher reference (r5) is mean_n[1/I_n] with I_n = sum_{k in I_n} lambda_k the realized per-window log-gain information at d = 0 (Poisson information for log-intensity is lambda itself), computed over the same distinct window members as the estimators; the nominal global 1/(W*lambda_bar) reference of r2-r4 is kept as the secondary column `fisher_reference_nominal`. Fisher comparisons, sub-Fisher flags, and rate slopes are stated in the log-domain metric against the LOCAL reference. `gain_rel_mse` (gain-domain scale-aligned relMSE) is retained for continuity with r2/r3 but is NOT Fisher-comparable.

CALIBRATION INTERPOLATION (empirical eps_cal, Remark D.4.1). The m_alpha table is exact at its 3000 grid points; between them the code linearly interpolates m_alpha against log(lambda). Measured on the dense check grid of all 2999 geometric midpoints (exact truncated-Poisson recomputation as ground truth): eps_cal = max|m_alpha - interp| = 1.641e-06 (attained near lambda = 0.916); the 60-step bisection contributes eps_bis <= 1.540e-17 (log-theta units). These enter the risk bound as a deterministic (eps_cal + eps_bis)^2 / kappa_lower_n^2 term and shrink the clamp margin by eps_cal + eps_bis -- empirical measurement, honestly labeled, not a certified analytic bound.

## (0) Edge-vs-interior window-semantics probe (r4 replicate padding -> r5 truncation)

- Windows per record: 2048; effective width 65; boundary windows affected: 64 (3.12% of frames).
- Interior windows (identical member sets): max |smoothed_r4 - smoothed_r5| = 0.000e+00 over all budgets (bit-identical expected: the truncated smoother reuses the padded convolution on the interior).
- Boundary windows (replicate padding removed): max |smoothed_r4 - smoothed_r5| = 3.465e-01, mean 7.321e-02 (soft-log transform units, first object / first seed, all budgets).

## (a) Per-photon-level mean LOG-domain gain MSE by arm (primary, Fisher-comparable)

| photon_budget | anscombe | naive_log | soft_log | soft_log_calibrated | soft_log_calibrated_carrier_oracle | fisher_reference_mean |
|---|---|---|---|---|---|---|
| 0.25 | 0.00715 | 0.1166 | 0.00468 | 0.06399 | 0.06395 | 0.06252 |
| 0.5 | 0.008917 | 0.1732 | 0.006039 | 0.03203 | 0.03208 | 0.03126 |
| 1 | 0.01002 | 0.2104 | 0.00844 | 0.01857 | 0.0185 | 0.01563 |
| 2 | 0.006948 | 0.1196 | 0.007496 | 0.009355 | 0.009284 | 0.007815 |
| 4 | 0.004202 | 0.03074 | 0.005081 | 0.005141 | 0.005122 | 0.003908 |
| 8 | 0.002081 | 0.002976 | 0.002294 | 0.002287 | 0.002223 | 0.001954 |
| 16 | 0.001156 | 0.001296 | 0.001208 | 0.001207 | 0.001172 | 0.0009769 |
| 32 | 0.0006232 | 0.0006457 | 0.0006339 | 0.0006339 | 0.0006059 | 0.0004884 |
| 64 | 0.0003765 | 0.0003864 | 0.0003814 | 0.0003814 | 0.0003518 | 0.0002442 |
| 128 | 0.0002428 | 0.0002443 | 0.0002434 | 0.0002434 | 0.0002168 | 0.0001221 |

## (a') Per-photon-level mean gain-domain relMSE by arm (continuity with r3; not Fisher-comparable)

| photon_budget | anscombe | naive_log | soft_log | soft_log_calibrated | soft_log_calibrated_carrier_oracle |
|---|---|---|---|---|---|
| 0.25 | 0.007065 | 0.1125 | 0.004613 | 0.05423 | 0.05417 |
| 0.5 | 0.008823 | 0.1578 | 0.006019 | 0.0289 | 0.02897 |
| 1 | 0.009851 | 0.1962 | 0.008386 | 0.01786 | 0.01781 |
| 2 | 0.006823 | 0.09821 | 0.007371 | 0.009085 | 0.009022 |
| 4 | 0.004098 | 0.02513 | 0.004899 | 0.004948 | 0.004931 |
| 8 | 0.002067 | 0.002907 | 0.002277 | 0.00227 | 0.002206 |
| 16 | 0.001135 | 0.001267 | 0.001185 | 0.001184 | 0.001149 |
| 32 | 0.0006099 | 0.000632 | 0.0006204 | 0.0006203 | 0.0005927 |
| 64 | 0.0003751 | 0.0003846 | 0.0003799 | 0.0003799 | 0.0003502 |
| 128 | 0.0002405 | 0.000242 | 0.0002412 | 0.0002412 | 0.0002138 |

## (b) Pairwise mean-MSE ratio tables (numerator/denominator as named)

Log-domain (primary):

| photon_budget | naive/soft | naive/anscombe | anscombe/soft | naive/carrier | anscombe/carrier | carrier/soft | meanpois/carrier |
|---|---|---|---|---|---|---|---|
| 0.25 | 24.91 | 16.31 | 1.528 | 1.823 | 0.1118 | 13.67 | 1.001 |
| 0.5 | 28.67 | 19.42 | 1.477 | 5.398 | 0.278 | 5.312 | 0.9985 |
| 1 | 24.93 | 21 | 1.187 | 11.37 | 0.5416 | 2.192 | 1.004 |
| 2 | 15.95 | 17.21 | 0.9269 | 12.88 | 0.7484 | 1.239 | 1.008 |
| 4 | 6.05 | 7.317 | 0.8269 | 6.002 | 0.8203 | 1.008 | 1.004 |
| 8 | 1.297 | 1.43 | 0.9071 | 1.339 | 0.9364 | 0.9687 | 1.029 |
| 16 | 1.073 | 1.121 | 0.9574 | 1.106 | 0.9869 | 0.97 | 1.03 |
| 32 | 1.019 | 1.036 | 0.9831 | 1.066 | 1.029 | 0.9558 | 1.046 |
| 64 | 1.013 | 1.026 | 0.9872 | 1.098 | 1.07 | 0.9223 | 1.084 |
| 128 | 1.004 | 1.006 | 0.9976 | 1.127 | 1.12 | 0.8908 | 1.123 |

Gain-domain (continuity):

| photon_budget | naive/soft | naive/anscombe | anscombe/soft | naive/carrier | anscombe/carrier | carrier/soft | meanpois/carrier |
|---|---|---|---|---|---|---|---|
| 0.25 | 24.39 | 15.92 | 1.531 | 2.077 | 0.1304 | 11.74 | 1.001 |
| 0.5 | 26.22 | 17.89 | 1.466 | 5.448 | 0.3046 | 4.812 | 0.9978 |
| 1 | 23.4 | 19.92 | 1.175 | 11.02 | 0.5532 | 2.124 | 1.003 |
| 2 | 13.32 | 14.39 | 0.9257 | 10.89 | 0.7563 | 1.224 | 1.007 |
| 4 | 5.129 | 6.131 | 0.8365 | 5.096 | 0.8312 | 1.006 | 1.004 |
| 8 | 1.277 | 1.406 | 0.9081 | 1.318 | 0.9372 | 0.9689 | 1.029 |
| 16 | 1.069 | 1.116 | 0.9577 | 1.103 | 0.9879 | 0.9694 | 1.031 |
| 32 | 1.019 | 1.036 | 0.9831 | 1.066 | 1.029 | 0.9554 | 1.047 |
| 64 | 1.013 | 1.026 | 0.9873 | 1.098 | 1.071 | 0.9219 | 1.085 |
| 128 | 1.004 | 1.006 | 0.9973 | 1.132 | 1.125 | 0.8866 | 1.128 |

Low-photon log-domain ranges (over budgets <= 1):
- naive/soft: 24.91-28.67x
- naive/anscombe: 16.31-21.00x
- anscombe/soft: 1.19-1.53x
- naive/carrier: 1.82-11.37x
- anscombe/carrier: 0.11-0.54x
- carrier/soft: 2.19-13.67x
- meanpois/carrier: 1.00-1.00x

## (c) Fitted log-log rate slopes of mean MSE vs photon budget (1/(W*lambda) law => slope -1)

| method | log-domain [2,32] | log-domain [1,16] | gain-domain [2,32] | gain-domain [1,16] |
|---|---|---|---|---|
| soft_log | -0.920 | -0.732 | -0.919 | -0.734 |
| soft_log_calibrated | -0.986 | -0.992 | -0.981 | -0.983 |
| soft_log_calibrated_carrier_oracle | -1.000 | -1.002 | -0.996 | -0.994 |
| naive_log | -1.963 | -2.001 | -1.887 | -1.963 |
| anscombe | -0.882 | -0.797 | -0.882 | -0.796 |

Slopes are fit on the discrete design column photon_budget (endpoints included); no post-hoc correction is needed.

## (d) Fisher-excess table (log-domain mean MSE / LOCAL realized Fisher reference, per budget)

| photon_budget | soft_log/fisher | soft_log_calibrated/fisher | soft_log_calibrated_carrier_oracle/fisher | anscombe/fisher |
|---|---|---|---|---|
| 0.25 | 0.07485 | 1.024 | 1.023 | 0.1144 |
| 0.5 | 0.1932 | 1.025 | 1.026 | 0.2853 |
| 1 | 0.54 | 1.188 | 1.184 | 0.641 |
| 2 | 0.9591 | 1.197 | 1.188 | 0.889 |
| 4 | 1.3 | 1.316 | 1.311 | 1.075 |
| 8 | 1.174 | 1.171 | 1.138 | 1.065 |
| 16 | 1.236 | 1.235 | 1.199 | 1.184 |
| 32 | 1.298 | 1.298 | 1.24 | 1.276 |
| 64 | 1.562 | 1.562 | 1.44 | 1.542 |
| 128 | 1.993 | 1.993 | 1.776 | 1.989 |

## (e) Qualitative checks (log-domain metric)

- Oracle-known-carrier calibrated soft-log beats Anscombe (lower mean log-domain MSE) at budgets: 32, 64, 128; Anscombe is equal/better at: 0.25, 0.5, 1, 2, 4, 8, 16.
- Log-domain MSE below the unbiased LOCAL realized Fisher reference mean_n[1/I_n] (shrinkage-bias signature): soft_log at budgets 0.25, 0.5, 1, 2; soft_log_calibrated at budgets none; soft_log_calibrated_carrier_oracle at budgets none.
- meanpois/carrier log-domain mean-MSE ratio spans 0.9985-1.1226 across all budgets (values near 1 mean the r3 mean-Poisson proxy and the oracle-known-carrier estimator agree numerically at this carrier CV; the oracle-carrier arm is the one the theorem is about, run as a flat-field-calibrated benchmark).
- carrier/soft log-domain mean-MSE ratio spans 0.891-13.666 across all budgets (> 1 means the calibrated estimator pays extra MSE over the biased proxy at that budget, < 1 that it gains).
- At the high-photon end (budget=128) the soft_log log-domain gain-MSE floor shrinks from 2.434e-04 (rho=0.001) to 1.411e-04 (rho=0.0001), confirming the floor is drift-limited.
- At the high-photon end (budget=128) the soft_log_calibrated log-domain gain-MSE floor shrinks from 2.434e-04 (rho=0.001) to 1.411e-04 (rho=0.0001), confirming the floor is drift-limited.
- At the high-photon end (budget=128) the soft_log_calibrated_carrier_oracle log-domain gain-MSE floor shrinks from 2.168e-04 (rho=0.001) to 1.125e-04 (rho=0.0001), confirming the floor is drift-limited.

