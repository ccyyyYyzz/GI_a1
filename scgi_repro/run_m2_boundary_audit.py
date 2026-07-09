from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from src.config_utils import project_root


CHALLENGERS = ["random_uniform", "random_binary", "random_gaussian", "fourier_fourstep", "dct_paired", "srht_paired"]
DEFAULT_ABOVE_FLOOR_REL_MSE = 0.5


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


def build_boundary_tables(
    summary: pd.DataFrame,
    *,
    above_floor_rel_mse: float = DEFAULT_ABOVE_FLOOR_REL_MSE,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    cell_rows: list[dict[str, object]] = []
    blind = summary[summary["correction"] != "oracle"].copy()
    for (sigma_a, correction), group in blind.groupby(["sigma_a", "correction"]):
        pivot = group.pivot_table(index="rho", columns="basis", values="psnr_mean", aggfunc="mean").sort_index()
        rel_pivot = group.pivot_table(index="rho", columns="basis", values="rel_mse_mean", aggfunc="mean").sort_index()
        if "hadamard_paired" not in pivot.columns:
            continue
        for challenger in CHALLENGERS:
            if challenger not in pivot.columns:
                continue
            diff = pivot[challenger] - pivot["hadamard_paired"]
            challenger_rel = rel_pivot[challenger] if challenger in rel_pivot.columns else pd.Series(np.nan, index=diff.index)
            baseline_rel = rel_pivot["hadamard_paired"] if "hadamard_paired" in rel_pivot.columns else pd.Series(np.nan, index=diff.index)
            min_rel = pd.concat([challenger_rel, baseline_rel], axis=1).min(axis=1)
            above_floor = min_rel < float(above_floor_rel_mse)
            for rho in diff.index:
                cell_rows.append(
                    {
                        "sigma_a": float(sigma_a),
                        "correction": correction,
                        "challenger": challenger,
                        "baseline": "hadamard_paired",
                        "rho": float(rho),
                        "challenger_psnr": float(pivot.loc[rho, challenger]),
                        "baseline_psnr": float(pivot.loc[rho, "hadamard_paired"]),
                        "margin_db": float(diff.loc[rho]),
                        "challenger_rel_mse": float(challenger_rel.loc[rho]) if np.isfinite(challenger_rel.loc[rho]) else np.nan,
                        "baseline_rel_mse": float(baseline_rel.loc[rho]) if np.isfinite(baseline_rel.loc[rho]) else np.nan,
                        "min_rel_mse": float(min_rel.loc[rho]) if np.isfinite(min_rel.loc[rho]) else np.nan,
                        "above_floor": bool(above_floor.loc[rho]),
                        "above_floor_rel_mse": float(above_floor_rel_mse),
                    }
                )
            above_diff = diff[above_floor.fillna(False)]
            if above_diff.empty:
                rho_star, status = None, "sub_floor_only"
            else:
                rho_star, status = interpolate_boundary(above_diff.index.to_numpy(dtype=float), above_diff.to_numpy(dtype=float))
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
                    "max_margin_db_above_floor": float(above_diff.max()) if not above_diff.empty else np.nan,
                    "min_margin_db_above_floor": float(above_diff.min()) if not above_diff.empty else np.nan,
                    "points": int(diff.notna().sum()),
                    "above_floor_points": int(above_floor.sum()),
                    "sub_floor_points": int((~above_floor).sum()),
                    "rho_min": float(np.nanmin(diff.index.to_numpy(dtype=float))),
                    "rho_max": float(np.nanmax(diff.index.to_numpy(dtype=float))),
                    "above_floor_rho_min": float(np.nanmin(above_diff.index.to_numpy(dtype=float))) if not above_diff.empty else np.nan,
                    "above_floor_rho_max": float(np.nanmax(above_diff.index.to_numpy(dtype=float))) if not above_diff.empty else np.nan,
                    "above_floor_rel_mse": float(above_floor_rel_mse),
                }
            )
    boundaries = pd.DataFrame(rows)
    comparison_cells = pd.DataFrame(cell_rows)
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
                    "sub_floor_only_points": int((group["boundary_status"] == "sub_floor_only").sum()),
                    "above_floor_points": int(group["above_floor_points"].sum()),
                    "sub_floor_points": int(group["sub_floor_points"].sum()),
                    "law": "rho_star ~ sigma_a^a",
                    **fit_log_boundary(group),
                }
            )
    return boundaries, pd.DataFrame(fit_rows).sort_values(["correction", "challenger"]), comparison_cells


def build_winner_tables(
    summary: pd.DataFrame,
    *,
    above_floor_rel_mse: float = DEFAULT_ABOVE_FLOOR_REL_MSE,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    blind = summary[summary["correction"] != "oracle"].copy()
    equal_frame = blind[blind["total_physical_frames"] == blind["num_frames"]].copy()
    scope_tables = {
        "all_non_oracle": blind,
        "equal_frame_non_oracle": equal_frame,
    }
    winner_rows: list[pd.Series] = []
    for scope, table in scope_tables.items():
        for (_rho, _sigma), group in table.groupby(["rho", "sigma_a"], sort=True):
            above = group[group["rel_mse_mean"] < float(above_floor_rel_mse)].copy()
            if above.empty:
                best = group.sort_values("psnr_mean", ascending=False).iloc[0].copy()
                selected = best.copy()
                selected["basis"] = "sub_floor"
                selected["correction"] = "noise_floor"
                selected["above_floor"] = False
                selected["above_floor_candidates"] = 0
                selected["best_sub_floor_basis"] = best["basis"]
                selected["best_sub_floor_correction"] = best["correction"]
                selected["best_sub_floor_psnr_mean"] = best["psnr_mean"]
                selected["best_sub_floor_rel_mse_mean"] = best["rel_mse_mean"]
            else:
                selected = above.sort_values("psnr_mean", ascending=False).iloc[0].copy()
                selected["above_floor"] = True
                selected["above_floor_candidates"] = int(len(above))
                selected["best_sub_floor_basis"] = ""
                selected["best_sub_floor_correction"] = ""
                selected["best_sub_floor_psnr_mean"] = np.nan
                selected["best_sub_floor_rel_mse_mean"] = np.nan
            selected["scope"] = scope
            selected["candidate_count"] = int(len(group))
            selected["above_floor_rel_mse"] = float(above_floor_rel_mse)
            winner_rows.append(selected)
    winners = pd.DataFrame(winner_rows)
    rows: list[dict[str, object]] = []
    if not winners.empty:
        for (scope, basis, correction, above_floor), group in winners.groupby(["scope", "basis", "correction", "above_floor"]):
            rows.append(
                {
                    "scope": scope,
                    "basis": basis,
                    "correction": correction,
                    "above_floor": bool(above_floor),
                    "winning_cells": int(len(group)),
                    "rho_min": float(group["rho"].min()),
                    "rho_max": float(group["rho"].max()),
                    "sigma_min": float(group["sigma_a"].min()),
                    "sigma_max": float(group["sigma_a"].max()),
                    "psnr_mean_over_wins": float(group["psnr_mean"].mean()),
                    "rel_mse_mean_over_wins": float(group["rel_mse_mean"].mean()),
                    "above_floor_rel_mse": float(above_floor_rel_mse),
                }
            )
    winner_summary = pd.DataFrame(rows).sort_values(["scope", "winning_cells"], ascending=[True, False])
    return winners, winner_summary


def csv_text(frame: pd.DataFrame) -> str:
    return frame.to_csv(index=False, lineterminator="\n").strip()


def write_report(
    out_dir: Path,
    phase_dir: Path,
    coverage: dict[str, object],
    fits: pd.DataFrame,
    winner_summary: pd.DataFrame,
    comparison_cells: pd.DataFrame,
    *,
    above_floor_rel_mse: float,
) -> None:
    ok_fits = fits[(fits["fit_status"] == "ok") & (fits["r2"] >= 0.9)].copy() if "r2" in fits else pd.DataFrame()
    total_pair_cells = int(len(comparison_cells))
    above_pair_cells = int(comparison_cells["above_floor"].sum()) if not comparison_cells.empty else 0
    sub_pair_cells = total_pair_cells - above_pair_cells
    total_winner_cells = int(winner_summary["winning_cells"].sum()) if not winner_summary.empty else 0
    sub_winner_cells = (
        int(winner_summary.loc[~winner_summary["above_floor"].astype(bool), "winning_cells"].sum())
        if not winner_summary.empty and "above_floor" in winner_summary
        else 0
    )
    lines = [
        "# M2 Boundary Audit",
        "",
        f"Source phase directory: `{phase_dir.as_posix()}`",
        f"Above-floor reconstruction gate: `rel_mse_mean < {above_floor_rel_mse:g}` for at least one method in a comparison.",
        "",
        "## Rho Coverage",
        "",
    ]
    for key, value in coverage.items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Boundary Fits With R2 >= 0.9", ""])
    if ok_fits.empty:
        lines.append("No above-floor observed three-point boundary fit reaches R2 >= 0.9. Check censored and sub-floor rows before treating this as a failed trend.")
    else:
        columns = [
            "correction",
            "challenger",
            "observed_points",
            "left_censored_points",
            "not_reached_points",
            "sub_floor_only_points",
            "above_floor_points",
            "sigma_a_exponent",
            "r2",
        ]
        lines.append(csv_text(ok_fits[columns]))
    lines.extend(["", "## Winner Summary", ""])
    if not winner_summary.empty:
        lines.append(csv_text(winner_summary))
    lines.extend(
        [
            "",
            "## Above-Floor Accounting",
            "",
            f"- Pairwise challenger-vs-Hadamard cells: {above_pair_cells}/{total_pair_cells} above-floor; {sub_pair_cells} sub-floor.",
            f"- Winner-map cells across both scopes: {total_winner_cells - sub_winner_cells}/{total_winner_cells} above-floor; {sub_winner_cells} sub-floor.",
            "- Sub-floor winner cells are retained in CSVs as `sub_floor + noise_floor` placeholders and should be greyed out in headline maps.",
        ]
    )
    lines.extend(
        [
            "",
            "## Interpretation Notes",
            "",
            "- `observed` means the challenger crosses Hadamard within the sampled rho range using log-rho interpolation after applying the above-floor gate.",
            "- `left_censored` means the challenger is already >= Hadamard at the smallest sampled rho; this is stronger than an observed boundary for that grid.",
            "- `not_reached` means the challenger remains below Hadamard up to the largest sampled rho.",
            "- `sub_floor_only` means every sampled rho in that sigma/correction/challenger comparison is at reconstruction noise floor, so PSNR deltas are not reported as effects.",
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
    parser.add_argument("--above-floor-rel-mse", type=float, default=DEFAULT_ABOVE_FLOOR_REL_MSE)
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
    boundaries, fits, comparison_cells = build_boundary_tables(summary, above_floor_rel_mse=args.above_floor_rel_mse)
    winners, winner_summary = build_winner_tables(summary, above_floor_rel_mse=args.above_floor_rel_mse)

    pd.DataFrame([coverage]).to_csv(out_dir / "m2_rho_coverage.csv", index=False)
    boundaries.to_csv(out_dir / "m2_boundary_interpolated.csv", index=False)
    comparison_cells.to_csv(out_dir / "m2_boundary_comparison_cells.csv", index=False)
    comparison_cells.to_csv(out_dir / "flip_boundary.csv", index=False)
    fits.to_csv(out_dir / "m2_boundary_fit.csv", index=False)
    winners.to_csv(out_dir / "m2_winner_cells.csv", index=False)
    winner_summary.to_csv(out_dir / "m2_winner_summary.csv", index=False)
    figures = write_figures(out_dir, summary, boundaries, fits)
    (out_dir / "m2_boundary_key_summary.json").write_text(
        json.dumps(
            {
                **coverage,
                "above_floor_rel_mse": float(args.above_floor_rel_mse),
                "pairwise_comparison_cells": int(len(comparison_cells)),
                "above_floor_pairwise_comparison_cells": int(comparison_cells["above_floor"].sum()) if not comparison_cells.empty else 0,
                "sub_floor_pairwise_comparison_cells": int((~comparison_cells["above_floor"]).sum()) if not comparison_cells.empty else 0,
                "above_floor_winner_cells": int(winners["above_floor"].sum()) if not winners.empty else 0,
                "sub_floor_winner_cells": int((~winners["above_floor"]).sum()) if not winners.empty else 0,
                "fit_status_counts": fits["fit_status"].value_counts().to_dict() if not fits.empty else {},
                "r2_ge_0_9_fits": int(((fits.get("fit_status") == "ok") & (fits.get("r2") >= 0.9)).sum()) if not fits.empty else 0,
                "figures": figures,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    write_report(
        out_dir,
        phase_dir,
        coverage,
        fits,
        winner_summary,
        comparison_cells,
        above_floor_rel_mse=args.above_floor_rel_mse,
    )
    print(json.dumps(coverage, indent=2))
    print(f"wrote {out_dir / 'm2_boundary_audit_report.md'}")


if __name__ == "__main__":
    main()
