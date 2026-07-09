# Experiment A -- Tall-Design Identifiability Threshold (r1)

Forward model: R_n = exp(ell_n) * (M_n . T), ell = U theta, generic Gaussian design M in R^{N x K}, Fourier low-pass gain basis U in R^{N x p} (p odd), theta ~ N(0, s^2) with s=0.30, noiseless.
Panel (a) LOCAL RANK TEST: analytic Jacobian J = [R*U | exp(ell)*M]; local identifiability up to the single scale gauge holds iff rank(J) = p + K - 1 (rank in float64, threshold = rank_rtol * S_max, rank_rtol=1e-09).
Panel (b) RECOVERY TEST: blind alternating minimisation (weighted-LS T-step + damped Gauss-Newton theta-step), gauge fixed to mean(ell)=0, up to 8 restarts; success = scale-aligned relMSE(T) < 1e-06 AND max|ell_hat - ell| < 0.001.
Measured rank-test wall: first offset with local-ID rate >= 0.95 is -1 (theory: -1 = N=K+p-1); cell-level agreement rank_id == (offset >= -1) is 1.000 (acceptance >= 0.95).
Measured solver wall: first offset with success rate >= 0.90 is 2 (theory near +0 = N=K+p).
Acceptance bands: solver success for offset >= +4 is 1.000 (target >= 0.90); for offset <= -4 is 0.000 (target <= 0.10). The intermediate band may be ragged.
Grid: K=16, p in [3, 5], offsets(N-K-p) in [-4, -2, -1, 0, 2, 4, 6, 8], seeds=3. Rows: 45 (shard 0/1). Runtime seconds: 18.16.
