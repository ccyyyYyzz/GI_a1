# Fig. 7 Low-Photon Gain Estimation (r3, calibrated soft-log)

Poisson bucket counts are evaluated under identical random-basis carriers and shared gain traces; the summary is aggregated over discrete design columns (method, photon_budget) only. The soft_log_calibrated arm is the Theorem C estimator (windowed mean of log(C+alpha) inverted through the exact calibration curve m_alpha(lambda) = E[log(Poisson(lambda)+alpha)]); soft_log is the legacy uncalibrated proxy, retained unchanged for comparison.
(i) Ratio bookkeeping (mean-MSE ratios over budgets <= 1, numerator/denominator named): naive/soft 22.9-46.4x, naive/Anscombe 19.5-30.0x, Anscombe/soft 1.18-1.55x, naive/calibrated 3.8-10.7x, Anscombe/calibrated 0.13-0.55x, calibrated/soft 2.14-12.08x.
(ii) The 1/(W*lambda) Fisher scaling in the variance regime, fit natively on photon_budget in [2,32] (endpoints included): slope -0.91 (soft_log), -0.97 (calibrated); over the wider [1,16] window the fits shallow to -0.73 / -0.98 because lambda_bar~1 is the bias->variance transition peak, and above lambda_bar~32 a drift-limited floor sets in.
(iii) For lambda_bar < 1 the soft-log arms are shrinkage-bias-dominated: MSE falls BELOW the unbiased local Fisher reference (biased estimator, consistent with kappa_alpha(lambda) -> lambda*log(1+1/alpha)), so this region is NOT ~1/(W*lambda). See summary.md for the per-budget sub-Fisher flags of both soft-log arms.
(iv) Naive clipped log does not diverge: it saturates at a bias floor (~0.25 relMSE) set by the clip.
At the high-photon end (budget=128) the soft_log gain-MSE floor shrinks from 2.778e-04 (rho=0.001) to 1.725e-04 (rho=0.0001), confirming the floor is drift-limited.
At the high-photon end (budget=128) the soft_log_calibrated gain-MSE floor shrinks from 2.777e-04 (rho=0.001) to 1.725e-04 (rho=0.0001), confirming the floor is drift-limited.
Rows: 2000. Runtime seconds: 11.03.
