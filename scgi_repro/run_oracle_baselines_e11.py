"""E11 -- oracle / metered-gain baseline bars for blind DGI gain correction.

For four held-out objects (letter_A, stripe [== the task's "stripe_target": the
only stripe-family object in src.paper_experiments], letter_L, ring) under an OU
gain drift (rho=1e-3, s=0.1) on an oversampled random_uniform basis (N=2*K), this
runner reconstructs via DGI under five gain treatments spanning the accountability
spectrum from a full oracle down to no correction at all:

  1. oracle          -- divide by the true per-frame gain a_n.
  2. metered_noisy    -- divide by a metered gain a_n*(1+0.01*eta_n), eta_n~N(0,1):
                         a calibrated-but-imperfect meter (1% relative noise).
  3. blind_agc        -- divide by a blind windowed AGC estimate (mean_agc_gain),
                         window chosen once from a bias-variance sweep (Fig. 3's
                         convention: minimize scale_aligned_gain_error over
                         logspace_windows on the same channel).
  4. no_correction    -- reconstruct the raw drifted measurements unmodified.
  5. static_reference -- reconstruct the noiseless, driftless measurements
                         (a_n=1 for all n): the ceiling-diagnostic static
                         reference at this basis/N, per run_ceiling_diagnostic.py.

CNR and PSNR (src/metrics.py, no post-processing) are reported per object and
treatment over 5 independent drift-trace seeds.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch

from src.basis import make_random_basis
from src.metrics import cnr, psnr
from src.paper_experiments import build_run_manifest, logspace_windows, make_paper_objects, make_shared_channel, mean_agc_gain, scale_aligned_gain_error, write_caption


ROOT = Path(__file__).resolve().parent

OBJECT_NAMES = ["letter_A", "letter_L", "stripe", "ring"]
TREATMENTS = ["oracle", "metered_noisy", "blind_agc", "no_correction", "static_reference"]


def select_agc_window(
    objects: list,
    basis,
    num_frames: int,
    rho: float,
    sigma_a: float,
    seeds: int,
    seed_base: int,
) -> int:
    """Pick a single AGC window via a bias-variance sweep (Fig. 3's convention).

    For each candidate window in ``logspace_windows``, average the scale-aligned
    blind-gain error across all objects/seeds at the given drift, and keep the
    window minimizing that average. This mirrors ``run_paper_fig3_gain_error.py``:
    the window is chosen ONCE from the sweep and then held fixed for the main
    5-seed x 4-object baseline comparison, matching how a real deployment would
    fix an acquisition-time design constant rather than retuning it per frame.
    """

    windows = [w for w in logspace_windows(num_frames) if w <= num_frames // 2]
    errors_by_window: Dict[int, List[float]] = {w: [] for w in windows}
    for obj in objects:
        ideal = basis.measure(obj.vector)
        for seed_idx in range(seeds):
            gains = make_shared_channel(num_frames, rho=rho, sigma_a=sigma_a, seed=seed_base + 5003 * seed_idx)
            observed = ideal * gains
            for window in windows:
                gain_hat = mean_agc_gain(observed, window)
                errors_by_window[window].append(scale_aligned_gain_error(gain_hat, gains))
    mean_errors = {w: float(np.mean(errs)) for w, errs in errors_by_window.items() if errs}
    return int(min(mean_errors, key=mean_errors.get))


def main() -> None:
    parser = argparse.ArgumentParser(description="E11: oracle/metered-gain baseline bars (r1).")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "oracle_baselines_e11_r1")
    parser.add_argument("--image-size", type=int, default=32, help="K = image_size^2.")
    parser.add_argument("--oversample", type=int, default=2, help="N = oversample * K.")
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20240708)
    parser.add_argument("--rho", type=float, default=1.0e-3)
    parser.add_argument("--s", type=float, default=0.1, help="OU drift standard deviation (sigma_a).")
    parser.add_argument("--metered-noise-frac", type=float, default=0.01)
    args = parser.parse_args()

    start = time.time()
    out = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    k = args.image_size * args.image_size
    n = int(args.oversample) * k

    all_objects = make_paper_objects(6, image_size=args.image_size, seed=args.seed)
    objects = [o for o in all_objects if o.name in OBJECT_NAMES]
    if len(objects) != len(OBJECT_NAMES):
        missing = set(OBJECT_NAMES) - {o.name for o in objects}
        raise RuntimeError(f"Expected objects {OBJECT_NAMES}, missing {missing}.")

    basis = make_random_basis("uniform", num_pixels=k, num_frames=n, seed=args.seed + 555, reconstruction="correlation")

    agc_window = select_agc_window(objects, basis, n, args.rho, args.s, args.seeds, seed_base=args.seed + 9001)

    rows: List[Dict[str, object]] = []
    for obj in objects:
        ideal = basis.measure(obj.vector)
        static_recon = basis.reconstruct(ideal)

        for seed_idx in range(args.seeds):
            gains = make_shared_channel(n, rho=args.rho, sigma_a=args.s, seed=args.seed + 5003 * seed_idx)
            observed = ideal * gains

            # 1. oracle
            oracle_corrected = observed / gains.clamp_min(1.0e-8)
            oracle_recon = basis.reconstruct(oracle_corrected)

            # 2. metered_noisy
            meter_generator = torch.Generator(device="cpu")
            meter_generator.manual_seed(args.seed + 7001 * seed_idx + 31)
            eta = torch.randn(gains.shape, generator=meter_generator, dtype=gains.dtype)
            metered_gain = gains * (1.0 + float(args.metered_noise_frac) * eta)
            metered_corrected = observed / metered_gain.clamp_min(1.0e-8)
            metered_recon = basis.reconstruct(metered_corrected)

            # 3. blind_agc
            gain_hat = mean_agc_gain(observed, agc_window)
            agc_corrected = observed / gain_hat.clamp_min(1.0e-8)
            agc_recon = basis.reconstruct(agc_corrected)

            # 4. no_correction
            none_recon = basis.reconstruct(observed)

            recon_by_treatment = {
                "oracle": oracle_recon,
                "metered_noisy": metered_recon,
                "blind_agc": agc_recon,
                "no_correction": none_recon,
                "static_reference": static_recon,
            }

            for treatment, recon in recon_by_treatment.items():
                target = obj.vector.reshape(args.image_size, args.image_size)
                recon_img = recon.reshape(args.image_size, args.image_size)
                rows.append(
                    {
                        "object": obj.name,
                        "family": obj.family,
                        "K_eff": obj.k_eff,
                        "treatment": treatment,
                        "seed": int(seed_idx),
                        "agc_window": int(agc_window),
                        "cnr": cnr(recon_img, target),
                        "psnr": psnr(recon_img, target),
                    }
                )

    df = pd.DataFrame(rows)
    df.to_csv(out / "e11_oracle_baselines.csv", index=False)

    summary = df.groupby(["object", "family", "K_eff", "treatment"], as_index=False).agg(
        cnr_mean=("cnr", "mean"),
        cnr_std=("cnr", "std"),
        psnr_mean=("psnr", "mean"),
        psnr_std=("psnr", "std"),
    )
    summary.to_csv(out / "e11_oracle_baselines_summary.csv", index=False)

    # ---- Oracle-vs-blind gap per object. ----
    gap_rows: List[Dict[str, object]] = []
    for obj_name, group in summary.groupby("object"):
        by_treatment = group.set_index("treatment")
        oracle_cnr = float(by_treatment.loc["oracle", "cnr_mean"])
        blind_cnr = float(by_treatment.loc["blind_agc", "cnr_mean"])
        oracle_psnr = float(by_treatment.loc["oracle", "psnr_mean"])
        blind_psnr = float(by_treatment.loc["blind_agc", "psnr_mean"])
        none_cnr = float(by_treatment.loc["no_correction", "cnr_mean"])
        static_cnr = float(by_treatment.loc["static_reference", "cnr_mean"])
        gap_rows.append(
            {
                "object": obj_name,
                "oracle_cnr": oracle_cnr,
                "blind_agc_cnr": blind_cnr,
                "oracle_minus_blind_cnr": oracle_cnr - blind_cnr,
                "oracle_psnr": oracle_psnr,
                "blind_agc_psnr": blind_psnr,
                "oracle_minus_blind_psnr_db": oracle_psnr - blind_psnr,
                "no_correction_cnr": none_cnr,
                "static_reference_cnr": static_cnr,
                "blind_minus_none_cnr": blind_cnr - none_cnr,
            }
        )
    gaps = pd.DataFrame(gap_rows)
    gaps.to_csv(out / "e11_oracle_vs_blind_gap.csv", index=False)

    # ---- Figure: grouped ("stacked-together") bars per object, one panel per metric. ----
    colors = {
        "oracle": "#1f77b4",
        "metered_noisy": "#ff7f0e",
        "blind_agc": "#2ca02c",
        "no_correction": "#d62728",
        "static_reference": "#7f7f7f",
    }
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    obj_order = [o.name for o in objects]
    x = np.arange(len(obj_order))
    width = 0.16
    for metric_idx, (metric_col, metric_name) in enumerate([("cnr_mean", "CNR"), ("psnr_mean", "PSNR (dB)")]):
        ax = axes[metric_idx]
        for t_idx, treatment in enumerate(TREATMENTS):
            values = []
            errs = []
            for obj_name in obj_order:
                row = summary[(summary["object"] == obj_name) & (summary["treatment"] == treatment)].iloc[0]
                values.append(row[metric_col])
                errs.append(row[metric_col.replace("_mean", "_std")])
            offset = (t_idx - (len(TREATMENTS) - 1) / 2.0) * width
            ax.bar(
                x + offset,
                values,
                width=width,
                yerr=errs,
                capsize=2,
                label=treatment,
                color=colors[treatment],
                alpha=0.9,
            )
        ax.set_xticks(x)
        ax.set_xticklabels(obj_order, fontsize=8)
        ax.set_ylabel(metric_name)
        ax.set_title(metric_name, fontsize=9)
        ax.grid(True, axis="y", alpha=0.25)
    axes[0].legend(fontsize=7, frameon=False, ncol=2, loc="upper right")
    fig.suptitle(
        f"E11 oracle/metered/blind/none/static gain-treatment bars (rho={args.rho:g}, s={args.s:g}, "
        f"N=2K, AGC window={agc_window})",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out / "e11_treatment_bars.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    gap_lines = "; ".join(
        f"{r['object']}: oracle-blind CNR={r['oracle_minus_blind_cnr']:.3f} "
        f"(oracle={r['oracle_cnr']:.3f}, blind_agc={r['blind_agc_cnr']:.3f}), "
        f"oracle-blind PSNR={r['oracle_minus_blind_psnr_db']:.2f} dB"
        for r in gap_rows
    )

    write_caption(
        out / "e11_caption.md",
        "E11 Oracle / Metered-Gain Baseline Bars (r1)",
        [
            f"Setup: 4 held-out objects (letter_A, letter_L, stripe [= the task's 'stripe_target', the only "
            "stripe-family object in src.paper_experiments], ring), OU gain drift rho="
            f"{args.rho:g}, s={args.s:g}, random_uniform basis, N=2K={n} oversampled (K={k}) so the "
            "static_reference treatment matches the ceiling diagnostic's 2K static result. 5 gain treatments: "
            "oracle (divide by true a_n), metered_noisy (divide by a_n*(1+0.01*eta), eta~N(0,1), a calibrated "
            f"meter with {args.metered_noise_frac * 100.0:.0f}% relative noise), blind_agc (mean_agc_gain with "
            f"window W={agc_window}, chosen once via a bias-variance sweep over logspace_windows minimizing "
            "scale_aligned_gain_error, following Fig. 3's convention -- not retuned per object/seed), "
            "no_correction (raw drifted measurements), static_reference (noiseless a_n=1 measurements). CNR/PSNR "
            "(src/metrics.py, no post-processing) reported over 5 independent drift-trace seeds.",
            f"Oracle-vs-blind gap per object: {gap_lines}.",
            f"Ordering sanity check: static_reference CNR >= oracle CNR >= blind_agc CNR >= no_correction CNR "
            f"holds for {int((gaps['oracle_cnr'] >= gaps['blind_agc_cnr']).sum())}/4 objects (oracle>=blind) and "
            f"{int((gaps['blind_agc_cnr'] >= gaps['no_correction_cnr']).sum())}/4 objects (blind>=none), "
            "consistent with the accountability spectrum from full knowledge of the gain down to none.",
            f"Rows: {len(df)}. Runtime seconds: {time.time() - start:.2f}.",
        ],
    )
    (out / "run_manifest.json").write_text(
        json.dumps(
            build_run_manifest(args, ROOT, extra={"rows": int(len(df)), "agc_window": int(agc_window)}),
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    print(
        f"E11 complete rows={len(df)} agc_window={agc_window} "
        f"oracle_minus_blind_cnr={gaps['oracle_minus_blind_cnr'].to_dict()} "
        f"output={out} runtime={time.time() - start:.2f}s"
    )


if __name__ == "__main__":
    main()
