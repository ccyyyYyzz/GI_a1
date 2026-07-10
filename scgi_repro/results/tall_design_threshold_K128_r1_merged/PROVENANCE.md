# Provenance — `tall_design_threshold_K128_r1_merged`

Retroactive provenance record (audit blocker P0-7). This directory originally
shipped **without** a `run_manifest.json`. This file reconstructs the chain and
gives a byte-exact reproduction command.

## What this is

The flagship **K = 128** tall-design threshold scan (the second rank-transition
replicate; demonstrates the N = K + p − 1 transition holds at K = 128 as well as
K = 64). Merge of two Colab shards of `run_tall_design_threshold.py` run with
`--K 128 --seeds 30`.

| file | sha256 | data rows |
| --- | --- | --- |
| `threshold_scan.csv` | `8ed9270566cc82b53587dc313ffa0f0888cd26f2f5a425b6c16a540cb33d8300` | 1950 |

## Source shards (inputs)

Generating commit **`3382ee9bd95103893a24d9ca5dfeefe69b065852`** (recorded in
each shard's `artifacts/run_manifest.json` and `colab_job_summary.json` `"ref"`).

| shard | path | sha256 | rows | command |
| --- | --- | --- | --- | --- |
| 0/2 | `results/colab_imports/pro1_threshold_K128_shard0/artifacts/threshold_scan_shard0of2.csv` | `deb9bc259890c13d49ff06ecc25b7685be1aed5b021d7bc4acaf2af93097a439` | 975 | `python run_tall_design_threshold.py --output-dir results/tall_design_threshold_K128_0of2 --K 128 --seeds 30 --shard 0/2` |
| 1/2 | `results/colab_imports/pro2_threshold_K128_shard1/artifacts/threshold_scan_shard1of2.csv` | `2a11f5f497b8acb8cb30be22b9bfd3049b0a40004c0ab71074451b00e4678b76` | 975 | `python run_tall_design_threshold.py --output-dir results/tall_design_threshold_K128_1of2 --K 128 --seeds 30 --shard 1/2` |

Covers K=128, p∈{3,5,9,17,33}, 30 seeds, N-offsets −8…16; shard 0 = even
`unit_index`, shard 1 = odd.

## Reproduce (byte-identical)

Published file is in shard-arrival order (shard 0 block, then shard 1 block):

```
python merge_result_shards.py \
  --inputs results/colab_imports/pro1_threshold_K128_shard0/artifacts/threshold_scan_shard0of2.csv \
           results/colab_imports/pro2_threshold_K128_shard1/artifacts/threshold_scan_shard1of2.csv \
  --order input \
  --output results/tall_design_threshold_K128_r1_merged/threshold_scan.csv
```

Verified **byte-identical** to the published `threshold_scan.csv` at current
commit `43d0a648a65994b6c5497042c65697f8a29f9490`. Default `--order sort` is
**content-identical** (sorted-row sha256 match) but reorders rows to canonical
key order.

## Honest gaps

- No original merge manifest existed; reproduction is verified at the current
  commit, not the (unrecorded) original merge commit.
- Shard `run_manifest.json` files are v1 (predate manifest v2), lacking the
  dirty-state / diff / runner-sha fingerprints.
