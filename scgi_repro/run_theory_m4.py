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
from src.mechanisms import (
    estimate_agc_gain,
    gain_error_stats,
    make_multiplicative_channel,
    simulate_channel_measurements,
)


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


def fit_log_linear_bootstrap(
    frame: pd.DataFrame,
    y_col: str,
    x_cols: Iterable[str],
    iterations: int,
    seed: int,
) -> dict[str, float | int | str]:
    """Fit a log-linear law and add percentile bootstrap intervals."""

    x_cols = list(x_cols)
    fit = fit_log_linear(frame, y_col, x_cols)
    iterations = int(iterations)
    if fit.get("fit_status") != "ok" or iterations <= 0:
        fit["bootstrap_iterations"] = 0
        return fit

    columns = [y_col, *x_cols]
    data = frame.loc[:, columns].replace([np.inf, -np.inf], np.nan).dropna()
    for col in columns:
        data = data[data[col] > 0]
    if len(data) < len(x_cols) + 2:
        fit["bootstrap_iterations"] = 0
        return fit

    rng = np.random.default_rng(int(seed))
    draws: dict[str, list[float]] = {"intercept": []}
    for col in x_cols:
        draws[f"{col}_exponent"] = []

    for _ in range(iterations):
        sample_index = rng.integers(0, len(data), size=len(data))
        sample = data.iloc[sample_index].reset_index(drop=True)
        boot = fit_log_linear(sample, y_col, x_cols)
        if boot.get("fit_status") != "ok":
            continue
        for key in draws:
            value = boot.get(key)
            if isinstance(value, (int, float)) and math.isfinite(float(value)):
                draws[key].append(float(value))

    fit["bootstrap_iterations"] = int(min(len(values) for values in draws.values()) if draws else 0)
    for key, values in draws.items():
        if values:
            fit[f"{key}_ci_low"] = float(np.percentile(values, 2.5))
            fit[f"{key}_ci_high"] = float(np.percentile(values, 97.5))
    return fit


def run_error_scaling(
    sizes: list[int],
    basis_names: list[str],
    objects_per_size: int,
    seeds: int,
    residual_sigmas: list[float],
    seed: int,
    bootstrap_iterations: int = 0,
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
    for basis_index, (basis_name, group) in enumerate(summary.groupby("basis")):
        fit = fit_log_linear_bootstrap(
            group,
            "delta_recon_rel_mse_mean",
            ["sigma_delta", "num_frames"],
            bootstrap_iterations,
            seed + 7001 * basis_index,
        )
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
    bootstrap_iterations: int = 0,
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
    for basis_index, (basis_name, group) in enumerate(summary.groupby("basis")):
        fit = fit_log_linear_bootstrap(
            group,
            "delta_recon_rel_mse_mean",
            ["sigma_delta", "num_frames"],
            bootstrap_iterations,
            seed + 9001 * basis_index,
        )
        fit_rows.append({"basis": basis_name, "law": "fixed-P delta_rel_mse ~ sigma_delta^a * num_frames^b", **fit})
    fits = pd.DataFrame(fit_rows)
    return raw, summary, fits


def read_rho_grid(phase_dir: Path) -> list[float]:
    for name in ("phase_summary.csv", "phase_scan.csv"):
        path = phase_dir / name
        if path.exists():
            data = pd.read_csv(path, usecols=["rho"])
            values = sorted(float(x) for x in data["rho"].dropna().unique())
            if values:
                return values
    return []


def fit_flip_boundaries(phase_dir: Path, bootstrap_iterations: int = 0, seed: int = 0) -> pd.DataFrame:
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
        fit = fit_log_linear_bootstrap(
            observed.rename(columns={"rho_star_first_ge": "rho_star"}),
            "rho_star",
            ["sigma_a"],
            bootstrap_iterations,
            seed + 11003 * len(rows),
        )
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


def build_censored_flip_intervals(phase_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    path = phase_dir / "flip_boundary.csv"
    if not path.exists():
        missing = pd.DataFrame([{"fit_status": "missing_flip_boundary", "source": path.as_posix()}])
        return missing, missing, missing

    data = pd.read_csv(path)
    rho_grid = read_rho_grid(phase_dir)
    min_rho = min(rho_grid) if rho_grid else float("nan")
    max_rho = max(rho_grid) if rho_grid else float("nan")
    rows: list[dict[str, object]] = []

    for row in data.to_dict(orient="records"):
        status = str(row.get("boundary_status", "unknown"))
        rho_star = row.get("rho_star_first_ge")
        lower = float("nan")
        upper = float("nan")
        midpoint = float("nan")
        interval_kind = status
        if status == "observed" and pd.notna(rho_star) and float(rho_star) > 0:
            upper = float(rho_star)
            lower_candidates = [rho for rho in rho_grid if rho < upper]
            lower = max(lower_candidates) if lower_candidates else min_rho
            midpoint = math.sqrt(lower * upper) if lower > 0 else upper
            interval_kind = "closed_interval"
        elif status == "left_censored" and pd.notna(rho_star) and float(rho_star) > 0:
            upper = float(rho_star)
            midpoint = upper
            interval_kind = "upper_bound"
        elif status == "not_reached":
            lower = max_rho
            midpoint = lower
            interval_kind = "lower_bound"

        rows.append(
            {
                **row,
                "rho_lower_bound": lower,
                "rho_upper_bound": upper,
                "rho_interval_midpoint": midpoint,
                "interval_kind": interval_kind,
                "rho_grid_min": min_rho,
                "rho_grid_max": max_rho,
            }
        )

    intervals = pd.DataFrame(rows)
    summary = (
        intervals.groupby(["correction", "challenger", "baseline"], as_index=False)
        .agg(
            observed_points=("boundary_status", lambda s: int((s == "observed").sum())),
            left_censored_points=("boundary_status", lambda s: int((s == "left_censored").sum())),
            not_reached_points=("boundary_status", lambda s: int((s == "not_reached").sum())),
            lower_bound_points=("interval_kind", lambda s: int((s == "lower_bound").sum())),
            upper_bound_points=("interval_kind", lambda s: int((s == "upper_bound").sum())),
            closed_interval_points=("interval_kind", lambda s: int((s == "closed_interval").sum())),
            min_observed_midpoint=("rho_interval_midpoint", "min"),
            max_observed_midpoint=("rho_interval_midpoint", "max"),
        )
        .sort_values(["correction", "challenger"])
    )

    fit_rows = []
    for keys, group in intervals.groupby(["correction", "challenger", "baseline"]):
        usable = group[group["rho_interval_midpoint"].notna() & (group["rho_interval_midpoint"] > 0)].copy()
        observed_count = int((group["boundary_status"] == "observed").sum())
        if observed_count < 2:
            fit = {"fit_status": "censored_only_endpoint", "n": int(len(usable))}
        else:
            fit = fit_log_linear(usable.rename(columns={"rho_interval_midpoint": "rho_star"}), "rho_star", ["sigma_a"])
        fit_rows.append(
            {
                "correction": keys[0],
                "challenger": keys[1],
                "baseline": keys[2],
                "law": "rho_star_endpoint_midpoint ~ sigma_a^a",
                "fit_kind": "censored_endpoint_midpoint",
                "observed_points": observed_count,
                "left_censored_points": int((group["boundary_status"] == "left_censored").sum()),
                "not_reached_points": int((group["boundary_status"] == "not_reached").sum()),
                **fit,
            }
        )
    fits = pd.DataFrame(fit_rows).sort_values(["correction", "challenger"])
    return intervals, summary, fits


def run_agc_window_law(
    image_size: int,
    basis_names: list[str],
    objects_per_size: int,
    seeds: int,
    rho_values: list[float],
    sigma_values: list[float],
    window_fracs: list[float],
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    num_pixels = image_size * image_size
    frame_budget, _ = basis_frame_budget(num_pixels)
    objects = make_synthetic_objects(objects_per_size, image_size, seed + 59 * image_size)
    for basis_index, basis_name in enumerate(basis_names):
        basis = make_m4_basis(basis_name, num_pixels, frame_budget, seed + 811 * basis_index)
        for rho in rho_values:
            for sigma_a in sigma_values:
                for seed_idx in range(seeds):
                    for object_idx, obj in enumerate(objects):
                        ideal = basis.measure(obj)
                        channel = make_multiplicative_channel(
                            basis.num_frames,
                            model="ou",
                            rho=float(rho),
                            sigma_a=float(sigma_a),
                            seed=seed + 13001 * seed_idx + 97 * object_idx,
                            device=str(ideal.device),
                            dtype=ideal.dtype,
                        )
                        observed = simulate_channel_measurements(ideal, channel, read_noise=0.0, seed=seed_idx)
                        for window_frac in window_fracs:
                            window_frames = max(3, int(round(float(window_frac) * basis.num_frames)))
                            estimated = estimate_agc_gain(observed, window=window_frames)
                            stats = gain_error_stats(estimated, channel.gains)
                            rows.append(
                                {
                                    "image_size": image_size,
                                    "num_pixels": num_pixels,
                                    "basis": basis.name,
                                    "rho": float(rho),
                                    "sigma_a": float(sigma_a),
                                    "window_frac": float(window_frac),
                                    "window_frames": int(window_frames),
                                    "seed": seed_idx,
                                    "object": object_idx,
                                    **stats,
                                }
                            )
    raw = pd.DataFrame(rows)
    summary = (
        raw.groupby(["image_size", "num_pixels", "basis", "rho", "sigma_a", "window_frac", "window_frames"], as_index=False)
        .agg(
            gain_rel_mse_mean=("gain_rel_mse", "mean"),
            gain_rel_mse_std=("gain_rel_mse", "std"),
            gain_corr_mean=("gain_corr", "mean"),
            gain_corr_std=("gain_corr", "std"),
        )
        .sort_values(["basis", "rho", "sigma_a", "window_frames"])
    )
    best = summary.sort_values(["basis", "rho", "sigma_a", "gain_rel_mse_mean"]).groupby(
        ["basis", "rho", "sigma_a"], as_index=False
    ).head(1)
    fit_rows = []
    for basis_index, (basis_name, group) in enumerate(best.groupby("basis")):
        fit = fit_log_linear_bootstrap(
            group,
            "window_frames",
            ["rho", "sigma_a"],
            iterations=200,
            seed=seed + 15013 * basis_index,
        )
        fit_rows.append({"basis": basis_name, "law": "best_agc_window_frames ~ rho^a * sigma_a^b", **fit})
    fits = pd.DataFrame(fit_rows)
    return raw, summary, fits


def build_key_summary(
    fits: pd.DataFrame,
    frame_fits: pd.DataFrame,
    energy_summary: pd.DataFrame,
    flip_fits: pd.DataFrame,
    censored_summary: pd.DataFrame,
    agc_fits: pd.DataFrame,
) -> dict[str, object]:
    ok = fits[fits["fit_status"] == "ok"].copy() if "fit_status" in fits else pd.DataFrame()
    frame_ok = frame_fits[frame_fits["fit_status"] == "ok"].copy() if "fit_status" in frame_fits else pd.DataFrame()
    flip_ok = flip_fits[flip_fits["fit_status"] == "ok"].copy() if "fit_status" in flip_fits else pd.DataFrame()
    agc_ok = agc_fits[agc_fits["fit_status"] == "ok"].copy() if "fit_status" in agc_fits else pd.DataFrame()
    energy_max = energy_summary["num_pixels"].max() if len(energy_summary) else None
    energy_rows = []
    if energy_max is not None:
        energy_rows = (
            energy_summary[energy_summary["num_pixels"] == energy_max][
                ["basis", "top_5pct_energy_mean", "effective_rank_frac_mean"]
            ]
            .sort_values("basis")
            .to_dict(orient="records")
        )
    return {
        "error_sigma_exp_min": float(ok["sigma_delta_exponent"].min()) if len(ok) else None,
        "error_sigma_exp_max": float(ok["sigma_delta_exponent"].max()) if len(ok) else None,
        "error_r2_min": float(ok["r2"].min()) if len(ok) else None,
        "frame": frame_ok[["basis", "sigma_delta_exponent", "num_frames_exponent", "r2"]].to_dict(orient="records")
        if len(frame_ok)
        else [],
        "energy_largest_size": int(energy_max) if energy_max is not None else None,
        "energy_largest": energy_rows,
        "flip_ok": flip_ok[["correction", "challenger", "sigma_a_exponent", "r2", "n"]].to_dict(orient="records")
        if len(flip_ok)
        else [],
        "flip_status_counts": flip_fits["fit_status"].value_counts().to_dict()
        if "fit_status" in flip_fits
        else {},
        "censored_interval_counts": censored_summary[
            ["correction", "challenger", "observed_points", "left_censored_points", "not_reached_points"]
        ].to_dict(orient="records")
        if len(censored_summary)
        else [],
        "agc_window_fits": agc_ok[["basis", "rho_exponent", "sigma_a_exponent", "r2"]].to_dict(orient="records")
        if len(agc_ok)
        else [],
    }


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
    parser.add_argument("--bootstrap", type=int, default=200)
    parser.add_argument("--agc-size", type=int, default=32)
    parser.add_argument("--agc-bases", default="random_uniform random_binary hadamard_paired srht_paired")
    parser.add_argument("--agc-rhos", default="0.001 0.003 0.01 0.03 0.1 0.3 1.0")
    parser.add_argument("--agc-sigmas", default="0.05 0.15 0.30 0.50")
    parser.add_argument("--agc-window-fracs", default="0.005 0.01 0.02 0.05 0.10 0.20")
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

    raw, summary, fits = run_error_scaling(
        sizes,
        basis_names,
        args.objects,
        args.seeds,
        residual_sigmas,
        args.seed,
        bootstrap_iterations=args.bootstrap,
    )
    energy, energy_summary = run_energy_concentration(sizes, basis_names, args.objects, args.seed)
    frame_raw, frame_summary, frame_fits = run_random_frame_scaling(
        args.frame_sweep_size,
        parse_floats(args.frame_factors),
        args.objects,
        args.seeds,
        residual_sigmas,
        args.seed,
        bootstrap_iterations=args.bootstrap,
    )
    phase_dir = args.phase_dir if args.phase_dir.is_absolute() else root / args.phase_dir
    flip_fits = fit_flip_boundaries(phase_dir, bootstrap_iterations=args.bootstrap, seed=args.seed)
    censored_intervals, censored_summary, censored_fits = build_censored_flip_intervals(phase_dir)
    agc_raw, agc_summary, agc_fits = run_agc_window_law(
        args.agc_size,
        [part for part in args.agc_bases.replace(",", " ").split() if part.strip()],
        args.objects,
        args.seeds,
        parse_floats(args.agc_rhos),
        parse_floats(args.agc_sigmas),
        parse_floats(args.agc_window_fracs),
        args.seed,
    )

    raw.to_csv(out_dir / "m4_error_scaling.csv", index=False)
    summary.to_csv(out_dir / "m4_error_scaling_summary.csv", index=False)
    fits.to_csv(out_dir / "m4_error_scaling_fit.csv", index=False)
    energy.to_csv(out_dir / "m4_energy_concentration.csv", index=False)
    energy_summary.to_csv(out_dir / "m4_energy_concentration_summary.csv", index=False)
    frame_raw.to_csv(out_dir / "m4_random_frame_scaling.csv", index=False)
    frame_summary.to_csv(out_dir / "m4_random_frame_scaling_summary.csv", index=False)
    frame_fits.to_csv(out_dir / "m4_random_frame_scaling_fit.csv", index=False)
    flip_fits.to_csv(out_dir / "m4_flip_boundary_fit.csv", index=False)
    censored_intervals.to_csv(out_dir / "m4_flip_boundary_censored_intervals.csv", index=False)
    censored_summary.to_csv(out_dir / "m4_flip_boundary_censored_summary.csv", index=False)
    censored_fits.to_csv(out_dir / "m4_flip_boundary_censored_fit.csv", index=False)
    agc_raw.to_csv(out_dir / "m4_agc_window_law.csv", index=False)
    agc_summary.to_csv(out_dir / "m4_agc_window_law_summary.csv", index=False)
    agc_fits.to_csv(out_dir / "m4_agc_window_law_fit.csv", index=False)
    key_summary = build_key_summary(fits, frame_fits, energy_summary, flip_fits, censored_summary, agc_fits)
    (out_dir / "m4_key_summary.json").write_text(json.dumps(key_summary, indent=2), encoding="utf-8")

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
            "m4_flip_boundary_censored_intervals.csv",
            "m4_flip_boundary_censored_summary.csv",
            "m4_flip_boundary_censored_fit.csv",
            "m4_agc_window_law.csv",
            "m4_agc_window_law_summary.csv",
            "m4_agc_window_law_fit.csv",
            "m4_key_summary.json",
        ],
    }
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"wrote {out_dir / 'm4_error_scaling_fit.csv'}")
    print(f"wrote {out_dir / 'm4_random_frame_scaling_fit.csv'}")
    print(f"wrote {out_dir / 'm4_energy_concentration_summary.csv'}")
    print(f"wrote {out_dir / 'm4_flip_boundary_fit.csv'}")


if __name__ == "__main__":
    main()
