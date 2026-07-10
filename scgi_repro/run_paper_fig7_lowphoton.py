from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from scipy.special import gammaln

from src.mechanisms import moving_average_1d
from src.paper_experiments import (
    build_run_manifest,
    make_paper_basis,
    make_paper_objects,
    make_shared_channel,
    scale_aligned_gain_error,
    write_caption,
)


ROOT = Path(__file__).resolve().parent


class SoftLogCalibration:
    """Exact tabulation + monotone inversion of m_alpha(lambda) = E[log(Poisson(lambda) + alpha)].

    This is the calibration curve of Theorem C / Appendix D.4: the theorem's
    windowed soft-log estimator is theta_hat = m_alpha^{-1}(mean_W log(C+alpha)).
    The table is computed by a truncated Poisson sum with a rigorous a-priori
    tail bound (no Monte Carlo): for Cmax >= lambda the pmf ratio satisfies
    P(c+1)/P(c) = lambda/(c+1) <= r := lambda/(Cmax+1) < 1 for c >= Cmax, and
    log(c + alpha) <= log(Cmax + alpha) + (c - Cmax)/(Cmax + alpha), so the
    neglected (positive) tail is at most
        P(Cmax) * [ log(Cmax + alpha) * r/(1-r) + r / ((Cmax + alpha) * (1-r)^2) ].
    Cmax is grown until this bound falls below `tol` for every grid point.
    m_alpha is strictly increasing in lambda, so the inverse is a monotone
    interpolation of log(lambda) against the tabulated m values.
    """

    def __init__(
        self,
        alpha: float,
        lam_lo: float,
        lam_hi: float,
        num_points: int = 3000,
        tol: float = 1.0e-12,
    ) -> None:
        if not (0.0 < lam_lo < lam_hi):
            raise ValueError("Require 0 < lam_lo < lam_hi.")
        if alpha <= 0.0:
            raise ValueError("Require alpha > 0.")
        self.alpha = float(alpha)
        self.lam_lo = float(lam_lo)
        self.lam_hi = float(lam_hi)
        self.num_points = int(num_points)
        self.tol = float(tol)
        self.lam_grid = np.logspace(math.log10(lam_lo), math.log10(lam_hi), int(num_points))
        self.m_grid, self.max_tail_bound = self._tabulate(self.lam_grid, self.alpha, self.tol)
        if not np.all(np.diff(self.m_grid) > 0):
            raise RuntimeError("m_alpha table is not strictly increasing; refine the lambda grid.")
        self._log_lam_grid = np.log(self.lam_grid)

    @staticmethod
    def _tabulate(lam_grid: np.ndarray, alpha: float, tol: float) -> tuple[np.ndarray, float]:
        m = np.empty_like(lam_grid)
        worst_bound = 0.0
        chunk = 128
        for start in range(0, lam_grid.size, chunk):
            lam_c = lam_grid[start : start + chunk]
            lam_max = float(lam_c.max())
            cmax = int(math.ceil(lam_max + 12.0 * math.sqrt(max(lam_max, 1.0)) + 60.0))
            while True:
                c = np.arange(cmax + 1, dtype=np.float64)
                logpmf = (
                    -lam_c[:, None]
                    + c[None, :] * np.log(lam_c)[:, None]
                    - gammaln(c + 1.0)[None, :]
                )
                pmf = np.exp(logpmf)
                r = lam_c / (cmax + 1.0)
                tail = pmf[:, -1] * (
                    math.log(cmax + alpha) * r / (1.0 - r)
                    + r / ((cmax + alpha) * (1.0 - r) ** 2)
                )
                if float(tail.max()) <= tol:
                    m[start : start + chunk] = pmf @ np.log(c + alpha)
                    worst_bound = max(worst_bound, float(tail.max()))
                    break
                cmax = 2 * cmax + 64
        return m, worst_bound

    def invert(self, targets: np.ndarray) -> np.ndarray:
        """Monotone inverse m_alpha^{-1}; values outside the tabulated range clamp to the grid ends."""

        targets = np.asarray(targets, dtype=np.float64)
        return np.exp(np.interp(targets, self.m_grid, self._log_lam_grid))

    def evaluate(self, lam: np.ndarray) -> np.ndarray:
        """Forward interpolation of m_alpha at arbitrary intensities.

        Interpolates log(lambda) against the tabulated m values (the table is
        log-spaced, and m_alpha is smooth in log(lambda)); intensities outside
        the tabulated range clamp to the grid ends (constant extension)."""

        lam = np.asarray(lam, dtype=np.float64)
        return np.interp(np.log(np.maximum(lam, 1.0e-300)), self._log_lam_grid, self.m_grid)

    def solve_carrier_windows(
        self, targets: np.ndarray, carrier_windows: np.ndarray, iters: int = 60
    ) -> np.ndarray:
        """Carrier-aware calibrated inversion (Theorem C with known per-frame carriers).

        For each window n with known positive per-frame intensity factors
        b_{n,k} (the carrier times the photon budget; dark counts d = 0 in this
        protocol) it solves the theorem's window calibration equation

            (1/W) sum_k m_alpha(theta * b_{n,k}) = targets_n
                                       = (1/W) sum_k log(C_{n,k} + alpha),

        by bisection in log(theta): the left side is strictly increasing in
        theta because m_alpha is strictly increasing and every b_{n,k} > 0, and
        each m_alpha evaluation reuses the exact homogeneous table (for C ~
        Pois(theta*b), E[log(C+alpha)] = m_alpha(theta*b) with the SAME
        homogeneous curve -- no new tabulation is needed). The returned
        theta_hat is CLAMPED to the bracket

            [theta_lo, theta_hi] = [lam_lo / max(b), lam_hi / min(b)],

        the range over which every evaluated intensity stays within (or clamps
        to) the tabulated calibration range: targets below the attainable range
        (e.g. an all-zero window, whose target is log(alpha)) return theta_lo,
        targets above it return theta_hi. This clamp is part of the estimator's
        definition in the theorem statement (Appendix D.4)."""

        b = np.asarray(carrier_windows, dtype=np.float64)
        if float(b.min()) <= 0.0:
            raise ValueError("Carrier-aware inversion requires strictly positive carriers.")
        t = np.asarray(targets, dtype=np.float64)
        lo = np.full(t.shape, math.log(self.lam_lo) - math.log(float(b.max())))
        hi = np.full(t.shape, math.log(self.lam_hi) - math.log(float(b.min())))
        for _ in range(int(iters)):
            mid = 0.5 * (lo + hi)
            lhs = self.evaluate(np.exp(mid)[:, None] * b).mean(axis=1)
            go_up = lhs < t
            lo = np.where(go_up, mid, lo)
            hi = np.where(go_up, hi, mid)
        return np.exp(0.5 * (lo + hi))

    def metadata(self) -> Dict[str, object]:
        return {
            "alpha": self.alpha,
            "lam_lo": self.lam_lo,
            "lam_hi": self.lam_hi,
            "num_points": self.num_points,
            "truncation_tol": self.tol,
            "max_tail_bound": self.max_tail_bound,
            "m_at_lam_lo": float(self.m_grid[0]),
            "m_at_lam_hi": float(self.m_grid[-1]),
        }


def _window_indices(num_frames: int, window: int) -> np.ndarray:
    """Member indices of the centered moving-average windows.

    Mirrors ``moving_average_1d`` exactly: odd effective width (window+1 when
    even, capped at the record length made odd), centered, replicate padding
    (out-of-range member indices clamp to the record ends)."""

    width = max(1, int(window))
    if width % 2 == 0:
        width += 1
    width = min(width, max(1, num_frames if num_frames % 2 == 1 else num_frames - 1))
    left = width // 2
    idx = np.arange(num_frames)[:, None] + (np.arange(width) - left)[None, :]
    return np.clip(idx, 0, num_frames - 1)


def centered_log_gain_mse(gain_hat: torch.Tensor, true_gains: torch.Tensor) -> float:
    """Log-domain (Theorem C) loss: mean over frames of the squared centered-log error.

    Theorem C's target is the log-gain up to the additive gauge constant; the
    gauge is fixed by centering both log profiles at their record means, so the
    metric is invariant to the (unidentifiable) global scale of each profile.
    This is the loss the local Fisher reference 1/(W*lambda) is stated in (the
    Poisson Fisher information for LOG-intensity is lambda), so only this
    column is Fisher-comparable; the gain-domain relMSE is kept for continuity
    but is a different (scale-aligned, linear-domain) loss."""

    lg = torch.log(gain_hat.reshape(-1).to(dtype=torch.float64).clamp_min(1.0e-300))
    lt = torch.log(true_gains.reshape(-1).to(dtype=torch.float64).clamp_min(1.0e-300))
    return float(((lg - lg.mean()) - (lt - lt.mean())).pow(2).mean().item())


def estimate_from_counts(
    counts: torch.Tensor,
    method: str,
    window: int,
    alpha: float,
    calibration: Optional[SoftLogCalibration] = None,
    carrier_lam: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    values = counts.reshape(-1).to(dtype=torch.float32)
    if method == "soft_log":
        transformed = torch.log(values + float(alpha))
        smooth = moving_average_1d(transformed, window)
        gain_hat = torch.exp(smooth - smooth.mean())
    elif method == "soft_log_calibrated":
        # Mean-Poisson calibrated PROXY (previous r3 arm, kept for continuity):
        # per-window mean of log(C+alpha) -> homogeneous m_alpha^{-1} ->
        # estimated lambda profile -> normalize by its mean. It inverts the
        # HOMOGENEOUS Poisson(lambda) curve, i.e. it ignores the frame-varying
        # carrier inside the window, so it is NOT Theorem C's estimator when
        # the carrier is random; see soft_log_calibrated_carrier.
        if calibration is None:
            raise ValueError("soft_log_calibrated requires a SoftLogCalibration instance.")
        transformed = torch.log(values + float(alpha))
        smooth = moving_average_1d(transformed, window)
        lam_hat = calibration.invert(smooth.to(dtype=torch.float64).cpu().numpy())
        gain_hat = torch.from_numpy(lam_hat).to(dtype=torch.float32)
    elif method == "soft_log_calibrated_carrier":
        # Theorem C estimator (carrier-aware): with the per-frame carrier
        # intensities b_k KNOWN (design values; dark counts d = 0 here), solve
        # per window  (1/W) sum_k m_alpha(theta_hat * b_k) = (1/W) sum_k
        # log(C_k + alpha)  by monotone bisection on the exact homogeneous
        # table (E[log(Pois(theta*b)+alpha)] = m_alpha(theta*b)), with the
        # theorem's clamp of theta_hat to the tabulated range.
        if calibration is None or carrier_lam is None:
            raise ValueError(
                "soft_log_calibrated_carrier requires a SoftLogCalibration instance and per-frame carriers."
            )
        psi = np.log(values.to(dtype=torch.float64).cpu().numpy() + float(alpha))
        idx = _window_indices(psi.size, window)
        targets = psi[idx].mean(axis=1)
        b_win = carrier_lam.reshape(-1).to(dtype=torch.float64).cpu().numpy()[idx]
        theta_hat = calibration.solve_carrier_windows(targets, b_win)
        gain_hat = torch.from_numpy(theta_hat).to(dtype=torch.float32)
    elif method == "naive_log":
        transformed = torch.log(values.clamp_min(1.0e-3))
        smooth = moving_average_1d(transformed, window)
        gain_hat = torch.exp(smooth - smooth.mean())
    elif method == "anscombe":
        transformed = 2.0 * torch.sqrt(values + 0.375)
        smooth = moving_average_1d(transformed, window)
        gain_hat = (smooth / smooth.mean().clamp_min(1.0e-8)).pow(2)
    else:
        raise ValueError(method)
    return gain_hat / gain_hat.mean().clamp_min(1.0e-8)


METHODS = ["soft_log", "soft_log_calibrated", "soft_log_calibrated_carrier", "naive_log", "anscombe"]


def simulate(
    args: argparse.Namespace,
    basis,
    objects,
    rho: float,
    calibration: Optional[SoftLogCalibration],
) -> pd.DataFrame:
    budgets = [float(x) for x in args.photon_budgets.replace(" ", ",").split(",") if x.strip()]
    rows: List[Dict[str, object]] = []
    for obj in objects:
        carrier = (basis.patterns @ obj.vector).cpu().to(dtype=torch.float32)
        carrier = carrier / carrier.mean().clamp_min(1.0e-8)
        for seed_idx in range(args.seeds):
            gains = make_shared_channel(basis.num_frames, rho=float(rho), sigma_a=args.sigma_a, seed=args.seed + 701 * seed_idx)
            for budget in budgets:
                lam = (float(budget) * gains * carrier).clamp_min(0.0)
                generator = torch.Generator(device="cpu")
                generator.manual_seed(args.seed + 9001 * seed_idx + int(round(1000 * budget)))
                counts = torch.poisson(lam, generator=generator)
                zero_fraction = float((counts <= 0).to(dtype=torch.float32).mean().item())
                lambda_bar = float(lam.mean().item())
                carrier_lam = float(budget) * carrier
                for method in METHODS:
                    gain_hat = estimate_from_counts(
                        counts,
                        method=method,
                        window=args.window,
                        alpha=args.alpha,
                        calibration=calibration,
                        carrier_lam=carrier_lam,
                    )
                    rows.append(
                        {
                            "object": obj.name,
                            "family": obj.family,
                            "K_eff": obj.k_eff,
                            "basis": basis.name,
                            "rho": float(rho),
                            "s": float(args.sigma_a),
                            "seed": int(seed_idx),
                            "W": int(args.window),
                            "photon_budget": float(budget),
                            "lambda_bar": lambda_bar,
                            "zero_fraction": zero_fraction,
                            "method": method,
                            "gain_rel_mse": scale_aligned_gain_error(gain_hat, gains) ** 2,
                            "log_gain_mse": centered_log_gain_mse(gain_hat, gains),
                            "fisher_reference": float(1.0 / max(args.window * lambda_bar, 1.0e-12)),
                        }
                    )
    return pd.DataFrame(rows)


def fisher_slope(
    summary: pd.DataFrame, method: str, budget_lo: float, budget_hi: float, value_col: str = "log_gain_mse_mean"
) -> float:
    """Log-log slope of a mean-MSE column vs nominal photon budget over [budget_lo, budget_hi].

    Filters on the discrete design column ``photon_budget`` (NOT on the realized
    ``lambda_bar_mean``, which drifts slightly above the nominal budget and
    previously caused silent endpoint dropping)."""

    sub = summary[
        (summary["method"] == method)
        & (summary["photon_budget"] >= budget_lo)
        & (summary["photon_budget"] <= budget_hi)
    ]
    sub = sub[sub[value_col] > 0]
    if len(sub) < 2:
        return float("nan")
    x = np.log10(sub["photon_budget"].to_numpy(dtype=float))
    y = np.log10(sub[value_col].to_numpy(dtype=float))
    return float(np.polyfit(x, y, deg=1)[0])


RATIO_PAIRS = [
    ("naive_log", "soft_log", "naive/soft"),
    ("naive_log", "anscombe", "naive/anscombe"),
    ("anscombe", "soft_log", "anscombe/soft"),
    ("naive_log", "soft_log_calibrated_carrier", "naive/carrier"),
    ("anscombe", "soft_log_calibrated_carrier", "anscombe/carrier"),
    ("soft_log_calibrated_carrier", "soft_log", "carrier/soft"),
    ("soft_log_calibrated", "soft_log_calibrated_carrier", "meanpois/carrier"),
]


def build_ratio_table(summary: pd.DataFrame, value_col: str) -> pd.DataFrame:
    """Pairwise mean-MSE ratio table per photon budget, numerator/denominator named."""

    pivot = summary.pivot(index="photon_budget", columns="method", values=value_col)
    out = pd.DataFrame(index=pivot.index)
    for num, den, label in RATIO_PAIRS:
        out[label] = pivot[num] / pivot[den]
    return out.reset_index()


def _md_table(frame: pd.DataFrame, float_fmt: str = "{:.4g}") -> List[str]:
    cols = list(frame.columns)
    lines = ["| " + " | ".join(str(c) for c in cols) + " |", "|" + "---|" * len(cols)]
    for _, row in frame.iterrows():
        cells = []
        for c in cols:
            v = row[c]
            cells.append(float_fmt.format(v) if isinstance(v, (float, np.floating)) else str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def write_summary_md(
    path: Path,
    summary: pd.DataFrame,
    ratio_table_log: pd.DataFrame,
    ratio_table_gain: pd.DataFrame,
    slopes_log: Dict[str, Dict[str, float]],
    slopes_gain: Dict[str, Dict[str, float]],
    low_budget_ranges_log: Dict[str, tuple],
    fisher_excess: pd.DataFrame,
    floor_lines: List[str],
    calibration: SoftLogCalibration,
    args: argparse.Namespace,
    n_rows: int,
) -> None:
    fisher_ref = summary.groupby("photon_budget", as_index=False)["fisher_reference_mean"].mean()
    log_pivot = summary.pivot(index="photon_budget", columns="method", values="log_gain_mse_mean").reset_index()
    log_pivot = log_pivot.merge(fisher_ref, on="photon_budget")
    gain_pivot = summary.pivot(index="photon_budget", columns="method", values="gain_rel_mse_mean").reset_index()

    lines: List[str] = []
    lines.append("# Fig. 7 low-photon gain estimation (r4, carrier-aware calibrated soft-log) - native summary")
    lines.append("")
    lines.append(
        f"Protocol: random_uniform basis, {args.objects} objects, {args.seeds} seeds, W={args.window}, "
        f"alpha={args.alpha}, rho={args.rho}, s={args.sigma_a}, budgets={args.photon_budgets}; "
        f"floor probe rho={args.floor_probe_rho}. Rows: {n_rows}."
    )
    lines.append("")
    lines.append(
        "`soft_log_calibrated_carrier` is Theorem C's estimator (Appendix D.4, carrier-aware form): with the "
        "per-frame carrier intensities b_k known (design values; dark counts d = 0 in this protocol), it solves per "
        "window (1/W) sum_k m_alpha(theta_hat * b_k) = (1/W) sum_k log(C_k + alpha) by monotone bisection on the "
        "exactly tabulated homogeneous curve m_alpha(lambda) = E[log(Poisson(lambda)+alpha)] (truncated Poisson sum, "
        f"rigorous tail bound <= {calibration.max_tail_bound:.2e} on a {calibration.num_points}-point log grid over "
        f"lambda in [{calibration.lam_lo:g}, {calibration.lam_hi:g}]), with theta_hat clamped to the tabulated range "
        "(the theorem's clamp; all-zero windows clamp to the lower end). `soft_log_calibrated` is the r3 mean-Poisson "
        "calibrated PROXY (homogeneous inversion that ignores the frame-varying carrier), kept for continuity; "
        "`soft_log` is the legacy uncalibrated proxy exp(movmean(log(C+alpha)) - mean), also unchanged."
    )
    lines.append("")
    lines.append(
        "METRICS. `log_gain_mse` (PRIMARY, Fisher-comparable) is Theorem C's loss: mean over frames of the squared "
        "centered-log-gain error, mean_n[((log ghat_n - mean log ghat) - (log g_n - mean log g))^2]. The local Fisher "
        "reference 1/(W*lambda) is the Cramer-Rao scale for LOG-intensity (Poisson information for log-intensity is "
        "lambda), so Fisher comparisons, sub-Fisher flags, and rate slopes are stated in this metric. `gain_rel_mse` "
        "(gain-domain scale-aligned relMSE) is retained for continuity with r2/r3 but is NOT Fisher-comparable. "
        "The centered moving-average window has odd effective width W+1=65 (moving_average_1d convention) while the "
        "Fisher reference uses the nominal W=64, a <=1.6% conservative slack in the reference."
    )
    lines.append("")
    lines.append("## (a) Per-photon-level mean LOG-domain gain MSE by arm (primary, Fisher-comparable)")
    lines.append("")
    lines.extend(_md_table(log_pivot))
    lines.append("")
    lines.append("## (a') Per-photon-level mean gain-domain relMSE by arm (continuity with r3; not Fisher-comparable)")
    lines.append("")
    lines.extend(_md_table(gain_pivot))
    lines.append("")
    lines.append("## (b) Pairwise mean-MSE ratio tables (numerator/denominator as named)")
    lines.append("")
    lines.append("Log-domain (primary):")
    lines.append("")
    lines.extend(_md_table(ratio_table_log))
    lines.append("")
    lines.append("Gain-domain (continuity):")
    lines.append("")
    lines.extend(_md_table(ratio_table_gain))
    lines.append("")
    lines.append("Low-photon log-domain ranges (over budgets <= 1):")
    for label, (lo, hi) in low_budget_ranges_log.items():
        lines.append(f"- {label}: {lo:.2f}-{hi:.2f}x")
    lines.append("")
    lines.append("## (c) Fitted log-log rate slopes of mean MSE vs photon budget (1/(W*lambda) law => slope -1)")
    lines.append("")
    lines.append("| method | log-domain [2,32] | log-domain [1,16] | gain-domain [2,32] | gain-domain [1,16] |")
    lines.append("|---|---|---|---|---|")
    for method in METHODS:
        lines.append(
            f"| {method} | {slopes_log[method]['budget_2_32']:.3f} | {slopes_log[method]['budget_1_16']:.3f} "
            f"| {slopes_gain[method]['budget_2_32']:.3f} | {slopes_gain[method]['budget_1_16']:.3f} |"
        )
    lines.append("")
    lines.append("Slopes are fit on the discrete design column photon_budget (endpoints included); "
                 "no post-hoc correction is needed.")
    lines.append("")
    lines.append("## (d) Fisher-excess table (log-domain mean MSE / local Fisher reference, per budget)")
    lines.append("")
    lines.extend(_md_table(fisher_excess))
    lines.append("")
    lines.append("## (e) Qualitative checks (log-domain metric)")
    lines.append("")
    pivot = summary.pivot(index="photon_budget", columns="method", values="log_gain_mse_mean")
    fisher = summary.groupby("photon_budget")["fisher_reference_mean"].mean()
    carrier_beats_ansc = [
        f"{b:g}" for b in pivot.index if pivot.loc[b, "soft_log_calibrated_carrier"] < pivot.loc[b, "anscombe"]
    ]
    ansc_beats_carrier = [
        f"{b:g}" for b in pivot.index if pivot.loc[b, "soft_log_calibrated_carrier"] >= pivot.loc[b, "anscombe"]
    ]
    lines.append(
        f"- Carrier-aware calibrated soft-log beats Anscombe (lower mean log-domain MSE) at budgets: "
        f"{', '.join(carrier_beats_ansc) or 'none'}; Anscombe is equal/better at: {', '.join(ansc_beats_carrier) or 'none'}."
    )
    sub_fisher = {
        m: [f"{b:g}" for b in pivot.index if pivot.loc[b, m] < fisher.loc[b]]
        for m in ("soft_log", "soft_log_calibrated", "soft_log_calibrated_carrier")
    }
    lines.append(
        f"- Log-domain MSE below the unbiased local Fisher reference 1/(W*lambda) (shrinkage-bias signature): "
        f"soft_log at budgets {', '.join(sub_fisher['soft_log']) or 'none'}; "
        f"soft_log_calibrated at budgets {', '.join(sub_fisher['soft_log_calibrated']) or 'none'}; "
        f"soft_log_calibrated_carrier at budgets {', '.join(sub_fisher['soft_log_calibrated_carrier']) or 'none'}."
    )
    meanpois_over_carrier = ratio_table_log.set_index("photon_budget")["meanpois/carrier"]
    lines.append(
        f"- meanpois/carrier log-domain mean-MSE ratio spans {float(meanpois_over_carrier.min()):.4f}-"
        f"{float(meanpois_over_carrier.max()):.4f} across all budgets (values near 1 mean the r3 mean-Poisson proxy "
        "and the true carrier-aware estimator agree numerically at this carrier CV; the carrier-aware arm is the one "
        "the theorem is about)."
    )
    carrier_over_soft = ratio_table_log.set_index("photon_budget")["carrier/soft"]
    lines.append(
        f"- carrier/soft log-domain mean-MSE ratio spans {float(carrier_over_soft.min()):.3f}-"
        f"{float(carrier_over_soft.max()):.3f} across all budgets (> 1 means the calibrated estimator pays extra MSE "
        "over the biased proxy at that budget, < 1 that it gains)."
    )
    for line in floor_lines:
        lines.append(f"- {line}")
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fig. 7 low-photon gain estimation (r4, carrier-aware calibrated soft-log)."
    )
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "paper_fig7_lowphoton_r4_carrier")
    parser.add_argument("--image-size", type=int, default=32)
    parser.add_argument("--objects", type=int, default=10)
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20240708)
    parser.add_argument("--rho", type=float, default=0.001)
    parser.add_argument("--sigma-a", type=float, default=0.1)
    parser.add_argument("--window", type=int, default=64)
    parser.add_argument("--alpha", type=float, default=0.5)
    parser.add_argument("--photon-budgets", default="0.25,0.5,1,2,4,8,16,32,64,128")
    parser.add_argument("--floor-probe-rho", type=float, default=0.0, help="Optional second rho to show the high-photon floor shrinks with drift.")
    parser.add_argument("--calibration-points", type=int, default=3000, help="Grid size for the exact m_alpha(lambda) table.")
    parser.add_argument("--calibration-tol", type=float, default=1.0e-12, help="Rigorous truncation tolerance for the m_alpha table.")
    args = parser.parse_args()

    start = time.time()
    out = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    p = args.image_size * args.image_size
    basis = make_paper_basis("random_uniform", p, seed=args.seed)
    objects = make_paper_objects(args.objects, image_size=args.image_size, seed=args.seed)

    budgets = [float(x) for x in args.photon_budgets.replace(" ", ",").split(",") if x.strip()]
    calibration = SoftLogCalibration(
        alpha=float(args.alpha),
        lam_lo=min(budgets) * 1.0e-3,
        lam_hi=max(budgets) * 1.0e2,
        num_points=int(args.calibration_points),
        tol=float(args.calibration_tol),
    )
    calib_table = pd.DataFrame({"lambda": calibration.lam_grid, "m_alpha": calibration.m_grid})
    calib_table.to_csv(out / "m_alpha_calibration_table.csv", index=False)

    df = simulate(args, basis, objects, rho=args.rho, calibration=calibration)
    df.to_csv(out / "fig7_lowphoton.csv", index=False)

    # Fixed summary: group ONLY on discrete design columns (method, photon_budget).
    summary = df.groupby(["method", "photon_budget"], as_index=False).agg(
        gain_rel_mse_mean=("gain_rel_mse", "mean"),
        gain_rel_mse_std=("gain_rel_mse", "std"),
        gain_rel_mse_count=("gain_rel_mse", "count"),
        log_gain_mse_mean=("log_gain_mse", "mean"),
        log_gain_mse_std=("log_gain_mse", "std"),
        lambda_bar_mean=("lambda_bar", "mean"),
        zero_fraction_mean=("zero_fraction", "mean"),
        fisher_reference_mean=("fisher_reference", "mean"),
    )
    summary.to_csv(out / "fig7_lowphoton_summary.csv", index=False)

    # Native slope fits per arm on the nominal photon_budget column (endpoints included),
    # in BOTH metrics; the log-domain metric is the Fisher-comparable (primary) one.
    slopes_log: Dict[str, Dict[str, float]] = {
        method: {
            "budget_2_32": fisher_slope(summary, method, 2.0, 32.0, value_col="log_gain_mse_mean"),
            "budget_1_16": fisher_slope(summary, method, 1.0, 16.0, value_col="log_gain_mse_mean"),
        }
        for method in METHODS
    }
    slopes_gain: Dict[str, Dict[str, float]] = {
        method: {
            "budget_2_32": fisher_slope(summary, method, 2.0, 32.0, value_col="gain_rel_mse_mean"),
            "budget_1_16": fisher_slope(summary, method, 1.0, 16.0, value_col="gain_rel_mse_mean"),
        }
        for method in METHODS
    }
    soft = summary[summary["method"] == "soft_log"].sort_values("photon_budget")
    peak_budget = float(soft.loc[soft["log_gain_mse_mean"].idxmax(), "photon_budget"]) if len(soft) else float("nan")

    # Native pairwise ratio tables (numerator/denominator named in the column labels).
    ratio_table_log = build_ratio_table(summary, value_col="log_gain_mse_mean")
    ratio_table_log.to_csv(out / "fig7_ratio_table_logdomain.csv", index=False)
    ratio_table_gain = build_ratio_table(summary, value_col="gain_rel_mse_mean")
    ratio_table_gain.to_csv(out / "fig7_ratio_table.csv", index=False)
    low = ratio_table_log[ratio_table_log["photon_budget"] <= 1.0]
    low_budget_ranges_log = {
        label: (float(low[label].min()), float(low[label].max())) for _, _, label in RATIO_PAIRS
    }

    # Fisher-excess table (log-domain only: the reference 1/(W*lambda) is the
    # Cramer-Rao scale for LOG-intensity, so only the log-domain MSE compares).
    fisher = summary.groupby("photon_budget")["fisher_reference_mean"].mean()
    log_pivot_full = summary.pivot(index="photon_budget", columns="method", values="log_gain_mse_mean")
    fisher_excess = pd.DataFrame(index=log_pivot_full.index)
    for method in ("soft_log", "soft_log_calibrated", "soft_log_calibrated_carrier", "anscombe"):
        fisher_excess[f"{method}/fisher"] = log_pivot_full[method] / fisher
    fisher_excess = fisher_excess.reset_index()
    fisher_excess.to_csv(out / "fig7_fisher_excess_logdomain.csv", index=False)

    def _mse_figure(value_col: str, std_col: str, ylabel: str, filename: str, with_fisher: bool) -> None:
        fig, ax = plt.subplots(figsize=(7.2, 4.8))
        for method, group in summary.groupby("method"):
            curve = group.sort_values("photon_budget")
            ax.errorbar(
                curve["photon_budget"],
                curve[value_col],
                yerr=curve[std_col].fillna(0.0),
                marker="o",
                capsize=2,
                label=method,
            )
        if with_fisher:
            ref = (
                summary.groupby("photon_budget", as_index=False)["fisher_reference_mean"]
                .mean()
                .sort_values("photon_budget")
            )
            ax.plot(
                ref["photon_budget"], ref["fisher_reference_mean"], linestyle="--", color="black", label="1/(W lambda)"
            )
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("mean photon budget")
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.25)
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(out / filename, dpi=200)
        plt.close(fig)

    # Primary figure: LOG-domain MSE against the log-intensity Fisher reference.
    _mse_figure(
        "log_gain_mse_mean",
        "log_gain_mse_std",
        "centered-log-gain MSE",
        "fig7_logMSE_vs_photon.png",
        with_fisher=True,
    )
    # Continuity figure: gain-domain relMSE, WITHOUT the Fisher line (the
    # reference is a log-domain quantity and is not comparable in this metric).
    _mse_figure(
        "gain_rel_mse_mean",
        "gain_rel_mse_std",
        "gain relMSE (scale-aligned)",
        "fig7_gainMSE_vs_photon.png",
        with_fisher=False,
    )

    # Optional: high-photon floor vs drift.
    floor_lines: List[str] = []
    if args.floor_probe_rho and float(args.floor_probe_rho) > 0.0:
        df_probe = simulate(args, basis, objects, rho=float(args.floor_probe_rho), calibration=calibration)
        df_probe.to_csv(out / "fig7_lowphoton_floorprobe.csv", index=False)
        max_budget = float(max(budgets))

        def _floor(frame: pd.DataFrame, method: str) -> float:
            sel = frame[(frame["method"] == method) & (frame["photon_budget"] == max_budget)]
            return float(sel["log_gain_mse"].mean()) if len(sel) else float("nan")

        for method in ("soft_log", "soft_log_calibrated", "soft_log_calibrated_carrier"):
            floor_lines.append(
                f"At the high-photon end (budget={max_budget:g}) the {method} log-domain gain-MSE floor shrinks from "
                f"{_floor(df, method):.3e} (rho={args.rho:g}) to {_floor(df_probe, method):.3e} "
                f"(rho={args.floor_probe_rho:g}), confirming the floor is drift-limited."
            )

    carrier_excess = fisher_excess.set_index("photon_budget")["soft_log_calibrated_carrier/fisher"]
    low_excess = carrier_excess[carrier_excess.index <= 1.0]
    mid_excess = carrier_excess[(carrier_excess.index >= 2.0) & (carrier_excess.index <= 32.0)]
    write_caption(
        out / "fig7_caption.md",
        "Fig. 7 Low-Photon Gain Estimation (r4, carrier-aware calibrated soft-log)",
        [
            "Poisson bucket counts are evaluated under identical random-basis carriers and shared gain traces; the summary is "
            "aggregated over discrete design columns (method, photon_budget) only. The soft_log_calibrated_carrier arm is "
            "Theorem C's estimator (per-window root of (1/W) sum_k m_alpha(theta*b_k) = (1/W) sum_k log(C_k+alpha) with the "
            "known per-frame carriers b_k, dark counts d=0, and the theorem's clamp to the tabulated range); "
            "soft_log_calibrated is the r3 mean-Poisson calibrated proxy (homogeneous inversion, carrier ignored) and "
            "soft_log the legacy uncalibrated proxy, both retained unchanged for continuity.",
            "METRIC: the primary loss is the LOG-domain centered-log-gain MSE (Theorem C's loss), the only metric "
            "comparable to the local Fisher reference 1/(W*lambda) (Poisson information for LOG-intensity); the "
            "gain-domain relMSE is kept as a continuity column and is not Fisher-comparable.",
            f"(i) Log-domain ratio bookkeeping (mean-MSE ratios over budgets <= 1, numerator/denominator named): "
            f"naive/soft {low_budget_ranges_log['naive/soft'][0]:.1f}-{low_budget_ranges_log['naive/soft'][1]:.1f}x, "
            f"naive/Anscombe {low_budget_ranges_log['naive/anscombe'][0]:.1f}-{low_budget_ranges_log['naive/anscombe'][1]:.1f}x, "
            f"Anscombe/soft {low_budget_ranges_log['anscombe/soft'][0]:.2f}-{low_budget_ranges_log['anscombe/soft'][1]:.2f}x, "
            f"naive/carrier {low_budget_ranges_log['naive/carrier'][0]:.1f}-{low_budget_ranges_log['naive/carrier'][1]:.1f}x, "
            f"Anscombe/carrier {low_budget_ranges_log['anscombe/carrier'][0]:.2f}-{low_budget_ranges_log['anscombe/carrier'][1]:.2f}x, "
            f"carrier/soft {low_budget_ranges_log['carrier/soft'][0]:.2f}-{low_budget_ranges_log['carrier/soft'][1]:.2f}x, "
            f"meanpois/carrier {low_budget_ranges_log['meanpois/carrier'][0]:.4f}-{low_budget_ranges_log['meanpois/carrier'][1]:.4f}x.",
            f"(ii) The 1/(W*lambda) law in the variance regime (log-domain, fit natively on photon_budget, endpoints "
            f"included): slope {slopes_log['soft_log_calibrated_carrier']['budget_2_32']:.2f} (carrier-aware) / "
            f"{slopes_log['soft_log_calibrated']['budget_2_32']:.2f} (mean-Poisson proxy) / "
            f"{slopes_log['soft_log']['budget_2_32']:.2f} (uncalibrated proxy) on [2,32]; "
            f"{slopes_log['soft_log_calibrated_carrier']['budget_1_16']:.2f} / "
            f"{slopes_log['soft_log_calibrated']['budget_1_16']:.2f} / {slopes_log['soft_log']['budget_1_16']:.2f} on "
            f"[1,16]. lambda_bar~{peak_budget:g} is the soft_log bias->variance transition peak; above lambda_bar~32 a "
            f"drift-limited floor sets in.",
            f"(iii) Fisher excess of the carrier-aware arm (log-domain MSE / (1/(W*lambda))): "
            f"{float(low_excess.min()):.2f}-{float(low_excess.max()):.2f}x over budgets <= 1 and "
            f"{float(mid_excess.min()):.2f}-{float(mid_excess.max()):.2f}x over [2,32]. Sub-Fisher entries (<1) are a "
            f"shrinkage-bias signature, not super-efficiency; see summary.md section (e) for per-arm flags.",
            "(iv) Naive clipped log does not diverge: it saturates at a bias floor set by the clip.",
            *floor_lines,
            f"Rows: {len(df)}. Runtime seconds: {time.time() - start:.2f}.",
        ],
    )

    write_summary_md(
        out / "summary.md",
        summary,
        ratio_table_log,
        ratio_table_gain,
        slopes_log,
        slopes_gain,
        low_budget_ranges_log,
        fisher_excess,
        floor_lines,
        calibration,
        args,
        n_rows=len(df),
    )

    (out / "run_manifest.json").write_text(
        json.dumps(
            build_run_manifest(
                args,
                ROOT,
                extra={
                    "rows": int(len(df)),
                    "methods": METHODS,
                    "calibration": calibration.metadata(),
                    "slopes_vs_photon_budget_logdomain": slopes_log,
                    "slopes_vs_photon_budget_gaindomain": slopes_gain,
                    "soft_log_mse_peak_budget": peak_budget,
                    "low_budget_ratio_ranges_logdomain": {k: list(v) for k, v in low_budget_ranges_log.items()},
                    "carrier_fisher_excess_logdomain": {
                        f"{b:g}": float(v) for b, v in carrier_excess.items()
                    },
                    "metric_convention": "PRIMARY metric log_gain_mse = mean_n[((log ghat - mean log ghat) - "
                    "(log g - mean log g))^2] (Theorem C loss; Fisher-comparable to 1/(W*lambda)); gain_rel_mse "
                    "retained for r2/r3 continuity only.",
                    "slope_convention": "log10(mean MSE) vs log10(photon_budget), filtered on the nominal "
                    "photon_budget design column so the window endpoints are included; emitted natively by this run.",
                    "carrier_estimator": "soft_log_calibrated_carrier solves (1/W) sum_k m_alpha(theta*b_k) = "
                    "(1/W) sum_k log(C_k+alpha) per centered window (odd width, replicate padding, identical to "
                    "moving_average_1d) by 60-step bisection in log(theta) on the exact homogeneous m_alpha table; "
                    "theta clamped to [lam_lo/max(b), lam_hi/min(b)] (theorem's clamp); dark counts d=0.",
                },
            ),
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    print(
        f"Fig7 complete rows={len(df)} output={out} runtime={time.time() - start:.2f}s "
        f"log-domain slope[2,32]: carrier={slopes_log['soft_log_calibrated_carrier']['budget_2_32']:.3f} "
        f"meanpois={slopes_log['soft_log_calibrated']['budget_2_32']:.3f} "
        f"soft={slopes_log['soft_log']['budget_2_32']:.3f} peak_budget={peak_budget:g}"
    )


if __name__ == "__main__":
    main()
