# Stage 4 URED Continuous Binary r3 Grid Merge

Five Colab L4 shards completed and were merged for the strict continuous-output `denoiser=nlm` + binary-prior URED stripe refinement.

## Row Counts

- Metrics rows: 2916 / expected 2916
- Trace rows: 97686
- Summary rows: 2916

## Best Results

- Best final CNR: 9.933246 (APL URED min gate 10.43; pass=False)
- Best trace CNR: 9.933246 (pass=False)

Best final row:

source_import,config_id,config_index,global_config_index,init_seed,object,object_index,method,steps,lr,beta,xi,x_step,channels,blocks,residual_scale,denoiser,denoise_kernel,nlm_h,nlm_patch_size,nlm_patch_distance,otsu_temperature,binary_prior_weight,cnr,psnr,ssim,ks_d,ks_p,best_trace_cnr,final_loss,final_proxy_mean,final_proxy_std,final_proxy_min,final_proxy_max,final_proxy_range,final_proxy_tv_l1,final_proxy_roughness_l2,final_proxy_otsu_score,final_proxy_otsu_threshold,final_proxy_otsu_fg_fraction,final_proxy_hist_entropy,final_proxy_data_loss,final_proxy_aug_loss,final_proxy_denoiser_mse,final_proxy_binary_prior_loss,final_proxy_net_delta_mse,final_proxy_dual_abs_mean

pro1_stage4_ured_continuous_binary_refine_colab_r3grid_shard1of5,cfg0626,125,626,20240710,stripe_target,1,scgi_ured,32,0.0005,0.55,0.5,0.16,24,3,0.05,nlm,3,0.062,5,6,0.05,0.025,9.933245658874512,7.617018222808838,0.1919150948524475,0.0046856999397277,0.9740428844495652,9.933245658874512,0.002548411488533,0.4925968647003174,0.1045897677540779,0.1653587520122528,0.7985203266143799,0.6331615447998047,0.0785714387893676,0.01535040512681,0.0112164001911878,0.5483871102333069,0.2130126953125,1.5688740015029907,0.0002274657599627,0.0023209457285702,0.0043651084415614,0.0538155287504196,1.7220236259163357e-05,0.0745269507169723

## Interpretation

This larger strict continuous NLM/binary-prior refinement improves the previous merged best only modestly (9.898 -> 9.933) and remains below the APL URED minimum of 10.43. It supports shifting the next diagnostic from more SCGI/URED training toward the static DGI ceiling and estimator/frame-budget bottleneck.
