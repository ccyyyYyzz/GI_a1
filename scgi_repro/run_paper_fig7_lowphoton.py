from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch

from src.mechanisms import moving_average_1d
from src.paper_experiments import (
    make_paper_basis,
    make_paper_objects,
    make_shared_channel,
    scale_aligned_gain_error,
    write_caption,
)


ROOT = Path(__file__).resolve().parent


def estimate_from_counts(counts: torch.Tensor, method: str, window: int, alpha: float) -> torch.Tensor:
    values = counts.reshape(-1).to(dtype=torch.float32)
    if method == "soft_log":
        transformed = torch.log(values + float(alpha))
        smooth = moving_average_1d(transformed, window)
        gain_hat = torch.exp(smooth - smooth.mean())
    elif method == "naive_log":
        transformed = torch.log(values.clamp_min(1.0e-3))
        smooth = moving_average_1d(transformed, window)
        gain_hat = torch.exp(smooth - smooth.mean())
    elif method == "anscombe":
        transformed = 2.0 * torch.sqrt(values + 0.375)
        smooth = moving_average_1d(transformed, window)
        gain_hat = (smooth / smooth.mean().clamp_min(1.0e-8)).pow(2)
    else:
        raise ValueError(method)
    return gain_hat / gain_hat.mean().clamp_min(1.0e-8)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fig. 7 low-photon gain estimation.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "paper_fig7_lowphoton_r1")
    parser.add_argument("--image-size", type=int, default=32)
    parser.add_argument("--objects", type=int, default=10)
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20240708)
    parser.add_argument("--rho", type=float, default=0.001)
    parser.add_argument("--sigma-a", type=float, default=0.1)
    parser.add_argument("--window", type=int, default=64)
    parser.add_argument("--alpha", type=float, default=0.5)
    parser.add_argument("--photon-budgets", default="0.25,0.5,1,2,4,8,16,32,64,128")
    args = parser.parse_args()

    start = time.time()
    out = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    p = args.image_size * args.image_size
    basis = make_paper_basis("random_uniform", p, seed=args.seed)
    objects = make_paper_objects(args.objects, image_size=args.image_size, seed=args.seed)
    budgets = [float(x) for x in args.photon_budgets.replace(" ", ",").split(",") if x.strip()]
    methods = ["soft_log", "naive_log", "anscombe"]
    rows: List[Dict[str, object]] = []
    for obj in objects:
        carrier = (basis.patterns @ obj.vector).cpu().to(dtype=torch.float32)
        carrier = carrier / carrier.mean().clamp_min(1.0e-8)
        for seed_idx in range(args.seeds):
            gains = make_shared_channel(basis.num_frames, rho=args.rho, sigma_a=args.sigma_a, seed=args.seed + 701 * seed_idx)
            for budget in budgets:
                lam = (float(budget) * gains * carrier).clamp_min(0.0)
                generator = torch.Generator(device="cpu")
                generator.manual_seed(args.seed + 9001 * seed_idx + int(round(1000 * budget)))
                counts = torch.poisson(lam, generator=generator)
                zero_fraction = float((counts <= 0).to(dtype=torch.float32).mean().item())
                lambda_bar = float(lam.mean().item())
                for method in methods:
                    gain_hat = estimate_from_counts(counts, method=method, window=args.window, alpha=args.alpha)
                    rows.append(
                        {
                            "object": obj.name,
                            "family": obj.family,
                            "K_eff": obj.k_eff,
                            "basis": basis.name,
                            "rho": float(args.rho),
                            "s": float(args.sigma_a),
                            "seed": int(seed_idx),
                            "W": int(args.window),
                            "photon_budget": float(budget),
                            "lambda_bar": lambda_bar,
                            "zero_fraction": zero_fraction,
                            "method": method,
                            "gain_rel_mse": scale_aligned_gain_error(gain_hat, gains) ** 2,
                            "fisher_reference": float(1.0 / max(args.window * lambda_bar, 1.0e-12)),
                        }
                    )
    df = pd.DataFrame(rows)
    df.to_csv(out / "fig7_lowphoton.csv", index=False)

    summary = df.groupby(["method", "photon_budget", "lambda_bar"], as_index=False).agg(
        gain_rel_mse_mean=("gain_rel_mse", "mean"),
        gain_rel_mse_std=("gain_rel_mse", "std"),
        zero_fraction_mean=("zero_fraction", "mean"),
        fisher_reference=("fisher_reference", "mean"),
    )
    summary.to_csv(out / "fig7_lowphoton_summary.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for method, group in summary.groupby("method"):
        curve = group.groupby("photon_budget", as_index=False).agg(y=("gain_rel_mse_mean", "mean"), yerr=("gain_rel_mse_std", "mean"))
        ax.errorbar(
            curve["photon_budget"],
            curve["y"],
            yerr=curve["yerr"].fillna(0.0),
            marker="o",
            capsize=2,
            label=method,
        )
    ref = summary.groupby("photon_budget", as_index=False)["fisher_reference"].mean()
    ax.plot(ref["photon_budget"], ref["fisher_reference"], linestyle="--", color="black", label="1/(W lambda)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("mean photon budget")
    ax.set_ylabel("gain MSE")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out / "fig7_gainMSE_vs_photon.png", dpi=200)
    plt.close(fig)

    write_caption(
        out / "fig7_caption.md",
        "Fig. 7 Low-Photon Gain Estimation",
        [
            "Poisson bucket counts are evaluated under identical random-basis carriers and shared gain traces.",
            "Soft-log, naive clipped log, and Anscombe transforms are compared against the 1/(W lambda) Fisher-rate reference.",
            f"Rows: {len(df)}. Runtime seconds: {time.time() - start:.2f}.",
        ],
    )
    (out / "run_manifest.json").write_text(
        json.dumps({"args": vars(args), "rows": len(df)}, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"Fig7 complete rows={len(df)} output={out} runtime={time.time() - start:.2f}s")


if __name__ == "__main__":
    main()
