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
