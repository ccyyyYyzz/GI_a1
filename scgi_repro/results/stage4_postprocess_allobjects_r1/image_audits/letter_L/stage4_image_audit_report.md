# Stage 4 Image/ROI Audit

Object: `letter_L`
Source audit: `E:\GAN_FCC_WORK\github_sync\GI_a1_scgi_20260709_014434\scgi_repro\results\stage4_trace_audit_r3`

## Metrics

| method           | source_config          | steps | standard_cnr | bbox_cnr | standard_psnr | bbox_psnr |
| ---------------- | ---------------------- | ----- | ------------ | -------- | ------------- | --------- |
| static           |                        |       | 3.548        | 3.554    | 8.707         | 8.816     |
| dynamic          |                        |       | 0.049        | 0.051    | 5.765         | 5.771     |
| scgi             |                        |       | 3.548        | 3.554    | 8.709         | 8.818     |
| analytic         |                        |       | 3.548        | 3.554    | 8.707         | 8.817     |
| oracle           |                        |       | 3.548        | 3.554    | 8.707         | 8.817     |
| best_final       | nlm_allobjects/cfg0000 | 200   | 12.796       | 12.120   | 11.924        | 10.492    |
| best_trace_regen | nlm_allobjects/cfg0000 | 40    | 21.110       | 22.268   | 4.125         | 4.709     |

## Interpretation

The regenerated best Stage 4 stripe output has standard CNR 12.796, below the APL URED minimum 10.43.
Cropping to the target bounding box changes CNR by -0.677 (12.120 in the cropped box), so the miss is not explained by extra far-background pixels in the full-image mask.
The target-threshold sweep is invariant because the synthetic stripe target is binary.
The grid PNG should be used as a visual diagnostic, not as a replacement for the prompt CNR metric.
