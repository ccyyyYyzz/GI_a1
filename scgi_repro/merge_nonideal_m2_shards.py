from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from run_nonideal_m2 import summarize, write_key_summary
from src.config_utils import project_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge sharded nonideal M2 scans and recompute summaries.")
    parser.add_argument("--inputs", nargs="+", required=True, type=Path, help="Shard output directories.")
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    root = project_root()
    frames = []
    for input_dir in args.inputs:
        directory = input_dir if input_dir.is_absolute() else root / input_dir
        path = directory / "nonideal_phase_scan.csv"
        if not path.exists():
            raise FileNotFoundError(path)
        frames.append(pd.read_csv(path))
    df = pd.concat(frames, ignore_index=True).drop_duplicates()
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    df = df.sort_values(
        ["condition", "basis", "rho", "sigma_a", "seed", "object", "correction"]
    ).reset_index(drop=True)
    df.to_csv(out_dir / "nonideal_phase_scan.csv", index=False)
    summarize(df, out_dir)
    write_key_summary(df, out_dir)
    print(f"merged rows={len(df)}")
    print(f"wrote {out_dir / 'nonideal_phase_scan.csv'}")


if __name__ == "__main__":
    main()
