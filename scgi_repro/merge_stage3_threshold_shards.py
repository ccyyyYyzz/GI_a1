from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pandas as pd

from src.config_utils import project_root
from src.plotting import save_metrics_table


def find_metrics(input_dir: Path) -> Path:
    direct = input_dir / "stage3_metrics.csv"
    if direct.exists():
        return direct
    matches = sorted(input_dir.rglob("stage3_metrics.csv"))
    if not matches:
        raise FileNotFoundError(f"No stage3_metrics.csv under {input_dir}")
    return matches[0]


def build_acceptance(df: pd.DataFrame) -> list[dict[str, object]]:
    pivot = df.pivot_table(index="object", columns="method", values="cnr", aggfunc="mean")
    checks: list[dict[str, object]] = []
    if {"scgi", "dynamic"}.issubset(pivot.columns):
        checks.append(
            {
                "check": "scgi_cnr_above_dynamic_all",
                "value": bool((pivot["scgi"] > pivot["dynamic"]).all()),
                "passed": bool((pivot["scgi"] > pivot["dynamic"]).all()),
            }
        )
        checks.append(
            {
                "check": "scgi_cnr_ge_apl_min_all",
                "value": bool((pivot["scgi"] >= 3.39).all()),
                "passed": bool((pivot["scgi"] >= 3.39).all()),
            }
        )
    if {"scgi_unn", "scgi"}.issubset(pivot.columns):
        checks.append(
            {
                "check": "scgi_unn_cnr_above_scgi_all",
                "value": bool((pivot["scgi_unn"] > pivot["scgi"]).all()),
                "passed": bool((pivot["scgi_unn"] > pivot["scgi"]).all()),
            }
        )
        checks.append(
            {
                "check": "scgi_unn_cnr_ge_apl_min_all",
                "value": bool((pivot["scgi_unn"] >= 7.93).all()),
                "passed": bool((pivot["scgi_unn"] >= 7.93).all()),
            }
        )
    if {"scgi_ured", "scgi_unn"}.issubset(pivot.columns):
        checks.append(
            {
                "check": "scgi_ured_cnr_above_scgi_unn_all",
                "value": bool((pivot["scgi_ured"] > pivot["scgi_unn"]).all()),
                "passed": bool((pivot["scgi_ured"] > pivot["scgi_unn"]).all()),
            }
        )
        checks.append(
            {
                "check": "scgi_ured_cnr_ge_apl_min_all",
                "value": bool((pivot["scgi_ured"] >= 10.43).all()),
                "passed": bool((pivot["scgi_ured"] >= 10.43).all()),
            }
        )
    if "static" in df["method"].unique():
        static = df[df["method"] == "static"]
        checks.append(
            {
                "check": "static_psnr_gt_20_all",
                "value": bool((static["psnr"] > 20.0).all()),
                "passed": bool((static["psnr"] > 20.0).all()),
            }
        )
    return checks


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge sharded Stage 3 threshold-matrix runs.")
    parser.add_argument("--inputs", nargs="+", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    root = project_root()
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    frames = []
    manifest_rows = []
    for input_dir in args.inputs:
        path = find_metrics(input_dir if input_dir.is_absolute() else root / input_dir)
        df = pd.read_csv(path)
        df["source_file"] = str(path)
        frames.append(df)
        manifest_rows.append({"input": str(input_dir), "metrics_file": str(path), "rows": len(df)})
    merged = pd.concat(frames, ignore_index=True)
    merged = merged.drop_duplicates(subset=["object", "method"], keep="last").sort_values(["object", "method"])
    merged.to_csv(out_dir / "stage3_metrics.csv", index=False)
    pd.DataFrame(manifest_rows).to_csv(out_dir / "merge_manifest.csv", index=False)

    table = merged[["object", "method", "cnr", "psnr", "ssim", "ks_p"]]
    save_metrics_table(out_dir / "stage3_metrics_table.png", table, title="Merged Stage 3 threshold matrix", max_rows=64)

    checks = build_acceptance(merged)
    with (out_dir / "stage3_acceptance.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["check", "value", "passed"])
        writer.writeheader()
        writer.writerows(checks)
    print(f"merged_rows={len(merged)} output={out_dir}")


if __name__ == "__main__":
    main()
