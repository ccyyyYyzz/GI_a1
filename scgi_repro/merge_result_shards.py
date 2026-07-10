"""Deterministic merge of sharded result CSVs with provenance.

Concatenates a set of shard CSVs into one merged CSV, then:

* **stable-sorts** the rows by a documented identifier key set (see
  ``IDENTIFIER_COLUMNS`` below) so the output is order-independent of the
  order the shards were supplied (``--order sort``, the default), OR preserves
  the concatenation order (``--order input``) when byte-for-byte reproduction
  of a shard-arrival-ordered file is required;
* **dedupes exact duplicate rows** (rows identical across *all* columns);
* **refuses** (exits non-zero) on *conflicting* duplicates -- rows that share
  the identifier key set but disagree on any measured/derived column;
* writes the merged CSV plus a ``merge_manifest.json`` carrying v2-style run
  provenance (``src.paper_experiments.build_run_manifest``), a per-input
  SHA256, per-input/merged row counts, the chosen key set and the output
  SHA256.

Key-set convention
------------------
The dedup/sort/conflict key is the set of *non-derived identifier* columns --
the experiment configuration and cell indices, never the measured outcomes.
For the flagship threshold scans the resolved key is
``[K, p, N, offset, seed, object_kind, unit_index, shard]`` and every other
column (``rank_J``, ``best_relmse_T``, ``best_residual``, ...) is treated as a
value/derived column. Override with ``--key-cols`` when auto-detection is
wrong; the actually-used key set is always recorded in the manifest.

Determinism
-----------
CSV text is produced with ``DataFrame.to_csv(index=False)`` (LF line endings)
and written as raw bytes, so identical inputs always yield byte-identical
output regardless of platform.

Examples
--------
Reproduce the merged K=64 threshold flagship byte-for-byte (shard-arrival
order)::

    python merge_result_shards.py \\
        --inputs results/colab_imports/pro1_threshold_full_shard0of2_r1/artifacts/threshold_scan_shard0of2.csv \\
                 results/colab_imports/pro2_threshold_full_shard1of2_r1/artifacts/threshold_scan_shard1of2.csv \\
        --order input \\
        --output results/tall_design_threshold_full_r1_merged/threshold_scan.csv
"""

from __future__ import annotations

import argparse
import glob as globlib
import json
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import pandas as pd

from src.paper_experiments import build_run_manifest, sha256_file

# Repo root (this file lives at the repo root; runners always cd here).
ROOT = Path(__file__).resolve().parent

# Documented non-derived identifier columns, in canonical sort priority.
# The merge key is the intersection of this list with the CSV's columns.
# Everything NOT in this list is treated as a measured / derived value column.
IDENTIFIER_COLUMNS: List[str] = [
    # experiment configuration
    "K", "p", "N", "offset", "seed",
    "rho", "sigma", "sigma_a", "window", "block_size", "trial", "repeat",
    # categorical descriptors
    "dataset", "object", "object_kind", "family", "method", "basis",
    "correction", "variant", "hadamard_order",
    # cell / index bookkeeping
    "cell_index", "unit_index", "idx", "row_index", "shard",
]


class MergeConflictError(RuntimeError):
    """Raised when two rows share the key set but disagree on a value column."""


def resolve_key_columns(columns: Sequence[str], override: Optional[Sequence[str]] = None) -> List[str]:
    """Pick the identifier key columns for a set of CSV columns.

    ``override`` (if given) is validated against the actual columns. Otherwise
    the documented ``IDENTIFIER_COLUMNS`` are intersected with ``columns`` in
    canonical order. Falls back to *all* columns (exact-row dedup only) when no
    identifier column is present.
    """

    cols = list(columns)
    if override:
        missing = [c for c in override if c not in cols]
        if missing:
            raise ValueError(f"--key-cols not present in data: {missing}; available: {cols}")
        return list(override)
    keys = [c for c in IDENTIFIER_COLUMNS if c in cols]
    if not keys:
        # No recognised identifier column: treat the whole row as the key so we
        # still drop exact duplicates and never silently accept a conflict.
        return cols
    return keys


def dataframe_to_csv_bytes(frame: pd.DataFrame) -> bytes:
    """Deterministic CSV serialization: no index, LF line endings, UTF-8."""

    # to_csv(buf=None) returns a str with '\n' line endings on every platform.
    return frame.to_csv(index=False).encode("utf-8")


def read_inputs(paths: Sequence[Path]) -> List[Tuple[Path, pd.DataFrame, str, int]]:
    """Read each shard CSV; return (path, frame, sha256, rows) tuples."""

    out: List[Tuple[Path, pd.DataFrame, str, int]] = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"Input CSV not found: {path}")
        frame = pd.read_csv(path)
        digest = sha256_file(path)
        out.append((path, frame, digest or "", int(len(frame))))
    return out


def merge_frames(
    frames: Sequence[pd.DataFrame],
    key_cols: Sequence[str],
    order: str = "sort",
) -> Tuple[pd.DataFrame, dict]:
    """Concatenate, drop exact-duplicate rows, refuse conflicts, order rows.

    Returns ``(merged_frame, stats)`` where ``stats`` records the input/merged
    row counts and how many exact duplicates were dropped. Raises
    :class:`MergeConflictError` if two surviving rows share ``key_cols`` but
    differ on any other column.
    """

    if not frames:
        raise ValueError("No input frames to merge.")
    # Uniform columns are required for a meaningful merge.
    ref_cols = list(frames[0].columns)
    for i, frame in enumerate(frames[1:], start=1):
        if list(frame.columns) != ref_cols:
            raise ValueError(
                f"Shard {i} column mismatch.\n  expected: {ref_cols}\n  got:      {list(frame.columns)}"
            )
    key_cols = list(key_cols)

    combined = pd.concat(list(frames), ignore_index=True)
    input_rows = int(len(combined))

    # 1) Drop rows that are identical across ALL columns (exact duplicates).
    deduped = combined.drop_duplicates(keep="first").reset_index(drop=True)
    exact_dropped = input_rows - int(len(deduped))

    # 2) Refuse on conflicting duplicates: same key, different value column(s).
    conflict_mask = deduped.duplicated(subset=key_cols, keep=False)
    if bool(conflict_mask.any()):
        conflicts = deduped[conflict_mask].sort_values(key_cols, kind="mergesort")
        sample = conflicts.head(12).to_string(index=False)
        n_keys = int(conflicts[key_cols].drop_duplicates().shape[0])
        raise MergeConflictError(
            f"{n_keys} key group(s) have conflicting rows (same {key_cols}, "
            f"different values). Refusing to merge.\nFirst offending rows:\n{sample}"
        )

    # 3) Order the surviving rows.
    if order == "sort":
        merged = deduped.sort_values(key_cols, kind="mergesort").reset_index(drop=True)
    elif order == "input":
        merged = deduped
    else:
        raise ValueError(f"order must be 'sort' or 'input', got {order!r}")

    stats = {
        "input_rows_total": input_rows,
        "exact_duplicates_dropped": exact_dropped,
        "merged_rows": int(len(merged)),
    }
    return merged, stats


def build_merge_manifest(
    args: argparse.Namespace,
    inputs_meta: Sequence[Tuple[Path, pd.DataFrame, str, int]],
    key_cols: Sequence[str],
    stats: dict,
    output_path: Path,
    output_sha256: Optional[str],
) -> dict:
    """v2 run provenance + merge-specific fields (per-input sha256, counts)."""

    manifest = build_run_manifest(
        args,
        ROOT,
        extra={
            "merge": {
                "output_path": str(output_path),
                "output_sha256": output_sha256,
                "key_columns": list(key_cols),
                "row_order": args.order,
                "inputs": [
                    {"path": str(path), "sha256": digest, "rows": rows}
                    for (path, _frame, digest, rows) in inputs_meta
                ],
                **stats,
            }
        },
    )
    return manifest


def _resolve_input_paths(inputs: Optional[Sequence[str]], pattern: Optional[str]) -> List[Path]:
    paths: List[Path] = []
    if inputs:
        paths.extend(Path(p) for p in inputs)
    if pattern:
        # Sort glob matches for determinism.
        matches = sorted(globlib.glob(pattern, recursive=True))
        if not matches:
            raise FileNotFoundError(f"--glob matched no files: {pattern}")
        paths.extend(Path(p) for p in matches)
    if not paths:
        raise ValueError("Provide at least one shard via --inputs and/or --glob.")
    return paths


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministically merge sharded result CSVs.")
    parser.add_argument("--inputs", nargs="+", type=str, help="Explicit shard CSV paths.")
    parser.add_argument("--glob", type=str, default=None, help="Glob pattern for shard CSVs (sorted).")
    parser.add_argument("--output", type=Path, required=True, help="Merged CSV output path.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="merge_manifest.json path (default: <output-dir>/merge_manifest.json).",
    )
    parser.add_argument(
        "--key-cols",
        type=str,
        default=None,
        help="Comma-separated identifier key override (default: auto-detect).",
    )
    parser.add_argument(
        "--order",
        choices=["sort", "input"],
        default="sort",
        help="'sort' (canonical stable key sort, default) or 'input' (concat order).",
    )
    args = parser.parse_args(argv)

    input_paths = _resolve_input_paths(args.inputs, args.glob)
    inputs_meta = read_inputs(input_paths)
    frames = [meta[1] for meta in inputs_meta]

    override = [c.strip() for c in args.key_cols.split(",")] if args.key_cols else None
    key_cols = resolve_key_columns(frames[0].columns, override)

    merged, stats = merge_frames(frames, key_cols, order=args.order)

    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(dataframe_to_csv_bytes(merged))
    output_sha256 = sha256_file(output_path)

    manifest_path = args.manifest or (output_path.parent / "merge_manifest.json")
    if not manifest_path.is_absolute():
        manifest_path = ROOT / manifest_path
    manifest = build_merge_manifest(args, inputs_meta, key_cols, stats, output_path, output_sha256)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, default=str), encoding="utf-8")

    print(
        f"merged_rows={stats['merged_rows']} "
        f"exact_dropped={stats['exact_duplicates_dropped']} "
        f"keys={key_cols} order={args.order}\n"
        f"output={output_path} sha256={output_sha256}\n"
        f"manifest={manifest_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
