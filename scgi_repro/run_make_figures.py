from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.config_utils import project_root
from src.plotting import save_metrics_table, save_series_plot


def _read(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing required result file: {path}")
    return pd.read_csv(path)


def _series_by(df: pd.DataFrame, index: str, columns: str, values: str) -> pd.DataFrame:
    frame = df.pivot_table(index=index, columns=columns, values=values, aggfunc="mean")
    return frame.sort_index()


def _first_existing(*paths: Path) -> Path:
    for path in paths:
        if path.exists():
            return path
    return paths[0]


def _first_existing_with_file(filename: str, *paths: Path) -> Path:
    for path in paths:
        if (path / filename).exists():
            return path
    return paths[0]


def make_m1_figures(root: Path, out_dir: Path) -> list[Path]:
    paths: list[Path] = []
    m1_dir = _first_existing(
        root / "results" / "mechanism_m1_protocol_o10s5",
        root / "results" / "mechanism_m1_basis_expanded_quick",
        root / "results" / "mechanism_m1",
    )
    summary = _read(m1_dir / "mechanism_m1_summary.csv")

    oracle = summary[
        (summary["experiment"] == "oracle_agc")
        & (summary["basis"].isin(["hadamard_paired", "srht_paired", "random_uniform"]))
        & (summary["correction"].isin(["none", "agc", "oracle"]))
    ].copy()
    oracle["method"] = oracle["basis"].astype(str) + "+" + oracle["correction"].astype(str)
    paths.append(
        save_series_plot(
            out_dir / "m1_oracle_agc_psnr.png",
            _series_by(oracle, "rho", "method", "psnr_mean"),
            title="M1 oracle/AGC PSNR",
            x_label="rho index",
            y_label="PSNR",
        )
    )

    pairwise = summary[
        (summary["experiment"] == "pairwise_failure")
        & (summary["basis"].isin(["hadamard_paired", "srht_paired"]))
        & (summary["correction"].isin(["pairwise", "oracle", "agc"]))
    ].copy()
    pairwise["method"] = pairwise["basis"].astype(str) + "+" + pairwise["correction"].astype(str)
    paths.append(
        save_series_plot(
            out_dir / "m1_pairwise_failure_psnr.png",
            _series_by(pairwise, "rho", "method", "psnr_mean"),
            title="M1 pairwise failure PSNR",
            x_label="rho index",
            y_label="PSNR",
        )
    )
    top = oracle.sort_values("psnr_mean", ascending=False).head(12)
    paths.append(
        save_metrics_table(
            out_dir / "m1_top_methods_table.png",
            top[["basis", "correction", "rho", "sigma_a", "psnr_mean", "rel_mse_mean"]],
            title="M1 top rows",
            max_rows=12,
        )
    )
    agc_window_path = m1_dir / "mechanism_m1_agc_window_sweep.csv"
    if agc_window_path.exists():
        agc = _read(agc_window_path)
        agc_summary = agc.groupby(["basis", "window_frac"], as_index=False).agg(gain_rel_mse=("gain_rel_mse", "mean"))
        paths.append(
            save_series_plot(
                out_dir / "m1_agc_window_gain_error.png",
                _series_by(agc_summary, "window_frac", "basis", "gain_rel_mse"),
                title="M1 AGC window gain error",
                x_label="window fraction",
                y_label="gain relative MSE",
            )
        )
    fit_path = m1_dir / "mechanism_m1_error_scaling_fit.csv"
    if fit_path.exists():
        fit = _read(fit_path)
        paths.append(
            save_metrics_table(
                out_dir / "m1_error_scaling_fit_table.png",
                fit[["basis", "slope", "r2", "points"]],
                title="M1 residual gain scaling fit",
                max_rows=12,
            )
        )
    return paths


def make_m2_figures(root: Path, out_dir: Path) -> list[Path]:
    paths: list[Path] = []
    m2_dir = _first_existing_with_file(
        "best_methods.csv",
        root / "results" / "phase_m2_reference_protocol_o10s5",
        root / "results" / "phase_m2_reference_smoke",
        root / "results" / "phase_m2_protocol_o10s5",
        root / "results" / "phase_m2_basis_expanded_quick",
        root / "results" / "phase_m2_o3s2",
        root / "results" / "phase_m2_quick",
    )
    best = _read(m2_dir / "best_methods.csv")
    best_blind = _read(m2_dir / "best_blind_methods.csv")
    table_cols = ["rho", "sigma_a", "basis", "correction", "psnr_mean", "rel_mse_mean"]
    if "total_physical_frames" in best.columns:
        table_cols.append("total_physical_frames")
    paths.append(
        save_metrics_table(
            out_dir / "m2_best_methods_table.png",
            best[table_cols],
            title="M2 best methods",
            max_rows=20,
        )
    )
    blind_cols = [col for col in table_cols if col in best_blind.columns]
    paths.append(
        save_metrics_table(
            out_dir / "m2_best_blind_methods_table.png",
            best_blind[blind_cols],
            title="M2 best blind methods",
            max_rows=20,
        )
    )
    equal_path = m2_dir / "best_equal_frame_blind_methods.csv"
    if equal_path.exists():
        equal = _read(equal_path)
        equal_cols = [col for col in blind_cols if col in equal.columns]
        paths.append(
            save_metrics_table(
                out_dir / "m2_best_equal_frame_blind_methods_table.png",
                equal[equal_cols],
                title="M2 best equal-frame blind methods",
                max_rows=20,
            )
        )
    reference_path = m2_dir / "best_reference_methods.csv"
    if reference_path.exists():
        reference = _read(reference_path)
        reference_cols = [col for col in blind_cols if col in reference.columns]
        paths.append(
            save_metrics_table(
                out_dir / "m2_best_reference_methods_table.png",
                reference[reference_cols],
                title="M2 best reference-calibrated methods",
                max_rows=20,
            )
        )
    summary = _read(m2_dir / "phase_summary.csv")
    summary["method"] = summary["basis"].astype(str) + "+" + summary["correction"].astype(str)
    keep = summary["method"].isin(
        [
            "hadamard_paired+oracle",
            "hadamard_paired+pairwise",
            "hadamard_paired+reference_k8",
            "dct_paired+pairwise",
            "srht_paired+pairwise",
            "srht_paired+reference_k8",
            "fourier_fourstep+agc",
            "srht_paired+agc",
            "random_uniform+agc",
        ]
    )
    paths.append(
        save_series_plot(
            out_dir / "m2_selected_phase_psnr.png",
            _series_by(summary[keep], "rho", "method", "psnr_mean"),
            title="M2 selected methods PSNR",
            x_label="rho index",
            y_label="PSNR",
        )
    )
    flip_path = m2_dir / "flip_boundary.csv"
    if flip_path.exists():
        flip = _read(flip_path)
        paths.append(
            save_metrics_table(
                out_dir / "m2_flip_boundary_table.png",
                flip.sort_values(["sigma_a", "correction", "challenger"]).head(24)[
                    ["sigma_a", "correction", "challenger", "rho_star_first_ge", "max_margin_db", "points"]
                ],
                title="M2 flip-boundary diagnostics",
                max_rows=24,
            )
        )
    return paths


def make_gamma_figures(root: Path, out_dir: Path) -> list[Path]:
    paths: list[Path] = []
    gamma_path = root / "results" / "stage_0" / "gamma_sweep_recon.csv"
    if not gamma_path.exists():
        gamma_path = root / "results" / "stage_0" / "gamma_sweep.csv"
    gamma = _read(gamma_path)
    if "scgi_cnr" in gamma.columns:
        curves = gamma.set_index("gamma")[["dynamic_cnr", "scgi_cnr", "analytic_cnr", "oracle_cnr"]]
        paths.append(
            save_series_plot(
                out_dir / "stage0_gamma_cnr.png",
                curves,
                title="Stage 0 gamma sweep CNR",
                x_label="gamma index",
                y_label="CNR",
            )
        )
        paths.append(
            save_metrics_table(
                out_dir / "stage0_gamma_table.png",
                gamma[["gamma", "epochs", "scgi_cnr", "scgi_psnr", "scgi_ssim", "scgi_ks_p"]],
                title="Stage 0 gamma sweep",
                max_rows=12,
            )
        )
    return paths


def make_m3_figures(root: Path, out_dir: Path) -> list[Path]:
    paths: list[Path] = []
    m3_dir = _first_existing(
        root / "results" / "srht_m3_protocol_o10s5",
        root / "results" / "srht_m3_quick",
    )
    summary = _read(m3_dir / "srht_ablation_summary.csv")
    summary["method"] = summary["variant"].astype(str) + "+" + summary["correction"].astype(str)
    keep = summary["correction"].isin(["agc", "pairwise", "oracle"])
    paths.append(
        save_series_plot(
            out_dir / "m3_srht_ablation_psnr.png",
            _series_by(summary[keep], "rho", "method", "psnr_mean"),
            title="M3 SRHT ablation PSNR",
            x_label="rho index",
            y_label="PSNR",
        )
    )
    paths.append(
        save_metrics_table(
            out_dir / "m3_srht_ablation_table.png",
            summary.sort_values("psnr_mean", ascending=False).head(16)[["variant", "correction", "rho", "psnr_mean", "rel_mse_mean"]],
            title="M3 ablation top rows",
            max_rows=16,
        )
    )
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Render compact mechanism-study figures from CSV outputs.")
    parser.add_argument("--output-dir", type=Path, default=Path("results/figures"))
    args = parser.parse_args()
    root = project_root()
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    paths = []
    paths.extend(make_gamma_figures(root, out_dir))
    paths.extend(make_m1_figures(root, out_dir))
    paths.extend(make_m2_figures(root, out_dir))
    paths.extend(make_m3_figures(root, out_dir))

    manifest = pd.DataFrame({"figure": [p.name for p in paths], "path": [str(p) for p in paths]})
    manifest.to_csv(out_dir / "figure_manifest.csv", index=False)
    findings = root / "FINDINGS.md"
    marker = "## Rendered Figures"
    text = findings.read_text(encoding="utf-8") if findings.exists() else "# Findings\n"
    note = f"{marker}\n\nLatest figure manifest: `{(out_dir / 'figure_manifest.csv').as_posix()}`.\n"
    if marker in text:
        text = text[: text.index(marker)].rstrip() + "\n\n" + note
    else:
        text = text.rstrip() + "\n\n" + note
    findings.write_text(text, encoding="utf-8")
    print(f"wrote {out_dir / 'figure_manifest.csv'}")


if __name__ == "__main__":
    main()
