from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import torch

from src.basis import make_hadamard_paired_basis, make_random_basis, make_srht_paired_basis
from src.paper_experiments import make_paper_objects, rel_mse, write_caption


ROOT = Path(__file__).resolve().parent


def orthogonal_reconstruct(signed_rows: torch.Tensor, coeffs: torch.Tensor) -> torch.Tensor:
    return signed_rows.transpose(0, 1) @ coeffs / float(signed_rows.shape[1])


def main() -> None:
    parser = argparse.ArgumentParser(description="Fig. 4 residual gain error to reconstruction bridge.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "paper_fig4_bridge_r1")
    parser.add_argument("--image-size", type=int, default=32)
    parser.add_argument("--objects", type=int, default=10)
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20240708)
    parser.add_argument("--v-values", default="1e-4,3e-4,1e-3,3e-3,1e-2")
    parser.add_argument("--n-factors", default="1,2,4")
    args = parser.parse_args()

    start = time.time()
    out = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    p = args.image_size * args.image_size
    objects = make_paper_objects(args.objects, image_size=args.image_size, seed=args.seed)
    v_values = [float(x) for x in args.v_values.replace(" ", ",").split(",") if x.strip()]
    n_factors = [int(x) for x in args.n_factors.replace(" ", ",").split(",") if x.strip()]
    rows: List[Dict[str, object]] = []

    had = make_hadamard_paired_basis(p)
    srht = make_srht_paired_basis(p, seed=args.seed)
    for obj in objects:
        target_energy = float(obj.vector.to(dtype=torch.float64).pow(2).mean().item())
        signed_cases = [("orthogonal_inverse", had.signed_rows), ("srht_inverse", srht.signed_rows)]
        for basis_name, signed_rows in signed_cases:
            coeffs = signed_rows @ obj.vector
            for seed_idx in range(args.seeds):
                generator = torch.Generator(device="cpu")
                generator.manual_seed(args.seed + 131 * seed_idx)
                for v in v_values:
                    delta = torch.randn(coeffs.shape, generator=generator, dtype=coeffs.dtype) * (v**0.5)
                    recon = orthogonal_reconstruct(signed_rows, coeffs * (1.0 + delta))
                    measured = rel_mse(recon, obj.vector)
                    rows.append(
                        {
                            "object": obj.name,
                            "family": obj.family,
                            "K_eff": obj.k_eff,
                            "basis": basis_name,
                            "N": int(p),
                            "N_factor": 1,
                            "seed": int(seed_idx),
                            "v": float(v),
                            "rel_mse": measured,
                            "measured_leverage": 1.0,
                            "theory_rel_mse": float(v),
                            "target_energy": target_energy,
                        }
                    )

        for n_factor in n_factors:
            n_frames = int(n_factor * p)
            basis = make_random_basis("uniform", num_pixels=p, num_frames=n_frames, seed=args.seed + n_factor, reconstruction="correlation")
            clean = basis.measure(obj.vector)
            clean_recon = basis.reconstruct(clean)
            for seed_idx in range(args.seeds):
                generator = torch.Generator(device="cpu")
                generator.manual_seed(args.seed + 1709 * seed_idx + n_factor)
                unit_delta = torch.randn(clean.shape, generator=generator, dtype=clean.dtype)
                unit_recon = basis.reconstruct(clean * unit_delta) - clean_recon
                leverage = float(unit_recon.to(dtype=torch.float64).pow(2).mean().item() / max(target_energy, 1.0e-12))
                for v in v_values:
                    generator.manual_seed(args.seed + 3011 * seed_idx + n_factor + int(round(v * 1.0e6)))
                    delta = torch.randn(clean.shape, generator=generator, dtype=clean.dtype) * (v**0.5)
                    recon = basis.reconstruct(clean * (1.0 + delta))
                    residual = recon - clean_recon
                    residual_rel = float(residual.to(dtype=torch.float64).pow(2).mean().item() / max(target_energy, 1.0e-12))
                    rows.append(
                        {
                            "object": obj.name,
                            "family": obj.family,
                            "K_eff": obj.k_eff,
                            "basis": "random_dgi",
                            "N": int(n_frames),
                            "N_factor": int(n_factor),
                            "seed": int(seed_idx),
                            "v": float(v),
                            "rel_mse": residual_rel,
                            "measured_leverage": leverage,
                            "theory_rel_mse": float(leverage * v),
                            "target_energy": target_energy,
                        }
                    )

    df = pd.DataFrame(rows)
    df.to_csv(out / "fig4_bridge.csv", index=False)
    summary = df.groupby(["basis", "N", "N_factor", "v"], as_index=False).agg(
        rel_mse_mean=("rel_mse", "mean"),
        rel_mse_std=("rel_mse", "std"),
        theory_rel_mse_mean=("theory_rel_mse", "mean"),
        measured_leverage_mean=("measured_leverage", "mean"),
    )
    summary.to_csv(out / "fig4_bridge_summary.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.5))
    for basis, group in summary.groupby("basis"):
        curve = group.groupby("v", as_index=False).agg(y=("rel_mse_mean", "mean"), theory=("theory_rel_mse_mean", "mean"))
        axes[0].plot(curve["v"], curve["y"], marker="o", label=basis)
        axes[0].plot(curve["v"], curve["theory"], linestyle="--", alpha=0.7)
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].set_xlabel("residual gain variance v")
    axes[0].set_ylabel("relative MSE contribution")
    axes[0].grid(True, alpha=0.25)
    axes[0].legend(frameon=False, fontsize=8)

    random_summary = summary[summary["basis"] == "random_dgi"]
    for v, group in random_summary.groupby("v"):
        axes[1].plot(group["N"], group["rel_mse_mean"], marker="o", label=f"v={v:g}")
    axes[1].set_xscale("log", base=2)
    axes[1].set_yscale("log")
    axes[1].set_xlabel("random frames N")
    axes[1].set_ylabel("random-DGI residual contribution")
    axes[1].grid(True, alpha=0.25)
    axes[1].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "fig4_relmse_theory_vs_sim.png", dpi=200)
    plt.close(fig)

    write_caption(
        out / "fig4_caption.md",
        "Fig. 4 Reconstruction Bridge",
        [
            "Known residual gain variance is injected after noiseless bucket formation.",
            "Orthogonal signed inverse controls are compared with random-DGI residual contributions using measured leverage constants.",
            f"Rows: {len(df)}. Runtime seconds: {time.time() - start:.2f}.",
        ],
    )
    (out / "run_manifest.json").write_text(
        json.dumps({"args": vars(args), "rows": len(df)}, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"Fig4 complete rows={len(df)} output={out} runtime={time.time() - start:.2f}s")


if __name__ == "__main__":
    main()
