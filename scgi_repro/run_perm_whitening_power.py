"""Experiment B -- Multi-permutation whitening power (extends Fig. 2).

Fig. 2 (r2b) applied the Brown-Forsythe (Levene) stationarity test to the
noiseless bucket carrier of a single *fixed* random Hadamard permutation and
found the ordered arm rejected non-stationarity for ~7/10 objects while the
fixed random arm rejected for 2/10.  The probabilistic-permutation theorem
predicts that the 2/10 is an *unlucky-draw* effect: over independent random
permutations the rejection rate is low, and the occasional rejections are the
draws whose permuted squared object has an unusually peaked Walsh spectrum.

This runner quantifies that.  For each of the 10 standard paper objects it
draws ``--nperm`` (32) independent random pixel permutations and, per
permutation, computes two coupled quantities:

  * ``levene_p``               -- Brown-Forsythe p across 8 chunks of the
                                  hadamard_random_paired carrier of the
                                  *permuted* object (reusing the *exact* Fig. 2
                                  r2b metric, imported from
                                  run_paper_fig2_stationarity.stationarity_metrics).
  * ``walsh_flatness_ratio``   -- max non-DC |w_hat(q)| / S2, where
                                  ``w_hat = FWHT((T_perm)^2)`` and
                                  ``S2 = sum((T_perm)^2) = w_hat(0)``.  A peaked
                                  (aligned) permuted spectrum gives a ratio near
                                  1; a flat/whitened one gives a small ratio.

The ordered (natural-Hadamard, un-permuted) arm is run once per object as the
Fig. 2 r2b reference.

Acceptance: the mean random-arm rejection rate at p<1e-3 is LOW (<~15%) and the
rejections correlate with high ``walsh_flatness_ratio`` (reported as Spearman
rho), i.e. the fixed-permutation result is an unlucky-draw effect quantified by
the Walsh spectrum.

Outputs (in ``results/perm_whitening_power_r1/`` by default):
  * ``perm_power.csv``      -- one row per (object, arm, perm).
  * ``fig_perm_power.png``  -- per-object rejection rate + levene_p vs Walsh scatter.
  * ``perm_power_caption.md``
  * ``run_manifest.json``

Sharding: ``--shard i/k`` round-robins the flattened (object, arm, perm) unit
grid.  ``--smoke`` runs a tiny grid.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from scipy import stats as scipy_stats

from src.basis import hadamard_matrix, interleave_paired_frames, is_power_of_two
from src.mechanisms import moving_average_1d
from src.paper_experiments import build_run_manifest, make_paper_basis, make_paper_objects, write_caption

# Reuse the EXACT Fig. 2 r2b stationarity metric (Brown-Forsythe over 8 chunks).
from run_paper_fig2_stationarity import stationarity_metrics


ROOT = Path(__file__).resolve().parent


def parse_shard(value: Optional[str]) -> Tuple[int, int]:
    """Parse a zero-based shard spec like ``0/5`` (mirrors run_phase_m2)."""

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


def fwht(vector: torch.Tensor) -> torch.Tensor:
    """Unnormalised natural-ordered fast Walsh-Hadamard transform (== H @ x).

    ``H`` is the Sylvester-Hadamard matrix with +/-1 entries, so ``w_hat[0]`` is
    the sum of ``vector``.  Length must be a power of two.
    """

    n = vector.numel()
    if not is_power_of_two(n):
        raise ValueError(f"FWHT length must be a power of two, got {n}.")
    a = vector.clone().to(dtype=torch.float64).reshape(-1)
    h = 1
    while h < n:
        a = a.view(n // (2 * h), 2, h)
        top = a[:, 0, :] + a[:, 1, :]
        bot = a[:, 0, :] - a[:, 1, :]
        a = torch.stack([top, bot], dim=1).reshape(-1)
        h *= 2
    return a


def random_paired_carrier(coeffs: torch.Tensor, row_order: torch.Tensor, sum_pixels: float) -> torch.Tensor:
    """Paired-Hadamard bucket carrier from precomputed signed Walsh coefficients.

    For a paired-Hadamard basis measuring an object, frame ``2n`` equals
    ``0.5 * (sum(T) + <h_{order[n]}, T>)`` and frame ``2n+1`` its complement.
    ``coeffs[k] = <h_k, T>`` is exactly ``FWHT(T)[k]``, so the full carrier is
    reconstructed cheaply for any row order (natural or random) -- this is
    identical to make_paper_basis("hadamard_random_paired").measure(T) and is
    verified against it once per run.
    """

    ordered = coeffs[row_order]
    carrier = torch.empty(2 * ordered.numel(), dtype=ordered.dtype, device=ordered.device)
    carrier[0::2] = 0.5 * (sum_pixels + ordered)
    carrier[1::2] = 0.5 * (sum_pixels - ordered)
    return carrier


def walsh_flatness_ratio(squared_perm: torch.Tensor) -> Tuple[float, float]:
    """max non-DC |FWHT(T^2)| / S2, with S2 = sum(T^2) = FWHT(T^2)[0]."""

    w_hat = fwht(squared_perm)
    s2 = float(w_hat[0].item())
    if s2 <= 0:
        return float("nan"), s2
    max_non_dc = float(w_hat[1:].abs().max().item())
    return max_non_dc / s2, s2


def levene_of_carrier(carrier: torch.Tensor, window: int, chunks: int, transient: int) -> float:
    """Brown-Forsythe p via the imported Fig. 2 r2b metric."""

    carrier = carrier.to(dtype=torch.float32)
    running = moving_average_1d(carrier, int(window))
    metrics = stationarity_metrics(carrier, running, num_chunks=int(chunks), transient=int(transient))
    return float(metrics["levene_p"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiment B: multi-permutation whitening power (r1).")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "perm_whitening_power_r1")
    parser.add_argument("--image-size", type=int, default=64, help="Square side; K = image_size^2 (64 -> 4096 px / 8192 frames).")
    parser.add_argument("--objects", type=int, default=10)
    parser.add_argument("--nperm", type=int, default=32)
    parser.add_argument("--seed", type=int, default=20240708, help="Base seed (matches Fig. 2 object seed).")
    parser.add_argument("--window", type=int, default=64)
    parser.add_argument("--chunks", type=int, default=8)
    parser.add_argument("--transient", type=int, default=128)
    parser.add_argument("--reject-alpha", type=float, default=1.0e-3)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--shard", default="", help="Optional zero-based shard spec i/k, for example 0/5.")
    parser.add_argument("--smoke", action="store_true", help="Tiny grid for a local smoke test.")
    args = parser.parse_args()

    if args.smoke:
        args.image_size = 16
        args.objects = 3
        args.nperm = 4
        args.window = 16
        args.transient = 16
        if args.output_dir == ROOT / "results" / "perm_whitening_power_r1":
            args.output_dir = ROOT / "results" / "perm_whitening_power_smoke"

    shard_index, shard_count = parse_shard(args.shard)
    start = time.time()
    out = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    device = args.device
    K = args.image_size * args.image_size
    if not is_power_of_two(K):
        raise ValueError(f"K = image_size^2 must be a power of two, got {K}.")
    objects = make_paper_objects(args.objects, image_size=args.image_size, seed=args.seed)

    # One shared natural Hadamard matrix; per-perm carriers reuse FWHT coefficients.
    hadamard = hadamard_matrix(K, device=device, dtype=torch.float64)
    identity_order = torch.arange(K, device=device)

    # 32 shared, independent pixel permutations (reused across objects for a clean
    # per-object comparison) plus 32 independent Hadamard row orders.
    perm_pixels = []
    perm_rows = []
    for perm_idx in range(args.nperm):
        g_pix = torch.Generator(device="cpu")
        g_pix.manual_seed(args.seed + 101 * perm_idx)
        perm_pixels.append(torch.randperm(K, generator=g_pix).to(device=device))
        g_row = torch.Generator(device="cpu")
        g_row.manual_seed(args.seed + 977 * perm_idx)
        perm_rows.append(torch.randperm(K, generator=g_row).to(device=device))

    # Unit grid: for each object, one ordered-reference unit then nperm random units.
    units: List[Tuple[int, str, int]] = []
    for obj_idx in range(len(objects)):
        units.append((obj_idx, "ordered", -1))
        for perm_idx in range(args.nperm):
            units.append((obj_idx, "random", perm_idx))

    rows: List[Dict[str, object]] = []
    verify_diff: Optional[float] = None
    for unit_index, (obj_idx, arm, perm_idx) in enumerate(units):
        if unit_index % shard_count != shard_index:
            continue
        obj = objects[obj_idx]
        T = obj.vector.to(device=device, dtype=torch.float64)

        if arm == "ordered":
            coeffs = fwht(T)
            carrier = random_paired_carrier(coeffs, identity_order, float(T.sum().item()))
            ratio, s2 = walsh_flatness_ratio(T * T)
            perm_seed = -1
        else:
            pix = perm_pixels[perm_idx]
            row_order = perm_rows[perm_idx]
            T_perm = T[pix]
            coeffs = fwht(T_perm)
            carrier = random_paired_carrier(coeffs, row_order, float(T_perm.sum().item()))
            ratio, s2 = walsh_flatness_ratio(T_perm * T_perm)
            perm_seed = int(args.seed + 101 * perm_idx)

            # One-time equivalence check against make_paper_basis (faithfulness guard).
            if verify_diff is None:
                basis = make_paper_basis("hadamard_random_paired", K, seed=perm_seed)
                order_check = basis.row_indices.to(device=device)
                ref_carrier = random_paired_carrier(fwht(T_perm), order_check, float(T_perm.sum().item()))
                # basis.measure applies its own row order; compare against basis directly.
                direct = basis.measure(T_perm).to(dtype=torch.float64)
                verify_diff = float((ref_carrier - direct).abs().max().item())

        levene_p = levene_of_carrier(carrier, window=args.window, chunks=args.chunks, transient=args.transient)
        rows.append(
            {
                "unit_index": unit_index,
                "object": obj.name,
                "family": obj.family,
                "K_eff": obj.k_eff,
                "arm": arm,
                "perm": perm_idx,
                "perm_seed": perm_seed,
                "num_frames": int(carrier.numel()),
                "chunks": int(args.chunks),
                "levene_p": levene_p,
                "levene_reject": bool(levene_p < args.reject_alpha),
                "walsh_flatness_ratio": float(ratio),
                "walsh_S2": float(s2),
                "shard": args.shard or "0/1",
            }
        )

    if not rows:
        raise RuntimeError(f"Shard {args.shard or '0/1'} produced no rows.")

    df = pd.DataFrame(rows)
    csv_name = "perm_power.csv" if shard_count == 1 else f"perm_power_shard{shard_index}of{shard_count}.csv"
    df.to_csv(out / csv_name, index=False)

    caption_lines: List[str] = []
    if shard_count == 1:
        caption_lines = _make_figures_and_readout(df, out, args)

    manifest_extra = {
        "rows": int(len(df)),
        "units_total": int(len(units)),
        "shard": args.shard or "0/1",
        "K": int(K),
        "nperm": int(args.nperm),
        "carrier_verify_max_abs_diff_vs_make_paper_basis": verify_diff,
    }
    (out / "run_manifest.json").write_text(
        json.dumps(build_run_manifest(args, ROOT, extra=manifest_extra), indent=2, default=str),
        encoding="utf-8",
    )

    write_caption(
        out / "perm_power_caption.md",
        "Experiment B -- Multi-Permutation Whitening Power (r1)",
        [
            f"K={K} ({args.image_size}x{args.image_size}), num_frames={2 * K}, chunks={args.chunks}, "
            f"nperm={args.nperm}, reject at p<{args.reject_alpha:g}.",
            "Random arm: hadamard_random_paired carrier of each pixel-permuted object; Brown-Forsythe levene_p is the "
            "EXACT Fig. 2 r2b metric (run_paper_fig2_stationarity.stationarity_metrics).",
            "walsh_flatness_ratio = max non-DC |FWHT((T_perm)^2)| / sum((T_perm)^2); high => peaked/aligned spectrum.",
            *caption_lines,
            f"Rows: {len(df)} (shard {args.shard or '0/1'}). Runtime seconds: {time.time() - start:.2f}.",
        ],
    )
    print(
        f"PermWhiteningPower complete rows={len(df)} shard={args.shard or '0/1'} output={out} "
        f"runtime={time.time() - start:.2f}s"
    )


def _make_figures_and_readout(df: pd.DataFrame, out: Path, args: argparse.Namespace) -> List[str]:
    """Per-object rejection-rate bars + levene_p vs Walsh scatter; Spearman readout."""

    random_df = df[df["arm"] == "random"].copy()
    ordered_df = df[df["arm"] == "ordered"].copy()

    per_object = random_df.groupby("object").agg(
        reject_rate=("levene_reject", "mean"),
        mean_walsh=("walsh_flatness_ratio", "mean"),
        n=("levene_reject", "count"),
    ).reset_index()
    ordered_reject = dict(zip(ordered_df["object"], ordered_df["levene_reject"]))

    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.6))

    # (left) per-object random-arm rejection rate; mark ordered-arm rejection.
    ax = axes[0]
    order = per_object.sort_values("mean_walsh")
    xpos = np.arange(len(order))
    ax.bar(xpos, order["reject_rate"], color="tab:blue", alpha=0.8, label="random-arm reject rate")
    for i, obj in enumerate(order["object"]):
        if ordered_reject.get(obj, False):
            ax.plot(i, 1.02, marker="v", color="tab:red", markersize=7)
    ax.axhline(0.15, color="gray", linestyle="--", linewidth=1.0, label="0.15 acceptance ceiling")
    ax.set_xticks(xpos)
    ax.set_xticklabels(order["object"], rotation=45, ha="right", fontsize=7)
    ax.set_ylabel(f"reject rate over {args.nperm} perms (p<{args.reject_alpha:g})")
    ax.set_ylim(0.0, 1.08)
    ax.set_title("Per-object random-permutation rejection rate\n(v = ordered arm rejects)")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, axis="y", alpha=0.25)

    # (right) scatter: levene_p vs walsh_flatness_ratio (all random units).
    ax = axes[1]
    lp = random_df["levene_p"].to_numpy(dtype=float).clip(1e-300, 1.0)
    wr = random_df["walsh_flatness_ratio"].to_numpy(dtype=float)
    rej = random_df["levene_reject"].to_numpy(dtype=bool)
    ax.scatter(wr[~rej], lp[~rej], s=14, color="tab:blue", alpha=0.5, label="not rejected")
    ax.scatter(wr[rej], lp[rej], s=20, color="tab:red", alpha=0.7, label="rejected")
    ax.axhline(args.reject_alpha, color="gray", linestyle="--", linewidth=1.0)
    ax.set_yscale("log")
    ax.set_xlabel("walsh_flatness_ratio (max non-DC |FWHT(T^2)| / S2)")
    ax.set_ylabel("levene_p")
    ax.set_title("levene_p vs permuted-object Walsh peak")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, alpha=0.25)

    fig.tight_layout()
    fig.savefig(out / "fig_perm_power.png", dpi=200)
    plt.close(fig)

    # Spearman correlations over all random units.
    valid = np.isfinite(wr) & np.isfinite(lp)
    rho_p, p_p = scipy_stats.spearmanr(wr[valid], lp[valid]) if valid.sum() > 2 else (float("nan"), float("nan"))
    rho_r, p_r = (
        scipy_stats.spearmanr(wr[valid], random_df["levene_reject"].to_numpy(dtype=float)[valid])
        if valid.sum() > 2
        else (float("nan"), float("nan"))
    )

    mean_reject_rate = float(random_df["levene_reject"].mean())
    ordered_hits = int(ordered_df["levene_reject"].sum())
    ordered_total = int(len(ordered_df))

    return [
        f"Mean random-arm rejection rate across all objects/perms: {mean_reject_rate:.3f} (acceptance <~0.15).",
        f"Spearman(walsh_flatness_ratio, levene_p) = {rho_p:.3f} (p={p_p:.2e}); expect NEGATIVE -- higher Walsh peak "
        f"=> smaller levene_p (more rejection).",
        f"Spearman(walsh_flatness_ratio, reject_indicator) = {rho_r:.3f} (p={p_r:.2e}); expect POSITIVE.",
        f"Ordered (un-permuted natural-Hadamard) reference arm rejects {ordered_hits}/{ordered_total} objects "
        f"(Fig. 2 r2b expected ~7/10 at 8192 frames).",
    ]


if __name__ == "__main__":
    main()
