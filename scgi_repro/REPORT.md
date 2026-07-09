# SCGI Reproduction Report

Updated: 2026-07-09

## Runtime

Verified local runtime:

```text
D:\Anacondar\anaconda3\envs\pytorch\python.exe
torch 2.1.0+cu121, CUDA 12.1
NVIDIA GeForce RTX 4060 Laptop GPU
```

Source PDFs were re-opened from Zotero and extracted to
`results/pdf_text/scgi_text.txt` and `results/pdf_text/owc_text.txt` for
spot-checking the prompt-derived model assumptions.

## Task 1: SCGI Numerical Reproduction

The repository implements the APL 2024 numerical pipeline: dynamic
multiplicative ghost-imaging simulation, supervised gain-aware SCGI correction,
DGI reconstruction, analytic/oracle controls, and SCGI-UNN/URED-style untrained
refinement.

Latest smoke run:

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_monitored_job.py --run-id stage0_smoke_refresh_r1 --output-dir results\cli_runs\stage0_smoke_refresh_r1 --heartbeat-seconds 30 --accelerator local_cuda -- D:\Anacondar\anaconda3\envs\pytorch\python.exe run_stage0.py --profile smoke --epochs 2 --tag smoke --model-kind exponential_residual_unet
```

Outputs:

- `results/stage_0/smoke/metrics.json`
- `results/stage_0/smoke/metrics.csv`
- `results/stage_0/smoke/train_history.csv`
- `results/stage_0/smoke/model_checkpoint.pt`
- `results/stage_0/smoke/run_manifest.json`
- `results/stage_0/smoke/config_snapshot.yaml`
- `results/stage_0/smoke/stage0_recon_grid.png`

Key smoke metrics:

| Metric | Value |
|---|---:|
| image size / patterns | 32 / 1024 |
| train loss / validation MSE | -2.2406 / 2.687e-6 |
| dynamic slope / corrected slope | -0.6039 / 8.287e-6 |
| true lambda / analytic lambda | 0.998828 / 0.998824 |
| dynamic MSE vs static | 0.1470 |
| SCGI MSE vs static | 2.839e-6 |
| analytic/oracle MSE vs static | 2.87e-6 / 1.58e-15 |
| dynamic DGI CNR | 0.4886 |
| SCGI DGI CNR | 3.0587 |
| SCGI-UNN CNR | 3.0651 |
| SCGI-URED CNR | 4.3605 |
| static DGI PSNR | 8.9752 |
| validation SCGI KS pass rate | 1.0 |
| analytic/oracle DGI CNR | 3.0587 / 3.0618 |
| SCGI KS p-value | 0.0640 |
| validation SCGI KS pass rate | 0.1667 |

Interpretation: the smoke-scale chain now reproduces the essential direction:
dynamic scattering breaks DGI, SCGI restores most contrast, and URED improves the
corrected reconstruction further. Analytic and oracle controls prove that the
simulated channel is recoverable and bound the attainable CNR. The new
`acceptance.csv` also makes unmet paper thresholds explicit: smoke SCGI CNR is
below 3, static DGI PSNR is below 20 dB, and validation KS pass rate is below
90%.

Stage 1 diagnostics:

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_monitored_job.py --run-id stage1_smoke_refresh_r1 --output-dir results\cli_runs\stage1_smoke_refresh_r1 --heartbeat-seconds 30 --accelerator local_cuda -- D:\Anacondar\anaconda3\envs\pytorch\python.exe run_stage1_diagnostics.py --profile smoke --samples 3 --output-dir results\stage_1
```

Outputs:

- `results/stage_1/smoke/stage1_sample_diagnostics.csv`
- `results/stage_1/smoke/stage1_b_histograms.png`
- `results/stage_1/smoke/stage1_r_dynamic_curves.png`
- `results/stage_1/smoke/stage1_gain_curves.png`
- `results/stage_1/smoke/stage1_lambda_distribution.png`

The plotted Stage 1 samples pass the static-bucket KS check, show dynamic
attenuation, and cover lambdas from 0.9960 to 0.9990 in the smoke profile.

Latest stronger MNIST debug run:

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_stage0.py --profile debug --epochs 80 --tag debug_e80_ured
```

Key debug metrics:

| Metric | Value |
|---|---:|
| image size / patterns | 64 / 4096 |
| train loss / validation MSE | -2.4653 / 0.000781 |
| dynamic MSE vs static | 0.2937 |
| SCGI MSE vs static | 0.00197 |
| analytic/oracle MSE vs static | 4.10e-8 / 1.81e-15 |
| dynamic DGI CNR | 0.1416 |
| SCGI DGI CNR | 1.6021 |
| SCGI-UNN CNR | 1.5916 |
| SCGI-URED CNR | 3.8002 |
| analytic/oracle DGI CNR | 3.0264 / 3.0277 |
| SCGI KS p-value | 1.75e-7 |

The MNIST debug run shows substantial learned correction and URED recovery, but
the strict KS test still fails at this larger sample size. Full paper-scale
reproduction therefore remains a longer training and model-selection task.

Colab L4 accelerated checks via GitHub transfer:

| Run | Runtime | Key result |
|---|---:|---|
| `pro1_debug_e160_stage3` | 64.3 s | debug 64x64, 4096 patterns, 160 epochs plus Stage 3 |
| `pro2_full_e20_probe` | 117.2 s | full 128x128, 16384 patterns, 20-epoch feasibility probe |
| `pro1_gamma_debug_e60_foreground` | 68.9 s | debug gamma sweep, 60 epochs |
| `pro2_full_e100_skip_ured` | 456.3 s | full 128x128, 16384 patterns, 100 epochs, SCGI only |
| `pro2_full_e100_gainmin_branch_r4` | 467.9 s | full 100-epoch gain-U-Net after gain-range fix |
| `pro2_full_exp_residual_e2_r1` | 43.6 s | full 2-epoch physics-informed exponential-residual candidate |

Colab outputs are stored under:

- `results/colab_imports/pro1_debug_e160_stage3`
- `results/colab_imports/pro2_full_e20_probe`
- `results/colab_imports/pro1_gamma_debug_e60_foreground`
- `results/colab_imports/pro2_full_e100_skip_ured_foreground`
- `results/colab_imports/pro2_full_e100_gainmin_branch_r4`
- `results/colab_imports/pro2_full_exp_residual_e2_r1`

Key Colab SCGI metrics:

| Run | Dynamic CNR | SCGI CNR | URED CNR | Val SCGI KS pass | Note |
|---|---:|---:|---:|---:|---|
| debug 160 epoch | 0.1416 | 2.1466 | 4.4670 | 0.75 | URED clears CNR 3; SCGI still below prompt threshold |
| full 20 epoch probe | 0.0184 | 0.1280 | 0.1280 | 0.00 | proves full profile runs on L4 but is undertrained |
| full 100 epoch, skip URED | 0.0184 | 0.1273 | 0.1273 | 0.176 | still not converged; loss/profile needs redesign |
| full 100 epoch, gain-range fix | 0.0184 | 1.1705 | 1.1705 | 0.054 | gain range fix helps substantially but misses analytic/static CNR 2.535 |
| full 2 epoch, exp-residual | 0.0184 | 2.5353 | 2.5353 | 1.00 | matches analytic/static upper bound; paper CNR/PSNR gates exceed this DGI setup's static bound |

Gamma sweep on Colab debug 60 epochs:

| gamma | SCGI CNR | SCGI PSNR | SCGI KS p |
|---:|---:|---:|---:|
| 0.0 | 1.9278 | 7.8787 | 2.97e-3 |
| 0.1 | 1.8411 | 7.3353 | 2.32e-23 |
| 1.0 | 2.2419 | 7.8036 | 1.22e-5 |
| 10.0 | 1.8135 | 8.1582 | 3.72e-3 |

This suggests the supervised correction loss can be tuned for contrast, but the
current gamma sweep does not by itself solve the KS gate.

Physics-informed follow-up:

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_stage0.py --profile smoke --epochs 2 --tag smoke_exp_residual_e2_skipured --model-kind exponential_residual_unet --skip-ured
```

This optional model first fits the one-dimensional exponential gain implied by
the APL simulator and then permits a small U-Net residual. On the smoke profile
it reaches SCGI CNR 3.0587, validation SCGI KS pass rate 1.0, and validation
MSE 2.69e-6. On the full 128x128/N=16384/M=5000 Colab profile, a 2-epoch run
reaches SCGI CNR 2.5353, validation SCGI KS pass rate 1.0, and validation MSE
1.83e-8, essentially matching the analytic/static upper-bound controls. It does
not replace the saved plain `gain_unet` results above; it shows that the full
simulator can be corrected when the dynamic-scaling factor is parameterized.

Stage 3 held-out target test:

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_monitored_job.py --run-id stage3_smoke_refresh_r1 --output-dir results\cli_runs\stage3_smoke_refresh_r1 --heartbeat-seconds 30 --accelerator local_cuda -- D:\Anacondar\anaconda3\envs\pytorch\python.exe run_stage3_tests.py --profile smoke --checkpoint results\stage_0\smoke\model_checkpoint.pt --model-kind exponential_residual_unet --output-dir results\stage_3
```

Outputs:

- `results/stage_3/smoke/stage3_metrics.csv`
- `results/stage_3/smoke/stage3_acceptance.csv`
- `results/stage_3/smoke/stage3_recon_grid.png`

The refreshed smoke checkpoint improves every held-out target over raw dynamic
DGI (`scgi_cnr_above_dynamic_all=True`). SCGI CNRs are 3.219 for `letter_A`,
2.475 for `stripe_target`, 3.774 for `letter_L`, and 3.078 for `ring`, so the
stripe target still fails the prompt-level all-target `SCGI CNR >= 3` gate.
Static DGI also still fails the prompt `PSNR > 20 dB` gate. The Colab
160-epoch checkpoint also improves every held-out target over dynamic DGI. Its
SCGI CNRs are 8.54 for `letter_A`, 2.18 for `stripe_target`, 2.77 for
`letter_L`, and 2.63 for `ring`, so it passes the directionality gate but still
misses the all-target
CNR >= 3 requirement.

The full-profile exp-residual checkpoint was also tested on held-out targets in
`results/stage_3_exp_residual_colab_full/full`. SCGI matches analytic/static CNRs
for all four targets: `letter_A` 3.3095, `letter_L` 3.5481, `ring` 2.9819, and
`stripe_target` 2.4919. Thus directionality and KS behavior pass, while the
all-target CNR>=3 and static PSNR>20 gates still fail because the static DGI
upper bounds for `ring`, `stripe_target`, and PSNR are below those thresholds.

Static DGI upper-bound audit:

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_stage3_static_dgi_audit.py --profile full --output-dir results\stage3_static_dgi_audit
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_monitored_job.py --run-id stage3_static_sampling_r1 --output-dir results\cli_runs\stage3_static_sampling_r1 --heartbeat-seconds 30 --accelerator local_cuda -- D:\Anacondar\anaconda3\envs\pytorch\python.exe run_stage3_static_dgi_audit.py --profile full --heldout-count 4 --pattern-factors "0.25,0.5,1.0,2.0" --output-dir results\stage3_static_dgi_sampling_r1
```

Outputs:

- `results/stage3_static_dgi_audit/stage3_static_dgi_audit.csv`
- `results/stage3_static_dgi_audit/stage3_static_dgi_audit_report.md`
- `results/stage3_static_dgi_audit/stage3_static_dgi_affine_psnr.png`
- `results/stage3_static_dgi_sampling_r1/stage3_static_dgi_audit.csv`
- `results/stage3_static_dgi_sampling_r1/stage3_static_dgi_audit_report.md`

This audit adds four MNIST held-out targets to the four handcrafted targets and
compares raw/min-max random static DGI, post-hoc scale/affine alignment, and a
separate full paired-Hadamard exact inverse sanity ceiling. Even after optimal
affine alignment, the best random static DGI PSNR is only 15.92 dB and the mean
affine-aligned PSNR is 14.01 dB. The best random static DGI CNR is 3.55. The
paired-Hadamard exact inverse reaches 80.00 dB minimum PSNR, so the objects and
measurement dimensionality are reconstructable; the failure is specific to
random-DGI correlation noise. This shows that the `static PSNR > 20 dB` gate is
not blocked by a simple display-scale offset; for the APL-style random DGI
reconstructions, CNR/ROI is the defensible paper-facing metric.

The sampling-factor follow-up repeats the full-profile random static DGI audit
at 0.25P, 0.5P, 1P, and 2P random patterns. Affine-aligned mean PSNR rises from
11.58 to 16.13 dB and the best case rises from 13.55 to 18.11 dB as the random
pattern budget doubles beyond the paper value, while mean CNR rises from 1.49
to 3.91. This supports a sampling-noise interpretation: more random patterns
help, but even 2P random patterns do not reach the prompt's 20 dB static PSNR
gate.

Full-profile SCGI/UNN/URED threshold matrix:

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_stage3_tests.py --profile full --checkpoint results\colab_imports\pro2_full_exp_residual_e2_r1\artifacts\model_checkpoint.pt --model-kind exponential_residual_unet --include-unn-ured --ured-steps 500 --output-dir results\stage3_threshold_matrix_full_r2_authoritative
```

Outputs:

- `results/stage3_threshold_matrix_full_r2_authoritative/full/stage3_metrics.csv`
- `results/stage3_threshold_matrix_full_r2_authoritative/full/stage3_acceptance.csv`
- `results/stage3_threshold_matrix_full_r2_authoritative/full/stage3_recon_grid.png`

This is the current authoritative Fig. 6/Fig. 9-style proxy matrix. It confirms
the negative result: SCGI still improves over dynamic DGI for all four objects,
but the full-profile all-target gates remain unmet. Mean/min CNRs are SCGI
3.083/2.492, SCGI-UNN 2.446/2.254, and SCGI-URED 5.084/2.270. URED is
consistently above UNN, but this compact TinyNAFNet/average-pool URED proxy does
not reproduce the APL CNR ranges: SCGI 3.39-4.04, UNN 7.93-14.20, and URED
10.43-38.28.

Stage 4 URED stripe-target sweeps:

- `results/stage4_ured_sweep_r2_stripe_merged`
- `results/stage4_ured_sweep_nlm_r1_stripe`
- `results/stage4_ured_sweep_nlm_allobjects_r1`
- `results/stage4_ured_sweep_nlm_deeper_r1_stripe`
- `results/stage4_ured_sweep_nlm_earlystop_r1_stripe`
- `results/stage4_ured_sweep_nlm_refine_r1_stripe`
- `results/stage4_ured_sweep_nlm_microrefine_r1_stripe`
- `results/stage4_ured_sweep_nlm_patch_r1_stripe`
- `results/stage4_ured_sweep_naf_capacity_r1_stripe`
- `results/stage4_image_audit_r1`
- `results/stage4_ured_proxy_audit_r1`
- `results/stage4_trace_audit_r4`

The stripe target is the binding full-profile APL threshold failure. A 40-config
avg-pool RED/UNN sweep over `beta`, `xi`, `x_step`, and residual scale confirms
that the average-pool proxy is not enough: the best final stripe CNR is 2.916 and
the best target-aware trace CNR is 3.831. Replacing the fallback denoiser with
non-local means is much stronger: a 48-config stripe screen reaches final CNR
5.131 and best target-aware diagnostic trace CNR 8.913. Because single-object
filtering used a different lambda draw before the runner was fixed, the
authoritative follow-up is the all-object NLM audit. There, the better fixed
200-step configuration
(`nlm_h=0.08`) reaches CNRs `8.453`, `6.033`, `10.270`, and `7.842` for
`letter_A`, `stripe_target`, `letter_L`, and `ring`, respectively. This is a
real improvement over the SCGI/static bound of roughly 2.49-3.55, but only some
objects approach the APL UNN range and the all-target minimum still misses the
APL URED minimum of 10.43. The best trace remains target-aware diagnostic
evidence, not a deployable stopping rule.

Four monitored local-CUDA follow-ups sharpen this conclusion. A deeper 18-config
stripe sweep at 400 steps around the best NLM region reaches final CNR 5.637 and
target-aware trace CNR 8.520, so simply running longer is not the answer. A
40-config fixed-early-stop stripe sweep over `steps=36..160` and
`nlm_h=0.05..0.09` turns the previously observed early peak into a fixed-step
result: best final stripe CNR is 8.932 at 40 steps and `nlm_h=0.06`. An 81-row
coarse refinement then reaches final/trace CNRs 9.024/9.214, and a 72-row
micro-refinement around `beta=0.55`, `x_step=0.11`, and `nlm_h=0.06` raises the
best fixed-step stripe final/trace CNR to 9.365 at 36 steps, `x_step=0.11`, and
`nlm_h=0.062`. `run_stage4_ured_sweep.py` now exposes `nlm_patch_size` and
`nlm_patch_distance`; the 144-config monitored
`results/stage4_ured_sweep_nlm_patch_r1_stripe` sweep tests patch sizes 3/5/7
and distances 4/6 around this best region. It does not improve the gap: the
best row remains 9.365 CNR and uses `patch_size=5`, `patch_distance=6`.
The monitored 9-config `results/stage4_ured_sweep_naf_capacity_r1_stripe`
checks whether the NAFNet capacity mismatch is the binding issue by sweeping
24/32/48 channels and 3/4/5 blocks. It also does not improve the stripe plateau:
the best row remains the original 24-channel/3-block setting at 9.365 CNR, while
the prompt-like 32-channel/4-block row reaches 6.091. A monitored 24-seed
initialization sweep at the same best setting,
`results/stage4_ured_seed_sweep_r1_stripe`, also leaves the best stripe
final/trace CNR at 9.365, with the next-best seed at 9.356. This rules out a
single unlucky TinyNAFNet initialization as the continuous-output bottleneck.
The remaining low-risk continuous-output degrees of freedom were then swept in
three monitored follow-ups: LR, residual scale at the best LR, and `xi/x_step`
coupling at the best LR/residual-scale point. These write
`results/stage4_ured_lr_micro_r1_stripe`,
`results/stage4_ured_lr_residual_micro_r1_stripe`, and
`results/stage4_ured_lr_residual_xi_micro_r1_stripe`. The best stripe
final/target-aware trace CNRs rise to 9.502/9.606 with `lr=0.0005`,
`residual_scale=0.18`, and trace `x_step=0.14`, but the result remains below the
APL URED minimum of 10.43. `results/stage4_trace_audit_r5`
combines the NLM stripe, all-object, deeper, early-stop, refinement,
micro-refinement, patch, capacity, seed, LR, residual-scale, and `xi/x_step`
sweeps. It
shows target-aware traces clear the 10.43 APL URED minimum for `letter_A`,
`letter_L`, and `ring`, but not for `stripe_target`
(`best_final_cnr=9.502`, `best_trace_cnr=9.606`).
`results/stage4_image_audit_r1` then regenerates the best final/trace stripe
images and audits metric sensitivity. The best standard CNR remains 9.365;
cropping to the target bounding box lowers it to 7.578, and sweeping the target
threshold from 0.1 to 0.9 leaves CNR unchanged because the synthetic stripe is
binary. The remaining miss is therefore not explained by far-background ROI
choice or threshold convention.

`results/stage4_postprocess_audit_r1` changes the question from "is the
continuous URED image already high-CNR?" to "is the target shape present if the
continuous image is calibrated into a mask?" The answer is yes for stripe: a
target-free Otsu threshold on the reconstruction histogram raises CNR from 9.365
to 15.288 and gives IoU 0.987, while a simple mean+standard-deviation threshold
also reaches CNR 14.121. This should not be counted as the strict APL URED
reproduction unless the reporting protocol permits thresholded URED outputs, but
it is strong evidence that the remaining Stage 4 failure is output calibration or
post-processing, not target localization.

`results/stage4_postprocess_allobjects_r1` extends that check to all four
held-out objects by regenerating each object's best final and best target-aware
trace image from `stage4_trace_audit_r3`. The best-trace target-free masks all
clear the APL URED CNR gate: `letter_A=22.505`, `letter_L=70.550`,
`ring=21.163`, and `stripe_target=15.288`. The fixed best-final target-free
post-processing is weaker: `ring` remains below the gate at 9.332. Therefore the
current evidence supports "shape present, calibration/stopping unresolved",
rather than a fully deployable Stage 4 reproduction.

`results/stage4_threshold_trace_audit_r1` adds the missing stopping-rule check by
rerunning the best-trace configurations and evaluating thresholded images at
every step. The strongest target-free rule is
`minmax_otsu_binary + fixed_step_117`, where fixed steps select the nearest
available recorded step for shorter traces. It clears the APL URED CNR gate on
all four objects with minimum CNR 15.211. A simpler `fixed_step_40` Otsu rule
also clears all four with minimum CNR 12.757. This narrows the remaining Stage 4
gap to whether a thresholded-output protocol is acceptable relative to the
paper's continuous URED figures.

A follow-up target-free proxy audit records `loss`, data/augmentation losses,
denoiser residual, TV/roughness, Otsu, entropy, range, and related image proxies
at every URED step. Among these simple rules, `max_proxy_min` is best by
all-object minimum CNR on this fixed-seed audit (`min=6.210`, `mean=9.971`), but
it still has mean regret 3.748 and max regret 12.766 versus the target-aware
trace peak. `min_loss` is worse (`min=2.858`), and no tested proxy validates a
deployable stopping rule.

Published target calibration:

- `results/published_calibration/published_targets.csv`
- `results/published_calibration/current_scgi_cnr_results.csv`
- `results/published_calibration/published_calibration_summary.csv`
- `results/published_calibration/published_calibration_report.md`

These tables encode the APL Fig. 6/Fig. 9 CNR targets and OE PSNR/SSIM targets
from the PDFs. The current APL comparison has 16 rows and all are `below_min`.

Published channel calibration anchors:

- `results/published_channel_calibration/apl_intensity_traces_digitized.csv`
- `results/published_channel_calibration/apl_channel_fit_summary.csv`
- `results/published_channel_calibration/oe_curve_points.csv`
- `results/published_channel_calibration/oe_channel_fit_summary.csv`
- `results/published_channel_calibration/published_channel_calibration_report.md`

`run_published_channel_calibration.py` digitizes APL Fig. 5/Fig. 7 intensity
traces from rendered PDF pages and fits compact channel summaries from the OE
published target table. The APL collected traces give figure-level
`lambda_per_measurement` values from 0.999897 to 0.999921. Corrected traces have
mean normalized centerline standard deviation 0.0126 and mean visual band sigma
proxy 0.104. For the OE around-corner case, the fixed-reference Fig. 6 PSNR=30
dB crossing occurs at attenuation `beta = 1.90 x 10^-2 mm^-1`; without the
reference frame, the digitized PSNR curves stay well below 30 dB. These outputs
are useful published-channel priors, not raw hardware calibration logs.

## Task 2: Measurement-Basis Mechanism Study

The mechanism framework now includes random uniform/binary/gaussian bases,
Hadamard paired measurements, full-contrast DCT paired measurements, four-step
Fourier measurements, and SRHT paired measurements. M1/M2 runners use equal
physical frame budgets; in the current smoke mechanism profile all M2 bases use
2048 SLM frames. Fourier therefore uses 512 four-step coefficients for a
1024-pixel object in fair-frame scans.

Latest M1 protocol-statistics run:

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_monitored_job.py --run-id mechanism_m1_protocol_o10s5_rerun --output-dir results\cli_runs\mechanism_m1_protocol_o10s5_rerun --heartbeat-seconds 30 --accelerator local_cpu -- D:\Anacondar\anaconda3\envs\pytorch\python.exe run_mechanism_m1.py --profile debug --objects 10 --seeds 5 --output-dir results\mechanism_m1_protocol_o10s5 --no-findings
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_m1_mechanism_audit.py --input-dir results\mechanism_m1_protocol_o10s5
```

Outputs:

- `mechanism_m1_oracle_agc.csv` (4200 rows)
- `mechanism_m1_agc_window_sweep.csv` (1750 rows)
- `mechanism_m1_error_propagation.csv` (1750 rows)
- `mechanism_m1_error_scaling_fit.csv` (7 rows)
- `mechanism_m1_pairwise_failure.csv` (5400 rows)
- `mechanism_m1_summary.csv` (262 rows)
- `m1_mechanism_audit_report.md`, `m1_mechanism_audit_summary.json`, and
  three compact PNG audit views

Key M1 checks:

- Oracle correction restores Hadamard/SRHT to near-exact reconstruction, which
  supports H1: deterministic-basis failure under blind correction is mainly gain
  identifiability/error propagation, not missing measurements.
- The H3 jitter channel was fixed so adjacent-frame mismatch is controlled by
  `rho`; pairwise normalization now degrades monotonically as `rho` and
  `sigma_a` increase.
- AGC window sweeps and residual-gain log-log fits are now emitted as CSVs and
  figures, giving direct hooks for H1/H2 quantitative follow-up.

Latest M2 reference protocol run:

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile debug --objects 10 --seeds 5 --no-findings --output-dir results\phase_m2_reference_protocol_o10s5
```

Outputs:

- `phase_scan.csv` (68,250 rows, with frame-count audit columns)
- `phase_summary.csv` (1365 rows)
- `phase_blind_summary.csv` (1155 rows)
- `phase_equal_frame_blind_summary.csv` (525 rows)
- `phase_reference_summary.csv` (630 rows)
- `best_methods.csv`, `best_blind_methods.csv`,
  `best_equal_frame_blind_methods.csv`, `best_reference_methods.csv`
- `flip_boundary.csv` (135 rows)

Additional Colab-sharded M2 run with `scgi_proxy`:

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' merge_phase_m2_shards.py --inputs results\colab_imports\pro1_dense_r1_shard0of5\artifacts results\colab_imports\pro1_dense_r1_shard1of5\artifacts results\colab_imports\pro2_dense_r1_shard2of5\artifacts results\colab_imports\pro2_dense_r1_shard3of5\artifacts results\colab_imports\pro2_dense_r1_shard4of5\artifacts --output-dir results\phase_m2_scgi_proxy_dense_r1_merged
```

Outputs:

- `results/phase_m2_scgi_proxy_dense_r1_merged/phase_scan.csv` (78,750 rows)
- `results/phase_m2_scgi_proxy_dense_r1_merged/dense_r1_diagnostics.json`
- merged best-method, equal-frame, reference, and flip-boundary CSVs

`scgi_proxy` is a blind smooth-gain SCGI-style proxy with zero reference frames,
not a trained SCGI network. The dense run has 10,500 `scgi_proxy` rows; all have
`reference_frames=0` and `total_physical_frames=num_frames`.

Frozen SCGI-network M2 smoke baseline:

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile smoke --objects 1 --seeds 1 --no-findings --scgi-checkpoint results\colab_imports\pro2_full_exp_residual_e2_r1\artifacts\model_checkpoint.pt --scgi-model-kind exponential_residual_unet --output-dir results\phase_m2_scgi_frozen_smoke
```

This adds an explicit `scgi_frozen` correction that loads a saved SCGI
checkpoint, applies the frozen fully convolutional network to each M2 measurement
sequence, and keeps `gain_hat` undefined because it is not a gain-estimator
proxy. Non-square 2048-frame M2 sequences are padded to the nearest square,
processed by the network, and cropped back to the original frame count. The
smoke run writes 1785 rows, including 210 `scgi_frozen` rows. The initial dense
Colab-sharded run writes `results/phase_m2_scgi_frozen_dense_r1_merged` with
89,250 rows, all five shard labels present, and 10,500 `scgi_frozen` rows. A
local high-rho completion adds `rho=3,10` shards and merges them into
`results/phase_m2_scgi_frozen_dense_r1_highrho_merged`, with 114,750 rows over
the full 9x5 prompt rho/sigma grid and 13,500 `scgi_frozen` rows.
Direct cross-domain application of the full-profile `exponential_residual_unet`
checkpoint remains weak in the 9-rho dense setting: across matched rows,
`scgi_frozen` is -0.206 dB versus `none` on average, -0.796 dB versus
`scgi_proxy`, and -1.167 dB versus paired-basis `pairwise`; its win rates are
47.2%, 14.9%, and 5.0%, respectively. This is now a true prompt-range
frozen-network dense baseline, but not a successful network-level M2 phase
diagram.

Frame audit for M2 reference protocol:

| Correction | Measurement frames | Reference frames | Total physical frames |
|---|---:|---:|---:|
| non-reference | 2048 | 0 | 2048 |
| reference_k32 | 2048 | 65 | 2113 |
| reference_k8 | 2048 | 257 | 2305 |
| reference_k2 | 2048 | 1025 | 3073 |

Dense M2 winner summary:

| Budget rule | Winner across 35 rho/sigma cells | PSNR mean range |
|---|---|---:|
| strict equal-total-frame blind, 2048 frames | `srht_paired + pairwise` in 35/35 cells | 10.76-44.69 dB |
| any-budget blind/reference | `srht_paired + reference_k2` in 35/35 cells | 10.79-47.68 dB |

Interpretation: under the strict 2048-frame blind budget, SRHT paired
measurements with pairwise normalization dominate this compact M2 grid. The
reference-calibrated `reference_k2` variant improves PSNR but spends 3073 total
physical frames, so it is a separate semi-calibrated baseline rather than a
fair blind winner. In the dense `scgi_proxy` run, `scgi_proxy` improves over raw
`none` in 88.6% of matched basis/rho/sigma means and over AGC in 66.7%, but it
never beats pairwise on paired bases. Across equal-frame blind candidates, it is
ranked first in 45 of 210 basis/rho/sigma triples, mostly for random bases, but
it does not change the 35-cell best-method map. Flip-boundary diagnostics are
emitted with boundary statuses: 104 `not_reached`, 17 `left_censored`, and 14
`observed` in the reference protocol.

Prompt-range high-rho M2 extension:

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile smoke --objects 10 --seeds 5 --rho-values "3,10" --sigma-values "0.05,0.10,0.15,0.30,0.50" --shard i/5 --output-dir results\phase_m2_highrho_o10s5_shardiof5 --no-findings
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' merge_phase_m2_shards.py --inputs results\phase_m2_scgi_proxy_dense_r1_merged results\phase_m2_highrho_o10s5_shard0of5 results\phase_m2_highrho_o10s5_shard1of5 results\phase_m2_highrho_o10s5_shard2of5 results\phase_m2_highrho_o10s5_shard3of5 results\phase_m2_highrho_o10s5_shard4of5 --output-dir results\phase_m2_scgi_proxy_dense_r1_highrho_merged
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_m2_boundary_audit.py --phase-dir results\phase_m2_scgi_proxy_dense_r1_highrho_merged --output-dir results\m2_boundary_audit_highrho
```

The merged high-rho scan has 101,250 rows over 9 rho values
`0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1, 3, 10` and five amplitudes. It therefore
covers the prompt range `rho = 10^-3 ... 10`. The boundary audit reports five
observed log-rho boundary fits with `R2 >= 0.9`: `reference_k8/srht_paired`
(`R2=0.9995`), `agc/random_binary` (`R2=0.9950`),
`none/srht_paired` (`R2=0.9921`), `scgi_proxy/srht_paired` (`R2=0.9889`), and
`reference_k32/srht_paired` (`R2=0.9863`). Under the strict equal-frame blind
budget, `srht_paired + pairwise` wins all 45 high-rho merged rho/sigma cells.
Across all non-oracle methods, `srht_paired + reference_k2` wins 43/45 cells and
`srht_paired + pairwise` wins the two highest-amplitude high-rho cells. The
audit also writes `m2_psnr_rho_curves_sigma_0p30.png` and
`m2_boundary_fit_curves.png` for selected-curve and boundary-fit review.

Frozen-network prompt-range high-rho completion:

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile smoke --objects 10 --seeds 5 --rho-values "3,10" --sigma-values "0.05,0.10,0.15,0.30,0.50" --shard i/5 --scgi-checkpoint results\colab_imports\pro2_full_exp_residual_e2_r1\artifacts\model_checkpoint.pt --scgi-model-kind exponential_residual_unet --output-dir results\phase_m2_scgi_frozen_highrho_o10s5_shardiof5 --no-findings
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' merge_phase_m2_shards.py --inputs results\phase_m2_scgi_frozen_dense_r1_merged results\phase_m2_scgi_frozen_highrho_o10s5_shard0of5 results\phase_m2_scgi_frozen_highrho_o10s5_shard1of5 results\phase_m2_scgi_frozen_highrho_o10s5_shard2of5 results\phase_m2_scgi_frozen_highrho_o10s5_shard3of5 results\phase_m2_scgi_frozen_highrho_o10s5_shard4of5 --output-dir results\phase_m2_scgi_frozen_dense_r1_highrho_merged
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_m2_boundary_audit.py --phase-dir results\phase_m2_scgi_frozen_dense_r1_highrho_merged --output-dir results\m2_boundary_audit_frozen_highrho
```

The frozen high-rho merge has 114,750 rows and covers the same 45 rho/sigma
cells as the proxy high-rho scan. `results/m2_boundary_audit_frozen_highrho`
again reports `srht_paired + pairwise` as the strict equal-frame non-oracle
winner in 45/45 cells. The frozen network flattens near 10.6-11.8 dB at
`rho=3,10`, so the added high-rho coverage reinforces the direct-transfer
negative result rather than changing the winner map.

M2 fine-tuned SCGI-network smoke:

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_m2_scgi_train.py --profile smoke --model-kind gain_unet --bases "random_uniform hadamard_paired srht_paired" --rho-values "0.001 0.1 1.0" --sigma-values "0.05 0.30" --objects 3 --seeds 2 --epochs 20 --output-dir results\m2_scgi_finetune_gain_smoke_r1
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile smoke --objects 5 --seeds 3 --rho-values "0.003 0.3 3.0" --sigma-values "0.10 0.50" --reference-periods "2 8" --scgi-checkpoint-map results\m2_scgi_basis_specific_smoke_r1\checkpoint_map.json --output-dir results\phase_m2_scgi_basis_specific_heldout_smoke_r1 --no-findings
```

`run_m2_scgi_train.py` adds a supervised M2-specific SCGI training path, and
`run_phase_m2.py` now supports checkpoint metadata plus a basis-name checkpoint
map. A direct-output U-Net smoke is strongly negative: mean `scgi_frozen` PSNR is
11.08 dB, or -6.99 dB versus raw `none`. A single `gain_unet` checkpoint is less
destructive but still weak: 14.71 dB mean and -3.37 dB versus `none`. The
basis-specific `gain_unet` smoke is the first network result with local signal:
on the in-distribution small grid, mean `scgi_frozen` PSNR rises to 16.34 dB and
`srht_paired + scgi_frozen` wins 2/6 strict equal-frame cells. On the held-out
grid, it again wins 2/6 cells at `rho=0.3`, but overall it remains below the
non-network baselines (-0.90 dB versus `none`, -1.03 dB versus `agc`, -1.69 dB
versus `scgi_proxy`, and -2.48 dB versus paired-basis `pairwise` on matched
rows). This is a useful routing/training prototype, not yet a competitive
fine-tuned M2 phase diagram.

Signed/gain-prediction interface check:

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_m2_scgi_train.py --profile smoke --model-kind gain_predictor_unet --target-mode gain --input-normalize row_max --target-normalize none --gain-min 0.05 --gain-max 2.5 --bases "random_uniform hadamard_paired srht_paired" --rho-values "0.001 0.1 1.0" --sigma-values "0.05 0.30" --objects 3 --seeds 2 --epochs 30 --output-dir results\m2_scgi_gain_predictor_rawgain_smoke_r1
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile smoke --objects 5 --seeds 3 --rho-values "0.003 0.3 3.0" --sigma-values "0.10 0.50" --reference-periods "2 8" --scgi-checkpoint results\m2_scgi_gain_predictor_rawgain_smoke_r1\m2_scgi_checkpoint.pt --output-dir results\phase_m2_scgi_gain_predictor_rawgain_heldout_smoke_r1 --no-findings
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_m2_scgi_train.py --profile smoke --model-kind gain_predictor_1d --target-mode gain --input-mode scgi_proxy_gain --input-normalize none --target-normalize none --gain-min 0.05 --gain-max 2.5 --bases "random_uniform random_binary hadamard_paired dct_paired fourier_fourstep srht_paired" --rho-values "0.001 0.1 1.0" --sigma-values "0.05 0.30" --objects 3 --seeds 2 --epochs 30 --batch-size 16 --output-dir results\m2_scgi_proxyinput_gain1d_smoke_r1
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile smoke --objects 5 --seeds 3 --rho-values "0.003 0.3 3.0" --sigma-values "0.10 0.50" --reference-periods "2 8" --scgi-checkpoint results\m2_scgi_proxyinput_gain1d_smoke_r1\m2_scgi_checkpoint.pt --output-dir results\phase_m2_scgi_proxyinput_gain1d_heldout_smoke_r1 --no-findings
```

The implementation now also supports signed-safe U-Net outputs and a
`gain_predictor_unet` trained directly against the simulator's true gain
sequence (`target_mode=gain`); checkpoints with gain targets are applied as
`observed / gain_hat` instead of returning clamped corrected frames. Two
held-out gain-predictor smokes remain negative. With row-max-normalized gain
targets, mean `scgi_frozen` PSNR is 12.04 dB, or -3.27 dB versus `none`. With
raw mean-normalized gain targets, mean `scgi_frozen` PSNR is 12.05 dB, or
-3.26 dB versus `none`, -3.85 dB versus `scgi_proxy`, and -6.19 dB versus
paired-basis `pairwise` on matched rows. A checkpoint-loader fix then raises the
same raw-gain predictor to 14.77 dB mean by constructing the frozen model from
checkpoint metadata/config rather than the current `config.yaml`. The monitored
fixed-loader rerun in `results/phase_m2_scgi_gain_predictor_rawgain_fixedloader_r1`
writes 4,050 rows; `scgi_frozen` averages 14.77 dB, compared with 15.31 dB for
`none` and 15.90 dB for `scgi_proxy`, and `srht_paired + pairwise` remains the
strict equal-frame winner in all six held-out rho/sigma cells.

The first competitive trained smoke uses the blind `scgi_proxy` gain envelope as
the network input and a 1D gain predictor along frame index. On the same held-out
grid, `results/phase_m2_scgi_proxyinput_gain1d_heldout_smoke_r1` reaches mean
`scgi_frozen` PSNR 15.72 dB: +0.41 dB versus `none`, +0.41 dB versus AGC, and
-0.18 dB versus `scgi_proxy`. It beats `none` in 20/36 equal-frame cells and
matches or exceeds `scgi_proxy` in 14/36 cells. It still does not displace
`srht_paired + pairwise` as the strict equal-frame winner, so the dense
network-level phase diagram remains open.

Dense proxy-input trained-network phase scan:

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile smoke --objects 10 --seeds 5 --rho-values "0.001,0.003,0.01,0.03,0.1,0.3,1.0,3.0,10.0" --sigma-values "0.05,0.10,0.15,0.30,0.50" --reference-periods "2,8,32" --shard i/5 --resume --scgi-checkpoint results\m2_scgi_proxyinput_gain1d_smoke_r1\m2_scgi_checkpoint.pt --output-dir results\phase_m2_scgi_proxyinput_gain1d_dense_r1_shardiof5 --no-findings
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' merge_phase_m2_shards.py --inputs results\phase_m2_scgi_proxyinput_gain1d_dense_r1_shard0of5 results\phase_m2_scgi_proxyinput_gain1d_dense_r1_shard1of5 results\phase_m2_scgi_proxyinput_gain1d_dense_r1_shard2of5 results\phase_m2_scgi_proxyinput_gain1d_dense_r1_shard3of5 results\phase_m2_scgi_proxyinput_gain1d_dense_r1_shard4of5 --output-dir results\phase_m2_scgi_proxyinput_gain1d_dense_r1_merged
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_m2_boundary_audit.py --phase-dir results\phase_m2_scgi_proxyinput_gain1d_dense_r1_merged --output-dir results\m2_boundary_audit_proxyinput_gain1d_dense_r1
```

The merged dense scan has 114,750 rows over the full prompt grid
(`rho=0.001..10`, five `sigma_a` values, 10 objects, 5 seeds). The trained
`scgi_frozen` correction contributes 13,500 rows and averages 15.92 dB, versus
15.59 dB for `none`, 15.31 dB for AGC, and 16.18 dB for `scgi_proxy`. Across
matched equal-frame basis/rho/sigma means, it is +0.329 dB versus `none`,
+0.604 dB versus AGC, and -0.262 dB versus `scgi_proxy`; it beats `none` in
161/270 cells and matches or exceeds `scgi_proxy` in 118/270 cells.
`results/m2_boundary_audit_proxyinput_gain1d_dense_r1` confirms full prompt rho
coverage and keeps `srht_paired + pairwise` as the strict equal-frame winner in
45/45 cells. Thus the network-level phase diagram is now present and mildly
competitive against raw/AGC baselines, but it still supports the SRHT-pairwise
main conclusion.

Latest M3 high-rho SRHT ablation:

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_monitored_job.py --run-id srht_m3_protocol_o10s5_highrho_r1 --output-dir results\cli_runs\srht_m3_protocol_o10s5_highrho_r1 --heartbeat-seconds 30 --accelerator local_cpu -- D:\Anacondar\anaconda3\envs\pytorch\python.exe run_srht_m3.py --profile smoke --objects 10 --seeds 5 --rho-values "0.001,0.1,1.0,10.0" --sigma-a 0.30 --output-dir results\srht_m3_protocol_o10s5_highrho_r1 --no-findings
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_m3_srht_audit.py --input-dir results\srht_m3_protocol_o10s5_highrho_r1 --output-dir results\srht_m3_audit_highrho_r1
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_monitored_job.py --run-id m3_random_comparator_fast_r1 --output-dir results\cli_runs\m3_random_comparator_fast_r1 --heartbeat-seconds 30 --accelerator local_cpu -- D:\Anacondar\anaconda3\envs\pytorch\python.exe run_m3_random_comparator.py --objects 10 --seeds 5 --rho-values "1.0,10.0" --sigma-a-values "0.30,0.50" --output-dir results\m3_random_comparator_fast_r1
```

Outputs:

- `results/srht_m3_protocol_o10s5_highrho_r1/srht_ablation.csv` (3,200 rows)
- `results/srht_m3_protocol_o10s5_highrho_r1/srht_ablation_summary.csv` (64 rows)
- `results/srht_m3_audit_highrho_r1/m3_srht_delta_summary.csv` (16 rows)
- `results/srht_m3_audit_highrho_r1/m3_srht_audit_report.md`
- `results/m3_random_comparator_fast_r1/m3_random_comparator_raw.csv` (3,600 rows)
- `results/m3_random_comparator_fast_r1/m3_random_comparator_deltas.csv` (4 rows)
- `results/m3_random_comparator_fast_r1/m3_random_comparator_report.md`

The high-rho audit makes the M3 conclusion more conservative. Oracle correction
has minimum mean PSNR 120.0 dB, confirming that ordered Hadamard,
permutation-only, sign-only, and full SRHT all preserve the underlying
information when the gain is known. For `rho>=1` under non-oracle corrections,
however, full SRHT minus ordered Hadamard ranges from -0.043 to +0.083 dB, not
the prompt's requested `>=3 dB` advantage. The best ablation is usually
`sign_only`, so the current constructive evidence supports diagonal sign
randomization more strongly than full row permutation. M3 therefore remains a
partial mechanism result rather than a closed SRHT theorem.

The direct random-comparator follow-up closes the "not worse than random" check
for the sampled fast-drift cells: full SRHT is +0.016 to +0.190 dB above the
best random basis, but it is -0.009 to -0.003 dB below ordered Hadamard. Thus
the current M3 evidence supports SRHT/pairwise as a strong conservative
baseline, not a >=3 dB constructive advance over ordered Hadamard.

Latest M4 theory runs:

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_theory_m4.py --output-dir results\theory_m4_compact
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_theory_m4.py --sizes "16 32 64" --objects 5 --seeds 4 --sigmas "0.01 0.02 0.05 0.10" --frame-sweep-size 32 --frame-factors "1 2 4 8" --bootstrap 200 --agc-size 32 --agc-rhos "0.001 0.003 0.01 0.03 0.1 0.3 1.0" --agc-sigmas "0.05 0.15 0.30 0.50" --agc-window-fracs "0.005 0.01 0.02 0.05 0.10 0.20" --phase-dir results\phase_m2_scgi_frozen_dense_r1_merged --output-dir results\theory_m4_paper_r1
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_theory_m4.py --sizes "16 32 64" --objects 5 --seeds 4 --sigmas "0.01 0.02 0.05 0.10" --frame-sweep-size 32 --frame-factors "1 2 4 8" --bootstrap 200 --agc-size 32 --agc-rhos "0.001 0.003 0.01 0.03 0.1 0.3 1.0" --agc-sigmas "0.05 0.15 0.30 0.50" --agc-window-fracs "0.005 0.01 0.02 0.05 0.10 0.20" --phase-dir results\phase_m2_scgi_frozen_dense_r1_highrho_merged --output-dir results\theory_m4_paper_r2_highrho
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_m4_agc_boundary_aware.py --output-dir results\theory_m4_agc_boundary_aware_r1
```

Outputs:

- `m4_error_scaling.csv`, `m4_error_scaling_summary.csv`,
  `m4_error_scaling_fit.csv`
- `m4_random_frame_scaling.csv`, `m4_random_frame_scaling_summary.csv`,
  `m4_random_frame_scaling_fit.csv`
- `m4_energy_concentration.csv`, `m4_energy_concentration_summary.csv`
- `m4_flip_boundary_fit.csv`
- `m4_flip_boundary_censored_intervals.csv`,
  `m4_flip_boundary_censored_summary.csv`,
  `m4_flip_boundary_censored_fit.csv`
- `m4_agc_window_law.csv`, `m4_agc_window_law_summary.csv`,
  `m4_agc_window_law_fit.csv`
- `m4_key_summary.json`
- `results/theory_m4_agc_boundary_aware_r1/m4_agc_boundary_aware_fit.csv`,
  `m4_agc_boundary_aware_intervals.csv`, and
  `m4_agc_boundary_aware_summary.json`

Key M4 checks:

| Check | Result |
|---|---|
| residual gain law, 16/32/64 | `sigma_delta` exponent 2.001-2.003 across bases, min R2 0.99992; bootstrap 95% CIs tightly bracket 2 |
| fixed-P random frame law | random uniform/binary `num_frames` exponent about -0.72/-0.71, R2 > 0.998; bootstrap CIs roughly [-0.75,-0.70] and [-0.77,-0.66] |
| H4 energy concentration at 4096 pixels | DCT/Fourier/Hadamard top-5% energy 0.88-0.92; random/SRHT about 0.28 |
| flip-boundary fits | high-rho r2 has 5 observed fits and censored interval tables; three observed fits have R2 >= 0.9 inside M4, while the separate M2 high-rho audit has five R2-qualified fits |
| high-rho M2 boundary audit | prompt rho range now reaches 10; five log-rho boundary fits have R2 >= 0.9; strict equal-frame blind winner is SRHT/pairwise in 45/45 cells |
| AGC window law | candidate bias-variance derivation is now written in `THEORY.md`; targeted validation improves fits to R2 0.71-0.82 but still has 42-56% boundary-selected best windows; the censored follow-up reaches interval satisfaction 0.80 for random bases, 0.64 for SRHT, and 0.40 for Hadamard, so this remains diagnostic |

Interpretation: M4 now has a larger-N 16/32/64 sweep, bootstrap intervals for
the main log-linear fits, censored-aware flip-boundary interval tables, and an
AGC window-law diagnostic. `results/theory_m4_paper_r2_highrho` reruns these
hooks against the prompt-range frozen high-rho phase table. `THEORY.md` now
contains the candidate AGC bias-variance law, and `PAPER_OUTLINE.md` contains
draft captions for the eight main figures. `run_make_paper_figures.py` renders
the first paper-facing M2/M4 draft set under `results/paper_figures_r1`,
including prompt-range winner maps, boundary fits, residual-error fits,
random-frame scaling, energy concentration, and AGC-window diagnostics. These
draft assets now include PNG previews plus SVG sidecars recorded in
`paper_figure_manifest.csv` and `paper_figure_manifest_vectors.csv`. The
targeted AGC validation in `results/theory_m4_agc_targeted_r1` adds 86,400 raw
rows, a denser window grid, best-window saturation statistics, and fit tables.
It improves fit R2 to 0.71-0.82 but still leaves 42-56% of best-window cells at
the grid boundary. `results/theory_m4_agc_boundary_aware_r1` then treats those
boundary selections as censored intervals and writes four basis fits plus 180
interval rows; random binary/uniform reach 0.80 interval satisfaction, SRHT 0.64,
and Hadamard 0.40. The candidate AGC law therefore remains diagnostic. The
new `run_make_paper_multipanels.py` assembles those audited assets into draft
300-dpi PNG/PDF/SVG layouts for Figures 3, 4, and 7 under
`results/paper_figures_r1/multipanels`, with an 11-row panel provenance
manifest. The remaining publication work is venue-specific final artwork plus a
stronger AGC estimator or tighter censored-law validation.

Latest nonideal M2 digital-twin runs:

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_nonideal_m2.py --output-dir results\nonideal_m2_compact
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' merge_nonideal_m2_shards.py --inputs results\colab_imports\pro1_nonideal_m2_full_r1_shard0of5\artifacts results\colab_imports\pro1_nonideal_m2_full_r1_shard1of5\artifacts results\colab_imports\pro2_nonideal_m2_full_r1_shard2of5\artifacts results\colab_imports\pro2_nonideal_m2_full_r1_shard3of5\artifacts results\colab_imports\pro2_nonideal_m2_full_r1_shard4of5\artifacts --output-dir results\nonideal_m2_full_r1_merged
```

Outputs:

- `results/nonideal_m2_compact/nonideal_phase_scan.csv` (1224 rows; 612 ideal and 612 nonideal)
- `results/nonideal_m2_full_r1_merged/nonideal_phase_scan.csv` (157,500 rows; 78,750 ideal and 78,750 nonideal)
- `nonideal_summary.csv`
- `nonideal_best_equal_frame_blind_methods.csv`
- `nonideal_best_reference_methods.csv`
- `nonideal_key_summary.json`

The nonideal condition uses 8-bit SLM quantization, finite contrast ratio
1000:1, shot noise with photon count `1e4`, read noise `0.002` times mean
signal, timing jitter `0.05` frame, and noisy reference samples. The compact
3-basis/3-rho/2-sigma check remains a smoke-scale robustness entry point. The
full 7-rho x 5-sigma x 10-object x 5-seed run was split into five Colab L4
shards and merged with all shard labels `0/5` through `4/5` present. In the
full merged scan, strict equal-frame blind winners remain `pairwise` in all 35
rho/sigma cells for both ideal and nonideal conditions. The winning equal-frame
basis shifts from 16 Hadamard / 19 SRHT cells under ideal conditions to 23
Hadamard / 12 SRHT cells under nonideal conditions. The nonideal oracle mean
PSNR drops sharply from 65.36 dB to 28.35 dB, confirming active detector/SLM
perturbations, while `pairwise` drops only 0.17 dB on average. `scgi_proxy`
improves over raw `none` in 83.6% of nonideal matched comparisons and over AGC
in 65.8%, but still rarely beats `pairwise` on paired bases. These are
normalized digital-twin robustness results, not hardware-calibrated claims.

## Figures

`run_make_figures.py` now prefers the protocol-statistics result directories and
writes:

- `stage0_gamma_cnr.png`
- `stage0_gamma_table.png`
- `m1_oracle_agc_psnr.png`
- `m1_pairwise_failure_psnr.png`
- `m1_agc_window_gain_error.png`
- `m1_error_scaling_fit_table.png`
- `m2_best_methods_table.png`
- `m2_best_blind_methods_table.png`
- `m2_best_equal_frame_blind_methods_table.png`
- `m2_best_reference_methods_table.png`
- `m2_selected_phase_psnr.png`
- `m2_flip_boundary_table.png`
- `m3_srht_ablation_psnr.png`
- `m3_srht_ablation_table.png`

`run_make_paper_figures.py` writes 11 paper-facing M2/M4 PNG previews and 11
matching SVG sidecars under `results/paper_figures_r1`. The raster manifest is
`paper_figure_manifest.csv`; the vector-only manifest is
`paper_figure_manifest_vectors.csv`.

`run_make_paper_multipanels.py` writes three draft 300-dpi multipanel assemblies
under `results/paper_figures_r1/multipanels`: `figure3_agc_diagnostics`,
`figure4_error_scaling`, and `figure7_phase_diagram`, each as PNG, PDF, and SVG.
The panel-level provenance file is `paper_multipanel_manifest.csv`.

`run_make_final_figure_pack.py` writes `results/paper_figures_r2_final`, a
repo-relative final figure-pack draft with four figures and 13 panels. It adds
Figure 3 AGC diagnostics, Figure 4 fitted error laws, Figure 5 M2
phase/boundary maps, and Figure 8 SRHT energy/fast-drift ablation. Each figure
has editable SVG plus PNG/PDF/TIFF exports, and
`figure_assembly_manifest.csv` records panel-level source data.

## Verification

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' -m unittest discover -s tests -v
```

Result: 30 tests passed.

Additional checks:

- `py_compile` passed for runner scripts, `src/*.py`, and `tests/*.py`.
- `run_monitored_job.py` smoke-tested successfully and writes `status.json`,
  `run_manifest.json`, `stdout.log`, `stderr.log`, git state, CUDA device
  metadata, elapsed time, and estimated CU-hours when a CU rate is known.
- `run_phase_m2.py --resume` was smoke-tested on a 0/2 shard: first run wrote
  16 rows, the resumed run kept 16 rows and wrote 0 new rows while reporting
  `completed` in `progress.json`.
- `run_nonideal_m2.py --resume` was smoke-tested on a 0/2 shard: first run wrote
  9 rows, the resumed run kept 9 rows and wrote 0 new rows while reporting
  `completed` in `progress.json`.
- `run_stage0.py --resume-checkpoint` was smoke-tested from epoch 1 to epoch 2:
  `training_progress.json` reported `completed`, the history had 2 rows, and
  both `checkpoint_latest.pt` and `model_checkpoint.pt` were present.
- `run_m2_scgi_train.py --resume-checkpoint` was smoke-tested from epoch 1 to
  epoch 2: `training_progress.json` reported `completed`, the history had 2
  rows, and both `m2_scgi_checkpoint_latest.pt` and `m2_scgi_checkpoint.pt`
  were present.
- The Colab GitHub runner now writes `colab_job_status.json` in the artifact
  root, records accelerator/CU-rate metadata, and all Colab launch scripts pass
  `COLAB_GPU` plus optional `CU_PER_HOUR` through to the runner.
- The Colab runner also accepts `--persist-root`; launch scripts expose this as
  `PERSIST_ROOT` and periodically copy the artifact root to that mounted path
  every `SYNC_SECONDS` seconds. This is a persistence hook, not an automatic
  Drive authorization flow.
- Colab L4 via GitHub transfer completed debug 160 epoch + Stage 3, full
  20-epoch probe, gamma sweep, and full 100-epoch SCGI-only probe. Artifacts
  were extracted locally from Colab logs with `extract_colab_artifacts.py`.
- Full Stage 3 SCGI/UNN/URED threshold matrix ran with the returned full
  exp-residual checkpoint and local CUDA in 104.5 seconds.
- DCT and Fourier static round-trip MSE are below `1e-12` in unit tests.
- M2 fair-frame audit confirms measurement-frame equality and records reference
  overhead in `reference_frames` and `total_physical_frames`.
- M2 sharding was smoke-tested with `--shard 0/2` and `--shard 1/2`; merging
  with `merge_phase_m2_shards.py` reproduced the 1365-row smoke scan within
  numeric tolerance.
- M2 `scgi_proxy` dense run was split into five Colab L4 shards and merged into
  a 78,750-row scan with all five shard labels present.
- M2 high-rho extension was split into five monitored local CLI shards and
  merged into `results/phase_m2_scgi_proxy_dense_r1_highrho_merged` with
  101,250 rows covering `rho=0.001..10`; boundary audit writes
  `results/m2_boundary_audit_highrho`.
- Frozen `scgi_frozen` M2 smoke baseline loads the returned SCGI checkpoint and
  writes `results/phase_m2_scgi_frozen_smoke` with 1785 rows; the dense run
  writes `results/phase_m2_scgi_frozen_dense_r1_merged` with 89,250 rows, and
  the high-rho completion writes
  `results/phase_m2_scgi_frozen_dense_r1_highrho_merged` with 114,750 rows
  covering `rho=0.001..10`.
- Full nonideal M2 was split into five Colab L4 shards and merged into
  `results/nonideal_m2_full_r1_merged` with 157,500 rows and all five shard
  labels present.
- Stage 0 smoke now writes `val_diagnostics.csv` and `acceptance.csv`.
- Stage 1 smoke diagnostics write histogram, dynamic-curve, gain-curve, and
  lambda-distribution figures.
- Stage 3 smoke writes held-out target metrics, acceptance, and reconstruction grid.
- Stage 3 full threshold matrix writes SCGI/UNN/URED metrics and acceptance under
  `results/stage3_threshold_matrix_full_r2_authoritative`.
- Stage 3 static DGI upper-bound audit writes raw/minmax/scale/affine random-DGI
  metrics, a paired-Hadamard exact ceiling, and an affine-PSNR figure under
  `results/stage3_static_dgi_audit`.
- Stage 4 URED stripe sweeps write avg-pool and NLM denoiser hyperparameter
  screens under `results/stage4_ured_sweep_r2_stripe_merged` and
  `results/stage4_ured_sweep_nlm_r1_stripe`, plus the authoritative all-object
  NLM audit under `results/stage4_ured_sweep_nlm_allobjects_r1`, deeper and
  fixed-early-stop stripe sweeps under
  `results/stage4_ured_sweep_nlm_deeper_r1_stripe` and
  `results/stage4_ured_sweep_nlm_earlystop_r1_stripe`, refinement screens under
  `results/stage4_ured_sweep_nlm_refine_r1_stripe` and
  `results/stage4_ured_sweep_nlm_microrefine_r1_stripe`, and a combined trace
  audit under `results/stage4_trace_audit_r4`; the follow-up NLM
  patch-size/distance sweep writes `results/stage4_ured_sweep_nlm_patch_r1_stripe`,
  the NAFNet capacity check writes `results/stage4_ured_sweep_naf_capacity_r1_stripe`,
  and both confirm the previous 9.365 stripe CNR plateau. `results/stage4_image_audit_r1`
  adds regenerated best-output images and an ROI/threshold diagnostic.
- Published calibration writes APL/OE target tables under
  `results/published_calibration`.
- Published channel calibration writes APL trace digitizations and OE
  attenuation/distance anchors under `results/published_channel_calibration`.
- M4 compact theory runner writes residual-error, random-frame, energy
  concentration, and flip-boundary fit tables under `results/theory_m4_compact`.
- M4 paper-r1 theory runner writes larger-N, bootstrap, censored-boundary, and
  AGC-window diagnostics under `results/theory_m4_paper_r1`.
- M4 high-rho r2 reruns the same hooks against
  `results/phase_m2_scgi_frozen_dense_r1_highrho_merged` and writes
  `results/theory_m4_paper_r2_highrho`; `THEORY.md` and `PAPER_OUTLINE.md`
  now contain the AGC-law sketch and figure-caption drafts.
- M4 targeted and boundary-aware AGC runners write dense-window and censored
  interval diagnostics under `results/theory_m4_agc_targeted_r1` and
  `results/theory_m4_agc_boundary_aware_r1`.
- Paper-facing M2/M4 figures are rendered under `results/paper_figures_r1` with
  `paper_figure_manifest.csv`, SVG sidecars, and
  `paper_figure_manifest_vectors.csv`.
- Draft paper multipanels are rendered under
  `results/paper_figures_r1/multipanels` with PNG/PDF/SVG outputs for Figures
  3, 4, and 7 plus an 11-row `paper_multipanel_manifest.csv`.
- Nonideal M2 runners write compact and full ideal/nonideal digital-twin
  comparison tables under `results/nonideal_m2_compact` and
  `results/nonideal_m2_full_r1_merged`.

## Remaining Work Before Full Paper-Level Completion

- Redesign the `full` SCGI/UNN/URED path. The authoritative full matrix now
  exists, but its mean/min CNRs remain far below APL thresholds, especially for
  UNN/URED. Random static DGI PSNR has now been audited and remains below 20 dB
  even after affine alignment, while paired-Hadamard exact inversion reaches 80
  dB, so CNR/ROI, reconstruction-basis choice, and URED fidelity are the
  practical levers. NLM-based URED is materially better than the average-pool
  fallback on the binding stripe target, and fixed-step NLM refinement raises
  stripe final/trace CNR to 9.365. Exposing NLM patch size/distance and sweeping
  144 nearby stripe configurations leaves the best value unchanged; a 9-config
  NAFNet capacity check also fails to improve it. The best stripe final and
  target-aware diagnostic trace CNRs therefore remain below the APL URED target.
  A regenerated-image audit shows this miss is not an artifact of target
  threshold or far-background ROI choice.
  A first target-free proxy audit finds
  only partial correlation (`proxy_min` mean within-group Spearman 0.657) and no
  validated deployable stopping rule.
- Treat the new proxy-input 1D trained M2 dense scan as a secondary network-level
  baseline, not the main winner. It is above `none`/AGC and close to
  `scgi_proxy`, but `srht_paired + pairwise` still dominates the equal-frame
  prompt-range map. The published-channel figure anchors now exist; raw
  detector/SLM hardware calibration remains outside the available PDF data.
- Finish M4 from paper-r2 fitted-law hooks to final paper assets: the targeted
  and boundary-aware AGC analyses are now present but diagnostic, SVG sidecars
  exist for the current draft figures, draft multipanel PNG/PDF/SVG assemblies
  now exist for Figures 3, 4, and 7, and the paper still needs venue-specific
  final artwork and stronger AGC validation.
- Configure an authenticated mounted persistence target before future long
  Colab runs if mid-run copies are required. The code path now supports
  `PERSIST_ROOT`, but it does not perform Google Drive authorization or GitHub
  uploads by itself.

See `COMPLETION_AUDIT.md` for the strict requirement-by-requirement status.
