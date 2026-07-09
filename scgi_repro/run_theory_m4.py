from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import torch

from run_mechanism_m1 import make_synthetic_objects, object_metrics
from src.basis import MeasurementBasis, basis_frame_budget, make_basis
from src.config_utils import project_root


DEFAULT_BASES = [
    "random_uniform",
    "random_binary",
    "hadamard_paired",
    "dct_paired",
    "fourier_fourstep",
    "srht_paired",
]


def parse_floats(text: str) -> list[float]:
    return [float(part) for part in text.replace(",", " ").split() if part.strip()]


def parse_ints(text: str) -> list[int]:
    return [int(part) for part in text.replace(",", " ").split() if part.strip()]


def make_m4_basis(name: str, num_pixels: int, frame_budget: int, seed: int) -> MeasurementBasis:
    kwargs = {"num_pixels": num_pixels, "seed": seed}
    if name.startswith("random_"):
        kwargs["num_frames"] = frame_budget
        kwargs["reconstruction"] = "correlation"
    elif name == "fourier_fourstep":
        kwargs["num_frames"] = frame_budget
    else:
        kwargs["num_frames"] = frame_budget
    return make_basis(name, **kwargs)


def delta_reconstruction_metrics(reconstruction: torch.Tensor, reference: torch.Tensor) -> dict[str, float]:
    recon = reconstruction.reshape(-1).detach().cpu().to(dtype=torch.float64)
    ref = reference.reshape(-1).detach().cpu().to(dtype=torch.float64)
    delta = recon - ref
    mse = delta.pow(2).mean()
    rel = mse / ref.pow(2).mean().clamp_min(1.0e-12)
    return {
        "delta_recon_mse": float(mse.item()),
        "delta_recon_rel_mse": float(rel.item()),
    }


def coefficient_sequence(basis: MeasurementBasis, ideal: torch.Tensor) -> torch.Tensor:
    if basis.paired:
        coeffs = basis.coefficients_from_frames(ideal)
    elif basis.four_step:
        coeffs = basis._fourier_coefficients_from_frames(ideal)  # noqa: SLF001 - analysis script
    else:
        coeffs = ideal.reshape(-1) - ideal.reshape(-1).mean()
    return coeffs.reshape(-1).detach().cpu()


def energy_metrics(coefficients: torch.Tensor) -> dict[str, float]:
    values = coefficients
    if torch.is_complex(values):
        energy = values.abs().pow(2).to(dtype=torch.float64)
    else:
        energy = values.to(dtype=torch.float64).pow(2)
    total = energy.sum().clamp_min(1.0e-12)
    sorted_energy = torch.sort(energy, descending=True).values
    probs = (energy / total).clamp_min(1.0e-18)
    entropy = -float((probs * torch.log(probs)).sum().item())
    effective_rank = math.exp(entropy)
    count = int(energy.numel())

    def top_fraction(frac: float) -> float:
        k = max(1, int(math.ceil(frac * count)))
        return float((sorted_energy[:k].sum() / total).item())

    return {
        "coefficient_count": count,
        "top_1pct_energy": top_fraction(0.01),
        "top_5pct_energy": top_fraction(0.05),
        "top_10pct_energy": top_fraction(0.10),
        "effective_rank": effective_rank,
        "effective_rank_frac": effective_rank / max(count, 1),
    }


def fit_log_linear(frame: pd.DataFrame, y_col: str, x_cols: Iterable[str]) -> dict[str, float | int | str]:
    columns = [y_col, *x_cols]
    data = frame.loc[:, columns].replace([np.inf, -np.inf], np.nan).dropna()
    for col in columns:
        data = data[data[col] > 0]
    x_cols = list(x_cols)
    if len(data) < len(x_cols) + 2:
        return {"fit_status": "insufficient_points", "n": int(len(data))}
    y = np.log10(data[y_col].to_numpy(dtype=float))
    x_parts = [np.ones_like(y)]
    for col in x_cols:
        x_parts.append(np.log10(data[col].to_numpy(dtype=float)))
    x = np.column_stack(x_parts)
    coef, *_ = np.linalg.lstsq(x, y, rcond=None)
    pred = x @ coef
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    dof = max(0, len(y) - x.shape[1])
    if dof > 0:
        sigma2 = ss_res / float(dof)
        cov = sigma2 * np.linalg.pinv(x.T @ x)
        se = np.sqrt(np.clip(np.diag(cov), 0.0, None))
    else:
        se = np.full_like(coef, np.nan, dtype=float)
    result: dict[str, float | int | str] = {
        "fit_status": "ok",
        "n": int(len(data)),
        "intercept": float(coef[0]),
        "intercept_se": float(se[0]),
        "r2": float(1.0 - ss_res / ss_tot) if ss_tot > 0 else 1.0,
        "rmse_log10": float(math.sqrt(ss_res / max(len(y), 1))),
    }
    for col, value, stderr in zip(x_cols, coef[1:], se[1:]):
        result[f"{col}_exponent"] = float(value)
        result[f"{col}_exponent_se"] = float(stderr)
    return result


def run_error_scaling(
    sizes: list[int],
    basis_names: list[str],
    objects_per_size: int,
    seeds: int,
    residual_sigmas: list[float],
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    for image_size in sizes:
        num_pixels = image_size * image_size
        frame_budget, _ = basis_frame_budget(num_pixels)
        objects = make_synthetic_objects(objects_per_size, image_size, seed + image_size)
        for basis_index, basis_name in enumerate(basis_names):
            basis = make_m4_basis(basis_name, num_pixels, frame_budget, seed + 101 * basis_index)
            static_recons = [basis.reconstruct(basis.measure(obj)) for obj in objects]
            for sigma_delta in residual_sigmas:
                for seed_idx in range(seeds):
                    generator = torch.Generator(device="cpu")
                    generator.manual_seed(seed + 1009 * seed_idx + int(round(10000 * sigma_delta)) + 17 * image_size)
                    for object_idx, obj in enumerate(objects):
                        ideal = basis.measure(obj)
                        delta = torch.randn(ideal.shape, generator=generator, dtype=ideal.dtype) * float(sigma_delta)
                        perturbed = ideal * (1.0 + delta)
                        recon = basis.reconstruct(perturbed)
                        metrics = object_metrics(recon, obj)
                        metrics.update(delta_reconstruction_metrics(recon, static_recons[object_idx]))
                        rows.append(
                            {
                                "image_size": image_size,
                                "num_pixels": num_pixels,
                                "num_frames": basis.num_frames,
                                "basis": basis.name,
                                "sigma_delta": float(sigma_delta),
                                "seed": seed_idx,
                                "object": object_idx,
                                **metrics,
                            }
                        )
    raw = pd.DataFrame(rows)
    summary = (
        raw.groupby(["image_size", "num_pixels", "num_frames", "basis", "sigma_delta"], as_index=False)
        .agg(
            delta_recon_rel_mse_mean=("delta_recon_rel_mse", "mean"),
            delta_recon_rel_mse_std=("delta_recon_rel_mse", "std"),
            rel_mse_mean=("rel_mse", "mean"),
            rel_mse_std=("rel_mse", "std"),
            psnr_mean=("psnr", "mean"),
            psnr_std=("psnr", "std"),
        )
        .sort_values(["basis", "num_pixels", "sigma_delta"])
    )
    fit_rows = []
    for basis_name, group in summary.groupby("basis"):
        fit = fit_log_linear(group, "delta_recon_rel_mse_mean", ["sigma_delta", "num_frames"])
        fit_rows.append({"basis": basis_name, "law": "delta_rel_mse ~ sigma_delta^a * num_frames^b", **fit})
    fits = pd.DataFrame(fit_rows)
    return raw, summary, fits


def run_energy_concentration(
    sizes: list[int],
    basis_names: list[str],
    objects_per_size: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    for image_size in sizes:
        num_pixels = image_size * image_size
        frame_budget, _ = basis_frame_budget(num_pixels)
        objects = make_synthetic_objects(objects_per_size, image_size, seed + 2 * image_size)
        for basis_index, basis_name in enumerate(basis_names):
            basis = make_m4_basis(basis_name, num_pixels, frame_budget, seed + 211 * basis_index)
            for object_idx, obj in enumerate(objects):
                ideal = basis.measure(obj)
                coeffs = coefficient_sequence(basis, ideal)
                rows.append(
                    {
                        "image_size": image_size,
                        "num_pixels": num_pixels,
                        "num_frames": basis.num_frames,
                        "basis": basis.name,
                        "object": object_idx,
                        **energy_metrics(coeffs),
                    }
                )
    raw = pd.DataFrame(rows)
    summary = (
        raw.groupby(["image_size", "num_pixels", "num_frames", "basis"], as_index=False)
        .agg(
            top_1pct_energy_mean=("top_1pct_energy", "mean"),
            top_5pct_energy_mean=("top_5pct_energy", "mean"),
            top_10pct_energy_mean=("top_10pct_energy", "mean"),
            effective_rank_frac_mean=("effective_rank_frac", "mean"),
        )
        .sort_values(["basis", "num_pixels"])
    )
    return raw, summary


def run_random_frame_scaling(
    image_size: int,
    frame_factors: list[float],
    objects_per_size: int,
    seeds: int,
    residual_sigmas: list[float],
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    num_pixels = image_size * image_size
    objects = make_synthetic_objects(objects_per_size, image_size, seed + 37 * image_size)
    for basis_index, basis_name in enumerate(["random_uniform", "random_binary"]):
        for frame_factor in frame_factors:
            num_frames = max(1, int(round(float(frame_factor) * num_pixels)))
            basis = make_basis(
                basis_name,
                num_pixels=num_pixels,
                num_frames=num_frames,
                seed=seed + 409 * basis_index + int(round(100 * frame_factor)),
                reconstruction="correlation",
            )
            static_recons = [basis.reconstruct(basis.measure(obj)) for obj in objects]
            for sigma_delta in residual_sigmas:
                for seed_idx in range(seeds):
                    generator = torch.Generator(device="cpu")
                    generator.manual_seed(seed + 3001 * seed_idx + int(round(10000 * sigma_delta)) + int(num_frames))
                    for object_idx, obj in enumerate(objects):
                        ideal = basis.measure(obj)
                        delta = torch.randn(ideal.shape, generator=generator, dtype=ideal.dtype) * float(sigma_delta)
                        recon = basis.reconstruct(ideal * (1.0 + delta))
                        metrics = delta_reconstruction_metrics(recon, static_recons[object_idx])
                        rows.append(
                            {
                                "image_size": image_size,
                                "num_pixels": num_pixels,
                                "frame_factor": float(frame_factor),
                                "num_frames": num_frames,
                                "basis": basis.name,
                                "sigma_delta": float(sigma_delta),
                                "seed": seed_idx,
                                "object": object_idx,
                                **metrics,
                            }
                        )
    raw = pd.DataFrame(rows)
    summary = (
        raw.groupby(["image_size", "num_pixels", "frame_factor", "num_frames", "basis", "sigma_delta"], as_index=False)
        .agg(
            delta_recon_rel_mse_mean=("delta_recon_rel_mse", "mean"),
            delta_recon_rel_mse_std=("delta_recon_rel_mse", "std"),
        )
        .sort_values(["basis", "num_frames", "sigma_delta"])
    )
    fit_rows = []
    for basis_name, group in summary.groupby("basis"):
        fit = fit_log_linear(group, "delta_recon_rel_mse_mean", ["sigma_delta", "num_frames"])
        fit_rows.append({"basis": basis_name, "law": "fixed-P delta_rel_mse ~ sigma_delta^a * num_frames^b", **fit})
    fits = pd.DataFrame(fit_rows)
    return raw, summary, fits


def fit_flip_boundaries(phase_dir: Path) -> pd.DataFrame:
    path = phase_dir / "flip_boundary.csv"
    if not path.exists():
        return pd.DataFrame(
            [
                {
                    "fit_status": "missing_flip_boundary",
                    "source": path.as_posix(),
                }
            ]
        )
    data = pd.read_csv(path)
    rows = []
    group_cols = ["correction", "challenger", "baseline"]
    for keys, group in data.groupby(group_cols):
        observed = group[
            (group["boundary_status"] == "observed")
            & group["rho_star_first_ge"].notna()
            & (group["rho_star_first_ge"] > 0)
            & (group["sigma_a"] > 0)
        ].copy()
        fit = fit_log_linear(observed.rename(columns={"rho_star_first_ge": "rho_star"}), "rho_star", ["sigma_a"])
        rows.append(
            {
                "correction": keys[0],
                "challenger": keys[1],
                "baseline": keys[2],
                "observed_points": int((group["boundary_status"] == "observed").sum()),
                "left_censored_points": int((group["boundary_status"] == "left_censored").sum()),
                "not_reached_points": int((group["boundary_status"] == "not_reached").sum()),
                "law": "rho_star ~ sigma_a^a",
                **fit,
            }
        )
    return pd.DataFrame(rows).sort_values(["correction", "challenger"])


def main() -> None:
    parser = argparse.ArgumentParser(description="M4 theory hooks: N-sweep scaling, energy concentration, flip-boundary fits.")
    parser.add_argument("--sizes", default="8 16 32", help="Image sizes to sweep; num_pixels is size^2.")
    parser.add_argument("--objects", type=int, default=5)
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--sigmas", default="0.01 0.02 0.05 0.1")
    parser.add_argument("--bases", default=" ".join(DEFAULT_BASES))
    parser.add_argument("--frame-sweep-size", type=int, default=32)
    parser.add_argument("--frame-factors", default="1 2 4 8")
    parser.add_argument("--phase-dir", type=Path, default=Path("results/phase_m2_scgi_proxy_dense_r1_merged"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/theory_m4"))
    parser.add_argument("--seed", type=int, default=20240708)
    args = parser.parse_args()

    root = project_root()
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    sizes = parse_ints(args.sizes)
    for size in sizes:
        pixels = size * size
        if pixels <= 0 or pixels & (pixels - 1):
            raise ValueError(f"image_size^2 must be a power of two for Hadamard/SRHT, got image_size={size}.")
    residual_sigmas = parse_floats(args.sigmas)
    basis_names = [part for part in args.bases.replace(",", " ").split() if part.strip()]

    raw, summary, fits = run_error_scaling(sizes, basis_names, args.objects, args.seeds, residual_sigmas, args.seed)
    energy, energy_summary = run_energy_concentration(sizes, basis_names, args.objects, args.seed)
    frame_raw, frame_summary, frame_fits = run_random_frame_scaling(
        args.frame_sweep_size,
        parse_floats(args.frame_factors),
        args.objects,
        args.seeds,
        residual_sigmas,
        args.seed,
    )
    phase_dir = args.phase_dir if args.phase_dir.is_absolute() else root / args.phase_dir
    flip_fits = fit_flip_boundaries(phase_dir)

    raw.to_csv(out_dir / "m4_error_scaling.csv", index=False)
    summary.to_csv(out_dir / "m4_error_scaling_summary.csv", index=False)
    fits.to_csv(out_dir / "m4_error_scaling_fit.csv", index=False)
    energy.to_csv(out_dir / "m4_energy_concentration.csv", index=False)
    energy_summary.to_csv(out_dir / "m4_energy_concentration_summary.csv", index=False)
    frame_raw.to_csv(out_dir / "m4_random_frame_scaling.csv", index=False)
    frame_summary.to_csv(out_dir / "m4_random_frame_scaling_summary.csv", index=False)
    frame_fits.to_csv(out_dir / "m4_random_frame_scaling_fit.csv", index=False)
    flip_fits.to_csv(out_dir / "m4_flip_boundary_fit.csv", index=False)

    manifest = {
        "sizes": sizes,
        "objects": args.objects,
        "seeds": args.seeds,
        "residual_sigmas": residual_sigmas,
        "bases": basis_names,
        "phase_dir": phase_dir.as_posix(),
        "outputs": [
            "m4_error_scaling.csv",
            "m4_error_scaling_summary.csv",
            "m4_error_scaling_fit.csv",
            "m4_energy_concentration.csv",
            "m4_energy_concentration_summary.csv",
            "m4_random_frame_scaling.csv",
            "m4_random_frame_scaling_summary.csv",
            "m4_random_frame_scaling_fit.csv",
            "m4_flip_boundary_fit.csv",
        ],
    }
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"wrote {out_dir / 'm4_error_scaling_fit.csv'}")
    print(f"wrote {out_dir / 'm4_random_frame_scaling_fit.csv'}")
    print(f"wrote {out_dir / 'm4_energy_concentration_summary.csv'}")
    print(f"wrote {out_dir / 'm4_flip_boundary_fit.csv'}")


if __name__ == "__main__":
    main()
