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
| Configurable project with `config.yaml`, `src/`, `tests/`, `results/` | Done | Expected modules exist under `src/`; `config.yaml`; 18 unit tests pass |
| Static GI forward model, dynamic exponential scaling, DGI, CNR/PSNR/SSIM/KS | Done | `src/data_sim.py`, `src/dgi.py`, `src/metrics.py`; tests; `results/stage_0/smoke/metrics.json` |
| Stage 0 debug/smoke full pipeline | Done | `results/stage_0/smoke`, local debug e80, Colab debug e160 |
| Stage 1 diagnostics: B histogram, R dynamic curve, lambda distribution | Done at smoke scale | `results/stage_1/smoke/*` |
| Stage 2 SCGI U-Net with Gaussian prior and gamma sweep | Partial | `src/scgi_model.py`, `src/train_scgi.py`, Colab gamma sweep; strict KS pass target not met for plain gain U-Net; `exponential_residual_unet` smoke and full tests match analytic correction |
| Stage 3 held-out DGI validation | Partial | `results/stage_3/smoke`; Colab debug Stage3; full exp-residual Stage3 matches analytic/static but all-target CNR >= 3 fails where static bound is below 3 |
| Stage 4 SCGI-UNN and SCGI-URED | Partial | Implemented compact URED/UNN path; URED improves Stage0 CNR, but held-out UNN/URED target ranking is not fully validated |
| Full paper-scale profile, 128x128/N=16384/M=5000/100 epochs | Partial | Colab full e100 gain-U-Net now reaches SCGI CNR 1.1705 after gain-range fix; full exp-residual e2 reaches analytic/static CNR 2.5353 and KS pass 1.0 |
| Paper-threshold reproduction: SCGI CNR 3-4, UNN 8-14, URED 10-38 | Not achieved | Full exp-residual reaches the current static/analytic DGI bound, but that bound is below CNR 3 and PSNR 20 for some full targets; paper UNN/URED ranges remain unvalidated |
| Colab durability: checkpoint resume, Drive persistence, CU accounting | Partial | GitHub/Colab runners and local artifact extraction work; Drive/checkpoint resume and CU accounting are not implemented |

## Task 2: Measurement-Basis Mechanism Study

| Requirement | Status | Current evidence |
|---|---|---|
| Fair protocol in `PROTOCOL.md` | Done | `PROTOCOL.md` records frame budget, throughput, channel/noise, oracle, reference overhead |
| M1 oracle/AGC/error/pairwise mechanism experiments | Partial to done | `results/mechanism_m1_protocol_o10s5` has oracle, AGC window, error propagation, pairwise failure CSVs |
| M2 phase scan over rho/sigma grid with equal frame accounting | Done for compact protocol | `results/phase_m2_reference_protocol_o10s5/phase_scan.csv` has 68,250 rows; `results/phase_m2_scgi_proxy_dense_r1_merged/phase_scan.csv` has 78,750 rows with `scgi_proxy` |
| M2 outputs: best methods, selected curves, flip boundary | Partial | Tables/figures generated; flip boundary is diagnostic, not R2-fitted law |
| M2 includes SCGI-network blind correction | Partial | `scgi_proxy` is implemented and dense-tested as an equal-frame blind SCGI-style smooth-gain proxy with 10,500 rows and zero reference frames; a trained SCGI network correction is still not implemented |
| M3 SRHT constructive method and ablations | Partial | `results/srht_m3_protocol_o10s5` exists; M3 full claim thresholds are not all proven |
| M4 theory with fitted laws and notebook-level verification | Partial | `run_theory_m4.py` and `results/theory_m4_compact` provide compact N/frame-sweep fitted laws; larger N sweep, bootstrap intervals, AGC window law, and censored flip-boundary model remain open |
| Published-channel calibration and nonideal detector/SLM model | Not done | No WebPlotDigitizer-derived APL/OE calibration; no shot/read/SLM quantization main scan |
| Paper outline and conservative positioning | Partial | `PAPER_OUTLINE.md` exists, but needs updating with dense M2 and remaining limitations |
| Sharded Colab scanning and merge | Done for M2 | `run_phase_m2.py --shard i/k`; `merge_phase_m2_shards.py`; five Colab L4 shards merged into `results/phase_m2_scgi_proxy_dense_r1_merged` with 78,750 rows |

## Current Verified Commands

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' -m unittest discover -s tests -v
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_make_figures.py
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile smoke --objects 1 --seeds 1 --shard 0/2 --no-findings --output-dir results\phase_m2_shardcheck_0of2
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile smoke --objects 1 --seeds 1 --shard 1/2 --no-findings --output-dir results\phase_m2_shardcheck_1of2
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' merge_phase_m2_shards.py --inputs results\phase_m2_shardcheck_0of2 results\phase_m2_shardcheck_1of2 --output-dir results\phase_m2_shardcheck_merged
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile smoke --objects 1 --seeds 1 --output-dir results\phase_m2_scgi_proxy_smoke --no-findings
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' merge_phase_m2_shards.py --inputs results\colab_imports\pro1_dense_r1_shard0of5\artifacts results\colab_imports\pro1_dense_r1_shard1of5\artifacts results\colab_imports\pro2_dense_r1_shard2of5\artifacts results\colab_imports\pro2_dense_r1_shard3of5\artifacts results\colab_imports\pro2_dense_r1_shard4of5\artifacts --output-dir results\phase_m2_scgi_proxy_dense_r1_merged
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_stage0.py --profile smoke --epochs 2 --tag smoke_exp_residual_e2_skipured --model-kind exponential_residual_unet --skip-ured
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_stage3_tests.py --profile full --checkpoint results\colab_imports\pro2_full_exp_residual_e2_r1\artifacts\model_checkpoint.pt --output-dir results\stage_3_exp_residual_colab_full --model-kind exponential_residual_unet
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_theory_m4.py --output-dir results\theory_m4_compact
```

## Completion Decision

The goal is not yet fully complete under the original prompt scope. The current
state is a strong executable prototype plus several completed compact protocol
experiments, but the full paper-level SCGI thresholds, a true trained M2
SCGI-network correction, paper-grade M4 theory closure, and published/nonideal
calibration remain open.
