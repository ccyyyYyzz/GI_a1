# Goal Requirements Audit

Updated: 2026-07-09

This audit maps the two original task prompts to evidence in the current
repository. It intentionally separates strict paper reproduction from modified
diagnostic passes, oversampling controls, exact-inverse controls, and
post-processing routes.

## Current Shared Checkpoint

- Branch: `scgi-ceiling-diagnostic-r1`
- Latest pushed checkpoint before this audit: `5c499e84ae52bb1fc099744a82a373d2ce581f30`
- Review URL: <https://github.com/ccyyyYyzz/GI_a1/tree/scgi-ceiling-diagnostic-r1/scgi_repro>
- Draft PR URL: <https://github.com/ccyyyYyzz/GI_a1/pull/new/scgi-ceiling-diagnostic-r1>
- Latest verification before this audit: `pytest tests/test_core.py -q` passed with 34 tests.
- Colab L4 independently reran the static ceiling diagnostic at commit
  `5c499e84ae52bb1fc099744a82a373d2ce581f30`.
- New prompt-gap Colab runs used L4 sessions at the same commit and returned
  `state=success`, `return_code=0`: `pro1_stage0_debug_prompt_exact_colab_r1`
  and `pro2_stage1_full_diagnostics_colab_r1`.

## Goal Decision

The overall goal is not complete under the original strict prompts.

The repository now has a substantial and reviewable reproduction framework:
physics simulation, correction networks, DGI/SCGI/UNN/URED runners, mechanism
studies, Colab sharding, monitoring, and detailed reports. However, the strict
paper-scale gates are not met: full-matrix SCGI remains below the APL Fig. 9
CNR floor on hard targets, strict SCGI-UNN remains far below the APL range, and
strict continuous NLM URED remains below the APL minimum. Several modified or
off-protocol routes clear thresholds, but they must not be counted as strict
paper reproduction.

## SCGI Reproduction Prompt

| Requirement | Status | Evidence | Next action |
|---|---|---|---|
| Project structure with config, assumptions, `src/`, tests, and results | Done | `config.yaml`, `ASSUMPTIONS.md`, `src/`, `tests/`, `results/` | Keep naming clear because some outputs are not exactly `results/stage_X/`. |
| Static GI forward model, shared random patterns, exponential dynamic scattering, DGI, CNR/PSNR/SSIM/KS diagnostics | Done | `src/data_sim.py`, `src/dgi.py`, `src/metrics.py` | No immediate gap. |
| Stage 0 debug pipeline at 64x64, N=4096, M=200, 10 epochs | Direct evidence added, strict gates failed | Colab L4 `results/colab_imports/pro1_stage0_debug_prompt_exact_colab_r1/artifacts/metrics.json`: profile `debug`, device `cuda:0`, 64x64, N=4096, 10 epochs, `val_mse_last=0.02178`, dynamic slope -0.742, corrected slope -0.077, analytic slope -3.8e-05. Directionality passes, but `scgi_dgi_cnr=0.433`, static DGI PSNR 8.948, and SCGI KS pass rate 0.0 fail strict prompt gates. | Keep as negative direct evidence; do not count as strict Stage 2 success. |
| Stage 1 full MNIST data simulation and diagnostics | Done for direct diagnostics | Colab L4 `results/colab_imports/pro2_stage1_full_diagnostics_colab_r1/artifacts/full/stage1_summary.csv`: profile `full`, device `cuda:0`, samples 5000, image 128, patterns 16384, 10 plotted diagnostics, plotted KS pass rate 1.0, lambda range 0.9995-1.0. | Full diagnostics are covered; remaining strict failure is downstream correction/reconstruction, not missing Stage 1 simulation. |
| Stage 2 U-Net supervised correction with gamma sweep, KS pass >90%, near-zero residual slope | Partial / not proven for strict U-Net | Code exists in `src/scgi_model.py` and `src/train_scgi.py`; exp-residual model gives analytic-like correction; reports say strict gain/direct U-Net did not clear all gates | Restore or rerun direct `gamma_sweep.csv` and full 100-epoch strict U-Net artifacts if strict completion is still required. |
| Stage 3 held-out dynamic failure and SCGI recovery | Partial | Directionality is established; authoritative full matrix is under `results/stage3_threshold_matrix_full_r2_authoritative` | Strict all-target SCGI CNR and static PSNR gates remain open. |
| Stage 3 static DGI PSNR >20 at paper N=K | Not achieved | `results/stage3_static_dgi_audit/stage3_static_dgi_audit_report.md`; static random-DGI PSNR remains below 20 at N=K | Treat as a static estimator/frame-budget ceiling unless paper ROI/display normalization can be matched differently. |
| Stage 3 all-target SCGI CNR >=3 and APL Fig. 9 range 3.39-4.04 | Not achieved | Full matrix minimum SCGI CNR is below the APL floor; ceiling diagnostic at N=K gives A/stripe/L/ring CNR 3.377/2.475/3.490/2.973 | Static ceiling diagnostic shows stripe/ring clear only at 2K random frames or off-protocol inverse/LS controls. |
| Stage 4 strict SCGI-UNN range 8-14 | Not achieved | `results/stage4_unn_stripe_puredata_colab_r1_merged/REPORT.md`; best stripe UNN around 2.55 | Do not claim UNN reproduction without a new mechanism or matching paper details. |
| Stage 4 strict continuous NLM URED range 10-38 | Not achieved | `results/stage4_ured_continuous_binary_refine_colab_r3grid_merged/REPORT.md`; best strict continuous stripe CNR about 9.933 vs APL minimum 10.43 | Current evidence says strict NLM path misses narrowly but consistently. |
| Modified URED / thresholded trace routes | Diagnostic pass, not strict pass | `results/stage4_ured_otsu_soft_colab_allobjects_r1`, `results/stage4_ured_otsu_soft_seed_robust_colab_r1`, `results/stage4_threshold_trace_audit_r1` | Present as modified target-free diagnostic or new method, not as original continuous URED reproduction. |
| Colab, checkpoints, sharding, monitoring, resume | Partial to done | `run_monitored_job.py`, `colab/colab_github_job_runner.py`, launcher scripts, shard logs and merged outputs | Automatic Drive authorization/GitHub push from Colab remains intentionally avoided. |
| Final report | Done as status report, not proof of success | `REPORT.md`, `FINDINGS.md`, `COMPLETION_AUDIT.md` | Add this audit to make strict completion state explicit. |

## Measurement-Basis Mechanism Prompt

| Requirement | Status | Evidence | Next action |
|---|---|---|---|
| Fair comparison protocol for bases and correction settings | Done with new audit table | `PROTOCOL.md`, `src/basis.py`, `src/mechanisms.py`, and `results/protocol_audit_r1/`. `protocol_audit.csv` has 40 basis/reference rows over 10 strict bases and periods 0/2/8/32; `object_audit.csv` has 10 deterministic synthetic-object rows; `seed_split_audit.csv` records seed conventions. | Keep strict/diagnostic labels in every figure/table. `random_gaussian` is now explicitly labelled as a signed mathematical control. |
| M1 oracle, blind AGC error, residual propagation, pairwise failure curves | Mostly done | `run_mechanism_m1.py`, `run_m1_mechanism_audit.py`, reported M1 result directories | Still lacks a dedicated SCGI-network gain-error decomposition, random-order Hadamard AGC add-on, and full photon-budget curve. |
| M2 dense phase map over bases, corrections, rho/sigma grid, objects and seeds | Partial to mostly done | `results/m2_hadamard_order_dense_r1_merged`, `results/m2_boundary_audit_hadamard_order_dense_r1`; framework now includes `random_gaussian` in future `run_phase_m2.py` scans and boundary-audit challengers. | Existing dense evidence still lacks a single authoritative rerun combining `random_gaussian`, trained SCGI, Hadamard order variants, and seed-split stability; 16/45 strict cells remain sub-floor. |
| M3 SRHT / Hadamard / random comparison, fast-drift advantage hypothesis | Refuted / partial | `run_srht_m3.py`, `run_m3_random_comparator.py`, `results/m3_random_comparator_fast_ls_r1` | Do not force the original >=3 dB fast-drift claim; add pink-noise and sparse-Hadamard controls only if a method-paper extension is pursued. |
| M4 theory: identifiability, estimator lower bound, error propagation, numerical validation | Partial | `THEORY.md`, `run_theory_m4.py`, `run_m4_agc_targeted.py`, `results/theory_m4_agc_targeted_r1`, paper figures | AGC law remains diagnostic: targeted fits reach R2 about 0.71-0.82 with many boundary-selected windows. A notebook-level `.ipynb` verification artifact is still missing. |
| Published calibration / nonideal digital twin | Partial | `run_published_calibration.py`, `run_published_channel_calibration.py`, `run_nonideal_m2.py`, merged nonideal outputs | Raw hardware calibration data remains unavailable; label as published-anchor/digital-twin calibration. |
| Paper-ready figures, captions, outline, surprises | Partial | `PAPER_OUTLINE.md`, `SURPRISES.md`, `run_make_paper_figures.py`, `run_make_final_figure_pack.py` | Final venue-specific figure pack and text still need one polishing pass. |

## Highest-Priority Gaps

1. Freeze a strict reproduction status table that includes only paper-scale
   random-uniform N=K, continuous-output, non-oversampled, non-thresholded
   SCGI/UNN/URED outputs.
2. Recover or rerun the direct strict U-Net gamma sweep and full 100-epoch
   artifacts so the Stage 2 conclusion does not rely only on report prose.
3. Rerun the authoritative M2 dense table if the measurement-basis paper needs
   one table containing `random_gaussian`, trained SCGI, Hadamard order variants,
   and seed-split stability rather than separate supporting scans.
4. Decide whether the final deliverable should be a faithful negative/partial
   reproduction report or a redesigned method paper. The current evidence
   supports the former much more strongly.
5. For the measurement-basis study, keep M3 as a refuted hypothesis with a
   mechanistic explanation rather than a forced success claim.
6. Continue using Colab for direct evidence generation and independent
   validation, while local CUDA handles short audits and aggregation.
