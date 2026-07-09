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
| Configurable project with `config.yaml`, `src/`, `tests/`, `results/` | Done | Expected modules exist under `src/`; `config.yaml`; 21 unit tests pass |
| Static GI forward model, dynamic exponential scaling, DGI, CNR/PSNR/SSIM/KS | Done | `src/data_sim.py`, `src/dgi.py`, `src/metrics.py`; tests; `results/stage_0/smoke/metrics.json` |
| Stage 0 debug/smoke full pipeline | Done | `results/stage_0/smoke`, local debug e80, Colab debug e160 |
| Stage 1 diagnostics: B histogram, R dynamic curve, lambda distribution | Done at smoke scale | `results/stage_1/smoke/*` |
| Stage 2 SCGI U-Net with Gaussian prior and gamma sweep | Partial | `src/scgi_model.py`, `src/train_scgi.py`, Colab gamma sweep; strict KS pass target not met for plain gain U-Net; `exponential_residual_unet` smoke and full tests match analytic correction |
| Stage 3 held-out DGI validation | Partial | `results/stage_3/smoke`; Colab debug Stage3; full exp-residual Stage3 matches analytic/static but all-target CNR >= 3 fails where static bound is below 3; authoritative full matrix is in `results/stage3_threshold_matrix_full_r2_authoritative`; `results/stage3_static_dgi_audit` shows the static PSNR>20 gate remains unmet even after affine alignment, with best affine PSNR 15.92 dB |
| Stage 4 SCGI-UNN and SCGI-URED | Partial | Full 500-step matrix now includes SCGI-UNN and SCGI-URED for four held-out targets; URED is above UNN on all four, but mean/min CNRs are only 5.084/2.270 vs APL URED minimum 10.43 |
| Full paper-scale profile, 128x128/N=16384/M=5000/100 epochs | Partial | Colab full e100 gain-U-Net now reaches SCGI CNR 1.1705 after gain-range fix; full exp-residual e2 reaches analytic/static CNR 2.5353 and KS pass 1.0 |
| Paper-threshold reproduction: SCGI CNR 3-4, UNN 8-14, URED 10-38 | Not achieved | `results/published_calibration` encodes APL Fig. 6/Fig. 9 targets; authoritative full matrix remains below all APL minima: SCGI min 2.492 vs 3.39, UNN min 2.254 vs 7.93, URED min 2.270 vs 10.43 |
| Colab durability: checkpoint resume, Drive persistence, CU accounting | Partial | GitHub/Colab runners and local artifact extraction work; Drive/checkpoint resume and CU accounting are not implemented |

## Task 2: Measurement-Basis Mechanism Study

| Requirement | Status | Current evidence |
|---|---|---|
| Fair protocol in `PROTOCOL.md` | Done | `PROTOCOL.md` records frame budget, throughput, channel/noise, oracle, reference overhead |
| M1 oracle/AGC/error/pairwise mechanism experiments | Partial to done | `results/mechanism_m1_protocol_o10s5` has oracle, AGC window, error propagation, pairwise failure CSVs |
| M2 phase scan over rho/sigma grid with equal frame accounting | Done for compact protocol | `results/phase_m2_reference_protocol_o10s5/phase_scan.csv` has 68,250 rows; `results/phase_m2_scgi_proxy_dense_r1_merged/phase_scan.csv` has 78,750 rows with `scgi_proxy`; `results/phase_m2_scgi_proxy_dense_r1_highrho_merged/phase_scan.csv` has 101,250 rows and covers the prompt rho range 0.001..10 |
| M2 outputs: best methods, selected curves, flip boundary | Partial to done | Tables generated; `results/m2_boundary_audit_highrho` confirms rho coverage to 10, five log-rho boundary fits with R2 >= 0.9, `srht_paired + pairwise` as the strict equal-frame winner in 45/45 prompt-range cells, and two selected curve/boundary PNGs. Paper-ready captions remain open |
| M2 includes SCGI-network blind correction | Partial | `scgi_proxy` is dense-tested as an equal-frame blind smooth-gain proxy; `scgi_frozen` now loads a saved SCGI checkpoint and is dense-tested in `results/phase_m2_scgi_frozen_dense_r1_merged` with 10,500 frozen-network rows, but the direct cross-domain baseline underperforms and a competitive fine-tuned network phase diagram remains open |
| M3 SRHT constructive method and ablations | Partial | `results/srht_m3_protocol_o10s5` exists; M3 full claim thresholds are not all proven |
| M4 theory with fitted laws and notebook-level verification | Partial | `run_theory_m4.py`, `results/theory_m4_compact`, and `results/theory_m4_paper_r1` now provide 16/32/64 fitted laws, bootstrap intervals, AGC window diagnostics, and censored flip-boundary interval accounting; `results/m2_boundary_audit_highrho` extends the boundary grid to rho=10 with R2-qualified fits; analytical AGC law and paper-ready boundary figures remain open |
| Published-channel calibration and nonideal detector/SLM model | Partial | `run_nonideal_m2.py`, `results/nonideal_m2_compact`, and `results/nonideal_m2_full_r1_merged` implement shot/read noise, 8-bit SLM quantization, finite contrast, timing jitter, and noisy references through a full 157,500-row main scan; `results/published_calibration` records APL/OE target values, and `results/published_channel_calibration` now records APL trace digitizations plus OE channel anchors. Raw detector/SLM hardware calibration remains unavailable from the PDFs |
| Paper outline and conservative positioning | Partial | `PAPER_OUTLINE.md` exists, but needs updating with dense M2 and remaining limitations |
| Sharded Colab scanning and merge | Done for M2 and nonideal M2 | `run_phase_m2.py --shard i/k`; `merge_phase_m2_shards.py`; `run_nonideal_m2.py --shard i/k`; `merge_nonideal_m2_shards.py`; five Colab L4 shards merged into `results/phase_m2_scgi_proxy_dense_r1_merged` with 78,750 rows and `results/nonideal_m2_full_r1_merged` with 157,500 rows |

## Current Verified Commands

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' -m unittest discover -s tests -v
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
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' merge_phase_m2_shards.py --inputs results\colab_imports\pro1_m2_scgi_frozen_dense_r1_shard0of5\artifacts results\colab_imports\pro1_m2_scgi_frozen_dense_r1_shard1of5\artifacts results\colab_imports\pro2_m2_scgi_frozen_dense_r1_shard2of5\artifacts results\colab_imports\pro2_m2_scgi_frozen_dense_r1_shard3of5\artifacts results\colab_imports\pro2_m2_scgi_frozen_dense_r1_shard4of5\artifacts --output-dir results\phase_m2_scgi_frozen_dense_r1_merged
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_stage3_tests.py --profile full --checkpoint results\colab_imports\pro2_full_exp_residual_e2_r1\artifacts\model_checkpoint.pt --model-kind exponential_residual_unet --include-unn-ured --ured-steps 500 --output-dir results\stage3_threshold_matrix_full_r2_authoritative
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_stage3_static_dgi_audit.py --profile full --output-dir results\stage3_static_dgi_audit
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_published_calibration.py --output-dir results\published_calibration
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_published_channel_calibration.py --output-dir results\published_channel_calibration
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_theory_m4.py --output-dir results\theory_m4_compact
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_theory_m4.py --sizes "16 32 64" --objects 5 --seeds 4 --sigmas "0.01 0.02 0.05 0.10" --frame-sweep-size 32 --frame-factors "1 2 4 8" --bootstrap 200 --agc-size 32 --agc-rhos "0.001 0.003 0.01 0.03 0.1 0.3 1.0" --agc-sigmas "0.05 0.15 0.30 0.50" --agc-window-fracs "0.005 0.01 0.02 0.05 0.10 0.20" --phase-dir results\phase_m2_scgi_frozen_dense_r1_merged --output-dir results\theory_m4_paper_r1
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_nonideal_m2.py --output-dir results\nonideal_m2_compact
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' merge_nonideal_m2_shards.py --inputs results\colab_imports\pro1_nonideal_m2_full_r1_shard0of5\artifacts results\colab_imports\pro1_nonideal_m2_full_r1_shard1of5\artifacts results\colab_imports\pro2_nonideal_m2_full_r1_shard2of5\artifacts results\colab_imports\pro2_nonideal_m2_full_r1_shard3of5\artifacts results\colab_imports\pro2_nonideal_m2_full_r1_shard4of5\artifacts --output-dir results\nonideal_m2_full_r1_merged
```

## Completion Decision

The goal is not yet fully complete under the original prompt scope. The current
state is a strong executable prototype plus several completed compact protocol
experiments, but the full paper-level SCGI thresholds, a true trained M2
SCGI-network correction, paper-grade M4 theory closure, and raw hardware
calibration remain open.
