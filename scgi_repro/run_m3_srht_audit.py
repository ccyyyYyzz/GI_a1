from __future__ import annotations

import argparse
import json
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
    pivot = summary.pivot_table(
        index=["rho", "correction"],
        columns="variant",
        values="psnr_mean",
        aggfunc="mean",
    ).reset_index()
    rows = []
    for row in pivot.itertuples(index=False):
        record = row._asdict()
        srht = float(record.get("srht_full"))
        ordered = float(record.get("hadamard_ordered"))
        perm = float(record.get("perm_only"))
        sign = float(record.get("sign_only"))
        best_ablation = max(ordered, perm, sign, srht)
        rows.append(
            {
                "rho": float(record["rho"]),
                "correction": str(record["correction"]),
                "hadamard_ordered_psnr": ordered,
                "perm_only_psnr": perm,
                "sign_only_psnr": sign,
                "srht_full_psnr": srht,
                "srht_minus_ordered_db": srht - ordered,
                "srht_minus_sign_only_db": srht - sign,
                "srht_gap_to_best_ablation_db": srht - best_ablation,
                "best_ablation": (
                    "hadamard_ordered"
                    if best_ablation == ordered
                    else "perm_only"
                    if best_ablation == perm
                    else "sign_only"
                    if best_ablation == sign
                    else "srht_full"
                ),
            }
        )
    return pd.DataFrame(rows)


def write_report(out_dir: Path, raw: pd.DataFrame, summary: pd.DataFrame, deltas: pd.DataFrame) -> None:
    fast = deltas[(deltas["rho"] >= 1.0) & (deltas["correction"].isin(["agc", "none", "pairwise"]))]
    slow_pairwise = deltas[(deltas["rho"] == deltas["rho"].min()) & (deltas["correction"] == "pairwise")]
    oracle = summary[summary["correction"] == "oracle"]
    payload = {
        "raw_rows": int(len(raw)),
        "summary_rows": int(len(summary)),
        "rho_values": sorted(float(v) for v in raw["rho"].unique()),
        "sigma_a_values": sorted(float(v) for v in raw["sigma_a"].unique()),
        "oracle_min_psnr": float(oracle["psnr_mean"].min()) if len(oracle) else None,
        "fast_srht_minus_ordered_min_db": float(fast["srht_minus_ordered_db"].min()) if len(fast) else None,
        "fast_srht_minus_ordered_max_db": float(fast["srht_minus_ordered_db"].max()) if len(fast) else None,
        "fast_srht_gap_to_best_min_db": float(fast["srht_gap_to_best_ablation_db"].min()) if len(fast) else None,
        "slow_pairwise_srht_minus_ordered_db": float(slow_pairwise["srht_minus_ordered_db"].iloc[0]) if len(slow_pairwise) else None,
    }
    (out_dir / "m3_srht_audit_summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    key_table = deltas[
        (deltas["correction"].isin(["agc", "pairwise", "none"]))
        & (deltas["rho"].isin([0.001, 1.0, 10.0]))
    ][
        [
            "rho",
            "correction",
            "hadamard_ordered_psnr",
            "sign_only_psnr",
            "srht_full_psnr",
            "srht_minus_ordered_db",
            "best_ablation",
        ]
    ].copy()
    for column in [
        "hadamard_ordered_psnr",
        "sign_only_psnr",
        "srht_full_psnr",
        "srht_minus_ordered_db",
    ]:
        key_table[column] = key_table[column].map(lambda value: f"{float(value):.3f}")
    lines = [
        "# M3 SRHT Ablation Audit",
        "",
        f"Raw rows: `{payload['raw_rows']}`; summary rows: `{payload['summary_rows']}`.",
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
            "The best ablation is often sign_only rather than srht_full, so the current evidence supports "
            "the usefulness of diagonal sign randomization but does not prove that adding row permutation is beneficial under this protocol."
        ),
        "M3 should remain partial until a broader protocol shows a robust SRHT advantage or the manuscript reframes the result as an ablation-informed design rule.",
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
            (deltas["correction"].isin(["agc", "pairwise", "none"]))
            & (deltas["rho"].isin([0.001, 1.0, 10.0]))
        ][["rho", "correction", "srht_minus_ordered_db", "srht_gap_to_best_ablation_db", "best_ablation"]],
        title="M3 SRHT ablation deltas",
        max_rows=20,
    )
    write_report(out_dir, raw, summary, deltas)
    print(f"wrote {out_dir}")


if __name__ == "__main__":
    main()
