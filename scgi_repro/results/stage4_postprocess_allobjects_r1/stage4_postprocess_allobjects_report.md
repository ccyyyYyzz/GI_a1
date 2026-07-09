# Stage 4 All-Object Postprocess Audit

APL URED minimum CNR gate: `10.43`.
Objects: `letter_A, letter_L, ring, stripe_target`.

## Best Target-Free Postprocess Rows

| summary_source   | object        | postprocess_method       | cnr    | psnr   | ssim  | iou   | hits_apl_min | source_config                  | steps |
| ---------------- | ------------- | ------------------------ | ------ | ------ | ----- | ----- | ------------ | ------------------------------ | ----- |
| best_final       | letter_A      | raw_mean_plus_std_binary | 11.112 | 24.939 | 0.973 | 0.948 | True         | nlm_allobjects/cfg0001         | 200   |
| best_final       | letter_L      | raw_otsu_binary          | 34.910 | 35.154 | 0.998 | 0.997 | True         | nlm_allobjects/cfg0000         | 200   |
| best_final       | ring          | raw_mean_plus_std_binary | 9.332  | 21.316 | 0.958 | 0.946 | False        | nlm_allobjects/cfg0001         | 200   |
| best_final       | stripe_target | raw_otsu_binary          | 15.288 | 25.423 | 0.987 | 0.987 | True         | naf_capacity_stripe/cfg0000    | 36    |
| best_trace_regen | letter_A      | raw_mean_plus_std_binary | 22.505 | 22.566 | 0.958 | 0.925 | True         | nlm_allobjects/cfg0001         | 117   |
| best_trace_regen | letter_L      | raw_otsu_binary          | 70.550 | 31.352 | 0.994 | 0.992 | True         | nlm_allobjects/cfg0000         | 40    |
| best_trace_regen | ring          | raw_otsu_binary          | 21.163 | 23.336 | 0.973 | 0.966 | True         | nlm_allobjects/cfg0001         | 64    |
| best_trace_regen | stripe_target | raw_otsu_binary          | 15.288 | 25.423 | 0.987 | 0.987 | True         | nlm_microrefine_stripe/cfg0041 | 36    |

## Summary

Best-final target-free post-processing has minimum CNR `9.332` across the audited objects.
Best-trace target-free post-processing has minimum CNR `15.288` across the audited objects.
The best-trace rows still depend on target-aware step selection inherited from `stage4_trace_audit_r3`; only the threshold itself is target-free.
These outputs sharpen the interpretation of Stage 4: thresholded masks can clear the APL CNR gate across all held-out objects, but strict continuous-output URED remains below the original reproduction target.
