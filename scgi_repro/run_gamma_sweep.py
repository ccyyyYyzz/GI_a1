from __future__ import annotations

import argparse
import csv
from pathlib import Path

from src.config_utils import load_config, project_root
from src.data_sim import simulate_scgi_dataset, train_val_split
from src.dgi import dgi_reconstruct
from src.metrics import bundle, normal_ks_test, slope_vs_index
from src.scgi_model import make_scgi_model
from src.train_scgi import analytic_gain_correct, correct_measurements, oracle_gain_correct, train_scgi


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a compact SCGI gamma sweep.")
    parser.add_argument("--profile", default="smoke")
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    root = project_root()
    cfg = load_config(root / "config.yaml", args.profile)
    gammas = [float(x) for x in cfg.get("scgi", {}).get("gamma_sweep", [0.0, 0.1, 1.0, 10.0])]
    out = args.output or (root / "results" / "stage_0" / "gamma_sweep.csv")
    out.parent.mkdir(parents=True, exist_ok=True)

    data = simulate_scgi_dataset(cfg)
    train, val = train_val_split(data, int(cfg["active"]["train_samples"]))
    normalize_mode = str(cfg.get("data", {}).get("normalize", "max"))
    target = val.images[0]
    rec_dynamic = dgi_reconstruct(val.r_dynamic[0], val.patterns, val.image_size)
    y_oracle = oracle_gain_correct(val.r_dynamic, val.y_factors, normalize_mode=normalize_mode)
    y_analytic, lambda_hat = analytic_gain_correct(val.r_dynamic, normalize_mode=normalize_mode)
    rec_oracle = dgi_reconstruct(y_oracle[0], val.patterns, val.image_size)
    rec_analytic = dgi_reconstruct(y_analytic[0], val.patterns, val.image_size)
    dynamic_metrics = bundle(rec_dynamic, target, val.r_dynamic[0])
    oracle_metrics = bundle(rec_oracle, target, y_oracle[0])
    analytic_metrics = bundle(rec_analytic, target, y_analytic[0])
    rows = []
    for gamma in gammas:
        model = make_scgi_model(cfg).to(data.images.device)
        hist = train_scgi(
            model,
            train,
            val,
            epochs=int(args.epochs or cfg["active"]["scgi_epochs"]),
            batch_size=int(cfg["active"]["batch_size"]),
            lr=float(cfg["active"]["lr"]),
            gamma=gamma,
        )
        y = correct_measurements(model, val.r_dynamic, val.image_size)
        rec_scgi = dgi_reconstruct(y[0], val.patterns, val.image_size)
        scgi_metrics = bundle(rec_scgi, target, y[0])
        ks_d, ks_p = normal_ks_test(y[0])
        rows.append(
            {
                "profile": cfg["profile"],
                "gamma": gamma,
                "epochs": int(args.epochs or cfg["active"]["scgi_epochs"]),
                "train_loss_last": hist.train_loss[-1],
                "val_mse_last": hist.val_mse[-1],
                "slope_dynamic": slope_vs_index(val.r_dynamic[0]),
                "slope_corrected": slope_vs_index(y[0]),
                "ks_d_corrected": ks_d,
                "ks_p_corrected": ks_p,
                "dynamic_cnr": dynamic_metrics.cnr,
                "dynamic_psnr": dynamic_metrics.psnr,
                "dynamic_ssim": dynamic_metrics.ssim,
                "scgi_cnr": scgi_metrics.cnr,
                "scgi_psnr": scgi_metrics.psnr,
                "scgi_ssim": scgi_metrics.ssim,
                "scgi_ks_p": scgi_metrics.ks_p,
                "analytic_cnr": analytic_metrics.cnr,
                "analytic_psnr": analytic_metrics.psnr,
                "analytic_ssim": analytic_metrics.ssim,
                "analytic_ks_p": analytic_metrics.ks_p,
                "oracle_cnr": oracle_metrics.cnr,
                "oracle_psnr": oracle_metrics.psnr,
                "oracle_ssim": oracle_metrics.ssim,
                "oracle_ks_p": oracle_metrics.ks_p,
                "lambda_analytic": float(lambda_hat[0].detach().cpu()),
            }
        )

    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
