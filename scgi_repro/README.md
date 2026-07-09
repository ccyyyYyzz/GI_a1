# SCGI Reproduction And Measurement-Basis Mechanism Study

This repository implements the two requested tasks:

1. A reproducible numerical framework for Peng and Chen, APL 124, 181104 (2024):
   supervised correction of dynamic scaling factors for ghost imaging (SCGI),
   DGI reconstruction, and SCGI-UNN/SCGI-URED style refinement.
2. A mechanism-study framework for blind gain identifiability in time-varying
   multiplicative channels. Random speckles and randomized orthogonal bases
   supply statistical anchors; ordered deterministic bases can lose that anchor
   under blind correction even though they remain information-preserving under
   oracle calibration.

The verified local CUDA runtime is `D:\Anacondar\anaconda3\envs\pytorch\python.exe`
with PyTorch CUDA 12.1 on an RTX 4060 Laptop GPU. The code also keeps internal
fallbacks for synthetic MNIST-like objects, KS testing, simple SSIM, and PIL-based
figures so the smoke tests remain portable.

## Quick Start

```powershell
cd E:\GAN_FCC_WORK\scgi-repro
$py = 'D:\Anacondar\anaconda3\envs\pytorch\python.exe'
& $py run_monitored_job.py --run-id stage0_smoke_refresh_r1 --output-dir results\cli_runs\stage0_smoke_refresh_r1 --heartbeat-seconds 30 --accelerator local_cuda -- $py run_stage0.py --profile smoke --epochs 2 --tag smoke --model-kind exponential_residual_unet
& $py run_monitored_job.py --run-id stage1_smoke_refresh_r1 --output-dir results\cli_runs\stage1_smoke_refresh_r1 --heartbeat-seconds 30 --accelerator local_cuda -- $py run_stage1_diagnostics.py --profile smoke --samples 3 --output-dir results\stage_1
& $py run_monitored_job.py --run-id stage3_smoke_refresh_r1 --output-dir results\cli_runs\stage3_smoke_refresh_r1 --heartbeat-seconds 30 --accelerator local_cuda -- $py run_stage3_tests.py --profile smoke --checkpoint results\stage_0\smoke\model_checkpoint.pt --model-kind exponential_residual_unet --output-dir results\stage_3
& $py run_stage3_tests.py --profile full --checkpoint results\colab_imports\pro2_full_exp_residual_e2_r1\artifacts\model_checkpoint.pt --model-kind exponential_residual_unet --include-unn-ured --ured-steps 500 --output-dir results\stage3_threshold_matrix_full_r2_authoritative
& $py run_published_calibration.py --output-dir results\published_calibration
& $py run_published_channel_calibration.py --output-dir results\published_channel_calibration
& $py run_gamma_sweep.py --profile smoke --epochs 2
& $py run_mechanism_m1.py --profile smoke --objects 1 --seeds 1 --reconstruction correlation --no-findings --output-dir results\mechanism_m1_basis_expanded_quick
& $py run_monitored_job.py --run-id mechanism_m1_protocol_o10s5_rerun --output-dir results\cli_runs\mechanism_m1_protocol_o10s5_rerun --heartbeat-seconds 30 --accelerator local_cpu -- $py run_mechanism_m1.py --profile debug --objects 10 --seeds 5 --output-dir results\mechanism_m1_protocol_o10s5 --no-findings
& $py run_m1_mechanism_audit.py --input-dir results\mechanism_m1_protocol_o10s5
& $py run_phase_m2.py --profile smoke --objects 1 --seeds 1 --no-findings --output-dir results\phase_m2_basis_expanded_quick
& $py run_phase_m2.py --profile smoke --objects 1 --seeds 1 --no-findings --scgi-checkpoint results\colab_imports\pro2_full_exp_residual_e2_r1\artifacts\model_checkpoint.pt --scgi-model-kind exponential_residual_unet --output-dir results\phase_m2_scgi_frozen_smoke
& $py run_m2_scgi_train.py --profile smoke --model-kind gain_unet --bases "random_uniform hadamard_paired srht_paired" --rho-values "0.001 0.1 1.0" --sigma-values "0.05 0.30" --objects 3 --seeds 2 --epochs 20 --output-dir results\m2_scgi_finetune_gain_smoke_r1
& $py run_phase_m2.py --profile smoke --objects 5 --seeds 3 --rho-values "0.003 0.3 3.0" --sigma-values "0.10 0.50" --reference-periods "2 8" --scgi-checkpoint-map results\m2_scgi_basis_specific_smoke_r1\checkpoint_map.json --output-dir results\phase_m2_scgi_basis_specific_heldout_smoke_r1 --no-findings
& $py run_m2_scgi_train.py --profile smoke --model-kind gain_predictor_unet --target-mode gain --input-normalize row_max --target-normalize none --gain-min 0.05 --gain-max 2.5 --bases "random_uniform hadamard_paired srht_paired" --rho-values "0.001 0.1 1.0" --sigma-values "0.05 0.30" --objects 3 --seeds 2 --epochs 30 --output-dir results\m2_scgi_gain_predictor_rawgain_smoke_r1
& $py run_m2_scgi_train.py --profile smoke --model-kind gain_predictor_1d --target-mode gain --input-mode scgi_proxy_gain --input-normalize none --target-normalize none --gain-min 0.05 --gain-max 2.5 --bases "random_uniform random_binary hadamard_paired dct_paired fourier_fourstep srht_paired" --rho-values "0.001 0.1 1.0" --sigma-values "0.05 0.30" --objects 3 --seeds 2 --epochs 30 --batch-size 16 --output-dir results\m2_scgi_proxyinput_gain1d_smoke_r1
& $py run_phase_m2.py --profile smoke --objects 5 --seeds 3 --rho-values "0.003 0.3 3.0" --sigma-values "0.10 0.50" --reference-periods "2 8" --scgi-checkpoint results\m2_scgi_proxyinput_gain1d_smoke_r1\m2_scgi_checkpoint.pt --output-dir results\phase_m2_scgi_proxyinput_gain1d_heldout_smoke_r1 --no-findings
& $py run_phase_m2.py --profile smoke --objects 10 --seeds 5 --rho-values "0.001,0.003,0.01,0.03,0.1,0.3,1.0,3.0,10.0" --sigma-values "0.05,0.10,0.15,0.30,0.50" --reference-periods "2,8,32" --shard i/5 --resume --scgi-checkpoint results\m2_scgi_proxyinput_gain1d_smoke_r1\m2_scgi_checkpoint.pt --output-dir results\phase_m2_scgi_proxyinput_gain1d_dense_r1_shardiof5 --no-findings
& $py merge_phase_m2_shards.py --inputs results\phase_m2_scgi_proxyinput_gain1d_dense_r1_shard0of5 results\phase_m2_scgi_proxyinput_gain1d_dense_r1_shard1of5 results\phase_m2_scgi_proxyinput_gain1d_dense_r1_shard2of5 results\phase_m2_scgi_proxyinput_gain1d_dense_r1_shard3of5 results\phase_m2_scgi_proxyinput_gain1d_dense_r1_shard4of5 --output-dir results\phase_m2_scgi_proxyinput_gain1d_dense_r1_merged
& $py run_srht_m3.py --profile smoke --objects 1 --seeds 1 --no-findings --output-dir results\srht_m3_quick
& $py run_monitored_job.py --run-id srht_m3_protocol_o10s5_highrho_r2 --output-dir results\cli_runs\srht_m3_protocol_o10s5_highrho_r2 --heartbeat-seconds 30 --accelerator local_cpu -- $py run_srht_m3.py --profile smoke --objects 10 --seeds 5 --rho-values "0.001,0.1,1.0,10.0" --sigma-a 0.30 --block-size 32 --output-dir results\srht_m3_protocol_o10s5_highrho_r2 --no-findings
& $py run_m3_srht_audit.py --input-dir results\srht_m3_protocol_o10s5_highrho_r2 --output-dir results\srht_m3_audit_highrho_r2
& $py run_monitored_job.py --run-id m3_random_comparator_fast_r1 --output-dir results\cli_runs\m3_random_comparator_fast_r1 --heartbeat-seconds 30 --accelerator local_cpu -- $py run_m3_random_comparator.py --objects 10 --seeds 5 --rho-values "1.0,10.0" --sigma-a-values "0.30,0.50" --output-dir results\m3_random_comparator_fast_r1
& $py run_nonideal_m2.py --output-dir results\nonideal_m2_compact
& $py merge_nonideal_m2_shards.py --inputs results\colab_imports\pro1_nonideal_m2_full_r1_shard0of5\artifacts results\colab_imports\pro1_nonideal_m2_full_r1_shard1of5\artifacts results\colab_imports\pro2_nonideal_m2_full_r1_shard2of5\artifacts results\colab_imports\pro2_nonideal_m2_full_r1_shard3of5\artifacts results\colab_imports\pro2_nonideal_m2_full_r1_shard4of5\artifacts --output-dir results\nonideal_m2_full_r1_merged
& $py run_m4_agc_targeted.py --output-dir results\theory_m4_agc_targeted_r1
& $py run_m4_agc_boundary_aware.py --output-dir results\theory_m4_agc_boundary_aware_r1
& $py run_make_figures.py --output-dir results\figures
& $py run_make_paper_figures.py --output-dir results\paper_figures_r1
& $py run_make_paper_multipanels.py --output-dir results\paper_figures_r1\multipanels
& $py run_stage4_postprocess_audit.py --arrays results\stage4_image_audit_r1\stage4_image_audit_arrays.npz --output-dir results\stage4_postprocess_audit_r1
& $py run_monitored_job.py --run-id stage4_postprocess_allobjects_r1 --output-dir results\cli_runs\stage4_postprocess_allobjects_r1 --heartbeat-seconds 30 --accelerator local_cuda -- $py run_stage4_postprocess_allobjects.py --output-dir results\stage4_postprocess_allobjects_r1
& $py run_monitored_job.py --run-id stage4_threshold_trace_audit_r1 --output-dir results\cli_runs\stage4_threshold_trace_audit_r1 --heartbeat-seconds 30 --accelerator local_cuda -- $py run_stage4_threshold_trace_audit.py --output-dir results\stage4_threshold_trace_audit_r1
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
For Colab CLI sessions that lose their websocket during `colab run`,
`colab/background_command_launcher.py` can attach to a kept session, start a
detached background job, and leave `/content/<run_id>.log`, status JSON, and a
zip archive for later `colab download`.
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
- `results/stage3_threshold_matrix_full_r2_authoritative/`: full-profile
  SCGI/UNN/URED threshold matrix for four held-out targets using the returned
  exp-residual checkpoint; this is the retained full-profile validation path.
- `results/stage3_static_dgi_audit/`: full-profile static DGI upper-bound audit
  for handcrafted and MNIST held-out targets, including raw/minmax and
  affine-aligned random-DGI PSNR checks plus a paired-Hadamard exact sanity
  ceiling.
- `results/stage3_static_dgi_sampling_r1/`: monitored full-profile static DGI
  sampling-factor audit over 0.25P, 0.5P, 1P, and 2P random patterns. It shows
  affine-aligned PSNR improving with more random patterns but still below 20 dB
  at 2P.
- `results/stage3_static_dgi_streaming_colab_r2/`: Colab L4 streaming random-DGI
  audit over 4P, 8P, 16P, 32P, and 64P patterns. At 64P, minmax mean PSNR
  reaches 21.355 dB, but the all-object minimum remains 16.607 dB; affine
  alignment clears 28.152 dB minimum, showing a strong scale/offset component.
- `results/stage3_static_dgi_streaming_highsample_r1/`: monitored local-CUDA
  continuation over 128P and 256P random patterns. At 256P, strict minmax PSNR
  clears 20 dB on all eight objects (minimum/mean 21.515/24.366 dB), while
  affine-aligned PSNR is much higher (minimum/mean 34.500/36.938 dB), confirming
  that the remaining static-DGI issue is calibration/sampling rather than lost
  image information.
- `results/stage4_ured_sweep_r2_stripe_merged/` and
  `results/stage4_ured_sweep_nlm_r1_stripe/`: stripe-target Stage 4 URED
  denoiser/hyperparameter screens.
- `results/stage4_ured_sweep_nlm_allobjects_r1/`: repaired all-object NLM URED
  candidate audit preserving per-object dynamic factors.
- `results/stage4_ured_sweep_nlm_deeper_r1_stripe/`,
  `results/stage4_ured_sweep_nlm_earlystop_r1_stripe/`,
  `results/stage4_ured_sweep_nlm_refine_r1_stripe/`, and
  `results/stage4_ured_sweep_nlm_microrefine_r1_stripe/`: monitored
  local-CUDA stripe follow-ups showing longer 400-step NLM does not help, while
  fixed-step NLM refinement raises stripe final/trace CNR to 9.365.
- `results/stage4_ured_sweep_nlm_patch_r1_stripe/`: monitored 144-config NLM
  patch-size/patch-distance stripe sweep. It does not improve beyond 9.365 CNR;
  the best row keeps the previous effective NLM patch defaults (`5`, `6`).
- `results/stage4_ured_sweep_naf_capacity_r1_stripe/`: monitored 9-config
  NAFNet capacity check over 24/32/48 channels and 3/4/5 blocks. Prompt-like
  32-channel/4-block capacity does not improve the stripe CNR plateau.
- `results/stage4_ured_seed_sweep_r1_stripe/`: monitored 24-seed initialization
  sweep at the best continuous stripe setting. The best stripe final/trace CNR
  remains 9.365, so the miss is not a single-seed accident.
- `results/stage4_ured_lr_micro_r1_stripe/`,
  `results/stage4_ured_lr_residual_micro_r1_stripe/`, and
  `results/stage4_ured_lr_residual_xi_micro_r1_stripe/`: monitored continuous
  URED micro-sweeps over LR, residual scale, and `xi/x_step`; best stripe
  final/target-aware trace CNR improves to 9.502/9.606 but remains below 10.43.
- `results/stage4_ured_prompt_capacity_micro_r1_stripe/`: monitored retest of
  prompt-like capacity near the new LR/residual-scale basin. Best stripe CNR is
  9.670, so capacity alone still does not clear the APL URED gate.
- `results/stage4_ured_binary_prior_pilot_r1_stripe/`: monitored continuous
  double-well pilot. It gives a small gain to 9.711 CNR, but remains below
  10.43.
- `results/stage4_ured_otsu_soft_pilot_r1_stripe/` and
  `results/stage4_ured_otsu_soft_fixedstep_r1_stripe/`: monitored target-free
  soft-Otsu RED pilots. The fixed-step continuous `x-u` stripe output reaches
  12.350 CNR at 15 steps with `nlm_otsu_soft`, clearing the APL URED minimum
  for stripe under this modified regularizer.
- `results/stage4_ured_otsu_soft_colab_allobjects_r1/`: Colab pro2/L4
  all-object fixed-step validation of the same modified soft-Otsu RED path at
  commit `0b6e86e`. All four continuous `x-u` outputs clear the 10.43 CNR gate
  with minimum CNR 12.341.
- `results/stage4_ured_otsu_soft_seed_robust_colab_r1/`: Colab L4 five-seed
  robustness check for the same modified soft-Otsu RED configuration. The
  all-object minimum CNR remains above the APL URED gate, with worst stripe
  final CNR 11.237 across 20 object/seed rows.
- `results/stage4_trace_audit_r6/`: combined final-vs-target-aware trace audit
  for 16 Stage 4 sweeps. It records 893 detail rows and adds the soft-Otsu RED
  evidence; all objects have target-aware trace points above 10.43.
- `results/stage4_trace_audit_nlm_only_r1/`: original NLM-only trace audit
  separated from the modified soft-Otsu path. Historical NLM-only sweeps still
  leave `stripe_target` below the APL URED minimum; best trace CNR is 9.670.
- `results/stage4_ured_nlm_matched_soft_control_r1/` and
  `results/stage4_trace_audit_nlm_matched_soft_control_r1/`: monitored matched
  NLM-only control at the soft-Otsu hyperparameter basin over five seeds. It
  writes 20 object-level metric rows and 300 trace rows; `stripe_target` reaches
  only 7.337 final / 7.677 trace CNR, so soft-Otsu's all-object pass is not
  explained by the shared 15-step low-residual setting alone.
- `results/stage4_image_audit_r1/`: regenerated best stripe Stage 4 images,
  raw arrays, metric table, threshold sweep, and ROI/bounding-box diagnostic.
  It shows the 9.365 CNR miss is not caused by target threshold or far-background
  mask choice.
- `results/stage4_postprocess_audit_r1/`: target-free post-processing audit for
  the best stripe URED output. Otsu thresholding the reconstruction histogram
  raises stripe CNR from 9.365 to 15.288 with IoU 0.987, showing the shape is
  present, but this changes the reporting protocol relative to continuous URED.
- `results/stage4_postprocess_allobjects_r1/`: monitored all-object extension of
  the post-processing audit. Best-trace target-free thresholded masks clear the
  APL URED CNR gate on all four held-out objects (minimum 15.288), while
  best-final target-free masks still miss for ring (9.332), so fully deployable
  continuous/final Stage 4 remains open.
- `results/stage4_threshold_trace_audit_r1/`: monitored thresholded-trace
  stopping audit. `minmax_otsu_binary + fixed_step_117` clears the APL URED CNR
  gate on all four audited objects with minimum CNR 15.211; fixed-step rules use
  the nearest available recorded step, so short traces fall back to their final
  recorded step.
- `results/stage4_ured_proxy_audit_r1/`: earlier target-free continuous-output
  URED trace-proxy audit. It did not validate a stopping rule for continuous CNR,
  motivating the thresholded-trace audit above.
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
- `results/phase_m2_scgi_proxy_dense_r1_highrho_merged/`: retained
  101,250-row dense 9x5 M2 output extending the prompt rho range to
  `0.001..10` and including `scgi_proxy`; it supersedes earlier 7x5 reference
  and `scgi_proxy` merged directories that are not present in this checkout.
- `results/m2_hadamard_order_smoke_r1/`: monitored M2 smoke including natural,
  sequency, cake-cutting-proxy, and random Hadamard row orders via
  `run_phase_m2.py --hadamard-orders`. It writes 1,836 scan rows and verifies
  the expanded basis list in the phase-map pipeline; `hadamard_random_paired`
  is selected in 5/6 equal-frame smoke cells, while 2/6 selected cells are
  sub-floor by the default `rel_mse<0.5` gate.
- `results/m2_hadamard_order_dense_r1_merged/`: Colab-sharded 155,250-row dense
  9x5 M2 output over 10 objects x 5 seeds with natural, sequency,
  cake-cutting-proxy, and random Hadamard row orders. The five imported L4
  shards each have 31,050 rows, 4,050 completed units, and shard labels `0/5`
  through `4/5`.
- `results/m2_boundary_audit_hadamard_order_dense_r1/`: rho-coverage audit,
  above-floor `flip_boundary.csv`, winner maps, and boundary fits for the
  Hadamard-order dense run. With `rel_mse<0.5`, strict equal-frame winners are
  above-floor in 29/45 prompt-range cells: 28 select `srht_paired + pairwise`,
  one selects `hadamard_random_paired + scgi_proxy`, and 16/45 cells are
  sub-floor.
- `results/m2_boundary_audit_highrho/`: rho-coverage audit, above-floor
  `flip_boundary.csv`, log-rho interpolated flip-boundary fits, and winner-map
  summaries for the high-rho M2 merge. With the default `rel_mse<0.5` gate,
  strict equal-frame winners are above-floor in 29/45 prompt-range cells and
  16/45 cells are labelled sub-floor/noise-floor.
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
- `results/phase_m2_scgi_gain_predictor_rawgain_fixedloader_r1/`: monitored
  4,050-row held-out check through the fixed checkpoint-metadata loading path;
  raw-gain predictor improves from 12.05 to 14.77 dB mean but remains below
  `none` and `scgi_proxy`; the paired SRHT/pairwise baseline remains the
  pre-floor strict equal-frame winner in the six-cell diagnostic map.
- `results/m2_scgi_proxyinput_gain1d_smoke_r1/` and
  `results/phase_m2_scgi_proxyinput_gain1d_heldout_smoke_r1/`: proxy-envelope
  input plus 1D gain-predictor smoke; held-out `scgi_frozen` reaches 15.72 dB
  mean, above `none`/`agc` and 0.18 dB below `scgi_proxy`.
- `results/phase_m2_scgi_proxyinput_gain1d_dense_r1_merged/` and
  `results/m2_boundary_audit_proxyinput_gain1d_dense_r1/`: 114,750-row
  prompt-range dense trained-network scan. `scgi_frozen` averages 15.92 dB,
  above `none`/AGC but below `scgi_proxy`; `srht_paired + pairwise` remains the
  strict equal-frame winner before applying the reconstruction-floor mask.
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
  tables, fitted-law plots, SVG vector sidecars, captions, and
  `paper_figure_manifest.csv` / `paper_figure_manifest_vectors.csv`.
- `results/paper_figures_r1/multipanels/`: draft 300-dpi multipanel PNG/PDF/SVG
  assemblies for Figures 3, 4, and 7 plus `paper_multipanel_manifest.csv`
  linking each panel to its audited source CSV.
- `results/paper_figures_r2_final/`: final figure-pack draft with four figures
  and 13 panel rows, exported as editable SVG plus PNG/PDF/TIFF with
  repo-relative `figure_assembly_manifest.csv`.
- `results/nonideal_m2_compact/`: compact ideal/nonideal M2 digital-twin scan
  with SLM quantization, finite contrast, detector noise, timing jitter, and
  noisy reference samples.
- `results/nonideal_m2_full_r1_merged/`: 157,500-row full ideal/nonideal M2
  digital-twin scan over the dense 7x5 grid, merged from five Colab L4 shards.
- `results/mechanism_m1_protocol_o10s5/`: monitored 10-object x 5-seed
  M1 mechanism run with 4,200 oracle/AGC rows, 1,750 AGC-window rows,
  1,750 residual-error rows, 5,400 pairwise rows, plus
  `m1_mechanism_audit_report.md`, summary JSON, and compact PNG audit tables.
- `results/m2_hadamard_order_dense_r1_merged/` and
  `results/m2_boundary_audit_hadamard_order_dense_r1/`: current M2 source
  tables used by the latest paper-facing phase-map rendering.
- `results/srht_m3_protocol_o10s5_highrho_r2/`: monitored 10-object x 5-seed
  M3 fallback ablation at `rho=0.001,0.1,1,10` and `sigma_a=0.30`, with 8,000
  raw rows and 160 summary rows over ordered, signed, full-SRHT, time-interleaved,
  and block-shuffled variants.
- `results/srht_m3_audit_highrho_r2/`: M3 high-rho fallback audit tables, JSON
  summary, PNG table, and Markdown report. Full SRHT gives +5.453 dB over
  ordered Hadamard at `rho=0.001` under AGC, while row permutation or diagonal
  signs alone recover essentially the same advantage. At `rho=0.1`, AGC variants
  are already transitional/sub-floor by the default `rel_mse<0.5` gate
  (`rel_mse` about 0.57-0.67), and at `rho>=1` all blind variants are at the
  reconstruction floor; the high-rho fallback deltas are labelled noise-floor
  coincidences rather than effects.
- `results/m3_random_comparator_fast_r1/`: monitored sub-floor diagnostic M3 comparator
  adding direct `random_uniform` and `random_binary` baselines at
  `rho=1,10`, `sigma_a=0.30,0.50`; full SRHT is within +0.016 to +0.190 dB of
  the best random basis but remains slightly below ordered Hadamard, so the
  strong `>=3 dB` constructive gate is still refuted.
- `results/m3_random_comparator_fast_ls_r1/`: monitored least-squares random
  control over the same fast-drift grid. Random binary with LS remains at the
  reconstruction floor (`rel_mse` 0.963-0.987), and SRHT/pairwise is only
  +0.059 to +0.322 dB above the best random basis, so this narrows the estimator
  caveat without creating an above-floor fast-drift effect.
- Current M1 audit figures are under `results/mechanism_m1_protocol_o10s5/`;
  paper-facing M2/M4 and multipanel drafts live under `results/paper_figures_r1/`.

## Tests

Run the unittest suite with the CUDA conda runtime rather than the system `python`
on this machine:

```powershell
cd E:\GAN_FCC_WORK\scgi-repro
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' -m unittest discover -s tests -v
```
