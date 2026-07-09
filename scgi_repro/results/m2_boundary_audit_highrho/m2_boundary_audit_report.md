# M2 Boundary Audit

Source phase directory: `E:/GAN_FCC_WORK/github_sync/GI_a1_scgi_20260709_014434/scgi_repro/results/phase_m2_scgi_proxy_dense_r1_highrho_merged`
Above-floor reconstruction gate: `rel_mse_mean < 0.5` for at least one method in a comparison.

## Rho Coverage

- `rho_min`: 0.001
- `rho_max`: 10.0
- `rho_count`: 9
- `rho_values`: [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0]
- `sigma_count`: 5
- `sigma_values`: [0.05, 0.1, 0.15, 0.3, 0.5]
- `covers_prompt_rho_upper_10`: True
- `covers_prompt_rho_lower_1e-3`: True

## Boundary Fits With R2 >= 0.9

correction,challenger,observed_points,left_censored_points,not_reached_points,sub_floor_only_points,above_floor_points,sigma_a_exponent,r2
none,srht_paired,3,2,0,0,29,-0.9417758722549051,0.992130595121955
reference_k32,srht_paired,3,0,2,0,29,-1.0962098363918604,0.9916007498823576
reference_k8,srht_paired,5,0,0,0,29,-1.9285399494743396,0.9995089098299588
scgi_proxy,srht_paired,5,0,0,0,29,-1.5899376696523178,0.988902026284963

## Winner Summary

scope,basis,correction,above_floor,winning_cells,rho_min,rho_max,sigma_min,sigma_max,psnr_mean_over_wins,rel_mse_mean_over_wins,above_floor_rel_mse
all_non_oracle,srht_paired,reference_k2,True,31,0.001,10.0,0.05,0.5,26.27564812111692,0.10214199827356296,0.5
all_non_oracle,sub_floor,noise_floor,False,14,0.1,10.0,0.1,0.5,11.787288450663173,0.7699156691535433,0.5
equal_frame_non_oracle,srht_paired,pairwise,True,29,0.001,10.0,0.05,0.5,24.606602788200792,0.12381399858286207,0.5
equal_frame_non_oracle,sub_floor,noise_floor,False,16,0.03,10.0,0.1,0.5,11.699804794936533,0.7835732301316235,0.5

## Above-Floor Accounting

- Pairwise challenger-vs-Hadamard cells: 914/1440 above-floor; 526 sub-floor.
- Winner-map cells across both scopes: 60/90 above-floor; 30 sub-floor.
- Sub-floor winner cells are retained in CSVs as `sub_floor + noise_floor` placeholders and should be greyed out in headline maps.

## Interpretation Notes

- `observed` means the challenger crosses Hadamard within the sampled rho range using log-rho interpolation after applying the above-floor gate.
- `left_censored` means the challenger is already >= Hadamard at the smallest sampled rho; this is stronger than an observed boundary for that grid.
- `not_reached` means the challenger remains below Hadamard up to the largest sampled rho.
- `sub_floor_only` means every sampled rho in that sigma/correction/challenger comparison is at reconstruction noise floor, so PSNR deltas are not reported as effects.