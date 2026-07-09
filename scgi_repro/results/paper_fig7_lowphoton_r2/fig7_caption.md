# Fig. 7 Low-Photon Gain Estimation (r2)

Poisson bucket counts are evaluated under identical random-basis carriers and shared gain traces; the summary is aggregated over discrete design columns (method, photon_budget) only.
(i) Soft-log and Anscombe both stay finite across the whole budget range and beat naive clipped log for mean photon count lambda_bar <= 1, but by different margins: soft-log by 23-46x and Anscombe separately by 19.5-30x (naive/method mean-MSE ratio at budgets 0.25/0.5/1.0).
(ii) The 1/(W*lambda) Fisher scaling holds in the variance regime lambda_bar in [2,32] (fitted soft-log log-log slope -0.91); over the wider lambda_bar in [1,16] the fit shallows to -0.73 because lambda_bar~1 is the bias->variance transition peak, and above lambda_bar~32 a drift-limited floor sets in.
(iii) For lambda_bar < 1 the estimator enters the shrinkage-bias-dominated regime: MSE falls BELOW the Fisher reference (biased estimator, consistent with the R3 kappa_alpha(lambda) -> lambda*log(1+1/alpha) mechanism), so this region is NOT ~1/(W*lambda).
(iv) Naive clipped log does not diverge: it saturates at a bias floor (~0.25 relMSE) set by the clip.
At the high-photon end (budget=128) the soft-log gain-MSE floor shrinks from 2.778e-04 (rho=0.001) to 1.725e-04 (rho=0.0001), confirming the floor is drift-limited.
[Post-hoc correction, no rerun] The (ii) slopes and (i) ratio split were recomputed directly from the committed fig7_lowphoton.csv: the run's own fisher_slope() filtered on lambda_bar_mean, which drifts a hair above the nominal photon_budget and silently dropped the budget=32/16 endpoints, understating the slopes as -0.89/-0.65; refitting on photon_budget in [2,32]/[1,16] gives -0.91/-0.73. See run_manifest.json:slope_recompute_note.
Rows: 1500. Runtime seconds: 8.95.
