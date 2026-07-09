# Stage 3 Static DGI Audit

This audit isolates the static DGI upper bound before any dynamic-channel correction.

## Manifest

- `profile`: full
- `image_size`: 128
- `active_num_patterns`: 16384
- `pattern_factors`: [4.0, 8.0, 16.0, 32.0, 64.0]
- `pattern_counts`: [65536, 131072, 262144, 524288, 1048576]
- `objects`: 8
- `requested_dataset_source`: mnist
- `device`: cuda
- `chunk_patterns`: 1024
- `elapsed_seconds`: 151.725
- `figures`: ['stage3_static_dgi_affine_psnr.png']

## Variant Summary

variant,objects,psnr_min,psnr_mean,affine_psnr_min,affine_psnr_mean,cnr_min,cnr_mean
minmax,40,9.706550598144531,16.80956611633301,15.824284553527832,27.35910608768463,4.2500810623168945,9.170440912246704
raw,40,6.722481727600098,12.476351284980774,15.824284553527832,27.359105944633484,4.250080585479736,9.17044107913971

## Interpretation

- Best affine-aligned random static DGI PSNR is `53.106` dB; mean is `27.359` dB.
- Best random static DGI CNR is `28.134`.
- Full paired-Hadamard exact inverse sanity PSNR minimum is `nan` dB.
- If affine-aligned PSNR remains far below 20 dB, the prompt PSNR gate is not blocked by a simple display-scale offset.
- If the exact orthogonal ceiling is high, the forward objects are reconstructable and the limiting factor is random-DGI correlation noise.
- The Hadamard exact row is a 2P-frame orthogonal sanity ceiling, not the APL random-DGI protocol.
- CNR remains the more appropriate paper-facing metric for the APL-style DGI reconstructions.
