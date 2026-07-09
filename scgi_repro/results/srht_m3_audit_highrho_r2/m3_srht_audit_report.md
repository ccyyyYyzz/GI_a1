# M3 SRHT Ablation Audit

Raw rows: `8000`; summary rows: `160`.
Variants: `['hadamard_block_shuffle', 'hadamard_ordered', 'hadamard_time_interleave', 'perm_only', 'sign_block_shuffle', 'sign_only', 'sign_time_interleave', 'srht_full']`.
Rho values: `[0.001, 0.1, 1.0, 10.0]`; sigma_a values: `[0.3]`.

## Key Rows

| rho    | sigma_a | correction | hadamard_ordered_psnr | sign_only_psnr | sign_time_interleave_psnr | sign_block_shuffle_psnr | srht_full_psnr | srht_minus_ordered_db | best_alternative_minus_ordered_db | min_recon_rel_mse | above_floor | best_alternative     | best_ablation        |
| ------ | ------- | ---------- | --------------------- | -------------- | ------------------------- | ----------------------- | -------------- | --------------------- | --------------------------------- | ----------------- | ----------- | -------------------- | -------------------- |
| 0.001  | 0.300   | agc        | 23.375                | 28.841         | 28.870                    | 28.861                  | 28.828         | 5.453                 | 5.495                             | 0.015             | True        | sign_time_interleave | sign_time_interleave |
| 0.001  | 0.300   | none       | 24.443                | 24.589         | 24.650                    | 24.585                  | 24.593         | 0.150                 | 0.436                             | 0.037             | True        | perm_only            | perm_only            |
| 0.001  | 0.300   | pairwise   | 29.314                | 29.321         | 29.327                    | 29.334                  | 29.318         | 0.005                 | 0.020                             | 0.013             | True        | sign_block_shuffle   | sign_block_shuffle   |
| 0.001  | 0.300   | scgi_proxy | 28.771                | 28.822         | 28.856                    | 28.832                  | 28.804         | 0.033                 | 0.085                             | 0.015             | True        | sign_time_interleave | sign_time_interleave |
| 0.100  | 0.300   | agc        | 12.373                | 12.858         | 12.845                    | 12.894                  | 12.850         | 0.477                 | 0.627                             | 0.572             | False       | perm_only            | perm_only            |
| 0.100  | 0.300   | none       | 12.731                | 12.797         | 12.792                    | 12.828                  | 12.788         | 0.056                 | 0.238                             | 0.576             | False       | perm_only            | perm_only            |
| 0.100  | 0.300   | pairwise   | 13.067                | 13.090         | 13.093                    | 13.140                  | 13.069         | 0.003                 | 0.074                             | 0.552             | False       | sign_block_shuffle   | sign_block_shuffle   |
| 0.100  | 0.300   | scgi_proxy | 12.789                | 12.855         | 12.846                    | 12.889                  | 12.847         | 0.059                 | 0.222                             | 0.571             | False       | perm_only            | perm_only            |
| 1.000  | 0.300   | agc        | 10.902                | 11.034         | 11.042                    | 11.025                  | 10.984         | 0.083                 | 0.141                             | 0.893             | False       | sign_time_interleave | sign_time_interleave |
| 1.000  | 0.300   | none       | 10.992                | 11.033         | 11.042                    | 11.023                  | 10.983         | -0.009                | 0.050                             | 0.893             | False       | sign_time_interleave | sign_time_interleave |
| 1.000  | 0.300   | pairwise   | 11.043                | 11.071         | 11.078                    | 11.068                  | 11.012         | -0.031                | 0.035                             | 0.886             | False       | sign_time_interleave | sign_time_interleave |
| 1.000  | 0.300   | scgi_proxy | 10.993                | 11.034         | 11.043                    | 11.027                  | 10.985         | -0.008                | 0.050                             | 0.893             | False       | sign_time_interleave | sign_time_interleave |
| 10.000 | 0.300   | agc        | 10.779                | 10.876         | 10.880                    | 10.866                  | 10.816         | 0.036                 | 0.101                             | 0.927             | False       | sign_time_interleave | sign_time_interleave |
| 10.000 | 0.300   | none       | 10.841                | 10.876         | 10.880                    | 10.866                  | 10.815         | -0.026                | 0.039                             | 0.927             | False       | sign_time_interleave | sign_time_interleave |
| 10.000 | 0.300   | pairwise   | 10.867                | 10.891         | 10.894                    | 10.885                  | 10.824         | -0.043                | 0.027                             | 0.924             | False       | sign_time_interleave | sign_time_interleave |
| 10.000 | 0.300   | scgi_proxy | 10.841                | 10.876         | 10.880                    | 10.867                  | 10.816         | -0.025                | 0.039                             | 0.927             | False       | sign_time_interleave | sign_time_interleave |

## Interpretation

Oracle correction reaches minimum mean PSNR `120.000`, confirming the ablation variants are information-preserving under true gain correction.
The reconstruction-quality gate is `rel_mse < 0.5`. Only `4` non-oracle delta rows are above-floor, and `0` of the fast rho>=1 non-oracle rows are above-floor.
In the above-floor gain-estimable AGC cell at the smallest rho, full SRHT is `5.453` dB over ordered Hadamard; row permutation alone is `5.394` dB and diagonal signs alone are `5.466` dB over ordered. This is the constructive M3 effect.
The prompt-level >=3 dB fast-drift target is not met and is the wrong target for this grid: for rho>=1 and non-oracle corrections, srht_full minus ordered Hadamard ranges from `-0.043` to `0.083` dB, while every fast row is sub-floor. The fallback best-alternative deltas `0.027` to `0.141` dB are therefore noise-floor coincidences, not effects.
M3 remains partial relative to the original fast-drift gate, but it supports the corrected design rule: sign or row randomization supplies an identifiable statistical anchor where gain is estimable, while exact inversion is retained.
