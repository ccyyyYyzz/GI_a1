# Fig. 2 Carrier Stationarity (r2)

Noiseless bucket carriers B_n are audited before applying any dynamic gain; carriers reproduce the r1 seed/config.
All exhaustively paired bases share the Parseval invariant carrier_cv = 1/sqrt(K_eff); the ordered pathology lives only in the temporal variance structure, exposed by the variance-envelope probes below (not by the CV magnitude).
Non-stationarity is detected by object-dependent temporal envelopes: Brown-Forsythe (levene_p), adjacent-window KS on |B_n - local mean| (ks_absdev_p), and the per-chunk std envelope CV (local_std_envelope_cv).
Running-mean CV is reported from frame >= 128 to drop the DC transient; the full-trace value is kept as running_mean_cv_incl_transient.
Levene (Brown-Forsythe) rejection tally:
  hadamard_paired: Levene rejects 5/10 objects (p<1e-3)
  hadamard_random_paired: Levene rejects 0/10 objects (p<1e-3)
  random_binary: Levene rejects 0/10 objects (p<1e-3)
  random_uniform: Levene rejects 0/10 objects (p<1e-3)
  srht_paired: Levene rejects 0/10 objects (p<1e-3)
Rows: 50. Runtime seconds: 4.55.
