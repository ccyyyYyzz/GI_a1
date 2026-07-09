from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from run_stage3_tests import make_stage3_objects
from src.config_utils import load_config, project_root
from src.data_sim import compute_static_measurements, generate_patterns, load_mnist_or_synthetic, normalize_rows, seed_everything
from src.dgi import dgi_reconstruct
from src.metrics import cnr, psnr, ssim


def parse_floats(text: str) -> list[float]:
    return [float(part) for part in text.replace(",", " ").split() if part.strip()]


def align_scale(vec: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    x_hat = vec.reshape(-1).detach().to(dtype=torch.float64)
    x = target.reshape(-1).detach().to(dtype=torch.float64)
    scale = (x_hat @ x) / x_hat.pow(2).sum().clamp_min(1.0e-12)
    return (x_hat * scale).reshape_as(target).to(dtype=torch.float32).clamp(0.0, 1.0)


def align_affine(vec: torch.Tensor, target: torch.Tensor) -> tuple[torch.Tensor, float, float]:
    x_hat = vec.reshape(-1).detach().to(dtype=torch.float64)
    x = target.reshape(-1).detach().to(dtype=torch.float64)
    design = torch.stack([torch.ones_like(x_hat), x_hat], dim=1)
    coef = torch.linalg.lstsq(design, x).solution
    aligned = (design @ coef).reshape_as(target).to(dtype=torch.float32).clamp(0.0, 1.0)
    return aligned, float(coef[0].detach().cpu()), float(coef[1].detach().cpu())


def make_audit_objects(root: Path, cfg: dict, count: int, seed: int) -> tuple[list[tuple[str, str, torch.Tensor]], str]:
    h = int(cfg["active"]["image_size"])
    objects: list[tuple[str, str, torch.Tensor]] = []
    for name, obj in make_stage3_objects(h):
        objects.append((name, "handcrafted", obj))

    source = str(cfg["active"].get("data_source", cfg.get("data", {}).get("source", "mnist")))
    train_samples = int(cfg["active"].get("train_samples", 0))
    requested = train_samples + int(count)
    data = load_mnist_or_synthetic(
        num_samples=requested,
        image_size=h,
        data_dir=root / cfg.get("paths", {}).get("data_dir", "data"),
        seed=seed,
        synthetic_fallback=bool(cfg.get("data", {}).get("synthetic_fallback", True)),
        source=source,
    )
    heldout = data[train_samples:requested]
    if heldout.shape[0] < count:
        heldout = data[-count:]
    for idx in range(min(count, int(heldout.shape[0]))):
        objects.append((f"heldout_{idx}", source, heldout[idx, 0].detach().cpu().float()))
    return objects, source


def metric_row(object_name: str, object_source: str, variant: str, recon: torch.Tensor, target: torch.Tensor) -> dict[str, object]:
    affine, offset, slope = align_affine(recon, target)
    scaled = align_scale(recon, target)
    raw_vec = recon.reshape(-1).detach().float()
    return {
        "object": object_name,
        "object_source": object_source,
        "variant": variant,
        "cnr": cnr(recon, target),
        "psnr": psnr(recon, target),
        "ssim": ssim(recon, target),
        "scale_aligned_psnr": psnr(scaled, target),
        "affine_aligned_psnr": psnr(affine, target),
        "affine_offset": offset,
        "affine_slope": slope,
        "recon_min": float(raw_vec.min().detach().cpu()),
        "recon_max": float(raw_vec.max().detach().cpu()),
        "recon_mean": float(raw_vec.mean().detach().cpu()),
    }


def write_report(out_dir: Path, rows: pd.DataFrame, manifest: dict[str, object]) -> None:
    grouped = (
        rows.groupby(["variant"], as_index=False)
        .agg(
            objects=("object", "count"),
            psnr_min=("psnr", "min"),
            psnr_mean=("psnr", "mean"),
            affine_psnr_min=("affine_aligned_psnr", "min"),
            affine_psnr_mean=("affine_aligned_psnr", "mean"),
            cnr_min=("cnr", "min"),
            cnr_mean=("cnr", "mean"),
        )
        .sort_values("variant")
    )
    lines = [
        "# Stage 3 Static DGI Audit",
        "",
        "This audit isolates the static DGI upper bound before any dynamic-channel correction.",
        "",
        "## Manifest",
        "",
    ]
    for key, value in manifest.items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Variant Summary", "", grouped.to_csv(index=False), "", "## Interpretation", ""])
    affine_best = float(rows["affine_aligned_psnr"].max()) if len(rows) else float("nan")
    cnr_best = float(rows["cnr"].max()) if len(rows) else float("nan")
    lines.extend(
        [
            f"- Best affine-aligned static DGI PSNR is `{affine_best:.3f}` dB.",
            f"- Best static DGI CNR is `{cnr_best:.3f}`.",
            "- If affine-aligned PSNR remains far below 20 dB, the prompt PSNR gate is not blocked by a simple display-scale offset.",
            "- CNR remains the more appropriate paper-facing metric for the APL-style DGI reconstructions.",
        ]
    )
    (out_dir / "stage3_static_dgi_audit_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_figure(out_dir: Path, rows: pd.DataFrame) -> list[str]:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return []
    pivot = rows.pivot_table(index="object", columns="variant", values="affine_aligned_psnr", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=160)
    pivot.plot(kind="bar", ax=ax)
    ax.axhline(20.0, color="crimson", linestyle="--", linewidth=1.2, label="20 dB gate")
    ax.set_ylabel("Affine-aligned PSNR (dB)")
    ax.set_title("Static DGI upper-bound audit")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(fontsize=7)
    fig.tight_layout()
    path = out_dir / "stage3_static_dgi_affine_psnr.png"
    fig.savefig(path)
    plt.close(fig)
    return [path.name]


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit static DGI upper-bound metrics for Stage 3 held-out targets.")
    parser.add_argument("--profile", default="full")
    parser.add_argument("--output-dir", type=Path, default=Path("results/stage3_static_dgi_audit"))
    parser.add_argument("--heldout-count", type=int, default=4)
    parser.add_argument("--pattern-factors", default="1.0", help="Fractions/multiples of active.num_patterns to test.")
    args = parser.parse_args()

    root = project_root()
    cfg = load_config(root / "config.yaml", args.profile)
    active = cfg["active"]
    h = int(active["image_size"])
    n_full = int(active["num_patterns"])
    device = torch.device("cuda" if active.get("device") == "cuda" and torch.cuda.is_available() else "cpu")
    seed = int(cfg.get("seed", 0))
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    objects, requested_source = make_audit_objects(root, cfg, args.heldout_count, seed + 1701)
    images = torch.stack([obj for _name, _source, obj in objects], dim=0).unsqueeze(1).to(device)
    factors = parse_floats(args.pattern_factors)
    max_patterns = max(1, int(round(n_full * max(factors))))
    generator = seed_everything(seed)
    patterns_all = generate_patterns(
        max_patterns,
        h,
        generator,
        cfg.get("data", {}).get("pattern_distribution", "uniform"),
        device=device,
    )
    rows: list[dict[str, object]] = []
    for factor in factors:
        n = max(1, int(round(n_full * factor)))
        patterns = patterns_all[:n]
        b_static = normalize_rows(
            compute_static_measurements(images.reshape(images.shape[0], h * h), patterns, int(active.get("measurement_chunk", 128))),
            cfg.get("data", {}).get("normalize", "max"),
        )
        for idx, (name, source, _obj) in enumerate(objects):
            target = images[idx]
            raw = dgi_reconstruct(b_static[idx], patterns, h, normalize=False)
            minmax = dgi_reconstruct(b_static[idx], patterns, h, normalize=True)
            for variant, recon in [("raw", raw), ("minmax", minmax)]:
                row = metric_row(name, source, variant, recon, target)
                row["pattern_factor"] = float(factor)
                row["num_patterns"] = int(n)
                rows.append(row)
    frame = pd.DataFrame(rows)
    frame.to_csv(out_dir / "stage3_static_dgi_audit.csv", index=False)
    figures = write_figure(out_dir, frame)
    manifest = {
        "profile": cfg["profile"],
        "image_size": h,
        "active_num_patterns": n_full,
        "pattern_factors": factors,
        "objects": len(objects),
        "requested_dataset_source": requested_source,
        "device": str(device),
        "figures": figures,
    }
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    write_report(out_dir, frame, manifest)
    print(json.dumps(manifest, indent=2))
    print(f"wrote {out_dir / 'stage3_static_dgi_audit.csv'}")


if __name__ == "__main__":
    main()
