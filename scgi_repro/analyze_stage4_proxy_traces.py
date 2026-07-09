from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def select_row(group: pd.DataFrame, rule: str) -> pd.Series:
    if rule == "final_step":
        return group.loc[group["step"].idxmax()]
    if rule.startswith("fixed_step_"):
        target_step = int(rule.rsplit("_", 1)[1])
        eligible = group[group["step"] <= target_step]
        if len(eligible) == 0:
            eligible = group
        return eligible.loc[eligible["step"].idxmax()]
    if rule.startswith("min_"):
        column = rule[4:]
        return group.loc[group[column].idxmin()]
    if rule.startswith("max_"):
        column = rule[4:]
        return group.loc[group[column].idxmax()]
    if rule == "loss_plateau_10_1pct":
        ordered = group.sort_values("step").reset_index(drop=True)
        losses = ordered["loss"].astype(float)
        for idx in range(10, len(ordered)):
            window = losses.iloc[idx - 9 : idx + 1]
            rel_span = (window.max() - window.min()) / max(abs(float(window.iloc[0])), 1.0e-8)
            if rel_span < 0.01:
                return ordered.iloc[idx]
        return ordered.iloc[-1]
    raise ValueError(f"Unknown selection rule {rule!r}")


def summarize_stop_rules(traces: pd.DataFrame, rules: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    details = []
    group_cols = ["config_id", "object", "object_index"]
    for group_key, group in traces.groupby(group_cols, sort=False):
        peak = group.loc[group["cnr"].idxmax()]
        final = group.loc[group["step"].idxmax()]
        for rule in rules:
            selected = select_row(group, rule)
            details.append(
                {
                    "config_id": group_key[0],
                    "object": group_key[1],
                    "object_index": group_key[2],
                    "rule": rule,
                    "selected_step": int(selected["step"]),
                    "selected_cnr": float(selected["cnr"]),
                    "peak_step": int(peak["step"]),
                    "peak_cnr": float(peak["cnr"]),
                    "final_cnr": float(final["cnr"]),
                    "regret_to_peak": float(peak["cnr"] - selected["cnr"]),
                    "improvement_over_final": float(selected["cnr"] - final["cnr"]),
                }
            )
    detail_df = pd.DataFrame(details)
    summary_df = (
        detail_df.groupby("rule", as_index=False)
        .agg(
            observations=("selected_cnr", "count"),
            mean_selected_cnr=("selected_cnr", "mean"),
            min_selected_cnr=("selected_cnr", "min"),
            mean_regret_to_peak=("regret_to_peak", "mean"),
            max_regret_to_peak=("regret_to_peak", "max"),
            mean_improvement_over_final=("improvement_over_final", "mean"),
            min_improvement_over_final=("improvement_over_final", "min"),
            mean_selected_step=("selected_step", "mean"),
        )
        .sort_values(["min_selected_cnr", "mean_selected_cnr"], ascending=False)
    )
    return detail_df, summary_df


def summarize_correlations(traces: pd.DataFrame, proxy_columns: list[str]) -> pd.DataFrame:
    rows = []
    for column in proxy_columns + ["loss"]:
        group_pearson = []
        group_spearman = []
        for _group_key, group in traces.groupby(["config_id", "object", "object_index"], sort=False):
            if group[column].nunique(dropna=True) <= 1:
                continue
            group_pearson.append(float(group[["cnr", column]].corr(method="pearson").iloc[0, 1]))
            group_spearman.append(float(group[["cnr", column]].corr(method="spearman").iloc[0, 1]))
        global_pearson = float(traces[["cnr", column]].corr(method="pearson").iloc[0, 1])
        global_spearman = float(traces[["cnr", column]].corr(method="spearman").iloc[0, 1])
        rows.append(
            {
                "proxy": column,
                "global_pearson": global_pearson,
                "global_spearman": global_spearman,
                "mean_group_pearson": sum(group_pearson) / len(group_pearson) if group_pearson else float("nan"),
                "mean_group_spearman": sum(group_spearman) / len(group_spearman) if group_spearman else float("nan"),
                "groups": len(group_pearson),
            }
        )
    return pd.DataFrame(rows).sort_values("mean_group_spearman", ascending=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit target-free Stage 4 URED proxy trace stopping rules.")
    parser.add_argument("--trace-csv", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    traces = pd.read_csv(args.trace_csv)
    required = {"config_id", "object", "object_index", "step", "loss", "cnr"}
    missing = required.difference(traces.columns)
    if missing:
        raise ValueError(f"Trace CSV is missing required columns: {sorted(missing)}")
    proxy_columns = [column for column in traces.columns if column.startswith("proxy_")]
    if not proxy_columns:
        raise ValueError("Trace CSV has no proxy_* columns.")

    rules = [
        "final_step",
        "fixed_step_25",
        "fixed_step_50",
        "fixed_step_75",
        "fixed_step_100",
        "fixed_step_125",
        "fixed_step_150",
        "fixed_step_175",
        "min_loss",
        "loss_plateau_10_1pct",
    ]
    rules.extend(f"min_{column}" for column in proxy_columns)
    rules.extend(f"max_{column}" for column in proxy_columns)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    detail_df, summary_df = summarize_stop_rules(traces, rules)
    corr_df = summarize_correlations(traces, proxy_columns)

    detail_df.to_csv(args.output_dir / "proxy_stop_rule_details.csv", index=False)
    summary_df.to_csv(args.output_dir / "proxy_stop_rule_summary.csv", index=False)
    corr_df.to_csv(args.output_dir / "proxy_correlation_summary.csv", index=False)
    payload = {
        "trace_csv": str(args.trace_csv),
        "rows": int(len(traces)),
        "groups": int(traces.groupby(["config_id", "object", "object_index"]).ngroups),
        "proxy_columns": proxy_columns,
        "best_min_cnr_rule": summary_df.iloc[0].to_dict() if len(summary_df) else {},
        "best_mean_group_spearman_proxy": corr_df.iloc[0].to_dict() if len(corr_df) else {},
    }
    (args.output_dir / "proxy_analysis_summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
