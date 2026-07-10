# FIX P0-2 — Permutation-semantics mismatch and factorized whitening ablation

Date: 2026-07-10. Runner: `run_perm_ablation.py`. Results: `results/perm_ablation_r1/`
(`perm_ablation.csv`, `summary.md`, `fig_perm_ablation.png`, `run_manifest.json`).
The historical record `results/perm_whitening_power_r1/` and its runner
`run_perm_whitening_power.py` are unchanged.

## 1. The mismatch (audit claim — CONFIRMED)

Three different objects were all being called "permutation":

1. **Theory (Appendix E, assumption (E3)).** The SRHT coefficient vector is
   `x = U D P T` where **P is a uniformly random PIXEL/column permutation** of the
   object and **D = diag(η)** is an i.i.d. Rademacher **pixel sign** diagonal. Call
   these **P_col** and **D**. Lemma E.1 / Theorems E.2–E.3 characterize the
   sign-draw carrier *covariance* across Walsh rows; that covariance is a function
   of the permuted squared object `w^P` only and is **invariant to the
   acquisition row/time order**.

2. **Code SRHT (`src/basis.py::make_srht_paired_basis`, `permute_rows=True`).**
   Applies pixel signs D, but its permutation is `row_indices = randperm(size)`
   applied via `hadamard.index_select(0, row_indices)` — a **Hadamard ROW/time
   permutation (P_row)**, i.e. the order in which rows are acquired. It contains
   **no pixel/column permutation**. So the code's "SRHT" is P_row + D, not the
   theory's P_col + D.

3. **Old experiment (`run_perm_whitening_power.py`, authoritative dir
   `results/perm_whitening_power_r1`, headline 19/320 = 5.9% Levene rejections vs
   7/10 = 70% ordered).** Its single "random" arm applies **BOTH** a pixel
   permutation (`T_perm = T[pix]`) **AND** an independent row/time permutation
   (`random_paired_carrier(coeffs, row_order, …)`), with **no signs**. The 5.9%
   therefore could not be attributed to any single factor.

Additionally, Fig. 6's `perm_only` arm (`run_srht_m3.py::make_variant`) is a
**row/time permutation only** — not Appendix E's P_col — and its `srht_full` arm
is P_row + D. **No Fig. 6 arm realizes the P_col of the SRHT theorem.**

## 2. What we ran

`run_perm_ablation.py` factorizes the randomization into arms over
{P_col pixel-perm, D pixel-signs, P_row row/time-perm}, every arm applied to the
SAME ordered natural-Hadamard baseline (K = 4096, 64×64, 8192 paired frames,
noiseless carrier) and the SAME 10-object panel and Brown–Forsythe (Levene,
8 chunks, reject at p < 1e-3) protocol as the old runner. 32 independent draws
per randomized arm; pixel/row draws reuse the old runner's exact seed formulas
(`seed+101·i` / `seed+977·i`, seed 20240708), signs use a new stream
(`seed+613·i`). Carrier construction was verified once per run against an
explicit `interleave_paired_frames` measurement of the real signed Hadamard
basis (max abs diff 2.8e-14).

## 3. Per-arm results (results/perm_ablation_r1)

| arm | P_col | D | P_row | reject n/N | rate | mean Walsh peak | mean chunk-std CV |
|-----|:-----:|:--:|:-----:|:----------:|:----:|:----:|:----:|
| `ordered` | – | – | – | 7/10 | **0.700** | 0.890 | 0.758 |
| `row_perm_only` | – | – | Y | 39/320 | **0.122** | 0.890 | 0.535 |
| `pixel_perm_only` (theory's P) | Y | – | – | 18/320 | **0.056** | 0.147 | 0.275 |
| `sign_only` (theory's D) | – | Y | – | 139/320 | **0.434** | 0.890 | 0.039 |
| `pixel_sign` (theory's P+D) | Y | Y | – | 38/320 | **0.119** | 0.147 | 0.029 |
| `row_pixel` (old runner) | Y | – | Y | 19/320 | **0.059** | 0.147 | 0.275 |
| `row_pixel_sign` | Y | Y | Y | 23/320 | **0.072** | 0.147 | 0.028 |
| `row_sign` (code's srht_paired) | – | Y | Y | 19/320 | **0.059** | 0.890 | 0.028 |

Consistency check: the `row_pixel` arm reproduces the old headline **exactly**
(19/320 = 5.9%), confirming the seed-compatible reconstruction of the old
experiment.

## 4. Attribution

- **The theory's own randomization is sufficient.** P_col + D (`pixel_sign`,
  natural acquisition order) passes the Levene stationarity screen on its own:
  11.9% ≤ 15% ceiling. Appendix E's claims do not depend on the row-order
  confound.
- **Either permutation alone is sufficient; signs alone are not.** P_col alone
  gives 5.6% (the strongest single factor), P_row alone 12.2%, but D alone gives
  43.4% — sign flips randomize carrier *amplitudes* (chunk-std CV collapses from
  0.76 to 0.04) yet leave the temporal ordering of the natural-Hadamard sequency
  structure intact, so the Levene chunk test still often rejects.
- **Two distinct "whitenings" were conflated.** Appendix E's theorems govern
  cross-row carrier *covariance* (row-order invariant, driven by P_col and D);
  the Levene test probes *temporal* stationarity of the acquired time series
  (driven by P_col or P_row — anything that breaks the coarse-to-fine energy
  ordering of natural Hadamard rows). The old runner's 5.9% is a temporal-
  stationarity result that happens to be achievable by either mechanism; the
  factorized numbers now let each claim cite its own arm.
- Small honest wrinkle: adding D on top of P_col slightly *raises* the Levene
  rejection rate (5.6% → 11.9%). Signs make the carrier nearly white, so the
  variance-homogeneity test becomes sensitive to residual local-variance
  fluctuations; this is a property of the test, not a whitening failure, but
  captions should quote the arm they actually mean.

## 5. Caption-ready sentences (P_col vs P_row)

Use `P_col` (pixel/column permutation of the object, Appendix E's P) and
`P_row` (acquisition row/time reordering of Hadamard patterns) explicitly:

- *For Fig. 6 / `run_srht_m3.py`:* "The `perm_only` arm permutes the Hadamard
  **row (acquisition/time) order** (P_row) and applies no pixel-level
  randomization; the `sign_only` arm applies i.i.d. Rademacher **pixel sign
  flips** (D) in natural row order; the `srht_full` arm combines P_row with D.
  None of these arms permutes pixel indices, so none realizes the column
  permutation P_col of the SRHT analysis in Appendix E; the factorized ablation
  (results/perm_ablation_r1) shows the corresponding P_col arms separately."
- *For the old Experiment B result:* "The randomized arm of
  `run_perm_whitening_power.py` applied a pixel permutation P_col **and** an
  independent row/time permutation P_row simultaneously (no sign flips); its
  19/320 = 5.9% rejection rate is reproduced exactly by the factorized
  `row_pixel` arm, and is attributable to either factor alone
  (P_col-only: 5.6%; P_row-only: 12.2%)."
- *For the theory link:* "Appendix E's SRHT randomization x = U D P_col T —
  pixel sign flips plus pixel permutation, with natural acquisition order —
  passes the same stationarity screen on its own (38/320 = 11.9% Levene
  rejections vs 70% ordered), so the whitening claim attaches to the theory's
  randomization and not to the temporal reordering; note that the Levene screen
  probes temporal stationarity, whereas Lemma E.1 governs cross-row covariance,
  which is invariant to acquisition order."
- *For the code SRHT:* "`make_srht_paired_basis` implements P_row + D (row-order
  shuffle plus pixel signs), not the theory's P_col + D; empirically both
  combinations pass the stationarity screen (5.9% and 11.9%), but text and
  captions must not present the code's basis as the literal Appendix E
  construction."

## 6. Fig. 6 arm decode (mechanics of `run_srht_m3.py::make_variant`)

`h = hadamard_matrix(p)`; `signs` = length-p Rademacher; `perm = randperm(p)`
is a **row-index** permutation; rows are `h.index_select(0, row_indices)` and,
when `use_signs`, multiplied columnwise by `signs` (pixel signs D). All arms
paired via `interleave_paired_frames`. No arm permutes pixel columns.

| Fig. 6 variant | row/time order | D | P_col | = ablation arm |
|---|---|:--:|:--:|---|
| `hadamard_ordered` | natural | – | – | `ordered` |
| `perm_only` | full random ROW perm | – | – | `row_perm_only` |
| `sign_only` | natural | Y | – | `sign_only` |
| `srht_full` | full random ROW perm | Y | – | `row_sign` |
| `hadamard_time_interleave` | block round-robin interleave | – | – | deterministic P_row variant |
| `sign_time_interleave` | block round-robin interleave | Y | – | interleave + D |
| `hadamard_block_shuffle` | within-block ROW shuffle | – | – | block P_row variant |
| `sign_block_shuffle` | within-block ROW shuffle | Y | – | block P_row + D |
