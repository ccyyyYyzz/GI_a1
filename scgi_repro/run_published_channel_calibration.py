from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

from src.config_utils import project_root


@dataclass(frozen=True)
class TraceSpec:
    trace_id: str
    paper: str
    figure: str
    panel: str
    sample: str
    trace_kind: str
    source_image: str
    data_box: tuple[int, int, int, int]
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    x_unit: str
    y_unit: str
    threshold: int = 115
    y_quantile: float = 0.5


def project_rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(project_root()))
    except Exception:
        return str(path)


def apl_specs() -> list[TraceSpec]:
    paper = "Peng and Chen, Applied Physics Letters 2024 SCGI"
    return [
        TraceSpec("apl_fig5a_collected_usaf", paper, "Fig. 5", "a", "USAF 1951", "collected", "results/paper_figures/apl_pages/apl-5.png", (845, 1189, 1082, 1358), 0.0, 4.0, 0.0, 1.0, "1e4 measurements", "normalized intensity"),
        TraceSpec("apl_fig5b_corrected_usaf", paper, "Fig. 5", "b", "USAF 1951", "corrected", "results/paper_figures/apl_pages/apl-5.png", (1153, 1189, 1390, 1358), 0.0, 4.0, 0.0, 1.0, "1e4 measurements", "normalized intensity", threshold=105),
        TraceSpec("apl_fig7a_collected_0", paper, "Fig. 7", "a", "0", "collected", "results/paper_figures/apl_pages/apl-6.png", (843, 961, 1081, 1131), 0.0, 4.0, 0.0, 1.0, "1e4 measurements", "normalized intensity"),
        TraceSpec("apl_fig7b_corrected_0", paper, "Fig. 7", "b", "0", "corrected", "results/paper_figures/apl_pages/apl-6.png", (1153, 961, 1390, 1131), 0.0, 4.0, 0.0, 1.0, "1e4 measurements", "normalized intensity", threshold=105),
        TraceSpec("apl_fig7c_collected_nd", paper, "Fig. 7", "c", "nd", "collected", "results/paper_figures/apl_pages/apl-6.png", (843, 1206, 1081, 1376), 0.0, 4.0, 0.0, 1.0, "1e4 measurements", "normalized intensity"),
        TraceSpec("apl_fig7d_corrected_nd", paper, "Fig. 7", "d", "nd", "corrected", "results/paper_figures/apl_pages/apl-6.png", (1153, 1206, 1390, 1376), 0.0, 4.0, 0.0, 1.0, "1e4 measurements", "normalized intensity", threshold=105),
        TraceSpec("apl_fig7e_collected_eq", paper, "Fig. 7", "e", "Eq", "collected", "results/paper_figures/apl_pages/apl-6.png", (843, 1451, 1081, 1621), 0.0, 4.0, 0.0, 1.0, "1e4 measurements", "normalized intensity"),
        TraceSpec("apl_fig7f_corrected_eq", paper, "Fig. 7", "f", "Eq", "corrected", "results/paper_figures/apl_pages/apl-6.png", (1153, 1451, 1390, 1621), 0.0, 4.0, 0.0, 1.0, "1e4 measurements", "normalized intensity", threshold=105),
    ]


def fill_missing(values: np.ndarray) -> np.ndarray:
    x = np.arange(values.size)
    ok = np.isfinite(values)
    if ok.sum() == 0:
        return values
    if ok.sum() == 1:
        return np.full_like(values, values[ok][0])
    return np.interp(x, x[ok], values[ok])


def rolling_median(values: np.ndarray, window: int = 5) -> np.ndarray:
    if window <= 1:
        return values
    half = window // 2
    padded = np.pad(values, (half, half), mode="edge")
    return np.array([np.median(padded[i : i + window]) for i in range(values.size)])


def digitize_dark_trace(root: Path, spec: TraceSpec) -> pd.DataFrame:
    source_path = root / spec.source_image
    if not source_path.exists():
        raise FileNotFoundError(
            f"Missing local rendered source page: {source_path}. "
            "Render the authorized PDF pages locally before running this digitization; "
            "the page PNGs are intentionally not committed to the public relay."
        )
    image = Image.open(source_path).convert("L")
    x0, y0, x1, y1 = spec.data_box
    arr = np.asarray(image.crop((x0, y0, x1, y1)))
    # Avoid the axes and tick marks at the plot frame border.
    work = arr[3:-3, 3:-3]
    h, w = work.shape
    y_pixels = np.full(w, np.nan, dtype=float)
    y_q10 = np.full(w, np.nan, dtype=float)
    y_q90 = np.full(w, np.nan, dtype=float)
    pixel_counts = np.zeros(w, dtype=int)
    for col in range(w):
        ys = np.where(work[:, col] < spec.threshold)[0]
        if len(ys) >= 1:
            y_pixels[col] = float(np.quantile(ys, spec.y_quantile))
            y_q10[col] = float(np.quantile(ys, 0.1))
            y_q90[col] = float(np.quantile(ys, 0.9))
            pixel_counts[col] = int(len(ys))
    y_pixels = rolling_median(fill_missing(y_pixels), window=5)
    y_q10 = rolling_median(fill_missing(y_q10), window=5)
    y_q90 = rolling_median(fill_missing(y_q90), window=5)
    x_scaled = spec.x_min + (np.arange(w) + 0.5) / w * (spec.x_max - spec.x_min)
    y_value = spec.y_max - (y_pixels + 0.5) / h * (spec.y_max - spec.y_min)
    y_high = spec.y_max - (y_q10 + 0.5) / h * (spec.y_max - spec.y_min)
    y_low = spec.y_max - (y_q90 + 0.5) / h * (spec.y_max - spec.y_min)
    out = pd.DataFrame(
        {
            "trace_id": spec.trace_id,
            "paper": spec.paper,
            "figure": spec.figure,
            "panel": spec.panel,
            "sample": spec.sample,
            "trace_kind": spec.trace_kind,
            "x_axis": x_scaled,
            "x_measurements": x_scaled * 10000.0,
            "y_digitized": y_value.clip(spec.y_min, spec.y_max),
            "y_band_low": y_low.clip(spec.y_min, spec.y_max),
            "y_band_high": y_high.clip(spec.y_min, spec.y_max),
            "pixel_count": pixel_counts,
            "source_image": spec.source_image,
            "data_box": str(spec.data_box),
            "extraction": "fixed_axis_box_dark_pixel_median",
            "x_unit": spec.x_unit,
            "y_unit": spec.y_unit,
        }
    )
    return out


def ar1_corr(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size < 3:
        return float("nan")
    left = values[:-1] - values[:-1].mean()
    right = values[1:] - values[1:].mean()
    denom = float(np.sqrt(np.sum(left**2) * np.sum(right**2)))
    if denom <= 0:
        return float("nan")
    return float(np.sum(left * right) / denom)


def fit_collected_trace(df: pd.DataFrame) -> dict[str, object]:
    y = df["y_digitized"].to_numpy(dtype=float)
    x_axis = df["x_axis"].to_numpy(dtype=float)
    x_measurements = df["x_measurements"].to_numpy(dtype=float)
    mask = np.isfinite(y) & (x_axis > 0.08) & (y > 0.02) & (y < 0.98)
    if mask.sum() < 8:
        mask = np.isfinite(y) & (x_axis > 0.08) & (y > 0.005)
    log_y = np.log(np.clip(y[mask], 1e-6, None))
    slope_axis, intercept = np.polyfit(x_axis[mask], log_y, 1)
    pred = slope_axis * x_axis[mask] + intercept
    resid = log_y - pred
    ss_res = float(np.sum(resid**2))
    ss_tot = float(np.sum((log_y - log_y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    slope_measurement = slope_axis / 10000.0
    lambda_per_measurement = float(math.exp(slope_measurement))
    half_life_measurements = float(math.log(0.5) / slope_measurement) if slope_measurement < 0 else float("nan")
    mean_step = float(np.mean(np.diff(x_measurements))) if len(x_measurements) > 1 else float("nan")
    ar1_step = ar1_corr(resid)
    rho_per_measurement = float(np.sign(ar1_step) * abs(ar1_step) ** (1.0 / mean_step)) if np.isfinite(ar1_step) and mean_step > 0 and ar1_step != 0 else float("nan")
    return {
        "trace_id": df["trace_id"].iloc[0],
        "paper": df["paper"].iloc[0],
        "figure": df["figure"].iloc[0],
        "panel": df["panel"].iloc[0],
        "sample": df["sample"].iloc[0],
        "trace_kind": "collected",
        "points": int(len(df)),
        "fit_points": int(mask.sum()),
        "log_linear_slope_per_1e4_measurements": float(slope_axis),
        "lambda_per_measurement": lambda_per_measurement,
        "decay_constant_per_1e4_measurements": float(-slope_axis),
        "half_life_measurements": half_life_measurements,
        "log_residual_std": float(np.std(resid, ddof=1)) if len(resid) > 1 else float("nan"),
        "log_residual_ar1_digitized_step": ar1_step,
        "rho_per_measurement_proxy": rho_per_measurement,
        "r2": r2,
        "quality_note": "approximate figure-level digitization; use as calibration prior, not raw detector data",
    }


def fit_corrected_trace(df: pd.DataFrame) -> dict[str, object]:
    y = df["y_digitized"].to_numpy(dtype=float)
    y_low = df["y_band_low"].to_numpy(dtype=float)
    y_high = df["y_band_high"].to_numpy(dtype=float)
    x_axis = df["x_axis"].to_numpy(dtype=float)
    slope, intercept = np.polyfit(x_axis, y, 1)
    pred = slope * x_axis + intercept
    resid = y - pred
    return {
        "trace_id": df["trace_id"].iloc[0],
        "paper": df["paper"].iloc[0],
        "figure": df["figure"].iloc[0],
        "panel": df["panel"].iloc[0],
        "sample": df["sample"].iloc[0],
        "trace_kind": "corrected",
        "points": int(len(df)),
        "fit_points": int(len(df)),
        "corrected_mean": float(np.mean(y)),
        "corrected_std": float(np.std(y, ddof=1)),
        "corrected_cv": float(np.std(y, ddof=1) / np.mean(y)) if np.mean(y) != 0 else float("nan"),
        "corrected_visual_band_mean": float(np.mean(y_high - y_low)),
        "corrected_visual_sigma_proxy": float(np.mean(y_high - y_low) / 2.563),
        "linear_slope_per_1e4_measurements": float(slope),
        "linear_residual_std": float(np.std(resid, ddof=1)),
        "linear_residual_ar1_digitized_step": ar1_corr(resid),
        "quality_note": "approximate figure-level digitization; black band median suppresses visual spikes",
    }


def parse_condition_value(condition: str, key: str) -> float | None:
    match = re.search(rf"{re.escape(key)}=([0-9.]+)", condition)
    return float(match.group(1)) if match else None


def interpolate_threshold(x: np.ndarray, y: np.ndarray, threshold: float) -> float | None:
    order = np.argsort(x)
    x = x[order]
    y = y[order]
    for i in range(len(x) - 1):
        y0, y1 = y[i], y[i + 1]
        if (y0 - threshold) == 0:
            return float(x[i])
        if (y0 - threshold) * (y1 - threshold) <= 0 and y0 != y1:
            frac = (threshold - y0) / (y1 - y0)
            return float(x[i] + frac * (x[i + 1] - x[i]))
    return None


def build_oe_channel_fits(root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    targets_path = root / "results" / "published_calibration" / "published_targets.csv"
    if not targets_path.exists():
        return pd.DataFrame(), pd.DataFrame()
    targets = pd.read_csv(targets_path)
    oe = targets[(targets["paper"].str.contains("Optics Express")) & (targets["metric"].isin(["PSNR", "SSIM"]))].copy()
    rows: list[dict[str, object]] = []
    for _, row in oe.iterrows():
        condition = str(row["condition"])
        beta = parse_condition_value(condition, "attenuation_beta_x1e2")
        distance = parse_condition_value(condition, "distance")
        rows.append(
            {
                "series_id": f"{row['figure']}_{row['panel']}_{row['method']}_{row['metric']}",
                "paper": row["paper"],
                "figure": row["figure"],
                "panel": row["panel"],
                "method": row["method"],
                "metric": row["metric"],
                "x_variable": "attenuation_beta_x1e2" if beta is not None else ("distance_mm" if distance is not None else "categorical"),
                "x_value": beta if beta is not None else distance,
                "value": float(row["value"]),
                "unit": row["unit"],
                "approximate": bool(row.get("approximate", False)),
                "source_path": row["source_path"],
            }
        )
    curves = pd.DataFrame(rows)
    fits: list[dict[str, object]] = []
    for (figure, method, metric, x_variable), group in curves.dropna(subset=["x_value"]).groupby(
        ["figure", "method", "metric", "x_variable"]
    ):
        if len(group) < 3:
            continue
        x = group["x_value"].to_numpy(dtype=float)
        y = group["value"].to_numpy(dtype=float)
        slope, intercept = np.polyfit(x, y, 1)
        pred = slope * x + intercept
        ss_res = float(np.sum((y - pred) ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        threshold = 30.0 if metric == "PSNR" else (0.99 if x_variable == "distance_mm" else 0.97)
        crossing = interpolate_threshold(x, y, threshold)
        fits.append(
            {
                "figure": figure,
                "method": method,
                "metric": metric,
                "x_variable": x_variable,
                "points": int(len(group)),
                "x_min": float(np.min(x)),
                "x_max": float(np.max(x)),
                "value_min": float(np.min(y)),
                "value_max": float(np.max(y)),
                "linear_slope": float(slope),
                "linear_intercept": float(intercept),
                "linear_r2": 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan"),
                "threshold": threshold,
                "threshold_crossing_x": crossing,
                "quality_note": "linear fit is a compact calibration summary; use exact/digitized curve rows for thresholds",
            }
        )
    return curves, pd.DataFrame(fits)


def draw_apl_overlay(root: Path, specs: list[TraceSpec], traces: pd.DataFrame, out_dir: Path) -> None:
    by_image: dict[str, list[TraceSpec]] = {}
    for spec in specs:
        by_image.setdefault(spec.source_image, []).append(spec)
    for source, source_specs in by_image.items():
        im = Image.open(root / source).convert("RGB")
        draw = ImageDraw.Draw(im)
        for spec in source_specs:
            x0, y0, x1, y1 = spec.data_box
            draw.rectangle((x0, y0, x1, y1), outline=(255, 0, 0), width=3)
            draw.text((x0 + 4, y0 + 4), spec.trace_id, fill=(255, 0, 0))
            subset = traces[traces["trace_id"] == spec.trace_id]
            if subset.empty:
                continue
            w = x1 - x0 - 6
            h = y1 - y0 - 6
            points = []
            for _, row in subset.iloc[:: max(1, len(subset) // 120)].iterrows():
                px = x0 + 3 + (float(row["x_axis"]) - spec.x_min) / (spec.x_max - spec.x_min) * w
                py = y0 + 3 + (spec.y_max - float(row["y_digitized"])) / (spec.y_max - spec.y_min) * h
                points.append((px, py))
            if len(points) > 1:
                draw.line(points, fill=(0, 180, 255), width=2)
        im.save(out_dir / f"{Path(source).stem}_digitization_overlay.png")


def write_report(out_dir: Path, apl_fit: pd.DataFrame, oe_fit: pd.DataFrame, summary: dict[str, object]) -> None:
    lines = [
        "# Published Channel Calibration",
        "",
        "Generated by `run_published_channel_calibration.py` from rendered PDF pages and published target tables.",
        "",
        "## Key Summary",
        "",
    ]
    for key, value in summary.items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## APL Dynamic Scaling", ""])
    if not apl_fit.empty:
        cols = [
            "trace_id",
            "sample",
            "trace_kind",
            "lambda_per_measurement",
            "decay_constant_per_1e4_measurements",
            "corrected_mean",
            "corrected_std",
            "corrected_visual_sigma_proxy",
            "r2",
        ]
        available = [col for col in cols if col in apl_fit.columns]
        lines.append(apl_fit[available].to_csv(index=False))
    lines.extend(["", "## OE Channel Anchors", ""])
    if not oe_fit.empty:
        lines.append(oe_fit.to_csv(index=False))
    lines.extend(
        [
            "",
            "## Caveats",
            "",
            "- APL intensity traces are figure-level digitizations from rendered pages, not raw detector logs.",
            "- OE Fig. 6 and Fig. 8 points combine exact paper text anchors with approximate curve readings from `published_targets.csv`.",
            "- Rendered source pages and overlay QA PNGs are local-only artifacts and are intentionally not published in the GitHub relay.",
            "- Use these outputs as published-channel priors and sanity checks for normalized simulator parameters.",
        ]
    )
    (out_dir / "published_channel_calibration_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Digitize APL/OE published curves and fit channel calibration anchors.")
    parser.add_argument("--output-dir", type=Path, default=project_root() / "results" / "published_channel_calibration")
    args = parser.parse_args()

    root = project_root()
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    specs = apl_specs()
    trace_frames = [digitize_dark_trace(root, spec) for spec in specs]
    apl_traces = pd.concat(trace_frames, ignore_index=True)
    apl_traces.to_csv(out_dir / "apl_intensity_traces_digitized.csv", index=False)

    fit_rows = []
    for trace_id, group in apl_traces.groupby("trace_id"):
        kind = group["trace_kind"].iloc[0]
        fit_rows.append(fit_collected_trace(group) if kind == "collected" else fit_corrected_trace(group))
    apl_fit = pd.DataFrame(fit_rows).sort_values(["figure", "panel"])
    apl_fit.to_csv(out_dir / "apl_channel_fit_summary.csv", index=False)

    oe_curves, oe_fit = build_oe_channel_fits(root)
    oe_curves.to_csv(out_dir / "oe_curve_points.csv", index=False)
    oe_fit.to_csv(out_dir / "oe_channel_fit_summary.csv", index=False)

    collected = apl_fit[apl_fit["trace_kind"] == "collected"]
    corrected = apl_fit[apl_fit["trace_kind"] == "corrected"]
    summary = {
        "apl_collected_traces": int(len(collected)),
        "apl_corrected_traces": int(len(corrected)),
        "apl_lambda_per_measurement_min": float(collected["lambda_per_measurement"].min()),
        "apl_lambda_per_measurement_max": float(collected["lambda_per_measurement"].max()),
        "apl_corrected_std_mean": float(corrected["corrected_std"].mean()),
        "apl_corrected_visual_sigma_proxy_mean": float(corrected["corrected_visual_sigma_proxy"].mean()),
        "oe_curve_points": int(len(oe_curves)),
        "oe_fit_rows": int(len(oe_fit)),
        "oe_fig6_fixed_ref_psnr30_beta_x1e2": None,
        "source_images": sorted({project_rel(root / spec.source_image) for spec in specs}),
    }
    match = oe_fit[
        (oe_fit["figure"] == "Fig. 6")
        & (oe_fit["method"] == "fixed_reference")
        & (oe_fit["metric"] == "PSNR")
        & (oe_fit["x_variable"] == "attenuation_beta_x1e2")
    ]
    if not match.empty:
        value = match["threshold_crossing_x"].iloc[0]
        summary["oe_fig6_fixed_ref_psnr30_beta_x1e2"] = None if pd.isna(value) else float(value)
    (out_dir / "published_channel_key_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    draw_apl_overlay(root, specs, apl_traces, out_dir)
    write_report(out_dir, apl_fit, oe_fit, summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
