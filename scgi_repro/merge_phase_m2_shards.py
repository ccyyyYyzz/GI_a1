from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.config_utils import project_root


def write_phase_outputs(df: pd.DataFrame, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    df = df.sort_values(["basis", "rho", "sigma_a", "seed", "object", "correction"]).reset_index(drop=True)
    df.to_csv(out_dir / "phase_scan.csv", index=False)

    summary = (
        df.groupby(["rho", "sigma_a", "basis", "correction"], as_index=False)
        .agg(
            psnr_mean=("psnr", "mean"),
            psnr_std=("psnr", "std"),
            rel_mse_mean=("rel_mse", "mean"),
            rel_mse_std=("rel_mse", "std"),
            num_frames=("num_frames", "first"),
            reference_frames=("reference_frames", "first"),
            total_physical_frames=("total_physical_frames", "first"),
        )
        .sort_values(["rho", "sigma_a", "psnr_mean"], ascending=[True, True, False])
    )
    best = summary.groupby(["rho", "sigma_a"], as_index=False).head(1)
    blind_summary = summary[summary["correction"] != "oracle"].copy()
    best_blind = blind_summary.groupby(["rho", "sigma_a"], as_index=False).head(1)
    equal_frame_blind = blind_summary[blind_summary["total_physical_frames"] == blind_summary["num_frames"]].copy()
    best_equal_frame_blind = equal_frame_blind.groupby(["rho", "sigma_a"], as_index=False).head(1)
    reference_summary = blind_summary[blind_summary["correction"].str.startswith("reference_")].copy()
    best_reference = reference_summary.groupby(["rho", "sigma_a"], as_index=False).head(1)

    summary.to_csv(out_dir / "phase_summary.csv", index=False)
    best.to_csv(out_dir / "best_methods.csv", index=False)
    blind_summary.to_csv(out_dir / "phase_blind_summary.csv", index=False)
    best_blind.to_csv(out_dir / "best_blind_methods.csv", index=False)
    equal_frame_blind.to_csv(out_dir / "phase_equal_frame_blind_summary.csv", index=False)
    best_equal_frame_blind.to_csv(out_dir / "best_equal_frame_blind_methods.csv", index=False)
    reference_summary.to_csv(out_dir / "phase_reference_summary.csv", index=False)
    best_reference.to_csv(out_dir / "best_reference_methods.csv", index=False)

    flip_rows = []
    for (sigma_a, correction), group in blind_summary.groupby(["sigma_a", "correction"]):
        pivot = group.pivot_table(index="rho", columns="basis", values="psnr_mean", aggfunc="mean").sort_index()
        for challenger in ["random_uniform", "random_binary", "fourier_fourstep", "dct_paired", "srht_paired"]:
            if "hadamard_paired" not in pivot.columns or challenger not in pivot.columns:
                continue
            diff = pivot[challenger] - pivot["hadamard_paired"]
            positive = diff[diff >= 0.0]
            if not len(positive):
                rho_star = float("nan")
                boundary_status = "not_reached"
            else:
                rho_star = float(positive.index[0])
                boundary_status = "left_censored" if rho_star == float(diff.index.min()) else "observed"
            flip_rows.append(
                {
                    "sigma_a": float(sigma_a),
                    "correction": correction,
                    "challenger": challenger,
                    "baseline": "hadamard_paired",
                    "rho_star_first_ge": rho_star,
                    "boundary_status": boundary_status,
                    "max_margin_db": float(diff.max()),
                    "min_margin_db": float(diff.min()),
                    "points": int(diff.notna().sum()),
                }
            )
    pd.DataFrame(flip_rows).to_csv(out_dir / "flip_boundary.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge sharded M2 phase scans and recompute summaries.")
    parser.add_argument("--inputs", nargs="+", required=True, type=Path, help="Shard output directories.")
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    root = project_root()
    frames = []
    for input_dir in args.inputs:
        directory = input_dir if input_dir.is_absolute() else root / input_dir
        path = directory / "phase_scan.csv"
        if not path.exists():
            raise FileNotFoundError(path)
        frames.append(pd.read_csv(path))
    df = pd.concat(frames, ignore_index=True).drop_duplicates()
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    write_phase_outputs(df, out_dir)
    print(f"merged rows={len(df)}")
    print(f"wrote {out_dir / 'phase_scan.csv'}")


if __name__ == "__main__":
    main()
