# SCGI Reproduction And Measurement-Basis Mechanism Study

This repository implements the two requested tasks:

1. A reproducible numerical framework for Peng and Chen, APL 124, 181104 (2024):
   supervised correction of dynamic scaling factors for ghost imaging (SCGI),
   DGI reconstruction, and SCGI-UNN/SCGI-URED style refinement.
2. A mechanism-study framework for why i.i.d. random measurement bases can support
   blind gain correction in time-varying multiplicative channels while deterministic
   orthogonal bases often fail.

The verified local CUDA runtime is `D:\Anacondar\anaconda3\envs\pytorch\python.exe`
with PyTorch CUDA 12.1 on an RTX 4060 Laptop GPU. The code also keeps internal
fallbacks for synthetic MNIST-like objects, KS testing, simple SSIM, and PIL-based
figures so the smoke tests remain portable.

## Quick Start

```powershell
cd E:\GAN_FCC_WORK\scgi-repro
$py = 'D:\Anacondar\anaconda3\envs\pytorch\python.exe'
& $py run_stage0.py --profile smoke
& $py run_stage1_diagnostics.py --profile smoke --samples 3
& $py run_stage3_tests.py --profile smoke
& $py run_stage3_tests.py --profile full --checkpoint results\colab_imports\pro2_full_exp_residual_e2_r1\artifacts\model_checkpoint.pt --model-kind exponential_residual_unet --include-unn-ured --ured-steps 500 --output-dir results\stage3_threshold_matrix_full_r2_authoritative
& $py run_published_calibration.py --output-dir results\published_calibration
& $py run_published_channel_calibration.py --output-dir results\published_channel_calibration
& $py run_gamma_sweep.py --profile smoke --epochs 2
& $py run_mechanism_m1.py --profile smoke --objects 1 --seeds 1 --reconstruction correlation --no-findings --output-dir results\mechanism_m1_basis_expanded_quick
& $py run_phase_m2.py --profile smoke --objects 1 --seeds 1 --no-findings --output-dir results\phase_m2_basis_expanded_quick
& $py run_phase_m2.py --profile smoke --objects 1 --seeds 1 --no-findings --scgi-checkpoint results\colab_imports\pro2_full_exp_residual_e2_r1\artifacts\model_checkpoint.pt --scgi-model-kind exponential_residual_unet --output-dir results\phase_m2_scgi_frozen_smoke
& $py run_m2_scgi_train.py --profile smoke --model-kind gain_unet --bases "random_uniform hadamard_paired srht_paired" --rho-values "0.001 0.1 1.0" --sigma-values "0.05 0.30" --objects 3 --seeds 2 --epochs 20 --output-dir results\m2_scgi_finetune_gain_smoke_r1
& $py run_phase_m2.py --profile smoke --objects 5 --seeds 3 --rho-values "0.003 0.3 3.0" --sigma-values "0.10 0.50" --reference-periods "2 8" --scgi-checkpoint-map results\m2_scgi_basis_specific_smoke_r1\checkpoint_map.json --output-dir results\phase_m2_scgi_basis_specific_heldout_smoke_r1 --no-findings
& $py run_m2_scgi_train.py --profile smoke --model-kind gain_predictor_unet --target-mode gain --input-normalize row_max --target-normalize none --gain-min 0.05 --gain-max 2.5 --bases "random_uniform hadamard_paired srht_paired" --rho-values "0.001 0.1 1.0" --sigma-values "0.05 0.30" --objects 3 --seeds 2 --epochs 30 --output-dir results\m2_scgi_gain_predictor_rawgain_smoke_r1
& $py run_srht_m3.py --profile smoke --objects 1 --seeds 1 --no-findings --output-dir results\srht_m3_quick
& $py run_nonideal_m2.py --output-dir results\nonideal_m2_compact
& $py merge_nonideal_m2_shards.py --inputs results\colab_imports\pro1_nonideal_m2_full_r1_shard0of5\artifacts results\colab_imports\pro1_nonideal_m2_full_r1_shard1of5\artifacts results\colab_imports\pro2_nonideal_m2_full_r1_shard2of5\artifacts results\colab_imports\pro2_nonideal_m2_full_r1_shard3of5\artifacts results\colab_imports\pro2_nonideal_m2_full_r1_shard4of5\artifacts --output-dir results\nonideal_m2_full_r1_merged
& $py run_m4_agc_targeted.py --output-dir results\theory_m4_agc_targeted_r1
& $py run_m4_agc_boundary_aware.py --output-dir results\theory_m4_agc_boundary_aware_r1
& $py run_make_figures.py --output-dir results\figures
& $py run_make_paper_figures.py --output-dir results\paper_figures_r1
& $py -m unittest discover tests -v
```

M2 scans can be split across Colab or local workers:

```powershell
& $py run_phase_m2.py --profile smoke --objects 1 --seeds 1 --shard 0/2 --resume --no-findings --output-dir results\phase_m2_shard_0of2
& $py run_phase_m2.py --profile smoke --objects 1 --seeds 1 --shard 1/2 --resume --no-findings --output-dir results\phase_m2_shard_1of2
& $py merge_phase_m2_shards.py --inputs results\phase_m2_shard_0of2 results\phase_m2_shard_1of2 --output-dir results\phase_m2_shard_merged
```

## Durable Long Runs

Use `run_monitored_job.py` as the local or Colab entry wrapper for long CLI jobs.
It writes `status.json`, `run_manifest.json`, `stdout.log`, `stderr.log`, git
state, CUDA device metadata, elapsed time, and optional estimated Colab compute
units. Known prompt rates are built in for T4 and A100; pass `--cu-per-hour` or
`CU_PER_HOUR` for L4 or future Colab rates.

```powershell
& $py run_monitored_job.py --run-id m2_shard0 --accelerator t4 --resume-skip-success -- `
  $py run_phase_m2.py --profile smoke --objects 1 --seeds 1 --shard 0/2 --resume --no-findings --output-dir results\phase_m2_shard_0of2
```

`run_phase_m2.py` and `run_nonideal_m2.py` now append completed `unit_index`
blocks to their main CSVs and update `progress.json`; rerunning with `--resume`
skips completed units and recomputes all summary tables at the end. The Colab
GitHub runner also emits `colab_job_status.json` inside the artifact root, and
the launch scripts pass `COLAB_GPU`/`CU_PER_HOUR` through to that status record.
For training jobs, `run_stage0.py` writes `checkpoint_latest.pt` and
`training_progress.json`, while `run_m2_scgi_train.py` writes
`m2_scgi_checkpoint_latest.pt`; both support `--resume-checkpoint`.
If a mounted persistence location is available, set `PERSIST_ROOT` in the Colab
launch scripts to copy the artifact root there every `SYNC_SECONDS` seconds.
This does not perform Drive authorization; it uses an already-mounted directory.

For a closer-to-prompt debug run, use `--profile debug`. For the paper-scale run, use
`--profile full` on a GPU machine with torchvision/scipy/skimage/matplotlib installed.
The verified local CUDA environment is `D:\Anacondar\anaconda3\envs\pytorch\python.exe`.
If the unconstrained gain U-Net underfits at full scale, run the
physics-informed candidate with `--model-kind exponential_residual_unet`.

## Main Outputs

- `REPORT.md`: SCGI reproduction status, Colab runs, and mechanism-study summary.
- `COMPLETION_AUDIT.md`: strict prompt-requirement audit with done/partial/open status.
- `ASSUMPTIONS.md`: every implementation assumption for undisclosed paper details.
- `PROTOCOL.md`: fair-comparison rules for basis/channel studies.
- `THEORY.md`: derivations and theory hooks for H1-H4 and SRHT.
- `FINDINGS.md`: mechanism-study results in experiment-prediction-result format.
- `PAPER_OUTLINE.md`: theory/numerics paper outline and target venues.
- `results/stage_0/`: SCGI smoke run figures and metrics.
- `results/stage_1/smoke/`: Stage 1 B histogram, dynamic curve, gain curve, and
  lambda distribution diagnostics.
- `results/stage_3/smoke/`: held-out target reconstructions and Stage 3
  acceptance checks using the saved Stage 0 checkpoint.
- `results/colab_imports/pro2_full_exp_residual_e2_r1/`: full-profile
  physics-informed SCGI candidate with returned checkpoint and artifacts.
- `results/stage_3_exp_residual_colab_full/`: held-out full-profile Stage 3
  validation using that checkpoint.
- `results/stage3_threshold_matrix_full_r2_authoritative/`: full-profile
  SCGI/UNN/URED threshold matrix for four held-out targets using the returned
  exp-residual checkpoint.
- `results/stage3_static_dgi_audit/`: full-profile static DGI upper-bound audit
  for handcrafted and MNIST held-out targets, including raw/minmax and
  affine-aligned random-DGI PSNR checks plus a paired-Hadamard exact sanity
  ceiling.
- `results/stage4_ured_sweep_r2_stripe_merged/` and
  `results/stage4_ured_sweep_nlm_r1_stripe/`: stripe-target Stage 4 URED
  denoiser/hyperparameter screens.
- `results/stage4_ured_sweep_nlm_allobjects_r1/`: repaired all-object NLM URED
  candidate audit preserving per-object dynamic factors.
- `results/stage4_ured_proxy_audit_r1/`: target-free URED trace-proxy audit.
  Its target-aware trace peaks are diagnostic only, and no tested proxy is a
  deployable stopping rule.
- `results/published_calibration/`: machine-readable APL Fig. 6/Fig. 9 CNR
  targets, OE PSNR/SSIM targets, and current gap summary.
- `results/published_channel_calibration/`: figure-level APL intensity-trace
  digitization and OE channel-anchor fits. These are published-figure priors,
  not raw detector or hardware calibration logs. The numeric tables are safe to
  relay; rendered PDF pages and overlay QA PNGs stay local-only.
- `results/mechanism_m1_basis_expanded_quick/`: compact M1 output with random,
  Hadamard, DCT, Fourier, and SRHT bases.
- `results/phase_m2_basis_expanded_quick/`: compact fair-frame M2 output with
  frame-count audit columns.
- `results/phase_m2_reference_protocol_o10s5/`: 68,250-row dense 7x5 M2
  protocol output with `reference_k2/k8/k32` calibration, equal-frame blind
  summaries, and flip-boundary diagnostics.
- `results/phase_m2_scgi_proxy_dense_r1_merged/`: 78,750-row dense 7x5 M2
  output that adds `scgi_proxy` as an equal-frame blind smooth-gain proxy with
  zero reference frames.
- `results/phase_m2_scgi_proxy_dense_r1_highrho_merged/`: 101,250-row dense
  9x5 M2 output extending the prompt rho range to `0.001..10`.
- `results/m2_boundary_audit_highrho/`: rho-coverage audit, log-rho
  interpolated flip-boundary fits, and winner-map summaries for the high-rho M2
  merge.
- `results/phase_m2_scgi_frozen_dense_r1_highrho_merged/`: 114,750-row dense
  9x5 M2 output with frozen SCGI-network correction over the full prompt rho
  range.
- `results/m2_boundary_audit_frozen_highrho/`: matching frozen-network
  prompt-range coverage and winner-map audit.
- `results/phase_m2_scgi_frozen_smoke/`: frozen-network M2 smoke baseline using
  the returned SCGI checkpoint and explicit `scgi_frozen` correction.
- `results/phase_m2_scgi_frozen_dense_r1_merged/`: 89,250-row dense M2 run with
  explicit `scgi_frozen` correction and all five Colab shard labels present.
- `results/m2_scgi_finetune_smoke_r1/` and
  `results/m2_scgi_finetune_gain_smoke_r1/`: direct-output and single-checkpoint
  supervised M2 SCGI smoke training runs.
- `results/m2_scgi_basis_specific_smoke_r1/`: basis-routed `gain_unet`
  checkpoints plus `checkpoint_map.json` for random, Hadamard, and SRHT bases.
- `results/phase_m2_scgi_finetune_smoke_r1/` and
  `results/phase_m2_scgi_finetune_gain_smoke_r1/`: evaluations of the
  direct-output and single-checkpoint M2 SCGI fine-tuning smokes.
- `results/phase_m2_scgi_basis_specific_smoke_r1/` and
  `results/phase_m2_scgi_basis_specific_heldout_smoke_r1/`: in-distribution and
  held-out evaluations of the basis-specific fine-tuned SCGI smoke.
- `results/m2_scgi_gain_predictor_smoke_r1/` and
  `results/m2_scgi_gain_predictor_rawgain_smoke_r1/`: true-gain target SCGI
  smokes using the signed-safe gain-predictor interface.
- `results/phase_m2_scgi_gain_predictor_heldout_smoke_r1/` and
  `results/phase_m2_scgi_gain_predictor_rawgain_heldout_smoke_r1/`: held-out
  checks showing the gain-predictor route remains a negative baseline.
- `results/theory_m4_compact/`: compact M4 fitted-law outputs for residual gain
  scaling, random frame scaling, coefficient energy concentration, and observed
  flip-boundary fits.
- `results/theory_m4_paper_r1/`: larger-N M4 fitted-law outputs with bootstrap
  intervals, censored flip-boundary accounting, and AGC window diagnostics.
- `results/theory_m4_paper_r2_highrho/`: same M4 fitted-law hooks rerun against
  the prompt-range frozen high-rho M2 phase table; used by the current
  `THEORY.md` and `PAPER_OUTLINE.md` caption drafts.
- `results/theory_m4_agc_targeted_r1/`: targeted AGC window-law validation with
  dense window grid, saturation diagnostics, and fit tables.
- `results/theory_m4_agc_boundary_aware_r1/`: censored AGC window-selection
  analysis with four basis fits and 180 interval-satisfaction rows.
- `results/paper_figures_r1/`: paper-facing M2/M4 winner maps, boundary-fit
  tables, fitted-law plots, captions, and `paper_figure_manifest.csv`.
- `results/nonideal_m2_compact/`: compact ideal/nonideal M2 digital-twin scan
  with SLM quantization, finite contrast, detector noise, timing jitter, and
  noisy reference samples.
- `results/nonideal_m2_full_r1_merged/`: 157,500-row full ideal/nonideal M2
  digital-twin scan over the dense 7x5 grid, merged from five Colab L4 shards.
- `results/mechanism_m1_protocol_o10s5/`,
  `results/phase_m2_reference_protocol_o10s5/`, and
  `results/srht_m3_protocol_o10s5/`: 10-object x 5-seed mechanism outputs used
  by the latest figure rendering.
- `results/srht_m3_quick/`: compact SRHT ablation plumbing output.
- `results/figures/`: compact M1-M3 rendered figure outputs.

## Tests

Run the unittest suite with the CUDA conda runtime rather than the system `python`
on this machine:

```powershell
cd E:\GAN_FCC_WORK\scgi-repro
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' -m unittest discover -s tests -v
```
