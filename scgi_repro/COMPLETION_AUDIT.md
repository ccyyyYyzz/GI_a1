# Completion Audit

Updated: 2026-07-09

This audit maps the two user-provided prompt files to current evidence in this
repository. It is intentionally stricter than `REPORT.md`: a requirement is only
marked done when the current files/results prove it.

## Source Papers Checked

Zotero items and PDF attachments were found and used for spot checks.

| Paper | Zotero item | Attachment | Local extracted text |
|---|---|---|---|
| Peng and Chen, APL 2024 SCGI | `YE779UHZ` | `HCNJHIE9` | `results/pdf_text/scgi_text.txt` |
| Peng, Xiao, and Chen, OE 2025 OWT | `CQ36ATU6` | `RX8DL2G6` | `results/pdf_text/owc_text.txt` |

The SCGI PDF confirms the prompt's core numerical model: 128x128 patterns,
N=16384 realizations, M=5000 MNIST samples, dynamic scaling
`R_mn = a_mn B_mn = lambda_m^n B_mn`, lambda in `[0.9995, 1.0]`, U-Net
correction with Gaussian prior, and SCGI/SCGI-UNN/SCGI-URED CNR targets in
Fig. 9. The OWT PDF confirms the reference-pattern and differential
`(1 +/- P_k)/2` logic that motivates the mechanism-study reference and pairwise
baselines.

## Task 1: SCGI Reproduction

| Requirement | Status | Current evidence |
|---|---|---|
| Configurable project with `config.yaml`, `src/`, `tests/`, `results/` | Done | Expected modules exist under `src/`; `config.yaml`; 30 unit tests pass |
| Static GI forward model, dynamic exponential scaling, DGI, CNR/PSNR/SSIM/KS | Done | `src/data_sim.py`, `src/dgi.py`, `src/metrics.py`; tests; `results/stage_0/smoke/metrics.json` |
| Stage 0 debug/smoke full pipeline | Done | `results/stage_0/smoke`, local debug e80, Colab debug e160 |
| Stage 1 diagnostics: B histogram, R dynamic curve, lambda distribution | Done at smoke scale | `results/stage_1/smoke/*` |
| Stage 2 SCGI U-Net with Gaussian prior and gamma sweep | Partial | `src/scgi_model.py`, `src/train_scgi.py`, Colab gamma sweep; strict KS pass target not met for plain gain U-Net; `exponential_residual_unet` smoke and full tests match analytic correction |
| Stage 3 held-out DGI validation | Partial | `results/stage_3/smoke`; Colab debug Stage3; full exp-residual Stage3 matches analytic/static but all-target CNR >= 3 fails where static bound is below 3; authoritative full matrix is in `results/stage3_threshold_matrix_full_r2_authoritative`; `results/stage3_static_dgi_audit` shows the random static PSNR>20 gate remains unmet even after affine alignment, with best affine PSNR 15.92 dB, while paired-Hadamard exact inversion reaches 80.00 dB |
| Stage 4 SCGI-UNN and SCGI-URED | Partial | Full 500-step matrix now includes SCGI-UNN and SCGI-URED for four held-out targets; URED is above UNN on all four, but mean/min CNRs are only 5.084/2.270 vs APL URED minimum 10.43. Follow-up stripe screens show avg-pool RED final/target-aware trace CNR 2.916/3.831 and NLM RED final/target-aware trace CNR 5.131/8.913. The repaired all-object NLM audit reaches final CNRs 8.453/6.033/10.270/7.842 for A/stripe/L/ring, still below the all-target APL URED gate; `results/stage4_ured_proxy_audit_r1` finds no validated target-free stopping rule |
| Full paper-scale profile, 128x128/N=16384/M=5000/100 epochs | Partial | Colab full e100 gain-U-Net now reaches SCGI CNR 1.1705 after gain-range fix; full exp-residual e2 reaches analytic/static CNR 2.5353 and KS pass 1.0 |
| Paper-threshold reproduction: SCGI CNR 3-4, UNN 8-14, URED 10-38 | Not achieved | `results/published_calibration` encodes APL Fig. 6/Fig. 9 targets; authoritative full matrix remains below all APL minima: SCGI min 2.492 vs 3.39, UNN min 2.254 vs 7.93, URED min 2.270 vs 10.43 |
| Colab durability: checkpoint resume, Drive persistence, CU accounting | Partial to done | `run_monitored_job.py` adds durable local/Colab CLI logs, `status.json`, git/CUDA metadata, and CU estimates when a rate is supplied; `colab/colab_github_job_runner.py` writes `colab_job_status.json` and supports `--persist-root` periodic artifact copies to an already-mounted path; `run_phase_m2.py --resume` and `run_nonideal_m2.py --resume` append completed units and skip them on rerun; `run_stage0.py --resume-checkpoint` and `run_m2_scgi_train.py --resume-checkpoint` restore epoch checkpoints. Automatic Drive authorization or GitHub upload from Colab is not implemented |

## Task 2: Measurement-Basis Mechanism Study

| Requirement | Status | Current evidence |
|---|---|---|
| Fair protocol in `PROTOCOL.md` | Done | `PROTOCOL.md` records frame budget, throughput, channel/noise, oracle, reference overhead |
| M1 oracle/AGC/error/pairwise mechanism experiments | Partial to done | `results/mechanism_m1_protocol_o10s5` has oracle, AGC window, error propagation, pairwise failure CSVs |
| M2 phase scan over rho/sigma grid with equal frame accounting | Done for compact protocol | `results/phase_m2_reference_protocol_o10s5/phase_scan.csv` has 68,250 rows; `results/phase_m2_scgi_proxy_dense_r1_merged/phase_scan.csv` has 78,750 rows with `scgi_proxy`; `results/phase_m2_scgi_proxy_dense_r1_highrho_merged/phase_scan.csv` has 101,250 rows and covers the prompt rho range 0.001..10 |
| M2 outputs: best methods, selected curves, flip boundary | Partial to done | Tables generated; `results/m2_boundary_audit_highrho` confirms rho coverage to 10, five log-rho boundary fits with R2 >= 0.9, `srht_paired + pairwise` as the strict equal-frame winner in 45/45 prompt-range cells, and selected curve/boundary PNGs. `results/paper_figures_r1` now adds strict equal-frame and all-non-oracle prompt-range winner maps plus a compact observed-boundary fit table with captions in `paper_figure_manifest.csv`; final venue-specific vector panel assembly remains open |
| M2 includes SCGI-network blind correction | Partial | `scgi_proxy` is dense-tested as an equal-frame blind smooth-gain proxy; `scgi_frozen` loads saved SCGI checkpoints and is dense-tested through the full prompt rho range in `results/phase_m2_scgi_frozen_dense_r1_highrho_merged` with 13,500 frozen-network rows. `run_m2_scgi_train.py` and `--scgi-checkpoint-map` add a supervised M2 fine-tuning/routing path, and `results/phase_m2_scgi_basis_specific_heldout_smoke_r1` gives a held-out smoke check where `srht_paired + scgi_frozen` wins 2/6 local cells. Signed-safe outputs and `gain_predictor_unet --target-mode gain` are implemented, but `results/phase_m2_scgi_gain_predictor_rawgain_heldout_smoke_r1` still averages -3.26 dB versus `none`. Overall the trained network variants underperform `none`, `scgi_proxy`, and paired `pairwise`, so a competitive fine-tuned network phase diagram remains open |
| M3 SRHT constructive method and ablations | Partial | `results/srht_m3_protocol_o10s5` exists; M3 full claim thresholds are not all proven |
| M4 theory with fitted laws and notebook-level verification | Partial to done | `run_theory_m4.py`, `results/theory_m4_compact`, `results/theory_m4_paper_r1`, and `results/theory_m4_paper_r2_highrho` now provide 16/32/64 fitted laws, bootstrap intervals, AGC window diagnostics, and censored flip-boundary interval accounting against the prompt-range high-rho phase table; `THEORY.md` contains a candidate AGC bias-variance law and `PAPER_OUTLINE.md` now has eight draft main-figure captions. `results/theory_m4_agc_targeted_r1` adds a targeted AGC validation with 86,400 raw rows; fits improve to R2 0.71-0.82 but 42-56% of best windows remain boundary-selected, so the simple AGC law is diagnostic rather than final. `run_make_paper_figures.py` renders paper-facing M4 residual-error, random-frame, energy-concentration, and AGC-window draft panels under `results/paper_figures_r1`. Final venue-formatted vector polishing and a better/boundary-aware AGC model remain open |
| Published-channel calibration and nonideal detector/SLM model | Partial | `run_nonideal_m2.py`, `results/nonideal_m2_compact`, and `results/nonideal_m2_full_r1_merged` implement shot/read noise, 8-bit SLM quantization, finite contrast, timing jitter, and noisy references through a full 157,500-row main scan; `results/published_calibration` records APL/OE target values, and `results/published_channel_calibration` now records APL trace digitizations plus OE channel anchors. Raw detector/SLM hardware calibration remains unavailable from the PDFs |
| Paper outline and conservative positioning | Partial to done | `PAPER_OUTLINE.md` now reflects dense/high-rho M2, frozen SCGI limitations, M4 high-rho r2 hooks, and draft captions for the eight planned main figures; `results/paper_figures_r1/paper_figure_manifest.csv` maps current M2/M4 draft figures to source CSVs and captions. Final journal-specific figure assembly remains open |
| Sharded Colab scanning and merge | Done for M2 and nonideal M2 | `run_phase_m2.py --shard i/k --resume`; `merge_phase_m2_shards.py`; `run_nonideal_m2.py --shard i/k --resume`; `merge_nonideal_m2_shards.py`; both scanners now write `progress.json`; five Colab L4 shards merged into `results/phase_m2_scgi_proxy_dense_r1_merged` with 78,750 rows and `results/nonideal_m2_full_r1_merged` with 157,500 rows |

## Current Verified Commands

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' -m unittest discover -s tests -v
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' -m py_compile run_monitored_job.py colab\colab_github_job_runner.py run_phase_m2.py run_nonideal_m2.py src\run_progress.py
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_monitored_job.py --run-id wrapper_smoke --output-dir results\cli_runs\wrapper_smoke --heartbeat-seconds 1 --accelerator t4 -- 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' -c "print('wrapper smoke ok')"
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile smoke --objects 1 --seeds 1 --rho-values "0.001" --sigma-values "0.05" --reference-periods "2" --shard 0/2 --output-dir results\phase_m2_resume_smoke --no-findings
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile smoke --objects 1 --seeds 1 --rho-values "0.001" --sigma-values "0.05" --reference-periods "2" --shard 0/2 --output-dir results\phase_m2_resume_smoke --resume --no-findings
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_nonideal_m2.py --profile smoke --objects 1 --seeds 1 --rho "0.001" --sigma-a "0.05" --bases "random_uniform hadamard_paired" --corrections "none oracle agc reference_k8" --shard 0/2 --output-dir results\nonideal_m2_resume_smoke
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_nonideal_m2.py --profile smoke --objects 1 --seeds 1 --rho "0.001" --sigma-a "0.05" --bases "random_uniform hadamard_paired" --corrections "none oracle agc reference_k8" --shard 0/2 --output-dir results\nonideal_m2_resume_smoke --resume
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_stage0.py --profile smoke --epochs 1 --tag stage0_resume_smoke --skip-ured
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_stage0.py --profile smoke --epochs 2 --tag stage0_resume_smoke --skip-ured --resume-checkpoint results\stage_0\stage0_resume_smoke\checkpoint_latest.pt
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_m2_scgi_train.py --profile smoke --objects 2 --seeds 1 --bases "random_uniform" --rho-values "0.001" --sigma-values "0.05" --epochs 1 --batch-size 1 --model-kind gain_unet --output-dir results\m2_train_resume_smoke
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_m2_scgi_train.py --profile smoke --objects 2 --seeds 1 --bases "random_uniform" --rho-values "0.001" --sigma-values "0.05" --epochs 2 --batch-size 1 --model-kind gain_unet --output-dir results\m2_train_resume_smoke --resume-checkpoint results\m2_train_resume_smoke\m2_scgi_checkpoint_latest.pt
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_make_figures.py
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile smoke --objects 1 --seeds 1 --shard 0/2 --no-findings --output-dir results\phase_m2_shardcheck_0of2
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile smoke --objects 1 --seeds 1 --shard 1/2 --no-findings --output-dir results\phase_m2_shardcheck_1of2
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' merge_phase_m2_shards.py --inputs results\phase_m2_shardcheck_0of2 results\phase_m2_shardcheck_1of2 --output-dir results\phase_m2_shardcheck_merged
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile smoke --objects 1 --seeds 1 --output-dir results\phase_m2_scgi_proxy_smoke --no-findings
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' merge_phase_m2_shards.py --inputs results\colab_imports\pro1_dense_r1_shard0of5\artifacts results\colab_imports\pro1_dense_r1_shard1of5\artifacts results\colab_imports\pro2_dense_r1_shard2of5\artifacts results\colab_imports\pro2_dense_r1_shard3of5\artifacts results\colab_imports\pro2_dense_r1_shard4of5\artifacts --output-dir results\phase_m2_scgi_proxy_dense_r1_merged
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile smoke --objects 10 --seeds 5 --rho-values "3,10" --sigma-values "0.05,0.10,0.15,0.30,0.50" --shard i/5 --output-dir results\phase_m2_highrho_o10s5_shardiof5 --no-findings
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' merge_phase_m2_shards.py --inputs results\phase_m2_scgi_proxy_dense_r1_merged results\phase_m2_highrho_o10s5_shard0of5 results\phase_m2_highrho_o10s5_shard1of5 results\phase_m2_highrho_o10s5_shard2of5 results\phase_m2_highrho_o10s5_shard3of5 results\phase_m2_highrho_o10s5_shard4of5 --output-dir results\phase_m2_scgi_proxy_dense_r1_highrho_merged
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_m2_boundary_audit.py --phase-dir results\phase_m2_scgi_proxy_dense_r1_highrho_merged --output-dir results\m2_boundary_audit_highrho
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_stage0.py --profile smoke --epochs 2 --tag smoke_exp_residual_e2_skipured --model-kind exponential_residual_unet --skip-ured
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_stage3_tests.py --profile full --checkpoint results\colab_imports\pro2_full_exp_residual_e2_r1\artifacts\model_checkpoint.pt --output-dir results\stage_3_exp_residual_colab_full --model-kind exponential_residual_unet
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile smoke --objects 1 --seeds 1 --no-findings --scgi-checkpoint results\colab_imports\pro2_full_exp_residual_e2_r1\artifacts\model_checkpoint.pt --scgi-model-kind exponential_residual_unet --output-dir results\phase_m2_scgi_frozen_smoke
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_m2_scgi_train.py --profile smoke --model-kind gain_unet --bases "random_uniform hadamard_paired srht_paired" --rho-values "0.001 0.1 1.0" --sigma-values "0.05 0.30" --objects 3 --seeds 2 --epochs 20 --output-dir results\m2_scgi_finetune_gain_smoke_r1
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile smoke --objects 5 --seeds 3 --rho-values "0.003 0.3 3.0" --sigma-values "0.10 0.50" --reference-periods "2 8" --scgi-checkpoint-map results\m2_scgi_basis_specific_smoke_r1\checkpoint_map.json --output-dir results\phase_m2_scgi_basis_specific_heldout_smoke_r1 --no-findings
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_m2_scgi_train.py --profile smoke --model-kind gain_predictor_unet --target-mode gain --input-normalize row_max --target-normalize none --gain-min 0.05 --gain-max 2.5 --bases "random_uniform hadamard_paired srht_paired" --rho-values "0.001 0.1 1.0" --sigma-values "0.05 0.30" --objects 3 --seeds 2 --epochs 30 --output-dir results\m2_scgi_gain_predictor_rawgain_smoke_r1
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile smoke --objects 5 --seeds 3 --rho-values "0.003 0.3 3.0" --sigma-values "0.10 0.50" --reference-periods "2 8" --scgi-checkpoint results\m2_scgi_gain_predictor_rawgain_smoke_r1\m2_scgi_checkpoint.pt --output-dir results\phase_m2_scgi_gain_predictor_rawgain_heldout_smoke_r1 --no-findings
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' merge_phase_m2_shards.py --inputs results\colab_imports\pro1_m2_scgi_frozen_dense_r1_shard0of5\artifacts results\colab_imports\pro1_m2_scgi_frozen_dense_r1_shard1of5\artifacts results\colab_imports\pro2_m2_scgi_frozen_dense_r1_shard2of5\artifacts results\colab_imports\pro2_m2_scgi_frozen_dense_r1_shard3of5\artifacts results\colab_imports\pro2_m2_scgi_frozen_dense_r1_shard4of5\artifacts --output-dir results\phase_m2_scgi_frozen_dense_r1_merged
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_stage3_tests.py --profile full --checkpoint results\colab_imports\pro2_full_exp_residual_e2_r1\artifacts\model_checkpoint.pt --model-kind exponential_residual_unet --include-unn-ured --ured-steps 500 --output-dir results\stage3_threshold_matrix_full_r2_authoritative
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_stage3_static_dgi_audit.py --profile full --output-dir results\stage3_static_dgi_audit
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_stage4_ured_sweep.py --profile full --checkpoint results\colab_imports\pro2_full_exp_residual_e2_r1\artifacts\model_checkpoint.pt --model-kind exponential_residual_unet --object-names stripe_target --steps-values 200 --beta-values "0.1 0.25 0.5" --xi-values "0.25 0.50" --x-step-values "0.1 0.25" --residual-scale-values 0.3 --denoiser-values nlm --nlm-h-values "0.06 0.08 0.10 0.12" --fixed-init-seed 20240709 --output-dir results\stage4_ured_sweep_nlm_r1_stripe --save-traces
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_stage4_ured_sweep.py --profile full --checkpoint results\colab_imports\pro2_full_exp_residual_e2_r1\artifacts\model_checkpoint.pt --model-kind exponential_residual_unet --steps-values 200 --beta-values 0.5 --xi-values 0.5 --x-step-values 0.1 --residual-scale-values 0.3 --denoiser-values nlm --nlm-h-values "0.06 0.08" --fixed-init-seed 20240709 --output-dir results\stage4_ured_sweep_nlm_allobjects_r1 --save-traces
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_published_calibration.py --output-dir results\published_calibration
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_published_channel_calibration.py --output-dir results\published_channel_calibration
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_theory_m4.py --output-dir results\theory_m4_compact
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_theory_m4.py --sizes "16 32 64" --objects 5 --seeds 4 --sigmas "0.01 0.02 0.05 0.10" --frame-sweep-size 32 --frame-factors "1 2 4 8" --bootstrap 200 --agc-size 32 --agc-rhos "0.001 0.003 0.01 0.03 0.1 0.3 1.0" --agc-sigmas "0.05 0.15 0.30 0.50" --agc-window-fracs "0.005 0.01 0.02 0.05 0.10 0.20" --phase-dir results\phase_m2_scgi_frozen_dense_r1_merged --output-dir results\theory_m4_paper_r1
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_theory_m4.py --sizes "16 32 64" --objects 5 --seeds 4 --sigmas "0.01 0.02 0.05 0.10" --frame-sweep-size 32 --frame-factors "1 2 4 8" --bootstrap 200 --agc-size 32 --agc-rhos "0.001 0.003 0.01 0.03 0.1 0.3 1.0" --agc-sigmas "0.05 0.15 0.30 0.50" --agc-window-fracs "0.005 0.01 0.02 0.05 0.10 0.20" --phase-dir results\phase_m2_scgi_frozen_dense_r1_highrho_merged --output-dir results\theory_m4_paper_r2_highrho
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_m4_agc_targeted.py --output-dir results\theory_m4_agc_targeted_r1
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_make_paper_figures.py --output-dir results\paper_figures_r1
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_nonideal_m2.py --output-dir results\nonideal_m2_compact
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' merge_nonideal_m2_shards.py --inputs results\colab_imports\pro1_nonideal_m2_full_r1_shard0of5\artifacts results\colab_imports\pro1_nonideal_m2_full_r1_shard1of5\artifacts results\colab_imports\pro2_nonideal_m2_full_r1_shard2of5\artifacts results\colab_imports\pro2_nonideal_m2_full_r1_shard3of5\artifacts results\colab_imports\pro2_nonideal_m2_full_r1_shard4of5\artifacts --output-dir results\nonideal_m2_full_r1_merged
```

## Completion Decision

The goal is not yet fully complete under the original prompt scope. The current
state is a strong executable prototype plus several completed compact protocol
experiments, but the full paper-level SCGI thresholds, a competitive trained M2
SCGI-network correction, paper-grade M4 theory closure, and raw hardware
calibration remain open.
