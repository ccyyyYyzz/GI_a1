# Targeted M4 AGC Window Validation

This run uses a wider, denser window grid than the paper-r2 diagnostic
to test whether the candidate AGC bias-variance law is supported away
from sampled window-grid boundaries.

## Boundary Saturation

| basis           | lower_bound | interior | upper_bound | total_cells | interior_frac | boundary_frac |
| --------------- | ----------- | -------- | ----------- | ----------- | ------------- | ------------- |
| hadamard_paired | 25          | 20       | 0           | 45          | 0.4444        | 0.5556        |
| random_binary   | 19          | 26       | 0           | 45          | 0.5778        | 0.4222        |
| random_uniform  | 25          | 20       | 0           | 45          | 0.4444        | 0.5556        |
| srht_paired     | 25          | 20       | 0           | 45          | 0.4444        | 0.5556        |

## Log-Linear Fits

| basis           | rho_exponent | sigma_a_exponent | r2     | rmse_log10 | n  |
| --------------- | ------------ | ---------------- | ------ | ---------- | -- |
| hadamard_paired | -0.06654     | -0.09899         | 0.7068 | 0.05969    | 45 |
| random_binary   | -0.2955      | -0.6408          | 0.8209 | 0.2069     | 45 |
| random_uniform  | -0.2306      | -0.4847          | 0.7487 | 0.1987     | 45 |
| srht_paired     | -0.1786      | -0.3346          | 0.7866 | 0.1348     | 45 |

## Interpretation

A useful scaling law should have most best-window selections in the
interior of the sampled grid and stable exponents across bases.
Boundary-heavy selections indicate that the estimator or basis still
prefers the smallest/largest tested window, so the fitted law should
be treated as diagnostic rather than publication-ready.
