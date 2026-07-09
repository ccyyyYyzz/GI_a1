# Experiment B -- Multi-Permutation Whitening Power (r1)

K=4096 (64x64), num_frames=8192, chunks=8, nperm=32, reject at p<0.001.
Random arm: hadamard_random_paired carrier of each pixel-permuted object; Brown-Forsythe levene_p is the EXACT Fig. 2 r2b metric (run_paper_fig2_stationarity.stationarity_metrics).
walsh_flatness_ratio = max non-DC |FWHT((T_perm)^2)| / sum((T_perm)^2); high => peaked/aligned spectrum.
Mean random-arm rejection rate across all objects/perms: 0.059 (acceptance <~0.15).
Spearman(walsh_flatness_ratio, levene_p) = 0.092 (p=1.02e-01); expect NEGATIVE -- higher Walsh peak => smaller levene_p (more rejection).
Spearman(walsh_flatness_ratio, reject_indicator) = 0.070 (p=2.10e-01); expect POSITIVE.
Ordered (un-permuted natural-Hadamard) reference arm rejects 7/10 objects (Fig. 2 r2b expected ~7/10 at 8192 frames).
Rows: 330 (shard 0/1). Runtime seconds: 11.45.
