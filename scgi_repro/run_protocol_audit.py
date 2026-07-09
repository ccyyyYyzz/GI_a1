"""Write auditable protocol tables for measurement-basis comparisons.

The output is intentionally descriptive rather than inferential: it records
frame budgets, reference-frame costs, optical throughput proxies, object
statistics, and seed conventions so reviewers can audit whether later M1-M4
comparisons used comparable measurement budgets.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pandas as pd
import torch
import yaml

from run_mechanism_m1 import make_synthetic_objects
from src.basis import MeasurementBasis, basis_frame_budget, make_basis
from src.mechanisms import reference_anchor_count


ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = ROOT / "config.yaml"


def load_config(path: Path) -> Dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def build_basis_specs(num_pixels: int, seed: int) -> List[Tuple[str, Dict[str, object], str]]:
    """Return the basis set used for protocol-level auditing.

    ``random_gaussian`` is included as a signed mathematical control. It is not
    a non-negative amplitude-only SLM pattern family, so the audit labels it as
    non-optical rather than silently mixing it with physical amplitude frames.
    """

    random_frames, _ = basis_frame_budget(num_pixels)
    return [
        ("random_uniform", {"num_frames": random_frames, "reconstruction": "correlation"}, "amplitude_random"),
        (
            "random_binary",
            {"num_frames": random_frames, "reconstruction": "correlation", "seed": seed + 17},
            "amplitude_random",
        ),
        (
            "random_gaussian",
            {"num_frames": random_frames, "reconstruction": "correlation", "seed": seed + 31},
            "signed_control",
        ),
        ("hadamard_paired", {}, "paired_orthogonal"),
        ("hadamard_sequency_paired", {}, "paired_orthogonal"),
        ("hadamard_cake_paired", {}, "paired_orthogonal"),
        ("hadamard_random_paired", {"seed": seed + 101}, "paired_orthogonal"),
        ("dct_paired", {}, "paired_transform"),
        ("fourier_fourstep", {"num_frames": random_frames}, "four_step_transform"),
        ("srht_paired", {"seed": seed + 47}, "paired_randomized_transform"),
    ]


def tensor_stats(values: torch.Tensor, prefix: str) -> Dict[str, float]:
    values = values.detach().cpu().to(dtype=torch.float64).reshape(-1)
    return {
        f"{prefix}_mean": float(values.mean().item()),
        f"{prefix}_std": float(values.std(unbiased=False).item()),
        f"{prefix}_min": float(values.min().item()),
        f"{prefix}_max": float(values.max().item()),
    }


def paired_complement_error(basis: MeasurementBasis) -> Dict[str, float]:
    if not basis.paired:
        return {
            "paired_complement_mean_abs_error": float("nan"),
            "paired_complement_max_abs_error": float("nan"),
        }
    plus = basis.patterns[0::2].detach().cpu().to(dtype=torch.float64)
    minus = basis.patterns[1::2].detach().cpu().to(dtype=torch.float64)
    error = (plus + minus - 1.0).abs()
    return {
        "paired_complement_mean_abs_error": float(error.mean().item()),
        "paired_complement_max_abs_error": float(error.max().item()),
    }


def basis_audit_rows(
    basis: MeasurementBasis,
    family: str,
    requested_name: str,
    seed: int,
    reference_periods: Iterable[int],
) -> List[Dict[str, object]]:
    patterns = basis.patterns.detach().cpu().to(dtype=torch.float64)
    frame_mean = patterns.mean(dim=1)
    frame_sum = patterns.sum(dim=1)
    frame_l2 = patterns.pow(2).sum(dim=1).sqrt()
    frame_energy = patterns.pow(2).mean(dim=1)
    metadata = basis.metadata or {}
    amplitude_valid = bool(float(patterns.min().item()) >= -1.0e-8 and float(patterns.max().item()) <= 1.0 + 1.0e-8)
    nonnegative = bool(float(patterns.min().item()) >= -1.0e-8)

    base_row: Dict[str, object] = {
        "requested_basis": requested_name,
        "basis": basis.name,
        "basis_family": family,
        "seed": int(seed),
        "paired": bool(basis.paired),
        "four_step": bool(basis.four_step),
        "num_frames": int(basis.num_frames),
        "num_coefficients": int(basis.num_coefficients),
        "num_pixels": int(basis.num_pixels),
        "frames_per_coefficient": float(basis.num_frames / max(1, basis.num_coefficients)),
        "reconstruction": basis.reconstruction,
        "amplitude_valid_0_1": amplitude_valid,
        "nonnegative_frames": nonnegative,
        "pattern_min": float(patterns.min().item()),
        "pattern_max": float(patterns.max().item()),
        "negative_fraction": float((patterns < 0).to(dtype=torch.float64).mean().item()),
        "zero_fraction": float((patterns.abs() <= 1.0e-8).to(dtype=torch.float64).mean().item()),
        "one_fraction": float(((patterns - 1.0).abs() <= 1.0e-8).to(dtype=torch.float64).mean().item()),
        "metadata_json": json.dumps(metadata, sort_keys=True),
    }
    base_row.update(tensor_stats(frame_mean, "frame_mean"))
    base_row.update(tensor_stats(frame_sum, "frame_sum"))
    base_row.update(tensor_stats(frame_l2, "frame_l2"))
    base_row.update(tensor_stats(frame_energy, "frame_energy"))
    base_row.update(paired_complement_error(basis))

    rows: List[Dict[str, object]] = []
    for period in reference_periods:
        reference_period = int(period)
        reference_frames = reference_anchor_count(basis.num_frames, reference_period) if reference_period > 0 else 0
        row = dict(base_row)
        row.update(
            {
                "reference_period": reference_period,
                "reference_frames": int(reference_frames),
                "total_physical_frames": int(basis.num_frames + reference_frames),
                "reference_frame_overhead": float(reference_frames / max(1, basis.num_frames)),
            }
        )
        rows.append(row)
    return rows


def object_audit_rows(objects: List[torch.Tensor], image_size: int, seed: int) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for index, obj in enumerate(objects):
        values = obj.detach().cpu().to(dtype=torch.float64).reshape(-1)
        rows.append(
            {
                "object_index": int(index),
                "object_family": "synthetic_digit_shapes_lines_blur",
                "seed": int(seed),
                "image_size": int(image_size),
                "num_pixels": int(values.numel()),
                "mean": float(values.mean().item()),
                "std": float(values.std(unbiased=False).item()),
                "min": float(values.min().item()),
                "max": float(values.max().item()),
                "nonzero_fraction": float((values.abs() > 1.0e-8).to(dtype=torch.float64).mean().item()),
                "l2_norm": float(values.pow(2).sum().sqrt().item()),
            }
        )
    return rows


def seed_audit_rows(seed: int) -> List[Dict[str, object]]:
    return [
        {
            "scope": "global_config",
            "seed_rule": "config.seed",
            "seed_or_formula": str(int(seed)),
            "notes": "Base seed shared by compact mechanism/profile runners.",
        },
        {
            "scope": "object_generation",
            "seed_rule": "make_synthetic_objects(count, image_size, seed=config.seed)",
            "seed_or_formula": str(int(seed)),
            "notes": "Deterministic synthetic digit/shape/line objects; no external MNIST/natural-image split in M1 audit.",
        },
        {
            "scope": "basis_random_uniform",
            "seed_rule": "make_basis(..., seed=config.seed)",
            "seed_or_formula": str(int(seed)),
            "notes": "I.i.d. random pattern matrix seed.",
        },
        {
            "scope": "basis_random_binary",
            "seed_rule": "M1 uses config.seed + 17; protocol audit uses explicit requested basis row.",
            "seed_or_formula": f"{int(seed)} or {int(seed) + 17}",
            "notes": "The protocol table records the concrete seed used for each audited basis.",
        },
        {
            "scope": "basis_random_gaussian",
            "seed_rule": "M1 uses config.seed + 31 when constructed through make_bases.",
            "seed_or_formula": f"{int(seed)} or {int(seed) + 31}",
            "notes": "Signed mathematical control, not an amplitude-only optical frame family.",
        },
        {
            "scope": "basis_srht",
            "seed_rule": "M1/M2 use config.seed + 47 for SRHT sign/row randomness in compact runners.",
            "seed_or_formula": str(int(seed) + 47),
            "notes": "The protocol table records the concrete seed used for the audited SRHT basis.",
        },
        {
            "scope": "channel_oracle_agc",
            "seed_rule": "1000 + 97 * seed_idx",
            "seed_or_formula": "1000 + 97 * seed_idx",
            "notes": "See run_mechanism_m1.py for oracle/AGC channel seeds.",
        },
        {
            "scope": "channel_pairwise_failure",
            "seed_rule": "4000 + 89 * seed_idx",
            "seed_or_formula": "4000 + 89 * seed_idx",
            "notes": "See run_mechanism_m1.py for adjacent-frame jitter channel seeds.",
        },
    ]


def write_report(
    output_dir: Path,
    basis_df: pd.DataFrame,
    object_df: pd.DataFrame,
    seed_df: pd.DataFrame,
    reference_periods: List[int],
) -> None:
    strict_rows = basis_df[basis_df["reference_period"] == 0].copy()
    amplitude_invalid = strict_rows[~strict_rows["amplitude_valid_0_1"]]["basis"].tolist()
    summary = {
        "basis_rows": int(len(basis_df)),
        "strict_basis_count": int(len(strict_rows)),
        "object_rows": int(len(object_df)),
        "seed_rows": int(len(seed_df)),
        "reference_periods": [int(x) for x in reference_periods],
        "amplitude_invalid_bases": amplitude_invalid,
        "min_total_physical_frames": int(basis_df["total_physical_frames"].min()),
        "max_total_physical_frames": int(basis_df["total_physical_frames"].max()),
    }
    (output_dir / "protocol_audit_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    lines = [
        "# Protocol Audit Report",
        "",
        "This report audits comparison mechanics only. It does not claim that a basis wins.",
        "",
        "## Scope",
        "",
        f"- Audited strict bases: {len(strict_rows)}",
        f"- Audited object rows: {len(object_df)}",
        f"- Reference periods: {', '.join(str(int(x)) for x in reference_periods)}",
        f"- Total physical frame range with reference overhead: {summary['min_total_physical_frames']} to {summary['max_total_physical_frames']}",
        "",
        "## Key Checks",
        "",
        "- `num_frames`, `num_coefficients`, `num_pixels`, `reference_frames`, and `total_physical_frames` are explicit in `protocol_audit.csv`.",
        "- Pairwise complementary bases report complement-sum error; complete paired bases should be near zero.",
        "- Throughput proxies are exposed as per-frame mean, sum, L2 norm, and energy statistics.",
        "- `random_gaussian` is included as a signed mathematical control and is labeled non-optical because it contains negative entries.",
        "- Object generation is documented as deterministic synthetic digit/shape/line images, not MNIST or natural images.",
        "",
        "## Files",
        "",
        "- `protocol_audit.csv`: basis/frame/reference/throughput audit.",
        "- `object_audit.csv`: object-family and image-statistics audit.",
        "- `seed_split_audit.csv`: seed and split conventions used by compact mechanism runners.",
        "- `protocol_audit_summary.json`: compact machine-readable summary.",
        "",
    ]
    (output_dir / "protocol_audit_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit protocol mechanics for measurement-basis comparisons.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "protocol_audit_r1")
    parser.add_argument("--objects", type=int, default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    mechanism = config.get("mechanism", {})
    image_size = int(mechanism.get("image_size", 32))
    num_pixels = int(mechanism.get("num_pixels", image_size * image_size))
    if num_pixels != image_size * image_size:
        raise ValueError("Protocol audit expects square images with num_pixels == image_size * image_size.")

    seed = int(config.get("seed", 20240708))
    reference_periods = [0] + [int(x) for x in mechanism.get("reference_periods", [2, 8, 32])]
    object_count = int(args.objects if args.objects is not None else mechanism.get("objects", 10))

    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    basis_rows: List[Dict[str, object]] = []
    for basis_name, kwargs, family in build_basis_specs(num_pixels, seed):
        basis_kwargs = dict(kwargs)
        basis_seed = int(basis_kwargs.pop("seed", seed))
        basis = make_basis(basis_name, num_pixels=num_pixels, seed=basis_seed, **basis_kwargs)
        basis_rows.extend(
            basis_audit_rows(
                basis=basis,
                family=family,
                requested_name=basis_name,
                seed=basis_seed,
                reference_periods=reference_periods,
            )
        )

    objects = make_synthetic_objects(object_count, image_size=image_size, seed=seed)
    object_rows = object_audit_rows(objects, image_size=image_size, seed=seed)
    seed_rows = seed_audit_rows(seed)

    basis_df = pd.DataFrame(basis_rows)
    object_df = pd.DataFrame(object_rows)
    seed_df = pd.DataFrame(seed_rows)

    basis_df.to_csv(output_dir / "protocol_audit.csv", index=False)
    object_df.to_csv(output_dir / "object_audit.csv", index=False)
    seed_df.to_csv(output_dir / "seed_split_audit.csv", index=False)
    write_report(output_dir, basis_df, object_df, seed_df, reference_periods)

    print("Protocol audit complete")
    print(f"wrote {output_dir / 'protocol_audit.csv'} rows={len(basis_df)}")
    print(f"wrote {output_dir / 'object_audit.csv'} rows={len(object_df)}")
    print(f"wrote {output_dir / 'seed_split_audit.csv'} rows={len(seed_df)}")


if __name__ == "__main__":
    main()
