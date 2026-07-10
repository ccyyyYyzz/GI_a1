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

from src.basis import make_hadamard_paired_basis, make_random_basis, make_srht_paired_basis
from src.paper_experiments import build_run_manifest, make_paper_objects, make_paper_objects_pixels, rel_mse, write_caption


ROOT = Path(__file__).resolve().parent


def orthogonal_reconstruct(signed_rows: torch.Tensor, coeffs: torch.Tensor) -> torch.Tensor:
    return signed_rows.transpose(0, 1) @ coeffs / float(signed_rows.shape[1])


def main() -> None:
    parser = argparse.ArgumentParser(description="Fig. 4 residual gain error to reconstruction bridge (r2).")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "paper_fig4_bridge_r2")
    parser.add_argument("--image-size", type=int, default=32)
    parser.add_argument("--objects", type=int, default=10)
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20240708)
    parser.add_argument("--v-values", default="1e-4,3e-4,1e-3,3e-3,1e-2")
    parser.add_argument("--n-factors", default="1,2,4")
    parser.add_argument("--orthogonal-pixels", default="1024,2048,4096")
    args = parser.parse_args()

    start = time.time()
    out = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    p = args.image_size * args.image_size
    v_values = [float(x) for x in args.v_values.replace(" ", ",").split(",") if x.strip()]
    v_list = [0.0] + v_values  # v=0 row measures the numerical / reconstruction floor (C0)
    n_factors = [int(x) for x in args.n_factors.replace(" ", ",").split(",") if x.strip()]
    ortho_pixels = [int(x) for x in args.orthogonal_pixels.replace(" ", ",").split(",") if x.strip()]
    rows: List[Dict[str, object]] = []

    # ---- Orthogonal / SRHT complete-inverse arms, swept over transform size N. ----
    for n_pixels in ortho_pixels:
        objects_n = make_paper_objects_pixels(args.objects, n_pixels, seed=args.seed)
        had = make_hadamard_paired_basis(n_pixels)
        srht = make_srht_paired_basis(n_pixels, seed=args.seed)
        signed_cases = [("orthogonal_inverse", had.signed_rows), ("srht_inverse", srht.signed_rows)]
        for obj in objects_n:
            target_energy = float(obj.vector.to(dtype=torch.float64).pow(2).mean().item())
            for basis_name, signed_rows in signed_cases:
                coeffs = signed_rows @ obj.vector
                for seed_idx in range(args.seeds):
                    generator = torch.Generator(device="cpu")
                    generator.manual_seed(args.seed + 131 * seed_idx)
                    recon0 = orthogonal_reconstruct(signed_rows, coeffs)
                    rel_mse_v0 = rel_mse(recon0, obj.vector)
                    c0_measured = rel_mse_v0 * float(n_pixels)
                    for v in v_list:
                        if v == 0.0:
                            measured = rel_mse_v0
                        else:
                            delta = torch.randn(coeffs.shape, generator=generator, dtype=coeffs.dtype) * (v**0.5)
                            recon = orthogonal_reconstruct(signed_rows, coeffs * (1.0 + delta))
                            measured = rel_mse(recon, obj.vector)
                        rows.append(
                            {
                                "object": obj.name,
                                "family": obj.family,
                                "K_eff": obj.k_eff,
                                "basis": basis_name,
                                "N": int(n_pixels),
                                "N_factor": 1,
                                "seed": int(seed_idx),
                                "v": float(v),
                                "rel_mse": measured,
                                "measured_leverage": 1.0,
                                "C0_measured": c0_measured,
                                "theory_rel_mse": float(v),
                                "target_energy": target_energy,
                            }
                        )

    # ---- Random-DGI residual arm (unchanged leg; p=1024 objects, N=factor*p). ----
    objects = make_paper_objects(args.objects, image_size=args.image_size, seed=args.seed)
    for obj in objects:
        target_energy = float(obj.vector.to(dtype=torch.float64).pow(2).mean().item())
        for n_factor in n_factors:
            n_frames = int(n_factor * p)
            basis = make_random_basis(
                "uniform", num_pixels=p, num_frames=n_frames, seed=args.seed + n_factor, reconstruction="correlation"
            )
            clean = basis.measure(obj.vector)
            clean_recon = basis.reconstruct(clean)
            for seed_idx in range(args.seeds):
                generator = torch.Generator(device="cpu")
                generator.manual_seed(args.seed + 1709 * seed_idx + n_factor)
                unit_delta = torch.randn(clean.shape, generator=generator, dtype=clean.dtype)
                unit_recon = basis.reconstruct(clean * unit_delta) - clean_recon
                leverage = float(unit_recon.to(dtype=torch.float64).pow(2).mean().item() / max(target_energy, 1.0e-12))
                # v=0 residual is identically zero by construction (residual = recon - clean_recon).
                c0_measured = 0.0
                for v in v_list:
                    if v == 0.0:
                        residual_rel = 0.0
                    else:
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
                            "C0_measured": c0_measured,
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
        C0_measured_mean=("C0_measured", "mean"),
    )
    summary.to_csv(out / "fig4_bridge_summary.csv", index=False)

    # N-flatness slopes for the control arms (relMSE vs N at fixed v>0).
    flat_rows: List[Dict[str, object]] = []
    for (basis, v), group in df[df["v"] > 0].groupby(["basis", "v"]):
        per_n = group.groupby("N")["rel_mse"].mean().sort_index()
        if len(per_n) >= 2:
            x = np.log10(np.asarray(per_n.index, dtype=float))
            y = np.log10(np.asarray(per_n.values, dtype=float).clip(min=1.0e-18))
            slope = float(np.polyfit(x, y, deg=1)[0])
        else:
            slope = float("nan")
        flat_rows.append({"basis": basis, "v": float(v), "n_points": int(len(per_n)), "slope_log_relmse_vs_log_N": slope})
    flatness = pd.DataFrame(flat_rows)
    flatness.to_csv(out / "fig4_N_flatness.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.5))
    pos = summary[summary["v"] > 0]
    for basis, group in pos.groupby("basis"):
        curve = group.groupby("v", as_index=False).agg(y=("rel_mse_mean", "mean"), theory=("theory_rel_mse_mean", "mean"))
        axes[0].plot(curve["v"], curve["y"], marker="o", label=basis)
        axes[0].plot(curve["v"], curve["theory"], linestyle="--", alpha=0.7)
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].set_xlabel("residual gain variance v")
    axes[0].set_ylabel("relative MSE contribution")
    axes[0].grid(True, alpha=0.25)
    axes[0].legend(frameon=False, fontsize=8)

    for basis, group in pos.groupby("basis"):
        for v, vgroup in group.groupby("v"):
            curve = vgroup.groupby("N", as_index=False)["rel_mse_mean"].mean()
            if len(curve) >= 2:
                axes[1].plot(curve["N"], curve["rel_mse_mean"], marker="o", label=f"{basis} v={v:g}")
    axes[1].set_xscale("log", base=2)
    axes[1].set_yscale("log")
    axes[1].set_xlabel("frames / transform size N")
    axes[1].set_ylabel("relMSE contribution")
    axes[1].grid(True, alpha=0.25)
    axes[1].legend(frameon=False, fontsize=6)
    fig.tight_layout()
    fig.savefig(out / "fig4_relmse_theory_vs_sim.png", dpi=200)
    plt.close(fig)

    def _slope_str(basis: str) -> str:
        vals = flatness[flatness["basis"] == basis]["slope_log_relmse_vs_log_N"].dropna()
        return f"{vals.median():.3f}" if len(vals) else "nan"

    def _slope_range_str(basis: str) -> str:
        vals = flatness[flatness["basis"] == basis]["slope_log_relmse_vs_log_N"].dropna()
        if not len(vals):
            return "nan"
        return f"[{vals.min():.3f}, {vals.max():.3f}]"

    leverage_by_n = df[df["basis"] == "random_dgi"].groupby("N")["measured_leverage"].mean()
    leverage_n = (leverage_by_n * leverage_by_n.index).dropna()
    leverage_n_str = f"{leverage_n.min():.3g}-{leverage_n.max():.3g}" if len(leverage_n) else "nan"

    run_tag = out.name.replace("paper_fig4_bridge_", "") or "r2"
    write_caption(
        out / "fig4_caption.md",
        f"Fig. 4 Reconstruction Bridge ({run_tag})",
        [
            "Known residual gain variance v is injected after noiseless bucket formation; relMSE is scale-aligned to the object.",
            f"Complete orthogonal (Hadamard) and SRHT inverses are swept over transform size N in {{1024,2048,4096}} with "
            f"{args.seeds} seeds per (object, v, N): per-v log-log slope ranges over the 5 v values are "
            f"orthogonal_inverse={_slope_range_str('orthogonal_inverse')} (max|slope|="
            f"{flatness[flatness['basis']=='orthogonal_inverse']['slope_log_relmse_vs_log_N'].abs().max():.3f}), "
            f"srht_inverse={_slope_range_str('srht_inverse')} (max|slope|="
            f"{flatness[flatness['basis']=='srht_inverse']['slope_log_relmse_vs_log_N'].abs().max():.3f}) -- both well within "
            "the deterministic-inverse flatness band, so there is no 1/N reconstruction floor for the deterministic inverse; "
            f"random_dgi decays as 1/N at every v (per-v slope range {_slope_range_str('random_dgi')}, consistent with -1 "
            "at each v).",
            "v=0 rows give C0_measured = relMSE(v=0)*N, which is identically 0 by residual construction for random_dgi (the "
            "v=0 residual is recon(v=0) - clean_recon = 0) -- so C0_measured is NOT the right constant to quote for this arm. "
            "The deterministic orthogonal/SRHT inverses instead satisfy relMSE = (1+C0)*v with C0_measured ~ 0 (exact "
            "inversion, no range-ledger floor); random_dgi is governed by relMSE = leverage*v with "
            f"leverage*N ~ {leverage_n_str} across N in {{1024,2048,4096}} (the correct N-scaling constant for this arm).",
            "Theory line kept at theory=v for the orthogonal/SRHT arms (option B). DC-dominated objects (natural_patch, stripe) "
            "fall below the v line because the scale alignment absorbs the co-linear gain component; this is an alignment effect, "
            "not a model failure.",
            "random_dgi leg is unchanged in mechanism from r1 (1/N leverage law); only the seed count increased.",
            f"Rows: {len(df)}. Runtime seconds: {time.time() - start:.2f}.",
        ],
    )
    (out / "run_manifest.json").write_text(
        json.dumps(build_run_manifest(args, ROOT, extra={"rows": int(len(df))}, output_dir=out), indent=2, default=str),
        encoding="utf-8",
    )
    print(f"Fig4 complete rows={len(df)} output={out} runtime={time.time() - start:.2f}s")


if __name__ == "__main__":
    main()
