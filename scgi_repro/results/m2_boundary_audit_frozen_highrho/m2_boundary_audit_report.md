# M2 Boundary Audit

Source phase directory: `E:/GAN_FCC_WORK/github_sync/GI_a1_scgi_20260709_014434/scgi_repro/results/phase_m2_scgi_frozen_dense_r1_highrho_merged`

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

correction,challenger,observed_points,left_censored_points,not_reached_points,sigma_a_exponent,r2

agc,random_binary,3,0,2,-0.35266576993357884,0.9950057472285436

none,srht_paired,3,2,0,-0.9417758722549051,0.992130595121955

reference_k32,srht_paired,5,0,0,-1.4255903274938966,0.9862845984776658

reference_k8,srht_paired,5,0,0,-1.9285399494743396,0.9995089098299588

scgi_proxy,srht_paired,5,0,0,-1.5899376696523178,0.988902026284963



## Winner Summary

scope,basis,correction,winning_cells,rho_min,rho_max,sigma_min,sigma_max,psnr_mean_over_wins

all_non_oracle,srht_paired,reference_k2,43,0.001,10.0,0.05,0.5,22.283413232505385

all_non_oracle,srht_paired,pairwise,2,3.0,10.0,0.5,0.5,10.690180533088775

equal_frame_non_oracle,srht_paired,pairwise,45,0.001,10.0,0.05,0.5,20.01751905726239



## Interpretation Notes

- `observed` means the challenger crosses Hadamard within the sampled rho range using log-rho interpolation.
- `left_censored` means the challenger is already >= Hadamard at the smallest sampled rho; this is stronger than an observed boundary for that grid.
- `not_reached` means the challenger remains below Hadamard up to the largest sampled rho.
