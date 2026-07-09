from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from run_m4_agc_targeted import markdown_table
from src.config_utils import project_root


def _fit_log_linear_exact(frame: pd.DataFrame) -> tuple[np.ndarray, dict[str, float | int | str]]:
    data = frame.replace([np.inf, -np.inf], np.nan).dropna(subset=["rho", "sigma_a", "window_frames"])
    data = data[(data["rho"] > 0) & (data["sigma_a"] > 0) & (data["window_frames"] > 0)].copy()
    if len(data) < 3:
        return np.zeros(3, dtype=float), {"fit_status": "insufficient_exact_points", "n": int(len(data))}
    y = np.log10(data["window_frames"].to_numpy(dtype=float))
    x = np.column_stack(
        [
            np.ones(len(data), dtype=float),
            np.log10(data["rho"].to_numpy(dtype=float)),
            np.log10(data["sigma_a"].to_numpy(dtype=float)),
        ]
    )
    coef, *_ = np.linalg.lstsq(x, y, rcond=None)
    pred = x @ coef
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    return coef, {
        "fit_status": "ok",
        "n": int(len(data)),
        "r2": float(1.0 - ss_res / ss_tot) if ss_tot > 1.0e-15 else float("nan"),
        "rmse_log10": float(math.sqrt(ss_res / max(len(data), 1))),
    }


def _design(frame: pd.DataFrame) -> np.ndarray:
    return np.column_stack(
        [
            np.ones(len(frame), dtype=float),
            np.log10(frame["rho"].to_numpy(dtype=float)),
            np.log10(frame["sigma_a"].to_numpy(dtype=float)),
        ]
    )


def _censored_objective(coef: np.ndarray, frame: pd.DataFrame) -> float:
    pred = _design(frame) @ coef
    y = np.log10(frame["window_frames"].to_numpy(dtype=float))
    status = frame["boundary_status"].astype(str).to_numpy()
    residual = np.zeros(len(frame), dtype=float)
    exact = status == "interior"
    lower = status == "lower_bound"
    upper = status == "upper_bound"
    residual[exact] = pred[exact] - y[exact]
    residual[lower] = np.maximum(pred[lower] - y[lower], 0.0)
    residual[upper] = np.maximum(y[upper] - pred[upper], 0.0)
    return float(np.mean(residual**2))


def _coordinate_search(frame: pd.DataFrame, starts: list[np.ndarray]) -> np.ndarray:
    best = min(starts, key=lambda coef: _censored_objective(coef, frame)).astype(float)
    best_value = _censored_objective(best, frame)
    for step in [0.5, 0.2, 0.08, 0.03, 0.01, 0.003]:
        improved = True
        while improved:
            improved = False
            for idx in range(len(best)):
                for sign in (-1.0, 1.0):
                    candidate = best.copy()
                    candidate[idx] += sign * step
                    value = _censored_objective(candidate, frame)
                    if value + 1.0e-12 < best_value:
                        best = candidate
                        best_value = value
                        improved = True
    return best


def fit_basis(
    frame: pd.DataFrame, grid_bounds: dict[str, int]
) -> tuple[dict[str, float | int | str], pd.DataFrame]:
    basis = str(frame["basis"].iloc[0])
    selected_bounds = frame["window_frames"].agg(["min", "max"])
    sampled_min = int(grid_bounds["sampled_min_window_frames"])
    sampled_max = int(grid_bounds["sampled_max_window_frames"])
    intervals = frame.copy()
    intervals["censor_type"] = intervals["boundary_status"].map(
        {
            "interior": "exact",
            "lower_bound": "upper_bounded",
            "upper_bound": "lower_bounded",
        }
    )
    intervals["log_window_observed"] = np.log10(intervals["window_frames"].astype(float))
    intervals["sampled_min_window_frames"] = sampled_min
    intervals["sampled_max_window_frames"] = sampled_max
    intervals["log_window_lower"] = np.where(
        intervals["boundary_status"].astype(str) == "upper_bound",
        np.log10(float(sampled_max)),
        np.where(intervals["boundary_status"].astype(str) == "interior", intervals["log_window_observed"], -np.inf),
    )
    intervals["log_window_upper"] = np.where(
        intervals["boundary_status"].astype(str) == "lower_bound",
        np.log10(float(sampled_min)),
        np.where(intervals["boundary_status"].astype(str) == "interior", intervals["log_window_observed"], np.inf),
    )

    interior = intervals[intervals["boundary_status"] == "interior"].copy()
    interior_coef, interior_stats = _fit_log_linear_exact(interior)
    full_coef, _full_stats = _fit_log_linear_exact(intervals)
    starts = [interior_coef, full_coef, np.array([math.log10(float(sampled_min)), 0.0, 0.0], dtype=float)]
    coef = _coordinate_search(intervals, starts)
    pred = _design(intervals) @ coef
    intervals["predicted_log_window"] = pred
    intervals["predicted_window_frames"] = np.power(10.0, pred)

    status = intervals["boundary_status"].astype(str)
    exact = status == "interior"
    lower = status == "lower_bound"
    upper = status == "upper_bound"
    tolerance = 0.02
    satisfied = np.zeros(len(intervals), dtype=bool)
    y = intervals["log_window_observed"].to_numpy(dtype=float)
    exact_tolerance = float(interior_stats.get("rmse_log10", tolerance)) if interior_stats.get("fit_status") == "ok" else tolerance
    if not math.isfinite(exact_tolerance):
        exact_tolerance = tolerance
    satisfied[exact.to_numpy()] = np.abs(pred[exact.to_numpy()] - y[exact.to_numpy()]) <= max(
        tolerance,
        exact_tolerance,
    )
    satisfied[lower.to_numpy()] = pred[lower.to_numpy()] <= y[lower.to_numpy()] + tolerance
    satisfied[upper.to_numpy()] = pred[upper.to_numpy()] >= y[upper.to_numpy()] - tolerance
    intervals["interval_satisfied"] = satisfied
    intervals["hinge_residual_log10"] = 0.0
    intervals.loc[exact, "hinge_residual_log10"] = pred[exact.to_numpy()] - y[exact.to_numpy()]
    intervals.loc[lower, "hinge_residual_log10"] = np.maximum(pred[lower.to_numpy()] - y[lower.to_numpy()], 0.0)
    intervals.loc[upper, "hinge_residual_log10"] = np.maximum(y[upper.to_numpy()] - pred[upper.to_numpy()], 0.0)

    exact_rmse = float(
        math.sqrt(np.mean((pred[exact.to_numpy()] - y[exact.to_numpy()]) ** 2))
    ) if int(exact.sum()) else float("nan")
    hinge_rmse = float(math.sqrt(_censored_objective(coef, intervals)))
    exact_frac = float(np.mean(satisfied[exact.to_numpy()])) if int(exact.sum()) else float("nan")
    bounded_mask = (lower | upper).to_numpy()
    bounded_frac = float(np.mean(satisfied[bounded_mask])) if int(np.sum(bounded_mask)) else float("nan")
    interval_satisfaction_frac = float(np.mean(satisfied))
    result: dict[str, float | int | str] = {
        "basis": basis,
        "model": "censored_hinge_power_law",
        "fit_status": "ok",
        "n_total": int(len(intervals)),
        "n_exact": int(exact.sum()),
        "n_upper_bounded": int(lower.sum()),
        "n_lower_bounded": int(upper.sum()),
        "n_upper_censored": int(lower.sum()),
        "n_lower_censored": int(upper.sum()),
        "intercept": float(coef[0]),
        "rho_exponent": float(coef[1]),
        "sigma_a_exponent": float(coef[2]),
        "hinge_rmse_log10": hinge_rmse,
        "exact_rmse_log10": exact_rmse,
        "exact_within_tolerance_frac": exact_frac,
        "bounded_inequality_satisfied_frac": bounded_frac,
        "interval_satisfaction_frac": interval_satisfaction_frac,
        "interval_consistency_frac": interval_satisfaction_frac,
        "interior_fit_r2": float(interior_stats.get("r2", float("nan"))),
        "interior_fit_rmse_log10": float(interior_stats.get("rmse_log10", float("nan"))),
        "sampled_min_window_frames": sampled_min,
        "sampled_max_window_frames": sampled_max,
        "selected_min_window_frames": int(selected_bounds["min"]),
        "selected_max_window_frames": int(selected_bounds["max"]),
    }
    return result, intervals


def write_report(out_dir: Path, fits: pd.DataFrame, intervals: pd.DataFrame) -> None:
    lines = [
        "# Boundary-Aware M4 AGC Analysis",
        "",
        "The targeted AGC sweep often selects the smallest sampled window. This",
        "analysis treats those selections as censored observations rather than",
        "exact optima: a lower-bound grid hit means the true optimum is at or",
        "below the sampled minimum, while an interior hit remains an exact",
        "best-window observation.",
        "",
        "## Censored Power-Law Fits",
        "",
        markdown_table(
            fits[
                [
                    "basis",
                    "n_total",
                    "n_exact",
                    "n_upper_bounded",
                    "rho_exponent",
                    "sigma_a_exponent",
                    "hinge_rmse_log10",
                    "interval_satisfaction_frac",
                    "bounded_inequality_satisfied_frac",
                    "interior_fit_r2",
                ]
            ]
        ),
        "",
        "## Interpretation",
        "",
        "High interval satisfaction with many bounded points supports a weaker",
        "claim than an exact best-window law: the data identify a feasible",
        "window region and confirm boundary pressure, but do not pin down a",
        "unique optimum in boundary-dominated cells. The satisfaction fraction",
        "uses exact-point tolerance and bounded-point hinge inequalities; it is",
        "not a statistical coverage probability.",
        "",
    ]
    status_counts = (
        intervals.groupby(["basis", "censor_type"], as_index=False)
        .size()
        .pivot(index="basis", columns="censor_type", values="size")
        .fillna(0)
        .reset_index()
    )
    lines.extend(["## Censor Counts", "", markdown_table(status_counts), ""])
    out_dir.joinpath("m4_agc_boundary_aware_report.md").write_text("\n".join(lines), encoding="utf-8")
    summary = {
        "fits": fits.to_dict(orient="records"),
        "censor_counts": status_counts.to_dict(orient="records"),
        "overall_interval_satisfaction_frac": float(intervals["interval_satisfied"].mean()),
        "overall_interval_consistency_frac": float(intervals["interval_satisfied"].mean()),
    }
    out_dir.joinpath("m4_agc_boundary_aware_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Boundary-aware/censored AGC best-window analysis.")
    parser.add_argument("--input-dir", type=Path, default=Path("results/theory_m4_agc_targeted_r1"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/theory_m4_agc_boundary_aware_r1"))
    args = parser.parse_args()

    root = project_root()
    input_dir = args.input_dir if args.input_dir.is_absolute() else root / args.input_dir
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    best_path = input_dir / "m4_agc_targeted_best_windows.csv"
    if not best_path.exists():
        raise FileNotFoundError(best_path)
    summary_path = input_dir / "m4_agc_targeted_summary.csv"
    if not summary_path.exists():
        raise FileNotFoundError(summary_path)
    best = pd.read_csv(best_path)
    summary = pd.read_csv(summary_path)
    grid_bounds_by_basis = {
        str(basis): {
            "sampled_min_window_frames": int(group["window_frames"].min()),
            "sampled_max_window_frames": int(group["window_frames"].max()),
        }
        for basis, group in summary.groupby("basis", sort=True)
    }
    fit_rows: list[dict[str, float | int | str]] = []
    interval_frames: list[pd.DataFrame] = []
    for _basis, group in best.groupby("basis", sort=True):
        basis = str(_basis)
        if basis not in grid_bounds_by_basis:
            raise ValueError(f"missing summary grid bounds for basis {basis}")
        fit, intervals = fit_basis(group.reset_index(drop=True), grid_bounds_by_basis[basis])
        fit_rows.append(fit)
        interval_frames.append(intervals)
    fits = pd.DataFrame(fit_rows).sort_values("basis")
    intervals = pd.concat(interval_frames, ignore_index=True)
    fits.to_csv(out_dir / "m4_agc_boundary_aware_fit.csv", index=False)
    intervals.to_csv(out_dir / "m4_agc_boundary_aware_intervals.csv", index=False)
    write_report(out_dir, fits, intervals)
    print(f"wrote {out_dir}")


if __name__ == "__main__":
    main()
