# Stage 3 Static DGI Audit

This audit isolates the static DGI upper bound before any dynamic-channel correction.

## Manifest

- `profile`: full
- `image_size`: 128
- `active_num_patterns`: 16384
- `pattern_factors`: [1.0]
- `objects`: 8
- `requested_dataset_source`: mnist
- `device`: cuda
- `figures`: ['stage3_static_dgi_affine_psnr.png']

## Variant Summary

variant,objects,psnr_min,psnr_mean,affine_psnr_min,affine_psnr_mean,cnr_min,cnr_mean
hadamard_exact,8,80.0,80.0,80.0,80.0,6.495166778564453,75000003.29069692
minmax,8,7.457932472229004,8.65872859954834,11.2125244140625,14.012114405632019,2.4917948246002197,2.8712652921676636
raw,8,6.722494125366211,9.80280864238739,11.2125244140625,14.012114524841309,2.4917945861816406,2.871265321969986

## Interpretation

- Best affine-aligned random static DGI PSNR is `15.920` dB; mean is `14.012` dB.
- Best random static DGI CNR is `3.548`.
- Full paired-Hadamard exact inverse sanity PSNR minimum is `80.000` dB.
- If affine-aligned PSNR remains far below 20 dB, the prompt PSNR gate is not blocked by a simple display-scale offset.
- If the exact orthogonal ceiling is high, the forward objects are reconstructable and the limiting factor is random-DGI correlation noise.
- The Hadamard exact row is a 2P-frame orthogonal sanity ceiling, not the APL random-DGI protocol.
- CNR remains the more appropriate paper-facing metric for the APL-style DGI reconstructions.
