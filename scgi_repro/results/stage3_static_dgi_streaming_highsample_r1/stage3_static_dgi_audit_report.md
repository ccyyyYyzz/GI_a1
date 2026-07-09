# Stage 3 Static DGI Audit

This audit isolates the static DGI upper bound before any dynamic-channel correction.

## Manifest

- `profile`: full
- `image_size`: 128
- `active_num_patterns`: 16384
- `pattern_factors`: [128.0, 256.0]
- `pattern_counts`: [2097152, 4194304]
- `objects`: 8
- `requested_dataset_source`: mnist
- `device`: cuda
- `chunk_patterns`: 2048
- `elapsed_seconds`: 481.972
- `figures`: ['stage3_static_dgi_affine_psnr.png']

## Variant Summary

variant,objects,psnr_min,psnr_mean,affine_psnr_min,affine_psnr_mean,cnr_min,cnr_mean
minmax,16,18.929523468017578,22.92054522037506,31.33765411376953,35.3926842212677,6.3903398513793945,20.35467055439949
raw,16,6.722482681274414,9.80279991030693,31.33765411376953,35.3926842212677,6.390338897705078,20.354670882225037

## Interpretation

- Best affine-aligned random static DGI PSNR is `38.648` dB; mean is `35.393` dB.
- Best random static DGI CNR is `56.074`.
- Full paired-Hadamard exact inverse sanity PSNR minimum is `nan` dB.
- If affine-aligned PSNR remains far below 20 dB, the prompt PSNR gate is not blocked by a simple display-scale offset.
- If the exact orthogonal ceiling is high, the forward objects are reconstructable and the limiting factor is random-DGI correlation noise.
- The Hadamard exact row is a 2P-frame orthogonal sanity ceiling, not the APL random-DGI protocol.
- CNR remains the more appropriate paper-facing metric for the APL-style DGI reconstructions.
