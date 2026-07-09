# Paper-Driven Experiment Status

Target prompt:

`C:\Users\CYZ的computer\AppData\Roaming\Claude\local-agent-mode-sessions\79b20112-b255-407d-b0f8-2272b141ced6\61f2a993-86ee-4a33-a62e-d1124f40226c\local_0a992d9a-cc55-4ef9-811a-fade264e6b76\outputs\论文驱动实验计划_给执行agent.md`

Branch:

`scgi-ceiling-diagnostic-r1`

Review entry points:

- `src/paper_experiments.py`
- `run_paper_fig2_stationarity.py`
- `run_paper_fig3_gain_error.py`
- `merge_paper_fig3_gain_error.py`
- `run_paper_fig4_bridge.py`
- `run_paper_fig7_lowphoton.py`
- `launch_colab_paper_fig_jobs.sh`

## Main Outputs

| Figure task | Output directory | Key CSV | Rows | Status |
| --- | --- | --- | ---: | --- |
| Fig. 2 carrier stationarity | `results/paper_fig2_stationarity_r1` | `fig2_stationarity.csv` | 50 | complete, local |
| Fig. 3 blind gain error | `results/paper_fig3_gain_error_merged_r1` | `fig3_gain_est_error.csv` | 4500 | complete, Colab shards merged |
| Fig. 4 reconstruction bridge | `results/paper_fig4_bridge_r1` | `fig4_bridge.csv` | 1250 | complete, local rerun |
| Fig. 7 low-photon soft log | `results/paper_fig7_lowphoton_r1` | `fig7_lowphoton.csv` | 1500 | complete, Colab artifact copied to main result dir |

## Colab Runs

| Run id | Account | Accelerator | Main result | Status |
| --- | --- | --- | --- | --- |
| `pro1_fig3_rho1e3_random_r2` | pro1 | L4 | Fig. 3 rho=1e-3 random/SRHT shard, 1350 rows | success |
| `pro2_fig3_rho1e3_hadamard_r1_retry4` | pro2 | L4 | Fig. 3 rho=1e-3 Hadamard shard, 900 rows | success |
| `pro1_fig3_rho1e2_all_r3` | pro1 | L4 | Fig. 3 rho=1e-2 all-basis shard, 2250 rows | success |
| `pro2_fig7_lowphoton_r2` | pro2 | L4 | Fig. 7 low-photon sweep, 1500 rows | success |
| `pro2_fig4_bridge_r3` | pro2 | L4 | command reported 1250 rows, but zip contained only status | not used as main data |

No active Colab sessions remained after `pro2_fig3_rho1e3_hadamard_r1_retry4`.

## Fig. 3 Slope Check

Merged Fig. 3 row count is 4500 with no duplicate `(object, basis, rho, s, seed, W)` keys.

Mean fitted slopes over objects using `W <= 32`:

| rho | basis | mean slope |
| ---: | --- | ---: |
| 0.001 | random_uniform | -0.314 |
| 0.001 | random_binary | -0.380 |
| 0.001 | srht_paired | -0.375 |
| 0.001 | hadamard_random_paired | -0.399 |
| 0.001 | hadamard_paired | 0.062 |
| 0.010 | random_uniform | -0.019 |
| 0.010 | random_binary | -0.172 |
| 0.010 | srht_paired | 0.051 |
| 0.010 | hadamard_random_paired | 0.034 |
| 0.010 | hadamard_paired | 0.156 |

The rho=1e-3 early-window regime shows the intended diagnostic separation: random/SRHT-like bases reduce error with window size, while ordered Hadamard does not.

## Caveats

This status closes the new paper-driven mechanism-figure target, not the earlier strict SCGI reproduction target. The earlier strict reproduction remains partial/blocked because learned SCGI/UNN/URED thresholds did not match the original paper gates.

The Fig. 4 Colab command finished, but the runner zip omitted the CSV/figures. The main Fig. 4 result therefore comes from a local rerun of the same runner parameters, which completed in 7.18 seconds and produced the expected 1250 rows.

## r2 revision round (2026-07-09, post-verification)

Adversarial numerical verification of the r1 figure sets led to an r2 revision implementing:
Fig. 3: honest arm renaming (hadamard_paired / hadamard_random_paired) + two NEW raw non-paired
Hadamard arms (raw_ordered error ~0.96 non-decaying = the chronology failure; raw_shuffled ~0.86),
theory-floor-normalized collapse (err/floor collapses across objects to +/-5-7%), adaptive
variance-segment slope fits (random_binary -0.39, srht -0.60, hadamard_random_paired -0.61),
per-seed drift resampling. VERDICT: PASS (results/paper_fig3_gain_error_r2, 6100 rows).
Fig. 2: variance-sensitive stationarity metrics (Brown-Forsythe levene_p, KS on |B-local mean|,
std-envelope CV), DC-transient exclusion (frames>=128). r2b power increase (8192 frames):
ordered arm rejects 7/10 at p<1e-3 (min 1e-20) vs 0/10 for iid random arms; permuted arms 2/10
(probabilistic permutation whitening, theory-consistent). (paper_fig2_stationarity_r2 + _r2b)
Fig. 4: control-arm N sweep + v=0 rows + C0_measured; r2b seed increase (15 seeds, 8100 rows):
orthogonal max per-v |slope|=0.074 (<0.1), srht 0.014, random_dgi ~ -1.0; leverage*N 7.4-7.7e5.
DGI's correct constant is leverage*N (v=0 floor is identically 0 by residual construction).
(paper_fig4_bridge_r2 + _r2b)
Fig. 7: manifest/caption Fisher slopes recomputed from committed CSV (-0.910 for lambda in
[2,32], -0.730 for [1,16]; root cause: endpoint-dropping filter bug); ratio claims split
(soft-log 23-46x, Anscombe 19.5-30x); floorprobe confirms drift-limited high-photon floor
(2.78e-4 -> 1.73e-4 at rho=1e-4). (paper_fig7_lowphoton_r2)

Paper draft: paper_draft/MANUSCRIPT_DRAFT.md (sections 1-8+10 assembled; section 9 + abstract
pending, to be written from the verified numbers) + paper_draft/REVIEW_FLAGS.md.
