from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch

from src.paper_experiments import make_paper_basis, make_paper_objects, moving_average_1d, write_caption


ROOT = Path(__file__).resolve().parent


def ks_2sample(x: torch.Tensor, y: torch.Tensor) -> tuple[float, float]:
    x = torch.sort(x.reshape(-1).to(dtype=torch.float64))[0]
    y = torch.sort(y.reshape(-1).to(dtype=torch.float64))[0]
    if x.numel() < 2 or y.numel() < 2:
        return float("nan"), float("nan")
    values = torch.cat([x, y])
    cdf_x = torch.searchsorted(x, values, right=True).to(dtype=torch.float64) / x.numel()
    cdf_y = torch.searchsorted(y, values, right=True).to(dtype=torch.float64) / y.numel()
    d = float((cdf_x - cdf_y).abs().max().item())
    n_eff = x.numel() * y.numel() / (x.numel() + y.numel())
    p = min(1.0, max(0.0, 2.0 * math.exp(-2.0 * n_eff * d * d)))
    return d, p


def main() -> None:
    parser = argparse.ArgumentParser(description="Fig. 2 carrier stationarity diagnostics.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "paper_fig2_stationarity_r1")
    parser.add_argument("--image-size", type=int, default=32)
    parser.add_argument("--objects", type=int, default=6)
    parser.add_argument("--seed", type=int, default=20240708)
    parser.add_argument("--window", type=int, default=64)
    parser.add_argument(
        "--bases",
        nargs="+",
        default=["random_uniform", "random_binary", "hadamard_ordered", "hadamard_shuffled", "srht_paired"],
    )
    args = parser.parse_args()

    start = time.time()
    out = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    p = args.image_size * args.image_size
    objects = make_paper_objects(args.objects, image_size=args.image_size, seed=args.seed)
    rows: List[Dict[str, object]] = []
    trace_rows: List[Dict[str, object]] = []
    for b_idx, basis_name in enumerate(args.bases):
        basis = make_paper_basis(basis_name, p, seed=args.seed + 37 * b_idx)
        for obj in objects:
            carrier = (basis.patterns @ obj.vector).cpu().to(dtype=torch.float32)
            running = moving_average_1d(carrier, args.window)
            cv = float((carrier.std(unbiased=False) / carrier.mean().clamp_min(1.0e-8)).item())
            segments = torch.chunk(carrier, 8)
            ks_values = [ks_2sample(segments[i], segments[i + 1]) for i in range(len(segments) - 1)]
            rows.append(
                {
                    "object": obj.name,
                    "family": obj.family,
                    "K_eff": obj.k_eff,
                    "basis": basis.name,
                    "requested_basis": basis_name,
                    "num_frames": basis.num_frames,
                    "window": int(args.window),
                    "carrier_mean": float(carrier.mean().item()),
                    "carrier_cv": cv,
                    "running_mean_cv": float((running.std(unbiased=False) / running.mean().clamp_min(1.0e-8)).item()),
                    "adjacent_window_ks_d_mean": float(np.mean([d for d, _ in ks_values])),
                    "adjacent_window_ks_p_median": float(np.median([pval for _, pval in ks_values])),
                }
            )
            step = max(1, carrier.numel() // 256)
            for idx in range(0, carrier.numel(), step):
                trace_rows.append(
                    {
                        "object": obj.name,
                        "basis": basis.name,
                        "frame": int(idx),
                        "carrier": float(carrier[idx].item()),
                        "running_mean": float(running[idx].item()),
                    }
                )
    df = pd.DataFrame(rows)
    traces = pd.DataFrame(trace_rows)
    df.to_csv(out / "fig2_stationarity.csv", index=False)
    traces.to_csv(out / "fig2_stationarity_traces.csv", index=False)

    plot_objects = list(df.sort_values("K_eff")["object"].drop_duplicates().iloc[[0, -1]] if len(df["object"].unique()) > 1 else df["object"].drop_duplicates())
    plot_bases = list(df["basis"].drop_duplicates())[:4]
    fig, axes = plt.subplots(len(plot_objects), len(plot_bases), figsize=(4.0 * len(plot_bases), 3.0 * len(plot_objects)), squeeze=False)
    for i, obj in enumerate(plot_objects):
        for j, basis in enumerate(plot_bases):
            ax = axes[i][j]
            sub = traces[(traces["object"] == obj) & (traces["basis"] == basis)]
            ax.plot(sub["frame"], sub["carrier"], linewidth=0.8, alpha=0.45, label="B_n")
            ax.plot(sub["frame"], sub["running_mean"], linewidth=1.8, label="running mean")
            ax.set_title(f"{basis}\n{obj}")
            ax.grid(True, alpha=0.25)
            if i == 0 and j == 0:
                ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "fig2_carrier_traces.png", dpi=200)
    plt.close(fig)

    write_caption(
        out / "fig2_caption.md",
        "Fig. 2 Carrier Stationarity",
        [
            "Noiseless bucket carriers B_n are audited before applying any dynamic gain.",
            "Randomized bases should have flat running means and weak adjacent-window distribution shifts; ordered Hadamard carriers reveal object-dependent temporal envelopes.",
            f"Rows: {len(df)}. Runtime seconds: {time.time() - start:.2f}.",
        ],
    )
    (out / "run_manifest.json").write_text(
        json.dumps({"args": vars(args), "rows": len(df)}, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"Fig2 complete rows={len(df)} output={out} runtime={time.time() - start:.2f}s")


if __name__ == "__main__":
    main()
