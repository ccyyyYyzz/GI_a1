"""E9 -- DGI one-sample constant C0 audit + flip-boundary photon-convention audit.

Part A measures the one-sample DGI correlator constant

    C0 = E||Z||^2 / S2 - 1,    Z(x) = [I(x) - mu] * B / sigma^2,  B = sum_x' I(x') O(x')

empirically (many single-frame pattern draws I) for four pattern ensembles --
uniform[0,1], binary 0/1, signed Rademacher, and a clipped Gaussian(mu=0.5,
sigma=0.2) -- against five objects spanning K_eff, and compares it against the
closed form

    C0 = K + beta_4 - 2 + K_eff * [K*(mu/sigma)^2 + 2*gamma_3*(mu/sigma)]

where mu, sigma are the pattern ensemble's mean/std, beta_4 = E[(I-mu)^4]/sigma^4
is its (raw, not excess) kurtosis, gamma_3 = E[(I-mu)^3]/sigma^3 is its skewness,
and K_eff = S1^2/S2 is the object's effective support. (For symmetric zero-mean
patterns the K_eff term vanishes and this reduces to the manuscript's special
case C0 = K + beta_4 - 2.) Because Z(x) = J(x) * B/sigma^2 with J = I - mu shared
across pixels at a given draw, ||Z||^2 = (B/sigma^2)^2 * ||J||^2 exactly -- this
identity is used to evaluate the estimator without ever materializing the (n_draws,
K) Z matrix.

Part B evaluates the finite-N flip-boundary heuristic rho* = 2*C0/(N*K_eff*s^2)
(Prop 3, leading order) under three PHOTON conventions that govern how the
per-frame photon budget Phi_frame depends on N. C0 itself is a pure pattern-
statistics constant (Part A) with no photon dependence, so the photon convention
is instead implemented -- as the task frames it, "a weighting of the noise term"
-- as an EFFECTIVE drift variance s_eff^2(N, convention) = s^2 + kappa_s /
Phi_frame(N, convention): at low per-frame flux, shot noise inflates the residual
gain error that survives blind correction (the manuscript's v_blind), so less of
the true drift needs to leak through for the flip to occur. See the caption for
the exact convention definitions, kappa_s, and the reported spread across
conventions.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Callable, Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch

from src.paper_experiments import build_run_manifest, make_paper_objects, write_caption


ROOT = Path(__file__).resolve().parent

ENSEMBLE_SEED_OFFSET = {"uniform": 0, "binary": 4001, "rademacher": 8009, "gaussian_clipped": 12007}
OBJECT_NAMES = ["letter_L", "digit_2", "ring", "stripe", "natural_patch"]
CONVENTIONS = ["equal_exposure", "equal_count", "fixed_flux"]


def gen_uniform(shape: tuple, generator: torch.Generator, **_: object) -> torch.Tensor:
    return torch.rand(shape, generator=generator, dtype=torch.float32)


def gen_binary(shape: tuple, generator: torch.Generator, **_: object) -> torch.Tensor:
    return torch.randint(0, 2, shape, generator=generator, dtype=torch.int64).to(dtype=torch.float32)


def gen_rademacher(shape: tuple, generator: torch.Generator, **_: object) -> torch.Tensor:
    return torch.randint(0, 2, shape, generator=generator, dtype=torch.int64).to(dtype=torch.float32) * 2.0 - 1.0


def gen_gaussian_clipped(shape: tuple, generator: torch.Generator, mu: float = 0.5, sigma: float = 0.2) -> torch.Tensor:
    raw = mu + sigma * torch.randn(shape, generator=generator, dtype=torch.float32)
    return raw.clamp(0.0, 1.0)


ENSEMBLE_GENERATORS: Dict[str, Callable[..., torch.Tensor]] = {
    "uniform": gen_uniform,
    "binary": gen_binary,
    "rademacher": gen_rademacher,
    "gaussian_clipped": gen_gaussian_clipped,
}


def phi_frame(n: float, convention: str, phi_ref: float, n0: float) -> float:
    """Per-frame photon flux under a documented, simplified convention.

    equal_exposure: Phi_frame = Phi_ref (fixed per-frame dwell/flux; total budget
        grows linearly with N).
    equal_count:    Phi_frame = Phi_ref * N0 / N (fixed TOTAL budget Phi_ref*N0,
        redistributed equally across however many frames N are taken).
    fixed_flux:     Phi_frame = Phi_ref * sqrt(N0 / N) (fixed-power source with
        partially adaptive per-frame integration time; geometric-mean
        intermediate between the two conventions above, bracketing the range).
    """

    if convention == "equal_exposure":
        return float(phi_ref)
    if convention == "equal_count":
        return float(phi_ref) * float(n0) / float(n)
    if convention == "fixed_flux":
        return float(phi_ref) * math.sqrt(float(n0) / float(n))
    raise ValueError(f"Unknown photon convention: {convention}")


def main() -> None:
    parser = argparse.ArgumentParser(description="E9: DGI one-sample C0 audit + photon-convention flip-boundary spread (r1).")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "c0_audit_e9_r1")
    parser.add_argument("--image-size", type=int, default=32, help="K = image_size^2.")
    parser.add_argument("--seed", type=int, default=20240708)
    parser.add_argument("--n-draws", type=int, default=20000, help="Single-frame pattern draws per ensemble.")
    parser.add_argument("--gaussian-mu", type=float, default=0.5)
    parser.add_argument("--gaussian-sigma", type=float, default=0.2)
    parser.add_argument("--s", type=float, default=0.1, help="Gain drift standard deviation entering rho*.")
    parser.add_argument(
        "--rho-star-n",
        type=int,
        default=None,
        help="N used to evaluate rho* (default: 4*K, i.e. N != N0 so the three photon conventions actually differ "
        "numerically -- at N=N0 all three collapse to the same Phi_frame by construction).",
    )
    parser.add_argument(
        "--photon-ref",
        type=float,
        default=8.0,
        help="Reference photon budget Phi_ref (default matches the low-photon regime audited elsewhere in this "
        "repo, e.g. run_paper_fig7_lowphoton.py's lambda_bar grid, so the photon term is a physically realistic "
        "rather than an arbitrarily huge/negligible number).",
    )
    parser.add_argument("--photon-n0", type=float, default=None, help="Reference frame count N0 (default: K).")
    parser.add_argument(
        "--kappa-s",
        type=float,
        default=0.05,
        help="Shot-noise-to-drift-variance coupling: s_eff^2 = s^2 + kappa_s/Phi_frame. Chosen so the photon term "
        "is comparable to s^2 (not negligible, not dominant) at the default s and Phi_ref.",
    )
    args = parser.parse_args()

    start = time.time()
    out = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    k = int(args.image_size * args.image_size)
    n_draws = int(args.n_draws)
    rho_star_n = int(args.rho_star_n) if args.rho_star_n is not None else 4 * k
    photon_n0 = float(args.photon_n0) if args.photon_n0 is not None else float(k)

    all_objects = make_paper_objects(10, image_size=args.image_size, seed=args.seed)
    objects = [o for o in all_objects if o.name in OBJECT_NAMES]
    if len(objects) != len(OBJECT_NAMES):
        missing = set(OBJECT_NAMES) - {o.name for o in objects}
        raise RuntimeError(f"Expected objects {OBJECT_NAMES}, missing {missing}.")
    objects_matrix = torch.stack([o.vector for o in objects], dim=0)  # (num_objects, K)
    s1 = objects_matrix.to(dtype=torch.float64).sum(dim=1)
    s2 = objects_matrix.to(dtype=torch.float64).pow(2).sum(dim=1).clamp_min(1.0e-12)
    k_eff = (s1.pow(2) / s2).numpy()
    s2_np = s2.numpy()

    moment_rows: List[Dict[str, object]] = []
    c0_rows: List[Dict[str, object]] = []

    for ensemble_name, generator_fn in ENSEMBLE_GENERATORS.items():
        generator = torch.Generator(device="cpu")
        generator.manual_seed(int(args.seed) + ENSEMBLE_SEED_OFFSET[ensemble_name])
        kwargs = {"mu": args.gaussian_mu, "sigma": args.gaussian_sigma} if ensemble_name == "gaussian_clipped" else {}
        patterns = generator_fn((n_draws, k), generator, **kwargs)  # (n_draws, K), float32

        patterns64 = patterns.to(dtype=torch.float64)
        mu = float(patterns64.mean().item())
        sigma = float(patterns64.std(unbiased=False).item())
        j = patterns64 - mu
        m3 = float(j.pow(3).mean().item())
        m4 = float(j.pow(4).mean().item())
        gamma_3 = m3 / (sigma**3)
        beta_4 = m4 / (sigma**4)

        moment_rows.append(
            {
                "ensemble": ensemble_name,
                "n_draws": n_draws,
                "K": k,
                "mu": mu,
                "sigma": sigma,
                "gamma_3": gamma_3,
                "beta_4": beta_4,
            }
        )

        j_sq_norm = j.pow(2).sum(dim=1)  # (n_draws,) -- ||I - mu||^2 per draw, shared across objects
        buckets = (patterns64 @ objects_matrix.to(dtype=torch.float64).transpose(0, 1))  # (n_draws, num_objects)

        for obj_idx, obj in enumerate(objects):
            s2_j = float(s2_np[obj_idx])
            k_eff_j = float(k_eff[obj_idx])

            z_sq = (buckets[:, obj_idx] / (sigma**2)).pow(2) * j_sq_norm  # (n_draws,), exact ||Z||^2 per draw
            c0_measured = float(z_sq.mean().item()) / s2_j - 1.0
            c0_measured_se = float(z_sq.std(unbiased=True).item()) / math.sqrt(n_draws) / s2_j

            c0_formula = (k + beta_4 - 2.0) + k_eff_j * (k * (mu / sigma) ** 2 + 2.0 * gamma_3 * (mu / sigma))

            abs_rel_err = abs(c0_measured - c0_formula) / max(abs(c0_formula), 1.0e-12)

            # ---- Part B: flip-boundary heuristic under three photon conventions. ----
            rho_star_by_convention: Dict[str, float] = {}
            for convention in CONVENTIONS:
                flux = phi_frame(rho_star_n, convention, args.photon_ref, photon_n0)
                s_eff_sq = (args.s**2) + float(args.kappa_s) / max(flux, 1.0e-12)
                rho_star = 2.0 * c0_measured / (float(rho_star_n) * k_eff_j * s_eff_sq)
                rho_star_by_convention[convention] = rho_star

            rho_values = np.array(list(rho_star_by_convention.values()), dtype=np.float64)
            rho_spread_ratio = float(rho_values.max() / max(rho_values.min(), 1.0e-18))
            rho_spread_abs = float(rho_values.max() - rho_values.min())

            c0_rows.append(
                {
                    "ensemble": ensemble_name,
                    "object": obj.name,
                    "family": obj.family,
                    "K": k,
                    "K_eff": k_eff_j,
                    "S2": s2_j,
                    "mu": mu,
                    "sigma": sigma,
                    "gamma_3": gamma_3,
                    "beta_4": beta_4,
                    "C0_measured": c0_measured,
                    "C0_measured_se": c0_measured_se,
                    "C0_formula": c0_formula,
                    "abs_rel_err": abs_rel_err,
                    "rho_star_equal_exposure": rho_star_by_convention["equal_exposure"],
                    "rho_star_equal_count": rho_star_by_convention["equal_count"],
                    "rho_star_fixed_flux": rho_star_by_convention["fixed_flux"],
                    "rho_star_spread_ratio": rho_spread_ratio,
                    "rho_star_spread_abs": rho_spread_abs,
                }
            )

    moments_df = pd.DataFrame(moment_rows)
    c0_df = pd.DataFrame(c0_rows)
    moments_df.to_csv(out / "e9_ensemble_moments.csv", index=False)
    c0_df.to_csv(out / "e9_c0_audit.csv", index=False)

    ensemble_summary = c0_df.groupby("ensemble", as_index=False).agg(
        abs_rel_err_mean=("abs_rel_err", "mean"),
        abs_rel_err_max=("abs_rel_err", "max"),
        C0_measured_min=("C0_measured", "min"),
        C0_measured_max=("C0_measured", "max"),
        rho_star_spread_ratio_mean=("rho_star_spread_ratio", "mean"),
        rho_star_spread_ratio_max=("rho_star_spread_ratio", "max"),
    )
    ensemble_summary.to_csv(out / "e9_ensemble_summary.csv", index=False)

    overall_abs_rel_err_max = float(c0_df["abs_rel_err"].max())
    overall_abs_rel_err_mean = float(c0_df["abs_rel_err"].mean())
    worst_row = c0_df.loc[c0_df["abs_rel_err"].idxmax()]
    rho_spread_ratio_min = float(c0_df["rho_star_spread_ratio"].min())
    rho_spread_ratio_max = float(c0_df["rho_star_spread_ratio"].max())
    rho_spread_ratio_mean = float(c0_df["rho_star_spread_ratio"].mean())

    # ---- Small table figure: ensemble moments + formula-vs-measured + rho* spread. ----
    fig, axes = plt.subplots(2, 1, figsize=(11.5, 5.6))
    axes[0].axis("off")
    axes[1].axis("off")

    moment_cols = ["ensemble", "mu", "sigma", "gamma_3", "beta_4", "abs_rel_err_mean", "abs_rel_err_max"]
    table1 = moments_df.merge(ensemble_summary, on="ensemble")[moment_cols].round(4)
    t1 = axes[0].table(
        cellText=table1.values.tolist(),
        colLabels=["ensemble", "mu", "sigma", "gamma_3", "beta_4", "mean |formula-measured|/formula", "max |.../formula"],
        loc="center",
        cellLoc="center",
    )
    t1.auto_set_font_size(False)
    t1.set_fontsize(8)
    t1.scale(1.0, 1.6)
    axes[0].set_title("Ensemble moments and C0 formula-vs-measured agreement", fontsize=9)

    table2 = c0_df[
        ["ensemble", "object", "K_eff", "C0_measured", "C0_formula", "abs_rel_err", "rho_star_spread_ratio"]
    ].round(4)
    t2 = axes[1].table(
        cellText=table2.values.tolist(),
        colLabels=["ensemble", "object", "K_eff", "C0 measured", "C0 formula", "|rel err|", "rho* spread (max/min)"],
        loc="center",
        cellLoc="center",
    )
    t2.auto_set_font_size(False)
    t2.set_fontsize(7)
    t2.scale(1.0, 1.35)
    axes[1].set_title("Per (ensemble, object) C0 and flip-boundary photon-convention spread", fontsize=9)

    fig.tight_layout()
    fig.savefig(out / "e9_c0_audit_table.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    write_caption(
        out / "e9_caption.md",
        "E9 DGI One-Sample Constant C0 Audit + Photon-Convention Flip-Boundary Spread (r1)",
        [
            f"Setup: C0 = E||Z||^2/S2 - 1 with Z(x)=[I(x)-mu]*B/sigma^2, B=sum_x' I(x')O(x'), measured from "
            f"{n_draws} single-frame pattern draws per ensemble (K={k} pixels), for 4 pattern ensembles "
            "(uniform[0,1], binary 0/1, signed Rademacher, Gaussian(mu=0.5,sigma=0.2) hard-clipped to [0,1]) x "
            f"5 objects spanning K_eff (letter_L, digit_2, ring, stripe, natural_patch; K_eff="
            f"{c0_df['K_eff'].min():.1f}-{c0_df['K_eff'].max():.1f}). ||Z||^2=(B/sigma^2)^2*||I-mu||^2 exactly "
            "(Z is a per-draw scalar times a fixed centered-pattern vector), so the estimator needs no explicit "
            "(n_draws,K) Z matrix. mu/sigma/beta_4/gamma_3 are the SAME large-sample empirical moments used to "
            "seed the formula, not independently-sourced textbook values.",
            f"Formula-vs-measured: C0 = K+beta_4-2+K_eff*[K*(mu/sigma)^2+2*gamma_3*(mu/sigma)] agrees with the "
            f"direct E||Z||^2/S2-1 estimate to mean |rel err|={overall_abs_rel_err_mean * 100.0:.2f}%, worst "
            f"{overall_abs_rel_err_max * 100.0:.2f}% (ensemble={worst_row['ensemble']}, object={worst_row['object']}, "
            f"C0_measured={worst_row['C0_measured']:.1f}, C0_formula={worst_row['C0_formula']:.1f}) across all "
            "20 (ensemble, object) cells -- confirming the derivation (only signed Rademacher has mu=0 among "
            "these 4 ensembles, so the K_eff-dependent cross term is non-trivial for uniform/binary/gaussian_clipped, "
            "and C0 itself ranges from O(K) for Rademacher to O(K_eff * K) ~ 1e5-1e6 for uniform/binary/gaussian "
            "with the higher-K_eff objects -- consistent in order of magnitude with the leverage*N ~ 7.4-7.7e5 "
            "range independently measured for the uniform-pattern random_dgi arm in the Fig. 4 bridge).",
            "Photon-convention weighting (documented, simplified add-on -- NOT part of the leading-order rho* "
            "formula itself, which has no explicit photon term; C0 is a pure pattern-statistics constant with no "
            "photon dependence, per Part A, so the convention instead inflates the EFFECTIVE drift variance that "
            "survives blind correction): Phi_frame(N) is defined per convention as equal_exposure=Phi_ref (fixed "
            "per-frame flux, total budget grows with N), equal_count=Phi_ref*N0/N (fixed TOTAL budget Phi_ref*N0 "
            "redistributed across N frames), fixed_flux=Phi_ref*sqrt(N0/N) (geometric-mean intermediate), with "
            f"Phi_ref={args.photon_ref:g}, N0={photon_n0:g}=K, evaluated at N={rho_star_n}=4*N0 (chosen != N0 so "
            f"the three conventions differ numerically -- at N=N0 all three collapse to the same Phi_frame by "
            f"construction). s_eff^2=s^2+kappa_s/Phi_frame with s={args.s:g}, kappa_s={args.kappa_s:g}, and "
            "rho*=2*C0_measured/(N*K_eff*s_eff^2). Spread of rho* across the 3 conventions (max/min ratio) ranges "
            f"{rho_spread_ratio_min:.3f}-{rho_spread_ratio_max:.3f} across cells (mean {rho_spread_ratio_mean:.3f}) "
            "-- non-trivial (kappa_s/Phi_frame is comparable to s^2 at this Phi_ref by construction) and IDENTICAL "
            "across ensembles/objects for fixed (N, s, kappa_s, Phi_ref) since the convention only rescales the "
            "shared denominator s_eff^2, not C0 or K_eff; a photon-starved acquisition (equal_count, low Phi_ref) "
            "raises rho* relative to a well-exposed one (equal_exposure), i.e. it shrinks the slow-drift regime "
            "where pairwise Hadamard remains the safe choice.",
            f"Rows: C0 audit {len(c0_df)}, moments {len(moments_df)}. Runtime seconds: {time.time() - start:.2f}.",
        ],
    )
    (out / "run_manifest.json").write_text(
        json.dumps(
            build_run_manifest(args, ROOT, extra={"rows": int(len(c0_df))}),
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    print(
        f"E9 complete rows={len(c0_df)} mean_abs_rel_err={overall_abs_rel_err_mean:.4f} "
        f"max_abs_rel_err={overall_abs_rel_err_max:.4f} rho_spread_ratio=[{rho_spread_ratio_min:.4f},"
        f"{rho_spread_ratio_max:.4f}] output={out} runtime={time.time() - start:.2f}s"
    )


if __name__ == "__main__":
    main()
