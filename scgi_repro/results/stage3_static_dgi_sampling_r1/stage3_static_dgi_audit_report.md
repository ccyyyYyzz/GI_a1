# Stage 3 Static DGI Audit

This audit isolates the static DGI upper bound before any dynamic-channel correction.

## Manifest

- `profile`: full
- `image_size`: 128
- `active_num_patterns`: 16384
- `pattern_factors`: [0.25, 0.5, 1.0, 2.0]
- `objects`: 8
- `requested_dataset_source`: mnist
- `device`: cuda
- `figures`: ['stage3_static_dgi_affine_psnr.png']

## Variant Summary

variant,objects,psnr_min,psnr_mean,affine_psnr_min,affine_psnr_mean,cnr_min,cnr_mean
hadamard_exact,8,80.0,80.0,80.0,80.0,6.495166778564453,75000003.29069692
minmax,32,6.716050624847412,8.366911873221397,8.802316665649414,13.561504244804382,1.2345037460327148,2.587946005165577
raw,32,6.7224860191345215,9.802811950445175,8.802316665649414,13.561504453420639,1.2345036268234253,2.5879459530115128

## Interpretation

- Best affine-aligned random static DGI PSNR is `18.112` dB; mean is `13.562` dB.
- Best random static DGI CNR is `5.045`.
- Full paired-Hadamard exact inverse sanity PSNR minimum is `80.000` dB.
- If affine-aligned PSNR remains far below 20 dB, the prompt PSNR gate is not blocked by a simple display-scale offset.
- If the exact orthogonal ceiling is high, the forward objects are reconstructable and the limiting factor is random-DGI correlation noise.
- The Hadamard exact row is a 2P-frame orthogonal sanity ceiling, not the APL random-DGI protocol.
- CNR remains the more appropriate paper-facing metric for the APL-style DGI reconstructions.
