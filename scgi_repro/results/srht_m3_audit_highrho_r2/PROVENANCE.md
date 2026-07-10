# Provenance — `srht_m3_audit_highrho_r2`

Retroactive provenance record (audit blocker P0-7). This directory shipped
**without** a `run_manifest.json` because its generator, `run_m3_srht_audit.py`,
predates manifest v2 and never called `build_run_manifest`.

## What this is

The **M3 SRHT ablation audit** (Fig. 6): information-preservation ablation of
SRHT vs. ordered Hadamard vs. sign/permutation variants at high ρ. Like the M2
audit, this is a *downstream audit* — **not** a shard concatenation — so the
generic `merge_result_shards.py` (Wave C-prep T2) does not apply; the
reproduction path is the M3 pipeline below.

CSV artifact in this directory:

| file | sha256 |
| --- | --- |
| `m3_srht_delta_summary.csv` | `bcc53f60eb7df615760bf3aff4755ab502b701f71557a9c0fc242341b4dfdeb8` |

(alongside `m3_srht_audit_summary.json`, `m3_srht_audit_report.md`,
`m3_srht_delta_table.png`).

## Generating pipeline

**Step 1 — Protocol run (local CPU).** Produced the raw ablation tables in
`results/srht_m3_protocol_o10s5_highrho_r2/`:

```
python run_srht_m3.py --profile smoke --objects 10 --seeds 5 \
  --rho-values 0.001,0.1,1.0,10.0 --sigma-a 0.30 --block-size 32 \
  --output-dir results/srht_m3_protocol_o10s5_highrho_r2 --no-findings
```

Provenance from the monitored-job manifest
(`results/cli_runs/srht_m3_protocol_o10s5_highrho_r2/run_manifest.json`, which is
git-ignored / local-only):

- commit **`f3d1eef0c33b6f6acbbc5345383b9c0ee17c4537`**, branch `scgi-colab-20260709`
- UTC 2026-07-09T12:30:59Z → 12:46:34Z, local CPU, python 3.11.5, torch 2.2.1+cu121
- **working tree was dirty**: `M run_m3_srht_audit.py`, `M run_srht_m3.py`,
  `M tests/test_core.py` (uncommitted edits to the very runners that produced
  this result)
- source CSVs: `srht_ablation.csv`
  (`f20a54880e58b0bb0c69b538cdbe59a014270e4a5da9daf871ff61f417dfd725`),
  `srht_ablation_summary.csv`
  (`d24fd85ee42c837c8564269c718e227117dc11acc1b9aeba9ed8704991d84ef7`)

**Step 2 — Audit → this directory:**

```
python run_m3_srht_audit.py \
  --input-dir results/srht_m3_protocol_o10s5_highrho_r2 \
  --output-dir results/srht_m3_audit_highrho_r2
```

Re-running Step 2 on the tracked `srht_m3_protocol_o10s5_highrho_r2/` inputs
reproduces the audit tables.

## Honest gaps

- **The audit step's exact commit is unknowable**: `run_m3_srht_audit.py` wrote
  no manifest (predates manifest v2). The audit is a deterministic function of
  the protocol directory, so reproduction is anchored to that input.
- **The protocol run itself was on a dirty working tree** that included
  uncommitted modifications to `run_srht_m3.py` and `run_m3_srht_audit.py`, so
  the effective code differs from commit `f3d1eef` as checked in. This is
  precisely the failure mode manifest v2 now captures (`git_dirty`,
  `git_diff_sha256`, `runner_sha256`); for this pre-v2 run the exact diff is not
  recovered, only the fact that it existed.
- The monitored-job manifest that pins commit `f3d1eef` lives under
  `results/cli_runs/` which is git-ignored, so it is not part of the committed
  evidence bundle.
