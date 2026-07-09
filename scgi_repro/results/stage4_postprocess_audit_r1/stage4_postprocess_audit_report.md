# Stage 4 Stripe Postprocess Audit

APL URED minimum CNR gate: `10.43`.

| method                      | target_free_threshold | cnr    | psnr   | ssim  | iou   | foreground_fraction | threshold | note                                                                   |
| --------------------------- | --------------------- | ------ | ------ | ----- | ----- | ------------------- | --------- | ---------------------------------------------------------------------- |
| raw_best_final              | True                  | 9.365  | 7.605  | 0.178 |       |                     |           | Continuous URED output.                                                |
| minmax_best_final           | True                  | 9.365  | 8.477  | 0.274 |       |                     |           | Linear display scaling only.                                           |
| raw_otsu_binary             | True                  | 15.288 | 25.423 | 0.987 | 0.987 | 0.212               | 0.550     | Otsu threshold from reconstruction histogram only.                     |
| minmax_otsu_binary          | True                  | 15.288 | 25.423 | 0.987 | 0.987 | 0.212               | 0.607     | Otsu threshold after min-max scaling; same mask as raw Otsu.           |
| raw_mean_binary             | True                  | 10.001 | 17.611 | 0.929 | 0.924 | 0.229               | 0.484     | Simple target-free mean threshold.                                     |
| raw_mean_plus_std_binary    | True                  | 14.121 | 24.436 | 0.986 | 0.983 | 0.209               | 0.580     | Simple target-free mean plus one standard deviation threshold.         |
| target_fraction_upper_bound | False                 | 16.469 | 25.710 | 0.987 | 0.987 | 0.213               | 0.540     | Upper bound using the true target foreground fraction; not deployable. |

## Interpretation

The continuous best stripe URED output remains below the APL gate, with CNR `9.365`.
A target-free Otsu threshold on the same reconstruction reaches CNR `15.288` and IoU `0.987`, which means the shape is largely present but the continuous CNR score is penalized by within-region gray variation.
This should not be counted as a strict paper reproduction unless a thresholded URED output is accepted as the reporting protocol; it is a strong diagnostic that the remaining Stage 4 gap is output calibration/post-processing rather than target localization.
