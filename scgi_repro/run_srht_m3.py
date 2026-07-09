from __future__ import annotations

import argparse
import math
from pathlib import Path
import time

import pandas as pd
import torch

from run_mechanism_m1 import make_synthetic_objects, simulate_and_reconstruct
from src.basis import MeasurementBasis, hadamard_matrix, interleave_paired_frames
from src.config_utils import load_config, project_root
from src.run_progress import append_rows, write_json_atomic, write_progress


DEFAULT_VARIANTS = [
    "hadamard_ordered",
    "perm_only",
    "sign_only",
    "srht_full",
    "hadamard_time_interleave",
    "sign_time_interleave",
    "hadamard_block_shuffle",
    "sign_block_shuffle",
]
DEFAULT_CORRECTIONS = ["none", "agc", "scgi_proxy", "pairwise", "oracle"]


def parse_floats(text: str | None, default: list[float]) -> list[float]:
    if text is None:
        return default
    return [float(part) for part in text.replace(",", " ").split() if part.strip()]


def parse_variants(text: str | None) -> list[str]:
    if text is None:
        return list(DEFAULT_VARIANTS)
    variants = [part for part in text.replace(",", " ").split() if part.strip()]
    if not variants:
        raise ValueError("At least one variant is required.")
    return variants


def parse_strings(text: str | None, default: list[str]) -> list[str]:
    if text is None:
        return list(default)
    values = [part for part in text.replace(",", " ").split() if part.strip()]
    if not values:
        raise ValueError("At least one value is required.")
    return values


def default_block_size(num_pixels: int, block_size: int | None = None) -> int:
    if block_size is None:
        return max(1, int(math.sqrt(num_pixels)))
    return max(1, min(int(block_size), int(num_pixels)))


def interleaved_row_indices(num_pixels: int, block_size: int | None = None) -> torch.Tensor:
    """Interleave Hadamard row blocks in round-robin temporal order."""

    block_size = default_block_size(num_pixels, block_size)
    num_blocks = int(math.ceil(num_pixels / block_size))
    rows = []
    for offset in range(block_size):
        for block_idx in range(num_blocks):
            row = block_idx * block_size + offset
            if row < num_pixels:
                rows.append(row)
    return torch.tensor(rows, dtype=torch.long)


def block_permuted_row_indices(num_pixels: int, seed: int, block_size: int | None = None) -> torch.Tensor:
    """Randomize rows within each contiguous block while preserving block order."""

    block_size = default_block_size(num_pixels, block_size)
    num_blocks = int(math.ceil(num_pixels / block_size))
    generator = torch.Generator(device="cpu").manual_seed(int(seed) + 7919)
    blocks = []
    for block_idx in range(num_blocks):
        start = int(block_idx) * block_size
        end = min(start + block_size, num_pixels)
        block = torch.arange(start, end, dtype=torch.long)
        blocks.append(block.index_select(0, torch.randperm(block.numel(), generator=generator)))
    return torch.cat(blocks)


def make_variant(name: str, num_pixels: int, seed: int, block_size: int | None = None) -> MeasurementBasis:
    g = torch.Generator(device="cpu").manual_seed(seed)
    h = hadamard_matrix(num_pixels)
    signs = torch.randint(0, 2, (num_pixels,), generator=g).mul(2).sub(1).float()
    perm = torch.randperm(num_pixels, generator=g)
    ordered = torch.arange(num_pixels)
    resolved_block_size = default_block_size(num_pixels, block_size)
    interleaved = interleaved_row_indices(num_pixels, resolved_block_size)
    block_perm = block_permuted_row_indices(num_pixels, seed=seed, block_size=block_size)
    use_signs = False
    if name == "hadamard_ordered":
        row_indices = ordered
        row_order = "ordered"
    elif name == "perm_only":
        row_indices = perm
        row_order = "full_random_permutation"
    elif name == "sign_only":
        row_indices = ordered
        row_order = "ordered"
        use_signs = True
    elif name == "srht_full":
        row_indices = perm
        row_order = "full_random_permutation"
        use_signs = True
    elif name in {"hadamard_interleaved", "hadamard_time_interleave"}:
        row_indices = interleaved
        row_order = "block_round_robin_interleaved"
    elif name in {"sign_interleaved", "sign_time_interleave"}:
        row_indices = interleaved
        row_order = "block_round_robin_interleaved"
        use_signs = True
    elif name in {"block_perm_only", "hadamard_block_shuffle"}:
        row_indices = block_perm
        row_order = "within_block_shuffle"
    elif name in {"sign_block_perm", "sign_block_shuffle"}:
        row_indices = block_perm
        row_order = "within_block_shuffle"
        use_signs = True
    else:
        raise ValueError(name)
    rows = h.index_select(0, row_indices)
    if use_signs:
        rows = rows * signs.reshape(1, -1)
    return MeasurementBasis(
        name=name,
        patterns=interleave_paired_frames(rows),
        paired=True,
        signed_rows=rows,
        row_indices=row_indices,
        srht_signs=signs if use_signs else None,
        metadata={
            "ablation": name,
            "row_order": row_order,
            "sign_randomized": use_signs,
            "block_size": resolved_block_size,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Compact M3 SRHT ablation.")
    parser.add_argument("--profile", default="smoke")
    parser.add_argument("--objects", type=int, default=1)
    parser.add_argument("--seeds", type=int, default=1)
    parser.add_argument("--rho-values", default=None)
    parser.add_argument("--sigma-a", type=float, default=None)
    parser.add_argument("--variants", default=None, help="Space/comma-separated ablation variants.")
    parser.add_argument("--corrections", default=None, help="Space/comma-separated correction methods.")
    parser.add_argument("--block-size", type=int, default=None, help="Rows per block for block_perm variants.")
    parser.add_argument("--output-dir", type=Path, default=Path("results/srht_m3"))
    parser.add_argument("--no-findings", action="store_true")
    args = parser.parse_args()

    root = project_root()
    cfg = load_config(root / "config.yaml", args.profile)
    mech = cfg.get("mechanism", {})
    h = int(mech.get("image_size", 32))
    p = h * h
    objects = make_synthetic_objects(args.objects, h, int(cfg.get("seed", 0)))
    rho_values = parse_floats(args.rho_values, list(mech.get("rho_values", [0.001, 0.01, 0.1, 1.0]))[:4])
    sigma_a = float(
        args.sigma_a
        if args.sigma_a is not None
        else list(mech.get("sigma_a_values", [0.15]))[min(1, len(mech.get("sigma_a_values", [0.15])) - 1)]
    )
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    variants = parse_variants(args.variants)
    corrections = parse_strings(args.corrections, DEFAULT_CORRECTIONS)
    scan_path = out_dir / "srht_ablation.csv"
    if scan_path.exists():
        scan_path.unlink()
    start_time = time.time()
    total_units = len(variants) * len(rho_values) * int(args.seeds) * len(objects)
    write_json_atomic(
        out_dir / "run_manifest.json",
        {
            "profile": args.profile,
            "objects": int(args.objects),
            "seeds": int(args.seeds),
            "rho_values": rho_values,
            "sigma_a": sigma_a,
            "variants": variants,
            "corrections": corrections,
            "block_size": default_block_size(p, args.block_size),
            "outputs": {
                "raw": "srht_ablation.csv",
                "summary": "srht_ablation_summary.csv",
                "progress": "progress.json",
            },
        },
    )
    write_progress(
        out_dir,
        state="running",
        start_time=start_time,
        completed_units=0,
        selected_units=total_units,
        total_units=total_units,
        last_unit_index=None,
        extra={"rows_written_this_run": 0},
    )

    unit_index = 0
    rows_written = 0
    last_unit_index: int | None = None
    for variant in variants:
        basis = make_variant(variant, p, int(cfg.get("seed", 0)), block_size=args.block_size)
        for rho in rho_values:
            for seed_idx in range(args.seeds):
                for obj_idx, obj in enumerate(objects):
                    unit_rows = []
                    for correction in corrections:
                        metrics = simulate_and_reconstruct(
                            basis=basis,
                            obj=obj,
                            correction=correction,
                            channel_model="ou",
                            rho=float(rho),
                            sigma_a=sigma_a,
                            channel_seed=12000 + seed_idx,
                            read_noise=float(mech.get("read_noise", 0.0)),
                            noise_seed=12100 + obj_idx,
                            agc_window=max(9, int(0.05 * basis.num_frames)),
                        )
                        unit_rows.append(
                            {
                                "variant": variant,
                                "correction": correction,
                                "rho": float(rho),
                                "sigma_a": sigma_a,
                                "row_order": str(basis.metadata.get("row_order", variant) if basis.metadata else variant),
                                "sign_randomized": bool(
                                    basis.metadata.get("sign_randomized", False) if basis.metadata else False
                                ),
                                "block_size": int(basis.metadata.get("block_size", 0) if basis.metadata else 0),
                                "seed": seed_idx,
                                "object": obj_idx,
                                "num_frames": int(basis.num_frames),
                                "num_coefficients": int(basis.num_coefficients),
                                "num_pixels": int(basis.num_pixels),
                                "agc_window": max(9, int(0.05 * basis.num_frames)),
                                **metrics,
                            }
                        )
                    append_rows(scan_path, unit_rows)
                    rows_written += len(unit_rows)
                    last_unit_index = unit_index
                    unit_index += 1
                    write_progress(
                        out_dir,
                        state="running",
                        start_time=start_time,
                        completed_units=unit_index,
                        selected_units=total_units,
                        total_units=total_units,
                        last_unit_index=last_unit_index,
                        extra={
                            "rows_written_this_run": rows_written,
                            "last_variant": variant,
                            "last_rho": float(rho),
                            "last_seed": int(seed_idx),
                            "last_object": int(obj_idx),
                        },
                    )
    if not scan_path.exists():
        raise RuntimeError(f"M3 run produced no rows in {scan_path}.")
    df = pd.read_csv(scan_path)
    if df.empty:
        raise RuntimeError(f"M3 run produced an empty {scan_path}.")
    write_progress(
        out_dir,
        state="summarizing",
        start_time=start_time,
        completed_units=unit_index,
        selected_units=total_units,
        total_units=total_units,
        last_unit_index=last_unit_index,
        extra={"rows": int(len(df)), "rows_written_this_run": rows_written},
    )
    (
        df.groupby(["variant", "row_order", "sign_randomized", "block_size", "correction", "rho", "sigma_a"], as_index=False)
        .agg(
            psnr_mean=("psnr", "mean"),
            psnr_std=("psnr", "std"),
            rel_mse_mean=("rel_mse", "mean"),
            rel_mse_std=("rel_mse", "std"),
            gain_rel_mse_mean=("gain_rel_mse", "mean"),
        )
        .to_csv(out_dir / "srht_ablation_summary.csv", index=False)
    )
    write_progress(
        out_dir,
        state="completed",
        start_time=start_time,
        completed_units=unit_index,
        selected_units=total_units,
        total_units=total_units,
        last_unit_index=last_unit_index,
        extra={"rows": int(len(df)), "rows_written_this_run": rows_written},
    )
    if not args.no_findings:
        with (root / "FINDINGS.md").open("a", encoding="utf-8") as f:
            f.write("\n## M3 Compact SRHT Ablation\n\n")
            f.write(
                f"Wrote `{scan_path.as_posix()}` for variants: "
                f"`{', '.join(variants)}`.\n"
            )
    print(f"wrote {scan_path}")


if __name__ == "__main__":
    main()
