from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from run_stage3_tests import load_stage0_model, make_stage3_objects
from src.config_utils import load_config, project_root
from src.data_sim import compute_static_measurements, dynamic_factors, generate_patterns, normalize_rows, seed_everything
from src.dgi import dgi_reconstruct
from src.metrics import bundle, cnr, psnr, ssim
from src.plotting import save_image_grid, save_metrics_table
from src.train_scgi import analytic_gain_correct, correct_measurements, oracle_gain_correct
from src.ured import optimize_untrained


def _read(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def _find_object_index(objects: list[tuple[str, torch.Tensor]], name: str) -> int:
    for idx, (object_name, _obj) in enumerate(objects):
        if object_name == name:
            return idx
    raise ValueError(f"Unknown object {name!r}; available: {[name for name, _ in objects]}")


def _row_to_ured_cfg(base_cfg: dict, row: pd.Series, *, steps: int | None = None) -> dict:
    def get_value(name: str, default: object) -> object:
        value = row.get(name, default)
        if pd.isna(value):
            return default
        return value

    cfg = deepcopy(base_cfg)
    cfg.setdefault("active", {})["ured_steps"] = int(steps if steps is not None else row["steps"])
    cfg.setdefault("active", {})["ured_lr"] = float(get_value("lr", 0.001))
    cfg.setdefault("ured", {}).update(
        {
            "beta": float(row["beta"]),
            "xi": float(row["xi"]),
            "x_step": float(row["x_step"]),
            "channels": int(row["channels"]),
            "blocks": int(row["blocks"]),
            "residual_scale": float(row["residual_scale"]),
            "denoiser": str(row["denoiser"]),
            "denoise_kernel": int(row["denoise_kernel"]),
            "nlm_h": float(row["nlm_h"]),
            "nlm_patch_size": int(get_value("nlm_patch_size", base_cfg.get("ured", {}).get("nlm_patch_size", 5))),
            "nlm_patch_distance": int(get_value("nlm_patch_distance", base_cfg.get("ured", {}).get("nlm_patch_distance", 6))),
        }
    )
    return cfg


def _bbox_from_target(target: torch.Tensor, threshold: float = 0.5, pad: int = 2) -> tuple[slice, slice]:
    mask = target.detach().float().squeeze() > threshold
    coords = torch.nonzero(mask, as_tuple=False)
    if coords.numel() == 0:
        h, w = mask.shape
        return slice(0, h), slice(0, w)
    y0 = max(0, int(coords[:, 0].min().item()) - pad)
    y1 = min(mask.shape[0], int(coords[:, 0].max().item()) + pad + 1)
    x0 = max(0, int(coords[:, 1].min().item()) - pad)
    x1 = min(mask.shape[1], int(coords[:, 1].max().item()) + pad + 1)
    return slice(y0, y1), slice(x0, x1)


def _mask_stats(recon: torch.Tensor, target: torch.Tensor, *, crop: tuple[slice, slice] | None = None) -> dict[str, float]:
    if crop is not None:
        yslice, xslice = crop
        recon = recon[..., yslice, xslice]
        target = target[..., yslice, xslice]
    return {
        "cnr": cnr(recon, target),
        "psnr": psnr(recon, target),
        "ssim": ssim(recon, target),
    }


def _threshold_sweep(recon: torch.Tensor, target: torch.Tensor) -> pd.DataFrame:
    rows = []
    for threshold in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
        rows.append({"target_threshold": threshold, "cnr": cnr(recon, target, threshold=threshold)})
    return pd.DataFrame(rows)


def _markdown_table(frame: pd.DataFrame) -> str:
    headers = list(frame.columns)
    rows = frame.fillna("").astype(str).values.tolist()
    widths = [len(str(header)) for header in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(cell))
    header = "| " + " | ".join(str(header).ljust(widths[idx]) for idx, header in enumerate(headers)) + " |"
    sep = "| " + " | ".join("-" * widths[idx] for idx in range(len(headers))) + " |"
    body = ["| " + " | ".join(row[idx].ljust(widths[idx]) for idx in range(len(headers))) + " |" for row in rows]
    return "\n".join([header, sep, *body])


def _write_report(out_dir: Path, metrics: pd.DataFrame, manifest: dict[str, object]) -> None:
    compact = metrics[
        [
            "method",
            "source_config",
            "steps",
            "standard_cnr",
            "bbox_cnr",
            "standard_psnr",
            "bbox_psnr",
        ]
    ].copy()
    for column in ["standard_cnr", "bbox_cnr", "standard_psnr", "bbox_psnr"]:
        compact[column] = compact[column].map(lambda value: f"{float(value):.3f}" if value != "" else "")
    final = metrics[metrics["method"] == "best_final"].iloc[0]
    bbox_delta = float(final["bbox_cnr"]) - float(final["standard_cnr"])
    lines = [
        "# Stage 4 Image/ROI Audit",
        "",
        f"Object: `{manifest['object']}`",
        f"Source audit: `{manifest['audit_dir']}`",
        "",
        "## Metrics",
        "",
        _markdown_table(compact),
        "",
        "## Interpretation",
        "",
        (
            f"The regenerated best Stage 4 stripe output has standard CNR "
            f"{float(final['standard_cnr']):.3f}, below the APL URED minimum 10.43."
        ),
        (
            f"Cropping to the target bounding box changes CNR by {bbox_delta:.3f} "
            f"({float(final['bbox_cnr']):.3f} in the cropped box), so the miss is not "
            "explained by extra far-background pixels in the full-image mask."
        ),
        "The target-threshold sweep is invariant because the synthetic stripe target is binary.",
        "The grid PNG should be used as a visual diagnostic, not as a replacement for the prompt CNR metric.",
        "",
    ]
    (out_dir / "stage4_image_audit_report.md").write_text("\n".join(lines), encoding="utf-8")


def select_rows(audit_dir: Path, object_name: str) -> tuple[pd.Series, pd.Series]:
    details = _read(audit_dir / "stage4_trace_audit_details.csv")
    details = details[details["object"] == object_name].copy()
    if details.empty:
        raise ValueError(f"No audit rows found for object {object_name!r} in {audit_dir}")
    final_row = details.sort_values("cnr", ascending=False).iloc[0]
    trace_row = details.sort_values("best_trace_cnr_audited", ascending=False).iloc[0]
    return final_row, trace_row


def run_audit(args: argparse.Namespace) -> Path:
    root = project_root()
    cfg = load_config(root / "config.yaml", args.profile)
    if args.model_kind:
        cfg.setdefault("scgi", {})["model_kind"] = str(args.model_kind)
    active = cfg["active"]
    h = int(active["image_size"])
    n = int(active["num_patterns"])
    device = torch.device("cuda" if active.get("device") == "cuda" and torch.cuda.is_available() else "cpu")
    checkpoint = args.checkpoint if args.checkpoint.is_absolute() else root / args.checkpoint
    audit_dir = args.audit_dir if args.audit_dir.is_absolute() else root / args.audit_dir
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    final_row, trace_row = select_rows(audit_dir, args.object_name)
    objects = make_stage3_objects(h)
    object_index = _find_object_index(objects, args.object_name)
    generator = seed_everything(int(cfg.get("seed", 0)))
    model = load_stage0_model(root, cfg, checkpoint, device)
    patterns = generate_patterns(n, h, generator, cfg.get("data", {}).get("pattern_distribution", "uniform"), device=device)

    images = torch.stack([obj for _name, obj in objects], dim=0).unsqueeze(1).to(device)
    flat = images.reshape(images.shape[0], h * h)
    b_static = normalize_rows(
        compute_static_measurements(flat, patterns, int(active.get("measurement_chunk", 128))),
        cfg.get("data", {}).get("normalize", "max"),
    )
    factors, lambdas = dynamic_factors(
        images.shape[0],
        n,
        float(active.get("lambda_min", cfg.get("data", {}).get("lambda_min", 0.9995))),
        float(active.get("lambda_max", cfg.get("data", {}).get("lambda_max", 1.0))),
        generator,
        device=device,
    )
    r_dynamic = normalize_rows(factors * b_static, cfg.get("data", {}).get("normalize", "max"))
    y_scgi = correct_measurements(model, r_dynamic, h)
    y_oracle = oracle_gain_correct(r_dynamic, factors, normalize_mode=cfg.get("data", {}).get("normalize", "max"))
    y_analytic, lambda_hat = analytic_gain_correct(r_dynamic, normalize_mode=cfg.get("data", {}).get("normalize", "max"))

    target = images[object_index]
    base_recons: dict[str, tuple[torch.Tensor, torch.Tensor]] = {
        "target": (target.squeeze(0), b_static[object_index]),
        "static": (dgi_reconstruct(b_static[object_index], patterns, h), b_static[object_index]),
        "dynamic": (dgi_reconstruct(r_dynamic[object_index], patterns, h), r_dynamic[object_index]),
        "scgi": (dgi_reconstruct(y_scgi[object_index], patterns, h), y_scgi[object_index]),
        "analytic": (dgi_reconstruct(y_analytic[object_index], patterns, h), y_analytic[object_index]),
        "oracle": (dgi_reconstruct(y_oracle[object_index], patterns, h), y_oracle[object_index]),
    }

    ured_outputs: dict[str, tuple[torch.Tensor, pd.Series, int]] = {}
    for label, row, steps in [
        ("best_final", final_row, int(final_row["steps"])),
        ("best_trace_regen", trace_row, int(trace_row["best_trace_step"])),
    ]:
        init_seed = int(row.get("init_seed", int(cfg.get("seed", 0))))
        seed_everything(init_seed)
        run_cfg = _row_to_ured_cfg(cfg, row, steps=steps)
        result = optimize_untrained(
            base_recons["scgi"][0],
            y_scgi[object_index],
            patterns,
            run_cfg,
            target=target,
            metric_fn=cnr,
            use_regularizer=True,
        )
        ured_outputs[label] = (result.image, row, steps)

    rows: list[dict[str, object]] = []
    bbox = _bbox_from_target(target, pad=args.bbox_pad)
    image_items = []
    labels = []
    arrays: dict[str, np.ndarray] = {}
    for method, (image, measurements) in base_recons.items():
        image_cpu = image.detach().float().cpu().squeeze()
        arrays[method] = image_cpu.numpy()
        image_items.append(image_cpu.numpy())
        labels.append(method)
        if method == "target":
            continue
        standard = bundle(image, target, measurements)
        bbox_stats = _mask_stats(image, target, crop=bbox)
        rows.append(
            {
                "method": method,
                "source_config": "",
                "steps": "",
                "standard_cnr": standard.cnr,
                "standard_psnr": standard.psnr,
                "standard_ssim": standard.ssim,
                "bbox_cnr": bbox_stats["cnr"],
                "bbox_psnr": bbox_stats["psnr"],
                "bbox_ssim": bbox_stats["ssim"],
                "ks_p": standard.ks_p,
            }
        )

    for method, (image, row, steps) in ured_outputs.items():
        image_cpu = image.detach().float().cpu().squeeze()
        arrays[method] = image_cpu.numpy()
        image_items.append(image_cpu.numpy())
        labels.append(f"{method}\n{row['sweep']} {row['config_id']}")
        standard = bundle(image, target, y_scgi[object_index])
        bbox_stats = _mask_stats(image, target, crop=bbox)
        rows.append(
            {
                "method": method,
                "source_config": f"{row['sweep']}/{row['config_id']}",
                "steps": steps,
                "standard_cnr": standard.cnr,
                "standard_psnr": standard.psnr,
                "standard_ssim": standard.ssim,
                "bbox_cnr": bbox_stats["cnr"],
                "bbox_psnr": bbox_stats["psnr"],
                "bbox_ssim": bbox_stats["ssim"],
                "ks_p": standard.ks_p,
            }
        )
        _threshold_sweep(image, target).assign(method=method).to_csv(
            out_dir / f"{method}_target_threshold_sweep.csv",
            index=False,
        )

    np.savez_compressed(out_dir / "stage4_image_audit_arrays.npz", **arrays)
    metrics = pd.DataFrame(rows)
    metrics.to_csv(out_dir / "stage4_image_audit_metrics.csv", index=False)
    save_metrics_table(
        out_dir / "stage4_image_audit_metrics.png",
        metrics[["method", "standard_cnr", "bbox_cnr", "standard_psnr", "bbox_psnr"]],
        title=f"Stage 4 image/ROI audit: {args.object_name}",
        max_rows=12,
    )
    save_image_grid(
        out_dir / "stage4_image_audit_grid.png",
        image_items,
        labels=labels,
        columns=4,
        cell_size=128,
    )
    manifest = {
        "profile": args.profile,
        "checkpoint": str(checkpoint),
        "audit_dir": str(audit_dir),
        "object": args.object_name,
        "object_index": object_index,
        "lambda_true": float(lambdas[object_index].detach().cpu()),
        "lambda_analytic": float(lambda_hat[object_index].detach().cpu()),
        "bbox_pad": int(args.bbox_pad),
        "bbox": {
            "y_start": bbox[0].start,
            "y_stop": bbox[0].stop,
            "x_start": bbox[1].start,
            "x_stop": bbox[1].stop,
        },
        "final_source": {
            "sweep": str(final_row["sweep"]),
            "config_id": str(final_row["config_id"]),
            "cnr": float(final_row["cnr"]),
        },
        "trace_source": {
            "sweep": str(trace_row["sweep"]),
            "config_id": str(trace_row["config_id"]),
            "best_trace_step": int(trace_row["best_trace_step"]),
            "best_trace_cnr": float(trace_row["best_trace_cnr_audited"]),
        },
    }
    (out_dir / "stage4_image_audit_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    _write_report(out_dir, metrics, manifest)
    print(f"wrote {out_dir}")
    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate Stage 4 best images and audit CNR/ROI sensitivity.")
    parser.add_argument("--profile", default="full")
    parser.add_argument("--checkpoint", type=Path, default=Path("results/colab_imports/pro2_full_exp_residual_e2_r1/artifacts/model_checkpoint.pt"))
    parser.add_argument("--model-kind", default="exponential_residual_unet")
    parser.add_argument("--audit-dir", type=Path, default=Path("results/stage4_trace_audit_r3"))
    parser.add_argument("--object-name", default="stripe_target")
    parser.add_argument("--bbox-pad", type=int, default=2)
    parser.add_argument("--output-dir", type=Path, default=Path("results/stage4_image_audit_r1"))
    args = parser.parse_args()
    run_audit(args)


if __name__ == "__main__":
    main()
