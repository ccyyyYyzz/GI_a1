# Protocol Audit Report

This report audits comparison mechanics only. It does not claim that a basis wins.

## Scope

- Audited strict bases: 10
- Audited object rows: 10
- Reference periods: 0, 2, 8, 32
- Total physical frame range with reference overhead: 2048 to 3073

## Key Checks

- `num_frames`, `num_coefficients`, `num_pixels`, `reference_frames`, and `total_physical_frames` are explicit in `protocol_audit.csv`.
- Pairwise complementary bases report complement-sum error; complete paired bases should be near zero.
- Throughput proxies are exposed as per-frame mean, sum, L2 norm, and energy statistics.
- `random_gaussian` is included as a signed mathematical control and is labeled non-optical because it contains negative entries.
- Object generation is documented as deterministic synthetic digit/shape/line images, not MNIST or natural images.

## Files

- `protocol_audit.csv`: basis/frame/reference/throughput audit.
- `object_audit.csv`: object-family and image-statistics audit.
- `seed_split_audit.csv`: seed and split conventions used by compact mechanism runners.
- `protocol_audit_summary.json`: compact machine-readable summary.
