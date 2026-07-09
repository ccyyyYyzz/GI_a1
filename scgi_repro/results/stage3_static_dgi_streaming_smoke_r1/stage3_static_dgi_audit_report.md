# Stage 3 Static DGI Audit

This audit isolates the static DGI upper bound before any dynamic-channel correction.

## Manifest

- `profile`: smoke
- `image_size`: 32
- `active_num_patterns`: 1024
- `pattern_factors`: [0.5, 1.0]
- `pattern_counts`: [512, 1024]
- `objects`: 5
- `requested_dataset_source`: synthetic
- `device`: cuda
- `chunk_patterns`: 128
- `elapsed_seconds`: 2.244
- `figures`: ['stage3_static_dgi_affine_psnr.png']

## Variant Summary

variant,objects,psnr_min,psnr_mean,affine_psnr_min,affine_psnr_mean,cnr_min,cnr_mean
minmax,10,7.503238201141357,8.594984531402588,9.811941146850586,13.43237943649292,1.7279325723648071,2.693676745891571
raw,10,6.885648727416992,10.12658257484436,9.811941146850586,13.43237943649292,1.7279324531555176,2.6936768770217894

## Interpretation

- Best affine-aligned random static DGI PSNR is `15.688` dB; mean is `13.432` dB.
- Best random static DGI CNR is `3.777`.
- Full paired-Hadamard exact inverse sanity PSNR minimum is `nan` dB.
- If affine-aligned PSNR remains far below 20 dB, the prompt PSNR gate is not blocked by a simple display-scale offset.
- If the exact orthogonal ceiling is high, the forward objects are reconstructable and the limiting factor is random-DGI correlation noise.
- The Hadamard exact row is a 2P-frame orthogonal sanity ceiling, not the APL random-DGI protocol.
- CNR remains the more appropriate paper-facing metric for the APL-style DGI reconstructions.
