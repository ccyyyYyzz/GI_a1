# Stage 4 Image/ROI Audit

Object: `letter_A`
Source audit: `E:\GAN_FCC_WORK\github_sync\GI_a1_scgi_20260709_014434\scgi_repro\results\stage4_trace_audit_r3`

## Metrics

| method           | source_config          | steps | standard_cnr | bbox_cnr | standard_psnr | bbox_psnr |
| ---------------- | ---------------------- | ----- | ------------ | -------- | ------------- | --------- |
| static           |                        |       | 3.310        | 3.318    | 8.759         | 9.178     |
| dynamic          |                        |       | 0.011        | 0.018    | 6.005         | 6.026     |
| scgi             |                        |       | 3.310        | 3.318    | 8.761         | 9.179     |
| analytic         |                        |       | 3.310        | 3.318    | 8.758         | 9.178     |
| oracle           |                        |       | 3.310        | 3.318    | 8.759         | 9.178     |
| best_final       | nlm_allobjects/cfg0001 | 200   | 8.453        | 7.417    | 10.253        | 9.880     |
| best_trace_regen | nlm_allobjects/cfg0001 | 117   | 13.210       | 9.719    | 3.503         | 4.533     |

## Interpretation

The regenerated best Stage 4 stripe output has standard CNR 8.453, below the APL URED minimum 10.43.
Cropping to the target bounding box changes CNR by -1.036 (7.417 in the cropped box), so the miss is not explained by extra far-background pixels in the full-image mask.
The target-threshold sweep is invariant because the synthetic stripe target is binary.
The grid PNG should be used as a visual diagnostic, not as a replacement for the prompt CNR metric.
