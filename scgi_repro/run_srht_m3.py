from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import torch

from run_mechanism_m1 import make_synthetic_objects, simulate_and_reconstruct
from src.basis import MeasurementBasis, hadamard_matrix, interleave_paired_frames
from src.config_utils import load_config, project_root


def make_variant(name: str, num_pixels: int, seed: int) -> MeasurementBasis:
    g = torch.Generator(device="cpu").manual_seed(seed)
    h = hadamard_matrix(num_pixels)
    signs = torch.randint(0, 2, (num_pixels,), generator=g).mul(2).sub(1).float()
    perm = torch.randperm(num_pixels, generator=g)
    if name == "hadamard_ordered":
        rows = h
    elif name == "perm_only":
        rows = h.index_select(0, perm)
    elif name == "sign_only":
        rows = h * signs.reshape(1, -1)
    elif name == "srht_full":
        rows = h.index_select(0, perm) * signs.reshape(1, -1)
    else:
        raise ValueError(name)
    return MeasurementBasis(
        name=name,
        patterns=interleave_paired_frames(rows),
        paired=True,
        signed_rows=rows,
        row_indices=perm if "perm" in name or name == "srht_full" else torch.arange(num_pixels),
        srht_signs=signs if "sign" in name or name == "srht_full" else None,
        metadata={"ablation": name},
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Compact M3 SRHT ablation.")
    parser.add_argument("--profile", default="smoke")
    parser.add_argument("--objects", type=int, default=1)
    parser.add_argument("--seeds", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=Path("results/srht_m3"))
    parser.add_argument("--no-findings", action="store_true")
    args = parser.parse_args()

    root = project_root()
    cfg = load_config(root / "config.yaml", args.profile)
    mech = cfg.get("mechanism", {})
    h = int(mech.get("image_size", 32))
    p = h * h
    objects = make_synthetic_objects(args.objects, h, int(cfg.get("seed", 0)))
    rho_values = list(mech.get("rho_values", [0.001, 0.01, 0.1, 1.0]))[:4]
    sigma_a = float(list(mech.get("sigma_a_values", [0.15]))[min(1, len(mech.get("sigma_a_values", [0.15])) - 1)])
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for variant in ["hadamard_ordered", "perm_only", "sign_only", "srht_full"]:
        basis = make_variant(variant, p, int(cfg.get("seed", 0)))
        for rho in rho_values:
            for seed_idx in range(args.seeds):
                for obj_idx, obj in enumerate(objects):
                    for correction in ["none", "agc", "pairwise", "oracle"]:
                        metrics = simulate_and_reconstruct(
                            basis=basis,
                            obj=obj,
                            correction=correction,
                            channel_model="ou",
                            rho=float(rho),
                            sigma_a=sigma_a,
                            channel_seed=12000 + seed_idx,
                            read_noise=float(mech.get("read_noise", 0.0)),
                            noise_seed=12100 + obj_idx,
                            agc_window=max(9, int(0.05 * basis.num_frames)),
                        )
                        rows.append(
                            {
                                "variant": variant,
                                "correction": correction,
                                "rho": float(rho),
                                "sigma_a": sigma_a,
                                "seed": seed_idx,
                                "object": obj_idx,
                                **metrics,
                            }
                        )
    df = pd.DataFrame(rows)
    out = out_dir / "srht_ablation.csv"
    df.to_csv(out, index=False)
    (
        df.groupby(["variant", "correction", "rho"], as_index=False)
        .agg(
            psnr_mean=("psnr", "mean"),
            psnr_std=("psnr", "std"),
            rel_mse_mean=("rel_mse", "mean"),
            rel_mse_std=("rel_mse", "std"),
        )
        .to_csv(out_dir / "srht_ablation_summary.csv", index=False)
    )
    if not args.no_findings:
        with (root / "FINDINGS.md").open("a", encoding="utf-8") as f:
            f.write("\n## M3 Compact SRHT Ablation\n\n")
            f.write(f"Wrote `{out.as_posix()}` for ordered/permuted/sign/SRHT smoke ablations.\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
