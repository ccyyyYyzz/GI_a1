# Authoritative M2 dense winner table (recount, audit fix P0-4)

Source: `results/m2_hadamard_order_dense_r1_merged/phase_scan.csv` (155,250 rows;
10 objects x 5 seeds x 9 rho x 5 sigma_a; N = 2048 frames, K = 1024 pixels).
Recomputed independently of `run_m2_boundary_audit.py` by `run_prop3_boundary.py`
(same declared criteria: winner = highest mean PSNR among candidates with
`rel_mse_mean < 0.5`; cells with no above-floor candidate = noise floor).
Per-cell table: `winner_table_cells.csv`.

## Definitive counts

| scope | total cells | above-floor | noise floor | winners |
|---|---|---|---|---|
| equal_frame_non_oracle | **45** | **29** | **16** | srht_paired+pairwise **28**, hadamard_random_paired+scgi_proxy **1** (rho=0.3, sigma=0.15) |
| all_non_oracle | 45 | 31 | 14 | srht_paired+reference_k2 31 |

The manuscript's "wins all 28 above-floor cells of the 44-cell winner map ...
the remaining 16 cells" is arithmetically inconsistent (28+16=44 but the grid is
9x5=45) and factually wrong on two counts: there are **29** above-floor cells,
and SRHT-paired+pairwise wins **28 of 29**, not all.

## Equal-frame winner map (9 rho x 5 sigma_a)

| sigma_a \ rho | 0.001 | 0.003 | 0.01 | 0.03 | 0.1 | 0.3 | 1.0 | 3.0 | 10.0 |
|---|---|---|---|---|---|---|---|---|---|
| 0.05 | SRHT | SRHT | SRHT | SRHT | SRHT | SRHT | SRHT | SRHT | SRHT |
| 0.10 | SRHT | SRHT | SRHT | SRHT | SRHT | SRHT | SRHT | floor | floor |
| 0.15 | SRHT | SRHT | SRHT | SRHT | SRHT | **HRP** | floor | floor | floor |
| 0.30 | SRHT | SRHT | SRHT | SRHT | floor | floor | floor | floor | floor |
| 0.50 | SRHT | SRHT | SRHT | floor | floor | floor | floor | floor | floor |

SRHT = srht_paired + pairwise; HRP = hadamard_random_paired + scgi_proxy
(PSNR 13.86 dB, relMSE 0.468 — barely above the 0.5 gate); floor = no candidate
with relMSE < 0.5.

## All-non-oracle winner map

srht_paired + reference_k2 wins every above-floor cell (31); the noise-floor
region is the same lower-right wedge minus (0.1, 0.5) and (0.3, 0.3) which the
reference-frame arm keeps above floor. Reference arms use 3073 physical frames
vs 2048, so this scope is not budget-matched.

## Notes

- Winner-map cells across both scopes: 90, of which 60 above-floor / 30 floor
  (matches the published audit report's accounting).
- Pairwise challenger-vs-Hadamard comparison cells (within-correction strata):
  1440, of which 914 above-floor (matches the published audit report).
- No cell in either scope is won by ordered pairwise Hadamard or by bare
  random+DGI (any correction).
