# Fig. 2 Carrier Stationarity (r2b)

Noiseless bucket carriers B_n are audited before applying any dynamic gain; carriers reproduce the r1 seed/config.
Statistical-power upgrade over r2: num_frames=8192 per arm (image_size=64, num_pixels=4096), chunks=8, chunk_size=1024.
All exhaustively paired bases share the Parseval invariant carrier_cv = 1/sqrt(K_eff); the ordered pathology lives only in the temporal variance structure, exposed by the variance-envelope probes below (not by the CV magnitude).
Non-stationarity is detected by object-dependent temporal envelopes: Brown-Forsythe (levene_p), adjacent-window KS on |B_n - local mean| (ks_absdev_p), and the per-chunk std envelope CV (local_std_envelope_cv).
Running-mean CV is reported from frame >= 128 to drop the DC transient; the full-trace value is kept as running_mean_cv_incl_transient.
Levene (Brown-Forsythe) rejection tally:
  hadamard_paired: Levene rejects 7/10 objects (p<1e-3)
  hadamard_random_paired: Levene rejects 2/10 objects (p<1e-3)
  random_binary: Levene rejects 0/10 objects (p<1e-3)
  random_uniform: Levene rejects 0/10 objects (p<1e-3)
  srht_paired: Levene rejects 2/10 objects (p<1e-3)
Honest readout at this power: the ordered hadamard_paired arm rejects 7/10 objects.
hadamard_random_paired also rejects 2/10 at this chunk size (digit_2, stripe); these track objects with concentrated low-K_eff/structured energy (e.g. stripe, low-index digits) aliasing against the fixed-seed row permutation, not a genuine non-stationarity signal.
srht_paired also rejects 2/10 at this chunk size (digit_2, digit_3); these track objects with concentrated low-K_eff/structured energy (e.g. stripe, low-index digits) aliasing against the fixed-seed row permutation, not a genuine non-stationarity signal.
Rows: 50. Runtime seconds: 6.77.
