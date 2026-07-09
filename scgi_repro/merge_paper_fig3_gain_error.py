from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import List

import pandas as pd

from run_paper_fig3_gain_error import fit_slope, plot_outputs
from src.paper_experiments import write_caption


ROOT = Path(__file__).resolve().parent
DEFAULT_KEYS = ["object", "basis", "rho", "s", "seed", "W"]


def resolve_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def summarize(df: pd.DataFrame, fit_max_w: int) -> pd.DataFrame:
    slope_rows: List[dict[str, object]] = []
    for (basis, rho, obj), group in df.groupby(["basis", "rho", "object"]):
        slope_rows.append(
            {
                "basis": basis,
                "rho": rho,
                "object": obj,
                "fit_max_W": int(fit_max_w),
                "slope_log_err_vs_log_W": fit_slope(group, fit_max_w),
            }
        )
    slopes = pd.DataFrame(slope_rows)

    spread_rows: List[dict[str, object]] = []
    for (basis, rho, window), group in df.groupby(["basis", "rho", "W"]):
        means = group.groupby("object")["gain_rel_err"].mean()
        spread_rows.append(
            {
                "basis": basis,
                "rho": rho,
                "W": int(window),
                "object_mean_err": float(means.mean()),
                "object_std_err": float(means.std(ddof=0)),
                "relative_spread": float(means.std(ddof=0) / max(means.mean(), 1.0e-12)),
            }
        )
    spread = pd.DataFrame(spread_rows)
    return slopes.merge(spread, how="left", on=["basis", "rho"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge Colab Fig. 3 gain-error shards.")
    parser.add_argument("--input", type=Path, nargs="+", required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "paper_fig3_gain_error_merged_r1")
    parser.add_argument("--expect-rows", type=int, default=4500)
    parser.add_argument("--slope-max-window", type=int, default=32)
    args = parser.parse_args()

    start = time.time()
    frames: list[pd.DataFrame] = []
    sources: list[str] = []
    for item in args.input:
        path = resolve_path(item)
        df = pd.read_csv(path)
        df["source_file"] = str(item).replace("\\", "/")
        frames.append(df)
        sources.append(str(path))

    merged = pd.concat(frames, ignore_index=True)
    duplicated = merged.duplicated(DEFAULT_KEYS, keep=False)
    if duplicated.any():
        duplicate_path = resolve_path(args.output_dir) / "duplicate_rows.csv"
        duplicate_path.parent.mkdir(parents=True, exist_ok=True)
        merged.loc[duplicated].sort_values(DEFAULT_KEYS).to_csv(duplicate_path, index=False)
        raise SystemExit(f"duplicate Fig3 rows detected: {int(duplicated.sum())}; wrote {duplicate_path}")

    if args.expect_rows and len(merged) != args.expect_rows:
        raise SystemExit(f"expected {args.expect_rows} rows, found {len(merged)}")

    out = resolve_path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    merged = merged.sort_values(["rho", "basis", "object", "seed", "W"]).reset_index(drop=True)
    summary = summarize(merged, int(args.slope_max_window))
    merged.to_csv(out / "fig3_gain_est_error.csv", index=False)
    plot_outputs(merged, summary, out)
    write_caption(
        out / "fig3_caption.md",
        "Fig. 3 Blind Gain Identifiability",
        [
            "Merged Colab shards for rho=1e-3 and rho=1e-2 under equal objects, seeds, frames, estimator, and drift traces.",
            "Random and SRHT-like bases are evaluated against the W^-1/2 AGC variance law; ordered and shuffled Hadamard expose carrier-stationarity failures.",
            f"Rows: {len(merged)}. Sources: {len(sources)}. Runtime seconds: {time.time() - start:.2f}.",
        ],
    )
    (out / "merge_manifest.json").write_text(
        json.dumps(
            {
                "rows": int(len(merged)),
                "sources": sources,
                "expected_rows": int(args.expect_rows),
                "slope_max_window": int(args.slope_max_window),
                "runtime_seconds": round(time.time() - start, 3),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Fig3 merge complete rows={len(merged)} output={out} runtime={time.time() - start:.2f}s")


if __name__ == "__main__":
    main()
