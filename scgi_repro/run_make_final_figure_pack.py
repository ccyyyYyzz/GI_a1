from __future__ import annotations

import argparse
import csv
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path

import matplotlib as mpl
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pandas as pd

from src.config_utils import project_root
from src.plotting import save_metrics_table, save_metrics_table_svg


mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "font.size": 7,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.linewidth": 0.8,
        "legend.frameon": False,
    }
)


@dataclass(frozen=True)
class PanelSpec:
    label: str
    title: str
    svg_asset: str
    png_asset: str
    source: str
    caption: str


@dataclass(frozen=True)
class FigureSpec:
    figure_id: str
    title: str
    claim: str
    caption: str
    status: str
    panels: tuple[PanelSpec, ...]


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def svg_size(path: Path) -> tuple[float, float]:
    text = path.read_text(encoding="utf-8")
    viewbox = re.search(r'viewBox=["\']([^"\']+)["\']', text)
    if viewbox:
        parts = [float(part) for part in viewbox.group(1).replace(",", " ").split()]
        if len(parts) == 4 and parts[2] > 0 and parts[3] > 0:
            return parts[2], parts[3]
    width = re.search(r'width=["\']([0-9.]+)', text)
    height = re.search(r'height=["\']([0-9.]+)', text)
    if width and height:
        return float(width.group(1)), float(height.group(1))
    raise ValueError(f"Could not determine SVG size: {path}")


def svg_inner(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.find(">")
    end = text.rfind("</svg>")
    if start < 0 or end < 0:
        raise ValueError(f"Could not extract SVG body: {path}")
    return text[start + 1 : end].strip()


def esc(text: object) -> str:
    return html.escape(str(text), quote=True)


def svg_text(x: float, y: float, text: object, *, size: int = 12, weight: str = "normal", fill: str = "#111111") -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, Helvetica, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}">{esc(text)}</text>'
    )


def wrap_lines(text: str, max_chars: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join([*current, word])
        if len(candidate) <= max_chars or not current:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def render_svg_figure(spec: FigureSpec, out_path: Path, root: Path) -> None:
    width = 1800
    margin = 64
    gutter = 36
    title_h = 128
    caption_h = 110
    cols = 2 if len(spec.panels) > 1 else 1
    rows = (len(spec.panels) + cols - 1) // cols
    cell_w = (width - 2 * margin - gutter * (cols - 1)) / cols
    cell_h = 430
    height = int(title_h + rows * cell_h + (rows - 1) * gutter + caption_h + margin)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff" />',
        svg_text(margin, 42, spec.title, size=26, weight="bold"),
        svg_text(margin, 74, spec.claim, size=15, fill="#333333"),
        svg_text(margin, 102, f"Status: {spec.status}", size=13, fill="#666666"),
    ]
    for idx, panel in enumerate(spec.panels):
        row = idx // cols
        col = idx % cols
        span = 1
        if len(spec.panels) % 2 == 1 and idx == len(spec.panels) - 1 and cols == 2:
            span = 2
            col = 0
        x0 = margin + col * (cell_w + gutter)
        y0 = title_h + row * (cell_h + gutter)
        w = cell_w * span + gutter * (span - 1)
        h = cell_h
        parts.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#ffffff" stroke="#d0d0d0" />')
        parts.append(svg_text(x0 + 14, y0 + 30, panel.label, size=22, weight="bold"))
        parts.append(svg_text(x0 + 58, y0 + 30, panel.title, size=14, fill="#333333"))
        svg_path = root / panel.svg_asset
        src_w, src_h = svg_size(svg_path)
        inner_w = w - 32
        inner_h = h - 70
        scale = min(inner_w / src_w, inner_h / src_h)
        tx = x0 + 16 + (inner_w - src_w * scale) / 2
        ty = y0 + 58 + (inner_h - src_h * scale) / 2
        parts.append(f'<g transform="translate({tx:.2f},{ty:.2f}) scale({scale:.5f})">')
        parts.append(svg_inner(svg_path))
        parts.append("</g>")

    caption_y = height - caption_h + 8
    parts.append(f'<line x1="{margin}" y1="{caption_y - 18}" x2="{width - margin}" y2="{caption_y - 18}" stroke="#d9d9d9" />')
    for line_idx, line in enumerate(wrap_lines(spec.caption, 165)):
        parts.append(svg_text(margin, caption_y + line_idx * 19, line, size=13, fill="#333333"))
    parts.append("</svg>\n")
    out_path.write_text("\n".join(parts), encoding="utf-8")


def render_raster_figure(spec: FigureSpec, out_base: Path, root: Path, dpi: int) -> None:
    cols = 2 if len(spec.panels) > 1 else 1
    rows = (len(spec.panels) + cols - 1) // cols
    fig_w = 7.2
    cell_h = 2.05
    fig_h = 1.0 + rows * cell_h + 0.45
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi)
    fig.patch.set_facecolor("white")
    fig.text(0.04, 0.965, spec.title, ha="left", va="top", fontsize=11, fontweight="bold")
    fig.text(0.04, 0.925, spec.claim, ha="left", va="top", fontsize=7, color="#333333")
    fig.text(0.04, 0.895, f"Status: {spec.status}", ha="left", va="top", fontsize=6.5, color="#666666")
    top = 0.84
    bottom = 0.13
    left = 0.04
    right = 0.98
    h_gap = 0.035
    v_gap = 0.055
    panel_w = (right - left - h_gap * (cols - 1)) / cols
    panel_h = (top - bottom - v_gap * (rows - 1)) / rows
    for idx, panel in enumerate(spec.panels):
        row = idx // cols
        col = idx % cols
        span = 1
        if len(spec.panels) % 2 == 1 and idx == len(spec.panels) - 1 and cols == 2:
            span = 2
            col = 0
        x = left + col * (panel_w + h_gap)
        y = top - (row + 1) * panel_h - row * v_gap
        w = panel_w * span + h_gap * (span - 1)
        ax = fig.add_axes([x, y, w, panel_h])
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color("#d0d0d0")
            spine.set_linewidth(0.6)
        ax.set_facecolor("white")
        img = mpimg.imread(root / panel.png_asset)
        ax.imshow(img)
        ax.set_title(f"{panel.label}  {panel.title}", loc="left", fontsize=7, fontweight="bold", pad=3)
    fig.text(0.04, 0.035, spec.caption, ha="left", va="bottom", fontsize=6.3, color="#333333", wrap=True)
    fig.savefig(out_base.with_suffix(".png"), dpi=dpi, bbox_inches="tight")
    fig.savefig(out_base.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(out_base.with_suffix(".tiff"), dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def make_m3_panel_assets(root: Path, out_dir: Path) -> tuple[str, str, str]:
    source = root / "results" / "srht_m3_audit_highrho_r2" / "m3_srht_delta_summary.csv"
    df = pd.read_csv(source)
    table = df[(df["rho"] >= 1.0) & (df["correction"].isin(["none", "agc", "scgi_proxy", "pairwise"]))][
        [
            "rho",
            "sigma_a",
            "correction",
            "srht_minus_ordered_db",
            "best_alternative_minus_ordered_db",
            "best_alternative",
        ]
    ].copy()
    table["srht_minus_ordered_db"] = table["srht_minus_ordered_db"].astype(float).round(3)
    table["best_alternative_minus_ordered_db"] = table["best_alternative_minus_ordered_db"].astype(float).round(3)
    panel_dir = out_dir / "panel_assets"
    panel_dir.mkdir(parents=True, exist_ok=True)
    png = panel_dir / "m3_fallback_delta_table.png"
    svg = panel_dir / "m3_fallback_delta_table.svg"
    save_metrics_table(png, table, title="M3 fast-drift fallback deltas", max_rows=8)
    save_metrics_table_svg(svg, table, title="M3 fast-drift fallback deltas", max_rows=8)
    return rel(svg, root), rel(png, root), rel(source, root)


def build_specs(root: Path, out_dir: Path) -> tuple[FigureSpec, ...]:
    m3_svg, m3_png, m3_source = make_m3_panel_assets(root, out_dir)
    return (
        FigureSpec(
            figure_id="figure3_agc_diagnostic",
            title="Figure 3. AGC remains diagnostic",
            claim="Best-window AGC follows a partial bias-variance pattern, but boundary pressure prevents theorem-level closure.",
            caption=(
                "AGC window-law evidence across the original, targeted, and boundary-aware fits. "
                "The figure is intentionally labelled diagnostic because many best windows remain at the grid boundary."
            ),
            status="diagnostic; not a final quantitative theorem",
            panels=(
                PanelSpec("A", "Original window-law fit", "results/paper_figures_r1/m4_agc_window_fit_table.svg", "results/paper_figures_r1/m4_agc_window_fit_table.png", "results/theory_m4_paper_r2_highrho/m4_agc_window_law_fit.csv", "Original AGC window-law fit."),
                PanelSpec("B", "Targeted saturation", "results/paper_figures_r1/m4_agc_targeted_saturation_table.svg", "results/paper_figures_r1/m4_agc_targeted_saturation_table.png", "results/theory_m4_agc_targeted_r1/m4_agc_targeted_saturation.csv", "Targeted grid saturation table."),
                PanelSpec("C", "Targeted fit", "results/paper_figures_r1/m4_agc_targeted_fit_table.svg", "results/paper_figures_r1/m4_agc_targeted_fit_table.png", "results/theory_m4_agc_targeted_r1/m4_agc_targeted_fit.csv", "Targeted AGC fit table."),
                PanelSpec("D", "Boundary-aware fit", "results/paper_figures_r1/m4_agc_boundary_aware_fit_table.svg", "results/paper_figures_r1/m4_agc_boundary_aware_fit_table.png", "results/theory_m4_agc_boundary_aware_r1/m4_agc_boundary_aware_fit.csv", "Censored/boundary-aware fit table."),
            ),
        ),
        FigureSpec(
            figure_id="figure4_error_scaling",
            title="Figure 4. Residual gain errors and averaging laws",
            claim="Residual gain error scales quadratically, while random-frame reconstructions average residual error down with frame count.",
            caption=(
                "The main fitted laws supporting H2/H4: residual gain errors have near-quadratic scaling; "
                "random-frame correlation reconstructions improve with frame count; deterministic bases concentrate coefficient energy."
            ),
            status="strong quantitative support",
            panels=(
                PanelSpec("A", "Residual gain scaling", "results/paper_figures_r1/m4_error_scaling_fit_table.svg", "results/paper_figures_r1/m4_error_scaling_fit_table.png", "results/theory_m4_paper_r2_highrho/m4_error_scaling_fit.csv", "Residual gain scaling fit."),
                PanelSpec("B", "Random-frame curve", "results/paper_figures_r1/m4_random_frame_scaling_sigma0p05.svg", "results/paper_figures_r1/m4_random_frame_scaling_sigma0p05.png", "results/theory_m4_paper_r2_highrho/m4_random_frame_scaling_summary.csv", "Random-frame scaling at sigma_delta=0.05."),
                PanelSpec("C", "Frame-count fit", "results/paper_figures_r1/m4_random_frame_scaling_fit_table.svg", "results/paper_figures_r1/m4_random_frame_scaling_fit_table.png", "results/theory_m4_paper_r2_highrho/m4_random_frame_scaling_fit.csv", "Frame-count fit table."),
                PanelSpec("D", "Energy concentration", "results/paper_figures_r1/m4_top5_energy_concentration.svg", "results/paper_figures_r1/m4_top5_energy_concentration.png", "results/theory_m4_paper_r2_highrho/m4_energy_concentration_summary.csv", "Top-5% coefficient energy."),
            ),
        ),
        FigureSpec(
            figure_id="figure5_m2_phase_boundary",
            title="Figure 5. M2 phase map and flip boundaries",
            claim="Across the prompt rho/sigma grid, SRHT/Hadamard pairwise correction dominates strict equal-frame blind comparisons.",
            caption=(
                "Prompt-range M2 phase maps and observed flip-boundary fits. Reference-frame methods are shown separately because they spend extra physical frames."
            ),
            status="compact-protocol complete; final artwork draft",
            panels=(
                PanelSpec("A", "Strict equal-frame winners", "results/paper_figures_r1/m2_equal_frame_winner_map.svg", "results/paper_figures_r1/m2_equal_frame_winner_map.png", "results/m2_boundary_audit_highrho/m2_winner_cells.csv", "Strict equal-frame winner map."),
                PanelSpec("B", "All non-oracle winners", "results/paper_figures_r1/m2_all_non_oracle_winner_map.svg", "results/paper_figures_r1/m2_all_non_oracle_winner_map.png", "results/m2_boundary_audit_highrho/m2_winner_cells.csv", "All non-oracle winner map."),
                PanelSpec("C", "Boundary fits", "results/paper_figures_r1/m2_observed_boundary_fit_table.svg", "results/paper_figures_r1/m2_observed_boundary_fit_table.png", "results/m2_boundary_audit_highrho/m2_boundary_fit.csv", "Observed boundary fits."),
            ),
        ),
        FigureSpec(
            figure_id="figure8_srht_energy_ablation",
            title="Figure 8. Signed time interleaving is best, but not by 3 dB",
            claim="Diagonal randomization plus time interleaving gives the best fast-drift ablation, but current tests refute the strong >=3 dB gate.",
            caption=(
                "Energy concentration and fast-drift fallback-ablation evidence. Signed time interleaving is the best fast non-oracle alternative, "
                "but its advantage over ordered Hadamard remains only about 0.03-0.14 dB."
            ),
            status="strong-claim refuted under current protocol",
            panels=(
                PanelSpec("A", "Energy spreading", "results/paper_figures_r1/m4_top5_energy_concentration.svg", "results/paper_figures_r1/m4_top5_energy_concentration.png", "results/theory_m4_paper_r2_highrho/m4_energy_concentration_summary.csv", "Energy concentration by basis."),
                PanelSpec("B", "Fast-drift fallback", m3_svg, m3_png, m3_source, "M3 fast-drift fallback deltas."),
            ),
        ),
    )


def write_manifest(specs: tuple[FigureSpec, ...], out_dir: Path, root: Path, dpi: int) -> None:
    rows: list[dict[str, object]] = []
    for spec in specs:
        for panel in spec.panels:
            rows.append(
                {
                    "figure_id": spec.figure_id,
                    "figure_title": spec.title,
                    "claim": spec.claim,
                    "status": spec.status,
                    "panel": panel.label,
                    "panel_title": panel.title,
                    "panel_svg_asset": panel.svg_asset,
                    "panel_png_asset": panel.png_asset,
                    "source_data": panel.source,
                    "panel_caption": panel.caption,
                    "output_svg": f"results/paper_figures_r2_final/{spec.figure_id}.svg",
                    "output_png": f"results/paper_figures_r2_final/{spec.figure_id}.png",
                    "output_pdf": f"results/paper_figures_r2_final/{spec.figure_id}.pdf",
                    "output_tiff": f"results/paper_figures_r2_final/{spec.figure_id}.tiff",
                    "figure_caption": spec.caption,
                    "dpi": dpi,
                }
            )
    pd.DataFrame(rows).to_csv(out_dir / "figure_assembly_manifest.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    qa = {
        "figures": len(specs),
        "panels": len(rows),
        "outputs_per_figure": ["svg", "png", "pdf", "tiff"],
        "svg_mode": "source SVG panels embedded as editable vector groups",
        "raster_mode": "matplotlib preview/export from audited PNG panels",
        "all_paths_relative_to_repo": True,
    }
    (out_dir / "figure_pack_qa.json").write_text(json.dumps(qa, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create final paper-figure pack from audited M2/M3/M4 assets.")
    parser.add_argument("--output-dir", type=Path, default=Path("results/paper_figures_r2_final"))
    parser.add_argument("--dpi", type=int, default=600)
    args = parser.parse_args()

    root = project_root()
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    specs = build_specs(root, out_dir)
    for spec in specs:
        for panel in spec.panels:
            for asset in [panel.svg_asset, panel.png_asset, panel.source]:
                if not (root / asset).exists():
                    raise FileNotFoundError(f"Missing required figure asset or source: {asset}")
        out_base = out_dir / spec.figure_id
        render_svg_figure(spec, out_base.with_suffix(".svg"), root)
        render_raster_figure(spec, out_base, root, dpi=args.dpi)
    write_manifest(specs, out_dir, root, args.dpi)
    print(f"wrote final figure pack to {out_dir}")


if __name__ == "__main__":
    main()
