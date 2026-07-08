# SCGI Reproduction Report

Updated: 2026-07-09

## Runtime

Verified local runtime:

```text
D:\Anacondar\anaconda3\envs\pytorch\python.exe
torch 2.1.0+cu121, CUDA 12.1
NVIDIA GeForce RTX 4060 Laptop GPU
```

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
`SCGI CNR >= 3` and `static PSNR > 20 dB` gates.

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

Latest M2 reference smoke run:

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile smoke --objects 1 --seeds 1 --no-findings --output-dir results\phase_m2_reference_smoke
```

Outputs:

- `phase_scan.csv` (1365 rows, with frame-count audit columns)
- `phase_summary.csv`
- `phase_blind_summary.csv`
- `best_methods.csv`
- `best_blind_methods.csv`
- `best_equal_frame_blind_methods.csv`
- `best_reference_methods.csv`
- `flip_boundary.csv`

Frame audit for M2 reference smoke:

| Correction | Measurement frames | Reference frames | Total physical frames |
|---|---:|---:|---:|
| non-reference | 2048 | 0 | 2048 |
| reference_k32 | 2048 | 65 | 2113 |
| reference_k8 | 2048 | 257 | 2305 |
| reference_k2 | 2048 | 1025 | 3073 |

This run now separates any-budget blind winners from strict equal-total-frame
blind winners. In the smoke grid, `reference_k2` wins the any-budget table but
uses 3073 physical frames; `srht_paired + pairwise` wins most strict 2048-frame
cells. A 10-object x 5-seed reference run is in progress at
`results/phase_m2_reference_protocol_o10s5`.

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
- DCT and Fourier static round-trip MSE are below `1e-12` in unit tests.
- M2 fair-frame audit confirms measurement-frame equality and records reference
  overhead in `reference_frames` and `total_physical_frames`.
- Stage 0 smoke now writes `val_diagnostics.csv` and `acceptance.csv`.
- Stage 1 smoke diagnostics write histogram, dynamic-curve, gain-curve, and
  lambda-distribution figures.
- Stage 3 smoke writes held-out target metrics, acceptance, and reconstruction grid.

## Remaining Work Before Full Paper-Level Completion

- Run the `full` SCGI profile at 128x128, N=16384, M=5000, 100 epochs.
- Extend M2 reference scans from smoke to completed 10 objects x 5 seeds if the
  running job has not finished, then refresh figures from that directory.
- Add SCGI-network correction inside M2 and published-channel/non-ideal detector
  calibration.
- Fit and report M2 flip-boundary laws with R2, then update `THEORY.md` with
  quantitative curves rather than smoke-level diagnostics.
