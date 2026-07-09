# Boundary-Aware M4 AGC Analysis

The targeted AGC sweep often selects the smallest sampled window. This
analysis treats those selections as censored observations rather than
exact optima: a lower-bound grid hit means the true optimum is at or
below the sampled minimum, while an interior hit remains an exact
best-window observation.

## Censored Power-Law Fits

| basis           | n_total | n_exact | n_upper_bounded | rho_exponent | sigma_a_exponent | hinge_rmse_log10 | interval_satisfaction_frac | bounded_inequality_satisfied_frac | interior_fit_r2 |
| --------------- | ------- | ------- | --------------- | ------------ | ---------------- | ---------------- | -------------------------- | --------------------------------- | --------------- |
| hadamard_paired | 45      | 20      | 25              | -0.07654     | -0.119           | 0.05404          | 0.4                        | 0.56                              | nan             |
| random_binary   | 45      | 26      | 19              | -0.4371      | -1.024           | 0.1005           | 0.8                        | 0.8421                            | 0.9133          |
| random_uniform  | 45      | 20      | 25              | -0.479       | -0.9967          | 0.02864          | 0.8                        | 1                                 | 0.9861          |
| srht_paired     | 45      | 20      | 25              | -0.3145      | -0.5997          | 0.04236          | 0.6444                     | 0.8                               | 0.9497          |

## Interpretation

High interval satisfaction with many bounded points supports a weaker
claim than an exact best-window law: the data identify a feasible
window region and confirm boundary pressure, but do not pin down a
unique optimum in boundary-dominated cells. The satisfaction fraction
uses exact-point tolerance and bounded-point hinge inequalities; it is
not a statistical coverage probability.

## Censor Counts

| basis           | exact | upper_bounded |
| --------------- | ----- | ------------- |
| hadamard_paired | 20    | 25            |
| random_binary   | 26    | 19            |
| random_uniform  | 20    | 25            |
| srht_paired     | 20    | 25            |
