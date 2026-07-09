# M3 SRHT Ablation Audit

Raw rows: `3200`; summary rows: `64`.
Rho values: `[0.001, 0.1, 1.0, 10.0]`; sigma_a values: `[0.3]`.

## Key Rows

| rho   | correction | hadamard_ordered_psnr | sign_only_psnr | srht_full_psnr | srht_minus_ordered_db | best_ablation |
| ----- | ---------- | --------------------- | -------------- | -------------- | --------------------- | ------------- |
| 0.001 | agc        | 23.375                | 28.841         | 28.828         | 5.453                 | sign_only     |
| 0.001 | none       | 24.443                | 24.589         | 24.593         | 0.150                 | perm_only     |
| 0.001 | pairwise   | 29.314                | 29.321         | 29.318         | 0.005                 | sign_only     |
| 1     | agc        | 10.902                | 11.034         | 10.984         | 0.083                 | sign_only     |
| 1     | none       | 10.992                | 11.033         | 10.983         | -0.009                | sign_only     |
| 1     | pairwise   | 11.043                | 11.071         | 11.012         | -0.031                | sign_only     |
| 10    | agc        | 10.779                | 10.876         | 10.816         | 0.036                 | sign_only     |
| 10    | none       | 10.841                | 10.876         | 10.815         | -0.026                | sign_only     |
| 10    | pairwise   | 10.867                | 10.891         | 10.824         | -0.043                | sign_only     |

## Interpretation

Oracle correction reaches minimum mean PSNR `120.000`, confirming the ablation variants are information-preserving under true gain correction.
The prompt-level constructive SRHT threshold is not met in this run: for rho>=1 and non-oracle corrections, srht_full minus ordered Hadamard ranges from `-0.043` to `0.083` dB, not the requested >=3 dB advantage.
The best ablation is often sign_only rather than srht_full, so the current evidence supports the usefulness of diagonal sign randomization but does not prove that adding row permutation is beneficial under this protocol.
M3 should remain partial until a broader protocol shows a robust SRHT advantage or the manuscript reframes the result as an ablation-informed design rule.
