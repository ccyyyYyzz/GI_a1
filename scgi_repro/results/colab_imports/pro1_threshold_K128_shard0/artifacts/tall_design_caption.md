# Experiment A -- Tall-Design Identifiability Threshold (r1)

Forward model: R_n = exp(ell_n) * (M_n . T), ell = U theta, generic Gaussian design M in R^{N x K}, Fourier low-pass gain basis U in R^{N x p} (p odd), theta ~ N(0, s^2) with s=0.30, noiseless.
Panel (a) LOCAL RANK TEST: analytic Jacobian J = [R*U | exp(ell)*M]; local identifiability up to the single scale gauge holds iff rank(J) = p + K - 1 (rank in float64, threshold = rank_rtol * S_max, rank_rtol=1e-09).
Panel (b) RECOVERY TEST: blind alternating minimisation (weighted-LS T-step + damped Gauss-Newton theta-step), gauge fixed to mean(ell)=0, up to 8 restarts; success = scale-aligned relMSE(T) < 1e-06 AND max|ell_hat - ell| < 0.001.
Grid: K=128, p in [3, 5, 9, 17, 33], offsets(N-K-p) in [-8, -6, -4, -2, -1, 0, 2, 4, 6, 8, 10, 12, 14, 16], seeds=30. Rows: 975 (shard 0/2). Runtime seconds: 1347.50.
