"""Experiment B2 -- Factorized whitening ablation (audit fix for P0-2).

WHY THIS EXISTS
---------------
``run_perm_whitening_power.py`` (authoritative dir ``results/perm_whitening_power_r1``,
headline mean random-arm Levene rejection 5.9% vs ~70% ordered) applies BOTH a
pixel/column permutation (``T_perm = T[pix]``) AND a Hadamard row/time
permutation (``random_paired_carrier(coeffs, row_order, ...)``) simultaneously in
its single "random" arm, and NO Rademacher sign flips. So the 5.9% cannot be
attributed to any one factor.

Meanwhile Appendix E proves whitening for the SRHT randomization ``x = U D P T``
where ``P`` is a PIXEL/column permutation and ``D`` is a diagonal of i.i.d.
Rademacher pixel SIGNS. The code's SRHT basis
(``src.basis.make_srht_paired_basis(permute_rows=True)``) instead permutes the
Hadamard ROW (time) order and applies pixel signs -- it never permutes pixel
columns. Theory (P_col + D) and both experiments therefore use mismatched
randomization semantics.

This runner factorizes the randomization into independent arms, each applied to
the SAME ordered natural-Hadamard baseline, the SAME 10-object panel, and the
SAME protocol (K=4096, 8192 frames, Brown-Forsythe/Levene over 8 chunks of the
noiseless paired carrier) as ``run_perm_whitening_power.py``:

  * ``ordered``          -- none (baseline; expect high rejection).
  * ``row_perm_only``    -- permute Hadamard row/time order only (P_row).
  * ``pixel_perm_only``  -- permute pixel/column indices only (Appendix E's P_col).
  * ``sign_only``        -- Rademacher pixel sign flips only (Appendix E's D).
  * ``pixel_sign``       -- P_col + D, natural row order (THE THEORY's SRHT).
  * ``row_pixel``        -- P_row + P_col (what the OLD runner effectively did).
  * ``row_pixel_sign``   -- P_row + P_col + D (everything).
  * ``row_sign``         -- P_row + D (what the CODE's srht_paired basis does).

Carrier construction is physically faithful (verified once per run against an
explicit ``interleave_paired_frames`` measurement of the real signed Hadamard
basis): for a row ``g`` the paired frames are ``0.5*(sum(P T) +/- <h_g, D P T>)``
with ``<h_g, D P T> = FWHT(signs * T[pix])[g]`` and ``sum(P T) = sum(T)``.

Randomization draws reuse the OLD runner's seed formulas so pixel/row numbers are
directly comparable:
  pixel perm draw i : seed + 101*i ;  row perm draw i : seed + 977*i ;
  signs   draw  i   : seed + 613*i  (new stream; the old runner had no signs).

Outputs (``results/perm_ablation_r1/``):
  * ``perm_ablation.csv``   -- one row per (arm, object, draw).
  * ``fig_perm_ablation.png``
  * ``summary.md``          -- per-arm table + attribution + Fig. 6 arm decode.
  * ``run_manifest.json``
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

from src.basis import MeasurementBasis, hadamard_matrix, interleave_paired_frames, is_power_of_two
from src.mechanisms import moving_average_1d
from src.paper_experiments import build_run_manifest, make_paper_objects, write_caption

# Reuse the EXACT Fig. 2 r2b stationarity metric (Brown-Forsythe over 8 chunks),
# identical to the reference run_perm_whitening_power.py.
from run_paper_fig2_stationarity import stationarity_metrics


ROOT = Path(__file__).resolve().parent

# Arm factorization: (name, use_pixel_perm P_col, use_sign D, use_row_perm P_row).
ARMS: List[Tuple[str, bool, bool, bool]] = [
    ("ordered", False, False, False),
    ("row_perm_only", False, False, True),
    ("pixel_perm_only", True, False, False),
    ("sign_only", False, True, False),
    ("pixel_sign", True, True, False),   # THE THEORY's SRHT randomization (natural row order)
    ("row_pixel", True, False, True),    # what run_perm_whitening_power.py effectively did
    ("row_pixel_sign", True, True, True),
    ("row_sign", False, True, True),     # what src.basis.make_srht_paired_basis does
]


def fwht(vector: torch.Tensor) -> torch.Tensor:
    """Unnormalised natural-ordered fast Walsh-Hadamard transform (== H @ x).

    Identical to run_perm_whitening_power.fwht: ``w_hat[0]`` is the sum of the
    input, length must be a power of two.
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


def paired_carrier(coeffs: torch.Tensor, row_order: torch.Tensor, sum_pixels: float) -> torch.Tensor:
    """Paired-Hadamard bucket carrier from signed Walsh coefficients.

    Frame ``2n = 0.5*(sum_pixels + coeffs[row_order[n]])`` and frame ``2n+1`` its
    complement. Identical convention to run_perm_whitening_power.random_paired_carrier.
    """

    ordered = coeffs[row_order]
    carrier = torch.empty(2 * ordered.numel(), dtype=ordered.dtype, device=ordered.device)
    carrier[0::2] = 0.5 * (sum_pixels + ordered)
    carrier[1::2] = 0.5 * (sum_pixels - ordered)
    return carrier


def walsh_flatness_ratio(squared_perm: torch.Tensor) -> Tuple[float, float]:
    """max non-DC |FWHT(T^2)| / S2, with S2 = sum(T^2) = FWHT(T^2)[0].

    Depends only on the PERMUTED squared object (Lemma E.1: signs D do not enter
    the carrier covariance, only the pixel ordering does).
    """

    w_hat = fwht(squared_perm)
    s2 = float(w_hat[0].item())
    if s2 <= 0:
        return float("nan"), s2
    max_non_dc = float(w_hat[1:].abs().max().item())
    return max_non_dc / s2, s2


def carrier_for_arm(
    T: torch.Tensor,
    pix: Optional[torch.Tensor],
    signs: Optional[torch.Tensor],
    row_order: torch.Tensor,
) -> Tuple[torch.Tensor, torch.Tensor, float]:
    """Build the noiseless paired carrier for a chosen (P_col, D, P_row) combo.

    Returns (carrier, obj_pixel, sum_pixels). ``obj_pixel`` is the pixel-permuted
    (but unsigned) object, used for the theory-relevant Walsh flatness metric.
    """

    obj_pixel = T[pix] if pix is not None else T
    obj_signed = signs * obj_pixel if signs is not None else obj_pixel
    coeffs = fwht(obj_signed)                       # <h_g, D P T>
    sum_pixels = float(obj_pixel.sum().item())      # sum(P T) = sum(T); signs do NOT enter the DC baseline
    carrier = paired_carrier(coeffs, row_order, sum_pixels)
    return carrier, obj_pixel, sum_pixels


def levene_of_carrier(carrier: torch.Tensor, window: int, chunks: int, transient: int) -> Dict[str, float]:
    """Full Fig. 2 r2b stationarity metric dict on the noiseless carrier."""

    carrier = carrier.to(dtype=torch.float32)
    running = moving_average_1d(carrier, int(window))
    return stationarity_metrics(carrier, running, num_chunks=int(chunks), transient=int(transient))


def _rademacher(K: int, seed: int, device: str) -> torch.Tensor:
    g = torch.Generator(device="cpu")
    g.manual_seed(int(seed))
    signs = torch.randint(0, 2, (K,), generator=g).mul(2).sub(1).to(dtype=torch.float64)
    return signs.to(device=device)


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiment B2: factorized whitening ablation (P0-2 fix).")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "perm_ablation_r1")
    parser.add_argument("--image-size", type=int, default=64, help="Square side; K = image_size^2 (64 -> 8192 frames).")
    parser.add_argument("--objects", type=int, default=10)
    parser.add_argument("--nperm", type=int, default=32, help="Independent draws per RANDOMIZED arm.")
    parser.add_argument("--seed", type=int, default=20240708, help="Base seed (matches Fig. 2 / old runner).")
    parser.add_argument("--window", type=int, default=64)
    parser.add_argument("--chunks", type=int, default=8)
    parser.add_argument("--transient", type=int, default=128)
    parser.add_argument("--reject-alpha", type=float, default=1.0e-3)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--smoke", action="store_true", help="Tiny grid for a local smoke test.")
    args = parser.parse_args()

    if args.smoke:
        args.image_size = 16
        args.objects = 3
        args.nperm = 4
        args.window = 16
        args.transient = 16
        if args.output_dir == ROOT / "results" / "perm_ablation_r1":
            args.output_dir = ROOT / "results" / "perm_ablation_smoke"

    start = time.time()
    out = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    device = args.device
    K = args.image_size * args.image_size
    if not is_power_of_two(K):
        raise ValueError(f"K = image_size^2 must be a power of two, got {K}.")
    objects = make_paper_objects(args.objects, image_size=args.image_size, seed=args.seed)

    identity_order = torch.arange(K, device=device)

    # Shared per-draw randomizations. SAME seed formulas as run_perm_whitening_power.py
    # for pixels (seed+101*i) and rows (seed+977*i); a NEW stream for signs (seed+613*i).
    perm_pixels: List[torch.Tensor] = []
    perm_rows: List[torch.Tensor] = []
    signs_list: List[torch.Tensor] = []
    for i in range(args.nperm):
        g_pix = torch.Generator(device="cpu"); g_pix.manual_seed(args.seed + 101 * i)
        perm_pixels.append(torch.randperm(K, generator=g_pix).to(device=device))
        g_row = torch.Generator(device="cpu"); g_row.manual_seed(args.seed + 977 * i)
        perm_rows.append(torch.randperm(K, generator=g_row).to(device=device))
        signs_list.append(_rademacher(K, args.seed + 613 * i, device))

    rows: List[Dict[str, object]] = []
    verify_diff: Optional[float] = None

    for arm_name, use_pix, use_sign, use_row in ARMS:
        ndraws = 1 if arm_name == "ordered" else args.nperm
        for obj in objects:
            T = obj.vector.to(device=device, dtype=torch.float64)
            for draw in range(ndraws):
                pix = perm_pixels[draw] if use_pix else None
                signs = signs_list[draw] if use_sign else None
                row_order = perm_rows[draw] if use_row else identity_order

                carrier, obj_pixel, sum_pixels = carrier_for_arm(T, pix, signs, row_order)
                ratio, s2 = walsh_flatness_ratio(obj_pixel * obj_pixel)
                metrics = levene_of_carrier(carrier, args.window, args.chunks, args.transient)

                # One-time physical-faithfulness guard: rebuild the carrier via an
                # explicit signed-Hadamard interleaved-paired measurement and compare.
                if verify_diff is None and use_sign and use_pix and use_row:
                    H = hadamard_matrix(K, device=device, dtype=torch.float64)
                    signed_rows = H.index_select(0, row_order) * signs.reshape(1, -1)
                    ref_basis = MeasurementBasis(
                        name="verify", patterns=interleave_paired_frames(signed_rows),
                        paired=True, signed_rows=signed_rows, row_indices=row_order,
                    )
                    direct = ref_basis.measure(obj_pixel).to(dtype=torch.float64)
                    verify_diff = float((carrier - direct).abs().max().item())

                rows.append({
                    "arm": arm_name,
                    "pixel_perm": bool(use_pix),
                    "sign_flip": bool(use_sign),
                    "row_perm": bool(use_row),
                    "object": obj.name,
                    "family": obj.family,
                    "K_eff": float(obj.k_eff),
                    "draw": int(draw),
                    "num_frames": int(carrier.numel()),
                    "chunks": int(args.chunks),
                    "levene_p": float(metrics["levene_p"]),
                    "levene_reject": bool(metrics["levene_p"] < args.reject_alpha),
                    "ks_absdev_p": float(metrics["ks_absdev_p"]),
                    "local_std_envelope_cv": float(metrics["local_std_envelope_cv"]),
                    "running_mean_cv": float(metrics["running_mean_cv"]),
                    "walsh_flatness_ratio": float(ratio),
                    "walsh_S2": float(s2),
                })

    df = pd.DataFrame(rows)
    df.to_csv(out / "perm_ablation.csv", index=False)

    summary = _summarize(df, args)
    _write_summary_md(out / "summary.md", df, summary, args, K)
    _make_figure(df, summary, out, args)

    manifest_extra = {
        "rows": int(len(df)),
        "K": int(K),
        "nperm": int(args.nperm),
        "arms": [a[0] for a in ARMS],
        "reject_alpha": float(args.reject_alpha),
        "carrier_verify_max_abs_diff_vs_explicit_basis": verify_diff,
        "per_arm_reject": {r["arm"]: {"n": int(r["n_reject"]), "N": int(r["N"]), "rate": float(r["rate"])} for r in summary},
    }
    (out / "run_manifest.json").write_text(
        json.dumps(build_run_manifest(args, ROOT, extra=manifest_extra), indent=2, default=str),
        encoding="utf-8",
    )
    write_caption(
        out / "perm_ablation_caption.md",
        "Experiment B2 -- Factorized Whitening Ablation (r1)",
        [
            f"K={K} ({args.image_size}x{args.image_size}), num_frames={2 * K}, chunks={args.chunks}, "
            f"nperm={args.nperm}, reject at Levene p<{args.reject_alpha:g}.",
            "Each arm applies a distinct subset of {P_col pixel-perm, D pixel-signs, P_row row/time-perm} to the same "
            "ordered natural-Hadamard baseline and 10-object panel; Levene = EXACT Fig. 2 r2b metric.",
            f"Physical-faithfulness guard (row_pixel_sign vs explicit interleaved-paired measurement): "
            f"max abs diff {verify_diff:.2e}.",
        ]
        + [f"{r['arm']}: {r['n_reject']}/{r['N']} = {r['rate']:.3f} reject." for r in summary]
        + [f"Rows: {len(df)}. Runtime seconds: {time.time() - start:.2f}."],
    )

    print(f"[perm_ablation] rows={len(df)} verify_diff={verify_diff} out={out} runtime={time.time() - start:.2f}s")
    for r in summary:
        print(f"  {r['arm']:<16} {r['n_reject']:>4}/{r['N']:<4} = {r['rate']:.3f}   "
              f"mean_walsh={r['mean_walsh']:.4f} mean_stdCV={r['mean_std_cv']:.4f}")


def _summarize(df: pd.DataFrame, args: argparse.Namespace) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for arm_name, _, _, _ in ARMS:
        sub = df[df["arm"] == arm_name]
        n = int(sub["levene_reject"].sum())
        N = int(len(sub))
        out.append({
            "arm": arm_name,
            "n_reject": n,
            "N": N,
            "rate": (n / N) if N else float("nan"),
            "mean_walsh": float(sub["walsh_flatness_ratio"].mean()),
            "mean_std_cv": float(sub["local_std_envelope_cv"].mean()),
            "mean_run_cv": float(sub["running_mean_cv"].mean()),
        })
    return out


def _write_summary_md(path: Path, df: pd.DataFrame, summary: List[Dict[str, object]], args: argparse.Namespace, K: int) -> None:
    lines: List[str] = []
    lines.append("# Experiment B2 -- Factorized whitening ablation (P0-2 audit fix)")
    lines.append("")
    lines.append(f"K={K} ({args.image_size}x{args.image_size}), num_frames={2 * K}, chunks={args.chunks}, "
                 f"nperm={args.nperm}, reject at Brown-Forsythe (Levene) p<{args.reject_alpha:g}.")
    lines.append("Noiseless paired-Hadamard carrier; Levene metric identical to Fig. 2 r2b "
                 "(run_paper_fig2_stationarity.stationarity_metrics).")
    lines.append("")
    lines.append("## Per-arm Levene non-stationarity rejection")
    lines.append("")
    lines.append("| arm | P_col pixel | D signs | P_row time | reject n/N | rate | mean Walsh peak | mean chunk-std CV |")
    lines.append("|-----|:-----------:|:-------:|:----------:|:----------:|:----:|:---------------:|:-----------------:|")
    arm_flags = {a[0]: (a[1], a[2], a[3]) for a in ARMS}
    for r in summary:
        pix, sign, row = arm_flags[r["arm"]]
        lines.append(
            f"| `{r['arm']}` | {'Y' if pix else '-'} | {'Y' if sign else '-'} | {'Y' if row else '-'} | "
            f"{r['n_reject']}/{r['N']} | {r['rate']:.3f} | {r['mean_walsh']:.4f} | {r['mean_std_cv']:.4f} |"
        )
    lines.append("")

    rate = {r["arm"]: r["rate"] for r in summary}

    def verdict(x: float) -> str:
        if x <= 0.15:
            return "SUFFICIENT (low, <=0.15)"
        if x >= 0.5:
            return "NOT sufficient (high)"
        return "PARTIAL"

    lines.append("## Attribution")
    lines.append("")
    lines.append(f"- `ordered` baseline rejects at rate {rate['ordered']:.3f} (high non-stationarity, as expected).")
    lines.append(f"- `row_perm_only` (P_row alone): rate {rate['row_perm_only']:.3f} -> {verdict(rate['row_perm_only'])}.")
    lines.append(f"- `pixel_perm_only` (P_col alone, Appendix E's P): rate {rate['pixel_perm_only']:.3f} -> {verdict(rate['pixel_perm_only'])}.")
    lines.append(f"- `sign_only` (D alone, Appendix E's signs): rate {rate['sign_only']:.3f} -> {verdict(rate['sign_only'])}.")
    lines.append(f"- `pixel_sign` (P_col + D = THE THEORY's SRHT randomization, natural row order): "
                 f"rate {rate['pixel_sign']:.3f} -> {verdict(rate['pixel_sign'])}.")
    lines.append(f"- `row_pixel` (what the OLD run_perm_whitening_power.py did): rate {rate['row_pixel']:.3f}.")
    lines.append(f"- `row_sign` (what the CODE's srht_paired basis does: P_row + D): rate {rate['row_sign']:.3f} -> {verdict(rate['row_sign'])}.")
    lines.append(f"- `row_pixel_sign` (everything): rate {rate['row_pixel_sign']:.3f}.")
    lines.append("")
    # Data-driven attribution sentence.
    drivers = []
    if rate["row_perm_only"] <= 0.15:
        drivers.append("row/time permutation (P_row) alone")
    if rate["pixel_perm_only"] <= 0.15:
        drivers.append("pixel permutation (P_col) alone")
    if rate["sign_only"] <= 0.15:
        drivers.append("pixel sign flips (D) alone")
    if rate["pixel_sign"] <= 0.15:
        drivers.append("the theory's P_col+D (pixel_sign) alone")
    if drivers:
        lines.append("**Sufficient single/theory factors (rate <=0.15): " + "; ".join(drivers) + ".**")
    else:
        lines.append("**No single factor nor the theory's P_col+D arm reaches the <=0.15 acceptance ceiling on its own.**")
    theory_ok = rate["pixel_sign"] <= 0.15
    lines.append("")
    lines.append(f"**Theory-vs-experiment finding:** the manuscript's SRHT randomization is P_col+D "
                 f"(`pixel_sign`, natural row order), which rejects at {rate['pixel_sign']:.3f}. "
                 + ("This IS sufficient for carrier stationarity on its own." if theory_ok else
                    "This is NOT sufficient for carrier stationarity on its own -- the temporal (P_row) reorder is "
                    "what the old 5.9% headline actually required. This is a critical honest correction: the "
                    "temporal stationarity measured by the Levene test is driven by row/time permutation, which is "
                    "OUTSIDE Appendix E's carrier-decorrelation theorem (Lemma E.1 covariance is row-order-invariant)."))
    lines.append("")
    lines.append("Note (theory scope): Appendix E (Lemma E.1, Thm E.2/E.3) characterizes the sign-draw carrier "
                 "*covariance* across Walsh rows -- a function of the PERMUTED SQUARED object w^P only, invariant to "
                 "the acquisition row/time order. The Levene test here probes TEMPORAL stationarity of the carrier as "
                 "an acquired time series, which the row/time order (P_row) controls directly. The two notions of "
                 "'whitening' are distinct; the old runner conflated them.")
    lines.append("")
    lines.append("## Fig. 6 arm decode (run_srht_m3.py `make_variant`) -- caption-ready mechanics")
    lines.append("")
    lines.append("In `run_srht_m3.py`, `h = hadamard_matrix(p)`; `signs` is a length-p Rademacher vector; "
                 "`perm = randperm(p)` is a **row-index** permutation; measurement rows are "
                 "`rows = h.index_select(0, row_indices)` and, when `use_signs`, `rows = rows * signs.reshape(1, -1)` "
                 "which multiplies each **column (pixel)** by a sign. There is **no pixel/column permutation in any "
                 "Fig. 6 arm.** All arms are paired (`interleave_paired_frames`). Concretely:")
    lines.append("")
    lines.append("| Fig. 6 variant | row/time order | pixel signs D | pixel perm P_col | = which ablation arm |")
    lines.append("|----------------|----------------|:-------------:|:----------------:|----------------------|")
    lines.append("| `hadamard_ordered` | natural | - | - | `ordered` |")
    lines.append("| `perm_only` | full random ROW permutation | - | - | `row_perm_only` (NOT pixel perm) |")
    lines.append("| `sign_only` | natural | Y | - | `sign_only` |")
    lines.append("| `srht_full` | full random ROW permutation | Y | - | `row_sign` (NOT theory's P_col+D) |")
    lines.append("| `hadamard_time_interleave` | block round-robin interleave | - | - | (deterministic P_row variant) |")
    lines.append("| `sign_time_interleave` | block round-robin interleave | Y | - | (interleave + D) |")
    lines.append("| `hadamard_block_shuffle` | within-block ROW shuffle | - | - | (block P_row variant) |")
    lines.append("| `sign_block_shuffle` | within-block ROW shuffle | Y | - | (block P_row + D) |")
    lines.append("")
    lines.append("Caption correction: Fig. 6 `perm_only` is a **row/time-order** permutation of the Hadamard patterns, "
                 "NOT the pixel/column permutation P of Appendix E; and `srht_full` is **row-permutation + pixel signs** "
                 "(P_row + D), NOT the theory's SRHT `x = U D P_col T`. No Fig. 6 arm realizes the P_col of the SRHT "
                 "theorem.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _make_figure(df: pd.DataFrame, summary: List[Dict[str, object]], out: Path, args: argparse.Namespace) -> None:
    arms = [r["arm"] for r in summary]
    rates = [r["rate"] for r in summary]
    walsh = [r["mean_walsh"] for r in summary]
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.8))

    ax = axes[0]
    xpos = np.arange(len(arms))
    colors = ["tab:gray" if a == "ordered" else "tab:blue" for a in arms]
    ax.bar(xpos, rates, color=colors, alpha=0.85)
    ax.axhline(0.15, color="red", linestyle="--", linewidth=1.0, label="0.15 acceptance ceiling")
    ax.set_xticks(xpos)
    ax.set_xticklabels(arms, rotation=40, ha="right", fontsize=8)
    ax.set_ylabel(f"Levene reject rate (p<{args.reject_alpha:g})")
    ax.set_ylim(0.0, 1.05)
    ax.set_title("Per-arm carrier non-stationarity rejection\n(factorized: P_col / D / P_row)")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, axis="y", alpha=0.25)

    ax = axes[1]
    lp = df["levene_p"].to_numpy(dtype=float).clip(1e-300, 1.0)
    wr = df["walsh_flatness_ratio"].to_numpy(dtype=float)
    rej = df["levene_reject"].to_numpy(dtype=bool)
    ax.scatter(wr[~rej], lp[~rej], s=12, color="tab:blue", alpha=0.4, label="not rejected")
    ax.scatter(wr[rej], lp[rej], s=18, color="tab:red", alpha=0.7, label="rejected")
    ax.axhline(args.reject_alpha, color="gray", linestyle="--", linewidth=1.0)
    ax.set_yscale("log")
    ax.set_xlabel("walsh_flatness_ratio (max non-DC |FWHT(P T)^2| / S2)")
    ax.set_ylabel("levene_p")
    ax.set_title("levene_p vs permuted-object Walsh peak (all units)")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, alpha=0.25)

    fig.tight_layout()
    fig.savefig(out / "fig_perm_ablation.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()
