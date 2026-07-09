from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from src.config_utils import project_root


CHALLENGERS = ["random_uniform", "random_binary", "fourier_fourstep", "dct_paired", "srht_paired"]


def fit_log_boundary(frame: pd.DataFrame) -> dict[str, object]:
    observed = frame[
        (frame["boundary_status"] == "observed")
        & frame["rho_star_log_interp"].notna()
        & (frame["rho_star_log_interp"] > 0)
        & (frame["sigma_a"] > 0)
    ].copy()
    if len(observed) < 3:
        return {"fit_status": "insufficient_observed_points", "n": int(len(observed))}
    x = np.log10(observed["sigma_a"].to_numpy(dtype=float))
    y = np.log10(observed["rho_star_log_interp"].to_numpy(dtype=float))
    design = np.column_stack([np.ones_like(x), x])
    coef, *_ = np.linalg.lstsq(design, y, rcond=None)
    pred = design @ coef
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    return {
        "fit_status": "ok",
        "n": int(len(observed)),
        "intercept": float(coef[0]),
        "sigma_a_exponent": float(coef[1]),
        "r2": float(1.0 - ss_res / ss_tot) if ss_tot > 0 else 1.0,
        "rmse_log10": float(math.sqrt(ss_res / max(len(y), 1))),
    }


def interpolate_boundary(rhos: np.ndarray, margins: np.ndarray) -> tuple[float | None, str]:
    order = np.argsort(rhos)
    rhos = rhos[order]
    margins = margins[order]
    valid = np.isfinite(rhos) & np.isfinite(margins)
    rhos = rhos[valid]
    margins = margins[valid]
    if len(rhos) == 0:
        return None, "missing"
    if margins[0] >= 0.0:
        return float(rhos[0]), "left_censored"
    for idx in range(len(rhos) - 1):
        left_margin = margins[idx]
        right_margin = margins[idx + 1]
        if left_margin < 0.0 <= right_margin:
            left_log = math.log10(float(rhos[idx]))
            right_log = math.log10(float(rhos[idx + 1]))
            frac = (0.0 - float(left_margin)) / (float(right_margin) - float(left_margin))
            return float(10 ** (left_log + frac * (right_log - left_log))), "observed"
    return None, "not_reached"


def load_phase_summary(phase_dir: Path) -> pd.DataFrame:
    summary_path = phase_dir / "phase_summary.csv"
    if summary_path.exists():
        return pd.read_csv(summary_path)
    scan_path = phase_dir / "phase_scan.csv"
    if not scan_path.exists():
        raise FileNotFoundError(f"Missing phase_summary.csv or phase_scan.csv in {phase_dir}")
    scan = pd.read_csv(scan_path)
    return (
        scan.groupby(["rho", "sigma_a", "basis", "correction"], as_index=False)
        .agg(
            psnr_mean=("psnr", "mean"),
            psnr_std=("psnr", "std"),
            rel_mse_mean=("rel_mse", "mean"),
            rel_mse_std=("rel_mse", "std"),
            num_frames=("num_frames", "first"),
            reference_frames=("reference_frames", "first"),
            total_physical_frames=("total_physical_frames", "first"),
        )
        .sort_values(["rho", "sigma_a", "psnr_mean"], ascending=[True, True, False])
    )


def build_boundary_tables(summary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    blind = summary[summary["correction"] != "oracle"].copy()
    for (sigma_a, correction), group in blind.groupby(["sigma_a", "correction"]):
        pivot = group.pivot_table(index="rho", columns="basis", values="psnr_mean", aggfunc="mean").sort_index()
        if "hadamard_paired" not in pivot.columns:
            continue
        for challenger in CHALLENGERS:
            if challenger not in pivot.columns:
                continue
            diff = pivot[challenger] - pivot["hadamard_paired"]
            rho_star, status = interpolate_boundary(diff.index.to_numpy(dtype=float), diff.to_numpy(dtype=float))
            rows.append(
                {
                    "sigma_a": float(sigma_a),
                    "correction": correction,
                    "challenger": challenger,
                    "baseline": "hadamard_paired",
                    "rho_star_log_interp": rho_star,
                    "boundary_status": status,
                    "max_margin_db": float(diff.max()),
                    "min_margin_db": float(diff.min()),
                    "points": int(diff.notna().sum()),
                    "rho_min": float(np.nanmin(diff.index.to_numpy(dtype=float))),
                    "rho_max": float(np.nanmax(diff.index.to_numpy(dtype=float))),
                }
            )
    boundaries = pd.DataFrame(rows)
    fit_rows: list[dict[str, object]] = []
    if not boundaries.empty:
        for keys, group in boundaries.groupby(["correction", "challenger", "baseline"]):
            fit_rows.append(
                {
                    "correction": keys[0],
                    "challenger": keys[1],
                    "baseline": keys[2],
                    "observed_points": int((group["boundary_status"] == "observed").sum()),
                    "left_censored_points": int((group["boundary_status"] == "left_censored").sum()),
                    "not_reached_points": int((group["boundary_status"] == "not_reached").sum()),
                    "law": "rho_star ~ sigma_a^a",
                    **fit_log_boundary(group),
                }
            )
    return boundaries, pd.DataFrame(fit_rows).sort_values(["correction", "challenger"])


def build_winner_tables(summary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    blind = summary[summary["correction"] != "oracle"].copy()
    equal_frame = blind[blind["total_physical_frames"] == blind["num_frames"]].copy()
    winners = {
        "all_non_oracle": blind.sort_values(["rho", "sigma_a", "psnr_mean"], ascending=[True, True, False])
        .groupby(["rho", "sigma_a"], as_index=False)
        .head(1),
        "equal_frame_non_oracle": equal_frame.sort_values(["rho", "sigma_a", "psnr_mean"], ascending=[True, True, False])
        .groupby(["rho", "sigma_a"], as_index=False)
        .head(1),
    }
    rows: list[dict[str, object]] = []
    for scope, table in winners.items():
        for (basis, correction), group in table.groupby(["basis", "correction"]):
            rows.append(
                {
                    "scope": scope,
                    "basis": basis,
                    "correction": correction,
                    "winning_cells": int(len(group)),
                    "rho_min": float(group["rho"].min()),
                    "rho_max": float(group["rho"].max()),
                    "sigma_min": float(group["sigma_a"].min()),
                    "sigma_max": float(group["sigma_a"].max()),
                    "psnr_mean_over_wins": float(group["psnr_mean"].mean()),
                }
            )
    winner_summary = pd.DataFrame(rows).sort_values(["scope", "winning_cells"], ascending=[True, False])
    return pd.concat(winners.values(), ignore_index=True), winner_summary


def write_report(out_dir: Path, phase_dir: Path, coverage: dict[str, object], fits: pd.DataFrame, winner_summary: pd.DataFrame) -> None:
    ok_fits = fits[(fits["fit_status"] == "ok") & (fits["r2"] >= 0.9)].copy() if "r2" in fits else pd.DataFrame()
    lines = [
        "# M2 Boundary Audit",
        "",
        f"Source phase directory: `{phase_dir.as_posix()}`",
        "",
        "## Rho Coverage",
        "",
    ]
    for key, value in coverage.items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Boundary Fits With R2 >= 0.9", ""])
    if ok_fits.empty:
        lines.append("No observed three-point boundary fit reaches R2 >= 0.9. Check censored rows before treating this as a failed trend.")
    else:
        columns = ["correction", "challenger", "observed_points", "left_censored_points", "not_reached_points", "sigma_a_exponent", "r2"]
        lines.append(ok_fits[columns].to_csv(index=False))
    lines.extend(["", "## Winner Summary", ""])
    if not winner_summary.empty:
        lines.append(winner_summary.to_csv(index=False))
    lines.extend(
        [
            "",
            "## Interpretation Notes",
            "",
            "- `observed` means the challenger crosses Hadamard within the sampled rho range using log-rho interpolation.",
            "- `left_censored` means the challenger is already >= Hadamard at the smallest sampled rho; this is stronger than an observed boundary for that grid.",
            "- `not_reached` means the challenger remains below Hadamard up to the largest sampled rho.",
        ]
    )
    (out_dir / "m2_boundary_audit_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_figures(out_dir: Path, summary: pd.DataFrame, boundaries: pd.DataFrame, fits: pd.DataFrame) -> list[str]:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return []

    written: list[str] = []
    sigma_values = sorted(float(x) for x in summary["sigma_a"].dropna().unique())
    sigma_plot = 0.30 if 0.30 in sigma_values else sigma_values[len(sigma_values) // 2]
    curve_specs = [
        ("srht_paired", "pairwise"),
        ("hadamard_paired", "pairwise"),
        ("srht_paired", "scgi_proxy"),
        ("random_binary", "agc"),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 4.5), dpi=160)
    for basis, correction in curve_specs:
        subset = summary[
            (summary["sigma_a"].astype(float) == sigma_plot)
            & (summary["basis"] == basis)
            & (summary["correction"] == correction)
        ].sort_values("rho")
        if subset.empty:
            continue
        ax.plot(subset["rho"], subset["psnr_mean"], marker="o", linewidth=1.8, label=f"{basis} + {correction}")
    ax.set_xscale("log")
    ax.set_xlabel("rho = frame time / coherence time")
    ax.set_ylabel("Mean PSNR (dB)")
    ax.set_title(f"M2 PSNR-rho curves at sigma_a={sigma_plot:g}")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=7.5)
    fig.tight_layout()
    curve_path = out_dir / "m2_psnr_rho_curves_sigma_0p30.png"
    fig.savefig(curve_path)
    plt.close(fig)
    written.append(curve_path.name)

    ok = fits[(fits["fit_status"] == "ok") & (fits["r2"] >= 0.9)].copy() if "r2" in fits else pd.DataFrame()
    if not ok.empty:
        fig, ax = plt.subplots(figsize=(7.2, 4.8), dpi=160)
        for _, fit_row in ok.iterrows():
            mask = (
                (boundaries["correction"] == fit_row["correction"])
                & (boundaries["challenger"] == fit_row["challenger"])
                & (boundaries["baseline"] == fit_row["baseline"])
                & (boundaries["boundary_status"] == "observed")
                & boundaries["rho_star_log_interp"].notna()
            )
            points = boundaries[mask].sort_values("sigma_a")
            if points.empty:
                continue
            label = f"{fit_row['correction']} / {fit_row['challenger']} (R2={float(fit_row['r2']):.3f})"
            ax.scatter(points["sigma_a"], points["rho_star_log_interp"], s=28, label=label)
            x = np.geomspace(float(points["sigma_a"].min()), float(points["sigma_a"].max()), 80)
            y = 10 ** (float(fit_row["intercept"]) + float(fit_row["sigma_a_exponent"]) * np.log10(x))
            ax.plot(x, y, linewidth=1.4)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("sigma_a")
        ax.set_ylabel("Interpolated rho*")
        ax.set_title("M2 flip-boundary fits with R2 >= 0.9")
        ax.grid(True, which="both", alpha=0.25)
        ax.legend(fontsize=6.5)
        fig.tight_layout()
        boundary_path = out_dir / "m2_boundary_fit_curves.png"
        fig.savefig(boundary_path)
        plt.close(fig)
        written.append(boundary_path.name)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit M2 phase-map rho coverage, flip boundaries, and winner stability.")
    parser.add_argument("--phase-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    root = project_root()
    phase_dir = args.phase_dir if args.phase_dir.is_absolute() else root / args.phase_dir
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = load_phase_summary(phase_dir)
    rhos = sorted(float(x) for x in summary["rho"].dropna().unique())
    sigmas = sorted(float(x) for x in summary["sigma_a"].dropna().unique())
    coverage = {
        "rho_min": min(rhos) if rhos else None,
        "rho_max": max(rhos) if rhos else None,
        "rho_count": len(rhos),
        "rho_values": rhos,
        "sigma_count": len(sigmas),
        "sigma_values": sigmas,
        "covers_prompt_rho_upper_10": bool(rhos and max(rhos) >= 10.0),
        "covers_prompt_rho_lower_1e-3": bool(rhos and min(rhos) <= 0.001),
    }
    boundaries, fits = build_boundary_tables(summary)
    winners, winner_summary = build_winner_tables(summary)

    pd.DataFrame([coverage]).to_csv(out_dir / "m2_rho_coverage.csv", index=False)
    boundaries.to_csv(out_dir / "m2_boundary_interpolated.csv", index=False)
    fits.to_csv(out_dir / "m2_boundary_fit.csv", index=False)
    winners.to_csv(out_dir / "m2_winner_cells.csv", index=False)
    winner_summary.to_csv(out_dir / "m2_winner_summary.csv", index=False)
    figures = write_figures(out_dir, summary, boundaries, fits)
    (out_dir / "m2_boundary_key_summary.json").write_text(
        json.dumps(
            {
                **coverage,
                "fit_status_counts": fits["fit_status"].value_counts().to_dict() if not fits.empty else {},
                "r2_ge_0_9_fits": int(((fits.get("fit_status") == "ok") & (fits.get("r2") >= 0.9)).sum()) if not fits.empty else 0,
                "figures": figures,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    write_report(out_dir, phase_dir, coverage, fits, winner_summary)
    print(json.dumps(coverage, indent=2))
    print(f"wrote {out_dir / 'm2_boundary_audit_report.md'}")


if __name__ == "__main__":
    main()
