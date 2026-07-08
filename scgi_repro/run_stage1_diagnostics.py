from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
import pandas as pd

from src.config_utils import load_config, project_root
from src.data_sim import simulate_scgi_dataset
from src.metrics import normal_ks_test, slope_vs_index
from src.plotting import save_metrics_table, save_series_plot


def _hist_frame(values: list[tuple[str, np.ndarray]], bins: int = 40) -> pd.DataFrame:
    finite = np.concatenate([v[np.isfinite(v)] for _name, v in values])
    low, high = float(finite.min()), float(finite.max())
    if high <= low:
        high = low + 1.0
    centers = None
    data: dict[str, np.ndarray] = {}
    for name, arr in values:
        counts, edges = np.histogram(arr[np.isfinite(arr)], bins=bins, range=(low, high), density=True)
        centers = 0.5 * (edges[:-1] + edges[1:])
        data[name] = counts
    frame = pd.DataFrame(data)
    frame.index = centers
    return frame


def _downsample_series(values: np.ndarray, points: int = 256) -> np.ndarray:
    if values.size <= points:
        return values
    idx = np.linspace(0, values.size - 1, points).round().astype(int)
    return values[idx]


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 1 data-simulation diagnostics.")
    parser.add_argument("--profile", default="smoke")
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--output-dir", type=Path, default=Path("results/stage_1"))
    args = parser.parse_args()

    root = project_root()
    cfg = load_config(root / "config.yaml", args.profile)
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir / cfg["profile"]
    out_dir.mkdir(parents=True, exist_ok=True)

    data = simulate_scgi_dataset(cfg)
    sample_count = max(1, min(int(args.samples), int(data.b_static.shape[0])))
    rows = []
    hist_values = []
    dynamic_curves: dict[str, np.ndarray] = {}
    factor_curves: dict[str, np.ndarray] = {}

    for idx in range(sample_count):
        b = data.b_static[idx]
        r = data.r_dynamic[idx]
        factors = data.y_factors[idx]
        ks_d, ks_p = normal_ks_test(b)
        rows.append(
            {
                "sample": idx,
                "lambda": float(data.lambdas[idx].detach().cpu()),
                "b_mean": float(b.mean().detach().cpu()),
                "b_var": float(b.var(unbiased=False).detach().cpu()),
                "b_ks_d": ks_d,
                "b_ks_p": ks_p,
                "r_slope": slope_vs_index(r),
                "factor_start": float(factors[0].detach().cpu()),
                "factor_end": float(factors[-1].detach().cpu()),
            }
        )
        hist_values.append((f"B sample {idx}", b.detach().cpu().numpy().reshape(-1)))
        dynamic_curves[f"R sample {idx}"] = _downsample_series(r.detach().cpu().numpy().reshape(-1))
        factor_curves[f"a sample {idx}"] = _downsample_series(factors.detach().cpu().numpy().reshape(-1))

    diagnostics = pd.DataFrame(rows)
    diagnostics.to_csv(out_dir / "stage1_sample_diagnostics.csv", index=False)
    save_metrics_table(
        out_dir / "stage1_sample_diagnostics_table.png",
        diagnostics[["sample", "lambda", "b_ks_p", "r_slope", "factor_end"]],
        title="Stage 1 sample diagnostics",
        max_rows=sample_count,
    )
    save_series_plot(
        out_dir / "stage1_b_histograms.png",
        _hist_frame(hist_values),
        title="Stage 1 static bucket histograms",
        x_label="normalized bucket",
        y_label="density",
    )
    save_series_plot(
        out_dir / "stage1_r_dynamic_curves.png",
        pd.DataFrame(dynamic_curves),
        title="Stage 1 dynamic bucket curves",
        x_label="downsampled measurement index",
        y_label="normalized R",
    )
    save_series_plot(
        out_dir / "stage1_gain_curves.png",
        pd.DataFrame(factor_curves),
        title="Stage 1 dynamic gain curves",
        x_label="downsampled measurement index",
        y_label="a_n",
    )

    lambda_counts, lambda_edges = np.histogram(data.lambdas.detach().cpu().numpy(), bins=min(30, max(5, data.lambdas.numel())))
    lambda_centers = 0.5 * (lambda_edges[:-1] + lambda_edges[1:])
    lambda_frame = pd.DataFrame({"lambda_count": lambda_counts}, index=lambda_centers)
    save_series_plot(
        out_dir / "stage1_lambda_distribution.png",
        lambda_frame,
        title="Stage 1 lambda distribution",
        x_label="lambda",
        y_label="count",
    )

    summary = {
        "profile": cfg["profile"],
        "device": str(data.images.device),
        "samples": int(data.images.shape[0]),
        "image_size": data.image_size,
        "patterns": int(data.patterns.shape[0]),
        "sampled_for_plots": sample_count,
        "ks_pass_rate_plotted": float((diagnostics["b_ks_p"] > 0.05).mean()),
        "lambda_min": float(data.lambdas.min().detach().cpu()),
        "lambda_max": float(data.lambdas.max().detach().cpu()),
        "outputs": str(out_dir),
    }
    with (out_dir / "stage1_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary.keys()))
        writer.writeheader()
        writer.writerow(summary)
    print(f"wrote {out_dir}")


if __name__ == "__main__":
    main()
