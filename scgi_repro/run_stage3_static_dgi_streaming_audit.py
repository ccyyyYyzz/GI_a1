from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd
import torch

from run_stage3_static_dgi_audit import (
    hadamard_exact_reconstruct,
    make_audit_objects,
    metric_row,
    parse_floats,
    write_figure,
    write_report,
)
from src.config_utils import load_config, project_root
from src.data_sim import generate_patterns, seed_everything
from src.dgi import minmax


def factor_to_count(factor: float, base_patterns: int) -> int:
    return max(1, int(round(float(factor) * int(base_patterns))))


def empty_accumulators(num_objects: int, num_pixels: int, device: torch.device) -> dict[str, torch.Tensor]:
    return {
        "b_sum": torch.zeros(num_objects, dtype=torch.float64, device=device),
        "b_max": torch.zeros(num_objects, dtype=torch.float64, device=device),
        "bi_sum": torch.zeros(num_objects, num_pixels, dtype=torch.float64, device=device),
        "q_sum": torch.zeros((), dtype=torch.float64, device=device),
        "qi_sum": torch.zeros(num_pixels, dtype=torch.float64, device=device),
    }


def clone_accumulators(acc: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
    return {key: value.detach().clone() for key, value in acc.items()}


def add_segment(acc: dict[str, torch.Tensor], flat_images: torch.Tensor, patterns: torch.Tensor) -> None:
    if patterns.numel() == 0:
        return
    b = flat_images @ patterns.t()
    q = patterns.sum(dim=1)
    acc["b_sum"] += b.sum(dim=1).to(torch.float64)
    acc["b_max"] = torch.maximum(acc["b_max"], b.amax(dim=1).to(torch.float64))
    acc["bi_sum"] += (b @ patterns).to(torch.float64)
    acc["q_sum"] += q.sum().to(torch.float64)
    acc["qi_sum"] += (q.unsqueeze(0) @ patterns).squeeze(0).to(torch.float64)


def reconstruct_from_accumulators(acc: dict[str, torch.Tensor], num_patterns: int, image_size: int) -> torch.Tensor:
    b_max = acc["b_max"].clamp_min(1.0e-12).unsqueeze(1)
    y_sum = acc["b_sum"] / acc["b_max"].clamp_min(1.0e-12)
    yi_sum = acc["bi_sum"] / b_max
    out = yi_sum / float(num_patterns) - (y_sum / acc["q_sum"].clamp_min(1.0e-12)).unsqueeze(1) * (
        acc["qi_sum"].unsqueeze(0) / float(num_patterns)
    )
    return out.reshape(out.shape[0], 1, image_size, image_size).to(torch.float32)


def write_progress(out_dir: Path, completed_patterns: int, max_patterns: int, completed_factors: list[float], started: float) -> None:
    payload = {
        "completed_patterns": int(completed_patterns),
        "max_patterns": int(max_patterns),
        "completed_factors": completed_factors,
        "elapsed_seconds": round(time.time() - started, 3),
    }
    (out_dir / "progress.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Streaming Stage 3 static random-DGI sampling audit.")
    parser.add_argument("--profile", default="full")
    parser.add_argument("--output-dir", type=Path, default=Path("results/stage3_static_dgi_streaming_r1"))
    parser.add_argument("--heldout-count", type=int, default=4)
    parser.add_argument("--pattern-factors", default="4,8,16,32")
    parser.add_argument("--chunk-patterns", type=int, default=512)
    parser.add_argument("--include-hadamard-exact", action="store_true")
    args = parser.parse_args()

    started = time.time()
    root = project_root()
    cfg = load_config(root / "config.yaml", args.profile)
    active = cfg["active"]
    h = int(active["image_size"])
    p = h * h
    n_full = int(active["num_patterns"])
    device = torch.device("cuda" if active.get("device") == "cuda" and torch.cuda.is_available() else "cpu")
    seed = int(cfg.get("seed", 0))
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    factors = sorted({float(factor) for factor in parse_floats(args.pattern_factors)})
    targets = [(factor, factor_to_count(factor, n_full)) for factor in factors]
    max_patterns = max(count for _factor, count in targets)
    objects, requested_source = make_audit_objects(root, cfg, args.heldout_count, seed + 1701)
    images_cpu = torch.stack([obj for _name, _source, obj in objects], dim=0).unsqueeze(1).float()
    images = images_cpu.to(device)
    flat = images.reshape(images.shape[0], p)

    generator = seed_everything(seed)
    acc = empty_accumulators(len(objects), p, device)
    snapshots: dict[float, dict[str, torch.Tensor]] = {}
    target_index = 0
    completed = 0
    completed_factors: list[float] = []
    while completed < max_patterns:
        chunk = min(int(args.chunk_patterns), max_patterns - completed)
        patterns = generate_patterns(
            chunk,
            h,
            generator,
            cfg.get("data", {}).get("pattern_distribution", "uniform"),
            device=device,
        )
        offset = 0
        while offset < chunk:
            next_target_count = targets[target_index][1]
            segment_end_global = min(completed + chunk, next_target_count)
            segment_len = segment_end_global - (completed + offset)
            if segment_len <= 0:
                snapshots[targets[target_index][0]] = clone_accumulators(acc)
                completed_factors.append(targets[target_index][0])
                target_index += 1
                continue
            add_segment(acc, flat, patterns[offset : offset + segment_len])
            offset += segment_len
            if completed + offset == next_target_count:
                snapshots[targets[target_index][0]] = clone_accumulators(acc)
                completed_factors.append(targets[target_index][0])
                target_index += 1
                if target_index >= len(targets):
                    break
        completed += chunk
        write_progress(out_dir, min(completed, max_patterns), max_patterns, completed_factors, started)
        if target_index >= len(targets):
            break

    rows: list[dict[str, object]] = []
    for factor, n_patterns in targets:
        recon_batch = reconstruct_from_accumulators(snapshots[factor], n_patterns, h).cpu()
        for idx, (name, source, _obj) in enumerate(objects):
            target = images_cpu[idx]
            raw = recon_batch[idx]
            mm = minmax(raw).clamp(0.0, 1.0)
            for variant, recon in [("raw", raw), ("minmax", mm)]:
                row = metric_row(name, source, variant, recon, target)
                row["pattern_factor"] = float(factor)
                row["num_patterns"] = int(n_patterns)
                row["streaming"] = True
                rows.append(row)
            if args.include_hadamard_exact and abs(float(factor) - 1.0) < 1.0e-12:
                recon = hadamard_exact_reconstruct(target)
                row = metric_row(name, source, "hadamard_exact", recon, target)
                row["pattern_factor"] = float(factor)
                row["num_patterns"] = int(2 * h * h)
                row["streaming"] = False
                rows.append(row)

    frame = pd.DataFrame(rows)
    frame.to_csv(out_dir / "stage3_static_dgi_streaming_audit.csv", index=False)
    figures = write_figure(out_dir, frame.rename(columns={"variant": "variant"}))
    manifest = {
        "profile": cfg["profile"],
        "image_size": h,
        "active_num_patterns": n_full,
        "pattern_factors": factors,
        "pattern_counts": [count for _factor, count in targets],
        "objects": len(objects),
        "requested_dataset_source": requested_source,
        "device": str(device),
        "chunk_patterns": int(args.chunk_patterns),
        "elapsed_seconds": round(time.time() - started, 3),
        "figures": figures,
    }
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_report(out_dir, frame, manifest)
    print(json.dumps(manifest, indent=2), flush=True)
    print(f"wrote {out_dir / 'stage3_static_dgi_streaming_audit.csv'}", flush=True)


if __name__ == "__main__":
    main()
