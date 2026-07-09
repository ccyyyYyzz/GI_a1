from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image, ImageDraw, ImageFont

from src.config_utils import load_config, project_root
from src.data_sim import compute_static_measurements, dynamic_factors, generate_patterns, normalize_rows, seed_everything
from src.dgi import dgi_reconstruct
from src.metrics import bundle
from src.plotting import save_image_grid, save_metrics_table
from src.scgi_model import make_scgi_model
from src.train_scgi import analytic_gain_correct, correct_measurements, oracle_gain_correct


def _font(size: int) -> ImageFont.ImageFont:
    for name in ("C:/Windows/Fonts/arial.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def make_stage3_objects(image_size: int) -> list[tuple[str, torch.Tensor]]:
    h = int(image_size)
    objects: list[tuple[str, np.ndarray]] = []

    canvas = Image.new("L", (h, h), 0)
    draw = ImageDraw.Draw(canvas)
    draw.text((h // 5, h // 8), "A", fill=255, font=_font(max(12, int(h * 0.75))))
    objects.append(("letter_A", np.asarray(canvas, dtype=np.float32) / 255.0))

    stripes = np.zeros((h, h), dtype=np.float32)
    for width, start in [(1, h // 8), (2, h // 3), (3, h // 2)]:
        for x in range(start, min(h, start + h // 5), 2 * width):
            stripes[h // 6 : 5 * h // 6, x : min(h, x + width)] = 1.0
    objects.append(("stripe_target", stripes))

    bars = np.zeros((h, h), dtype=np.float32)
    bars[h // 5 : 4 * h // 5, h // 5 : h // 5 + max(2, h // 12)] = 1.0
    bars[4 * h // 5 - max(2, h // 12) : 4 * h // 5, h // 5 : 4 * h // 5] = 1.0
    objects.append(("letter_L", bars))

    ring = Image.new("L", (h, h), 0)
    draw = ImageDraw.Draw(ring)
    margin = h // 5
    draw.ellipse((margin, margin, h - margin, h - margin), outline=255, width=max(2, h // 12))
    objects.append(("ring", np.asarray(ring, dtype=np.float32) / 255.0))

    out = []
    for name, arr in objects:
        if arr.max() > 0:
            arr = arr / float(arr.max())
        out.append((name, torch.from_numpy(arr).float()))
    return out


def load_stage0_model(root: Path, cfg: dict, checkpoint: Path, device: torch.device) -> torch.nn.Module:
    model = make_scgi_model(cfg).to(device)
    payload = torch.load(checkpoint, map_location=device)
    model.load_state_dict(payload["model_state_dict"])
    model.eval()
    return model


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 3 held-out target DGI/SCGI tests.")
    parser.add_argument("--profile", default="smoke")
    parser.add_argument("--checkpoint", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=Path("results/stage_3"))
    parser.add_argument("--model-kind", default=None, help="Override scgi.model_kind for loading a checkpoint.")
    args = parser.parse_args()

    root = project_root()
    cfg = load_config(root / "config.yaml", args.profile)
    if args.model_kind:
        cfg.setdefault("scgi", {})["model_kind"] = str(args.model_kind)
    active = cfg["active"]
    h = int(active["image_size"])
    n = int(active["num_patterns"])
    device = torch.device("cuda" if active.get("device") == "cuda" and torch.cuda.is_available() else "cpu")
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir / cfg["profile"]
    out_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = args.checkpoint or (root / "results" / "stage_0" / cfg["profile"] / "model_checkpoint.pt")
    model = load_stage0_model(root, cfg, checkpoint, device)

    generator = seed_everything(int(cfg.get("seed", 0)))
    patterns = generate_patterns(n, h, generator, cfg.get("data", {}).get("pattern_distribution", "uniform"), device=device)
    objects = make_stage3_objects(h)
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

    rows = []
    grid_images = []
    grid_labels = []
    for idx, (name, _obj) in enumerate(objects):
        target = images[idx]
        reconstructions = {
            "static": (dgi_reconstruct(b_static[idx], patterns, h), b_static[idx]),
            "dynamic": (dgi_reconstruct(r_dynamic[idx], patterns, h), r_dynamic[idx]),
            "scgi": (dgi_reconstruct(y_scgi[idx], patterns, h), y_scgi[idx]),
            "analytic": (dgi_reconstruct(y_analytic[idx], patterns, h), y_analytic[idx]),
            "oracle": (dgi_reconstruct(y_oracle[idx], patterns, h), y_oracle[idx]),
        }
        grid_images.append(target.detach().cpu().squeeze().numpy())
        grid_labels.append(f"{name} target")
        for method, (recon, measurements) in reconstructions.items():
            metrics = bundle(recon, target, measurements)
            rows.append(
                {
                    "object": name,
                    "method": method,
                    "lambda_true": float(lambdas[idx].detach().cpu()),
                    "lambda_analytic": float(lambda_hat[idx].detach().cpu()),
                    **metrics.__dict__,
                }
            )
            grid_images.append(recon.detach().cpu().squeeze().numpy())
            grid_labels.append(f"{name} {method}")

    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "stage3_metrics.csv", index=False)
    save_metrics_table(
        out_dir / "stage3_metrics_table.png",
        df[["object", "method", "cnr", "psnr", "ssim", "ks_p"]].head(30),
        title="Stage 3 held-out target metrics",
        max_rows=30,
    )
    save_image_grid(
        out_dir / "stage3_recon_grid.png",
        grid_images,
        labels=grid_labels,
        columns=6,
        cell_size=72,
    )

    pivot = df.pivot_table(index="object", columns="method", values="cnr", aggfunc="mean")
    checks = [
        {
            "check": "scgi_cnr_above_dynamic_all",
            "value": bool((pivot["scgi"] > pivot["dynamic"]).all()),
            "passed": bool((pivot["scgi"] > pivot["dynamic"]).all()),
        },
        {
            "check": "scgi_cnr_ge_3_all",
            "value": bool((pivot["scgi"] >= 3.0).all()),
            "passed": bool((pivot["scgi"] >= 3.0).all()),
        },
        {
            "check": "static_psnr_gt_20_all",
            "value": bool((df[df["method"] == "static"]["psnr"] > 20.0).all()),
            "passed": bool((df[df["method"] == "static"]["psnr"] > 20.0).all()),
        },
    ]
    with (out_dir / "stage3_acceptance.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["check", "value", "passed"])
        writer.writeheader()
        writer.writerows(checks)
    print(f"wrote {out_dir}")


if __name__ == "__main__":
    main()
