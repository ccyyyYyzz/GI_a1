from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import torch

from run_m4_agc_targeted import markdown_table
from run_mechanism_m1 import make_synthetic_objects, simulate_and_reconstruct
from run_srht_m3 import make_variant, parse_floats
from src.basis import MeasurementBasis, basis_frame_budget, make_basis
from src.config_utils import load_config, project_root
from src.plotting import save_metrics_table


def make_comparator_basis(name: str, num_pixels: int, seed: int, reconstruction: str) -> MeasurementBasis:
    if name in {"hadamard_ordered", "sign_only", "srht_full", "perm_only"}:
        return make_variant(name, num_pixels, seed)
    random_frames, _coeffs = basis_frame_budget(num_pixels)
    if name in {"random_uniform", "random_binary", "random_gaussian"}:
        offset = {"random_uniform": 0, "random_binary": 17, "random_gaussian": 31}[name]
        return make_basis(
            name,
            num_pixels=num_pixels,
            num_frames=random_frames,
            seed=seed + offset,
            reconstruction=reconstruction,
        )
    raise ValueError(name)


def correction_set(basis: MeasurementBasis) -> list[str]:
    if basis.paired:
        return ["none", "agc", "pairwise", "oracle"]
    return ["none", "agc", "oracle"]


def summarize(raw: pd.DataFrame) -> pd.DataFrame:
    return (
        raw.groupby(["variant", "correction", "rho", "sigma_a"], as_index=False)
        .agg(
            psnr_mean=("psnr", "mean"),
            psnr_std=("psnr", "std"),
            rel_mse_mean=("rel_mse", "mean"),
            rel_mse_std=("rel_mse", "std"),
            gain_rel_mse_mean=("gain_rel_mse", "mean"),
        )
        .sort_values(["rho", "sigma_a", "variant", "correction"])
    )


def build_fast_delta(summary: pd.DataFrame) -> pd.DataFrame:
    blind = summary[summary["correction"] != "oracle"].copy()
    best = (
        blind.sort_values(["rho", "sigma_a", "variant", "psnr_mean"], ascending=[True, True, True, False])
        .groupby(["rho", "sigma_a", "variant"], as_index=False)
        .head(1)
        .copy()
    )
    rows = []
    for (rho, sigma_a), group in best.groupby(["rho", "sigma_a"], sort=True):
        records = {str(row.variant): row for row in group.itertuples(index=False)}
        srht = records.get("srht_full")
        ordered = records.get("hadamard_ordered")
        sign_only = records.get("sign_only")
        random_candidates = [
            records[name]
            for name in ["random_uniform", "random_binary", "random_gaussian"]
            if name in records
        ]
        if srht is None or ordered is None or not random_candidates:
            continue
        best_random = max(random_candidates, key=lambda row: float(row.psnr_mean))
        best_ablation = max(
            [row for row in [srht, ordered, sign_only] if row is not None],
            key=lambda row: float(row.psnr_mean),
        )
        rows.append(
            {
                "rho": float(rho),
                "sigma_a": float(sigma_a),
                "srht_best_correction": str(srht.correction),
                "srht_best_psnr": float(srht.psnr_mean),
                "ordered_best_correction": str(ordered.correction),
                "ordered_best_psnr": float(ordered.psnr_mean),
                "best_random_variant": str(best_random.variant),
                "best_random_correction": str(best_random.correction),
                "best_random_psnr": float(best_random.psnr_mean),
                "srht_minus_ordered_db": float(srht.psnr_mean) - float(ordered.psnr_mean),
                "srht_minus_best_random_db": float(srht.psnr_mean) - float(best_random.psnr_mean),
                "srht_gap_to_best_srht_ablation_db": float(srht.psnr_mean) - float(best_ablation.psnr_mean),
                "best_srht_ablation": str(best_ablation.variant),
            }
        )
    return pd.DataFrame(rows)


def write_report(out_dir: Path, raw: pd.DataFrame, summary: pd.DataFrame, deltas: pd.DataFrame) -> None:
    payload = {
        "raw_rows": int(len(raw)),
        "summary_rows": int(len(summary)),
        "delta_rows": int(len(deltas)),
        "rho_values": sorted(float(v) for v in raw["rho"].unique()),
        "sigma_a_values": sorted(float(v) for v in raw["sigma_a"].unique()),
        "variants": sorted(str(v) for v in raw["variant"].unique()),
        "srht_minus_ordered_min_db": float(deltas["srht_minus_ordered_db"].min()) if len(deltas) else None,
        "srht_minus_ordered_max_db": float(deltas["srht_minus_ordered_db"].max()) if len(deltas) else None,
        "srht_minus_best_random_min_db": float(deltas["srht_minus_best_random_db"].min()) if len(deltas) else None,
        "srht_minus_best_random_max_db": float(deltas["srht_minus_best_random_db"].max()) if len(deltas) else None,
    }
    (out_dir / "m3_random_comparator_summary.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )

    display = deltas.copy()
    for column in [
        "srht_best_psnr",
        "ordered_best_psnr",
        "best_random_psnr",
        "srht_minus_ordered_db",
        "srht_minus_best_random_db",
        "srht_gap_to_best_srht_ablation_db",
    ]:
        if column in display:
            display[column] = display[column].map(lambda value: f"{float(value):.3f}")

    lines = [
        "# M3 Random Comparator Audit",
        "",
        f"Raw rows: `{payload['raw_rows']}`; summary rows: `{payload['summary_rows']}`.",
        f"Rho values: `{payload['rho_values']}`; sigma_a values: `{payload['sigma_a_values']}`.",
        "",
        "## Best Blind Deltas",
        "",
        markdown_table(display),
        "",
        "## Interpretation",
        "",
        "This audit closes the direct-random-comparator gap in the M3 ablation.",
        "It compares the best non-oracle correction for full SRHT against ordered",
        "Hadamard and the best random basis under the same object/seed/rho/sigma",
        "cells. The strong prompt gate still requires a robust >=3 dB fast-drift",
        "advantage over ordered Hadamard and no more than a 1 dB loss versus",
        "random bases; these fields are reported directly in the delta table.",
        "",
    ]
    (out_dir / "m3_random_comparator_report.md").write_text("\n".join(lines), encoding="utf-8")
    if len(deltas):
        save_metrics_table(
            out_dir / "m3_random_comparator_delta_table.png",
            deltas[
                [
                    "rho",
                    "sigma_a",
                    "srht_minus_ordered_db",
                    "srht_minus_best_random_db",
                    "best_random_variant",
                    "best_srht_ablation",
                ]
            ],
            title="M3 SRHT vs random comparator",
            max_rows=20,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="M3 fast-drift SRHT-vs-random comparator.")
    parser.add_argument("--profile", default="smoke")
    parser.add_argument("--objects", type=int, default=10)
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--rho-values", default="1.0,10.0")
    parser.add_argument("--sigma-a-values", default="0.30,0.50")
    parser.add_argument("--variants", default="hadamard_ordered sign_only srht_full random_uniform random_binary")
    parser.add_argument("--reconstruction", choices=["least_squares", "correlation"], default="correlation")
    parser.add_argument("--output-dir", type=Path, default=Path("results/m3_random_comparator_fast_r1"))
    args = parser.parse_args()

    root = project_root()
    cfg = load_config(root / "config.yaml", args.profile)
    mech = cfg.get("mechanism", {})
    h = int(mech.get("image_size", 32))
    p = h * h
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    objects = make_synthetic_objects(int(args.objects), h, int(cfg.get("seed", 0)))
    variants = [part for part in args.variants.replace(",", " ").split() if part.strip()]
    rho_values = parse_floats(args.rho_values, [1.0, 10.0])
    sigma_values = parse_floats(args.sigma_a_values, [0.30, 0.50])

    rows: list[dict[str, object]] = []
    for variant in variants:
        basis = make_comparator_basis(variant, p, int(cfg.get("seed", 0)), args.reconstruction)
        for rho in rho_values:
            for sigma_a in sigma_values:
                for seed_idx in range(int(args.seeds)):
                    for obj_idx, obj in enumerate(objects):
                        for correction in correction_set(basis):
                            metrics = simulate_and_reconstruct(
                                basis=basis,
                                obj=obj,
                                correction=correction,
                                channel_model="ou",
                                rho=float(rho),
                                sigma_a=float(sigma_a),
                                channel_seed=22000 + seed_idx,
                                read_noise=float(mech.get("read_noise", 0.0)),
                                noise_seed=22100 + obj_idx,
                                agc_window=max(9, int(0.05 * basis.num_frames)),
                            )
                            rows.append(
                                {
                                    "variant": variant,
                                    "basis_name": basis.name,
                                    "paired": bool(basis.paired),
                                    "correction": correction,
                                    "rho": float(rho),
                                    "sigma_a": float(sigma_a),
                                    "seed": seed_idx,
                                    "object": obj_idx,
                                    "num_frames": basis.num_frames,
                                    **metrics,
                                }
                            )
    raw = pd.DataFrame(rows)
    summary = summarize(raw)
    deltas = build_fast_delta(summary)
    raw.to_csv(out_dir / "m3_random_comparator_raw.csv", index=False)
    summary.to_csv(out_dir / "m3_random_comparator_summary.csv", index=False)
    deltas.to_csv(out_dir / "m3_random_comparator_deltas.csv", index=False)
    write_report(out_dir, raw, summary, deltas)
    print(f"wrote {out_dir}")


if __name__ == "__main__":
    main()
