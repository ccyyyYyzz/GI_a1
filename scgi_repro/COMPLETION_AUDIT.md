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
| Configurable project with `config.yaml`, `src/`, `tests/`, `results/` | Done | Expected modules exist under `src/`; `config.yaml`; 14 unit tests pass |
| Static GI forward model, dynamic exponential scaling, DGI, CNR/PSNR/SSIM/KS | Done | `src/data_sim.py`, `src/dgi.py`, `src/metrics.py`; tests; `results/stage_0/smoke/metrics.json` |
| Stage 0 debug/smoke full pipeline | Done | `results/stage_0/smoke`, local debug e80, Colab debug e160 |
| Stage 1 diagnostics: B histogram, R dynamic curve, lambda distribution | Done at smoke scale | `results/stage_1/smoke/*` |
| Stage 2 SCGI U-Net with Gaussian prior and gamma sweep | Partial | `src/scgi_model.py`, `src/train_scgi.py`, Colab gamma sweep; strict KS pass target not met |
| Stage 3 held-out DGI validation | Partial | `results/stage_3/smoke`; Colab Stage3 extracted; directionality passes, all-target CNR >= 3 fails |
| Stage 4 SCGI-UNN and SCGI-URED | Partial | Implemented compact URED/UNN path; URED improves Stage0 CNR, but held-out UNN/URED target ranking is not fully validated |
| Full paper-scale profile, 128x128/N=16384/M=5000/100 epochs | Attempted, not achieved | Colab full e20 and e100 ran; both underfit badly (`SCGI CNR ~0.127` at e100) |
| Paper-threshold reproduction: SCGI CNR 3-4, UNN 8-14, URED 10-38 | Not achieved | Debug URED reaches 4.467 on one Colab run; full profile and held-out all-target thresholds fail |
| Colab durability: checkpoint resume, Drive persistence, CU accounting | Partial | GitHub/Colab runners and local artifact extraction work; Drive/checkpoint resume and CU accounting are not implemented |

## Task 2: Measurement-Basis Mechanism Study

| Requirement | Status | Current evidence |
|---|---|---|
| Fair protocol in `PROTOCOL.md` | Done | `PROTOCOL.md` records frame budget, throughput, channel/noise, oracle, reference overhead |
| M1 oracle/AGC/error/pairwise mechanism experiments | Partial to done | `results/mechanism_m1_protocol_o10s5` has oracle, AGC window, error propagation, pairwise failure CSVs |
| M2 phase scan over rho/sigma grid with equal frame accounting | Done for compact protocol | `results/phase_m2_reference_protocol_o10s5/phase_scan.csv` has 68,250 rows |
| M2 outputs: best methods, selected curves, flip boundary | Partial | Tables/figures generated; flip boundary is diagnostic, not R2-fitted law |
| M2 includes SCGI-network blind correction | Not done | Current M2 corrections are none/oracle/AGC/pairwise/reference |
| M3 SRHT constructive method and ablations | Partial | `results/srht_m3_protocol_o10s5` exists; M3 full claim thresholds are not all proven |
| M4 theory with fitted laws and notebook-level verification | Partial | `THEORY.md` has derivations and hooks; no dedicated N-sweep/R2 theory notebook yet |
| Published-channel calibration and nonideal detector/SLM model | Not done | No WebPlotDigitizer-derived APL/OE calibration; no shot/read/SLM quantization main scan |
| Paper outline and conservative positioning | Partial | `PAPER_OUTLINE.md` exists, but needs updating with dense M2 and remaining limitations |
| Sharded Colab scanning and merge | Done for M2 | `run_phase_m2.py --shard i/k`; `merge_phase_m2_shards.py`; shardcheck merge returns 1365 rows |

## Current Verified Commands

```powershell
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' -m unittest discover -s tests -v
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_make_figures.py
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile smoke --objects 1 --seeds 1 --shard 0/2 --no-findings --output-dir results\phase_m2_shardcheck_0of2
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' run_phase_m2.py --profile smoke --objects 1 --seeds 1 --shard 1/2 --no-findings --output-dir results\phase_m2_shardcheck_1of2
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' merge_phase_m2_shards.py --inputs results\phase_m2_shardcheck_0of2 results\phase_m2_shardcheck_1of2 --output-dir results\phase_m2_shardcheck_merged
```

## Completion Decision

The goal is not yet fully complete under the original prompt scope. The current
state is a strong executable prototype plus several completed compact protocol
experiments, but the full paper-level SCGI thresholds, M2 SCGI-network
correction, M4 fitted theory, and published/nonideal calibration remain open.
