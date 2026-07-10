# Experiment B2 -- Factorized Whitening Ablation (r1)

K=4096 (64x64), num_frames=8192, chunks=8, nperm=32, reject at Levene p<0.001.
Each arm applies a distinct subset of {P_col pixel-perm, D pixel-signs, P_row row/time-perm} to the same ordered natural-Hadamard baseline and 10-object panel; Levene = EXACT Fig. 2 r2b metric.
Physical-faithfulness guard (row_pixel_sign vs explicit interleaved-paired measurement): max abs diff 2.84e-14.
ordered: 7/10 = 0.700 reject.
row_perm_only: 39/320 = 0.122 reject.
pixel_perm_only: 18/320 = 0.056 reject.
sign_only: 139/320 = 0.434 reject.
pixel_sign: 38/320 = 0.119 reject.
row_pixel: 19/320 = 0.059 reject.
row_pixel_sign: 23/320 = 0.072 reject.
row_sign: 19/320 = 0.059 reject.
Rows: 2250. Runtime seconds: 22.49.
