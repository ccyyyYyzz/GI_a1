from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import pandas as pd

from run_m4_agc_targeted import markdown_table
from src.config_utils import project_root
from src.plotting import save_metrics_table


def _read(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def build_delta_summary(summary: pd.DataFrame) -> pd.DataFrame:
    index_columns = ["rho", "correction"]
    if "sigma_a" in summary.columns:
        index_columns.insert(1, "sigma_a")
    pivot = summary.pivot_table(
        index=index_columns,
        columns="variant",
        values="psnr_mean",
        aggfunc="mean",
    ).reset_index()
    variant_columns = [column for column in pivot.columns if column not in set(index_columns)]
    rows = []
    for _, row in pivot.iterrows():
        variant_values = {
            str(variant): float(row[variant])
            for variant in variant_columns
            if pd.notna(row[variant])
        }
        ordered = variant_values.get("hadamard_ordered")
        srht = variant_values.get("srht_full")
        sign = variant_values.get("sign_only")
        best_variant = max(variant_values, key=variant_values.get)
        best_value = variant_values[best_variant]
        alternatives = {
            variant: value
            for variant, value in variant_values.items()
            if variant != "hadamard_ordered"
        }
        best_alternative = max(alternatives, key=alternatives.get) if alternatives else None
        best_alternative_value = alternatives[best_alternative] if best_alternative else math.nan
        record = {
            "rho": float(row["rho"]),
            **({"sigma_a": float(row["sigma_a"])} if "sigma_a" in index_columns else {}),
            "correction": str(row["correction"]),
            "srht_minus_ordered_db": srht - ordered
            if srht is not None and ordered is not None
            else math.nan,
            "srht_minus_sign_only_db": srht - sign
            if srht is not None and sign is not None
            else math.nan,
            "srht_gap_to_best_ablation_db": srht - best_value if srht is not None else math.nan,
            "best_ablation": best_variant,
            "best_ablation_psnr": best_value,
            "best_alternative": best_alternative,
            "best_alternative_psnr": best_alternative_value,
            "best_alternative_minus_ordered_db": best_alternative_value - ordered
            if best_alternative is not None and ordered is not None
            else math.nan,
        }
        for variant in variant_columns:
            record[f"{variant}_psnr"] = variant_values.get(str(variant), math.nan)
        rows.append(record)
    return pd.DataFrame(rows)


def write_report(out_dir: Path, raw: pd.DataFrame, summary: pd.DataFrame, deltas: pd.DataFrame) -> None:
    non_oracle_corrections = ["agc", "none", "scgi_proxy", "pairwise"]
    fast = deltas[(deltas["rho"] >= 1.0) & (deltas["correction"].isin(non_oracle_corrections))]
    slow_pairwise = deltas[(deltas["rho"] == deltas["rho"].min()) & (deltas["correction"] == "pairwise")]
    oracle = summary[summary["correction"] == "oracle"]
    payload = {
        "raw_rows": int(len(raw)),
        "summary_rows": int(len(summary)),
        "variants": sorted(str(v) for v in raw["variant"].unique()),
        "rho_values": sorted(float(v) for v in raw["rho"].unique()),
        "sigma_a_values": sorted(float(v) for v in raw["sigma_a"].unique()),
        "oracle_min_psnr": float(oracle["psnr_mean"].min()) if len(oracle) else None,
        "fast_srht_minus_ordered_min_db": float(fast["srht_minus_ordered_db"].min()) if len(fast) else None,
        "fast_srht_minus_ordered_max_db": float(fast["srht_minus_ordered_db"].max()) if len(fast) else None,
        "fast_srht_gap_to_best_min_db": float(fast["srht_gap_to_best_ablation_db"].min()) if len(fast) else None,
        "fast_best_alternative_minus_ordered_max_db": float(fast["best_alternative_minus_ordered_db"].max())
        if len(fast)
        else None,
        "fast_best_alternative_minus_ordered_min_db": float(fast["best_alternative_minus_ordered_db"].min())
        if len(fast)
        else None,
        "fast_best_alternatives": sorted(str(v) for v in fast["best_alternative"].dropna().unique()),
        "slow_pairwise_srht_minus_ordered_db": float(slow_pairwise["srht_minus_ordered_db"].iloc[0]) if len(slow_pairwise) else None,
    }
    (out_dir / "m3_srht_audit_summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    key_table = deltas[
        (deltas["correction"].isin(non_oracle_corrections))
        & (deltas["rho"].isin([0.001, 1.0, 10.0]))
    ].copy()
    desired_columns = [
        "rho",
        "sigma_a",
        "correction",
        "hadamard_ordered_psnr",
        "sign_only_psnr",
        "sign_time_interleave_psnr",
        "sign_block_shuffle_psnr",
        "srht_full_psnr",
        "srht_minus_ordered_db",
        "best_alternative_minus_ordered_db",
        "best_alternative",
        "best_ablation",
    ]
    key_table = key_table[[column for column in desired_columns if column in key_table.columns]]
    for column in [
        column
        for column in key_table.columns
        if column not in {"correction", "best_alternative", "best_ablation"}
    ]:
        key_table[column] = key_table[column].map(lambda value: "" if pd.isna(value) else f"{float(value):.3f}")
    lines = [
        "# M3 SRHT Ablation Audit",
        "",
        f"Raw rows: `{payload['raw_rows']}`; summary rows: `{payload['summary_rows']}`.",
        f"Variants: `{payload['variants']}`.",
        f"Rho values: `{payload['rho_values']}`; sigma_a values: `{payload['sigma_a_values']}`.",
        "",
        "## Key Rows",
        "",
        markdown_table(key_table),
        "",
        "## Interpretation",
        "",
        f"Oracle correction reaches minimum mean PSNR `{payload['oracle_min_psnr']:.3f}`, confirming the ablation variants are information-preserving under true gain correction.",
        (
            "The prompt-level constructive SRHT threshold is not met in this run: "
            f"for rho>=1 and non-oracle corrections, srht_full minus ordered Hadamard ranges from "
            f"`{payload['fast_srht_minus_ordered_min_db']:.3f}` to `{payload['fast_srht_minus_ordered_max_db']:.3f}` dB, not the requested >=3 dB advantage."
        ),
        (
            "The fallback alternatives are summarized by best_alternative_minus_ordered_db. "
            f"Across fast non-oracle cells this ranges from `{payload['fast_best_alternative_minus_ordered_min_db']:.3f}` "
            f"to `{payload['fast_best_alternative_minus_ordered_max_db']:.3f}` dB, with best alternatives "
            f"`{payload['fast_best_alternatives']}`."
        ),
        (
            "The best ablation is often a signed deterministic ordering rather than full SRHT, so the current evidence supports "
            "diagonal sign randomization and paired normalization more strongly than unrestricted row permutation."
        ),
        "M3 should remain partial until a broader protocol shows a robust SRHT/interleaving advantage or the manuscript reframes the result as an ablation-informed design rule.",
        "",
    ]
    (out_dir / "m3_srht_audit_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit M3 SRHT ablation outputs against constructive-method gates.")
    parser.add_argument("--input-dir", type=Path, default=Path("results/srht_m3_protocol_o10s5_highrho_r1"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/srht_m3_audit_highrho_r1"))
    args = parser.parse_args()

    root = project_root()
    input_dir = args.input_dir if args.input_dir.is_absolute() else root / args.input_dir
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = _read(input_dir / "srht_ablation.csv")
    summary = _read(input_dir / "srht_ablation_summary.csv")
    deltas = build_delta_summary(summary)
    deltas.to_csv(out_dir / "m3_srht_delta_summary.csv", index=False)
    save_metrics_table(
        out_dir / "m3_srht_delta_table.png",
        deltas[
            (deltas["correction"].isin(["agc", "none", "scgi_proxy", "pairwise"]))
            & (deltas["rho"].isin([0.001, 1.0, 10.0]))
        ][
            [
                "rho",
                "correction",
                "srht_minus_ordered_db",
                "best_alternative_minus_ordered_db",
                "srht_gap_to_best_ablation_db",
                "best_ablation",
            ]
        ],
        title="M3 SRHT ablation deltas",
        max_rows=20,
    )
    write_report(out_dir, raw, summary, deltas)
    print(f"wrote {out_dir}")


if __name__ == "__main__":
    main()
