"""Compact M1 mechanism-study runner.

The runner writes CSV files under ``results/mechanism_m1`` for:

* oracle/none/blind-AGC reconstruction under multiplicative drift;
* residual gain error propagation through random and paired bases;
* pairwise normalization failure as adjacent-frame drift increases.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Dict, Iterable, List

import numpy as np
import pandas as pd
import torch
import yaml
from PIL import Image, ImageDraw, ImageFilter

from src.basis import MeasurementBasis, basis_frame_budget, make_basis
from src.mechanisms import apply_correction, gain_error_stats, make_multiplicative_channel, simulate_channel_measurements


ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = ROOT / "config.yaml"


def load_config(path: Path, profile: str) -> Dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    config["profile"] = profile
    return config


def make_synthetic_objects(count: int, image_size: int, seed: int) -> List[torch.Tensor]:
    """Generate small deterministic grayscale objects without external datasets."""

    rng = np.random.default_rng(int(seed))
    objects: List[torch.Tensor] = []
    for index in range(int(count)):
        image = Image.new("L", (image_size, image_size), 0)
        draw = ImageDraw.Draw(image)

        digit = str(index % 10)
        text_x = int(rng.integers(max(1, image_size // 8), max(2, image_size // 3)))
        text_y = int(rng.integers(max(1, image_size // 8), max(2, image_size // 3)))
        draw.text((text_x, text_y), digit, fill=int(rng.integers(140, 230)))

        for _ in range(3):
            x0 = int(rng.integers(0, max(1, image_size - 8)))
            y0 = int(rng.integers(0, max(1, image_size - 8)))
            width = int(rng.integers(max(4, image_size // 8), max(5, image_size // 2)))
            height = int(rng.integers(max(4, image_size // 8), max(5, image_size // 2)))
            x1 = min(image_size - 1, x0 + width)
            y1 = min(image_size - 1, y0 + height)
            fill = int(rng.integers(60, 210))
            if rng.random() < 0.5:
                draw.rectangle((x0, y0, x1, y1), outline=fill, fill=int(0.45 * fill))
            else:
                draw.ellipse((x0, y0, x1, y1), outline=fill, fill=int(0.35 * fill))

        for _ in range(2):
            y = int(rng.integers(0, image_size))
            draw.line((0, y, image_size - 1, y), fill=int(rng.integers(40, 140)), width=1)

        image = image.filter(ImageFilter.GaussianBlur(radius=0.45))
        array = np.asarray(image, dtype=np.float32) / 255.0
        if float(array.max()) > 0:
            array = array / float(array.max())
        objects.append(torch.from_numpy(array.reshape(-1)).to(dtype=torch.float32))
    return objects


def object_metrics(reconstruction: torch.Tensor, target: torch.Tensor) -> Dict[str, float]:
    """Scale-aligned reconstruction metrics for compact comparisons."""

    x_hat = reconstruction.reshape(-1).detach().cpu().to(dtype=torch.float64)
    x = target.reshape(-1).detach().cpu().to(dtype=torch.float64)
    scale = (x_hat @ x) / x_hat.pow(2).sum().clamp_min(1.0e-12)
    aligned = x_hat * scale
    error = aligned - x
    mse = error.pow(2).mean()
    rel_mse = mse / x.pow(2).mean().clamp_min(1.0e-12)
    psnr = 10.0 * math.log10(1.0 / max(float(mse.item()), 1.0e-12))
    return {
        "mse": float(mse.item()),
        "rel_mse": float(rel_mse.item()),
        "psnr": float(psnr),
        "recon_scale": float(scale.item()),
    }


def simulate_and_reconstruct(
    basis: MeasurementBasis,
    obj: torch.Tensor,
    correction: str,
    channel_model: str,
    rho: float,
    sigma_a: float,
    channel_seed: int,
    read_noise: float,
    noise_seed: int,
    agc_window: int,
) -> Dict[str, float]:
    ideal = basis.measure(obj)
    channel = make_multiplicative_channel(
        basis.num_frames,
        model=channel_model,
        rho=rho,
        sigma_a=sigma_a,
        seed=channel_seed,
        device=str(ideal.device),
        dtype=ideal.dtype,
    )
    observed = simulate_channel_measurements(ideal, channel, read_noise=read_noise, seed=noise_seed)
    corrected = apply_correction(
        observed,
        correction=correction,
        true_gains=channel.gains,
        paired=basis.paired,
        agc_window=agc_window,
    )
    recon = basis.reconstruct(corrected.values, values_are_coefficients=corrected.values_are_coefficients)
    metrics = object_metrics(recon, obj)
    metrics.update(gain_error_stats(corrected.gain_hat, channel.gains))
    return metrics


def reconstruct_observed(
    basis: MeasurementBasis,
    obj: torch.Tensor,
    observed: torch.Tensor,
    true_gains: torch.Tensor,
    correction: str,
    agc_window: int,
) -> Dict[str, float]:
    corrected = apply_correction(
        observed,
        correction=correction,
        true_gains=true_gains,
        paired=basis.paired,
        agc_window=agc_window,
    )
    recon = basis.reconstruct(corrected.values, values_are_coefficients=corrected.values_are_coefficients)
    metrics = object_metrics(recon, obj)
    metrics.update(gain_error_stats(corrected.gain_hat, true_gains))
    return metrics


def make_bases(num_pixels: int, seed: int, reconstruction: str) -> List[MeasurementBasis]:
    random_frames, _ = basis_frame_budget(num_pixels)
    return [
        make_basis("random_uniform", num_pixels=num_pixels, num_frames=random_frames, seed=seed, reconstruction=reconstruction),
        make_basis("random_binary", num_pixels=num_pixels, num_frames=random_frames, seed=seed + 17, reconstruction=reconstruction),
        make_basis("random_gaussian", num_pixels=num_pixels, num_frames=random_frames, seed=seed + 31, reconstruction=reconstruction),
        make_basis("hadamard_paired", num_pixels=num_pixels),
        make_basis("dct_paired", num_pixels=num_pixels),
        make_basis("fourier_fourstep", num_pixels=num_pixels, num_frames=random_frames),
        make_basis("srht_paired", num_pixels=num_pixels, seed=seed + 47),
    ]


def compact_values(values: Iterable[float], limit: int) -> List[float]:
    items = list(values)
    return items[: max(1, min(int(limit), len(items)))]


def run_oracle_agc(
    bases: List[MeasurementBasis],
    objects: List[torch.Tensor],
    seeds: int,
    rho_values: List[float],
    sigma_a: float,
    read_noise: float,
    agc_window: int,
) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    corrections = ["oracle", "none", "agc"]
    for basis in bases:
        for rho in rho_values:
            for seed_idx in range(seeds):
                for object_idx, obj in enumerate(objects):
                    ideal = basis.measure(obj)
                    channel = make_multiplicative_channel(
                        basis.num_frames,
                        model="ou",
                        rho=float(rho),
                        sigma_a=float(sigma_a),
                        seed=1000 + 97 * seed_idx,
                        device=str(ideal.device),
                        dtype=ideal.dtype,
                    )
                    observed = simulate_channel_measurements(
                        ideal,
                        channel,
                        read_noise=read_noise,
                        seed=2000 + 53 * object_idx + seed_idx,
                    )
                    for correction in corrections:
                        metrics = reconstruct_observed(
                            basis=basis,
                            obj=obj,
                            observed=observed,
                            true_gains=channel.gains,
                            correction=correction,
                            agc_window=agc_window,
                        )
                        rows.append(
                            {
                                "experiment": "oracle_agc",
                                "basis": basis.name,
                                "correction": correction,
                                "channel": "ou",
                                "rho": float(rho),
                                "sigma_a": float(sigma_a),
                                "seed": seed_idx,
                                "object": object_idx,
                                "num_frames": basis.num_frames,
                                "num_pixels": basis.num_pixels,
                                **metrics,
                            }
                        )
    return pd.DataFrame(rows)


def run_agc_window_sweep(
    bases: List[MeasurementBasis],
    objects: List[torch.Tensor],
    seeds: int,
    window_fracs: List[float],
    rho: float,
    sigma_a: float,
    read_noise: float,
) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    for basis in bases:
        for window_frac in window_fracs:
            window = max(3, int(round(float(window_frac) * basis.num_frames)))
            if window % 2 == 0:
                window += 1
            for seed_idx in range(seeds):
                for object_idx, obj in enumerate(objects):
                    ideal = basis.measure(obj)
                    channel = make_multiplicative_channel(
                        basis.num_frames,
                        model="ou",
                        rho=float(rho),
                        sigma_a=float(sigma_a),
                        seed=7000 + 97 * seed_idx,
                        device=str(ideal.device),
                        dtype=ideal.dtype,
                    )
                    observed = simulate_channel_measurements(
                        ideal,
                        channel,
                        read_noise=read_noise,
                        seed=7100 + 53 * object_idx + seed_idx,
                    )
                    metrics = reconstruct_observed(
                        basis=basis,
                        obj=obj,
                        observed=observed,
                        true_gains=channel.gains,
                        correction="agc",
                        agc_window=window,
                    )
                    rows.append(
                        {
                            "experiment": "agc_window_sweep",
                            "basis": basis.name,
                            "correction": "agc",
                            "channel": "ou",
                            "rho": float(rho),
                            "sigma_a": float(sigma_a),
                            "window_frac": float(window_frac),
                            "agc_window": int(window),
                            "seed": seed_idx,
                            "object": object_idx,
                            "num_frames": basis.num_frames,
                            "num_pixels": basis.num_pixels,
                            **metrics,
                        }
                    )
    return pd.DataFrame(rows)


def run_error_propagation(
    bases: List[MeasurementBasis],
    objects: List[torch.Tensor],
    seeds: int,
    residual_sigmas: List[float],
) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    for basis in bases:
        for sigma_delta in residual_sigmas:
            for seed_idx in range(seeds):
                generator = torch.Generator(device="cpu")
                generator.manual_seed(3000 + 131 * seed_idx + int(round(1000 * sigma_delta)))
                for object_idx, obj in enumerate(objects):
                    ideal = basis.measure(obj)
                    delta = torch.randn(ideal.shape, generator=generator, dtype=ideal.dtype) * float(sigma_delta)
                    perturbed = ideal * (1.0 + delta)
                    recon = basis.reconstruct(perturbed)
                    metrics = object_metrics(recon, obj)
                    rows.append(
                        {
                            "experiment": "error_propagation",
                            "basis": basis.name,
                            "correction": "synthetic_residual_gain",
                            "channel": "residual",
                            "rho": float("nan"),
                            "sigma_delta": float(sigma_delta),
                            "seed": seed_idx,
                            "object": object_idx,
                            "num_frames": basis.num_frames,
                            "num_pixels": basis.num_pixels,
                            **metrics,
                        }
                    )
    return pd.DataFrame(rows)


def fit_error_scaling(error_prop: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    df = error_prop[error_prop["sigma_delta"].astype(float) > 0].copy()
    for basis, group in df.groupby("basis"):
        summary = group.groupby("sigma_delta", as_index=False).agg(rel_mse_mean=("rel_mse", "mean"))
        usable = summary[(summary["sigma_delta"] > 0) & (summary["rel_mse_mean"] > 0)]
        if len(usable) < 2:
            slope = float("nan")
            intercept = float("nan")
            r2 = float("nan")
        else:
            x = np.log10(usable["sigma_delta"].to_numpy(dtype=float))
            y = np.log10(usable["rel_mse_mean"].to_numpy(dtype=float))
            slope, intercept = np.polyfit(x, y, deg=1)
            pred = slope * x + intercept
            denom = np.sum((y - y.mean()) ** 2)
            r2 = 1.0 - float(np.sum((y - pred) ** 2) / denom) if denom > 0 else float("nan")
        rows.append(
            {
                "basis": basis,
                "fit": "log_rel_mse_vs_log_sigma_delta",
                "slope": float(slope),
                "intercept": float(intercept),
                "r2": float(r2),
                "points": int(len(usable)),
            }
        )
    return pd.DataFrame(rows)


def run_pairwise_failure(
    bases: List[MeasurementBasis],
    objects: List[torch.Tensor],
    seeds: int,
    rho_values: List[float],
    sigma_values: List[float],
    read_noise: float,
    agc_window: int,
) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    paired_bases = [basis for basis in bases if basis.paired]
    corrections = ["oracle", "pairwise", "none"]
    for basis in paired_bases:
        for rho in rho_values:
            for sigma_a in sigma_values:
                for seed_idx in range(seeds):
                    for object_idx, obj in enumerate(objects):
                        ideal = basis.measure(obj)
                        channel = make_multiplicative_channel(
                            basis.num_frames,
                            model="jitter",
                            rho=float(rho),
                            sigma_a=float(sigma_a),
                            seed=4000 + 89 * seed_idx,
                            device=str(ideal.device),
                            dtype=ideal.dtype,
                        )
                        observed = simulate_channel_measurements(
                            ideal,
                            channel,
                            read_noise=read_noise,
                            seed=5000 + 41 * object_idx + seed_idx,
                        )
                        for correction in corrections:
                            metrics = reconstruct_observed(
                                basis=basis,
                                obj=obj,
                                observed=observed,
                                true_gains=channel.gains,
                                correction=correction,
                                agc_window=agc_window,
                            )
                            rows.append(
                                {
                                    "experiment": "pairwise_failure",
                                    "basis": basis.name,
                                    "correction": correction,
                                    "channel": "jitter",
                                    "rho": float(rho),
                                    "sigma_a": float(sigma_a),
                                    "seed": seed_idx,
                                    "object": object_idx,
                                    "num_frames": basis.num_frames,
                                    "num_pixels": basis.num_pixels,
                                    **metrics,
                                }
                            )
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame, group_cols: List[str]) -> pd.DataFrame:
    metric_cols = [col for col in ["mse", "rel_mse", "psnr", "gain_rel_mse", "gain_corr"] if col in df.columns]
    grouped = df.groupby(group_cols, dropna=False)[metric_cols]
    mean = grouped.mean().add_suffix("_mean")
    std = grouped.std(ddof=0).add_suffix("_std")
    return pd.concat([mean, std], axis=1).reset_index()


def append_findings(output_dir: Path, summary_path: Path) -> None:
    findings = ROOT / "FINDINGS.md"
    marker = "## M1 Smoke Runner"
    if findings.exists() and marker in findings.read_text(encoding="utf-8"):
        return
    text = (
        f"\n{marker}\n\n"
        "Experiment: compact oracle/AGC, residual error propagation, and pairwise failure scans.\n"
        "Prediction: oracle correction should bound attainable error; blind AGC should favor i.i.d. random/SRHT-like sequences; pairwise normalization should degrade under high adjacent-frame jitter.\n"
        f"Result: CSV outputs written to `{output_dir.as_posix()}` with summary `{summary_path.name}`.\n"
        "Supports/refutes: smoke data are intended for pipeline and mechanism sanity checks, not final paper-scale claims.\n"
        "Notes: use larger object/seed counts for publication figures.\n"
    )
    with findings.open("a", encoding="utf-8") as handle:
        handle.write(text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run compact M1 basis/channel mechanism smoke experiments.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--profile", default="smoke")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "mechanism_m1")
    parser.add_argument("--objects", type=int, default=None)
    parser.add_argument("--seeds", type=int, default=None)
    parser.add_argument("--reconstruction", choices=["least_squares", "correlation"], default="correlation")
    parser.add_argument("--no-findings", action="store_true", help="Do not append the short M1 note to FINDINGS.md.")
    args = parser.parse_args()

    config = load_config(args.config, args.profile)
    mechanism = config.get("mechanism", {})
    paths = config.get("paths", {})

    image_size = int(mechanism.get("image_size", 32))
    num_pixels = int(mechanism.get("num_pixels", image_size * image_size))
    if num_pixels != image_size * image_size:
        raise ValueError("The compact runner expects num_pixels == image_size * image_size.")

    compact_profile = args.profile == "smoke"
    object_count = int(args.objects if args.objects is not None else mechanism.get("objects", 10))
    seed_count = int(args.seeds if args.seeds is not None else mechanism.get("seeds", 5))
    if compact_profile:
        object_count = min(object_count, 2)
        seed_count = min(seed_count, 1)

    rho_values = compact_values(mechanism.get("rho_values", [0.001, 0.01, 0.1, 1.0]), 4)
    sigma_values = compact_values(mechanism.get("sigma_a_values", [0.05, 0.15, 0.3]), 3)
    sigma_for_agc = float(sigma_values[min(1, len(sigma_values) - 1)])
    read_noise = float(mechanism.get("read_noise", 0.0))
    agc_window = max(9, min(101, int(round(0.05 * 2 * num_pixels))))

    if not args.output_dir.is_absolute():
        args.output_dir = ROOT / args.output_dir
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    base_seed = int(config.get("seed", 20240708))
    objects = make_synthetic_objects(object_count, image_size=image_size, seed=base_seed)
    bases = make_bases(num_pixels=num_pixels, seed=base_seed, reconstruction=args.reconstruction)

    oracle_agc = run_oracle_agc(
        bases=bases,
        objects=objects,
        seeds=seed_count,
        rho_values=rho_values,
        sigma_a=sigma_for_agc,
        read_noise=read_noise,
        agc_window=agc_window,
    )
    agc_windows = run_agc_window_sweep(
        bases=bases,
        objects=objects,
        seeds=seed_count,
        window_fracs=[0.01, 0.02, 0.05, 0.10, 0.20],
        rho=0.01,
        sigma_a=sigma_for_agc,
        read_noise=read_noise,
    )
    error_prop = run_error_propagation(
        bases=bases,
        objects=objects,
        seeds=seed_count,
        residual_sigmas=[0.0, 0.02, 0.05, 0.10, 0.20],
    )
    pairwise = run_pairwise_failure(
        bases=bases,
        objects=objects,
        seeds=seed_count,
        rho_values=rho_values,
        sigma_values=sigma_values,
        read_noise=read_noise,
        agc_window=agc_window,
    )

    oracle_path = output_dir / "mechanism_m1_oracle_agc.csv"
    agc_window_path = output_dir / "mechanism_m1_agc_window_sweep.csv"
    error_path = output_dir / "mechanism_m1_error_propagation.csv"
    error_fit_path = output_dir / "mechanism_m1_error_scaling_fit.csv"
    pairwise_path = output_dir / "mechanism_m1_pairwise_failure.csv"
    summary_path = output_dir / "mechanism_m1_summary.csv"

    oracle_agc.to_csv(oracle_path, index=False)
    agc_windows.to_csv(agc_window_path, index=False)
    error_prop.to_csv(error_path, index=False)
    error_fit = fit_error_scaling(error_prop)
    error_fit.to_csv(error_fit_path, index=False)
    pairwise.to_csv(pairwise_path, index=False)

    summary_frames = [
        summarize(oracle_agc, ["experiment", "basis", "correction", "channel", "rho", "sigma_a"]),
        summarize(agc_windows, ["experiment", "basis", "correction", "channel", "rho", "sigma_a", "window_frac", "agc_window"]),
        summarize(error_prop, ["experiment", "basis", "correction", "channel", "sigma_delta"]),
        summarize(pairwise, ["experiment", "basis", "correction", "channel", "rho", "sigma_a"]),
    ]
    summary = pd.concat(summary_frames, ignore_index=True, sort=False)
    summary.to_csv(summary_path, index=False)

    manifest = pd.DataFrame(
        [
            {"file": oracle_path.name, "rows": len(oracle_agc)},
            {"file": agc_window_path.name, "rows": len(agc_windows)},
            {"file": error_path.name, "rows": len(error_prop)},
            {"file": error_fit_path.name, "rows": len(error_fit)},
            {"file": pairwise_path.name, "rows": len(pairwise)},
            {"file": summary_path.name, "rows": len(summary)},
        ]
    )
    manifest.to_csv(output_dir / "mechanism_m1_manifest.csv", index=False)

    if not args.no_findings:
        append_findings(output_dir, summary_path)

    print("M1 mechanism smoke complete")
    print(f"objects={object_count} seeds={seed_count} pixels={num_pixels} reconstruction={args.reconstruction}")
    print(f"wrote {oracle_path}")
    print(f"wrote {agc_window_path}")
    print(f"wrote {error_path}")
    print(f"wrote {error_fit_path}")
    print(f"wrote {pairwise_path}")
    print(f"wrote {summary_path}")


if __name__ == "__main__":
    main()
