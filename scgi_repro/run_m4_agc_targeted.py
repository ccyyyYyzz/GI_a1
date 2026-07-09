from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from run_theory_m4 import parse_floats, run_agc_window_law
from src.config_utils import project_root


def analyze_saturation(summary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    best = (
        summary.sort_values(["basis", "rho", "sigma_a", "gain_rel_mse_mean"])
        .groupby(["basis", "rho", "sigma_a"], as_index=False)
        .head(1)
        .copy()
    )
    bounds = (
        summary.groupby("basis", as_index=False)
        .agg(min_window_frames=("window_frames", "min"), max_window_frames=("window_frames", "max"))
        .set_index("basis")
    )
    statuses = []
    for row in best.itertuples(index=False):
        min_w = int(bounds.loc[row.basis, "min_window_frames"])
        max_w = int(bounds.loc[row.basis, "max_window_frames"])
        if int(row.window_frames) <= min_w:
            status = "lower_bound"
        elif int(row.window_frames) >= max_w:
            status = "upper_bound"
        else:
            status = "interior"
        statuses.append(status)
    best["boundary_status"] = statuses
    saturation = (
        best.groupby(["basis", "boundary_status"], as_index=False)
        .size()
        .pivot(index="basis", columns="boundary_status", values="size")
        .fillna(0)
        .reset_index()
    )
    for col in ["lower_bound", "interior", "upper_bound"]:
        if col not in saturation.columns:
            saturation[col] = 0
    saturation["total_cells"] = saturation[["lower_bound", "interior", "upper_bound"]].sum(axis=1)
    saturation["interior_frac"] = saturation["interior"] / saturation["total_cells"].clip(lower=1)
    saturation["boundary_frac"] = 1.0 - saturation["interior_frac"]
    return best, saturation[["basis", "lower_bound", "interior", "upper_bound", "total_cells", "interior_frac", "boundary_frac"]]


def markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "(empty)"
    text = frame.copy()
    for col in text.columns:
        if pd.api.types.is_float_dtype(text[col]):
            text[col] = text[col].map(lambda value: f"{float(value):.4g}")
        else:
            text[col] = text[col].astype(str)
    columns = list(text.columns)
    rows = text.astype(str).values.tolist()
    widths = [
        max(len(str(col)), *(len(row[idx]) for row in rows))
        for idx, col in enumerate(columns)
    ]
    header = "| " + " | ".join(str(col).ljust(widths[idx]) for idx, col in enumerate(columns)) + " |"
    sep = "| " + " | ".join("-" * widths[idx] for idx, _col in enumerate(columns)) + " |"
    body = [
        "| " + " | ".join(row[idx].ljust(widths[idx]) for idx in range(len(columns))) + " |"
        for row in rows
    ]
    return "\n".join([header, sep, *body])


def write_report(out_dir: Path, best: pd.DataFrame, saturation: pd.DataFrame, fits: pd.DataFrame) -> None:
    ok = fits[fits["fit_status"] == "ok"].copy() if "fit_status" in fits else pd.DataFrame()
    lines = [
        "# Targeted M4 AGC Window Validation",
        "",
        "This run uses a wider, denser window grid than the paper-r2 diagnostic",
        "to test whether the candidate AGC bias-variance law is supported away",
        "from sampled window-grid boundaries.",
        "",
        "## Boundary Saturation",
        "",
        markdown_table(saturation),
        "",
        "## Log-Linear Fits",
        "",
    ]
    if len(ok):
        lines.append(
            markdown_table(
                ok[
                [
                    "basis",
                    "rho_exponent",
                    "sigma_a_exponent",
                    "r2",
                    "rmse_log10",
                    "n",
                ]
                ]
            )
        )
    else:
        lines.append("No successful log-linear fits.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "A useful scaling law should have most best-window selections in the",
            "interior of the sampled grid and stable exponents across bases.",
            "Boundary-heavy selections indicate that the estimator or basis still",
            "prefers the smallest/largest tested window, so the fitted law should",
            "be treated as diagnostic rather than publication-ready.",
            "",
        ]
    )
    out_dir.joinpath("m4_agc_targeted_report.md").write_text("\n".join(lines), encoding="utf-8")

    key = {
        "total_best_cells": int(len(best)),
        "saturation": saturation.to_dict(orient="records"),
        "fits": ok.to_dict(orient="records") if len(ok) else [],
    }
    out_dir.joinpath("m4_agc_targeted_summary.json").write_text(json.dumps(key, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Targeted AGC best-window validation for M4.")
    parser.add_argument("--output-dir", type=Path, default=Path("results/theory_m4_agc_targeted_r1"))
    parser.add_argument("--image-size", type=int, default=32)
    parser.add_argument("--bases", default="random_uniform random_binary hadamard_paired srht_paired")
    parser.add_argument("--objects", type=int, default=8)
    parser.add_argument("--seeds", type=int, default=4)
    parser.add_argument("--rhos", default="0.0003 0.001 0.003 0.01 0.03 0.1 0.3 1.0 3.0")
    parser.add_argument("--sigmas", default="0.05 0.10 0.15 0.30 0.50")
    parser.add_argument(
        "--window-fracs",
        default="0.0015 0.0025 0.004 0.006 0.009 0.013 0.02 0.03 0.045 0.067 0.10 0.15 0.22 0.33 0.50",
    )
    parser.add_argument("--seed", type=int, default=20260709)
    args = parser.parse_args()

    root = project_root()
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    basis_names = [part for part in args.bases.replace(",", " ").split() if part.strip()]
    raw, summary, fits = run_agc_window_law(
        int(args.image_size),
        basis_names,
        int(args.objects),
        int(args.seeds),
        parse_floats(args.rhos),
        parse_floats(args.sigmas),
        parse_floats(args.window_fracs),
        int(args.seed),
    )
    best, saturation = analyze_saturation(summary)
    raw.to_csv(out_dir / "m4_agc_targeted_raw.csv", index=False)
    summary.to_csv(out_dir / "m4_agc_targeted_summary.csv", index=False)
    best.to_csv(out_dir / "m4_agc_targeted_best_windows.csv", index=False)
    saturation.to_csv(out_dir / "m4_agc_targeted_saturation.csv", index=False)
    fits.to_csv(out_dir / "m4_agc_targeted_fit.csv", index=False)
    write_report(out_dir, best, saturation, fits)
    print(f"wrote {out_dir}")


if __name__ == "__main__":
    main()
