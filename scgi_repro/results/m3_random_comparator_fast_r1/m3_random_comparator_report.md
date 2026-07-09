# M3 Random Comparator Audit

Raw rows: `3600`; summary rows: `72`.
Rho values: `[1.0, 10.0]`; sigma_a values: `[0.3, 0.5]`.

## Best Blind Deltas

| rho | sigma_a | srht_best_correction | srht_best_psnr | srht_best_rel_mse | ordered_best_correction | ordered_best_psnr | ordered_best_rel_mse | best_random_variant | best_random_correction | best_random_psnr | best_random_rel_mse | srht_minus_ordered_db | srht_minus_best_random_db | srht_gap_to_best_srht_ablation_db | best_srht_ablation | min_recon_rel_mse | above_floor | above_floor_rel_mse |
| --- | ------- | -------------------- | -------------- | ----------------- | ----------------------- | ----------------- | -------------------- | ------------------- | ---------------------- | ---------------- | ------------------- | --------------------- | ------------------------- | --------------------------------- | ------------------ | ----------------- | ----------- | ------------------- |
| 1   | 0.3     | pairwise             | 11.033         | 0.895             | pairwise                | 11.042            | 0.8928               | random_binary       | none                   | 10.843           | 0.935               | -0.009                | 0.190                     | -0.013                            | sign_only          | 0.893             | False       | 0.5                 |
| 1   | 0.5     | pairwise             | 10.730         | 0.9592            | pairwise                | 10.738            | 0.9574               | random_binary       | none                   | 10.649           | 0.977               | -0.008                | 0.082                     | -0.008                            | sign_only          | 0.957             | False       | 0.5                 |
| 10  | 0.3     | pairwise             | 10.865         | 0.93              | pairwise                | 10.868            | 0.9292               | random_binary       | none                   | 10.845           | 0.934               | -0.003                | 0.020                     | -0.014                            | sign_only          | 0.929             | False       | 0.5                 |
| 10  | 0.5     | pairwise             | 10.667         | 0.9733            | pairwise                | 10.670            | 0.9725               | random_binary       | none                   | 10.650           | 0.977               | -0.004                | 0.016                     | -0.009                            | sign_only          | 0.973             | False       | 0.5                 |

## Interpretation

This audit closes the direct-random-comparator gap in the M3 ablation, but all rows are fast-drift rows and should be read through the reconstruction-floor mask.
With the default rel_mse<0.5 gate, `0` rows are above-floor and `4` rows are sub-floor.
The small SRHT-vs-random deltas in this table narrow the estimator caveat; they do not create an above-floor fast-drift effect or rescue the original >=3 dB fast-drift gate.
