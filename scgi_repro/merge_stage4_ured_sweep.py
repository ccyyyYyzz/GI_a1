from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.config_utils import project_root


def find_file(input_dir: Path, name: str) -> Path:
    direct = input_dir / name
    if direct.exists():
        return direct
    matches = sorted(input_dir.rglob(name))
    if not matches:
        raise FileNotFoundError(f"No {name} under {input_dir}")
    return matches[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge sharded Stage 4 URED sweep outputs.")
    parser.add_argument("--inputs", nargs="+", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    root = project_root()
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    metric_frames = []
    baseline_frames = []
    manifest_rows = []
    for input_dir in args.inputs:
        resolved = input_dir if input_dir.is_absolute() else root / input_dir
        metrics_path = find_file(resolved, "ured_sweep_metrics.csv")
        metrics = pd.read_csv(metrics_path)
        metrics["source_file"] = str(metrics_path)
        metric_frames.append(metrics)
        try:
            baseline_path = find_file(resolved, "baseline_metrics.csv")
            baseline = pd.read_csv(baseline_path)
            baseline["source_file"] = str(baseline_path)
            baseline_frames.append(baseline)
            baseline_rows = len(baseline)
        except FileNotFoundError:
            baseline_path = None
            baseline_rows = 0
        manifest_rows.append(
            {
                "input": str(input_dir),
                "metrics_file": str(metrics_path),
                "metrics_rows": len(metrics),
                "baseline_file": str(baseline_path) if baseline_path else "",
                "baseline_rows": baseline_rows,
            }
        )

    merged = pd.concat(metric_frames, ignore_index=True)
    merged = merged.drop_duplicates(subset=["config_id", "object", "method"], keep="last")
    merged = merged.sort_values(["config_id", "object", "method"])
    merged.to_csv(out_dir / "ured_sweep_metrics.csv", index=False)

    if baseline_frames:
        baseline = pd.concat(baseline_frames, ignore_index=True)
        baseline = baseline.drop_duplicates(subset=["object", "method"], keep="last").sort_values(["object", "method"])
        baseline.to_csv(out_dir / "baseline_metrics.csv", index=False)

    summary = (
        merged.groupby(["config_id"], as_index=False)
        .agg(
            objects=("object", "count"),
            mean_cnr=("cnr", "mean"),
            min_cnr=("cnr", "min"),
            max_best_trace_cnr=("best_trace_cnr", "max"),
            mean_best_trace_cnr=("best_trace_cnr", "mean"),
            mean_psnr=("psnr", "mean"),
            min_psnr=("psnr", "min"),
            mean_ssim=("ssim", "mean"),
        )
        .sort_values(["min_cnr", "mean_cnr"], ascending=False)
    )
    config_columns = [
        "global_config_index",
        "steps",
        "lr",
        "beta",
        "xi",
        "x_step",
        "channels",
        "blocks",
        "residual_scale",
        "denoiser",
        "denoise_kernel",
        "nlm_h",
        "init_seed",
    ]
    for key in config_columns:
        if key in merged.columns:
            values = merged.groupby("config_id")[key].first()
            summary[key] = summary["config_id"].map(values)
    summary.to_csv(out_dir / "ured_sweep_summary.csv", index=False)
    pd.DataFrame(manifest_rows).to_csv(out_dir / "merge_manifest.csv", index=False)
    print(f"merged_rows={len(merged)} configs={summary['config_id'].nunique()} output={out_dir}")


if __name__ == "__main__":
    main()
