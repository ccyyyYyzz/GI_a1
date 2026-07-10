# Provenance — `m2_boundary_audit_hadamard_order_dense_r1`

Retroactive provenance record (audit blocker P0-7). This directory shipped
**without** a `run_manifest.json` because its generator,
`run_m2_boundary_audit.py`, predates manifest v2 and never called
`build_run_manifest`.

## What this is

The **M2 flip-boundary / phase-diagram audit** (Fig. 5). Unlike the threshold
flagships, this directory is **not** a shard concatenation — it is a *downstream
audit* computed by `run_m2_boundary_audit.py` from a merged phase-scan
directory. The generic `merge_result_shards.py` (Wave C-prep T2) does **not**
apply here; the reproduction path is the M2 pipeline below.

CSV artifacts in this directory:

| file | sha256 |
| --- | --- |
| `flip_boundary.csv` | `bc492b848e3435d5ee48ee072b43082f9d8ad0a33b58cae1a9940f83f5296f45` |
| `m2_boundary_comparison_cells.csv` | `bc492b848e3435d5ee48ee072b43082f9d8ad0a33b58cae1a9940f83f5296f45` |
| `m2_boundary_fit.csv` | `69f123dc44394eef506cd568106ae0fe8bfe24cce98c4e6b66ea5e7c7c4e70be` |
| `m2_boundary_interpolated.csv` | `a7581b6dd4da3845e2c72ef19cd9c670205cf7b418d3f91fc5a0f8b384e00001` |
| `m2_rho_coverage.csv` | `a7e0ea8a645e8898487ef4e39a0ba975787c4487233a0713ba48a32edff8737e` |
| `m2_winner_cells.csv` | `57bbec087546515a516f8854cd7ed1a15d4f9ad812ef6bda3c69d1fa50b64764` |
| `m2_winner_summary.csv` | `ce9b2070ca83bac66ad06075704b7e1d1cc9beaccb2aed5dfd2b7b443c936562` |

## Generating pipeline

**Step 1 — Colab phase scan (5 shards).** `run_phase_m2.py` swept ρ∈{1e-3…10},
σ∈{0.05…0.5}, reference periods {2,8,32}, Hadamard orders
{natural, sequency, cake, random}, 10 objects × 5 seeds, over 5 shards, e.g.:

```
python run_phase_m2.py --profile smoke --objects 10 --seeds 5 \
  --rho-values '0.001,0.003,0.01,0.03,0.1,0.3,1.0,3.0,10.0' \
  --sigma-values '0.05,0.10,0.15,0.30,0.50' \
  --reference-periods '2,8,32' --hadamard-orders 'natural sequency cake random' \
  --shard 0/5 --resume --no-findings \
  --output-dir results/m2_hadamard_order_dense_r1_shard0of5
```

Colab job ref **`4752431ef218c2446a6c201010acaaa64d7a4b78`** (from
`colab_job_summary.json` `"ref"`). Imports landed under
`results/colab_imports/pro{1,2}_m2_hadamard_order_dense_r1_*shard{i}of5/`
(these shard directories are **local-only / untracked**).

**Step 2 — Phase merge** → `results/m2_hadamard_order_dense_r1_merged/`
(155,250-row `phase_scan.csv`, sha256
`9fdcd8c43baf71aaf42993e0d29db6144ab95f5a860eb9f6782cadf6a6976b18`):

```
python merge_phase_m2_shards.py \
  --inputs results/colab_imports/pro1_m2_hadamard_order_dense_r1_shard0of5/artifacts \
           results/colab_imports/pro1_m2_hadamard_order_dense_r1_bg_shard1of5/artifacts \
           results/colab_imports/pro2_m2_hadamard_order_dense_r1_bg_shard2of5/artifacts \
           results/colab_imports/pro1_m2_hadamard_order_dense_r1_bg_shard3of5/artifacts \
           results/colab_imports/pro2_m2_hadamard_order_dense_r1_bg_shard4of5/artifacts \
  --output-dir results/m2_hadamard_order_dense_r1_merged
```

**Step 3 — Boundary audit → this directory** (local, deterministic given the
merged input):

```
python run_m2_boundary_audit.py \
  --phase-dir results/m2_hadamard_order_dense_r1_merged \
  --output-dir results/m2_boundary_audit_hadamard_order_dense_r1
```

Re-running Step 3 on the tracked `m2_hadamard_order_dense_r1_merged/` inputs
reproduces these audit tables.

## Honest gaps

- **The original boundary-audit run commit is unknowable**: `run_m2_boundary_audit.py`
  wrote no manifest (predates manifest v2). The audit is a deterministic function
  of the merged phase-scan directory, so reproduction is anchored to that input
  rather than to a recorded commit.
- The Colab phase-scan shards were launched from a *moving* branch ref
  (`scgi-colab-20260709`); the concrete commit is pinned only by
  `colab_job_summary.json` `"ref" = 4752431e`. The in-Colab shard
  `run_manifest.json` recorded `git_commit = null` (the Colab environment lacked
  git), which is exactly the provenance hole manifest v2 closes going forward.
- The Step-1 shard import directories are untracked; regenerating the merged
  phase scan from scratch requires re-running the Colab jobs at ref `4752431e`.
