# Stage 4 Thresholded Trace Stop-Rule Audit

APL URED minimum CNR gate: `10.43`.
Metric rows: `3185`; stop-rule rows: `736`.

## Top Stop Rules

| postprocess_method       | rule                    | observations | mean_selected_cnr | min_selected_cnr | all_hit_apl_min | mean_regret_to_peak | max_regret_to_peak | mean_selected_step |
| ------------------------ | ----------------------- | ------------ | ----------------- | ---------------- | --------------- | ------------------- | ------------------ | ------------------ |
| minmax_otsu_binary       | fixed_step_117          | 4            | 23.866            | 15.211           | True            | 11.562              | 30.497             | 97.000             |
| raw_otsu_binary          | fixed_step_117          | 4            | 23.866            | 15.211           | True            | 11.562              | 30.497             | 97.000             |
| minmax_otsu_binary       | fixed_step_64           | 4            | 24.010            | 14.161           | True            | 11.418              | 32.696             | 57.250             |
| raw_otsu_binary          | fixed_step_64           | 4            | 24.010            | 14.161           | True            | 11.418              | 32.696             | 57.250             |
| raw_mean_plus_std_binary | fixed_step_117          | 4            | 22.910            | 13.509           | True            | 20.122              | 73.551             | 97.000             |
| raw_mean_plus_std_binary | fixed_step_40           | 4            | 22.534            | 13.509           | True            | 20.499              | 60.464             | 39.250             |
| raw_mean_plus_std_binary | fixed_step_64           | 4            | 20.066            | 13.509           | True            | 22.967              | 77.554             | 57.250             |
| minmax_otsu_binary       | fixed_step_40           | 4            | 28.502            | 12.757           | True            | 6.926               | 10.936             | 39.250             |
| raw_otsu_binary          | fixed_step_40           | 4            | 28.502            | 12.757           | True            | 6.926               | 10.936             | 39.250             |
| raw_mean_plus_std_binary | min_proxy_net_delta_mse | 4            | 11.629            | 9.885            | False           | 31.404              | 95.831             | 33.250             |
| raw_mean_plus_std_binary | fixed_step_36           | 4            | 17.705            | 9.526            | False           | 25.328              | 75.417             | 36.000             |
| raw_mean_plus_std_binary | final_step              | 4            | 16.396            | 9.332            | False           | 26.637              | 77.692             | 159.250            |

## Interpretation

At least one fully target-free rule/method combination clears the APL gate on all audited objects: `minmax_otsu_binary + fixed_step_117` has minimum CNR `15.211`.
This audit uses the same best-trace configurations identified earlier, but the step selection and thresholding rules are target-free.
Fixed-step rules select the nearest available recorded step; for shorter traces this is the final recorded step.
It should be read as a deployable-stopping diagnostic, not as a replacement for the original continuous URED protocol.
