from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import time

import pandas as pd
import torch

from run_mechanism_m1 import make_synthetic_objects, reconstruct_observed
from src.basis import basis_frame_budget, make_basis
from src.config_utils import load_config, project_root
from src.mechanisms import (
    estimate_agc_gain,
    estimate_scgi_proxy_gain,
    make_multiplicative_channel,
    reference_anchor_count,
    simulate_channel_measurements,
)
from src.run_progress import append_rows, read_completed_unit_indexes, write_json_atomic, write_progress
from src.scgi_model import make_scgi_model
from src.train_scgi import correct_measurements_padded


def parse_shard(value: str | None) -> tuple[int, int]:
    """Parse a zero-based shard spec like ``0/5``."""

    if not value:
        return 0, 1
    parts = value.split("/", 1)
    if len(parts) != 2:
        raise ValueError("--shard must use the form i/k, for example 0/5.")
    shard_index = int(parts[0])
    shard_count = int(parts[1])
    if shard_count <= 0:
        raise ValueError("Shard count must be positive.")
    if shard_index < 0 or shard_index >= shard_count:
        raise ValueError("Shard index must be zero-based and satisfy 0 <= i < k.")
    return shard_index, shard_count


def parse_float_list(value: str | None) -> list[float] | None:
    if value is None or not str(value).strip():
        return None
    return [float(part) for part in str(value).replace(",", " ").split() if part.strip()]


def parse_int_list(value: str | None) -> list[int] | None:
    if value is None or not str(value).strip():
        return None
    return [int(part) for part in str(value).replace(",", " ").split() if part.strip()]


def load_frozen_scgi_corrector(
    root: Path,
    cfg: dict,
    checkpoint: Path | None,
    model_kind: str | None,
):
    if checkpoint is None:
        return None
    resolved = checkpoint if checkpoint.is_absolute() else root / checkpoint
    if not resolved.exists():
        raise FileNotFoundError(f"SCGI checkpoint not found: {resolved}")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    payload = torch.load(resolved, map_location=device)
    state_dict = payload["model_state_dict"] if isinstance(payload, dict) and "model_state_dict" in payload else payload
    metadata = payload.get("corrector_metadata", {}) if isinstance(payload, dict) else {}
    payload_cfg = payload.get("config") if isinstance(payload, dict) else None
    model_cfg = copy.deepcopy(payload_cfg if isinstance(payload_cfg, dict) else cfg)
    if isinstance(metadata, dict) and metadata.get("model_kind") and not model_kind:
        model_cfg.setdefault("scgi", {})["model_kind"] = str(metadata["model_kind"])
    if model_kind:
        model_cfg.setdefault("scgi", {})["model_kind"] = str(model_kind)
    model = make_scgi_model(model_cfg).to(device)
    model.load_state_dict(state_dict)
    model.eval()

    def correct(values: torch.Tensor) -> torch.Tensor:
        source_device = values.device
        source_dtype = values.dtype
        input_mode = str(metadata.get("input_mode", "raw")).lower() if isinstance(metadata, dict) else "raw"
        if input_mode == "scgi_proxy_gain":
            model_values = estimate_scgi_proxy_gain(
                values.detach().to(dtype=torch.float32),
                paired=False,
                window=max(9, int(0.05 * values.numel())),
            )
        elif input_mode == "agc_gain":
            model_values = estimate_agc_gain(
                values.detach().to(dtype=torch.float32),
                window=max(9, int(0.05 * values.numel())),
            )
        else:
            model_values = values.detach().to(dtype=torch.float32)
        rows = model_values.reshape(1, -1).to(device=device, dtype=torch.float32)
        if metadata.get("input_normalize") == "row_max":
            rows = rows / rows.amax(dim=1, keepdim=True).clamp_min(1.0e-8)
        elif metadata.get("input_normalize") == "row_absmax":
            rows = rows / rows.abs().amax(dim=1, keepdim=True).clamp_min(1.0e-8)
        output_clamp = metadata.get("output_clamp", "01")
        predicted = correct_measurements_padded(model, rows, clamp=(output_clamp != "none")).reshape(-1)
        if metadata.get("target_mode") == "gain":
            corrected = values.detach().to(device=device, dtype=torch.float32) / predicted.clamp_min(1.0e-6)
        else:
            corrected = predicted
        return corrected.to(device=source_device, dtype=source_dtype)

    return correct


def load_frozen_scgi_corrector_map(
    root: Path,
    cfg: dict,
    checkpoint_map: Path | None,
):
    if checkpoint_map is None:
        return {}
    resolved = checkpoint_map if checkpoint_map.is_absolute() else root / checkpoint_map
    if not resolved.exists():
        raise FileNotFoundError(f"SCGI checkpoint map not found: {resolved}")
    entries = json.loads(resolved.read_text(encoding="utf-8-sig"))
    correctors = {}
    for basis_name, entry in entries.items():
        if isinstance(entry, str):
            checkpoint = Path(entry)
            model_kind = None
        else:
            checkpoint = Path(entry["checkpoint"])
            model_kind = entry.get("model_kind")
        correctors[str(basis_name)] = load_frozen_scgi_corrector(root, cfg, checkpoint, model_kind)
    return correctors


def main() -> None:
    parser = argparse.ArgumentParser(description="M2 phase scan with fair frame accounting.")
    parser.add_argument("--profile", default="smoke")
    parser.add_argument("--objects", type=int, default=1)
    parser.add_argument("--seeds", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=Path("results/phase_m2"))
    parser.add_argument("--shard", default="", help="Optional zero-based shard spec i/k, for example 0/5.")
    parser.add_argument("--scgi-checkpoint", type=Path, default=None, help="Optional frozen SCGI checkpoint for scgi_frozen correction.")
    parser.add_argument("--scgi-checkpoint-map", type=Path, default=None, help="Optional JSON map from basis name to basis-specific SCGI checkpoint.")
    parser.add_argument("--scgi-model-kind", default=None, help="Model kind to use when loading --scgi-checkpoint.")
    parser.add_argument("--rho-values", default="", help="Optional override for mechanism.rho_values, e.g. '0.001 0.01 0.1 1 10'.")
    parser.add_argument("--sigma-values", default="", help="Optional override for mechanism.sigma_a_values, e.g. '0.05 0.1 0.3'.")
    parser.add_argument("--reference-periods", default="", help="Optional override for mechanism.reference_periods, e.g. '2 8 32'.")
    parser.add_argument("--resume", action="store_true", help="Resume from an existing phase_scan.csv by skipping completed unit_index values.")
    parser.add_argument("--no-findings", action="store_true")
    args = parser.parse_args()

    root = project_root()
    cfg = load_config(root / "config.yaml", args.profile)
    scgi_corrector = load_frozen_scgi_corrector(root, cfg, args.scgi_checkpoint, args.scgi_model_kind)
    scgi_corrector_map = load_frozen_scgi_corrector_map(root, cfg, args.scgi_checkpoint_map)
    shard_index, shard_count = parse_shard(args.shard)
    mech = cfg.get("mechanism", {})
    h = int(mech.get("image_size", 32))
    p = h * h
    frame_budget, _ = basis_frame_budget(p)
    rho_values = parse_float_list(args.rho_values) or list(mech.get("rho_values", [0.001, 0.01, 0.1, 1.0]))
    sigma_values = parse_float_list(args.sigma_values) or list(mech.get("sigma_a_values", [0.05, 0.15, 0.3]))
    reference_periods = parse_int_list(args.reference_periods) or [int(x) for x in mech.get("reference_periods", [2, 8, 32])]
    objects = make_synthetic_objects(args.objects, h, int(cfg.get("seed", 0)))
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    scan_path = out_dir / "phase_scan.csv"

    basis_specs = [
        ("random_uniform", {"num_frames": frame_budget, "reconstruction": "correlation"}),
        ("random_binary", {"num_frames": frame_budget, "reconstruction": "correlation"}),
        ("hadamard_paired", {}),
        ("dct_paired", {}),
        ("fourier_fourstep", {"num_frames": frame_budget}),
        ("srht_paired", {}),
    ]
    if scan_path.exists() and not args.resume:
        scan_path.unlink()
    start_time = time.time()
    total_units = len(basis_specs) * len(rho_values) * len(sigma_values) * int(args.seeds) * len(objects)
    selected_units = sum(1 for index in range(total_units) if index % shard_count == shard_index)
    completed_units = read_completed_unit_indexes(scan_path) if args.resume else set()
    write_json_atomic(
        out_dir / "run_manifest.json",
        {
            "profile": args.profile,
            "objects": int(args.objects),
            "seeds": int(args.seeds),
            "shard": args.shard or "0/1",
            "resume": bool(args.resume),
            "rho_values": rho_values,
            "sigma_values": sigma_values,
            "reference_periods": reference_periods,
            "scgi_checkpoint": None if args.scgi_checkpoint is None else str(args.scgi_checkpoint),
            "scgi_checkpoint_map": None if args.scgi_checkpoint_map is None else str(args.scgi_checkpoint_map),
            "scgi_model_kind": args.scgi_model_kind,
            "outputs": {
                "scan": "phase_scan.csv",
                "progress": "progress.json",
                "summary": "phase_summary.csv",
                "best_equal_frame_blind": "best_equal_frame_blind_methods.csv",
                "flip_boundary": "flip_boundary.csv",
            },
        },
    )
    write_progress(
        out_dir,
        state="running",
        start_time=start_time,
        completed_units=len(completed_units),
        selected_units=selected_units,
        total_units=total_units,
        last_unit_index=max(completed_units) if completed_units else None,
        extra={"rows_written_this_run": 0, "resume": bool(args.resume)},
    )
    rows_written_this_run = 0
    last_unit_index: int | None = max(completed_units) if completed_units else None
    unit_index = 0
    for basis_name, kwargs in basis_specs:
        basis = make_basis(basis_name, num_pixels=p, seed=int(cfg.get("seed", 0)), **kwargs)
        corrections = ["none", "oracle", "agc", "scgi_proxy"]
        basis_scgi_corrector = scgi_corrector_map.get(basis.name, scgi_corrector)
        if basis_scgi_corrector is not None:
            corrections.append("scgi_frozen")
        corrections += [f"reference_k{k}" for k in reference_periods]
        if basis.paired:
            corrections.append("pairwise")
        for rho in rho_values:
            for sigma_a in sigma_values:
                for seed_idx in range(args.seeds):
                    for obj_idx, obj in enumerate(objects):
                        current_unit = unit_index
                        unit_index += 1
                        if current_unit % shard_count != shard_index:
                            continue
                        if current_unit in completed_units:
                            continue
                        ideal = basis.measure(obj)
                        channel = make_multiplicative_channel(
                            basis.num_frames,
                            model="ou",
                            rho=float(rho),
                            sigma_a=float(sigma_a),
                            seed=9000 + seed_idx,
                            device=str(ideal.device),
                            dtype=ideal.dtype,
                        )
                        observed = simulate_channel_measurements(
                            ideal,
                            channel,
                            read_noise=float(mech.get("read_noise", 0.0)),
                            seed=9100 + obj_idx,
                        )
                        unit_rows = []
                        for correction in corrections:
                            metrics = reconstruct_observed(
                                basis=basis,
                                obj=obj,
                                observed=observed,
                                true_gains=channel.gains,
                                correction=correction,
                                agc_window=max(9, int(0.05 * frame_budget)),
                                scgi_corrector=basis_scgi_corrector,
                            )
                            reference_period = int(correction.rsplit("k", 1)[1]) if correction.startswith("reference_k") else 0
                            reference_frames = reference_anchor_count(basis.num_frames, reference_period) if reference_period else 0
                            unit_rows.append(
                                {
                                    "basis": basis.name,
                                    "correction": correction,
                                    "reference_period": reference_period,
                                    "rho": float(rho),
                                    "sigma_a": float(sigma_a),
                                    "seed": seed_idx,
                                    "object": obj_idx,
                                    "num_frames": basis.num_frames,
                                    "reference_frames": reference_frames,
                                    "total_physical_frames": basis.num_frames + reference_frames,
                                    "num_coefficients": basis.num_coefficients,
                                    "num_pixels": basis.num_pixels,
                                    "shard": args.shard or "0/1",
                                    "unit_index": current_unit,
                                    **metrics,
                                }
                            )
                        append_rows(scan_path, unit_rows)
                        completed_units.add(current_unit)
                        rows_written_this_run += len(unit_rows)
                        last_unit_index = current_unit
                        write_progress(
                            out_dir,
                            state="running",
                            start_time=start_time,
                            completed_units=len(completed_units),
                            selected_units=selected_units,
                            total_units=total_units,
                            last_unit_index=last_unit_index,
                            extra={"rows_written_this_run": rows_written_this_run, "resume": bool(args.resume)},
                        )
    if not scan_path.exists():
        raise RuntimeError(f"Shard {args.shard} produced no rows.")
    df = pd.read_csv(scan_path)
    if df.empty:
        raise RuntimeError(f"Shard {args.shard} produced an empty phase_scan.csv.")
    write_progress(
        out_dir,
        state="summarizing",
        start_time=start_time,
        completed_units=len(completed_units),
        selected_units=selected_units,
        total_units=total_units,
        last_unit_index=last_unit_index,
        extra={"rows": int(len(df)), "rows_written_this_run": rows_written_this_run, "resume": bool(args.resume)},
    )
    summary = (
        df.groupby(["rho", "sigma_a", "basis", "correction"], as_index=False)
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
    best = summary.groupby(["rho", "sigma_a"], as_index=False).head(1)
    blind_summary = summary[summary["correction"] != "oracle"].copy()
    best_blind = blind_summary.groupby(["rho", "sigma_a"], as_index=False).head(1)
    equal_frame_blind = blind_summary[blind_summary["total_physical_frames"] == blind_summary["num_frames"]].copy()
    best_equal_frame_blind = equal_frame_blind.groupby(["rho", "sigma_a"], as_index=False).head(1)
    reference_summary = blind_summary[blind_summary["correction"].str.startswith("reference_")].copy()
    best_reference = reference_summary.groupby(["rho", "sigma_a"], as_index=False).head(1)
    summary.to_csv(out_dir / "phase_summary.csv", index=False)
    best.to_csv(out_dir / "best_methods.csv", index=False)
    blind_summary.to_csv(out_dir / "phase_blind_summary.csv", index=False)
    best_blind.to_csv(out_dir / "best_blind_methods.csv", index=False)
    equal_frame_blind.to_csv(out_dir / "phase_equal_frame_blind_summary.csv", index=False)
    best_equal_frame_blind.to_csv(out_dir / "best_equal_frame_blind_methods.csv", index=False)
    reference_summary.to_csv(out_dir / "phase_reference_summary.csv", index=False)
    best_reference.to_csv(out_dir / "best_reference_methods.csv", index=False)
    flip_rows = []
    for (sigma_a, correction), group in blind_summary.groupby(["sigma_a", "correction"]):
        pivot = group.pivot_table(index="rho", columns="basis", values="psnr_mean", aggfunc="mean").sort_index()
        for challenger in ["random_uniform", "random_binary", "fourier_fourstep", "dct_paired", "srht_paired"]:
            if "hadamard_paired" not in pivot.columns or challenger not in pivot.columns:
                continue
            diff = pivot[challenger] - pivot["hadamard_paired"]
            positive = diff[diff >= 0.0]
            if not len(positive):
                rho_star = float("nan")
                boundary_status = "not_reached"
            else:
                rho_star = float(positive.index[0])
                boundary_status = "left_censored" if rho_star == float(diff.index.min()) else "observed"
            flip_rows.append(
                {
                    "sigma_a": float(sigma_a),
                    "correction": correction,
                    "challenger": challenger,
                    "baseline": "hadamard_paired",
                    "rho_star_first_ge": rho_star,
                    "boundary_status": boundary_status,
                    "max_margin_db": float(diff.max()),
                    "min_margin_db": float(diff.min()),
                    "points": int(diff.notna().sum()),
                }
            )
    pd.DataFrame(flip_rows).to_csv(out_dir / "flip_boundary.csv", index=False)
    if not args.no_findings:
        with (root / "FINDINGS.md").open("a", encoding="utf-8") as f:
            f.write("\n## M2 Compact Phase Scan\n\n")
            f.write(f"Wrote `{scan_path.as_posix()}` and best-method table for smoke-scale phase-map plumbing.\n")
    write_progress(
        out_dir,
        state="completed",
        start_time=start_time,
        completed_units=len(completed_units),
        selected_units=selected_units,
        total_units=total_units,
        last_unit_index=last_unit_index,
        extra={"rows": int(len(df)), "rows_written_this_run": rows_written_this_run, "resume": bool(args.resume)},
    )
    print(f"wrote {scan_path}")
    print(f"wrote {out_dir / 'best_methods.csv'}")
    print(f"wrote {out_dir / 'best_blind_methods.csv'}")
    print(f"wrote {out_dir / 'best_equal_frame_blind_methods.csv'}")
    print(f"wrote {out_dir / 'best_reference_methods.csv'}")
    print(f"wrote {out_dir / 'flip_boundary.csv'}")


if __name__ == "__main__":
    main()
