from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from run_m4_agc_targeted import markdown_table
from src.config_utils import project_root
from src.metrics import cnr, psnr, ssim
from src.plotting import save_image_grid, save_metrics_table


def otsu_threshold(values: np.ndarray, bins: int = 256) -> float:
    counts, edges = np.histogram(values.reshape(-1), bins=bins)
    centers = (edges[:-1] + edges[1:]) / 2.0
    total = float(counts.sum())
    if total <= 0:
        return float(np.nan)
    sum_total = float((counts * centers).sum())
    weight_bg = 0.0
    sum_bg = 0.0
    best_score = -1.0
    best_threshold = float(centers[0])
    for count, center in zip(counts, centers):
        weight_bg += float(count)
        if weight_bg <= 0:
            continue
        weight_fg = total - weight_bg
        if weight_fg <= 0:
            break
        sum_bg += float(count) * float(center)
        mean_bg = sum_bg / weight_bg
        mean_fg = (sum_total - sum_bg) / weight_fg
        score = weight_bg * weight_fg * (mean_bg - mean_fg) ** 2
        if score > best_score:
            best_score = score
            best_threshold = float(center)
    return best_threshold


def minmax(values: np.ndarray) -> np.ndarray:
    lo = float(np.nanmin(values))
    hi = float(np.nanmax(values))
    return (values - lo) / max(hi - lo, 1e-12)


def torch_metrics(image: np.ndarray, target: np.ndarray) -> dict[str, float]:
    recon_t = torch.tensor(image, dtype=torch.float32)
    target_t = torch.tensor(target, dtype=torch.float32)
    return {
        "cnr": cnr(recon_t, target_t),
        "psnr": psnr(recon_t, target_t),
        "ssim": ssim(recon_t, target_t),
    }


def mask_metrics(image: np.ndarray, target: np.ndarray, threshold: float = 0.5) -> dict[str, float]:
    pred = image >= threshold
    truth = target > 0.5
    inter = int(np.logical_and(pred, truth).sum())
    union = int(np.logical_or(pred, truth).sum())
    return {
        "foreground_fraction": float(pred.mean()),
        "target_foreground_fraction": float(truth.mean()),
        "iou": float(inter / union) if union else float("nan"),
        "false_positive_pixels": int(np.logical_and(pred, ~truth).sum()),
        "false_negative_pixels": int(np.logical_and(~pred, truth).sum()),
    }


def add_row(
    rows: list[dict[str, object]],
    *,
    method: str,
    image: np.ndarray,
    target: np.ndarray,
    threshold: float | None = None,
    target_free: bool,
    note: str,
) -> None:
    metric_row = torch_metrics(image, target)
    row: dict[str, object] = {
        "method": method,
        "threshold": "" if threshold is None else float(threshold),
        "target_free_threshold": bool(target_free),
        **metric_row,
        "min": float(np.nanmin(image)),
        "max": float(np.nanmax(image)),
        "mean": float(np.nanmean(image)),
        "note": note,
    }
    if threshold is not None:
        row.update(mask_metrics(image, target))
    else:
        row.update(
            {
                "foreground_fraction": "",
                "target_foreground_fraction": float((target > 0.5).mean()),
                "iou": "",
                "false_positive_pixels": "",
                "false_negative_pixels": "",
            }
        )
    rows.append(row)


def build_audit(arrays: dict[str, np.ndarray]) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    target = arrays["target"].astype(np.float32)
    raw = arrays["best_final"].astype(np.float32)
    scaled = minmax(raw).astype(np.float32)
    truth_fraction = float((target > 0.5).mean())
    raw_otsu = otsu_threshold(raw)
    scaled_otsu = otsu_threshold(scaled)
    target_fraction_threshold = float(np.quantile(raw, 1.0 - truth_fraction))

    images: dict[str, np.ndarray] = {
        "target": target,
        "raw_best_final": raw,
        "raw_otsu_binary": (raw >= raw_otsu).astype(np.float32),
        "minmax_otsu_binary": (scaled >= scaled_otsu).astype(np.float32),
        "raw_mean_binary": (raw >= float(raw.mean())).astype(np.float32),
        "raw_mean_plus_std_binary": (raw >= float(raw.mean() + raw.std())).astype(np.float32),
        "target_fraction_upper_bound": (raw >= target_fraction_threshold).astype(np.float32),
    }

    rows: list[dict[str, object]] = []
    add_row(rows, method="raw_best_final", image=raw, target=target, target_free=True, note="Continuous URED output.")
    add_row(rows, method="minmax_best_final", image=scaled, target=target, target_free=True, note="Linear display scaling only.")
    add_row(
        rows,
        method="raw_otsu_binary",
        image=images["raw_otsu_binary"],
        target=target,
        threshold=raw_otsu,
        target_free=True,
        note="Otsu threshold from reconstruction histogram only.",
    )
    add_row(
        rows,
        method="minmax_otsu_binary",
        image=images["minmax_otsu_binary"],
        target=target,
        threshold=scaled_otsu,
        target_free=True,
        note="Otsu threshold after min-max scaling; same mask as raw Otsu.",
    )
    add_row(
        rows,
        method="raw_mean_binary",
        image=images["raw_mean_binary"],
        target=target,
        threshold=float(raw.mean()),
        target_free=True,
        note="Simple target-free mean threshold.",
    )
    add_row(
        rows,
        method="raw_mean_plus_std_binary",
        image=images["raw_mean_plus_std_binary"],
        target=target,
        threshold=float(raw.mean() + raw.std()),
        target_free=True,
        note="Simple target-free mean plus one standard deviation threshold.",
    )
    add_row(
        rows,
        method="target_fraction_upper_bound",
        image=images["target_fraction_upper_bound"],
        target=target,
        threshold=target_fraction_threshold,
        target_free=False,
        note="Upper bound using the true target foreground fraction; not deployable.",
    )
    return pd.DataFrame(rows), images


def write_report(out_dir: Path, metrics: pd.DataFrame, payload: dict[str, object]) -> None:
    compact = metrics[
        [
            "method",
            "target_free_threshold",
            "cnr",
            "psnr",
            "ssim",
            "iou",
            "foreground_fraction",
            "threshold",
            "note",
        ]
    ].copy()
    for column in ["cnr", "psnr", "ssim", "iou", "foreground_fraction", "threshold"]:
        compact[column] = compact[column].map(lambda value: "" if value == "" else f"{float(value):.3f}")
    lines = [
        "# Stage 4 Stripe Postprocess Audit",
        "",
        f"APL URED minimum CNR gate: `{payload['apl_min_cnr']:.2f}`.",
        "",
        markdown_table(compact),
        "",
        "## Interpretation",
        "",
        (
            "The continuous best stripe URED output remains below the APL gate, "
            f"with CNR `{payload['raw_cnr']:.3f}`."
        ),
        (
            "A target-free Otsu threshold on the same reconstruction reaches "
            f"CNR `{payload['otsu_cnr']:.3f}` and IoU `{payload['otsu_iou']:.3f}`, "
            "which means the shape is largely present but the continuous CNR score is penalized by within-region gray variation."
        ),
        (
            "This should not be counted as a strict paper reproduction unless a thresholded URED output is accepted as the reporting protocol; "
            "it is a strong diagnostic that the remaining Stage 4 gap is output calibration/post-processing rather than target localization."
        ),
        "",
    ]
    (out_dir / "stage4_postprocess_audit_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit target-free post-processing of the best Stage 4 stripe URED output.")
    parser.add_argument("--arrays", type=Path, default=Path("results/stage4_image_audit_r1/stage4_image_audit_arrays.npz"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/stage4_postprocess_audit_r1"))
    parser.add_argument("--apl-min-cnr", type=float, default=10.43)
    args = parser.parse_args()

    root = project_root()
    arrays_path = args.arrays if args.arrays.is_absolute() else root / args.arrays
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    arrays = dict(np.load(arrays_path))
    metrics, images = build_audit(arrays)
    metrics.to_csv(out_dir / "stage4_postprocess_audit_metrics.csv", index=False)
    save_metrics_table(
        out_dir / "stage4_postprocess_audit_metrics.png",
        metrics[["method", "target_free_threshold", "cnr", "psnr", "ssim", "iou", "foreground_fraction"]],
        title="Stage 4 stripe postprocess audit",
        max_rows=12,
    )
    save_image_grid(
        out_dir / "stage4_postprocess_audit_grid.png",
        [images[key] for key in images],
        labels=[key for key in images],
        columns=4,
    )
    raw_row = metrics[metrics["method"] == "raw_best_final"].iloc[0]
    otsu_row = metrics[metrics["method"] == "raw_otsu_binary"].iloc[0]
    payload = {
        "arrays": str(arrays_path),
        "apl_min_cnr": float(args.apl_min_cnr),
        "raw_cnr": float(raw_row["cnr"]),
        "otsu_cnr": float(otsu_row["cnr"]),
        "otsu_iou": float(otsu_row["iou"]),
        "otsu_hits_apl_min": bool(float(otsu_row["cnr"]) >= float(args.apl_min_cnr)),
        "target_free_methods_over_apl_min": metrics[
            (metrics["target_free_threshold"].astype(bool)) & (metrics["cnr"].astype(float) >= float(args.apl_min_cnr))
        ]["method"].tolist(),
    }
    (out_dir / "stage4_postprocess_audit_summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_report(out_dir, metrics, payload)
    print(f"wrote {out_dir}")


if __name__ == "__main__":
    main()
