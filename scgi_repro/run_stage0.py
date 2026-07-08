from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import pandas as pd
import torch
import yaml

from src.config_utils import load_config, project_root
from src.data_sim import simulate_scgi_dataset, train_val_split
from src.dgi import dgi_reconstruct
from src.metrics import bundle, cnr, normal_ks_test, slope_vs_index
from src.scgi_model import make_scgi_model
from src.train_scgi import analytic_gain_correct, correct_measurements, oracle_gain_correct, train_scgi
from src.ured import optimize_untrained


def try_plot_grid(rows, out_path: Path) -> None:
    try:
        from src.plotting import save_image_grid

        labels = [name for name, _img in rows]
        images = [img.detach().cpu().squeeze().numpy() if hasattr(img, "detach") else img for _name, img in rows]
        save_image_grid(out_path, images, labels=labels, columns=len(images), cell_size=96)
    except Exception:
        pass


def measurement_mse(a: torch.Tensor, b: torch.Tensor) -> float:
    return float(torch.mean((a.detach().float() - b.detach().float()) ** 2).cpu())


def validation_diagnostics(val, y_corr: torch.Tensor, y_oracle: torch.Tensor, y_analytic: torch.Tensor) -> tuple[pd.DataFrame, dict[str, float]]:
    rows = []
    for idx in range(int(val.b_static.shape[0])):
        row = {"sample": idx}
        for name, meas in [
            ("static", val.b_static[idx]),
            ("dynamic", val.r_dynamic[idx]),
            ("scgi", y_corr[idx]),
            ("analytic", y_analytic[idx]),
            ("oracle", y_oracle[idx]),
        ]:
            ks_d, ks_p = normal_ks_test(meas)
            row[f"{name}_ks_d"] = ks_d
            row[f"{name}_ks_p"] = ks_p
            row[f"{name}_slope"] = slope_vs_index(meas)
            row[f"{name}_mse_vs_static"] = 0.0 if name == "static" else measurement_mse(meas, val.b_static[idx])
        rows.append(row)
    frame = pd.DataFrame(rows)
    summary = {}
    for name in ["dynamic", "scgi", "analytic", "oracle"]:
        summary[f"{name}_ks_pass_rate"] = float((frame[f"{name}_ks_p"] > 0.05).mean())
        summary[f"{name}_slope_mean"] = float(frame[f"{name}_slope"].mean())
        summary[f"{name}_slope_std"] = float(frame[f"{name}_slope"].std(ddof=0))
        summary[f"{name}_mse_vs_static_mean"] = float(frame[f"{name}_mse_vs_static"].mean())
    return frame, summary


def write_acceptance(out_dir: Path, metrics: dict, val_summary: dict, skip_ured: bool) -> None:
    checks = [
        {
            "check": "dynamic_dgi_cnr_below_static",
            "target": "dynamic_dgi_cnr < static_dgi_cnr",
            "value": metrics["dynamic_dgi_cnr"],
            "threshold": metrics["static_dgi_cnr"],
            "passed": metrics["dynamic_dgi_cnr"] < metrics["static_dgi_cnr"],
        },
        {
            "check": "scgi_dgi_cnr_above_dynamic",
            "target": "scgi_dgi_cnr > dynamic_dgi_cnr",
            "value": metrics["scgi_dgi_cnr"],
            "threshold": metrics["dynamic_dgi_cnr"],
            "passed": metrics["scgi_dgi_cnr"] > metrics["dynamic_dgi_cnr"],
        },
        {
            "check": "scgi_dgi_cnr_ge_3",
            "target": "paper prompt threshold",
            "value": metrics["scgi_dgi_cnr"],
            "threshold": 3.0,
            "passed": metrics["scgi_dgi_cnr"] >= 3.0,
        },
        {
            "check": "static_dgi_psnr_gt_20",
            "target": "paper prompt sanity threshold",
            "value": metrics["static_dgi_psnr"],
            "threshold": 20.0,
            "passed": metrics["static_dgi_psnr"] > 20.0,
        },
        {
            "check": "sample_scgi_ks_p_gt_0_05",
            "target": "single-sample KS sanity",
            "value": metrics["scgi_dgi_ks_p"],
            "threshold": 0.05,
            "passed": metrics["scgi_dgi_ks_p"] > 0.05,
        },
        {
            "check": "val_scgi_ks_pass_rate_ge_0_9",
            "target": "Stage 2 prompt threshold",
            "value": val_summary["scgi_ks_pass_rate"],
            "threshold": 0.9,
            "passed": val_summary["scgi_ks_pass_rate"] >= 0.9,
        },
        {
            "check": "val_scgi_mse_below_dynamic",
            "target": "corrected measurements closer to static",
            "value": val_summary["scgi_mse_vs_static_mean"],
            "threshold": val_summary["dynamic_mse_vs_static_mean"],
            "passed": val_summary["scgi_mse_vs_static_mean"] < val_summary["dynamic_mse_vs_static_mean"],
        },
    ]
    if not skip_ured:
        checks.append(
            {
                "check": "ured_cnr_above_scgi",
                "target": "Stage 4 directionality",
                "value": metrics["scgi_ured_cnr"],
                "threshold": metrics["scgi_dgi_cnr"],
                "passed": metrics["scgi_ured_cnr"] > metrics["scgi_dgi_cnr"],
            }
        )
    pd.DataFrame(checks).to_csv(out_dir / "acceptance.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default=None)
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--tag", default=None, help="Optional result subdirectory suffix, e.g. debug_e80.")
    parser.add_argument("--skip-ured", action="store_true")
    parser.add_argument("--append-report", action="store_true", help="Append a short run block to REPORT.md.")
    args = parser.parse_args()

    root = project_root()
    cfg = load_config(root / "config.yaml", args.profile)
    active = cfg["active"]
    result_name = str(args.tag or cfg["profile"])
    out_dir = root / "results" / "stage_0" / result_name
    out_dir.mkdir(parents=True, exist_ok=True)

    data = simulate_scgi_dataset(cfg)
    train, val = train_val_split(data, int(active["train_samples"]))
    model = make_scgi_model(cfg).to(data.images.device)
    hist = train_scgi(
        model,
        train,
        val,
        epochs=int(args.epochs or active["scgi_epochs"]),
        batch_size=int(active["batch_size"]),
        lr=float(active["lr"]),
        gamma=float(active.get("gamma", cfg.get("scgi", {}).get("gamma", 1.0))),
    )
    y_corr = correct_measurements(model, val.r_dynamic, val.image_size)
    normalize_mode = str(cfg.get("data", {}).get("normalize", "max"))
    y_oracle = oracle_gain_correct(val.r_dynamic, val.y_factors, normalize_mode=normalize_mode)
    y_analytic, lambda_hat = analytic_gain_correct(val.r_dynamic, normalize_mode=normalize_mode)

    idx = 0
    target = val.images[idx]
    rec_static = dgi_reconstruct(val.b_static[idx], val.patterns, val.image_size)
    rec_dynamic = dgi_reconstruct(val.r_dynamic[idx], val.patterns, val.image_size)
    rec_scgi = dgi_reconstruct(y_corr[idx], val.patterns, val.image_size)
    rec_oracle = dgi_reconstruct(y_oracle[idx], val.patterns, val.image_size)
    rec_analytic = dgi_reconstruct(y_analytic[idx], val.patterns, val.image_size)

    rec_unn = rec_scgi
    rec_ured = rec_scgi
    if not args.skip_ured:
        rec_unn = optimize_untrained(rec_scgi, y_corr[idx], val.patterns, cfg, target=target, metric_fn=cnr, use_regularizer=False).image
        rec_ured = optimize_untrained(rec_scgi, y_corr[idx], val.patterns, cfg, target=target, metric_fn=cnr, use_regularizer=True).image

    metrics = {
        "profile": cfg["profile"],
        "device": str(data.images.device),
        "image_size": val.image_size,
        "num_patterns": int(val.patterns.shape[0]),
        "epochs": int(args.epochs or active["scgi_epochs"]),
        "train_loss_last": hist.train_loss[-1],
        "val_mse_last": hist.val_mse[-1],
        "slope_dynamic": slope_vs_index(val.r_dynamic[idx]),
        "slope_corrected": slope_vs_index(y_corr[idx]),
        "slope_oracle": slope_vs_index(y_oracle[idx]),
        "slope_analytic": slope_vs_index(y_analytic[idx]),
        "lambda_true": float(val.lambdas[idx].detach().cpu()),
        "lambda_analytic": float(lambda_hat[idx].detach().cpu()),
        "dynamic_static_mse": measurement_mse(val.r_dynamic[idx], val.b_static[idx]),
        "scgi_static_mse": measurement_mse(y_corr[idx], val.b_static[idx]),
        "oracle_static_mse": measurement_mse(y_oracle[idx], val.b_static[idx]),
        "analytic_static_mse": measurement_mse(y_analytic[idx], val.b_static[idx]),
    }
    for name, rec, meas in [
        ("static_dgi", rec_static, val.b_static[idx]),
        ("dynamic_dgi", rec_dynamic, val.r_dynamic[idx]),
        ("scgi_dgi", rec_scgi, y_corr[idx]),
        ("oracle_dgi", rec_oracle, y_oracle[idx]),
        ("analytic_dgi", rec_analytic, y_analytic[idx]),
        ("scgi_unn", rec_unn, y_corr[idx]),
        ("scgi_ured", rec_ured, y_corr[idx]),
    ]:
        b = bundle(rec, target, meas)
        metrics.update({f"{name}_{k}": v for k, v in b.__dict__.items()})
    metrics["ks_pass_corrected"] = metrics["scgi_dgi_ks_p"] > 0.05
    metrics["ks_pass_analytic"] = metrics["analytic_dgi_ks_p"] > 0.05
    val_diag, val_summary = validation_diagnostics(val, y_corr, y_oracle, y_analytic)
    metrics.update({f"val_{key}": value for key, value in val_summary.items()})

    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    with (out_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(metrics.keys()))
        writer.writeheader()
        writer.writerow(metrics)
    with (out_dir / "train_history.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["epoch", "train_loss", "val_mse"])
        writer.writeheader()
        for i, (tl, vm) in enumerate(zip(hist.train_loss, hist.val_mse), 1):
            writer.writerow({"epoch": i, "train_loss": tl, "val_mse": vm})
    val_diag.to_csv(out_dir / "val_diagnostics.csv", index=False)
    write_acceptance(out_dir, metrics, val_summary, args.skip_ured)
    with (out_dir / "config_snapshot.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)
    with (out_dir / "run_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "profile": cfg["profile"],
                "tag": result_name,
                "device": metrics["device"],
                "outputs": {
                    "metrics": "metrics.json",
                    "metrics_csv": "metrics.csv",
                    "train_history": "train_history.csv",
                    "val_diagnostics": "val_diagnostics.csv",
                    "acceptance": "acceptance.csv",
                    "checkpoint": "model_checkpoint.pt",
                    "figure": "stage0_recon_grid.png",
                },
                "acceptance_passed": bool(pd.read_csv(out_dir / "acceptance.csv")["passed"].all()),
            },
            f,
            indent=2,
        )
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "profile": cfg["profile"],
            "tag": result_name,
            "active_config": active,
            "scgi_config": cfg.get("scgi", {}),
            "metrics": metrics,
        },
        out_dir / "model_checkpoint.pt",
    )

    try_plot_grid(
        [
            ("target", target),
            ("static DGI", rec_static),
            ("dynamic DGI", rec_dynamic),
            ("SCGI", rec_scgi),
            ("analytic", rec_analytic),
            ("oracle", rec_oracle),
            ("SCGI-UNN", rec_unn),
            ("SCGI-URED", rec_ured),
        ],
        out_dir / "stage0_recon_grid.png",
    )

    if args.append_report:
        report = root / "REPORT.md"
        with report.open("a", encoding="utf-8") as f:
            f.write("\n## Stage 0 Run\n\n")
            f.write(f"- profile: `{cfg['profile']}`\n")
            f.write(f"- device: `{metrics['device']}`\n")
            f.write(f"- image size / patterns: `{metrics['image_size']}` / `{metrics['num_patterns']}`\n")
            f.write(f"- epochs: `{metrics['epochs']}`\n")
            f.write(f"- final train loss: `{metrics['train_loss_last']:.6g}`\n")
            f.write(f"- final val MSE: `{metrics['val_mse_last']:.6g}`\n")
            f.write(f"- CNR dynamic DGI -> SCGI -> URED: `{metrics['dynamic_dgi_cnr']:.3g}` -> `{metrics['scgi_dgi_cnr']:.3g}` -> `{metrics['scgi_ured_cnr']:.3g}`\n")
            f.write(f"- CNR analytic/oracle controls: `{metrics['analytic_dgi_cnr']:.3g}` / `{metrics['oracle_dgi_cnr']:.3g}`\n")
            f.write(f"- lambda true / analytic: `{metrics['lambda_true']:.6g}` / `{metrics['lambda_analytic']:.6g}`\n")
            f.write(f"- measurement MSE dynamic / SCGI / analytic / oracle vs static: `{metrics['dynamic_static_mse']:.3g}` / `{metrics['scgi_static_mse']:.3g}` / `{metrics['analytic_static_mse']:.3g}` / `{metrics['oracle_static_mse']:.3g}`\n")
            f.write(f"- corrected KS p-value: `{metrics['scgi_dgi_ks_p']:.3g}`\n")
            f.write(f"- validation SCGI KS pass rate: `{metrics['val_scgi_ks_pass_rate']:.3g}`\n")
            f.write(f"- result dir: `results/stage_0/{result_name}`\n")
            f.write(f"- figure: `results/stage_0/{result_name}/stage0_recon_grid.png`\n")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
