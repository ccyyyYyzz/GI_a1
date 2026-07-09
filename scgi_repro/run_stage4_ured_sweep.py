from __future__ import annotations

import argparse
import itertools
import json
import time
from copy import deepcopy
from pathlib import Path

import pandas as pd
import torch

from run_stage3_tests import load_stage0_model, make_stage3_objects, parse_shard
from src.config_utils import load_config, project_root
from src.data_sim import compute_static_measurements, dynamic_factors, generate_patterns, normalize_rows, seed_everything
from src.dgi import dgi_reconstruct
from src.metrics import bundle, cnr
from src.train_scgi import analytic_gain_correct, correct_measurements, oracle_gain_correct
from src.ured import optimize_untrained


def parse_floats(text: str | None, default: list[float]) -> list[float]:
    if text is None:
        return default
    return [float(part) for part in text.replace(",", " ").split() if part.strip()]


def parse_ints(text: str | None, default: list[int]) -> list[int]:
    if text is None:
        return default
    return [int(part) for part in text.replace(",", " ").split() if part.strip()]


def parse_strings(text: str | None, default: list[str]) -> list[str]:
    if text is None:
        return default
    return [part.strip() for part in text.replace(",", " ").split() if part.strip()]


def select_shard(items: list, shard: tuple[int, int] | None) -> list:
    if shard is None:
        return items
    index, total = shard
    return [item for item_index, item in enumerate(items) if item_index % total == index]


def build_grid(args: argparse.Namespace, cfg: dict) -> list[dict[str, object]]:
    active = cfg.get("active", {})
    ured = cfg.get("ured", {})
    values = {
        "steps": parse_ints(args.steps_values, [int(active.get("ured_steps", 50))]),
        "lr": parse_floats(args.lr_values, [float(active.get("ured_lr", 0.001))]),
        "beta": parse_floats(args.beta_values, [float(ured.get("beta", 0.5))]),
        "xi": parse_floats(args.xi_values, [float(ured.get("xi", 0.5))]),
        "x_step": parse_floats(args.x_step_values, [float(ured.get("x_step", 0.5))]),
        "channels": parse_ints(args.channels_values, [int(ured.get("channels", 24))]),
        "blocks": parse_ints(args.blocks_values, [int(ured.get("blocks", 3))]),
        "residual_scale": parse_floats(args.residual_scale_values, [float(ured.get("residual_scale", 0.1))]),
        "denoiser": parse_strings(args.denoiser_values, [str(ured.get("denoiser", "avg_pool"))]),
        "denoise_kernel": parse_ints(args.denoise_kernel_values, [int(ured.get("denoise_kernel", 3))]),
        "nlm_h": parse_floats(args.nlm_h_values, [float(ured.get("nlm_h", 0.08))]),
    }
    keys = list(values.keys())
    grid = []
    for global_index, combo in enumerate(itertools.product(*(values[key] for key in keys))):
        record = dict(zip(keys, combo))
        record["global_config_index"] = global_index
        grid.append(record)
    return grid


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sweep SCGI-UNN/URED hyperparameters on Stage 3 held-out targets.")
    parser.add_argument("--profile", default="full")
    parser.add_argument("--checkpoint", type=Path, default=None)
    parser.add_argument("--model-kind", default="exponential_residual_unet")
    parser.add_argument("--output-dir", type=Path, default=Path("results/stage4_ured_sweep"))
    parser.add_argument("--object-names", default=None, help="Comma/space separated object names to include.")
    parser.add_argument("--object-shard", type=parse_shard, default=None)
    parser.add_argument("--config-shard", type=parse_shard, default=None)
    parser.add_argument("--steps-values", default=None)
    parser.add_argument("--lr-values", default=None)
    parser.add_argument("--beta-values", default=None)
    parser.add_argument("--xi-values", default=None)
    parser.add_argument("--x-step-values", default=None)
    parser.add_argument("--channels-values", default=None)
    parser.add_argument("--blocks-values", default=None)
    parser.add_argument("--residual-scale-values", default=None)
    parser.add_argument("--denoiser-values", default=None)
    parser.add_argument("--denoise-kernel-values", default=None)
    parser.add_argument("--nlm-h-values", default=None)
    parser.add_argument("--seed-offset", type=int, default=0)
    parser.add_argument("--fixed-init-seed", type=int, default=None)
    parser.add_argument("--save-traces", action="store_true")
    args = parser.parse_args()

    started = time.time()
    root = project_root()
    cfg = load_config(root / "config.yaml", args.profile)
    if args.model_kind:
        cfg.setdefault("scgi", {})["model_kind"] = str(args.model_kind)
    active = cfg["active"]
    h = int(active["image_size"])
    n = int(active["num_patterns"])
    device = torch.device("cuda" if active.get("device") == "cuda" and torch.cuda.is_available() else "cpu")
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = args.checkpoint or (root / "results" / "stage_0" / cfg["profile"] / "model_checkpoint.pt")

    generator = seed_everything(int(cfg.get("seed", 0)) + int(args.seed_offset))
    model = load_stage0_model(root, cfg, checkpoint, device)
    patterns = generate_patterns(n, h, generator, cfg.get("data", {}).get("pattern_distribution", "uniform"), device=device)

    all_objects = make_stage3_objects(h)
    if args.object_names:
        requested = set(parse_strings(args.object_names, []))
        all_objects = [(name, obj) for name, obj in all_objects if name in requested]
    selected_objects = select_shard(all_objects, args.object_shard)
    if not selected_objects:
        raise ValueError("No objects selected for Stage 4 URED sweep.")

    grid = build_grid(args, cfg)
    grid = select_shard(grid, args.config_shard)
    if not grid:
        raise ValueError("No configs selected for Stage 4 URED sweep.")

    manifest = {
        "profile": args.profile,
        "checkpoint": str(checkpoint),
        "model_kind": args.model_kind,
        "device": str(device),
        "image_size": h,
        "num_patterns": n,
        "objects": [name for name, _ in selected_objects],
        "num_configs": len(grid),
        "object_shard": str(args.object_shard),
        "config_shard": str(args.config_shard),
        "fixed_init_seed": args.fixed_init_seed,
        "started_unix": started,
    }
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    images = torch.stack([obj for _name, obj in selected_objects], dim=0).unsqueeze(1).to(device)
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

    baseline_rows: list[dict[str, object]] = []
    coarse_recons: list[torch.Tensor] = []
    for idx, (name, _obj) in enumerate(selected_objects):
        target = images[idx]
        baselines = {
            "static": (dgi_reconstruct(b_static[idx], patterns, h), b_static[idx]),
            "dynamic": (dgi_reconstruct(r_dynamic[idx], patterns, h), r_dynamic[idx]),
            "scgi": (dgi_reconstruct(y_scgi[idx], patterns, h), y_scgi[idx]),
            "analytic": (dgi_reconstruct(y_analytic[idx], patterns, h), y_analytic[idx]),
            "oracle": (dgi_reconstruct(y_oracle[idx], patterns, h), y_oracle[idx]),
        }
        coarse_recons.append(baselines["scgi"][0])
        for method, (recon, measurements) in baselines.items():
            metrics = bundle(recon, target, measurements)
            baseline_rows.append(
                {
                    "object": name,
                    "method": method,
                    "lambda_true": float(lambdas[idx].detach().cpu()),
                    "lambda_analytic": float(lambda_hat[idx].detach().cpu()),
                    **metrics.__dict__,
                }
            )
    write_csv(out_dir / "baseline_metrics.csv", baseline_rows)

    metric_rows: list[dict[str, object]] = []
    trace_rows: list[dict[str, object]] = []
    for config_index, config in enumerate(grid):
        global_config_index = int(config["global_config_index"])
        config_id = f"cfg{global_config_index:04d}"
        for object_index, (name, _obj) in enumerate(selected_objects):
            if args.fixed_init_seed is None:
                init_seed = int(cfg.get("seed", 0)) + int(args.seed_offset) + 1000 * global_config_index + object_index
            else:
                init_seed = int(args.fixed_init_seed) + object_index
            seed_everything(init_seed)
            run_cfg = deepcopy(cfg)
            run_cfg.setdefault("active", {})["ured_steps"] = int(config["steps"])
            run_cfg.setdefault("active", {})["ured_lr"] = float(config["lr"])
            run_cfg.setdefault("ured", {}).update(
                {
                    "beta": float(config["beta"]),
                    "xi": float(config["xi"]),
                    "x_step": float(config["x_step"]),
                    "channels": int(config["channels"]),
                    "blocks": int(config["blocks"]),
                    "residual_scale": float(config["residual_scale"]),
                    "denoiser": str(config["denoiser"]),
                    "denoise_kernel": int(config["denoise_kernel"]),
                    "nlm_h": float(config["nlm_h"]),
                }
            )
            target = images[object_index]
            result = optimize_untrained(
                coarse_recons[object_index],
                y_scgi[object_index],
                patterns,
                run_cfg,
                target=target,
                metric_fn=cnr,
                use_regularizer=True,
            )
            metrics = bundle(result.image, target, y_scgi[object_index])
            row = {
                "config_id": config_id,
                "config_index": config_index,
                "global_config_index": global_config_index,
                "init_seed": init_seed,
                "object": name,
                "method": "scgi_unn" if float(config["beta"]) == 0.0 else "scgi_ured",
                **config,
                **metrics.__dict__,
                "best_trace_cnr": max(result.cnr_trace) if result.cnr_trace else float("nan"),
                "final_loss": result.loss_trace[-1] if result.loss_trace else float("nan"),
            }
            metric_rows.append(row)
            if args.save_traces:
                for step, (loss_value, cnr_value) in enumerate(zip(result.loss_trace, result.cnr_trace), start=1):
                    trace_rows.append(
                        {
                            "config_id": config_id,
                            "object": name,
                            "step": step,
                            "loss": loss_value,
                            "cnr": cnr_value,
                        }
                    )
            write_csv(out_dir / "ured_sweep_metrics.csv", metric_rows)
            if args.save_traces:
                write_csv(out_dir / "ured_sweep_traces.csv", trace_rows)
            (out_dir / "progress.json").write_text(
                json.dumps(
                    {
                        "completed_metric_rows": len(metric_rows),
                        "total_metric_rows": len(grid) * len(selected_objects),
                        "last_config_id": config_id,
                        "last_object": name,
                        "elapsed_seconds": time.time() - started,
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            print(
                f"{config_id} {name} {row['method']} cnr={row['cnr']:.4f} psnr={row['psnr']:.4f} "
                f"best_trace={row['best_trace_cnr']:.4f}",
                flush=True,
            )

    metrics_df = pd.DataFrame(metric_rows)
    if len(metrics_df):
        summary = (
            metrics_df.groupby(["config_id"], as_index=False)
            .agg(
                objects=("object", "count"),
                mean_cnr=("cnr", "mean"),
                min_cnr=("cnr", "min"),
                mean_psnr=("psnr", "mean"),
                min_psnr=("psnr", "min"),
                mean_ssim=("ssim", "mean"),
            )
            .sort_values(["min_cnr", "mean_cnr"], ascending=False)
        )
        for key in [key for key in grid[0].keys() if key != "global_config_index"]:
            values = metrics_df.groupby("config_id")[key].first()
            summary[key] = summary["config_id"].map(values)
        summary.to_csv(out_dir / "ured_sweep_summary.csv", index=False)
    manifest["elapsed_seconds"] = time.time() - started
    manifest["completed"] = True
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out_dir}")


if __name__ == "__main__":
    main()
