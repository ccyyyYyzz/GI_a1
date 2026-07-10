"""R15 theorem-contract run for Prop. 3 paired and same-record estimators.

The production ``median(pair_sum)`` estimator remains unchanged, with a
theorem-faithful true-S1 arm added on the same objects and OU traces.  The
optional blind arm exports the exact reconstruction-space decomposition for
the noiseless same-record protocol; because that protocol contains no additive
detector noise, its residual--noise cross term is structurally absent rather
than empirically estimated.  Output authority is derived from manifest
provenance rather than the output-directory name.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from run_mechanism_m1 import make_synthetic_objects, object_metrics
from src.basis import basis_frame_budget, make_basis
from src.mechanisms import apply_correction, gain_error_stats, make_multiplicative_channel
from src.paper_experiments import build_run_manifest, classify_run_authority


ROOT = Path(__file__).resolve().parent
GRID_RHOS = [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0]
GRID_SIGMAS = [0.05, 0.10, 0.15, 0.30, 0.50]
CONFIG_SEED = 20240708
IMAGE_SIZE = 32
NUM_OBJECTS = 10
DEFAULT_NUM_SEEDS = 5
EPS = 1.0e-8


def raw_rel_mse(reconstruction: torch.Tensor, target: torch.Tensor) -> float:
    x_hat = reconstruction.reshape(-1).detach().cpu().to(dtype=torch.float64)
    x = target.reshape(-1).detach().cpu().to(dtype=torch.float64)
    return float((x_hat - x).square().sum() / x.square().sum().clamp_min(1.0e-12))


def first_crossing(rhos: np.ndarray, margin: np.ndarray) -> tuple[float, str]:
    if margin[0] >= 0.0:
        return float(rhos[0]), "left_censored"
    for index in range(len(rhos) - 1):
        if margin[index] < 0.0 <= margin[index + 1]:
            lo = math.log10(float(rhos[index]))
            hi = math.log10(float(rhos[index + 1]))
            fraction = -float(margin[index]) / float(margin[index + 1] - margin[index])
            return float(10.0 ** (lo + fraction * (hi - lo))), "observed"
    return float("nan"), "not_reached"


def pooled_slope(frame: pd.DataFrame, value_column: str) -> dict[str, float | int]:
    valid = frame[
        (frame["sigma_a"] >= 0.1)
        & (frame["emp_status"] == "observed")
        & np.isfinite(frame[value_column])
    ]
    x = np.log10(valid["sigma_a"].to_numpy(dtype=float))
    y = np.log10(valid[value_column].to_numpy(dtype=float))
    slope, intercept = np.polyfit(x, y, 1)
    fitted = slope * x + intercept
    ss_res = float(np.square(y - fitted).sum())
    ss_tot = float(np.square(y - y.mean()).sum())
    return {
        "n_cells": int(len(valid)),
        "slope": float(slope),
        "intercept": float(intercept),
        "r_squared": float(1.0 - ss_res / ss_tot),
    }


def random_leverage(basis, ideal: torch.Tensor, target: torch.Tensor) -> float:
    design = basis.patterns.to(dtype=torch.float64)
    centered = design - design.mean(dim=0, keepdim=True)
    variance = centered.square().mean(dim=0).clamp_min(EPS)
    column_norm_sq = (centered / (float(basis.num_frames) * variance)).square().sum(dim=1)
    b = ideal.to(dtype=torch.float64)
    s2 = target.to(dtype=torch.float64).square().sum().clamp_min(1.0e-12)
    return float((b.square() * column_norm_sq).sum() / s2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/prop3_estimator_contract_r15_provisional"),
    )
    parser.add_argument("--mode", choices=("all", "pair", "blind"), default="all")
    parser.add_argument("--num-seeds", type=int, default=DEFAULT_NUM_SEEDS)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace only this runner's known outputs in an existing directory.",
    )
    args = parser.parse_args()
    if args.num_seeds <= 0:
        raise ValueError("--num-seeds must be positive")

    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_names = (
        "contract_constants.csv",
        "pair_contract_scan.csv",
        "oracle_raw_scan.csv",
        "pair_boundary.csv",
        "blind_trace_diagnostics.csv",
        "blind_projection_diagnostics.csv",
        "pair_contract_summary.json",
        "run_manifest.json",
    )
    existing_outputs = [output_dir / name for name in generated_names if (output_dir / name).exists()]
    if existing_outputs and not args.overwrite:
        names = ", ".join(path.name for path in existing_outputs)
        raise FileExistsError(
            f"Refusing to mix this run with existing outputs ({names}); "
            "use a fresh --output-dir or pass --overwrite."
        )
    if args.overwrite:
        for path in existing_outputs:
            path.unlink()
    started = time.time()

    num_pixels = IMAGE_SIZE * IMAGE_SIZE
    frame_budget, _ = basis_frame_budget(num_pixels)
    agc_window = max(9, int(0.05 * frame_budget))
    objects = make_synthetic_objects(NUM_OBJECTS, IMAGE_SIZE, CONFIG_SEED)
    basis_hadamard = make_basis(
        "hadamard_paired", num_pixels=num_pixels, seed=CONFIG_SEED
    )
    basis_random = make_basis(
        "random_uniform",
        num_pixels=num_pixels,
        num_frames=frame_budget,
        seed=CONFIG_SEED,
        reconstruction="correlation",
    )
    ideal_h = [basis_hadamard.measure(obj) for obj in objects]
    ideal_r = [basis_random.measure(obj) for obj in objects]

    constants_rows: list[dict[str, float | int]] = []
    for object_index, target in enumerate(objects):
        target64 = target.to(dtype=torch.float64)
        s1 = float(target64.sum())
        s2 = float(target64.square().sum())
        coefficients = (
            ideal_h[object_index][0::2] - ideal_h[object_index][1::2]
        ).to(dtype=torch.float64)
        x = coefficients / s1
        clean_random = basis_random.reconstruct(ideal_r[object_index])
        constants_rows.append(
            {
                "object": object_index,
                "S1": s1,
                "S2": s2,
                "K_eff": s1 * s1 / s2,
                "D_H": float((1.0 - x.square()).square().mean()),
                "C0_floor_raw_fix": raw_rel_mse(clean_random, target) * frame_budget,
                "random_leverage_exact": random_leverage(
                    basis_random, ideal_r[object_index], target
                ),
            }
        )
    constants = pd.DataFrame(constants_rows)
    constants.to_csv(output_dir / "contract_constants.csv", index=False)

    pair_rows: list[dict[str, object]] = []
    oracle_rows: list[dict[str, object]] = []
    blind_rows: list[dict[str, object]] = []
    projected_u: dict[tuple[str, float, float, int], list[np.ndarray]] = defaultdict(list)
    projected_meta: dict[tuple[str, float, float, int], dict[str, object]] = {}

    total_cells = len(GRID_SIGMAS) * len(GRID_RHOS) * args.num_seeds
    completed = 0
    for sigma in GRID_SIGMAS:
        for rho in GRID_RHOS:
            for seed_index in range(args.num_seeds):
                channel = make_multiplicative_channel(
                    frame_budget,
                    model="ou",
                    rho=float(rho),
                    sigma_a=float(sigma),
                    seed=9000 + seed_index,
                    device="cpu",
                    dtype=torch.float32,
                )
                gains = channel.gains
                delta_pair = (
                    gains[1::2].to(dtype=torch.float64)
                    / gains[0::2].to(dtype=torch.float64)
                    - 1.0
                )

                for object_index, target in enumerate(objects):
                    const = constants.iloc[object_index]
                    target64 = target.to(dtype=torch.float64)
                    s1 = float(const.S1)
                    s2 = float(const.S2)

                    if args.mode in {"all", "pair"}:
                        observed_h = ideal_h[object_index] * gains
                        plus = observed_h[0::2].to(dtype=torch.float64)
                        minus = observed_h[1::2].to(dtype=torch.float64)
                        pair_sum = plus + minus
                        coefficients = (
                            ideal_h[object_index][0::2]
                            - ideal_h[object_index][1::2]
                        ).to(dtype=torch.float64)
                        x = coefficients / s1
                        denominator = 2.0 + delta_pair * (1.0 - x)
                        e_f7 = (
                            -s1
                            * delta_pair
                            * (1.0 - x.square())
                            / denominator
                        )

                        for estimator, total in (
                            ("true_s1", s1),
                            ("median_pair_sum", None),
                        ):
                            corrected = apply_correction(
                                observed_h,
                                "pairwise",
                                paired=True,
                                pair_total_intensity=total,
                            )
                            estimated = corrected.values.to(dtype=torch.float64)
                            s1_hat = s1 if total is not None else float(pair_sum.median().abs())
                            gamma = s1_hat / s1
                            expected_error = gamma * e_f7 + (gamma - 1.0) * coefficients
                            actual_error = estimated - coefficients
                            reconstruction = basis_hadamard.reconstruct(
                                corrected.values, values_are_coefficients=True
                            )
                            metrics = object_metrics(reconstruction, target)
                            k = int(coefficients.numel())
                            f7_component = (
                                gamma * gamma * float(e_f7.square().sum()) / (k * s2)
                            )
                            gauge_component = (gamma - 1.0) ** 2
                            cross_component = (
                                2.0
                                * gamma
                                * (gamma - 1.0)
                                * float(torch.dot(e_f7, coefficients))
                                / (k * s2)
                            )
                            measured_coefficient_risk = float(
                                actual_error.square().sum() / (k * s2)
                            )
                            pair_rows.append(
                                {
                                    "estimator": estimator,
                                    "sigma_a": sigma,
                                    "rho": rho,
                                    "seed": seed_index,
                                    "object": object_index,
                                    "S1_true": s1,
                                    "S1_hat": s1_hat,
                                    "gamma": gamma,
                                    "gamma_minus_1_sq": (gamma - 1.0) ** 2,
                                    "min_pair_sum": float(pair_sum.min()),
                                    "n_denominator_clipped": int((pair_sum <= EPS).sum()),
                                    "delta_mean": float(delta_pair.mean()),
                                    "delta_second_moment": float(delta_pair.square().mean()),
                                    "rel_mse_raw": raw_rel_mse(reconstruction, target),
                                    "rel_mse_aligned": float(metrics["rel_mse"]),
                                    "coefficient_risk_raw": measured_coefficient_risk,
                                    "risk_f7_component": f7_component,
                                    "risk_gauge_component": gauge_component,
                                    "risk_normalization_increment_cross": cross_component,
                                    "risk_decomposition_sum": (
                                        f7_component + gauge_component + cross_component
                                    ),
                                    "risk_decomposition_abs_error": abs(
                                        measured_coefficient_risk
                                        - f7_component
                                        - gauge_component
                                        - cross_component
                                    ),
                                    "coefficient_identity_max_abs_over_S1": float(
                                        (actual_error - expected_error).abs().max() / s1
                                    ),
                                }
                            )

                        corrected_oracle = apply_correction(
                            ideal_r[object_index] * gains,
                            "oracle",
                            true_gains=gains,
                            paired=False,
                        )
                        reconstruction_oracle = basis_random.reconstruct(
                            corrected_oracle.values
                        )
                        oracle_rows.append(
                            {
                                "sigma_a": sigma,
                                "rho": rho,
                                "seed": seed_index,
                                "object": object_index,
                                "rel_mse_raw": raw_rel_mse(
                                    reconstruction_oracle, target
                                ),
                            }
                        )

                    if args.mode in {"all", "blind"}:
                        ideal = ideal_r[object_index]
                        clean_reconstruction = basis_random.reconstruct(ideal)
                        d0 = (
                            clean_reconstruction.to(dtype=torch.float64) - target64
                        )
                        observed = ideal * gains
                        for correction in ("agc", "scgi_proxy"):
                            corrected = apply_correction(
                                observed,
                                correction,
                                paired=False,
                                agc_window=agc_window,
                            )
                            if corrected.gain_hat is None:
                                raise RuntimeError(f"{correction} did not return gain_hat")
                            residual = (
                                gains.to(dtype=torch.float64)
                                / corrected.gain_hat.to(dtype=torch.float64).clamp_min(EPS)
                                - 1.0
                            )
                            u = basis_random.reconstruct(
                                (ideal.to(dtype=torch.float64) * residual).to(dtype=ideal.dtype)
                            ).to(dtype=torch.float64)
                            reconstruction = basis_random.reconstruct(corrected.values)
                            total_error = reconstruction.to(dtype=torch.float64) - target64
                            clean_floor = float(d0.square().sum() / s2)
                            gain_energy = float(u.square().sum() / s2)
                            clean_cross = float(2.0 * torch.dot(d0, u) / s2)
                            raw_total = float(total_error.square().sum() / s2)
                            identity_sum = clean_floor + gain_energy + clean_cross
                            residual_centered = residual - residual.mean()
                            lag_denom = float(residual_centered.square().sum())
                            lag1 = (
                                float(
                                    torch.dot(
                                        residual_centered[:-1], residual_centered[1:]
                                    )
                                    / lag_denom
                                )
                                if lag_denom > 0.0
                                else float("nan")
                            )
                            gain_stats = gain_error_stats(corrected.gain_hat, gains)
                            q_delta = float(residual.square().mean())
                            blind_rows.append(
                                {
                                    "correction": correction,
                                    "sigma_a": sigma,
                                    "rho": rho,
                                    "seed": seed_index,
                                    "object": object_index,
                                    "q_delta_raw": q_delta,
                                    "m_delta": float(residual.mean()),
                                    "var_delta_scalar": float(residual_centered.square().mean()),
                                    "gain_rel_mse_aligned": float(gain_stats["gain_rel_mse"]),
                                    "qdelta_over_aligned": (
                                        q_delta / float(gain_stats["gain_rel_mse"])
                                        if float(gain_stats["gain_rel_mse"]) > 0.0
                                        else float("nan")
                                    ),
                                    "delta_lag1_corr": lag1,
                                    "raw_rel_mse_total": raw_total,
                                    "projected_gain_energy": gain_energy,
                                    "clean_floor_raw": clean_floor,
                                    "clean_floor_gain_cross": clean_cross,
                                    "raw_identity_sum": identity_sum,
                                    "raw_identity_abs_error": abs(raw_total - identity_sum),
                                    "scalar_qdelta_proxy": float(
                                        const.random_leverage_exact * q_delta
                                    ),
                                    "xi_present": False,
                                    "delta_xi_cross": 0.0,
                                }
                            )
                            key = (correction, sigma, rho, object_index)
                            projected_u[key].append(u.cpu().numpy())
                            projected_meta[key] = {
                                "d0": d0.cpu().numpy(),
                                "s2": s2,
                                "clean_floor": clean_floor,
                                "leverage": float(const.random_leverage_exact),
                            }

                completed += 1
                if completed % 25 == 0 or completed == total_cells:
                    print(
                        f"[{completed}/{total_cells}] sigma={sigma:g} rho={rho:g} "
                        f"seed={seed_index}",
                        flush=True,
                    )

    summary: dict[str, object] = {
        "mode": args.mode,
        "num_seeds": args.num_seeds,
    }

    if pair_rows:
        pair_frame = pd.DataFrame(pair_rows)
        pair_frame.to_csv(output_dir / "pair_contract_scan.csv", index=False)
        oracle_frame = pd.DataFrame(oracle_rows)
        oracle_frame.to_csv(output_dir / "oracle_raw_scan.csv", index=False)

        pair_agg = (
            pair_frame.groupby(
                ["estimator", "sigma_a", "object", "rho"], as_index=False
            )
            .agg(rel_mse_raw=("rel_mse_raw", "mean"))
        )
        oracle_agg = (
            oracle_frame.groupby(["sigma_a", "object", "rho"], as_index=False)
            .agg(rel_mse_raw_oracle=("rel_mse_raw", "mean"))
        )
        boundary_rows: list[dict[str, object]] = []
        for (estimator, sigma, object_index), group in pair_agg.groupby(
            ["estimator", "sigma_a", "object"]
        ):
            group = group.sort_values("rho")
            oracle_group = oracle_agg[
                (oracle_agg.sigma_a == sigma)
                & (oracle_agg.object == object_index)
            ].sort_values("rho")
            merged = group.merge(
                oracle_group, on=["sigma_a", "object", "rho"], how="inner"
            )
            margin = np.log10(merged.rel_mse_raw.to_numpy()) - np.log10(
                merged.rel_mse_raw_oracle.to_numpy()
            )
            empirical, empirical_status = first_crossing(
                merged.rho.to_numpy(dtype=float), margin
            )
            const = constants.iloc[int(object_index)]
            q_raw = (
                2.0
                * (float(const.C0_floor_raw_fix) / frame_budget)
                / (
                    float(const.K_eff)
                    * float(const.D_H)
                    * float(sigma)
                    * float(sigma)
                )
            )
            predicted = -math.log(1.0 - q_raw) if q_raw < 1.0 else float("nan")
            predicted_status = "predicted" if q_raw < 1.0 else "Q_raw_ge_1_no_crossing"
            log_ratio = (
                math.log10(predicted / empirical)
                if empirical_status == "observed" and math.isfinite(predicted)
                else float("nan")
            )
            boundary_rows.append(
                {
                    "estimator": estimator,
                    "validation_role": (
                        "same_estimator_theorem_validation"
                        if estimator == "true_s1"
                        else "production_robustness_check"
                    ),
                    "sigma_a": sigma,
                    "object": int(object_index),
                    "rho_star_emp_raw": empirical,
                    "emp_status": empirical_status,
                    "Q_raw": q_raw,
                    "rho_star_pred_f7_leading": predicted,
                    "pred_status": predicted_status,
                    "log10_pred_over_emp": log_ratio,
                    "agreement_factor": 10.0 ** abs(log_ratio)
                    if math.isfinite(log_ratio)
                    else float("nan"),
                }
            )
        boundary = pd.DataFrame(boundary_rows)
        boundary.to_csv(output_dir / "pair_boundary.csv", index=False)

        pair_summary: dict[str, object] = {
            "max_coefficient_identity_abs_over_S1": float(
                pair_frame.coefficient_identity_max_abs_over_S1.max()
            ),
            "max_risk_decomposition_abs_error": float(
                pair_frame.risk_decomposition_abs_error.max()
            ),
            "max_denominator_clipped": int(pair_frame.n_denominator_clipped.max()),
        }
        for estimator in ("true_s1", "median_pair_sum"):
            cells = boundary[
                (boundary.estimator == estimator)
                & (boundary.sigma_a >= 0.1)
                & (boundary.emp_status == "observed")
            ]
            pair_summary[estimator] = {
                "validation_role": str(cells.validation_role.iloc[0]),
                "n_observed_crossings": int(len(cells)),
                "factor_median": float(cells.agreement_factor.median()),
                "factor_max": float(cells.agreement_factor.max()),
                "empirical_pooled_fit": pooled_slope(cells, "rho_star_emp_raw"),
                "prediction_pooled_fit": pooled_slope(
                    cells, "rho_star_pred_f7_leading"
                ),
            }
        summary["pair_contract"] = pair_summary

    if blind_rows:
        blind_frame = pd.DataFrame(blind_rows)
        blind_frame.to_csv(output_dir / "blind_trace_diagnostics.csv", index=False)
        projection_rows: list[dict[str, object]] = []
        for key, vectors in projected_u.items():
            correction, sigma, rho, object_index = key
            matrix = np.stack(vectors, axis=0).astype(np.float64)
            mean_u = matrix.mean(axis=0)
            meta = projected_meta[key]
            d0 = np.asarray(meta["d0"], dtype=np.float64)
            s2 = float(meta["s2"])
            projected_mean_energy = float(np.dot(mean_u, mean_u) / s2)
            centered = matrix - mean_u[None, :]
            projected_covariance_trace = float(np.square(centered).sum() / (len(vectors) * s2))
            clean_cross = float(2.0 * np.dot(d0, mean_u) / s2)
            exact_total = float(
                np.dot(d0 + mean_u, d0 + mean_u) / s2
                + projected_covariance_trace
            )
            rows = blind_frame[
                (blind_frame.correction == correction)
                & (blind_frame.sigma_a == sigma)
                & (blind_frame.rho == rho)
                & (blind_frame.object == object_index)
            ]
            measured = float(rows.raw_rel_mse_total.mean())
            projection_rows.append(
                {
                    "correction": correction,
                    "sigma_a": sigma,
                    "rho": rho,
                    "object": object_index,
                    "projected_mean_energy": projected_mean_energy,
                    "projected_covariance_trace": projected_covariance_trace,
                    "clean_floor_raw": float(meta["clean_floor"]),
                    "clean_floor_mean_gain_cross": clean_cross,
                    "exact_projected_total": exact_total,
                    "measured_raw_total_mean": measured,
                    "exact_identity_abs_error": abs(exact_total - measured),
                    "scalar_qdelta_proxy": float(
                        float(meta["leverage"]) * rows.q_delta_raw.mean()
                    ),
                    "scalar_proxy_over_exact_gain_energy": float(
                        float(meta["leverage"]) * rows.q_delta_raw.mean()
                        / max(projected_mean_energy + projected_covariance_trace, 1.0e-30)
                    ),
                    "n_seeds": len(vectors),
                }
            )
        projection = pd.DataFrame(projection_rows)
        projection.to_csv(
            output_dir / "blind_projection_diagnostics.csv", index=False
        )
        summary["blind_contract"] = {
            "interpretation": "noiseless same-record conditional proxy; xi absent",
            "max_trace_identity_abs_error": float(
                blind_frame.raw_identity_abs_error.max()
            ),
            "max_projected_identity_abs_error": float(
                projection.exact_identity_abs_error.max()
            ),
            "qdelta_over_aligned_median": float(
                blind_frame.qdelta_over_aligned.median()
            ),
            "delta_lag1_corr_median": float(blind_frame.delta_lag1_corr.median()),
        }

    summary["runtime_seconds"] = float(time.time() - started)
    manifest = build_run_manifest(
        args,
        ROOT,
        output_dir=output_dir,
        extra={
            "script": "run_prop3_estimator_contract_r15.py",
            "config_seed": CONFIG_SEED,
            "image_size": IMAGE_SIZE,
            "num_objects": NUM_OBJECTS,
            "num_seeds": args.num_seeds,
            "frame_budget": frame_budget,
            "agc_window": agc_window,
            "rho_values": GRID_RHOS,
            "sigma_values": GRID_SIGMAS,
            "pair_estimators": ["true_s1", "median_pair_sum"],
            "metrics": {
                "primary": "raw relative MSE",
                "secondary": "least-squares scale-aligned relative MSE",
            },
            "detector_noise": "absent",
            "channel": {"model": "ou", "seed_rule": "9000+seed_index"},
        },
    )
    authority_status = classify_run_authority(manifest)
    summary["authority_status"] = authority_status
    manifest["authority_status"] = authority_status
    manifest["purpose"] = (
        "R15 submission-authoritative theorem-contract clean-commit rerun"
        if authority_status == "submission_authoritative_clean_commit"
        else "R15 provisional theorem-contract QA; not submission-authoritative"
    )
    (output_dir / "pair_contract_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    (output_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, default=str), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2), flush=True)
    print(f"[done] {time.time() - started:.1f}s -> {output_dir}", flush=True)


if __name__ == "__main__":
    main()
