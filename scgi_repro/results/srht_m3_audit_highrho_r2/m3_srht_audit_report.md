# M3 SRHT Ablation Audit

Raw rows: `8000`; summary rows: `160`.
Variants: `['hadamard_block_shuffle', 'hadamard_ordered', 'hadamard_time_interleave', 'perm_only', 'sign_block_shuffle', 'sign_only', 'sign_time_interleave', 'srht_full']`.
Rho values: `[0.001, 0.1, 1.0, 10.0]`; sigma_a values: `[0.3]`.

## Key Rows

| rho    | sigma_a | correction | hadamard_ordered_psnr | sign_only_psnr | sign_time_interleave_psnr | sign_block_shuffle_psnr | srht_full_psnr | srht_minus_ordered_db | best_alternative_minus_ordered_db | best_alternative     | best_ablation        |
| ------ | ------- | ---------- | --------------------- | -------------- | ------------------------- | ----------------------- | -------------- | --------------------- | --------------------------------- | -------------------- | -------------------- |
| 0.001  | 0.300   | agc        | 23.375                | 28.841         | 28.870                    | 28.861                  | 28.828         | 5.453                 | 5.495                             | sign_time_interleave | sign_time_interleave |
| 0.001  | 0.300   | none       | 24.443                | 24.589         | 24.650                    | 24.585                  | 24.593         | 0.150                 | 0.436                             | perm_only            | perm_only            |
| 0.001  | 0.300   | pairwise   | 29.314                | 29.321         | 29.327                    | 29.334                  | 29.318         | 0.005                 | 0.020                             | sign_block_shuffle   | sign_block_shuffle   |
| 0.001  | 0.300   | scgi_proxy | 28.771                | 28.822         | 28.856                    | 28.832                  | 28.804         | 0.033                 | 0.085                             | sign_time_interleave | sign_time_interleave |
| 1.000  | 0.300   | agc        | 10.902                | 11.034         | 11.042                    | 11.025                  | 10.984         | 0.083                 | 0.141                             | sign_time_interleave | sign_time_interleave |
| 1.000  | 0.300   | none       | 10.992                | 11.033         | 11.042                    | 11.023                  | 10.983         | -0.009                | 0.050                             | sign_time_interleave | sign_time_interleave |
| 1.000  | 0.300   | pairwise   | 11.043                | 11.071         | 11.078                    | 11.068                  | 11.012         | -0.031                | 0.035                             | sign_time_interleave | sign_time_interleave |
| 1.000  | 0.300   | scgi_proxy | 10.993                | 11.034         | 11.043                    | 11.027                  | 10.985         | -0.008                | 0.050                             | sign_time_interleave | sign_time_interleave |
| 10.000 | 0.300   | agc        | 10.779                | 10.876         | 10.880                    | 10.866                  | 10.816         | 0.036                 | 0.101                             | sign_time_interleave | sign_time_interleave |
| 10.000 | 0.300   | none       | 10.841                | 10.876         | 10.880                    | 10.866                  | 10.815         | -0.026                | 0.039                             | sign_time_interleave | sign_time_interleave |
| 10.000 | 0.300   | pairwise   | 10.867                | 10.891         | 10.894                    | 10.885                  | 10.824         | -0.043                | 0.027                             | sign_time_interleave | sign_time_interleave |
| 10.000 | 0.300   | scgi_proxy | 10.841                | 10.876         | 10.880                    | 10.867                  | 10.816         | -0.025                | 0.039                             | sign_time_interleave | sign_time_interleave |

## Interpretation

Oracle correction reaches minimum mean PSNR `120.000`, confirming the ablation variants are information-preserving under true gain correction.
The prompt-level constructive SRHT threshold is not met in this run: for rho>=1 and non-oracle corrections, srht_full minus ordered Hadamard ranges from `-0.043` to `0.083` dB, not the requested >=3 dB advantage.
The fallback alternatives are summarized by best_alternative_minus_ordered_db. Across fast non-oracle cells this ranges from `0.027` to `0.141` dB, with best alternatives `['sign_time_interleave']`.
The best ablation is often a signed deterministic ordering rather than full SRHT, so the current evidence supports diagonal sign randomization and paired normalization more strongly than unrestricted row permutation.
M3 should remain partial until a broader protocol shows a robust SRHT/interleaving advantage or the manuscript reframes the result as an ablation-informed design rule.
