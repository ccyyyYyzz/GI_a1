# Experiment B2 -- Factorized whitening ablation (P0-2 audit fix)

K=4096 (64x64), num_frames=8192, chunks=8, nperm=32, reject at Brown-Forsythe (Levene) p<0.001.
Noiseless paired-Hadamard carrier; Levene metric identical to Fig. 2 r2b (run_paper_fig2_stationarity.stationarity_metrics).

## Per-arm Levene non-stationarity rejection

| arm | P_col pixel | D signs | P_row time | reject n/N | rate | mean Walsh peak | mean chunk-std CV |
|-----|:-----------:|:-------:|:----------:|:----------:|:----:|:---------------:|:-----------------:|
| `ordered` | - | - | - | 7/10 | 0.700 | 0.8899 | 0.7578 |
| `row_perm_only` | - | - | Y | 39/320 | 0.122 | 0.8899 | 0.5345 |
| `pixel_perm_only` | Y | - | - | 18/320 | 0.056 | 0.1468 | 0.2747 |
| `sign_only` | - | Y | - | 139/320 | 0.434 | 0.8899 | 0.0386 |
| `pixel_sign` | Y | Y | - | 38/320 | 0.119 | 0.1468 | 0.0293 |
| `row_pixel` | Y | - | Y | 19/320 | 0.059 | 0.1468 | 0.2752 |
| `row_pixel_sign` | Y | Y | Y | 23/320 | 0.072 | 0.1468 | 0.0276 |
| `row_sign` | - | Y | Y | 19/320 | 0.059 | 0.8899 | 0.0275 |

## Attribution

- `ordered` baseline rejects at rate 0.700 (high non-stationarity, as expected).
- `row_perm_only` (P_row alone): rate 0.122 -> SUFFICIENT (low, <=0.15).
- `pixel_perm_only` (P_col alone, Appendix E's P): rate 0.056 -> SUFFICIENT (low, <=0.15).
- `sign_only` (D alone, Appendix E's signs): rate 0.434 -> PARTIAL.
- `pixel_sign` (P_col + D = THE THEORY's SRHT randomization, natural row order): rate 0.119 -> SUFFICIENT (low, <=0.15).
- `row_pixel` (what the OLD run_perm_whitening_power.py did): rate 0.059.
- `row_sign` (what the CODE's srht_paired basis does: P_row + D): rate 0.059 -> SUFFICIENT (low, <=0.15).
- `row_pixel_sign` (everything): rate 0.072.

**Sufficient single/theory factors (rate <=0.15): row/time permutation (P_row) alone; pixel permutation (P_col) alone; the theory's P_col+D (pixel_sign) alone.**

**Theory-vs-experiment finding:** the manuscript's SRHT randomization is P_col+D (`pixel_sign`, natural row order), which rejects at 0.119. This IS sufficient for carrier stationarity on its own.

Note (theory scope): Appendix E (Lemma E.1, Thm E.2/E.3) characterizes the sign-draw carrier *covariance* across Walsh rows -- a function of the PERMUTED SQUARED object w^P only, invariant to the acquisition row/time order. The Levene test here probes TEMPORAL stationarity of the carrier as an acquired time series, which the row/time order (P_row) controls directly. The two notions of 'whitening' are distinct; the old runner conflated them.

## Fig. 6 arm decode (run_srht_m3.py `make_variant`) -- caption-ready mechanics

In `run_srht_m3.py`, `h = hadamard_matrix(p)`; `signs` is a length-p Rademacher vector; `perm = randperm(p)` is a **row-index** permutation; measurement rows are `rows = h.index_select(0, row_indices)` and, when `use_signs`, `rows = rows * signs.reshape(1, -1)` which multiplies each **column (pixel)** by a sign. There is **no pixel/column permutation in any Fig. 6 arm.** All arms are paired (`interleave_paired_frames`). Concretely:

| Fig. 6 variant | row/time order | pixel signs D | pixel perm P_col | = which ablation arm |
|----------------|----------------|:-------------:|:----------------:|----------------------|
| `hadamard_ordered` | natural | - | - | `ordered` |
| `perm_only` | full random ROW permutation | - | - | `row_perm_only` (NOT pixel perm) |
| `sign_only` | natural | Y | - | `sign_only` |
| `srht_full` | full random ROW permutation | Y | - | `row_sign` (NOT theory's P_col+D) |
| `hadamard_time_interleave` | block round-robin interleave | - | - | (deterministic P_row variant) |
| `sign_time_interleave` | block round-robin interleave | Y | - | (interleave + D) |
| `hadamard_block_shuffle` | within-block ROW shuffle | - | - | (block P_row variant) |
| `sign_block_shuffle` | within-block ROW shuffle | Y | - | (block P_row + D) |

Caption correction: Fig. 6 `perm_only` is a **row/time-order** permutation of the Hadamard patterns, NOT the pixel/column permutation P of Appendix E; and `srht_full` is **row-permutation + pixel signs** (P_row + D), NOT the theory's SRHT `x = U D P_col T`. No Fig. 6 arm realizes the P_col of the SRHT theorem.
