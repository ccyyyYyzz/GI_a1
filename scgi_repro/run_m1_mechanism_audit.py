from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from run_m4_agc_targeted import markdown_table
from src.config_utils import project_root
from src.plotting import save_metrics_table, save_series_plot


def _read(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def _round(frame: pd.DataFrame, columns: list[str], digits: int = 3) -> pd.DataFrame:
    out = frame.copy()
    for col in columns:
        if col in out.columns:
            out[col] = out[col].map(lambda value: round(float(value), digits))
    return out


def build_key_tables(summary: pd.DataFrame, error_fit: pd.DataFrame) -> dict[str, pd.DataFrame]:
    oracle_agc = summary[summary["experiment"] == "oracle_agc"].copy()
    fastest_rho = float(oracle_agc["rho"].max())
    fastest = oracle_agc[oracle_agc["rho"] == fastest_rho][
        ["basis", "correction", "psnr_mean", "gain_rel_mse_mean"]
    ].copy()
    fastest = _round(fastest.sort_values(["basis", "correction"]), ["psnr_mean", "gain_rel_mse_mean"], 4)

    oracle = oracle_agc[oracle_agc["correction"] == "oracle"].copy()
    oracle_floor = (
        oracle.groupby("basis", as_index=False)
        .agg(
            oracle_min_psnr=("psnr_mean", "min"),
            oracle_mean_psnr=("psnr_mean", "mean"),
            oracle_max_gain_rel_mse=("gain_rel_mse_mean", "max"),
        )
        .sort_values("basis")
    )
    oracle_floor = _round(oracle_floor, ["oracle_min_psnr", "oracle_mean_psnr", "oracle_max_gain_rel_mse"], 4)

    agc = oracle_agc[oracle_agc["correction"] == "agc"].copy()
    agc_error = (
        agc.groupby("basis", as_index=False)
        .agg(
            agc_psnr_mean=("psnr_mean", "mean"),
            agc_gain_rel_mse_mean=("gain_rel_mse_mean", "mean"),
            agc_gain_rel_mse_min=("gain_rel_mse_mean", "min"),
            agc_gain_rel_mse_max=("gain_rel_mse_mean", "max"),
        )
        .sort_values("agc_gain_rel_mse_mean")
    )
    agc_error = _round(
        agc_error,
        ["agc_psnr_mean", "agc_gain_rel_mse_mean", "agc_gain_rel_mse_min", "agc_gain_rel_mse_max"],
        5,
    )

    scaling = error_fit.sort_values("basis").copy()
    scaling = _round(scaling, ["slope", "intercept", "r2"], 4)

    pairwise = summary[
        (summary["experiment"] == "pairwise_failure") & (summary["correction"] == "pairwise")
    ].copy()
    pairwise_ranges = (
        pairwise.groupby("basis", as_index=False)
        .agg(pairwise_min_psnr=("psnr_mean", "min"), pairwise_max_psnr=("psnr_mean", "max"))
        .sort_values("basis")
    )
    pairwise_ranges = _round(pairwise_ranges, ["pairwise_min_psnr", "pairwise_max_psnr"], 3)

    return {
        "fastest_oracle_agc": fastest,
        "oracle_floor": oracle_floor,
        "agc_error": agc_error,
        "error_scaling": scaling,
        "pairwise_ranges": pairwise_ranges,
    }


def write_report(
    out_dir: Path,
    manifest: pd.DataFrame,
    tables: dict[str, pd.DataFrame],
) -> None:
    payload = {
        "manifest_rows": {
            str(row.file): int(row.rows)
            for row in manifest.itertuples(index=False)
        },
        "oracle_min_psnr_by_basis": tables["oracle_floor"].to_dict(orient="records"),
        "agc_error_by_basis": tables["agc_error"].to_dict(orient="records"),
        "error_scaling_fit": tables["error_scaling"].to_dict(orient="records"),
        "pairwise_ranges": tables["pairwise_ranges"].to_dict(orient="records"),
    }
    (out_dir / "m1_mechanism_audit_summary.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# M1 Mechanism Audit",
        "",
        "This audit reads the o10s5 M1 protocol CSVs and summarizes the four",
        "mechanism checks: oracle gain correction, blind AGC error, synthetic",
        "residual-gain propagation, and pairwise-normalization failure curves.",
        "",
        "## Manifest",
        "",
        markdown_table(manifest),
        "",
        "## Oracle And AGC At Fastest Rho",
        "",
        markdown_table(tables["fastest_oracle_agc"]),
        "",
        "## Oracle Floor",
        "",
        markdown_table(tables["oracle_floor"]),
        "",
        "## Blind AGC Error",
        "",
        markdown_table(tables["agc_error"]),
        "",
        "## Residual Gain Error Scaling",
        "",
        markdown_table(tables["error_scaling"][["basis", "slope", "intercept", "r2", "points"]]),
        "",
        "## Pairwise Normalization Range",
        "",
        markdown_table(tables["pairwise_ranges"]),
        "",
        "## Interpretation",
        "",
        "Oracle correction restores the complete paired Hadamard/SRHT variants",
        "to exact or near-exact reconstruction, supporting the identifiability",
        "interpretation that the measurements still contain the object when true",
        "gains are known. The AGC and residual-error tables remain compact",
        "protocol evidence rather than final paper-grade figures, but they now",
        "provide concrete o10s5 artifacts for M1 instead of relying on stale",
        "documentation references.",
        "",
    ]
    (out_dir / "m1_mechanism_audit_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_figures(out_dir: Path, summary: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> None:
    save_metrics_table(
        out_dir / "m1_oracle_floor_table.png",
        tables["oracle_floor"],
        title="M1 oracle floor by basis",
        max_rows=12,
    )
    save_metrics_table(
        out_dir / "m1_error_scaling_table.png",
        tables["error_scaling"][["basis", "slope", "r2", "points"]],
        title="M1 residual gain scaling",
        max_rows=12,
    )

    pairwise = summary[
        (summary["experiment"] == "pairwise_failure")
        & (summary["correction"] == "pairwise")
        & (summary["sigma_a"] == summary["sigma_a"].min())
    ].copy()
    curve = pairwise.pivot_table(index="rho", columns="basis", values="psnr_mean", aggfunc="mean").sort_index()
    if not curve.empty:
        save_series_plot(
            out_dir / "m1_pairwise_psnr_vs_rho.png",
            curve.reset_index(drop=True),
            title="M1 pairwise PSNR vs rho",
            x_label="rho grid index",
            y_label="PSNR (dB)",
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit M1 mechanism-study CSV outputs.")
    parser.add_argument("--input-dir", type=Path, default=Path("results/mechanism_m1_protocol_o10s5"))
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    root = project_root()
    input_dir = args.input_dir if args.input_dir.is_absolute() else root / args.input_dir
    out_dir = args.output_dir if args.output_dir is not None else input_dir
    out_dir = out_dir if out_dir.is_absolute() else root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = _read(input_dir / "mechanism_m1_manifest.csv")
    summary = _read(input_dir / "mechanism_m1_summary.csv")
    error_fit = _read(input_dir / "mechanism_m1_error_scaling_fit.csv")
    tables = build_key_tables(summary, error_fit)
    write_report(out_dir, manifest, tables)
    write_figures(out_dir, summary, tables)
    print(f"wrote {out_dir}")


if __name__ == "__main__":
    main()
