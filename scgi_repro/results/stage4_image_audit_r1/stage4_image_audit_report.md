# Stage 4 Image/ROI Audit

Object: `stripe_target`
Source audit: `E:\GAN_FCC_WORK\github_sync\GI_a1_scgi_20260709_014434\scgi_repro\results\stage4_trace_audit_r3`

## Metrics

| method           | source_config                  | steps | standard_cnr | bbox_cnr | standard_psnr | bbox_psnr |
| ---------------- | ------------------------------ | ----- | ------------ | -------- | ------------- | --------- |
| static           |                                |       | 2.492        | 2.454    | 7.456         | 8.104     |
| dynamic          |                                |       | -0.009       | 0.000    | 5.890         | 5.718     |
| scgi             |                                |       | 2.492        | 2.454    | 7.458         | 8.104     |
| analytic         |                                |       | 2.492        | 2.454    | 7.462         | 8.105     |
| oracle           |                                |       | 2.492        | 2.454    | 7.456         | 8.103     |
| best_final       | naf_capacity_stripe/cfg0000    | 36    | 9.365        | 7.578    | 7.605         | 8.091     |
| best_trace_regen | nlm_microrefine_stripe/cfg0041 | 36    | 9.365        | 7.578    | 7.605         | 8.091     |

## Interpretation

The regenerated best Stage 4 stripe output has standard CNR 9.365, below the APL URED minimum 10.43.
Cropping to the target bounding box changes CNR by -1.787 (7.578 in the cropped box), so the miss is not explained by extra far-background pixels in the full-image mask.
The target-threshold sweep is invariant because the synthetic stripe target is binary.
The grid PNG should be used as a visual diagnostic, not as a replacement for the prompt CNR metric.
