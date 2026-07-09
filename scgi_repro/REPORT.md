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
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_stage0.py --profile smoke
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
| train loss / validation MSE | 1.4426 / 0.01579 |
| dynamic slope / corrected slope | -0.6039 / 0.0769 |
| true lambda / analytic lambda | 0.998828 / 0.998824 |
| dynamic MSE vs static | 0.1470 |
| SCGI MSE vs static | 0.00662 |
| analytic/oracle MSE vs static | 2.87e-6 / 1.58e-15 |
| dynamic DGI CNR | 0.4886 |
| SCGI DGI CNR | 1.9537 |
| SCGI-UNN CNR | 1.9579 |
| SCGI-URED CNR | 3.3891 |
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
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_stage1_diagnostics.py --profile smoke --samples 3
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
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_stage3_tests.py --profile smoke
```

Outputs:

- `results/stage_3/smoke/stage3_metrics.csv`
- `results/stage_3/smoke/stage3_acceptance.csv`
- `results/stage_3/smoke/stage3_recon_grid.png`

The saved smoke checkpoint improves every held-out target over raw dynamic DGI
(`scgi_cnr_above_dynamic_all=True`), but still fails the prompt-level
`SCGI CNR >= 3` and `static PSNR > 20 dB` gates. The Colab 160-epoch checkpoint
also improves every held-out target over dynamic DGI. Its SCGI CNRs are 8.54
for `letter_A`, 2.18 for `stripe_target`, 2.77 for `letter_L`, and 2.63 for
`ring`, so it passes the directionality gate but still misses the all-target
CNR >= 3 requirement.

The full-profile exp-residual checkpoint was also tested on held-out targets in
`results/stage_3_exp_residual_colab_full/full`. SCGI matches analytic/static CNRs
for all four targets: `letter_A` 3.3095, `letter_L` 3.5481, `ring` 2.9819, and
`stripe_target` 2.4919. Thus directionality and KS behavior pass, while the
all-target CNR>=3 and static PSNR>20 gates still fail because the static DGI
upper bounds for `ring`, `stripe_target`, and PSNR are below those thresholds.

## Task 2: Measurement-Basis Mechanism Study

The mechanism framework now includes random uniform/binary/gaussian bases,
Hadamard paired measurements, full-contrast DCT paired measurements, four-step
Fourier measurements, and SRHT paired measurements. M1/M2 runners use equal
physical frame budgets; in the current smoke mechanism profile all M2 bases use
2048 SLM frames. Fourier therefore uses 512 four-step coefficients for a
1024-pixel object in fair-frame scans.

Latest M1 protocol-statistics run:

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_mechanism_m1.py --profile debug --objects 10 --seeds 5 --reconstruction correlation --no-findings --output-dir results\mechanism_m1_protocol_o10s5
```

Outputs:

- `mechanism_m1_oracle_agc.csv` (4200 rows)
- `mechanism_m1_agc_window_sweep.csv` (1750 rows)
- `mechanism_m1_error_propagation.csv` (1750 rows)
- `mechanism_m1_error_scaling_fit.csv` (7 rows)
- `mechanism_m1_pairwise_failure.csv` (5400 rows)
- `mechanism_m1_summary.csv` (262 rows)

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

An additional M2 smoke validation at `results/phase_m2_scgi_proxy_smoke`
confirms the new `scgi_proxy` correction is present in the scan output. It is a
blind smooth-gain SCGI-style proxy with zero reference frames, not a trained
SCGI network. The smoke CSV has 1575 rows overall and 210 `scgi_proxy` rows.

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
fair blind winner. Flip-boundary diagnostics are emitted with boundary statuses:
104 `not_reached`, 17 `left_censored`, and 14 `observed`.

Latest M3 protocol-statistics run:

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_srht_m3.py --profile debug --objects 10 --seeds 5 --no-findings --output-dir results\srht_m3_protocol_o10s5
```

Outputs:

- `srht_ablation.csv` (3200 rows)
- `srht_ablation_summary.csv` (64 rows)

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

## Verification

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' -m unittest discover -s tests -v
```

Result: 14 tests passed.

Additional checks:

- `py_compile` passed for runner scripts, `src/*.py`, and `tests/*.py`.
- Colab L4 via GitHub transfer completed debug 160 epoch + Stage 3, full
  20-epoch probe, gamma sweep, and full 100-epoch SCGI-only probe. Artifacts
  were extracted locally from Colab logs with `extract_colab_artifacts.py`.
- DCT and Fourier static round-trip MSE are below `1e-12` in unit tests.
- M2 fair-frame audit confirms measurement-frame equality and records reference
  overhead in `reference_frames` and `total_physical_frames`.
- M2 sharding was smoke-tested with `--shard 0/2` and `--shard 1/2`; merging
  with `merge_phase_m2_shards.py` reproduced the 1365-row smoke scan within
  numeric tolerance.
- Stage 0 smoke now writes `val_diagnostics.csv` and `acceptance.csv`.
- Stage 1 smoke diagnostics write histogram, dynamic-curve, gain-curve, and
  lambda-distribution figures.
- Stage 3 smoke writes held-out target metrics, acceptance, and reconstruction grid.

## Remaining Work Before Full Paper-Level Completion

- Redesign the `full` SCGI training profile. Colab has now run both 20 and
  100 epochs at 128x128/N=16384; both remain far below the SCGI thresholds.
- Add SCGI-network correction inside M2 and published-channel/non-ideal detector
  calibration.
- Fit and report M2 flip-boundary laws with R2, then update `THEORY.md` with
  quantitative curves rather than smoke-level diagnostics.

See `COMPLETION_AUDIT.md` for the strict requirement-by-requirement status.
