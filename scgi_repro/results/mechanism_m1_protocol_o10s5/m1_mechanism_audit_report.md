# M1 Mechanism Audit

This audit reads the o10s5 M1 protocol CSVs and summarizes the four
mechanism checks: oracle gain correction, blind AGC error, synthetic
residual-gain propagation, and pairwise-normalization failure curves.

## Manifest

| file                               | rows |
| ---------------------------------- | ---- |
| mechanism_m1_oracle_agc.csv        | 4200 |
| mechanism_m1_agc_window_sweep.csv  | 1750 |
| mechanism_m1_error_propagation.csv | 1750 |
| mechanism_m1_error_scaling_fit.csv | 7    |
| mechanism_m1_pairwise_failure.csv  | 5400 |
| mechanism_m1_summary.csv           | 262  |

## Oracle And AGC At Fastest Rho

| basis            | correction | psnr_mean | gain_rel_mse_mean |
| ---------------- | ---------- | --------- | ----------------- |
| dct_paired       | agc        | 18.88     | 0.0074            |
| dct_paired       | none       | 21.34     | nan               |
| dct_paired       | oracle     | 101.3     | 0                 |
| fourier_fourstep | agc        | 18.28     | 0.0074            |
| fourier_fourstep | none       | 17.8      | nan               |
| fourier_fourstep | oracle     | 20.15     | 0                 |
| hadamard_paired  | agc        | 21.15     | 0.0074            |
| hadamard_paired  | none       | 23.91     | nan               |
| hadamard_paired  | oracle     | 120       | 0                 |
| random_binary    | agc        | 13.36     | 0.0042            |
| random_binary    | none       | 12.47     | nan               |
| random_binary    | oracle     | 15.39     | 0                 |
| random_gaussian  | agc        | 15.33     | 0.0096            |
| random_gaussian  | none       | 15.33     | nan               |
| random_gaussian  | oracle     | 15.36     | 0                 |
| random_uniform   | agc        | 12.08     | 0.0041            |
| random_uniform   | none       | 11.38     | nan               |
| random_uniform   | oracle     | 15.39     | 0                 |
| srht_paired      | agc        | 24.05     | 0.0041            |
| srht_paired      | none       | 23.53     | nan               |
| srht_paired      | oracle     | 120       | 0                 |

## Oracle Floor

| basis            | oracle_min_psnr | oracle_mean_psnr | oracle_max_gain_rel_mse |
| ---------------- | --------------- | ---------------- | ----------------------- |
| dct_paired       | 101.3           | 101.3            | 0                       |
| fourier_fourstep | 20.15           | 20.15            | 0                       |
| hadamard_paired  | 120             | 120              | 0                       |
| random_binary    | 15.39           | 15.39            | 0                       |
| random_gaussian  | 15.36           | 15.36            | 0                       |
| random_uniform   | 15.39           | 15.39            | 0                       |
| srht_paired      | 120             | 120              | 0                       |

## Blind AGC Error

| basis            | agc_psnr_mean | agc_gain_rel_mse_mean | agc_gain_rel_mse_min | agc_gain_rel_mse_max |
| ---------------- | ------------- | --------------------- | -------------------- | -------------------- |
| srht_paired      | 31.17         | 0.00161               | 0.00018              | 0.00414              |
| random_uniform   | 13.64         | 0.00161               | 0.00018              | 0.00414              |
| random_binary    | 14.46         | 0.00164               | 0.00021              | 0.00417              |
| hadamard_paired  | 23.41         | 0.00479               | 0.0033               | 0.00739              |
| fourier_fourstep | 21.76         | 0.00479               | 0.00331              | 0.00739              |
| dct_paired       | 21.8          | 0.0048                | 0.00331              | 0.00739              |
| random_gaussian  | 15.34         | 0.00698               | 0.00549              | 0.00962              |

## Residual Gain Error Scaling

| basis            | slope  | intercept | r2     | points |
| ---------------- | ------ | --------- | ------ | ------ |
| dct_paired       | 0.9336 | 0.7276    | 0.9129 | 4      |
| fourier_fourstep | 0.7491 | 0.5148    | 0.9792 | 4      |
| hadamard_paired  | 1.182  | 0.8681    | 0.9461 | 4      |
| random_binary    | 0.3947 | 0.2061    | 0.9887 | 4      |
| random_gaussian  | 0.0103 | -0.4648   | 0.7626 | 4      |
| random_uniform   | 0.3822 | 0.2711    | 0.9726 | 4      |
| srht_paired      | 1.179  | 0.8654    | 0.9462 | 4      |

## Pairwise Normalization Range

| basis           | pairwise_min_psnr | pairwise_max_psnr |
| --------------- | ----------------- | ----------------- |
| dct_paired      | 18.21             | 41.7              |
| hadamard_paired | 20.85             | 44.72             |
| srht_paired     | 20.86             | 44.73             |

## Interpretation

Oracle correction restores the complete paired Hadamard/SRHT variants
to exact or near-exact reconstruction, supporting the identifiability
interpretation that the measurements still contain the object when true
gains are known. The AGC and residual-error tables remain compact
protocol evidence rather than final paper-grade figures, but they now
provide concrete o10s5 artifacts for M1 instead of relying on stale
documentation references.
