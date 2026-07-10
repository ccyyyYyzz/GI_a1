# Provenance — `tall_design_threshold_full_r1_merged`

Retroactive provenance record (audit blocker P0-7). This directory originally
shipped **without** a `run_manifest.json`; the merged CSV was produced by an
ad-hoc pandas concat that wrote no provenance. This file reconstructs the chain
and gives a byte-exact reproduction command.

## What this is

The flagship **K = 64** tall-design threshold scan (Fig. 3 / rank-transition
table). Merge of two Colab shards of `run_tall_design_threshold.py`.

| file | sha256 | data rows |
| --- | --- | --- |
| `threshold_scan.csv` | `f7a4a9a3d42bd517df38bc5ee90211d7355e3a7d8051b3ab503fe389f5d299a5` | 1300 |

## Source shards (inputs)

Generating commit **`756e628b52fd1e69e95f8e723d97891838ee7c62`** (recorded in
each shard's `artifacts/run_manifest.json` **and** `colab_job_summary.json`
`"ref"`; Colab L4, python 3.12.13, torch 2.11.0+cu128).

| shard | path | sha256 | rows | command |
| --- | --- | --- | --- | --- |
| 0/2 | `results/colab_imports/pro1_threshold_full_shard0of2_r1/artifacts/threshold_scan_shard0of2.csv` | `9ef6f1630818867c04268d86d3e5a3aacc3e1018474f8895060f6bdb50059500` | 650 | `python run_tall_design_threshold.py --output-dir results/tall_design_threshold_full_0of2 --shard 0/2` |
| 1/2 | `results/colab_imports/pro2_threshold_full_shard1of2_r1/artifacts/threshold_scan_shard1of2.csv` | `45df7cf47295d8b1deeab839c5bff281dc241477982a02ef000f75371740ed61` | 650 | `python run_tall_design_threshold.py --output-dir results/tall_design_threshold_full_1of2 --shard 1/2` |

Shard 0 holds the even `unit_index` cells (0, 2, 4, …), shard 1 the odd
(1, 3, 5, …); together they cover K=64, p∈{3,5,9,17,33}, 20 seeds, N-offsets
−8…16.

## Reproduce (byte-identical)

The published file is in **shard-arrival order** (all of shard 0, then all of
shard 1), so byte-identity requires `--order input`:

```
python merge_result_shards.py \
  --inputs results/colab_imports/pro1_threshold_full_shard0of2_r1/artifacts/threshold_scan_shard0of2.csv \
           results/colab_imports/pro2_threshold_full_shard1of2_r1/artifacts/threshold_scan_shard1of2.csv \
  --order input \
  --output results/tall_design_threshold_full_r1_merged/threshold_scan.csv
```

Verified **byte-identical** to the published `threshold_scan.csv` at current
commit `43d0a648a65994b6c5497042c65697f8a29f9490`. The default `--order sort`
(canonical key sort on `[K, p, N, offset, seed, object_kind, unit_index, shard]`)
is **content-identical** (same rows, sorted-row sha256 match) but not
byte-identical, because it reorders rows into canonical order.

## Honest gaps

- No original merge manifest existed; the merge script/commit that first wrote
  this CSV is unrecorded. Reproduction is verified at the **current** commit.
- The shard `run_manifest.json` files are **v1** (they predate manifest v2), so
  they lack the dirty-state / diff / runner-sha fingerprints v2 now records.
- Colab shard directories under `results/colab_imports/` are local-only imports;
  the `text_outputs/` and `colab_artifacts.zip` payloads are git-ignored, but the
  shard `artifacts/threshold_scan_*.csv` used above are tracked.
