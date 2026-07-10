#!/usr/bin/env python
"""Regenerate all publication figures for the IEEE paper with a fixed, validated palette.

Run from the repo root with the project python:
    D:/Anacondar/anaconda3/envs/pytorch/python.exe paper_draft/latex/make_pub_figures.py

Every figure is drawn with a single module-level palette (never matplotlib defaults),
a shared white/hairline-grid style, and a FIXED series->color mapping applied identically
across all figures so a given acquisition arm keeps its colour everywhere.

Outputs (paper_draft/latex/figs/, PNGs overwritten in place; fig1 is new):
    fig1_conceptmap.png
    fig2_carrier_traces.png
    fig3a_error_vs_W.png
    fig3c_collapse.png
    fig4_relmse_theory_vs_sim.png
    fig5_flip_boundary.png
    fig6_ablation.png
    fig7_gainMSE_vs_photon.png
    fig8_threshold.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch

# Repo root = two levels up from this file (paper_draft/latex/make_pub_figures.py).
ROOT = Path(__file__).resolve().parents[2]
FIGS = ROOT / "paper_draft" / "latex" / "figs"
RESULTS = ROOT / "results"

# --------------------------------------------------------------------------------------
# PALETTE  (fixed order; never cycle beyond it, never use matplotlib C0..C9/tab10/viridis)
# --------------------------------------------------------------------------------------
P1 = "#2a78d6"  # blue
P2 = "#1baf7a"  # aqua
P3 = "#eda100"  # yellow
P4 = "#008300"  # green
P5 = "#4a3aa7"  # violet
P6 = "#e34948"  # red
P7 = "#e87ba4"  # magenta
P8 = "#eb6834"  # orange
PALETTE = (P1, P2, P3, P4, P5, P6, P7, P8)

# Low-contrast hues that always need direct labels / high-zorder markers.
LOW_CONTRAST = {P2, P3, P7}

# Ink / structure colours.
GRID = "#e1e0d9"      # hairline grid
AXIS = "#c3c2b7"      # axis / baseline
TICK_INK = "#52514e"  # tick + axis-label ink
TITLE_INK = "#0b0b0b"  # title ink
INK_GRAY = "#6f6e6a"  # dashed theory / reference lines
MUTED = "#a8a7a0"     # muted gray region (e.g. single fixed pattern)

# Sequential single-hue blue ramp (for any heatmap/sequential data) -- pale -> deep blue.
BLUE_RAMP = mcolors.LinearSegmentedColormap.from_list("blue_ramp", ["#cde2fb", "#0d366b"])
# Diverging blue<->red with gray midpoint.
DIVERGING = mcolors.LinearSegmentedColormap.from_list("blue_red", ["#0d366b", "#f0efec", "#8f1f1e"])

# --------------------------------------------------------------------------------------
# SERIES -> COLOUR MAPPING  (fixed by series identity, identical across every figure)
#
#   random_uniform ............ P1 blue      (also soft_log, K=64)
#   random_binary ............. P2 aqua      (also anscombe)
#   raw_shuffled .............. P3 yellow    (hadamard_raw_shuffled)
#   raw_ordered ............... P4 green     (hadamard_raw_ordered)
#   srht_paired ............... P5 violet    (srht_inverse, srht_full, K=128)
#   hadamard_ordered .......... P6 red       (hadamard_paired, orthogonal_inverse, naive_log)
#   hadamard_shuffled/permuted  P8 orange    (hadamard_random_paired)
# --------------------------------------------------------------------------------------
SERIES_COLOR = {
    # fig2 / fig3 measurement arms
    "random_uniform": P1,
    "random_binary": P2,
    "hadamard_raw_shuffled": P3,
    "hadamard_raw_ordered": P4,
    "srht_paired": P5,
    "hadamard_paired": P6,
    "hadamard_random_paired": P8,
    # fig4 reconstructors
    "random_dgi": P1,
    "srht_inverse": P5,
    "orthogonal_inverse": P6,
    # fig7 estimators
    "soft_log": P1,
    "anscombe": P2,
    "naive_log": P6,
    # fig8 design sizes
    "K64": P1,
    "K128": P5,
}

# Human-readable short labels for the fig3 arms.
ARM_LABEL = {
    "random_uniform": "random uniform",
    "random_binary": "random binary",
    "srht_paired": "SRHT",
    "hadamard_paired": "ordered Hadamard",
    "hadamard_random_paired": "permuted Hadamard",
    "hadamard_raw_ordered": "raw ordered",
    "hadamard_raw_shuffled": "raw shuffled",
}


# --------------------------------------------------------------------------------------
# Global style
# --------------------------------------------------------------------------------------
def apply_rcparams() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": AXIS,
            "axes.linewidth": 0.8,
            "axes.labelcolor": TICK_INK,
            "axes.grid": True,
            "axes.axisbelow": True,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "grid.color": GRID,
            "grid.linewidth": 0.6,
            "xtick.color": TICK_INK,
            "ytick.color": TICK_INK,
            "text.color": TITLE_INK,
            "font.family": "DejaVu Sans",
            "font.size": 8,
            "axes.labelsize": 9,
            "axes.titlesize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "legend.frameon": False,
            "lines.linewidth": 1.8,
            "lines.markersize": 5,
        }
    )


def style_ax(ax) -> None:
    """Consistent per-axes touch-up (spines, grid, tick ink)."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(AXIS)
        ax.spines[side].set_linewidth(0.8)
    ax.grid(True, color=GRID, linewidth=0.6)
    ax.tick_params(colors=TICK_INK, labelcolor=TICK_INK)


def tint(hex_color: str, frac: float) -> tuple:
    """Blend a colour toward white by `frac` in [0,1] (0 = original, 1 = white)."""
    rgb = np.array(mcolors.to_rgb(hex_color))
    return tuple(rgb + (1.0 - rgb) * float(frac))


def zorder_for(color: str) -> int:
    return 6 if color in LOW_CONTRAST else 4


def spread_positions(values: list[float], min_gap: float) -> list[float]:
    """Greedy vertical de-collision: nudge close label positions apart, keeping order.

    `values` and `min_gap` are in the axis's label coordinate (log10(y) for log axes,
    raw y for linear axes). Returns adjusted positions aligned to the input order.
    """
    order = sorted(range(len(values)), key=lambda i: values[i])
    out = list(values)
    prev = None
    for i in order:
        v = values[i]
        if prev is not None and v - prev < min_gap:
            v = prev + min_gap
        out[i] = v
        prev = v
    return out


def place_end_labels(ax, entries, *, log_y: bool, min_gap: float, dx: int = 4,
                     fontsize: float = 6.6) -> None:
    """Draw de-collided line-end labels. entries = [(x, y, color, text), ...]."""
    ys = [np.log10(y) if log_y else y for (_x, y, _c, _t) in entries]
    adj = spread_positions(ys, min_gap)
    for (x, _y, color, text), ly in zip(entries, adj):
        y = 10 ** ly if log_y else ly
        ax.annotate(text, xy=(x, y), xytext=(dx, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=fontsize, color=color,
                    fontweight="bold", clip_on=False)


def save(fig, name: str) -> Path:
    out = FIGS / name
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out


# --------------------------------------------------------------------------------------
# Fig 1  --  two-axis concept map (NEW, drawn from scratch)
# --------------------------------------------------------------------------------------
def fig1_conceptmap() -> Path:
    apply_rcparams()
    fig, ax = plt.subplots(figsize=(3.5, 2.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("auto")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)

    # Arrow-style axes.
    ax.annotate("", xy=(1.0, 0.045), xytext=(0.045, 0.045),
                arrowprops=dict(arrowstyle="-|>", color=AXIS, lw=1.4))
    ax.annotate("", xy=(0.045, 1.0), xytext=(0.045, 0.045),
                arrowprops=dict(arrowstyle="-|>", color=AXIS, lw=1.4))
    ax.text(0.52, -0.045, "Blind gain identifiability (statistical anchor)",
            ha="center", va="top", fontsize=8.5, color=TICK_INK)
    ax.text(-0.055, 0.52, "Static conditioning / exact inversion",
            ha="center", va="center", rotation=90, fontsize=8.5, color=TICK_INK)

    # Dashed trade-off diagonal (top-left <-> bottom-right).
    ax.plot([0.22, 0.82], [0.80, 0.22], linestyle=(0, (5, 4)),
            color=INK_GRAY, lw=1.3, zorder=2)
    ax.text(0.42, 0.46, "trade-off", rotation=-34, ha="center", va="bottom",
            fontsize=7, color=INK_GRAY, style="italic")

    # Four regions.  (x, y, color, marker, size, label, label x/y, ha, va)
    pts = [
        (0.22, 0.80, P6, "o", 90, "Ordered Hadamard /\nDCT / Fourier", 0.04, 0.90, "left", "bottom"),
        (0.82, 0.22, P1, "o", 90, "i.i.d. random\n+ DGI", 0.82, 0.115, "center", "top"),
        (0.22, 0.24, MUTED, "o", 70, "single fixed\npattern", 0.30, 0.24, "left", "center"),
    ]
    for x, y, c, m, s, label, lx, ly, ha, va in pts:
        ax.scatter([x], [y], s=s, c=[c], marker=m, edgecolors="white",
                   linewidths=0.8, zorder=zorder_for(c) + 2)
        ax.text(lx, ly, label, ha=ha, va=va, fontsize=7.2,
                color=(TICK_INK if c == MUTED else c), zorder=8, linespacing=1.05)

    # SRHT star -- top-right, "best of both".
    ax.scatter([0.82], [0.80], s=230, c=[P5], marker="*", edgecolors="white",
               linewidths=0.9, zorder=10)
    ax.text(0.99, 0.895, "Randomized Hadamard\n(SRHT)", ha="right", va="bottom",
            fontsize=7.2, color=P5, fontweight="bold", zorder=10, linespacing=1.05)
    ax.annotate("best of both", xy=(0.795, 0.775), xytext=(0.59, 0.70),
                fontsize=6.8, color=P5, style="italic",
                arrowprops=dict(arrowstyle="->", color=P5, lw=0.9),
                ha="center", va="center", zorder=10)

    fig.subplots_adjust(left=0.11, right=0.985, top=0.86, bottom=0.14)
    return save(fig, "fig1_conceptmap.png")


# --------------------------------------------------------------------------------------
# Fig 2  --  carrier traces (regenerated at the r2b protocol)
# --------------------------------------------------------------------------------------
def fig2_carrier_traces() -> Path:
    from src.mechanisms import moving_average_1d
    from src.paper_experiments import make_paper_basis, make_paper_objects

    apply_rcparams()

    image_size = 64
    seed = 20240708
    window = 64
    num_pixels = image_size * image_size  # 4096  -> paired/random arms use 8192 frames
    obj_name = "digit_0"

    objects = make_paper_objects(10, image_size=image_size, seed=seed)
    obj = next(o for o in objects if o.name == obj_name)

    # Arm (a): i.i.d. random-uniform carrier;  Arm (b): ordered (paired) Hadamard carrier.
    arms = [
        ("random_uniform", "random_uniform", "(a) i.i.d. random-uniform carrier"),
        ("hadamard_ordered", "hadamard_paired", "(b) ordered Hadamard carrier"),
    ]

    fig, axes = plt.subplots(2, 1, figsize=(3.5, 4.1), sharex=True)
    band_a = None
    for idx, (ax, (req_name, series_key, title)) in enumerate(zip(axes, arms)):
        basis = make_paper_basis(req_name, num_pixels, seed=seed)
        carrier = (basis.patterns @ obj.vector).cpu().to(dtype=torch.float32)
        running = moving_average_1d(carrier, window)
        n = carrier.numel()
        x = np.arange(n)
        c = carrier.numpy()
        rm = running.numpy()
        color = SERIES_COLOR[series_key]

        # Variance envelope: mean +/- std band (visual reference for stationarity).
        mu = float(c.mean())
        sd = float(c.std())
        ax.axhspan(mu - sd, mu + sd, color=color, alpha=0.08, zorder=1)
        ax.axhline(mu, color=AXIS, lw=0.8, zorder=1)

        # Thin carrier trace + bold running mean (darker shade for contrast).
        ax.plot(x, c, lw=0.6, alpha=0.8, color=color, zorder=3, label=r"$B_n$")
        dark = tuple(np.array(mcolors.to_rgb(color)) * 0.62)
        ax.plot(x, rm, lw=1.8, color=dark, zorder=6, label="running mean")

        style_ax(ax)
        ax.set_title(title, fontsize=8.5, loc="left", color=TITLE_INK)
        ax.set_ylabel(r"carrier $B_n$")
        ax.set_xlim(0, n)
        ax.margins(x=0)
        if idx == 0:
            band_a = (mu, sd, n)

    # Legend on the top panel; annotate the variance envelope on the flat band.
    top = axes[0]
    top.legend(loc="upper left", fontsize=7.2, ncol=2, handlelength=1.3,
               columnspacing=0.9, borderaxespad=0.3)
    mu, sd, n = band_a
    top.annotate(r"$\pm1\,\mathrm{SD}$ variance envelope", xy=(int(0.80 * n), mu + sd),
                 xytext=(int(0.55 * n), mu + 2.9 * sd), textcoords="data",
                 fontsize=6.6, color=TICK_INK, style="italic", ha="center", va="center",
                 arrowprops=dict(arrowstyle="->", color=TICK_INK, lw=0.7))
    axes[1].set_xlabel("frame index $n$")
    fig.suptitle(f"Noiseless bucket carriers  ({obj_name}, 8192 frames)",
                 fontsize=9, color=TITLE_INK, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    return save(fig, "fig2_carrier_traces.png")


# --------------------------------------------------------------------------------------
# Fig 3a  --  mean blind gain error vs W (log-log), one line per arm, rho = 1e-3
# --------------------------------------------------------------------------------------
def fig3a_error_vs_W() -> Path:
    apply_rcparams()
    df = pd.read_csv(RESULTS / "paper_fig3_gain_error_e12_local_r1" / "fig3_gain_est_error.csv")
    df = df[np.isclose(df["rho"], 1e-3)]

    # Fixed plotting order (keeps overlaps predictable; low-contrast arms drawn on top).
    order = [
        "hadamard_raw_ordered", "hadamard_raw_shuffled", "random_uniform",
        "random_binary", "srht_paired", "hadamard_paired", "hadamard_random_paired",
    ]
    order = [b for b in order if b in set(df["basis"])]

    fig, ax = plt.subplots(figsize=(3.5, 2.7))
    xmax = 0
    ends = []
    for basis in order:
        sub = df[df["basis"] == basis]
        curve = sub.groupby("W", as_index=False)["gain_rel_err"].mean().sort_values("W")
        color = SERIES_COLOR[basis]
        ax.plot(curve["W"], curve["gain_rel_err"], marker="o", ms=5, lw=1.8,
                color=color, zorder=zorder_for(color),
                markeredgecolor="white", markeredgewidth=0.5)
        xe = float(curve["W"].iloc[-1])
        ye = float(curve["gain_rel_err"].iloc[-1])
        xmax = max(xmax, xe)
        ends.append((xe, ye, color, ARM_LABEL[basis]))
    # Direct labels at line ends, vertically de-collided for the converging arms.
    place_end_labels(ax, ends, log_y=True, min_gap=0.135, fontsize=6.5)

    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlabel("AGC window $W$")
    ax.set_ylabel(r"blind gain error $\|\hat a-a\|/\|a\|$")
    ax.set_xlim(3.2, xmax * 2.6)  # headroom for direct labels
    style_ax(ax)
    fig.tight_layout()
    return save(fig, "fig3a_error_vs_W.png")


# --------------------------------------------------------------------------------------
# Fig 3c  --  err / theory-floor collapse for the variance-obeying arms, rho = 1e-3
# --------------------------------------------------------------------------------------
def fig3c_collapse() -> Path:
    apply_rcparams()
    df = pd.read_csv(RESULTS / "paper_fig3_gain_error_e12_local_r1" / "fig3_gain_est_error.csv")
    df = df[np.isclose(df["rho"], 1e-3)]

    collapse_arms = ["random_uniform", "random_binary", "srht_paired", "hadamard_random_paired"]
    collapse_arms = [a for a in collapse_arms if a in set(df["basis"])]

    fig, ax = plt.subplots(figsize=(3.5, 2.7))
    ends = []
    for basis in collapse_arms:
        color = SERIES_COLOR[basis]
        sub = df[df["basis"] == basis]
        # Per-object variance segment (W <= object's argmin-error W) + thin lines.
        seg_frames = []
        for obj, grp in sub.groupby("object"):
            per_w = grp.groupby("W")["gain_rel_err"].mean()
            argmin_w = int(per_w.idxmin())
            seg = grp[grp["W"] <= argmin_w].groupby("W", as_index=False)["err_over_floor"].mean()
            seg_frames.append(seg.assign(object=obj))
            ax.plot(seg["W"], seg["err_over_floor"], lw=0.7, alpha=0.35,
                    color=color, zorder=zorder_for(color) - 1)
        # Arm median across objects at each W (bold).
        allseg = pd.concat(seg_frames, ignore_index=True)
        med = allseg.groupby("W", as_index=False)["err_over_floor"].median().sort_values("W")
        ax.plot(med["W"], med["err_over_floor"], lw=2.1, color=color,
                marker="o", ms=5, markeredgecolor="white", markeredgewidth=0.5,
                zorder=zorder_for(color) + 2)
        ends.append((float(med["W"].iloc[-1]), float(med["err_over_floor"].iloc[-1]),
                     color, ARM_LABEL[basis]))
    place_end_labels(ax, ends, log_y=False, min_gap=0.065, fontsize=6.5)

    ax.set_xscale("log", base=2)
    ax.set_xlabel("AGC window $W$")
    ax.set_ylabel(r"err / theory floor $\sqrt{\mathrm{CV}_B^2/W}$")
    xr = ax.get_xlim()
    ax.set_xlim(xr[0], xr[1] * 2.8)
    style_ax(ax)
    fig.tight_layout()
    return save(fig, "fig3c_collapse.png")


# --------------------------------------------------------------------------------------
# Fig 4  --  reconstruction bridge: relMSE vs v (theory vs sim) and relMSE vs N
# --------------------------------------------------------------------------------------
def fig4_relmse_theory_vs_sim() -> Path:
    apply_rcparams()
    df = pd.read_csv(RESULTS / "paper_fig4_bridge_r2b" / "fig4_bridge.csv")
    summary = df.groupby(["basis", "N", "v"], as_index=False).agg(
        rel_mse_mean=("rel_mse", "mean"),
        theory_mean=("theory_rel_mse", "mean"),
    )
    order = ["orthogonal_inverse", "srht_inverse", "random_dgi"]
    label = {"orthogonal_inverse": "orthogonal", "srht_inverse": "SRHT", "random_dgi": "random / DGI"}
    pos = summary[summary["v"] > 0]

    fig, axes = plt.subplots(1, 2, figsize=(3.5, 2.0))

    # Panel (a): relMSE vs v, sim markers + dashed ink-gray theory.
    ax = axes[0]
    theory_drawn = False
    for basis in order:
        g = pos[pos["basis"] == basis]
        if g.empty:
            continue
        curve = g.groupby("v", as_index=False).agg(y=("rel_mse_mean", "mean"), th=("theory_mean", "mean"))
        curve = curve.sort_values("v")
        color = SERIES_COLOR[basis]
        ax.plot(curve["v"], curve["y"], marker="o", ms=4.5, lw=1.4, color=color,
                markeredgecolor="white", markeredgewidth=0.4,
                zorder=zorder_for(color), label=label[basis])
        ax.plot(curve["v"], curve["th"], linestyle=(0, (4, 3)), lw=1.1, color=INK_GRAY,
                zorder=2, label=("theory" if not theory_drawn else None))
        theory_drawn = True
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("residual gain var. $v$")
    ax.set_ylabel("relative MSE")
    style_ax(ax)
    ax.legend(loc="upper left", fontsize=6.2, handlelength=1.3, borderaxespad=0.2, labelspacing=0.3)

    # Panel (b): relMSE vs N (flatness of deterministic inverses vs 1/N random decay).
    ax = axes[1]
    seen = set()
    for basis in order:
        g = pos[pos["basis"] == basis]
        if g.empty:
            continue
        color = SERIES_COLOR[basis]
        for v, vg in g.groupby("v"):
            curve = vg.groupby("N", as_index=False)["rel_mse_mean"].mean().sort_values("N")
            if len(curve) < 2:
                continue
            lab = label[basis] if basis not in seen else None
            seen.add(basis)
            ax.plot(curve["N"], curve["rel_mse_mean"], marker="o", ms=3.5, lw=1.2,
                    alpha=0.85, color=color, markeredgecolor="white", markeredgewidth=0.3,
                    zorder=zorder_for(color), label=lab)
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlabel("frames / size $N$")
    ax.set_ylabel("relMSE")
    style_ax(ax)
    # Panel (b) shares (a)'s series->colour mapping and is fully filled by the
    # 15 (basis x v) curves, so no separate legend is drawn (colours carry identity):
    # the flat red/violet bundles are the deterministic inverses, the descending blue
    # bundle is random/DGI (~1/N).

    fig.tight_layout(w_pad=1.1)
    return save(fig, "fig4_relmse_theory_vs_sim.png")


# --------------------------------------------------------------------------------------
# Fig 5  --  finite-N flip boundary: interpolated rho* vs sigma_a for R^2 >= 0.9 fits
# --------------------------------------------------------------------------------------
def fig5_flip_boundary() -> Path:
    apply_rcparams()
    audit = RESULTS / "m2_boundary_audit_hadamard_order_dense_r1"
    fits = pd.read_csv(audit / "m2_boundary_fit.csv")
    boundaries = pd.read_csv(audit / "m2_boundary_interpolated.csv")

    ok = fits[(fits["fit_status"] == "ok") & (fits["r2"] >= 0.9)].copy()
    ok = ok.sort_values("r2", ascending=False)

    # All ok fits are SRHT-paired vs ordered Hadamard under different correction refs;
    # give each correction a distinct, fixed palette hue (SRHT identity = violet first).
    corr_color = {"none": P5, "reference_k8": P1, "reference_k32": P2, "scgi_proxy": P8}
    corr_label = {"none": "no correction", "reference_k8": "ref k=8",
                  "reference_k32": "ref k=32", "scgi_proxy": "SCGI proxy"}

    fig, ax = plt.subplots(figsize=(3.5, 2.7))
    for _, row in ok.iterrows():
        corr = str(row["correction"])
        color = corr_color.get(corr, PALETTE[0])
        mask = (
            (boundaries["correction"] == corr)
            & (boundaries["challenger"] == row["challenger"])
            & (boundaries["baseline"] == row["baseline"])
            & (boundaries["boundary_status"] == "observed")
            & boundaries["rho_star_log_interp"].notna()
        )
        pts = boundaries[mask].sort_values("sigma_a")
        if pts.empty:
            continue
        ax.scatter(pts["sigma_a"], pts["rho_star_log_interp"], s=30, color=color,
                   edgecolors="white", linewidths=0.5, zorder=zorder_for(color) + 2,
                   label=f"{corr_label.get(corr, corr)} ($R^2$={float(row['r2']):.3f})")
        x = np.geomspace(float(pts["sigma_a"].min()), float(pts["sigma_a"].max()), 80)
        y = 10 ** (float(row["intercept"]) + float(row["sigma_a_exponent"]) * np.log10(x))
        ax.plot(x, y, lw=1.4, color=color, zorder=zorder_for(color))

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"gain amplitude $\sigma_a$")
    ax.set_ylabel(r"interpolated $\rho^{*}$")
    style_ax(ax)
    ax.legend(loc="best", fontsize=6.3, handlelength=1.0, labelspacing=0.35,
              handletextpad=0.4)
    fig.tight_layout()
    return save(fig, "fig5_flip_boundary.png")


# --------------------------------------------------------------------------------------
# Fig 6  --  SRHT ablation: delta-vs-ordered bars + delta-vs-rho collapse
# --------------------------------------------------------------------------------------
def fig6_ablation() -> Path:
    apply_rcparams()
    m = pd.read_csv(RESULTS / "srht_m3_audit_highrho_r2" / "m3_srht_delta_summary.csv")

    # Panel (a): delta vs ordered Hadamard (dB) at rho=1e-3 (agc correction).
    row = m[(np.isclose(m["rho"], 1e-3)) & (m["correction"] == "agc")].iloc[0]
    base_psnr = float(row["hadamard_ordered_psnr"])
    arms = ["perm_only", "sign_only", "sign_block_shuffle", "sign_time_interleave", "srht_full"]
    arm_disp = {
        "perm_only": "permutation only",
        "sign_only": "sign only",
        "sign_block_shuffle": "sign + block shuffle",
        "sign_time_interleave": "sign + time interleave",
        "srht_full": "full SRHT",
    }
    deltas = [(a, float(row[a + "_psnr"]) - base_psnr) for a in arms]

    fig, axes = plt.subplots(1, 2, figsize=(3.5, 2.15), gridspec_kw={"width_ratios": [2.0, 1.25]})

    ax = axes[0]
    ypos = np.arange(len(deltas))
    for i, (a, d) in enumerate(deltas):
        # Violet family; emphasize the full-SRHT bar.
        if a == "srht_full":
            c = P5
            edge = TITLE_INK
            lw = 1.0
        else:
            c = tint(P5, 0.42)
            edge = "white"
            lw = 0.6
        ax.barh(ypos[i], d, color=c, edgecolor=edge, linewidth=lw, height=0.68, zorder=3)
        ax.text(d + 0.06, ypos[i], f"{d:+.2f}", va="center", ha="left",
                fontsize=6.3, color=TICK_INK)
    ax.set_yticks(ypos)
    ax.set_yticklabels([arm_disp[a] for a, _ in deltas], fontsize=6.6)
    ax.set_xlabel(r"$\Delta$ PSNR vs ordered (dB)")
    ax.set_xlim(0, max(d for _, d in deltas) * 1.22)
    ax.set_title(r"(a) ablation at $\rho=10^{-3}$", fontsize=8, loc="left")
    style_ax(ax)
    ax.grid(True, axis="x", color=GRID, linewidth=0.6)
    ax.grid(False, axis="y")

    # Panel (b): full-SRHT delta vs rho (log-x); collapses to ~0; sub-floor shaded gray.
    ax = axes[1]
    agc = m[m["correction"] == "agc"].sort_values("rho")
    rhos = agc["rho"].to_numpy(dtype=float)
    dd = agc["srht_minus_ordered_db"].to_numpy(dtype=float)
    abovefloor = agc["above_floor"].astype(bool).to_numpy()
    # Shade the contiguous sub-floor (not above floor) region gray.
    sub = rhos[~abovefloor]
    if sub.size:
        lo = float(sub.min()) / 1.6
        ax.axvspan(lo, float(rhos.max()) * 1.6, color=MUTED, alpha=0.22, zorder=1,
                   label="sub-floor")
    ax.axhline(0.0, color=AXIS, lw=0.8, zorder=2)
    ax.plot(rhos, dd, marker="o", ms=5, lw=1.8, color=P5,
            markeredgecolor="white", markeredgewidth=0.5, zorder=5)
    ax.set_xscale("log")
    ax.set_xlabel(r"$\rho$")
    ax.set_ylabel(r"$\Delta$ dB (full SRHT)")
    ax.set_title("(b) vs drift", fontsize=8, loc="left")
    style_ax(ax)
    ax.legend(loc="upper right", fontsize=6.0, handlelength=1.1, borderaxespad=0.2)

    fig.tight_layout(w_pad=1.1)
    return save(fig, "fig6_ablation.png")


# --------------------------------------------------------------------------------------
# Fig 7  --  low-photon gain MSE vs photon budget (three estimators + Fisher reference)
# --------------------------------------------------------------------------------------
def fig7_gainMSE_vs_photon() -> Path:
    apply_rcparams()
    df = pd.read_csv(RESULTS / "paper_fig7_lowphoton_r2" / "fig7_lowphoton.csv")
    summary = df.groupby(["method", "photon_budget"], as_index=False).agg(
        y=("gain_rel_mse", "mean"),
        yerr=("gain_rel_mse", "std"),
        lam=("lambda_bar", "mean"),
        fisher=("fisher_reference", "mean"),
    )

    fig, ax = plt.subplots(figsize=(3.5, 2.7))

    # Shade the shrinkage-bias region (mean photon count lambda_bar < 1).
    soft = summary[summary["method"] == "soft_log"].sort_values("photon_budget")
    below = soft[soft["lam"] < 1.0]["photon_budget"]
    if len(below):
        xhi = float(below.max())
        xlo = float(summary["photon_budget"].min()) / 1.4
        ax.axvspan(xlo, xhi * (float(soft["photon_budget"].iloc[1] / soft["photon_budget"].iloc[0]) ** 0.5),
                   color=MUTED, alpha=0.18, zorder=1, label=r"$\bar\lambda<1$")

    method_order = ["soft_log", "naive_log", "anscombe"]
    method_disp = {"soft_log": "soft-log", "naive_log": "naive log", "anscombe": "Anscombe"}
    for method in method_order:
        g = summary[summary["method"] == method].sort_values("photon_budget")
        color = SERIES_COLOR[method]
        ax.errorbar(g["photon_budget"], g["y"], yerr=g["yerr"].fillna(0.0),
                    marker="o", ms=5, lw=1.8, capsize=2, color=color,
                    markeredgecolor="white", markeredgewidth=0.5,
                    ecolor=color, elinewidth=0.8, zorder=zorder_for(color),
                    label=method_disp[method])

    ref = summary.groupby("photon_budget", as_index=False)["fisher"].mean().sort_values("photon_budget")
    ax.plot(ref["photon_budget"], ref["fisher"], linestyle=(0, (4, 3)), lw=1.2,
            color=INK_GRAY, zorder=3, label=r"$1/(W\bar\lambda)$")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"mean photon budget $\bar\lambda$")
    ax.set_ylabel("gain MSE")
    style_ax(ax)
    ax.legend(loc="lower left", fontsize=6.6, handlelength=1.4, labelspacing=0.3,
              borderaxespad=0.2)
    fig.tight_layout()
    return save(fig, "fig7_gainMSE_vs_photon.png")


# --------------------------------------------------------------------------------------
# Fig 8  --  tall-design threshold: rank-test pass rate + solver success vs margin
# --------------------------------------------------------------------------------------
def fig8_threshold() -> Path:
    apply_rcparams()
    d64 = pd.read_csv(RESULTS / "tall_design_threshold_full_r1_merged" / "threshold_scan.csv")
    d128 = pd.read_csv(RESULTS / "tall_design_threshold_K128_r1_merged" / "threshold_scan.csv")

    def agg(d):
        return d.groupby("offset", as_index=False).agg(
            rank=("local_identifiable", "mean"),
            solver=("solver_success", "mean"),
        ).sort_values("offset")

    a64, a128 = agg(d64), agg(d128)

    fig, axes = plt.subplots(1, 2, figsize=(3.5, 2.05), sharex=True)

    def hairline(ax):
        ax.axvline(-1.0, color=INK_GRAY, lw=1.0, linestyle=(0, (2, 2)), zorder=2)

    # Panel (a): rank-test pass rate.
    ax = axes[0]
    ax.plot(a64["offset"], a64["rank"], marker="o", ms=4.5, lw=1.8, color=SERIES_COLOR["K64"],
            markeredgecolor="white", markeredgewidth=0.4, zorder=5, label="$K=64$")
    ax.plot(a128["offset"], a128["rank"], marker="s", ms=4.0, lw=1.6, linestyle=(0, (4, 2)),
            color=SERIES_COLOR["K128"], markeredgecolor="white", markeredgewidth=0.4,
            zorder=4, label="$K=128$")
    hairline(ax)
    ax.annotate("$N\\!=\\!K\\!+\\!p\\!-\\!1$", xy=(-1.0, 0.72), xytext=(-7.6, 0.60),
                fontsize=6.3, color=INK_GRAY, va="center", ha="left",
                arrowprops=dict(arrowstyle="->", color=INK_GRAY, lw=0.8))
    ax.set_ylabel("rank-test pass rate")
    ax.set_xlabel("margin $N-K-p$")
    ax.set_ylim(-0.05, 1.08)
    ax.set_title("(a) local rank test", fontsize=8, loc="left")
    style_ax(ax)
    ax.legend(loc="lower right", fontsize=6.4, handlelength=1.6, borderaxespad=0.3)

    # Panel (b): solver success.
    ax = axes[1]
    ax.plot(a64["offset"], a64["solver"], marker="o", ms=4.5, lw=1.8, color=SERIES_COLOR["K64"],
            markeredgecolor="white", markeredgewidth=0.4, zorder=5, label="$K=64$")
    ax.plot(a128["offset"], a128["solver"], marker="s", ms=4.0, lw=1.6, linestyle=(0, (4, 2)),
            color=SERIES_COLOR["K128"], markeredgecolor="white", markeredgewidth=0.4,
            zorder=4, label="$K=128$")
    hairline(ax)
    ax.set_ylabel("solver success rate")
    ax.set_xlabel("margin $N-K-p$")
    ax.set_title("(b) blind solver", fontsize=8, loc="left")
    style_ax(ax)
    ax.legend(loc="upper left", fontsize=6.4, handlelength=1.6, borderaxespad=0.2)

    fig.tight_layout(w_pad=1.1)
    return save(fig, "fig8_threshold.png")


# --------------------------------------------------------------------------------------
def main() -> None:
    import sys

    # Ensure repo-root imports (src.*) resolve when run from anywhere.
    sys.path.insert(0, str(ROOT))

    builders = [
        ("fig1_conceptmap.png", fig1_conceptmap),
        ("fig2_carrier_traces.png", fig2_carrier_traces),
        ("fig3a_error_vs_W.png", fig3a_error_vs_W),
        ("fig3c_collapse.png", fig3c_collapse),
        ("fig4_relmse_theory_vs_sim.png", fig4_relmse_theory_vs_sim),
        ("fig5_flip_boundary.png", fig5_flip_boundary),
        ("fig6_ablation.png", fig6_ablation),
        ("fig7_gainMSE_vs_photon.png", fig7_gainMSE_vs_photon),
        ("fig8_threshold.png", fig8_threshold),
    ]
    for name, fn in builders:
        out = fn()
        size = out.stat().st_size
        print(f"[ok] {out.relative_to(ROOT)}  ({size:,} bytes)")


if __name__ == "__main__":
    main()
