# Stage 4 Image/ROI Audit

Object: `ring`
Source audit: `E:\GAN_FCC_WORK\github_sync\GI_a1_scgi_20260709_014434\scgi_repro\results\stage4_trace_audit_r3`

## Metrics

| method           | source_config          | steps | standard_cnr | bbox_cnr | standard_psnr | bbox_psnr |
| ---------------- | ---------------------- | ----- | ------------ | -------- | ------------- | --------- |
| static           |                        |       | 2.982        | 2.993    | 8.290         | 8.483     |
| dynamic          |                        |       | 0.025        | 0.025    | 5.813         | 5.778     |
| scgi             |                        |       | 2.982        | 2.993    | 8.290         | 8.483     |
| analytic         |                        |       | 2.982        | 2.993    | 8.288         | 8.481     |
| oracle           |                        |       | 2.982        | 2.993    | 8.291         | 8.483     |
| best_final       | nlm_allobjects/cfg0001 | 200   | 7.842        | 7.146    | 11.404        | 8.614     |
| best_trace_regen | nlm_allobjects/cfg0001 | 64    | 14.300       | 12.512   | 3.483         | 4.359     |

## Interpretation

The regenerated best Stage 4 stripe output has standard CNR 7.842, below the APL URED minimum 10.43.
Cropping to the target bounding box changes CNR by -0.695 (7.146 in the cropped box), so the miss is not explained by extra far-background pixels in the full-image mask.
The target-threshold sweep is invariant because the synthetic stripe target is binary.
The grid PNG should be used as a visual diagnostic, not as a replacement for the prompt CNR metric.
