from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

import pandas as pd

from run_mechanism_m1 import make_synthetic_objects, object_metrics
from src.basis import MeasurementBasis, basis_frame_budget, make_basis
from src.config_utils import load_config, project_root
from src.mechanisms import (
    apply_correction,
    make_multiplicative_channel,
    quantize_slm_patterns,
    reference_anchor_count,
    simulate_nonideal_measurements,
)


def parse_floats(text: str) -> list[float]:
    return [float(part) for part in text.replace(",", " ").split() if part.strip()]


def parse_items(text: str) -> list[str]:
    return [part for part in text.replace(",", " ").split() if part.strip()]


def make_basis_for_scan(name: str, num_pixels: int, frame_budget: int, seed: int) -> MeasurementBasis:
    kwargs = {"num_pixels": num_pixels, "seed": seed}
    if name.startswith("random_"):
        kwargs["num_frames"] = frame_budget
        kwargs["reconstruction"] = "correlation"
    else:
        kwargs["num_frames"] = frame_budget
    return make_basis(name, **kwargs)


def apply_slm_nonidealities(
    basis: MeasurementBasis,
    slm_levels: int,
    contrast_ratio: float,
) -> MeasurementBasis:
    if slm_levels <= 0 and contrast_ratio <= 1.0:
        return basis
    levels = slm_levels if slm_levels > 0 else 65536
    patterns = quantize_slm_patterns(basis.patterns, levels=levels, contrast_ratio=contrast_ratio)
    return replace(basis, patterns=patterns, reconstruction_matrix=None)


def reconstruct_with_correction(
    basis: MeasurementBasis,
    obj,
    observed,
    gains,
    correction: str,
    agc_window: int,
    reference_photons: float,
    reference_read_noise: float,
    seed: int,
) -> dict[str, float]:
    corrected = apply_correction(
        observed,
        correction=correction,
        true_gains=gains,
        paired=basis.paired,
        agc_window=agc_window,
        reference_photons=reference_photons,
        reference_read_noise=reference_read_noise,
        reference_seed=seed,
    )
    recon = basis.reconstruct(corrected.values, values_are_coefficients=corrected.values_are_coefficients)
    return object_metrics(recon, obj)


def summarize(df: pd.DataFrame, out_dir: Path) -> None:
    summary = (
        df.groupby(["condition", "rho", "sigma_a", "basis", "correction"], as_index=False)
        .agg(
            psnr_mean=("psnr", "mean"),
            psnr_std=("psnr", "std"),
            rel_mse_mean=("rel_mse", "mean"),
            rel_mse_std=("rel_mse", "std"),
            num_frames=("num_frames", "first"),
            reference_frames=("reference_frames", "first"),
            total_physical_frames=("total_physical_frames", "first"),
        )
        .sort_values(["condition", "rho", "sigma_a", "psnr_mean"], ascending=[True, True, True, False])
    )
    blind = summary[summary["correction"] != "oracle"].copy()
    equal = blind[blind["total_physical_frames"] == blind["num_frames"]].copy()
    reference = blind[blind["correction"].str.startswith("reference_")].copy()
    best_equal = equal.groupby(["condition", "rho", "sigma_a"], as_index=False).head(1)
    best_reference = reference.groupby(["condition", "rho", "sigma_a"], as_index=False).head(1)
    summary.to_csv(out_dir / "nonideal_summary.csv", index=False)
    blind.to_csv(out_dir / "nonideal_blind_summary.csv", index=False)
    equal.to_csv(out_dir / "nonideal_equal_frame_blind_summary.csv", index=False)
    reference.to_csv(out_dir / "nonideal_reference_summary.csv", index=False)
    best_equal.to_csv(out_dir / "nonideal_best_equal_frame_blind_methods.csv", index=False)
    best_reference.to_csv(out_dir / "nonideal_best_reference_methods.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compact ideal/nonideal M2 digital-twin scan.")
    parser.add_argument("--profile", default="debug")
    parser.add_argument("--objects", type=int, default=3)
    parser.add_argument("--seeds", type=int, default=2)
    parser.add_argument("--rho", default="0.003 0.03 0.3")
    parser.add_argument("--sigma-a", default="0.1 0.3")
    parser.add_argument("--bases", default="random_uniform hadamard_paired srht_paired")
    parser.add_argument("--corrections", default="none oracle agc scgi_proxy reference_k8")
    parser.add_argument("--photon-count", type=float, default=10000.0)
    parser.add_argument("--read-noise", type=float, default=0.002)
    parser.add_argument("--reference-photons", type=float, default=10000.0)
    parser.add_argument("--reference-read-noise", type=float, default=0.002)
    parser.add_argument("--slm-levels", type=int, default=256)
    parser.add_argument("--contrast-ratio", type=float, default=1000.0)
    parser.add_argument("--timing-jitter-std", type=float, default=0.05)
    parser.add_argument("--output-dir", type=Path, default=Path("results/nonideal_m2_compact"))
    args = parser.parse_args()

    root = project_root()
    cfg = load_config(root / "config.yaml", args.profile)
    mech = cfg.get("mechanism", {})
    image_size = int(mech.get("image_size", 32))
    num_pixels = image_size * image_size
    frame_budget, _ = basis_frame_budget(num_pixels)
    objects = make_synthetic_objects(args.objects, image_size, int(cfg.get("seed", 0)))
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    conditions = [
        {
            "condition": "ideal",
            "slm_levels": 0,
            "contrast_ratio": 0.0,
            "photon_count": 0.0,
            "read_noise": 0.0,
            "reference_photons": 0.0,
            "reference_read_noise": 0.0,
            "timing_jitter_std": 0.0,
        },
        {
            "condition": "nonideal",
            "slm_levels": int(args.slm_levels),
            "contrast_ratio": float(args.contrast_ratio),
            "photon_count": float(args.photon_count),
            "read_noise": float(args.read_noise),
            "reference_photons": float(args.reference_photons),
            "reference_read_noise": float(args.reference_read_noise),
            "timing_jitter_std": float(args.timing_jitter_std),
        },
    ]

    rows = []
    for basis_index, basis_name in enumerate(parse_items(args.bases)):
        nominal_basis = make_basis_for_scan(basis_name, num_pixels, frame_budget, int(cfg.get("seed", 0)) + basis_index * 101)
        corrections = parse_items(args.corrections)
        if nominal_basis.paired and "pairwise" not in corrections:
            corrections.append("pairwise")
        for condition in conditions:
            basis = apply_slm_nonidealities(
                nominal_basis,
                slm_levels=int(condition["slm_levels"]),
                contrast_ratio=float(condition["contrast_ratio"]),
            )
            agc_window = max(9, int(0.05 * basis.num_frames))
            for rho in parse_floats(args.rho):
                for sigma_a in parse_floats(args.sigma_a):
                    for seed_idx in range(args.seeds):
                        for obj_idx, obj in enumerate(objects):
                            ideal = basis.measure(obj)
                            channel = make_multiplicative_channel(
                                basis.num_frames,
                                model="ou",
                                rho=float(rho),
                                sigma_a=float(sigma_a),
                                seed=20000 + 97 * seed_idx,
                                device=str(ideal.device),
                                dtype=ideal.dtype,
                            )
                            observed, effective_gains = simulate_nonideal_measurements(
                                ideal,
                                channel,
                                photon_count=float(condition["photon_count"]),
                                read_noise=float(condition["read_noise"]),
                                timing_jitter_std=float(condition["timing_jitter_std"]),
                                seed=21000 + 53 * obj_idx + seed_idx,
                            )
                            for correction in corrections:
                                if correction == "pairwise" and not basis.paired:
                                    continue
                                reference_period = int(correction.rsplit("k", 1)[1]) if correction.startswith("reference_k") else 0
                                reference_frames = reference_anchor_count(basis.num_frames, reference_period) if reference_period else 0
                                metrics = reconstruct_with_correction(
                                    basis=basis,
                                    obj=obj,
                                    observed=observed,
                                    gains=effective_gains,
                                    correction=correction,
                                    agc_window=agc_window,
                                    reference_photons=float(condition["reference_photons"]),
                                    reference_read_noise=float(condition["reference_read_noise"]),
                                    seed=22000 + seed_idx,
                                )
                                rows.append(
                                    {
                                        **condition,
                                        "basis": basis.name,
                                        "correction": correction,
                                        "reference_period": reference_period,
                                        "rho": float(rho),
                                        "sigma_a": float(sigma_a),
                                        "seed": seed_idx,
                                        "object": obj_idx,
                                        "num_frames": basis.num_frames,
                                        "reference_frames": reference_frames,
                                        "total_physical_frames": basis.num_frames + reference_frames,
                                        "num_coefficients": basis.num_coefficients,
                                        "num_pixels": basis.num_pixels,
                                        **metrics,
                                    }
                                )

    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "nonideal_phase_scan.csv", index=False)
    summarize(df, out_dir)
    print(f"wrote {out_dir / 'nonideal_phase_scan.csv'}")
    print(f"rows={len(df)}")


if __name__ == "__main__":
    main()
