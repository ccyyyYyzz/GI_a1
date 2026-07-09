from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import torch
from torch.utils.data import DataLoader, TensorDataset, random_split

from run_mechanism_m1 import make_synthetic_objects
from src.basis import basis_frame_budget, make_basis
from src.config_utils import load_config, project_root
from src.mechanisms import make_multiplicative_channel, simulate_channel_measurements
from src.run_progress import write_json_atomic
from src.scgi_model import make_scgi_model
from src.train_scgi import as_images, correct_measurements_padded


def parse_float_list(value: str | None, default: list[float]) -> list[float]:
    if value is None or not str(value).strip():
        return default
    return [float(part) for part in str(value).replace(",", " ").split() if part.strip()]


def parse_string_list(value: str | None, default: list[str]) -> list[str]:
    if value is None or not str(value).strip():
        return default
    return [part.strip() for part in str(value).replace(",", " ").split() if part.strip()]


def normalize_rows(rows: torch.Tensor, mode: str) -> torch.Tensor:
    key = str(mode).lower()
    if key == "row_max":
        return rows / rows.amax(dim=1, keepdim=True).clamp_min(1.0e-8)
    if key == "row_absmax":
        return rows / rows.abs().amax(dim=1, keepdim=True).clamp_min(1.0e-8)
    if key in {"none", "identity"}:
        return rows
    raise ValueError(f"Unsupported normalization mode: {mode}")


def pad_rows_to_square(rows: torch.Tensor, side: int) -> torch.Tensor:
    padded_frames = int(side) * int(side)
    if rows.shape[1] == padded_frames:
        return rows
    if rows.shape[1] > padded_frames:
        raise ValueError(f"Cannot pad {rows.shape[1]} frames into side={side}.")
    pad = rows.mean(dim=1, keepdim=True).expand(rows.shape[0], padded_frames - rows.shape[1])
    return torch.cat([rows, pad], dim=1)


def uses_signed_output(model_kind: str) -> bool:
    return str(model_kind).lower() in {"signed_gain_unet", "signed_unet", "tanh_unet", "linear_unet", "identity_unet"}


def predicts_gain(model_kind: str, target_mode: str) -> bool:
    return str(target_mode).lower() == "gain" or str(model_kind).lower() in {"gain_predictor_unet", "log_gain_predictor_unet"}


def basis_specs_from_names(names: list[str], frame_budget: int) -> list[tuple[str, dict[str, object]]]:
    specs: list[tuple[str, dict[str, object]]] = []
    for name in names:
        key = name.lower()
        if key in {"random_uniform", "random_binary"}:
            specs.append((key, {"num_frames": frame_budget, "reconstruction": "correlation"}))
        elif key == "fourier_fourstep":
            specs.append((key, {"num_frames": frame_budget}))
        else:
            specs.append((key, {}))
    return specs


def build_training_rows(args: argparse.Namespace, cfg: dict) -> tuple[torch.Tensor, torch.Tensor, pd.DataFrame]:
    mech = cfg.get("mechanism", {})
    h = int(mech.get("image_size", 32))
    p = h * h
    frame_budget, _ = basis_frame_budget(p)
    default_bases = ["random_uniform", "random_binary", "hadamard_paired", "dct_paired", "srht_paired"]
    basis_names = parse_string_list(args.bases, default_bases)
    rho_values = parse_float_list(args.rho_values, list(mech.get("rho_values", [0.001, 0.01, 0.1, 1.0])))
    sigma_values = parse_float_list(args.sigma_values, list(mech.get("sigma_a_values", [0.05, 0.15, 0.3])))
    objects = make_synthetic_objects(args.objects, h, int(cfg.get("seed", 0)))

    x_rows: list[torch.Tensor] = []
    y_rows: list[torch.Tensor] = []
    meta_rows: list[dict[str, object]] = []
    for basis_name, kwargs in basis_specs_from_names(basis_names, frame_budget):
        basis = make_basis(basis_name, num_pixels=p, seed=int(cfg.get("seed", 0)), **kwargs)
        for rho in rho_values:
            for sigma_a in sigma_values:
                for seed_idx in range(args.seeds):
                    for object_idx, obj in enumerate(objects):
                        ideal = basis.measure(obj)
                        channel = make_multiplicative_channel(
                            basis.num_frames,
                            model="ou",
                            rho=float(rho),
                            sigma_a=float(sigma_a),
                            seed=12000 + 97 * seed_idx + object_idx,
                            device=str(ideal.device),
                            dtype=ideal.dtype,
                        )
                        observed = simulate_channel_measurements(
                            ideal,
                            channel,
                            read_noise=float(mech.get("read_noise", 0.0)),
                            seed=13000 + 53 * object_idx + seed_idx,
                        )
                        x_rows.append(observed.reshape(1, -1))
                        if args.target_mode == "gain":
                            y_rows.append(channel.gains.reshape(1, -1))
                        else:
                            y_rows.append(ideal.reshape(1, -1))
                        meta_rows.append(
                            {
                                "basis": basis.name,
                                "rho": float(rho),
                                "sigma_a": float(sigma_a),
                                "seed": int(seed_idx),
                                "object": int(object_idx),
                                "num_frames": int(basis.num_frames),
                            }
                        )
    x = torch.cat(x_rows, dim=0).to(dtype=torch.float32)
    y = torch.cat(y_rows, dim=0).to(dtype=torch.float32)
    x = normalize_rows(x, args.input_normalize)
    y = normalize_rows(y, args.target_normalize)
    return x, y, pd.DataFrame(meta_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a supervised M2-specific SCGI measurement corrector.")
    parser.add_argument("--profile", default="smoke")
    parser.add_argument("--output-dir", type=Path, default=Path("results/m2_scgi_finetune"))
    parser.add_argument("--model-kind", default="direct_unet")
    parser.add_argument("--bases", default="")
    parser.add_argument("--rho-values", default="")
    parser.add_argument("--sigma-values", default="")
    parser.add_argument("--objects", type=int, default=4)
    parser.add_argument("--seeds", type=int, default=2)
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1.0e-3)
    parser.add_argument("--val-frac", type=float, default=0.2)
    parser.add_argument("--input-normalize", default="row_max", choices=["row_max", "row_absmax", "none"])
    parser.add_argument("--target-normalize", default="row_max", choices=["row_max", "row_absmax", "none"])
    parser.add_argument("--target-mode", default="measurement", choices=["measurement", "gain"])
    parser.add_argument("--output-clamp", default="auto", choices=["auto", "01", "none"])
    parser.add_argument("--gain-min", type=float, default=None)
    parser.add_argument("--gain-max", type=float, default=None)
    parser.add_argument("--seed", type=int, default=20260709)
    parser.add_argument("--resume-checkpoint", type=Path, default=None, help="Resume from m2_scgi_checkpoint_latest.pt.")
    parser.add_argument("--checkpoint-every", type=int, default=1, help="Save m2_scgi_checkpoint_latest.pt every N epochs; use 0 to disable.")
    args = parser.parse_args()

    root = project_root()
    cfg = load_config(root / "config.yaml", args.profile)
    cfg.setdefault("scgi", {})["model_kind"] = str(args.model_kind)
    if args.gain_min is not None:
        cfg["scgi"]["gain_min"] = float(args.gain_min)
    if args.gain_max is not None:
        cfg["scgi"]["gain_max"] = float(args.gain_max)
    if str(args.output_clamp) == "auto":
        output_clamp = "none" if uses_signed_output(args.model_kind) or predicts_gain(args.model_kind, args.target_mode) else "01"
    else:
        output_clamp = str(args.output_clamp)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    torch.manual_seed(int(args.seed))
    x, y, meta = build_training_rows(args, cfg)
    frames = int(x.shape[1])
    side = int(torch.ceil(torch.sqrt(torch.tensor(float(frames)))).item())
    model = make_scgi_model(cfg).to(device)
    ds = TensorDataset(x, y)
    val_count = max(1, int(round(float(args.val_frac) * len(ds))))
    train_count = len(ds) - val_count
    if train_count <= 0:
        raise ValueError("Training dataset too small after validation split.")
    split_gen = torch.Generator(device="cpu").manual_seed(int(args.seed))
    train_ds, val_ds = random_split(ds, [train_count, val_count], generator=split_gen)
    loader = DataLoader(train_ds, batch_size=int(args.batch_size), shuffle=True, generator=split_gen)
    opt = torch.optim.Adam(model.parameters(), lr=float(args.lr))
    history: list[dict[str, float]] = []
    start_epoch = 0
    if args.resume_checkpoint is not None:
        checkpoint = args.resume_checkpoint if args.resume_checkpoint.is_absolute() else root / args.resume_checkpoint
        if not checkpoint.exists():
            raise FileNotFoundError(f"Resume checkpoint not found: {checkpoint}")
        payload = torch.load(checkpoint, map_location=device)
        model.load_state_dict(payload["model_state_dict"])
        if "optimizer_state_dict" in payload:
            opt.load_state_dict(payload["optimizer_state_dict"])
        start_epoch = int(payload.get("epoch", 0))
        history = list(payload.get("history", []))
        print(f"resuming M2 SCGI training from epoch {start_epoch} at {checkpoint}", flush=True)

    checkpoint_latest = out_dir / "m2_scgi_checkpoint_latest.pt"

    def corrector_metadata() -> dict[str, object]:
        return {
            "task": "m2_scgi_finetune",
            "input_normalize": args.input_normalize,
            "target_normalize": args.target_normalize,
            "target_mode": args.target_mode,
            "output_clamp": output_clamp,
            "num_frames": frames,
            "padded_side": side,
            "model_kind": args.model_kind,
        }

    def save_epoch_checkpoint(epoch: int) -> None:
        if int(args.checkpoint_every) <= 0:
            return
        if epoch % int(args.checkpoint_every) != 0 and epoch != int(args.epochs):
            return
        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": opt.state_dict(),
                "config": cfg,
                "epoch": int(epoch),
                "target_epochs": int(args.epochs),
                "history": history,
                "corrector_metadata": corrector_metadata(),
            },
            checkpoint_latest,
        )
        write_json_atomic(
            out_dir / "training_progress.json",
            {
                "state": "training",
                "epoch": int(epoch),
                "target_epochs": int(args.epochs),
                "checkpoint": "m2_scgi_checkpoint_latest.pt",
                "train_mse_last": history[-1]["train_mse"] if history else None,
                "val_mse_last": history[-1]["val_mse"] if history else None,
                "resumed_from": None if args.resume_checkpoint is None else str(args.resume_checkpoint),
            },
        )

    for epoch in range(start_epoch + 1, int(args.epochs) + 1):
        model.train()
        train_losses = []
        for xb, yb in loader:
            xb = xb.to(device)
            yb = yb.to(device)
            opt.zero_grad(set_to_none=True)
            padded = pad_rows_to_square(xb, side)
            pred = model(as_images(padded, side)).reshape(padded.shape[0], -1)[:, :frames]
            loss = torch.mean((pred.reshape_as(yb) - yb) ** 2)
            loss.backward()
            opt.step()
            train_losses.append(float(loss.detach().cpu()))
        model.eval()
        val_losses = []
        with torch.no_grad():
            for xb, yb in DataLoader(val_ds, batch_size=int(args.batch_size)):
                pred = correct_measurements_padded(model, xb.to(device), clamp=(output_clamp != "none")).to(device)
                val_losses.append(float(torch.mean((pred.reshape_as(yb.to(device)) - yb.to(device)) ** 2).detach().cpu()))
        row = {
            "epoch": float(epoch),
            "train_mse": float(sum(train_losses) / max(1, len(train_losses))),
            "val_mse": float(sum(val_losses) / max(1, len(val_losses))),
        }
        history.append(row)
        save_epoch_checkpoint(epoch)
        print(f"epoch={epoch} train_mse={row['train_mse']:.6g} val_mse={row['val_mse']:.6g}", flush=True)

    checkpoint = out_dir / "m2_scgi_checkpoint.pt"
    payload = {
        "model_state_dict": model.state_dict(),
        "config": cfg,
        "epoch": int(args.epochs),
        "history": history,
        "corrector_metadata": corrector_metadata(),
    }
    torch.save(payload, checkpoint)
    pd.DataFrame(history).to_csv(out_dir / "train_history.csv", index=False)
    meta.to_csv(out_dir / "train_dataset_manifest.csv", index=False)
    manifest = {
        "profile": args.profile,
        "device": str(device),
        "checkpoint": str(checkpoint),
        "samples": int(len(ds)),
        "train_samples": int(train_count),
        "val_samples": int(val_count),
        "num_frames": frames,
        "padded_side": side,
        "model_kind": args.model_kind,
        "input_normalize": args.input_normalize,
        "target_normalize": args.target_normalize,
        "target_mode": args.target_mode,
        "output_clamp": output_clamp,
        "start_epoch": int(start_epoch),
        "resume_checkpoint": None if args.resume_checkpoint is None else str(args.resume_checkpoint),
        "latest_checkpoint": str(checkpoint_latest),
        "final_train_mse": history[-1]["train_mse"],
        "final_val_mse": history[-1]["val_mse"],
    }
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_json_atomic(
        out_dir / "training_progress.json",
        {
            "state": "completed",
            "epoch": int(args.epochs),
            "target_epochs": int(args.epochs),
            "checkpoint": "m2_scgi_checkpoint_latest.pt",
            "final_checkpoint": "m2_scgi_checkpoint.pt",
            "train_mse_last": history[-1]["train_mse"],
            "val_mse_last": history[-1]["val_mse"],
            "resumed_from": None if args.resume_checkpoint is None else str(args.resume_checkpoint),
        },
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
