"""Experiment A -- Tall-design threshold scan: validates the LOCAL-RANK component
of Theorem A' (part (i)) and probes algorithmic recovery.

Scope note: this runner does NOT test the global sufficiency thresholds of
Theorem A'(ii)-(iii) (generic exact at ``N >= K + p``; uniform at
``N >= 2K + p - 1``) nor their conjectured sharpness -- those are a.e.-(M,T)
uniqueness statements that a rank scan cannot certify.  What it measures is:

For the noiseless bilinear-with-log-gain forward model

    R_n = exp(ell_n) * (M_n . T),   ell = U theta,

with a generic Gaussian design ``M in R^{N x K}`` and a Fourier low-pass gain
basis ``U in R^{N x p}`` (p odd), Theorem A'(i) predicts the pair ``(theta, T)``
is LOCALLY identifiable up to the single global-scale gauge iff
``N >= K + p - 1`` (the collision Jacobian drops its extra deficiency there).

The forward map has exactly one continuous gauge freedom: rescaling
``T -> alpha T`` while shifting the constant log-gain column by ``-log alpha``
leaves ``R`` invariant.  So the full parameter dimension is ``p + K`` and the
gauge dimension is ``1``; local identifiability is therefore
``rank(J) == p + K - 1``.

This runner produces two panels per ``(N, K, p, seed)`` cell:

  (a) LOCAL RANK TEST (deterministic, cheap): assemble the analytic Jacobian of
      the forward map at the ground truth and test ``rank(J) == p + K - 1``
      -- the direct verification of Theorem A'(i)'s rank wall.
  (b) RECOVERY PROBE (expensive): blind alternating-minimisation recovery of
      ``(theta, T)`` from ``R`` alone, with the global scale gauge fixed to
      ``mean(ell) = 0`` and up to ``--restarts`` random restarts.  This is an
      ALGORITHMIC-RECOVERY observation, not a uniqueness test.

The gap between the (a) rank wall at ``N = K + p - 1`` and the (b) solver wall a
few measurements higher is the point of the figure: uniqueness (identifiability)
is not the same as conditioning (recoverability) near the wall.

Each CSV row also records the carrier margin ``min_n |(M T)_n|`` of its cell
(``carrier_margin_min_abs``): Theorem A' quantifies over the nonvanishing-carrier
set, and the margin lets later analyses condition on how close a draw came to
violating that hypothesis.

Outputs (in ``results/tall_design_threshold_r1/`` by default):
  * ``threshold_scan.csv``          -- one row per (N, p, seed) with both panels.
  * ``fig_threshold_heatmap.png``   -- solver success rate over (N-K-p, p).
  * ``fig_rank_vs_recovery.png``    -- rank-test vs solver-success transitions.
  * ``tall_design_caption.md``      -- measured transition locations.
  * ``run_manifest.json``           -- provenance.

Sharding: ``--shard i/k`` round-robins the flattened (p, N, seed) unit grid.
``--smoke`` runs a tiny grid (K=16, p in {3,5}, 3 seeds, small N range).
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch

from src.paper_experiments import build_run_manifest, rel_mse, write_caption


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


def fourier_lowpass_basis(num_rows: int, p: int, device: str, dtype: torch.dtype) -> torch.Tensor:
    """Fourier low-pass log-gain basis U in R^{N x p} (p odd).

    Column 0 is the constant (all-ones) DC column; the remaining columns are
    ``cos`` / ``sin`` pairs of integer frequencies ``1 .. (p-1)/2``.  Over the
    index grid ``n = 0 .. N-1`` every non-DC column has exactly zero mean, so
    ``mean_n(ell) = theta_0`` and the scale gauge is fixed simply by zeroing
    ``theta_0``.
    """

    if p < 1 or p % 2 == 0:
        raise ValueError(f"p must be a positive odd integer, got {p}.")
    n = torch.arange(num_rows, dtype=dtype, device=device)
    columns = [torch.ones(num_rows, dtype=dtype, device=device)]
    half = (p - 1) // 2
    for freq in range(1, half + 1):
        angle = 2.0 * math.pi * float(freq) * n / float(num_rows)
        columns.append(torch.cos(angle))
        columns.append(torch.sin(angle))
    return torch.stack(columns, dim=1)


def make_object(kind: str, K: int, seed: int, device: str, dtype: torch.dtype) -> torch.Tensor:
    """Non-negative object of length K. ``random_nonneg`` plus a couple of structured ones."""

    generator = torch.Generator(device="cpu")
    generator.manual_seed(int(seed))
    if kind == "random_nonneg":
        vector = torch.rand(K, generator=generator, dtype=torch.float64) + 0.1
    elif kind == "smooth_bump":
        side = int(math.isqrt(K))
        if side * side == K:
            yy, xx = torch.meshgrid(torch.arange(side), torch.arange(side), indexing="ij")
            cx = (side - 1) / 2.0 + 0.4 * float(torch.randn(1, generator=generator).item())
            cy = (side - 1) / 2.0 + 0.4 * float(torch.randn(1, generator=generator).item())
            radius2 = (xx.to(torch.float64) - cx) ** 2 + (yy.to(torch.float64) - cy) ** 2
            vector = torch.exp(-radius2 / (2.0 * (0.35 * side) ** 2)).reshape(-1) + 0.05
        else:
            n = torch.arange(K, dtype=torch.float64)
            vector = torch.exp(-((n - K / 2.0) ** 2) / (2.0 * (0.2 * K) ** 2)) + 0.05
    elif kind == "sparse_spikes":
        vector = torch.full((K,), 0.05, dtype=torch.float64)
        num_spikes = max(2, K // 12)
        idx = torch.randperm(K, generator=generator)[:num_spikes]
        vector[idx] = 0.5 + torch.rand(num_spikes, generator=generator, dtype=torch.float64)
    else:
        raise ValueError(f"Unknown object kind: {kind}")
    return vector.to(device=device, dtype=dtype)


def object_kind_for_seed(seed_idx: int) -> str:
    """A couple of structured objects (seeds 0,1) then random non-negative objects."""

    if seed_idx == 0:
        return "smooth_bump"
    if seed_idx == 1:
        return "sparse_spikes"
    return "random_nonneg"


def local_rank_test(
    M: torch.Tensor,
    U: torch.Tensor,
    ell: torch.Tensor,
    R: torch.Tensor,
    rank_rtol: float,
) -> Dict[str, object]:
    """Analytic Jacobian rank test at the ground truth.

    Columns:  ``J_theta[:, j] = R * U[:, j]``  (since dR/dtheta_j = R * U_j),
              ``J_T[:, k]     = exp(ell) * M[:, k]``  (since dR/dT_k = exp(ell) * M_k).

    Local identifiability (up to the 1-D scale gauge) holds iff
    ``rank(J) == p + K - 1``.  Rank is computed in float64 with a documented
    relative tolerance ``rank_rtol`` (threshold = rank_rtol * S_max).
    """

    N, K = M.shape
    p = U.shape[1]
    exp_ell = torch.exp(ell)
    J_theta = R.reshape(-1, 1) * U            # N x p
    J_T = exp_ell.reshape(-1, 1) * M          # N x K
    J = torch.cat([J_theta, J_T], dim=1).to(dtype=torch.float64)  # N x (p+K)

    svals = torch.linalg.svdvals(J)
    s_max = float(svals[0].item()) if svals.numel() else 0.0
    threshold = rank_rtol * s_max if s_max > 0 else 0.0
    rank = int((svals > threshold).sum().item())
    expected = p + K - 1

    # Diagnostic singular-value ratios: the (p+K-1)-th largest is the smallest
    # "informative" value; the (p+K)-th is the machine-zero scale gauge.
    def _ratio(index: int) -> float:
        if 0 <= index < svals.numel() and s_max > 0:
            return float((svals[index] / s_max).item())
        return float("nan")

    return {
        "rank_J": rank,
        "expected_rank": expected,
        "local_identifiable": bool(rank == expected),
        "rank_deficit": int(expected - rank),
        "sv_smallest_informative_ratio": _ratio(expected - 1),
        "sv_gauge_ratio": _ratio(expected),
        "rank_threshold": float(threshold),
    }


def _gauge_fix(theta: torch.Tensor, T: torch.Tensor, U: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """Fix the global-scale gauge to mean(ell) = 0 (equivalently theta_0 = 0)."""

    shift = float(theta[0].item())  # mean(ell) == theta_0 because non-DC cols are zero-mean
    theta = theta.clone()
    theta[0] = 0.0
    T = T * math.exp(shift)
    return theta, T


def recover(
    M: torch.Tensor,
    R: torch.Tensor,
    U: torch.Tensor,
    ell_true: torch.Tensor,
    T_true: torch.Tensor,
    restarts: int,
    max_iter: int,
    gn_iters: int,
    lm_damping: float,
    resid_tol: float,
    success_relmse: float,
    success_ell_max: float,
    ell_clamp: float,
) -> Dict[str, object]:
    """Blind alternating-minimisation recovery of (theta, T) from R alone.

    T-step: weighted least squares ``T = argmin || exp(ell) * (M T) - R ||``.
    theta-step: a few damped Gauss-Newton steps on
    ``theta = argmin || exp(U theta) * (M T) - R ||`` with m = M T fixed.
    After each alternation the scale gauge is fixed to mean(ell) = 0.
    """

    N, K = M.shape
    p = U.shape[1]
    dtype = M.dtype
    eye_p = torch.eye(p, dtype=dtype, device=M.device)
    R_norm = float(R.norm().item())

    # Gauge-fixed ground truth for scoring (both truth and estimate use mean(ell)=0).
    ell_true_gf = ell_true - ell_true.mean()

    best_relmse = float("inf")
    best_ell_max = float("inf")
    best_resid = float("inf")
    best_iters = 0
    success = False
    restarts_used = 0

    for restart in range(restarts):
        restarts_used = restart + 1
        if restart == 0:
            theta = torch.zeros(p, dtype=dtype, device=M.device)
        else:
            g = torch.Generator(device="cpu")
            g.manual_seed(1_000 + 97 * restart)
            theta = (0.3 * torch.randn(p, generator=g)).to(device=M.device, dtype=dtype)

        prev_resid = float("inf")
        iters_run = 0
        for iteration in range(max_iter):
            iters_run = iteration + 1
            ell = (U @ theta).clamp(-ell_clamp, ell_clamp)

            # T-step: weighted least squares with A = diag(exp(ell)) M.
            A = torch.exp(ell).reshape(-1, 1) * M
            T = torch.linalg.lstsq(A, R.reshape(-1, 1)).solution.reshape(-1)

            # theta-step: damped Gauss-Newton with m = M T fixed.
            m = M @ T
            for _ in range(gn_iters):
                ell = (U @ theta).clamp(-ell_clamp, ell_clamp)
                w = torch.exp(ell) * m
                residual = w - R
                J_gn = w.reshape(-1, 1) * U               # d residual / d theta_j
                JtJ = J_gn.transpose(0, 1) @ J_gn
                damp = lm_damping * (JtJ.diagonal().mean().clamp_min(1e-12))
                Jtr = J_gn.transpose(0, 1) @ residual
                delta = torch.linalg.solve(JtJ + damp * eye_p, Jtr)
                theta = theta - delta

            theta, T = _gauge_fix(theta, T, U)

            ell = (U @ theta).clamp(-ell_clamp, ell_clamp)
            resid = float((torch.exp(ell) * (M @ T) - R).norm().item()) / max(R_norm, 1e-30)
            if resid < resid_tol or abs(prev_resid - resid) < 1e-15:
                break
            prev_resid = resid

        ell_hat = U @ theta
        ell_hat = ell_hat - ell_hat.mean()
        relmse = rel_mse(T, T_true)
        ell_max = float((ell_hat - ell_true_gf).abs().max().item())
        this_success = bool(relmse < success_relmse and ell_max < success_ell_max)

        if relmse < best_relmse:
            best_relmse = relmse
            best_ell_max = ell_max
            best_resid = resid
            best_iters = iters_run
        if this_success:
            success = True
            best_relmse = relmse
            best_ell_max = ell_max
            best_resid = resid
            best_iters = iters_run
            break

    return {
        "solver_success": bool(success),
        "best_relmse_T": float(best_relmse),
        "best_ell_max_err": float(best_ell_max),
        "best_residual": float(best_resid),
        "iterations": int(best_iters),
        "restarts_used": int(restarts_used),
    }


def build_offsets(n_off_lo: int, n_off_hi: int, n_step: int) -> List[int]:
    """N sweep offsets (N-K-p): K+p-8..K+p+16 step 2, augmented with the local-ID wall -1."""

    base = list(range(int(n_off_lo), int(n_off_hi) + 1, int(n_step)))
    return sorted(set(base) | {-1})


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiment A: tall-design identifiability threshold (r1).")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "tall_design_threshold_r1")
    parser.add_argument("--K", type=int, default=64, help="Object dimension.")
    parser.add_argument("--p-values", type=int, nargs="+", default=[3, 5, 9, 17, 33], help="Gain-basis dims (odd).")
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--seed", type=int, default=20240709, help="Base seed.")
    parser.add_argument("--n-offset-lo", type=int, default=-8, help="Lowest N-K-p offset.")
    parser.add_argument("--n-offset-hi", type=int, default=16, help="Highest N-K-p offset.")
    parser.add_argument("--n-step", type=int, default=2)
    parser.add_argument("--restarts", type=int, default=8)
    parser.add_argument("--max-iter", type=int, default=150, help="Max alternations per restart.")
    parser.add_argument("--gn-iters", type=int, default=3, help="Gauss-Newton steps per theta-step.")
    parser.add_argument("--lm-damping", type=float, default=1e-8)
    parser.add_argument("--resid-tol", type=float, default=1e-11)
    parser.add_argument("--success-relmse", type=float, default=1e-6)
    parser.add_argument("--success-ell-max", type=float, default=1e-3)
    parser.add_argument("--ell-clamp", type=float, default=30.0)
    parser.add_argument("--theta-std", type=float, default=0.3, help="Std of the ground-truth theta.")
    parser.add_argument("--rank-rtol", type=float, default=1e-9, help="Relative singular-value tolerance for rank(J).")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--shard", default="", help="Optional zero-based shard spec i/k, for example 0/5.")
    parser.add_argument("--smoke", action="store_true", help="Tiny grid for a local smoke test.")
    args = parser.parse_args()

    if args.smoke:
        args.K = 16
        args.p_values = [3, 5]
        args.seeds = 3
        args.n_offset_lo = -4
        args.n_offset_hi = 8
        if args.output_dir == ROOT / "results" / "tall_design_threshold_r1":
            args.output_dir = ROOT / "results" / "tall_design_threshold_smoke"

    shard_index, shard_count = parse_shard(args.shard)
    start = time.time()
    out = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    device = args.device
    dtype = torch.float64
    K = int(args.K)
    offsets = build_offsets(args.n_offset_lo, args.n_offset_hi, args.n_step)

    # Enumerate the (p, N, seed) unit grid, then round-robin over the shard.
    units: List[Tuple[int, int, int]] = []
    for p in args.p_values:
        for off in offsets:
            N = K + p + off
            if N <= K:
                continue
            for seed_idx in range(args.seeds):
                units.append((p, N, seed_idx))

    rows: List[Dict[str, object]] = []
    for unit_index, (p, N, seed_idx) in enumerate(units):
        if unit_index % shard_count != shard_index:
            continue

        kind = object_kind_for_seed(seed_idx)
        obj_seed = args.seed + 7919 * seed_idx
        T_true = make_object(kind, K, obj_seed, device, dtype)

        # Fresh generic Gaussian design and gain-basis coefficients per (p, N, seed).
        design_seed = args.seed + 9973 * seed_idx + 131 * p + N
        g_design = torch.Generator(device="cpu")
        g_design.manual_seed(design_seed)
        M = torch.randn(N, K, generator=g_design, dtype=torch.float64).to(device=device, dtype=dtype)

        g_theta = torch.Generator(device="cpu")
        g_theta.manual_seed(design_seed + 555)
        theta_true = (args.theta_std * torch.randn(p, generator=g_theta)).to(device=device, dtype=dtype)

        U = fourier_lowpass_basis(N, p, device, dtype)
        ell_true = U @ theta_true
        carrier = M @ T_true
        # Carrier margin min_n |(MT)_n|: distance of this draw from the vanishing-carrier
        # exceptional set that Theorem A' excludes (recorded per cell for later analyses).
        carrier_margin = float(carrier.abs().min().item())
        R = torch.exp(ell_true) * carrier

        rank_info = local_rank_test(M, U, ell_true, R, args.rank_rtol)
        rec_info = recover(
            M,
            R,
            U,
            ell_true,
            T_true,
            restarts=int(args.restarts),
            max_iter=int(args.max_iter),
            gn_iters=int(args.gn_iters),
            lm_damping=float(args.lm_damping),
            resid_tol=float(args.resid_tol),
            success_relmse=float(args.success_relmse),
            success_ell_max=float(args.success_ell_max),
            ell_clamp=float(args.ell_clamp),
        )

        rows.append(
            {
                "unit_index": unit_index,
                "K": K,
                "p": p,
                "N": N,
                "offset": N - K - p,
                "seed": seed_idx,
                "object_kind": kind,
                "shard": args.shard or "0/1",
                "carrier_margin_min_abs": carrier_margin,
                **rank_info,
                **rec_info,
            }
        )

    if not rows:
        raise RuntimeError(f"Shard {args.shard or '0/1'} produced no rows.")

    df = pd.DataFrame(rows)
    csv_name = "threshold_scan.csv" if shard_count == 1 else f"threshold_scan_shard{shard_index}of{shard_count}.csv"
    df.to_csv(out / csv_name, index=False)

    # Figures and the acceptance readout only make sense on the full (unsharded) grid.
    transition_lines: List[str] = []
    if shard_count == 1:
        transition_lines = _make_figures_and_readout(df, out, K)

    manifest_extra = {
        "rows": int(len(df)),
        "units_total": int(len(units)),
        "shard": args.shard or "0/1",
        "offsets": offsets,
        "p_values": list(args.p_values),
    }
    (out / "run_manifest.json").write_text(
        json.dumps(build_run_manifest(args, ROOT, extra=manifest_extra), indent=2, default=str),
        encoding="utf-8",
    )

    write_caption(
        out / "tall_design_caption.md",
        "Experiment A -- Tall-Design Identifiability Threshold (r1)",
        [
            "Forward model: R_n = exp(ell_n) * (M_n . T), ell = U theta, generic Gaussian design M in R^{N x K}, "
            "Fourier low-pass gain basis U in R^{N x p} (p odd), theta ~ N(0, s^2) with s=%.2f, noiseless." % args.theta_std,
            "Panel (a) LOCAL RANK TEST: analytic Jacobian J = [R*U | exp(ell)*M]; local identifiability up to the single "
            "scale gauge holds iff rank(J) = p + K - 1 (rank in float64, threshold = rank_rtol * S_max, rank_rtol=%g)."
            % args.rank_rtol,
            "Panel (b) RECOVERY TEST: blind alternating minimisation (weighted-LS T-step + damped Gauss-Newton theta-step), "
            "gauge fixed to mean(ell)=0, up to %d restarts; success = scale-aligned relMSE(T) < %g AND "
            "max|ell_hat - ell| < %g." % (args.restarts, args.success_relmse, args.success_ell_max),
            *transition_lines,
            f"Grid: K={K}, p in {list(args.p_values)}, offsets(N-K-p) in {offsets}, seeds={args.seeds}. "
            f"Rows: {len(df)} (shard {args.shard or '0/1'}). Runtime seconds: {time.time() - start:.2f}.",
        ],
    )
    print(
        f"TallDesignThreshold complete rows={len(df)} shard={args.shard or '0/1'} output={out} "
        f"runtime={time.time() - start:.2f}s"
    )


def _make_figures_and_readout(df: pd.DataFrame, out: Path, K: int) -> List[str]:
    """Heatmap + rank-vs-recovery figure; returns caption lines with measured transitions."""

    # (1) Heatmap: solver success rate over (offset, p).
    pivot = df.pivot_table(index="p", columns="offset", values="solver_success", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    data = pivot.to_numpy(dtype=float)
    im = ax.imshow(data, aspect="auto", origin="lower", cmap="viridis", vmin=0.0, vmax=1.0)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([int(c) for c in pivot.columns])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([int(i) for i in pivot.index])
    ax.set_xlabel("N - K - p (measurement surplus)")
    ax.set_ylabel("p (gain-basis dimension)")
    ax.set_title("Solver success rate (blind recovery)")
    # Mark the two theoretical walls.
    if 0 in list(pivot.columns):
        ax.axvline(list(pivot.columns).index(0) - 0.5, color="white", linestyle="--", linewidth=1.0)
    fig.colorbar(im, ax=ax, label="success rate")
    fig.tight_layout()
    fig.savefig(out / "fig_threshold_heatmap.png", dpi=200)
    plt.close(fig)

    # (2) Rank-test vs solver-success transitions (aggregated across p and seeds).
    agg = df.groupby("offset").agg(
        rank_id_rate=("local_identifiable", "mean"),
        solver_rate=("solver_success", "mean"),
        n_cells=("solver_success", "count"),
    ).reset_index()
    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    ax.plot(agg["offset"], agg["rank_id_rate"], marker="o", label="local rank test (rank J = p+K-1)")
    ax.plot(agg["offset"], agg["solver_rate"], marker="s", label="blind solver success")
    ax.axvline(-1, color="tab:green", linestyle=":", linewidth=1.2, label="rank wall N=K+p-1")
    ax.axvline(0, color="tab:red", linestyle=":", linewidth=1.2, label="exact-ID wall N=K+p")
    ax.set_xlabel("N - K - p (measurement surplus)")
    ax.set_ylabel("rate over p and seeds")
    ax.set_ylim(-0.02, 1.02)
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False, fontsize=8)
    ax.set_title("Uniqueness (rank) vs conditioning (recovery) near the wall")
    fig.tight_layout()
    fig.savefig(out / "fig_rank_vs_recovery.png", dpi=200)
    plt.close(fig)

    # Measured transition locations.
    def _first_offset_at_least(column: str, rate: float) -> Optional[int]:
        hits = agg[agg[column] >= rate]["offset"]
        return int(hits.min()) if len(hits) else None

    # Cell-level exactness of the rank wall: rank_id == (N >= K+p-1) == (offset >= -1).
    df_local = df.assign(
        rank_pred=(df["offset"] >= -1),
    )
    rank_exact_frac = float((df_local["local_identifiable"] == df_local["rank_pred"]).mean())

    rank_on = _first_offset_at_least("rank_id_rate", 0.95)
    solver_on = _first_offset_at_least("solver_rate", 0.90)

    high_band = df[df["offset"] >= 4]["solver_success"].mean() if (df["offset"] >= 4).any() else float("nan")
    low_band = df[df["offset"] <= -4]["solver_success"].mean() if (df["offset"] <= -4).any() else float("nan")

    return [
        f"Measured rank-test wall: first offset with local-ID rate >= 0.95 is {rank_on} (theory: -1 = N=K+p-1); "
        f"cell-level agreement rank_id == (offset >= -1) is {rank_exact_frac:.3f} (acceptance >= 0.95).",
        f"Measured solver wall: first offset with success rate >= 0.90 is {solver_on} "
        "(algorithmic-recovery probe, not a uniqueness test; the N=K+p count of A'(ii) is not tested here).",
        f"Acceptance bands: solver success for offset >= +4 is {high_band:.3f} (target >= 0.90); "
        f"for offset <= -4 is {low_band:.3f} (target <= 0.10). The intermediate band may be ragged.",
    ]


if __name__ == "__main__":
    main()
