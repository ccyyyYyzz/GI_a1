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

from src.paper_experiments import (
    logspace_windows,
    make_paper_basis,
    make_paper_objects,
    make_shared_channel,
    mean_agc_gain,
    scale_aligned_gain_error,
    write_caption,
)


ROOT = Path(__file__).resolve().parent


def fit_slope(group: pd.DataFrame, max_w: int) -> float:
    subset = group[(group["W"] <= max_w) & (group["gain_rel_err"] > 0)].copy()
    if len(subset) < 2:
        return float("nan")
    x = np.log10(subset["W"].to_numpy(dtype=float))
    y = np.log10(subset["gain_rel_err"].to_numpy(dtype=float))
    return float(np.polyfit(x, y, deg=1)[0])


def run(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    image_size = int(args.image_size)
    p = image_size * image_size
    objects = make_paper_objects(args.objects, image_size=image_size, seed=args.seed)
    basis_items = [
        (basis_name, make_paper_basis(basis_name, p, seed=args.seed + 17 * idx))
        for idx, basis_name in enumerate(args.bases)
    ]
    num_frames = min(basis.num_frames for _, basis in basis_items)
    windows = [w for w in logspace_windows(num_frames, min_window=args.min_window) if w <= num_frames // 2]

    rows: List[Dict[str, object]] = []
    for rho in args.rho:
        channels = {
            seed_idx: make_shared_channel(num_frames, rho=float(rho), sigma_a=args.sigma_a, seed=args.seed + 1009 * seed_idx)
            for seed_idx in range(args.seeds)
        }
        for requested_basis, basis in basis_items:
            patterns = basis.patterns[:num_frames].cpu()
            for obj in objects:
                ideal = (patterns @ obj.vector).to(dtype=torch.float32)
                carrier_mean = float(ideal.mean().item())
                carrier_cv = float((ideal.std(unbiased=False) / ideal.mean().clamp_min(1.0e-8)).item())
                for seed_idx, gains in channels.items():
                    observed = ideal * gains
                    for window in windows:
                        gain_hat = mean_agc_gain(observed, window)
                        rows.append(
                            {
                                "object": obj.name,
                                "family": obj.family,
                                "K_eff": obj.k_eff,
                                "basis": basis.name,
                                "requested_basis": requested_basis,
                                "rho": float(rho),
                                "s": float(args.sigma_a),
                                "seed": int(seed_idx),
                                "W": int(window),
                                "num_frames": int(num_frames),
                                "carrier_mean": carrier_mean,
                                "carrier_cv": carrier_cv,
                                "gain_rel_err": scale_aligned_gain_error(gain_hat, gains),
                                "theory_variance_cv2_over_w": float(carrier_cv * carrier_cv / max(1, window)),
                            }
                        )

    df = pd.DataFrame(rows)
    slope_rows: List[Dict[str, object]] = []
    fit_max_w = int(args.slope_max_window or max(args.min_window * 4, min(32, num_frames // 16)))
    for (basis, rho, obj), group in df.groupby(["basis", "rho", "object"]):
        slope_rows.append(
            {
                "basis": basis,
                "rho": rho,
                "object": obj,
                "fit_max_W": fit_max_w,
                "slope_log_err_vs_log_W": fit_slope(group, fit_max_w),
            }
        )
    slopes = pd.DataFrame(slope_rows)

    spread_rows: List[Dict[str, object]] = []
    for (basis, rho, window), group in df.groupby(["basis", "rho", "W"]):
        means = group.groupby("object")["gain_rel_err"].mean()
        spread_rows.append(
            {
                "basis": basis,
                "rho": rho,
                "W": int(window),
                "object_mean_err": float(means.mean()),
                "object_std_err": float(means.std(ddof=0)),
                "relative_spread": float(means.std(ddof=0) / max(means.mean(), 1.0e-12)),
            }
        )
    spread = pd.DataFrame(spread_rows)
    summary = slopes.merge(spread, how="left", on=["basis", "rho"])
    return df, summary


def plot_outputs(df: pd.DataFrame, summary: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    bases = list(df["basis"].drop_duplicates())
    rhos = list(df["rho"].drop_duplicates())
    fig, axes = plt.subplots(len(rhos), len(bases), figsize=(4.3 * len(bases), 3.4 * len(rhos)), squeeze=False)
    for r_i, rho in enumerate(rhos):
        for b_i, basis in enumerate(bases):
            ax = axes[r_i][b_i]
            sub = df[(df["rho"] == rho) & (df["basis"] == basis)]
            for obj, group in sub.groupby("object"):
                curve = group.groupby("W", as_index=False)["gain_rel_err"].mean()
                ax.plot(curve["W"], curve["gain_rel_err"], alpha=0.55, linewidth=1.0)
            mean_curve = sub.groupby("W", as_index=False)["gain_rel_err"].mean()
            ax.plot(mean_curve["W"], mean_curve["gain_rel_err"], color="black", linewidth=2.2, label="mean")
            if len(mean_curve) > 0:
                w0 = float(mean_curve["W"].iloc[0])
                e0 = float(mean_curve["gain_rel_err"].iloc[0])
                ref = e0 * np.sqrt(w0 / mean_curve["W"].to_numpy(dtype=float))
                ax.plot(mean_curve["W"], ref, color="tab:red", linestyle="--", linewidth=1.2, label="W^-1/2")
            ax.set_xscale("log", base=2)
            ax.set_yscale("log")
            ax.set_title(f"{basis}, rho={rho:g}")
            ax.set_xlabel("AGC window W")
            ax.set_ylabel("scale-aligned gain error")
            ax.grid(True, alpha=0.25)
            if r_i == 0 and b_i == 0:
                ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "fig3a_error_vs_W.png", dpi=200)
    plt.close(fig)

    best = df.loc[df.groupby(["basis", "rho", "object"])["gain_rel_err"].idxmin()].copy()
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for basis, group in best.groupby("basis"):
        ax.scatter(group["K_eff"], group["gain_rel_err"], label=basis, s=34, alpha=0.85)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("K_eff")
    ax.set_ylabel("best-window gain error")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "fig3b_objectindep_vs_Keff.png", dpi=200)
    plt.close(fig)

    summary.to_csv(output_dir / "fig3_gain_error_summary.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fig. 3 blind gain-estimation error vs AGC window.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "paper_fig3_gain_error_r1")
    parser.add_argument("--image-size", type=int, default=32)
    parser.add_argument("--objects", type=int, default=10)
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20240708)
    parser.add_argument("--rho", type=float, nargs="+", default=[0.001, 0.01])
    parser.add_argument("--sigma-a", type=float, default=0.1)
    parser.add_argument(
        "--bases",
        nargs="+",
        default=["random_uniform", "random_binary", "hadamard_ordered", "hadamard_shuffled", "srht_paired"],
    )
    parser.add_argument("--min-window", type=int, default=4)
    parser.add_argument("--slope-max-window", type=int, default=0)
    args = parser.parse_args()

    start = time.time()
    out = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    df, summary = run(args)
    df.to_csv(out / "fig3_gain_est_error.csv", index=False)
    plot_outputs(df, summary, out)
    write_caption(
        out / "fig3_caption.md",
        "Fig. 3 Blind Gain Identifiability",
        [
            "Sliding-window AGC is applied identically to every basis and evaluated only on gain recovery.",
            "Random and SRHT-like bases should approach the W^-1/2 variance law in the slow-drift regime, while ordered Hadamard traces expose object-dependent carrier nonstationarity.",
            f"Rows: {len(df)}. Runtime seconds: {time.time() - start:.2f}.",
        ],
    )
    (out / "run_manifest.json").write_text(
        json.dumps(
            {"args": vars(args), "rows": int(len(df)), "runtime_seconds": round(time.time() - start, 3)},
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    print(f"Fig3 complete rows={len(df)} output={out} runtime={time.time() - start:.2f}s")


if __name__ == "__main__":
    main()
