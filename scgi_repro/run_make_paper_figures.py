from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from src.config_utils import project_root
from src.plotting import DEFAULT_PALETTE, save_metrics_table, save_series_plot


def _read(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing required result file: {path}")
    return pd.read_csv(path)


def _font() -> ImageFont.ImageFont:
    return ImageFont.load_default()


def _method_label(row: pd.Series) -> str:
    basis = str(row["basis"]).replace("_paired", "").replace("_fourstep", "")
    correction = str(row["correction"]).replace("reference_", "ref")
    return f"{basis}\n{correction}"


def _winner_map_rows(winner_cells: pd.DataFrame, scope: str) -> pd.DataFrame:
    rows: list[pd.Series] = []
    for (_rho, _sigma), group in winner_cells.groupby(["rho", "sigma_a"], sort=True):
        if scope == "equal_frame":
            candidates = group[group["reference_frames"].fillna(0).astype(float) == 0]
            if candidates.empty:
                candidates = group
            rows.append(candidates.sort_values("psnr_mean", ascending=False).iloc[0])
        elif scope == "all_non_oracle":
            reference = group[group["reference_frames"].fillna(0).astype(float) > 0]
            if not reference.empty:
                rows.append(reference.sort_values("psnr_mean", ascending=False).iloc[0])
            else:
                rows.append(group.sort_values("psnr_mean", ascending=False).iloc[0])
        else:
            raise ValueError(f"Unsupported scope: {scope}")
    return pd.DataFrame(rows).reset_index(drop=True)


def save_winner_heatmap(path: Path, winner_rows: pd.DataFrame, title: str) -> Path:
    rhos = sorted(winner_rows["rho"].unique())
    sigmas = sorted(winner_rows["sigma_a"].unique())
    cell_w, cell_h = 116, 58
    left, top, right, bottom = 78, 48, 18, 42
    width = left + len(rhos) * cell_w + right
    height = top + len(sigmas) * cell_h + bottom
    image = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = _font()

    methods = sorted({f"{r.basis}+{r.correction}" for r in winner_rows.itertuples()})
    color_map = {
        method: DEFAULT_PALETTE[idx % len(DEFAULT_PALETTE)]
        for idx, method in enumerate(methods)
    }

    draw.text((left, 10), title, fill=(0, 0, 0), font=font)
    for col, rho in enumerate(rhos):
        x = left + col * cell_w
        draw.text((x + 8, top - 22), f"rho={rho:g}", fill=(0, 0, 0), font=font)
    for row_idx, sigma in enumerate(sigmas):
        y = top + row_idx * cell_h
        draw.text((8, y + 18), f"sigma={sigma:g}", fill=(0, 0, 0), font=font)

    indexed = winner_rows.set_index(["rho", "sigma_a"])
    for row_idx, sigma in enumerate(sigmas):
        for col, rho in enumerate(rhos):
            item = indexed.loc[(rho, sigma)]
            method = f"{item['basis']}+{item['correction']}"
            color = color_map[method]
            x0 = left + col * cell_w
            y0 = top + row_idx * cell_h
            draw.rectangle((x0, y0, x0 + cell_w - 2, y0 + cell_h - 2), fill=color, outline=(70, 70, 70))
            label = _method_label(item)
            for line_idx, line in enumerate(label.splitlines()):
                draw.text((x0 + 6, y0 + 6 + 14 * line_idx), line, fill=(255, 255, 255), font=font)
            draw.text((x0 + 6, y0 + cell_h - 16), f"{float(item['psnr_mean']):.1f} dB", fill=(255, 255, 255), font=font)

    draw.text((left, height - 26), "Cell text: winning basis/correction and mean PSNR.", fill=(0, 0, 0), font=font)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return path


def make_m2_paper_figures(root: Path, out_dir: Path) -> list[dict[str, str]]:
    audit_dir = root / "results" / "m2_boundary_audit_highrho"
    winner_cells = _read(audit_dir / "m2_winner_cells.csv")
    boundary_fit = _read(audit_dir / "m2_boundary_fit.csv")
    boundary_observed = boundary_fit[boundary_fit["fit_status"] == "ok"].copy()

    manifest: list[dict[str, str]] = []
    for scope, title in [
        ("equal_frame", "M2 strict equal-frame non-oracle winners"),
        ("all_non_oracle", "M2 all-non-oracle winners with reference overhead"),
    ]:
        rows = _winner_map_rows(winner_cells, scope)
        out = save_winner_heatmap(out_dir / f"m2_{scope}_winner_map.png", rows, title)
        rows.to_csv(out_dir / f"m2_{scope}_winner_cells.csv", index=False)
        manifest.append(
            {
                "figure": out.name,
                "source": str(audit_dir / "m2_winner_cells.csv"),
                "caption": f"{title}. The map covers rho=0.001..10 and sigma_a=0.05..0.50.",
            }
        )

    if not boundary_observed.empty:
        boundary_observed = boundary_observed.sort_values("r2", ascending=False)
        out = save_metrics_table(
            out_dir / "m2_observed_boundary_fit_table.png",
            boundary_observed[
                [
                    "correction",
                    "challenger",
                    "baseline",
                    "observed_points",
                    "sigma_a_exponent",
                    "r2",
                    "rmse_log10",
                ]
            ],
            title="M2 observed log-rho boundary fits",
            max_rows=16,
        )
        manifest.append(
            {
                "figure": out.name,
                "source": str(audit_dir / "m2_boundary_fit.csv"),
                "caption": "Observed M2 flip-boundary fits; censored and not-reached crossings are excluded from this compact table.",
            }
        )
    return manifest


def _series_by(df: pd.DataFrame, index: str, columns: str, values: str) -> pd.DataFrame:
    frame = df.pivot_table(index=index, columns=columns, values=values, aggfunc="mean")
    return frame.sort_index()


def make_m4_paper_figures(root: Path, out_dir: Path) -> list[dict[str, str]]:
    theory_dir = root / "results" / "theory_m4_paper_r2_highrho"
    manifest: list[dict[str, str]] = []

    error_fit = _read(theory_dir / "m4_error_scaling_fit.csv")
    out = save_metrics_table(
        out_dir / "m4_error_scaling_fit_table.png",
        error_fit[
            [
                "basis",
                "sigma_delta_exponent",
                "sigma_delta_exponent_ci_low",
                "sigma_delta_exponent_ci_high",
                "num_frames_exponent",
                "r2",
            ]
        ],
        title="M4 residual gain error scaling",
        max_rows=12,
    )
    manifest.append(
        {
            "figure": out.name,
            "source": str(theory_dir / "m4_error_scaling_fit.csv"),
            "caption": "Residual gain error fits show sigma_delta exponents near 2 with R2 above 0.9999 across bases.",
        }
    )

    random_summary = _read(theory_dir / "m4_random_frame_scaling_summary.csv")
    random_slice = random_summary[np.isclose(random_summary["sigma_delta"], 0.05)].copy()
    out = save_series_plot(
        out_dir / "m4_random_frame_scaling_sigma0p05.png",
        _series_by(random_slice, "num_frames", "basis", "delta_recon_rel_mse_mean"),
        title="M4 random frame scaling at sigma_delta=0.05",
        x_label="num_frames index",
        y_label="relative MSE",
    )
    manifest.append(
        {
            "figure": out.name,
            "source": str(theory_dir / "m4_random_frame_scaling_summary.csv"),
            "caption": "Random-basis residual gain error decreases as frame count increases at fixed image size and sigma_delta=0.05.",
        }
    )

    random_fit = _read(theory_dir / "m4_random_frame_scaling_fit.csv")
    out = save_metrics_table(
        out_dir / "m4_random_frame_scaling_fit_table.png",
        random_fit[
            [
                "basis",
                "sigma_delta_exponent",
                "num_frames_exponent",
                "num_frames_exponent_ci_low",
                "num_frames_exponent_ci_high",
                "r2",
            ]
        ],
        title="M4 random frame scaling fits",
        max_rows=8,
    )
    manifest.append(
        {
            "figure": out.name,
            "source": str(theory_dir / "m4_random_frame_scaling_fit.csv"),
            "caption": "Fixed-size random-frame fits estimate num_frames exponents near -0.71 to -0.72.",
        }
    )

    energy = _read(theory_dir / "m4_energy_concentration_summary.csv")
    out = save_series_plot(
        out_dir / "m4_top5_energy_concentration.png",
        _series_by(energy, "num_pixels", "basis", "top_5pct_energy_mean"),
        title="M4 top-5% coefficient energy",
        x_label="num_pixels index",
        y_label="energy fraction",
        y_range=(0.0, 1.0),
    )
    manifest.append(
        {
            "figure": out.name,
            "source": str(theory_dir / "m4_energy_concentration_summary.csv"),
            "caption": "DCT/Fourier/Hadamard concentrate object energy in top coefficients; random and SRHT spread it.",
        }
    )

    agc_fit = _read(theory_dir / "m4_agc_window_law_fit.csv")
    out = save_metrics_table(
        out_dir / "m4_agc_window_fit_table.png",
        agc_fit[["basis", "rho_exponent", "sigma_a_exponent", "r2", "rmse_log10"]],
        title="M4 AGC best-window law fits",
        max_rows=8,
    )
    manifest.append(
        {
            "figure": out.name,
            "source": str(theory_dir / "m4_agc_window_law_fit.csv"),
            "caption": "AGC best-window fits are weak for random/SRHT, indicating the current window grid is diagnostic rather than final.",
        }
    )

    summary_path = theory_dir / "m4_key_summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        (out_dir / "m4_key_summary_used.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Render paper-facing M2/M4 figures from audited CSV outputs.")
    parser.add_argument("--output-dir", type=Path, default=Path("results/paper_figures_r1"))
    args = parser.parse_args()

    root = project_root()
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = []
    manifest.extend(make_m2_paper_figures(root, out_dir))
    manifest.extend(make_m4_paper_figures(root, out_dir))
    manifest_df = pd.DataFrame(manifest)
    manifest_df.to_csv(out_dir / "paper_figure_manifest.csv", index=False)
    print(f"wrote {out_dir / 'paper_figure_manifest.csv'}")


if __name__ == "__main__":
    main()
