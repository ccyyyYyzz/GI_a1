from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from run_m4_agc_targeted import markdown_table
from src.config_utils import project_root


CONFIG_COLUMNS = [
    "steps",
    "lr",
    "beta",
    "xi",
    "x_step",
    "channels",
    "blocks",
    "residual_scale",
    "denoiser",
    "denoise_kernel",
    "nlm_h",
]


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def _label(path: Path) -> str:
    return path.name.replace("stage4_ured_sweep_", "").replace("_r1", "")


def audit_sweep(path: Path, apl_min_cnr: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    metrics = _read_csv(path / "ured_sweep_metrics.csv")
    traces_path = path / "ured_sweep_traces.csv"
    if traces_path.exists():
        traces = _read_csv(traces_path)
        trace_idx = traces.groupby(["config_id", "object"])["cnr"].idxmax()
        trace_best = traces.loc[trace_idx].copy()
        trace_best = trace_best.rename(columns={"cnr": "best_trace_cnr_from_trace", "step": "best_trace_step"})
        metrics = metrics.merge(
            trace_best[["config_id", "object", "best_trace_cnr_from_trace", "best_trace_step"]],
            on=["config_id", "object"],
            how="left",
        )
        metrics["best_trace_cnr_audited"] = metrics["best_trace_cnr_from_trace"].fillna(metrics["best_trace_cnr"])
    else:
        metrics["best_trace_step"] = pd.NA
        metrics["best_trace_cnr_audited"] = metrics["best_trace_cnr"]

    metrics["sweep"] = _label(path)
    metrics["sweep_dir"] = str(path)
    metrics["final_hits_apl_min"] = metrics["cnr"].astype(float) >= apl_min_cnr
    metrics["trace_hits_apl_min"] = metrics["best_trace_cnr_audited"].astype(float) >= apl_min_cnr

    rows: list[dict[str, object]] = []
    for (sweep, obj), group in metrics.groupby(["sweep", "object"], sort=True):
        final_row = group.sort_values("cnr", ascending=False).iloc[0]
        trace_row = group.sort_values("best_trace_cnr_audited", ascending=False).iloc[0]
        row: dict[str, object] = {
            "sweep": sweep,
            "object": obj,
            "num_configs": int(len(group)),
            "best_final_cnr": float(final_row["cnr"]),
            "best_final_config": str(final_row["config_id"]),
            "best_trace_cnr": float(trace_row["best_trace_cnr_audited"]),
            "best_trace_config": str(trace_row["config_id"]),
            "best_trace_step": int(trace_row["best_trace_step"]) if pd.notna(trace_row["best_trace_step"]) else "",
            "apl_min_cnr": apl_min_cnr,
            "final_hits_apl_min": bool(final_row["cnr"] >= apl_min_cnr),
            "trace_hits_apl_min": bool(trace_row["best_trace_cnr_audited"] >= apl_min_cnr),
        }
        for column in CONFIG_COLUMNS:
            if column in final_row:
                row[f"final_{column}"] = final_row[column]
            if column in trace_row:
                row[f"trace_{column}"] = trace_row[column]
        rows.append(row)
    return metrics, pd.DataFrame(rows)


def write_report(out_dir: Path, summary: pd.DataFrame, details: pd.DataFrame, apl_min_cnr: float) -> None:
    best_trace_by_object = (
        summary.sort_values(["object", "best_trace_cnr"], ascending=[True, False])
        .groupby("object", as_index=False)
        .first()
    )
    best_final_by_object = (
        summary.sort_values(["object", "best_final_cnr"], ascending=[True, False])
        .groupby("object", as_index=False)
        .first()
    )
    lines = [
        "# Stage 4 URED Trace Audit",
        "",
        f"APL URED minimum CNR gate used for this audit: `{apl_min_cnr:.2f}`.",
        "",
        "The audit separates final-output CNR from target-aware best-trace CNR.",
        "Best-trace values are diagnostic upper bounds because they use the ground",
        "truth target to choose a step; they are not deployable stopping rules.",
        "",
        "## Best Sweep/Object Results",
        "",
        markdown_table(
            summary[
                [
                    "sweep",
                    "object",
                    "num_configs",
                    "best_final_cnr",
                    "best_final_config",
                    "best_trace_cnr",
                    "best_trace_config",
                    "best_trace_step",
                    "trace_hits_apl_min",
                ]
            ]
        ),
        "",
        "## Best Final Output Per Object",
        "",
        markdown_table(
            best_final_by_object[
                [
                    "object",
                    "sweep",
                    "best_final_cnr",
                    "best_final_config",
                    "final_hits_apl_min",
                    "final_steps",
                    "final_nlm_h",
                ]
            ]
        ),
        "",
        "## Best Target-Aware Trace Per Object",
        "",
        markdown_table(
            best_trace_by_object[
                [
                    "object",
                    "sweep",
                    "best_trace_cnr",
                    "best_trace_config",
                    "best_trace_step",
                    "trace_hits_apl_min",
                ]
            ]
        ),
        "",
        "## Interpretation",
        "",
    ]
    if bool(best_trace_by_object["trace_hits_apl_min"].all()):
        lines.append("All objects have a target-aware trace point above the APL URED minimum.")
    else:
        misses = best_trace_by_object[~best_trace_by_object["trace_hits_apl_min"].astype(bool)]
        miss_text = ", ".join(f"{row.object} ({row.best_trace_cnr:.3g})" for row in misses.itertuples())
        lines.append(
            "At least one object remains below the APL URED minimum even with target-aware trace selection: "
            + miss_text
            + "."
        )
    lines.extend(
        [
            "The final-output CNR remains lower than target-aware trace peaks, so any",
            "paper-threshold claim still requires either a deployable stopping rule",
            "or a stronger URED/SCGI reconstruction path.",
            "",
        ]
    )
    out_dir.joinpath("stage4_trace_audit_report.md").write_text("\n".join(lines), encoding="utf-8")
    payload = {
        "apl_min_cnr": apl_min_cnr,
        "num_sweeps": int(summary["sweep"].nunique()) if len(summary) else 0,
        "num_detail_rows": int(len(details)),
        "all_objects_trace_hit_apl_min": bool(best_trace_by_object["trace_hits_apl_min"].all()) if len(best_trace_by_object) else False,
        "best_final_by_object": best_final_by_object.to_dict(orient="records"),
        "best_trace_by_object": best_trace_by_object.to_dict(orient="records"),
    }
    out_dir.joinpath("stage4_trace_audit_summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit Stage 4 URED sweeps with final and target-aware trace CNR.")
    parser.add_argument("--inputs", nargs="+", type=Path, required=True, help="Stage 4 sweep output directories.")
    parser.add_argument("--output-dir", type=Path, default=Path("results/stage4_trace_audit_r1"))
    parser.add_argument("--apl-min-cnr", type=float, default=10.43)
    args = parser.parse_args()

    root = project_root()
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    detail_frames: list[pd.DataFrame] = []
    summary_frames: list[pd.DataFrame] = []
    for raw_path in args.inputs:
        path = raw_path if raw_path.is_absolute() else root / raw_path
        details, summary = audit_sweep(path, args.apl_min_cnr)
        detail_frames.append(details)
        summary_frames.append(summary)
    details = pd.concat(detail_frames, ignore_index=True)
    summary = pd.concat(summary_frames, ignore_index=True).sort_values(["object", "best_trace_cnr"], ascending=[True, False])
    details.to_csv(out_dir / "stage4_trace_audit_details.csv", index=False)
    summary.to_csv(out_dir / "stage4_trace_audit_summary.csv", index=False)
    write_report(out_dir, summary, details, args.apl_min_cnr)
    print(f"wrote {out_dir}")


if __name__ == "__main__":
    main()
