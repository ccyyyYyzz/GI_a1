from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

from src.config_utils import project_root


@dataclass(frozen=True)
class PublishedTarget:
    paper: str
    figure: str
    panel: str
    experiment: str
    sample: str
    condition: str
    method: str
    metric: str
    value: float
    unit: str
    extraction: str
    source_path: str
    note: str = ""
    approximate: bool = False
    uncertainty: float | None = None


def _relpath(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(project_root()))
    except Exception:
        return str(path)


def _target(
    *,
    paper: str,
    figure: str,
    panel: str,
    experiment: str,
    sample: str,
    condition: str,
    method: str,
    metric: str,
    value: float,
    unit: str,
    extraction: str,
    source_path: Path,
    note: str = "",
    approximate: bool = False,
    uncertainty: float | None = None,
) -> PublishedTarget:
    return PublishedTarget(
        paper=paper,
        figure=figure,
        panel=panel,
        experiment=experiment,
        sample=sample,
        condition=condition,
        method=method,
        metric=metric,
        value=float(value),
        unit=unit,
        extraction=extraction,
        source_path=_relpath(source_path),
        note=note,
        approximate=approximate,
        uncertainty=uncertainty,
    )


def apl_targets(root: Path) -> list[PublishedTarget]:
    paper = "Peng and Chen, Applied Physics Letters 2024 SCGI"
    text = root / "results" / "pdf_text" / "scgi_text.txt"
    apl6 = root / "results" / "paper_figures" / "apl_pages" / "apl-6.png"
    apl7 = root / "results" / "paper_figures" / "apl_pages" / "apl-7.png"
    rows: list[PublishedTarget] = []
    for panel, method, cnr in [
        ("a", "GI", 0.098),
        ("b", "SCGI", 4.04),
        ("c", "SCGI-UNN", 7.93),
        ("d", "SCGI-URED", 10.43),
    ]:
        rows.append(
            _target(
                paper=paper,
                figure="Fig. 6",
                panel=panel,
                experiment="USAF 1951 target through dynamic turbid water",
                sample="USAF 1951",
                condition="dynamic complex scattering",
                method=method,
                metric="CNR",
                value=cnr,
                unit="a.u.",
                extraction="exact_text_from_pdf",
                source_path=apl6 if apl6.exists() else text,
            )
        )

    for sample, scgi, unn, ured in [
        ("0", 3.39, 14.20, 34.91),
        ("nd", 3.83, 11.27, 35.76),
        ("Eq", 3.54, 12.12, 38.28),
    ]:
        rows.append(
            _target(
                paper=paper,
                figure="Fig. 9",
                panel="a/e/i",
                experiment="letter samples through dynamic turbid water",
                sample=sample,
                condition="conventional GI remains approximately zero CNR",
                method="GI",
                metric="CNR",
                value=0.0,
                unit="a.u.",
                extraction="text_approximation",
                source_path=apl7 if apl7.exists() else text,
                note="Paper states CNR values remain approximately 0.",
                approximate=True,
                uncertainty=0.1,
            )
        )
        for panel, method, cnr in [
            ("b/f/j", "SCGI", scgi),
            ("c/g/k", "SCGI-UNN", unn),
            ("d/h/l", "SCGI-URED", ured),
        ]:
            rows.append(
                _target(
                    paper=paper,
                    figure="Fig. 9",
                    panel=panel,
                    experiment="letter samples through dynamic turbid water",
                    sample=sample,
                    condition="dynamic complex scattering",
                    method=method,
                    metric="CNR",
                    value=cnr,
                    unit="a.u.",
                    extraction="exact_text_from_pdf",
                    source_path=apl7 if apl7.exists() else text,
                )
            )
    return rows


def _add_oe_pair(
    rows: list[PublishedTarget],
    *,
    figure: str,
    panel: str,
    experiment: str,
    sample: str,
    condition: str,
    method: str,
    psnr: float,
    ssim: float | None,
    extraction: str,
    source_path: Path,
    approximate: bool = False,
    psnr_uncertainty: float | None = None,
    ssim_uncertainty: float | None = None,
    note: str = "",
) -> None:
    paper = "Peng, Xiao, and Chen, Optics Express 2025 OWT"
    rows.append(
        _target(
            paper=paper,
            figure=figure,
            panel=panel,
            experiment=experiment,
            sample=sample,
            condition=condition,
            method=method,
            metric="PSNR",
            value=psnr,
            unit="dB",
            extraction=extraction,
            source_path=source_path,
            note=note,
            approximate=approximate,
            uncertainty=psnr_uncertainty,
        )
    )
    if ssim is not None:
        rows.append(
            _target(
                paper=paper,
                figure=figure,
                panel=panel,
                experiment=experiment,
                sample=sample,
                condition=condition,
                method=method,
                metric="SSIM",
                value=ssim,
                unit="a.u.",
                extraction=extraction,
                source_path=source_path,
                note=note,
                approximate=approximate,
                uncertainty=ssim_uncertainty,
            )
        )


def oe_targets(root: Path) -> list[PublishedTarget]:
    rows: list[PublishedTarget] = []
    text = root / "results" / "pdf_text" / "owc_text.txt"
    oe7 = root / "results" / "paper_figures" / "oe_pages" / "oe-07.png"
    oe8 = root / "results" / "paper_figures" / "oe_pages" / "oe-08.png"
    oe9 = root / "results" / "paper_figures" / "oe_pages" / "oe-09.png"
    oe11 = root / "results" / "paper_figures" / "oe_pages" / "oe-11.png"

    beta_order = [1.22e-2, 1.12e-2, 1.28e-2, 8.92e-3, 1.02e-2, 9.75e-3]
    no_ref_psnr = [12.50, 12.62, 14.92, 14.00, 19.23, 15.04]
    no_ref_ssim = [0.8449, 0.7930, 0.8885, 0.8247, 0.9476, 0.8808]
    ref_psnr = [37.60, 35.32, 38.02, 37.91, 37.68, 36.86]
    ref_ssim = [0.9854, 0.9938, 0.9942, 0.9911, 0.9952, 0.9838]
    for idx, beta in enumerate(beta_order, start=1):
        sample = f"image_{idx}"
        cond = f"attenuation_beta={beta:.4g} mm^-1"
        _add_oe_pair(
            rows,
            figure="Fig. 3",
            panel=chr(ord("g") + idx - 1),
            experiment="six 64x64 images, no reference pattern",
            sample=sample,
            condition=cond,
            method="without_reference",
            psnr=no_ref_psnr[idx - 1],
            ssim=no_ref_ssim[idx - 1],
            extraction="exact_caption_from_pdf",
            source_path=oe7 if oe7.exists() else text,
        )
        _add_oe_pair(
            rows,
            figure="Fig. 3",
            panel=chr(ord("m") + idx - 1),
            experiment="six 64x64 images, fixed reference pattern",
            sample=sample,
            condition=cond,
            method="fixed_reference",
            psnr=ref_psnr[idx - 1],
            ssim=ref_ssim[idx - 1],
            extraction="exact_caption_from_pdf",
            source_path=oe7 if oe7.exists() else text,
        )

    for idx, psnr in enumerate([14.18, 14.50, 17.90, 14.16, 18.00, 16.38], start=1):
        _add_oe_pair(
            rows,
            figure="Fig. 4",
            panel=chr(ord("a") + idx - 1),
            experiment="30th row profile, no reference pattern",
            sample=f"image_{idx}",
            condition="row profile from Fig. 3(a-f)",
            method="without_reference",
            psnr=psnr,
            ssim=None,
            extraction="exact_caption_from_pdf",
            source_path=oe8 if oe8.exists() else text,
        )
    for idx, psnr in enumerate([38.04, 35.88, 37.83, 39.68, 39.18, 40.29], start=1):
        _add_oe_pair(
            rows,
            figure="Fig. 5",
            panel=chr(ord("a") + idx - 1),
            experiment="30th row profile, fixed reference pattern",
            sample=f"image_{idx}",
            condition="row profile from Fig. 3(a-f)",
            method="fixed_reference",
            psnr=psnr,
            ssim=None,
            extraction="exact_caption_from_pdf",
            source_path=oe9 if oe9.exists() else text,
        )

    beta_x1e2 = [0.892, 1.22, 1.40, 1.76, 1.91, 2.29, 2.39, 3.47]
    fig6_no_ref = [
        (16.2, 0.88),
        (12.5, 0.82),
        (10.7, 0.67),
        (9.8, 0.63),
        (8.4, 0.52),
        (7.8, 0.48),
        (7.9, 0.55),
        (6.2, 0.35),
    ]
    fig6_ref = [
        (37.8, 0.984),
        (37.7, 0.984),
        (35.8, 0.985),
        (32.7, 0.980),
        (29.8, 0.983),
        (28.4, 0.982),
        (26.3, 0.970),
        (23.3, 0.975),
    ]
    for beta, (psnr, ssim) in zip(beta_x1e2, fig6_no_ref):
        _add_oe_pair(
            rows,
            figure="Fig. 6",
            panel="a",
            experiment="attenuation sweep, no reference pattern",
            sample="Fig. 3(a) carrier image",
            condition=f"attenuation_beta_x1e2={beta:.3g} mm^-1",
            method="without_reference",
            psnr=psnr,
            ssim=ssim,
            extraction="manual_digitized_from_rendered_page",
            source_path=oe9,
            approximate=True,
            psnr_uncertainty=0.4,
            ssim_uncertainty=0.02,
            note="Approximate point read from rendered Fig. 6; exact x positions are listed in the paper text.",
        )
    for beta, (psnr, ssim) in zip(beta_x1e2, fig6_ref):
        _add_oe_pair(
            rows,
            figure="Fig. 6",
            panel="b",
            experiment="attenuation sweep, fixed reference pattern",
            sample="Fig. 3(a) carrier image",
            condition=f"attenuation_beta_x1e2={beta:.3g} mm^-1",
            method="fixed_reference",
            psnr=psnr,
            ssim=ssim,
            extraction="manual_digitized_from_rendered_page",
            source_path=oe9,
            approximate=True,
            psnr_uncertainty=0.4,
            ssim_uncertainty=0.002,
            note="Approximate point read from rendered Fig. 6; PSNR crosses below 30 dB near beta=1.91e-2 mm^-1.",
        )

    for beta, no_ref, ref in [
        (8.92e-3, 17.97, 40.11),
        (1.40e-2, 10.28, 37.54),
        (3.47e-2, 6.49, 29.47),
    ]:
        cond = f"attenuation_beta={beta:.4g} mm^-1"
        _add_oe_pair(
            rows,
            figure="Fig. 7",
            panel="a/c/e",
            experiment="32nd row profile, no reference pattern",
            sample="Fig. 3(a) carrier image",
            condition=cond,
            method="without_reference",
            psnr=no_ref,
            ssim=None,
            extraction="exact_caption_from_pdf",
            source_path=oe9 if oe9.exists() else text,
        )
        _add_oe_pair(
            rows,
            figure="Fig. 7",
            panel="b/d/f",
            experiment="32nd row profile, fixed reference pattern",
            sample="Fig. 3(a) carrier image",
            condition=cond,
            method="fixed_reference",
            psnr=ref,
            ssim=None,
            extraction="exact_caption_from_pdf",
            source_path=oe9 if oe9.exists() else text,
        )

    distances = [3, 5, 10, 15, 20, 25]
    fig8_no_ref = [(9.2, 0.57), (8.9, 0.53), (11.7, 0.75), (12.4, 0.78), (14.1, 0.86), (16.3, 0.91)]
    fig8_ref = [(30.7, 0.990), (34.0, 0.992), (37.7, 0.991), (37.8, 0.996), (38.5, 0.995), (39.0, 0.995)]
    for distance, (psnr, ssim) in zip(distances, fig8_no_ref):
        _add_oe_pair(
            rows,
            figure="Fig. 8",
            panel="a",
            experiment="corner-distance sweep, no reference pattern",
            sample="Fig. 3(c) carrier image",
            condition=f"distance={distance} mm; beta approximately 9.81e-3 mm^-1",
            method="without_reference",
            psnr=psnr,
            ssim=ssim,
            extraction="manual_digitized_from_rendered_page",
            source_path=oe11,
            approximate=True,
            psnr_uncertainty=0.4,
            ssim_uncertainty=0.02,
        )
    for distance, (psnr, ssim) in zip(distances, fig8_ref):
        _add_oe_pair(
            rows,
            figure="Fig. 8",
            panel="b",
            experiment="corner-distance sweep, fixed reference pattern",
            sample="Fig. 3(c) carrier image",
            condition=f"distance={distance} mm; beta approximately 9.81e-3 mm^-1",
            method="fixed_reference",
            psnr=psnr,
            ssim=ssim,
            extraction="manual_digitized_from_rendered_page",
            source_path=oe11,
            approximate=True,
            psnr_uncertainty=0.4,
            ssim_uncertainty=0.002,
        )

    for distance, no_ref, ref in [(3, 10.50, 33.16), (10, 13.31, 37.71), (20, 15.09, 40.98)]:
        _add_oe_pair(
            rows,
            figure="Fig. 9",
            panel="a/c/e",
            experiment="32nd row profile at selected corner distances, no reference pattern",
            sample="Fig. 3(c) carrier image",
            condition=f"distance={distance} mm",
            method="without_reference",
            psnr=no_ref,
            ssim=None,
            extraction="exact_caption_from_pdf",
            source_path=oe11 if oe11.exists() else text,
        )
        _add_oe_pair(
            rows,
            figure="Fig. 9",
            panel="b/d/f",
            experiment="32nd row profile at selected corner distances, fixed reference pattern",
            sample="Fig. 3(c) carrier image",
            condition=f"distance={distance} mm",
            method="fixed_reference",
            psnr=ref,
            ssim=None,
            extraction="exact_caption_from_pdf",
            source_path=oe11 if oe11.exists() else text,
        )
    return rows


def load_current_scgi_results(root: Path) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    stage0 = root / "results" / "colab_imports" / "pro2_full_exp_residual_e2_r1" / "artifacts" / "metrics.csv"
    if stage0.exists():
        row = pd.read_csv(stage0).iloc[0].to_dict()
        metric_map = {
            "GI": "dynamic_dgi_cnr",
            "SCGI": "scgi_dgi_cnr",
            "SCGI-UNN": "scgi_unn_cnr",
            "SCGI-URED": "scgi_ured_cnr",
        }
        for method, col in metric_map.items():
            rows.append(
                {
                    "result_set": "full_exp_residual_stage0_colab",
                    "scope": "single full-profile target",
                    "method": method,
                    "metric": "CNR",
                    "value": float(row[col]),
                    "source_path": _relpath(stage0),
                }
            )

    stage3_paths = [
        (
            "full_exp_residual_stage3_colab",
            root / "results" / "stage_3_exp_residual_colab_full" / "full" / "stage3_metrics.csv",
        ),
        (
            "stage3_threshold_matrix_full_r2_authoritative",
            root / "results" / "stage3_threshold_matrix_full_r2_authoritative" / "full" / "stage3_metrics.csv",
        ),
    ]
    method_names = {
        "dynamic": "GI",
        "scgi": "SCGI",
        "scgi_unn": "SCGI-UNN",
        "scgi_ured": "SCGI-URED",
        "static": "STATIC",
        "analytic": "ANALYTIC",
        "oracle": "ORACLE",
    }
    for result_label, stage3 in stage3_paths:
        if not stage3.exists():
            continue
        df = pd.read_csv(stage3)
        for method, group in df.groupby("method"):
            canonical = method_names.get(str(method), str(method).upper())
            rows.append(
                {
                    "result_set": f"{result_label}_mean",
                    "scope": "held-out target mean",
                    "method": canonical,
                    "metric": "CNR",
                    "value": float(group["cnr"].mean()),
                    "source_path": _relpath(stage3),
                }
            )
            rows.append(
                {
                    "result_set": f"{result_label}_min",
                    "scope": "held-out target minimum",
                    "method": canonical,
                    "metric": "CNR",
                    "value": float(group["cnr"].min()),
                    "source_path": _relpath(stage3),
                }
            )
    return pd.DataFrame(rows)


def build_calibration_summary(targets: pd.DataFrame, current: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    apl = targets[(targets["paper"].str.contains("Applied Physics Letters")) & (targets["metric"] == "CNR")]
    for method, group in apl.groupby("method"):
        if method == "GI":
            # The conventional-GI Fig. 9 targets are approximate zero statements; use Fig. 6 exact value.
            exact = group[group["approximate"] == False]
            target_min = float(exact["value"].min()) if not exact.empty else float(group["value"].min())
            target_mean = float(exact["value"].mean()) if not exact.empty else float(group["value"].mean())
            target_max = float(exact["value"].max()) if not exact.empty else float(group["value"].max())
        else:
            target_min = float(group["value"].min())
            target_mean = float(group["value"].mean())
            target_max = float(group["value"].max())
        matches = current[(current["method"] == method) & (current["metric"] == "CNR")]
        if matches.empty:
            rows.append(
                {
                    "comparison": f"APL CNR target for {method}",
                    "method": method,
                    "current_result_set": "missing",
                    "published_min": target_min,
                    "published_mean": target_mean,
                    "published_max": target_max,
                    "current_value": None,
                    "gap_to_min": None,
                    "ratio_to_min": None,
                    "status": "no_current_result",
                }
            )
            continue
        for _, cur in matches.iterrows():
            cur_value = float(cur["value"])
            rows.append(
                {
                    "comparison": f"APL CNR target for {method}",
                    "method": method,
                    "current_result_set": cur["result_set"],
                    "published_min": target_min,
                    "published_mean": target_mean,
                    "published_max": target_max,
                    "current_value": cur_value,
                    "gap_to_min": cur_value - target_min,
                    "ratio_to_min": cur_value / target_min if target_min else None,
                    "status": "meets_min" if cur_value >= target_min else "below_min",
                    "current_source_path": cur["source_path"],
                }
            )

    oe = targets[(targets["paper"].str.contains("Optics Express")) & (targets["metric"] == "PSNR")]
    for figure, method, label in [
        ("Fig. 3", "fixed_reference", "OE Fig. 3 fixed-reference image PSNR"),
        ("Fig. 3", "without_reference", "OE Fig. 3 no-reference image PSNR"),
        ("Fig. 6", "fixed_reference", "OE Fig. 6 fixed-reference attenuation-sweep PSNR"),
        ("Fig. 8", "fixed_reference", "OE Fig. 8 fixed-reference distance-sweep PSNR"),
    ]:
        group = oe[(oe["figure"] == figure) & (oe["method"] == method)]
        if group.empty:
            continue
        rows.append(
            {
                "comparison": label,
                "method": method,
                "current_result_set": "not_calibrated_in_current_project",
                "published_min": float(group["value"].min()),
                "published_mean": float(group["value"].mean()),
                "published_max": float(group["value"].max()),
                "current_value": None,
                "gap_to_min": None,
                "ratio_to_min": None,
                "status": "target_only",
                "current_source_path": "",
            }
        )
    return pd.DataFrame(rows)


def write_key_summary(out_dir: Path, targets: pd.DataFrame, summary: pd.DataFrame) -> dict[str, object]:
    apl = targets[(targets["paper"].str.contains("Applied Physics Letters")) & (targets["metric"] == "CNR")]
    oe_psnr = targets[(targets["paper"].str.contains("Optics Express")) & (targets["metric"] == "PSNR")]
    key = {
        "num_targets": int(len(targets)),
        "apl_cnr_targets": int(len(apl)),
        "oe_psnr_targets": int(len(oe_psnr)),
        "approximate_digitized_targets": int(targets["approximate"].sum()),
        "apl_scgi_min_cnr": float(apl[apl["method"] == "SCGI"]["value"].min()),
        "apl_unn_min_cnr": float(apl[apl["method"] == "SCGI-UNN"]["value"].min()),
        "apl_ured_min_cnr": float(apl[apl["method"] == "SCGI-URED"]["value"].min()),
        "oe_fixed_reference_fig3_min_psnr": float(
            oe_psnr[(oe_psnr["figure"] == "Fig. 3") & (oe_psnr["method"] == "fixed_reference")]["value"].min()
        ),
        "oe_fixed_reference_fig6_min_psnr_digitized": float(
            oe_psnr[(oe_psnr["figure"] == "Fig. 6") & (oe_psnr["method"] == "fixed_reference")]["value"].min()
        ),
        "apl_current_status_counts": summary[summary["comparison"].str.contains("APL")]["status"]
        .value_counts()
        .to_dict(),
    }
    (out_dir / "published_calibration_key_summary.json").write_text(json.dumps(key, indent=2), encoding="utf-8")
    return key


def _markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    display = df.copy()
    for col in display.columns:
        display[col] = display[col].map(lambda value: "" if pd.isna(value) else str(value))
    header = "| " + " | ".join(display.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(display.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in display.to_numpy(dtype=str)]
    return "\n".join([header, separator, *rows])


def write_markdown_report(out_dir: Path, summary: pd.DataFrame, key: dict[str, object]) -> None:
    lines = [
        "# Published Target Calibration",
        "",
        "This file is generated by `run_published_calibration.py`.",
        "",
        "## Key Counts",
        "",
    ]
    for k, v in key.items():
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Current APL Gap", ""])
    apl_rows = summary[summary["comparison"].str.contains("APL")].copy()
    if apl_rows.empty:
        lines.append("No current APL comparisons were available.")
    else:
        lines.append(_markdown_table(apl_rows))
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- APL CNR values are exact text values from the PDF except conventional Fig. 9 GI, which the paper states remains approximately zero.",
            "- OE Fig. 3/4/5/7/9 PSNR or SSIM values are exact caption values.",
            "- OE Fig. 6 and Fig. 8 curve points are approximate manual digitization from rendered PDF pages and include uncertainty columns.",
            "- Current OWT physical-channel comparison is target-only because this repository's M2/nonideal scans use normalized digital-twin rho/sigma axes rather than the paper's attenuation coefficient or corner-distance axes.",
        ]
    )
    (out_dir / "published_calibration_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_targets(root: Path) -> pd.DataFrame:
    targets: Iterable[PublishedTarget] = [*apl_targets(root), *oe_targets(root)]
    df = pd.DataFrame([asdict(row) for row in targets])
    return df.sort_values(["paper", "figure", "method", "metric", "sample", "panel"]).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build source-grounded published target calibration tables.")
    parser.add_argument("--output-dir", type=Path, default=project_root() / "results" / "published_calibration")
    args = parser.parse_args()

    root = project_root()
    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    targets = build_targets(root)
    current = load_current_scgi_results(root)
    summary = build_calibration_summary(targets, current)

    targets.to_csv(out_dir / "published_targets.csv", index=False)
    current.to_csv(out_dir / "current_scgi_cnr_results.csv", index=False)
    summary.to_csv(out_dir / "published_calibration_summary.csv", index=False)
    key = write_key_summary(out_dir, targets, summary)
    write_markdown_report(out_dir, summary, key)
    print(json.dumps(key, indent=2))


if __name__ == "__main__":
    main()
