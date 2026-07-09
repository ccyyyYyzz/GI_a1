from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from run_m4_agc_targeted import markdown_table
from run_stage3_tests import load_stage0_model, make_stage3_objects
from run_stage4_image_audit import _find_object_index, _row_to_ured_cfg, select_rows
from run_stage4_postprocess_audit import mask_metrics, minmax, otsu_threshold, torch_metrics
from src.config_utils import load_config, project_root
from src.data_sim import compute_static_measurements, dynamic_factors, generate_patterns, normalize_rows, seed_everything
from src.dgi import dgi_reconstruct, forward_project
from src.metrics import cnr
from src.nafnet import TinyNAFNet
from src.plotting import save_metrics_table
from src.train_scgi import correct_measurements
from src.ured import apply_denoiser, target_free_image_proxies


THRESHOLD_METHODS = [
    "raw_otsu_binary",
    "minmax_otsu_binary",
    "raw_mean_binary",
    "raw_mean_plus_std_binary",
]


def parse_names(text: str | None) -> list[str] | None:
    if text is None:
        return None
    names = [part.strip() for part in text.replace(",", " ").split() if part.strip()]
    return names or None


def object_names_from_audit(audit_dir: Path) -> list[str]:
    summary = pd.read_csv(audit_dir / "stage4_trace_audit_summary.csv")
    return sorted(summary["object"].dropna().astype(str).unique().tolist())


def threshold_images(image: np.ndarray) -> dict[str, tuple[np.ndarray, float]]:
    image = image.astype(np.float32)
    scaled = minmax(image).astype(np.float32)
    raw_otsu = otsu_threshold(image)
    scaled_otsu = otsu_threshold(scaled)
    mean_threshold = float(image.mean())
    mean_plus_std = float(image.mean() + image.std())
    return {
        "raw_otsu_binary": ((image >= raw_otsu).astype(np.float32), raw_otsu),
        "minmax_otsu_binary": ((scaled >= scaled_otsu).astype(np.float32), scaled_otsu),
        "raw_mean_binary": ((image >= mean_threshold).astype(np.float32), mean_threshold),
        "raw_mean_plus_std_binary": ((image >= mean_plus_std).astype(np.float32), mean_plus_std),
    }


def run_trace(
    *,
    coarse: torch.Tensor,
    y_corrected: torch.Tensor,
    patterns: torch.Tensor,
    cfg: dict,
    target: torch.Tensor,
    object_name: str,
    source_config: str,
) -> list[dict[str, object]]:
    ured = cfg.get("ured", {})
    active = cfg.get("active", {})
    steps = int(active.get("ured_steps", 50))
    lr = float(active.get("ured_lr", 0.001))
    beta = float(ured.get("beta", 0.5))
    xi = float(ured.get("xi", 0.5))
    x_step = float(ured.get("x_step", 0.5))
    net = TinyNAFNet(
        channels=int(ured.get("channels", 24)),
        blocks=int(ured.get("blocks", 3)),
        residual_scale=float(ured.get("residual_scale", 0.1)),
    ).to(coarse.device)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.StepLR(opt, step_size=50, gamma=0.9)
    inp = coarse.detach().reshape(1, 1, *coarse.shape[-2:])
    x = inp.clone().detach()
    u = torch.zeros_like(x)
    y = y_corrected.detach().reshape(1, -1)
    target_np = target.detach().float().cpu().squeeze().numpy()
    rows: list[dict[str, object]] = []
    for step in range(1, steps + 1):
        opt.zero_grad(set_to_none=True)
        out = net(inp)
        pred_y = forward_project(out, patterns)
        pred_y = pred_y / pred_y.amax(dim=1, keepdim=True).clamp_min(1e-8)
        data_loss = 0.5 * torch.mean((pred_y - y) ** 2)
        aug_loss = 0.5 * xi * torch.mean((x - out - u) ** 2)
        loss = data_loss + aug_loss
        loss.backward()
        opt.step()
        scheduler.step()
        with torch.no_grad():
            out = net(inp)
            denoiser_mse = 0.0
            if beta > 0:
                fx = apply_denoiser(x, ured)
                denoiser_mse = float(torch.mean((x - fx) ** 2).detach().cpu())
                x = x - x_step * (beta * (x - fx) + xi * (x - out - u))
            else:
                x = out.detach()
            u = u - x + out.detach()
            final = (x - u).clamp(0.0, 1.0)
        final_np = final.detach().float().cpu().squeeze().numpy()
        proxy_row = target_free_image_proxies(final)
        proxy_row.update(
            {
                "loss": float(loss.detach().cpu()),
                "proxy_data_loss": float(data_loss.detach().cpu()),
                "proxy_aug_loss": float(aug_loss.detach().cpu()),
                "proxy_denoiser_mse": denoiser_mse,
                "proxy_net_delta_mse": float(torch.mean((out.detach() - inp) ** 2).detach().cpu()),
                "proxy_dual_abs_mean": float(torch.mean(torch.abs(u)).detach().cpu()),
            }
        )
        continuous = torch_metrics(final_np, target_np)
        rows.append(
            {
                "object": object_name,
                "source_config": source_config,
                "step": step,
                "postprocess_method": "continuous",
                "target_free_threshold": True,
                "threshold": "",
                **continuous,
                **mask_metrics(final_np, target_np),
                **proxy_row,
            }
        )
        for method, (image, threshold) in threshold_images(final_np).items():
            rows.append(
                {
                    "object": object_name,
                    "source_config": source_config,
                    "step": step,
                    "postprocess_method": method,
                    "target_free_threshold": True,
                    "threshold": float(threshold),
                    **torch_metrics(image, target_np),
                    **mask_metrics(image, target_np),
                    **proxy_row,
                }
            )
    return rows


def setup_object_traces(args: argparse.Namespace) -> pd.DataFrame:
    root = project_root()
    cfg = load_config(root / "config.yaml", args.profile)
    if args.model_kind:
        cfg.setdefault("scgi", {})["model_kind"] = str(args.model_kind)
    active = cfg["active"]
    h = int(active["image_size"])
    n = int(active["num_patterns"])
    device = torch.device("cuda" if active.get("device") == "cuda" and torch.cuda.is_available() else "cpu")
    checkpoint = args.checkpoint if args.checkpoint.is_absolute() else root / args.checkpoint
    audit_dir = args.audit_dir if args.audit_dir.is_absolute() else root / args.audit_dir
    object_names = parse_names(args.object_names) or object_names_from_audit(audit_dir)
    generator = seed_everything(int(cfg.get("seed", 0)))
    model = load_stage0_model(root, cfg, checkpoint, device)
    patterns = generate_patterns(n, h, generator, cfg.get("data", {}).get("pattern_distribution", "uniform"), device=device)
    objects = make_stage3_objects(h)
    images = torch.stack([obj for _name, obj in objects], dim=0).unsqueeze(1).to(device)
    flat = images.reshape(images.shape[0], h * h)
    b_static = normalize_rows(
        compute_static_measurements(flat, patterns, int(active.get("measurement_chunk", 128))),
        cfg.get("data", {}).get("normalize", "max"),
    )
    factors, _lambdas = dynamic_factors(
        images.shape[0],
        n,
        float(active.get("lambda_min", cfg.get("data", {}).get("lambda_min", 0.9995))),
        float(active.get("lambda_max", cfg.get("data", {}).get("lambda_max", 1.0))),
        generator,
        device=device,
    )
    r_dynamic = normalize_rows(factors * b_static, cfg.get("data", {}).get("normalize", "max"))
    y_scgi = correct_measurements(model, r_dynamic, h)
    rows: list[dict[str, object]] = []
    for object_name in object_names:
        _final_row, trace_row = select_rows(audit_dir, object_name)
        object_index = _find_object_index(objects, object_name)
        init_seed = int(trace_row.get("init_seed", int(cfg.get("seed", 0))))
        seed_everything(init_seed)
        run_cfg = _row_to_ured_cfg(cfg, trace_row, steps=int(trace_row["steps"]))
        source_config = f"{trace_row['sweep']}/{trace_row['config_id']}"
        coarse = dgi_reconstruct(y_scgi[object_index], patterns, h)
        rows.extend(
            run_trace(
                coarse=coarse,
                y_corrected=y_scgi[object_index],
                patterns=patterns,
                cfg=run_cfg,
                target=images[object_index],
                object_name=object_name,
                source_config=source_config,
            )
        )
    return pd.DataFrame(rows)


def select_step(group: pd.DataFrame, rule: str) -> pd.Series:
    step_frame = group.drop_duplicates("step").copy()
    if rule.startswith("fixed_step_"):
        requested = int(rule.replace("fixed_step_", ""))
        step_frame["distance"] = (step_frame["step"].astype(int) - requested).abs()
        selected_step = int(step_frame.sort_values(["distance", "step"]).iloc[0]["step"])
        return group[group["step"].astype(int) == selected_step].iloc[0]
    if rule == "final_step":
        selected_step = int(step_frame["step"].astype(int).max())
        return group[group["step"].astype(int) == selected_step].iloc[0]
    if rule == "min_loss":
        selected_step = int(step_frame.sort_values("loss", ascending=True).iloc[0]["step"])
        return group[group["step"].astype(int) == selected_step].iloc[0]
    direction, column = rule.split("_", 1)
    ascending = direction == "min"
    selected_step = int(step_frame.sort_values(column, ascending=ascending).iloc[0]["step"])
    return group[group["step"].astype(int) == selected_step].iloc[0]


def analyze_rules(metrics: pd.DataFrame, apl_min_cnr: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    proxy_columns = [
        "proxy_mean",
        "proxy_std",
        "proxy_min",
        "proxy_max",
        "proxy_range",
        "proxy_tv_l1",
        "proxy_roughness_l2",
        "proxy_otsu_score",
        "proxy_otsu_threshold",
        "proxy_otsu_fg_fraction",
        "proxy_hist_entropy",
        "proxy_data_loss",
        "proxy_aug_loss",
        "proxy_denoiser_mse",
        "proxy_net_delta_mse",
        "proxy_dual_abs_mean",
    ]
    rules = ["final_step", "min_loss"]
    fixed_steps = sorted(set([25, 36, 40, 50, 64, 75, 100, 117, 125, 150, 175, 200]))
    rules.extend(f"fixed_step_{step}" for step in fixed_steps)
    for column in proxy_columns:
        rules.append(f"min_{column}")
        rules.append(f"max_{column}")
    details: list[dict[str, object]] = []
    thresholded = metrics[metrics["postprocess_method"].isin(THRESHOLD_METHODS)].copy()
    for (method, object_name), group in thresholded.groupby(["postprocess_method", "object"]):
        peak_row = group.sort_values("cnr", ascending=False).iloc[0]
        for rule in rules:
            selected = select_step(group, rule)
            details.append(
                {
                    "postprocess_method": method,
                    "object": object_name,
                    "source_config": selected["source_config"],
                    "rule": rule,
                    "selected_step": int(selected["step"]),
                    "selected_cnr": float(selected["cnr"]),
                    "selected_psnr": float(selected["psnr"]),
                    "selected_ssim": float(selected["ssim"]),
                    "selected_iou": float(selected["iou"]),
                    "hits_apl_min": bool(float(selected["cnr"]) >= float(apl_min_cnr)),
                    "peak_step": int(peak_row["step"]),
                    "peak_cnr": float(peak_row["cnr"]),
                    "regret_to_peak": float(peak_row["cnr"]) - float(selected["cnr"]),
                }
            )
    detail_frame = pd.DataFrame(details)
    summary = (
        detail_frame.groupby(["postprocess_method", "rule"])
        .agg(
            observations=("object", "count"),
            mean_selected_cnr=("selected_cnr", "mean"),
            min_selected_cnr=("selected_cnr", "min"),
            all_hit_apl_min=("hits_apl_min", "all"),
            mean_regret_to_peak=("regret_to_peak", "mean"),
            max_regret_to_peak=("regret_to_peak", "max"),
            mean_selected_step=("selected_step", "mean"),
        )
        .reset_index()
        .sort_values(["all_hit_apl_min", "min_selected_cnr", "mean_selected_cnr"], ascending=[False, False, False])
    )
    return detail_frame, summary


def write_report(out_dir: Path, summary: pd.DataFrame, details: pd.DataFrame, payload: dict[str, object]) -> None:
    top = summary.head(12).copy()
    for column in ["mean_selected_cnr", "min_selected_cnr", "mean_regret_to_peak", "max_regret_to_peak", "mean_selected_step"]:
        top[column] = top[column].map(lambda value: f"{float(value):.3f}")
    all_hit = summary[summary["all_hit_apl_min"].astype(bool)]
    lines = [
        "# Stage 4 Thresholded Trace Stop-Rule Audit",
        "",
        f"APL URED minimum CNR gate: `{payload['apl_min_cnr']:.2f}`.",
        f"Metric rows: `{payload['metric_rows']}`; stop-rule rows: `{payload['detail_rows']}`.",
        "",
        "## Top Stop Rules",
        "",
        markdown_table(top),
        "",
        "## Interpretation",
        "",
    ]
    if len(all_hit):
        best = all_hit.iloc[0]
        lines.append(
            "At least one fully target-free rule/method combination clears the APL gate on all audited objects: "
            f"`{best['postprocess_method']} + {best['rule']}` has minimum CNR `{float(best['min_selected_cnr']):.3f}`."
        )
    else:
        best = summary.iloc[0]
        lines.append(
            "No audited fully target-free rule/method combination clears the APL gate on all objects. "
            f"The strongest combination is `{best['postprocess_method']} + {best['rule']}` with minimum CNR "
            f"`{float(best['min_selected_cnr']):.3f}`."
        )
    lines.extend(
        [
            "This audit uses the same best-trace configurations identified earlier, but the step selection and thresholding rules are target-free.",
            "Fixed-step rules select the nearest available recorded step; for shorter traces this is the final recorded step.",
            "It should be read as a deployable-stopping diagnostic, not as a replacement for the original continuous URED protocol.",
            "",
        ]
    )
    (out_dir / "stage4_threshold_trace_audit_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit target-free stopping rules for thresholded Stage 4 URED traces.")
    parser.add_argument("--profile", default="full")
    parser.add_argument("--checkpoint", type=Path, default=Path("results/colab_imports/pro2_full_exp_residual_e2_r1/artifacts/model_checkpoint.pt"))
    parser.add_argument("--model-kind", default="exponential_residual_unet")
    parser.add_argument("--audit-dir", type=Path, default=Path("results/stage4_trace_audit_r3"))
    parser.add_argument("--object-names", default=None)
    parser.add_argument("--output-dir", type=Path, default=Path("results/stage4_threshold_trace_audit_r1"))
    parser.add_argument("--apl-min-cnr", type=float, default=10.43)
    args = parser.parse_args()

    root = project_root()
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics = setup_object_traces(args)
    metrics.to_csv(out_dir / "stage4_threshold_trace_metrics.csv", index=False)
    details, summary = analyze_rules(metrics, float(args.apl_min_cnr))
    details.to_csv(out_dir / "stage4_threshold_trace_stop_rule_details.csv", index=False)
    summary.to_csv(out_dir / "stage4_threshold_trace_stop_rule_summary.csv", index=False)
    all_hit = summary[summary["all_hit_apl_min"].astype(bool)]
    payload = {
        "apl_min_cnr": float(args.apl_min_cnr),
        "metric_rows": int(len(metrics)),
        "detail_rows": int(len(details)),
        "summary_rows": int(len(summary)),
        "objects": sorted(metrics["object"].dropna().astype(str).unique().tolist()),
        "all_hit_rule_count": int(len(all_hit)),
        "best_all_hit_rule": all_hit.iloc[0].to_dict() if len(all_hit) else None,
        "best_overall_rule": summary.iloc[0].to_dict(),
    }
    (out_dir / "stage4_threshold_trace_audit_summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    save_metrics_table(
        out_dir / "stage4_threshold_trace_stop_rule_table.png",
        summary.head(16),
        title="Stage 4 thresholded trace stop rules",
        max_rows=16,
    )
    write_report(out_dir, summary, details, payload)
    print(f"wrote {out_dir}")


if __name__ == "__main__":
    main()
