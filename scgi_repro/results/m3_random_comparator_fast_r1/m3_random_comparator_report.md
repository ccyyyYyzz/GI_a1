# M3 Random Comparator Audit

Raw rows: `3600`; summary rows: `72`.
Rho values: `[1.0, 10.0]`; sigma_a values: `[0.3, 0.5]`.

## Best Blind Deltas

| rho | sigma_a | srht_best_correction | srht_best_psnr | ordered_best_correction | ordered_best_psnr | best_random_variant | best_random_correction | best_random_psnr | srht_minus_ordered_db | srht_minus_best_random_db | srht_gap_to_best_srht_ablation_db | best_srht_ablation |
| --- | ------- | -------------------- | -------------- | ----------------------- | ----------------- | ------------------- | ---------------------- | ---------------- | --------------------- | ------------------------- | --------------------------------- | ------------------ |
| 1   | 0.3     | pairwise             | 11.033         | pairwise                | 11.042            | random_binary       | none                   | 10.843           | -0.009                | 0.190                     | -0.013                            | sign_only          |
| 1   | 0.5     | pairwise             | 10.730         | pairwise                | 10.738            | random_binary       | none                   | 10.649           | -0.008                | 0.082                     | -0.008                            | sign_only          |
| 10  | 0.3     | pairwise             | 10.865         | pairwise                | 10.868            | random_binary       | none                   | 10.845           | -0.003                | 0.020                     | -0.014                            | sign_only          |
| 10  | 0.5     | pairwise             | 10.667         | pairwise                | 10.670            | random_binary       | none                   | 10.650           | -0.004                | 0.016                     | -0.009                            | sign_only          |

## Interpretation

This audit closes the direct-random-comparator gap in the M3 ablation.
It compares the best non-oracle correction for full SRHT against ordered
Hadamard and the best random basis under the same object/seed/rho/sigma
cells. The strong prompt gate still requires a robust >=3 dB fast-drift
advantage over ordered Hadamard and no more than a 1 dB loss versus
random bases; these fields are reported directly in the delta table.
