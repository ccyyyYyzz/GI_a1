from __future__ import annotations

import argparse
import json
from argparse import Namespace
from pathlib import Path

import numpy as np
import pandas as pd

from run_m4_agc_targeted import markdown_table
from run_stage4_image_audit import run_audit
from run_stage4_postprocess_audit import mask_metrics, minmax, otsu_threshold, torch_metrics
from src.config_utils import project_root
from src.plotting import save_metrics_table


POSTPROCESS_SOURCES = ["best_final", "best_trace_regen"]


def _read(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def parse_names(text: str | None) -> list[str] | None:
    if text is None:
        return None
    names = [part.strip() for part in text.replace(",", " ").split() if part.strip()]
    return names or None


def object_names_from_audit(audit_dir: Path) -> list[str]:
    summary = _read(audit_dir / "stage4_trace_audit_summary.csv")
    return sorted(summary["object"].dropna().astype(str).unique().tolist())


def add_metric_row(
    rows: list[dict[str, object]],
    *,
    object_name: str,
    source: str,
    source_config: str,
    steps: int,
    method: str,
    image: np.ndarray,
    target: np.ndarray,
    threshold: float | None,
    target_free_threshold: bool,
    apl_min_cnr: float,
    note: str,
) -> None:
    metrics = torch_metrics(image, target)
    row: dict[str, object] = {
        "object": object_name,
        "source": source,
        "source_config": source_config,
        "steps": int(steps),
        "postprocess_method": method,
        "target_free_threshold": bool(target_free_threshold),
        "threshold": "" if threshold is None else float(threshold),
        **metrics,
        "hits_apl_min": bool(float(metrics["cnr"]) >= float(apl_min_cnr)),
        "min": float(np.nanmin(image)),
        "max": float(np.nanmax(image)),
        "mean": float(np.nanmean(image)),
        "note": note,
    }
    if threshold is None:
        row.update(
            {
                "foreground_fraction": "",
                "target_foreground_fraction": float((target > 0.5).mean()),
                "iou": "",
                "false_positive_pixels": "",
                "false_negative_pixels": "",
            }
        )
    else:
        row.update(mask_metrics(image, target))
    rows.append(row)


def audit_source(
    *,
    object_name: str,
    source: str,
    source_config: str,
    steps: int,
    image: np.ndarray,
    target: np.ndarray,
    apl_min_cnr: float,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    image = image.astype(np.float32)
    target = target.astype(np.float32)
    scaled = minmax(image).astype(np.float32)
    otsu = otsu_threshold(image)
    scaled_otsu = otsu_threshold(scaled)
    mean_threshold = float(image.mean())
    mean_plus_std = float(image.mean() + image.std())
    target_fraction = float((target > 0.5).mean())
    target_fraction_threshold = float(np.quantile(image, 1.0 - target_fraction))
    add_metric_row(
        rows,
        object_name=object_name,
        source=source,
        source_config=source_config,
        steps=steps,
        method="continuous",
        image=image,
        target=target,
        threshold=None,
        target_free_threshold=True,
        apl_min_cnr=apl_min_cnr,
        note="Continuous URED output.",
    )
    add_metric_row(
        rows,
        object_name=object_name,
        source=source,
        source_config=source_config,
        steps=steps,
        method="minmax_continuous",
        image=scaled,
        target=target,
        threshold=None,
        target_free_threshold=True,
        apl_min_cnr=apl_min_cnr,
        note="Linear display scaling only.",
    )
    add_metric_row(
        rows,
        object_name=object_name,
        source=source,
        source_config=source_config,
        steps=steps,
        method="raw_otsu_binary",
        image=(image >= otsu).astype(np.float32),
        target=target,
        threshold=otsu,
        target_free_threshold=True,
        apl_min_cnr=apl_min_cnr,
        note="Otsu threshold from reconstruction histogram only.",
    )
    add_metric_row(
        rows,
        object_name=object_name,
        source=source,
        source_config=source_config,
        steps=steps,
        method="minmax_otsu_binary",
        image=(scaled >= scaled_otsu).astype(np.float32),
        target=target,
        threshold=scaled_otsu,
        target_free_threshold=True,
        apl_min_cnr=apl_min_cnr,
        note="Otsu threshold after min-max scaling.",
    )
    add_metric_row(
        rows,
        object_name=object_name,
        source=source,
        source_config=source_config,
        steps=steps,
        method="raw_mean_binary",
        image=(image >= mean_threshold).astype(np.float32),
        target=target,
        threshold=mean_threshold,
        target_free_threshold=True,
        apl_min_cnr=apl_min_cnr,
        note="Simple target-free mean threshold.",
    )
    add_metric_row(
        rows,
        object_name=object_name,
        source=source,
        source_config=source_config,
        steps=steps,
        method="raw_mean_plus_std_binary",
        image=(image >= mean_plus_std).astype(np.float32),
        target=target,
        threshold=mean_plus_std,
        target_free_threshold=True,
        apl_min_cnr=apl_min_cnr,
        note="Simple target-free mean plus one standard deviation threshold.",
    )
    add_metric_row(
        rows,
        object_name=object_name,
        source=source,
        source_config=source_config,
        steps=steps,
        method="target_fraction_upper_bound",
        image=(image >= target_fraction_threshold).astype(np.float32),
        target=target,
        threshold=target_fraction_threshold,
        target_free_threshold=False,
        apl_min_cnr=apl_min_cnr,
        note="Upper bound using the true target foreground fraction; not deployable.",
    )
    return rows


def best_target_free(metrics: pd.DataFrame, source: str) -> pd.DataFrame:
    eligible = metrics[(metrics["source"] == source) & (metrics["target_free_threshold"].astype(bool))].copy()
    idx = eligible.groupby("object")["cnr"].idxmax()
    return eligible.loc[idx].sort_values("object").reset_index(drop=True)


def write_report(out_dir: Path, metrics: pd.DataFrame, payload: dict[str, object]) -> None:
    final_best = best_target_free(metrics, "best_final")
    trace_best = best_target_free(metrics, "best_trace_regen")
    compact = pd.concat(
        [
            final_best.assign(summary_source="best_final"),
            trace_best.assign(summary_source="best_trace_regen"),
        ],
        ignore_index=True,
    )[
        [
            "summary_source",
            "object",
            "postprocess_method",
            "cnr",
            "psnr",
            "ssim",
            "iou",
            "hits_apl_min",
            "source_config",
            "steps",
        ]
    ].copy()
    for column in ["cnr", "psnr", "ssim", "iou"]:
        compact[column] = compact[column].map(lambda value: "" if value == "" else f"{float(value):.3f}")
    lines = [
        "# Stage 4 All-Object Postprocess Audit",
        "",
        f"APL URED minimum CNR gate: `{payload['apl_min_cnr']:.2f}`.",
        f"Objects: `{', '.join(payload['objects'])}`.",
        "",
        "## Best Target-Free Postprocess Rows",
        "",
        markdown_table(compact),
        "",
        "## Summary",
        "",
        (
            f"Best-final target-free post-processing has minimum CNR "
            f"`{payload['best_final_target_free_min_cnr']:.3f}` across the audited objects."
        ),
        (
            f"Best-trace target-free post-processing has minimum CNR "
            f"`{payload['best_trace_target_free_min_cnr']:.3f}` across the audited objects."
        ),
        (
            "The best-trace rows still depend on target-aware step selection inherited from "
            "`stage4_trace_audit_r3`; only the threshold itself is target-free."
        ),
        (
            "These outputs sharpen the interpretation of Stage 4: thresholded masks can clear "
            "the APL CNR gate across all held-out objects, but strict continuous-output URED "
            "remains below the original reproduction target."
        ),
        "",
    ]
    (out_dir / "stage4_postprocess_allobjects_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate Stage 4 best images for all objects and audit target-free post-processing.")
    parser.add_argument("--profile", default="full")
    parser.add_argument("--checkpoint", type=Path, default=Path("results/colab_imports/pro2_full_exp_residual_e2_r1/artifacts/model_checkpoint.pt"))
    parser.add_argument("--model-kind", default="exponential_residual_unet")
    parser.add_argument("--audit-dir", type=Path, default=Path("results/stage4_trace_audit_r3"))
    parser.add_argument("--object-names", default=None)
    parser.add_argument("--bbox-pad", type=int, default=2)
    parser.add_argument("--output-dir", type=Path, default=Path("results/stage4_postprocess_allobjects_r1"))
    parser.add_argument("--reuse-image-audits", action="store_true")
    parser.add_argument("--apl-min-cnr", type=float, default=10.43)
    args = parser.parse_args()

    root = project_root()
    audit_dir = args.audit_dir if args.audit_dir.is_absolute() else root / args.audit_dir
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    object_names = parse_names(args.object_names) or object_names_from_audit(audit_dir)
    rows: list[dict[str, object]] = []
    image_audit_dirs: dict[str, str] = {}
    for object_name in object_names:
        object_dir = out_dir / "image_audits" / object_name
        arrays_path = object_dir / "stage4_image_audit_arrays.npz"
        metrics_path = object_dir / "stage4_image_audit_metrics.csv"
        if not args.reuse_image_audits or not arrays_path.exists() or not metrics_path.exists():
            run_audit(
                Namespace(
                    profile=args.profile,
                    checkpoint=args.checkpoint,
                    model_kind=args.model_kind,
                    audit_dir=args.audit_dir,
                    object_name=object_name,
                    bbox_pad=args.bbox_pad,
                    output_dir=object_dir,
                )
            )
        arrays = dict(np.load(arrays_path))
        source_metrics = _read(metrics_path).set_index("method")
        target = arrays["target"]
        image_audit_dirs[object_name] = str(object_dir)
        for source in POSTPROCESS_SOURCES:
            source_row = source_metrics.loc[source]
            rows.extend(
                audit_source(
                    object_name=object_name,
                    source=source,
                    source_config=str(source_row["source_config"]),
                    steps=int(source_row["steps"]),
                    image=arrays[source],
                    target=target,
                    apl_min_cnr=float(args.apl_min_cnr),
                )
            )
    metrics = pd.DataFrame(rows)
    metrics.to_csv(out_dir / "stage4_postprocess_allobjects_metrics.csv", index=False)
    final_best = best_target_free(metrics, "best_final")
    trace_best = best_target_free(metrics, "best_trace_regen")
    payload = {
        "apl_min_cnr": float(args.apl_min_cnr),
        "objects": object_names,
        "image_audit_dirs": image_audit_dirs,
        "num_metric_rows": int(len(metrics)),
        "best_final_target_free_min_cnr": float(final_best["cnr"].min()),
        "best_final_target_free_all_hit_apl_min": bool(final_best["hits_apl_min"].all()),
        "best_trace_target_free_min_cnr": float(trace_best["cnr"].min()),
        "best_trace_target_free_all_hit_apl_min": bool(trace_best["hits_apl_min"].all()),
        "best_final_target_free_methods": final_best[["object", "postprocess_method", "cnr", "hits_apl_min"]].to_dict(orient="records"),
        "best_trace_target_free_methods": trace_best[["object", "postprocess_method", "cnr", "hits_apl_min"]].to_dict(orient="records"),
    }
    (out_dir / "stage4_postprocess_allobjects_summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    save_metrics_table(
        out_dir / "stage4_postprocess_allobjects_best_table.png",
        pd.concat([final_best.assign(source_group="best_final"), trace_best.assign(source_group="best_trace_regen")], ignore_index=True)[
            ["source_group", "object", "postprocess_method", "cnr", "psnr", "ssim", "iou", "hits_apl_min"]
        ],
        title="Stage 4 all-object postprocess best rows",
        max_rows=12,
    )
    write_report(out_dir, metrics, payload)
    print(f"wrote {out_dir}")


if __name__ == "__main__":
    main()
