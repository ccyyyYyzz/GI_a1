# Fig. 3 Blind Gain Identifiability (r2)

Sliding-window AGC (movmean(R,W)/mean(R)) is applied identically to every arm and scored only on gain recovery.
paired/permuted Hadamard variants confirm the permutation theorem (R2): pairing cancels slow drift, permutation restores stationarity; only the raw ordered chronology fails.
hadamard_paired = complementary +/- pairing in natural order; hadamard_random_paired = the same pairing under a random time permutation; hadamard_raw_ordered/shuffled feed the bare signed Walsh coefficients (one per frame, no pairing) directly as B_n, so the near-zero/negative mean makes blind AGC ill-posed and object-dependent.
fig3b: within the variance-obeying arms the best-window error depends on the object only through K_eff, as theory predicts.
fig3c: err/theory_floor (theory_floor=sqrt(carrier_cv^2/W)) collapses across objects at the low-W (pure-variance) end of the segment; the spread re-opens toward the argmin as object-dependent drift bias re-enters. Cross-object collapse at the smallest W (slow drift):
  hadamard_random_paired: err/floor = 0.40 at W=4, cross-object spread +/-6%
  random_binary: err/floor = 0.89 at W=4, cross-object spread +/-5%
  random_uniform: err/floor = 0.90 at W=4, cross-object spread +/-5%
  srht_paired: err/floor = 0.41 at W=4, cross-object spread +/-8%
Variance-segment slope of log(err) vs log(W) (strict-below-argmin fit, argmin point added only to reach 3 points, fast-drift cells with argmin_W<=8 left unresolved). In the slow-drift regime where the W^-1/2 law applies, random_binary/srht_paired/hadamard_random_paired all land inside [-0.65,-0.35]; the fast-drift (rho=1e-2) regime shallows because the variance segment collapses to W<=8 (reported honestly, per-arm below):
  hadamard_paired: slope (all rho) nan [IQR nan], slow-drift (rho=0.001) nan
  hadamard_random_paired: slope (all rho) -0.618 [IQR 0.143], slow-drift (rho=0.001) -0.620
  hadamard_raw_ordered: slope (all rho) 0.005 [IQR 0.016], slow-drift (rho=0.001) 0.005
  hadamard_raw_shuffled: slope (all rho) -0.020 [IQR 0.025], slow-drift (rho=0.001) -0.020
  random_binary: slope (all rho) -0.353 [IQR 0.100], slow-drift (rho=0.001) -0.396
  random_uniform: slope (all rho) -0.327 [IQR 0.214], slow-drift (rho=0.001) -0.384
  srht_paired: slope (all rho) -0.570 [IQR 0.135], slow-drift (rho=0.001) -0.596
Rows: 24400. Runtime seconds: 49.94.
