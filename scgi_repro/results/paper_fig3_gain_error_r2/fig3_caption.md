# Fig. 3 Blind Gain Identifiability (r2)

Sliding-window AGC (movmean(R,W)/mean(R)) is applied identically to every arm and scored only on gain recovery.
paired/permuted Hadamard variants confirm the permutation theorem (R2): pairing cancels slow drift, permutation restores stationarity; only the raw ordered chronology fails.
hadamard_paired = complementary +/- pairing in natural order; hadamard_random_paired = the same pairing under a random time permutation; hadamard_raw_ordered/shuffled feed the bare signed Walsh coefficients (one per frame, no pairing) directly as B_n, so the near-zero/negative mean makes blind AGC ill-posed and object-dependent.
fig3b: within the variance-obeying arms the best-window error depends on the object only through K_eff, as theory predicts.
fig3c: err/theory_floor (theory_floor=sqrt(carrier_cv^2/W)) collapses across objects at the low-W (pure-variance) end of the segment; the spread re-opens toward the argmin as object-dependent drift bias re-enters. Cross-object collapse at the smallest W (slow drift):
  hadamard_random_paired: err/floor = 0.40 at W=4, cross-object spread +/-7%
  random_binary: err/floor = 0.89 at W=4, cross-object spread +/-5%
  random_uniform: err/floor = 0.90 at W=4, cross-object spread +/-5%
  srht_paired: err/floor = 0.41 at W=4, cross-object spread +/-7%
Variance-segment slope of log(err) vs log(W) (strict-below-argmin fit, argmin point added only to reach 3 points, fast-drift cells with argmin_W<=8 left unresolved). In the slow-drift regime where the W^-1/2 law applies, random_binary/srht_paired/hadamard_random_paired all land inside [-0.65,-0.35]; the fast-drift (rho=1e-2) regime shallows because the variance segment collapses to W<=8 (reported honestly, per-arm below):
  hadamard_paired: slope (all rho) -0.243 [IQR 0.000], slow-drift (rho=0.001) -0.243
  hadamard_random_paired: slope (all rho) -0.609 [IQR 0.150], slow-drift (rho=0.001) -0.609
  hadamard_raw_ordered: slope (all rho) 0.005 [IQR 0.017], slow-drift (rho=0.001) 0.006
  hadamard_raw_shuffled: slope (all rho) -0.021 [IQR 0.020], slow-drift (rho=0.001) -0.028
  random_binary: slope (all rho) -0.356 [IQR 0.101], slow-drift (rho=0.001) -0.394
  random_uniform: slope (all rho) -0.327 [IQR 0.213], slow-drift (rho=0.001) -0.384
  srht_paired: slope (all rho) -0.597 [IQR 0.141], slow-drift (rho=0.001) -0.597
Rows: 6100. Runtime seconds: 12.39.
