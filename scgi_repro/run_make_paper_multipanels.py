from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageOps

from src.config_utils import project_root


@dataclass(frozen=True)
class PanelSpec:
    label: str
    title: str
    asset: str


@dataclass(frozen=True)
class FigureSpec:
    figure_id: str
    title: str
    caption: str
    panels: tuple[PanelSpec, ...]


FIGURES: tuple[FigureSpec, ...] = (
    FigureSpec(
        figure_id="figure3_agc_diagnostics",
        title="Figure 3. AGC window diagnostics",
        caption=(
            "Current AGC evidence supports a bias-variance diagnostic, but "
            "targeted and boundary-aware fits remain boundary-sensitive rather "
            "than theorem-level closure."
        ),
        panels=(
            PanelSpec("A", "Original best-window fit", "m4_agc_window_fit_table.png"),
            PanelSpec("B", "Targeted grid saturation", "m4_agc_targeted_saturation_table.png"),
            PanelSpec("C", "Targeted fit", "m4_agc_targeted_fit_table.png"),
            PanelSpec("D", "Boundary-aware fit", "m4_agc_boundary_aware_fit_table.png"),
        ),
    ),
    FigureSpec(
        figure_id="figure4_error_scaling",
        title="Figure 4. Residual error scaling and coefficient spreading",
        caption=(
            "Residual gain errors scale quadratically, random-frame averaging "
            "reduces reconstruction error with frame count, and SRHT spreads "
            "object energy similarly to random bases."
        ),
        panels=(
            PanelSpec("A", "Residual gain error scaling", "m4_error_scaling_fit_table.png"),
            PanelSpec("B", "Random-frame scaling", "m4_random_frame_scaling_sigma0p05.png"),
            PanelSpec("C", "Frame-count fit", "m4_random_frame_scaling_fit_table.png"),
            PanelSpec("D", "Top-5% coefficient energy", "m4_top5_energy_concentration.png"),
        ),
    ),
    FigureSpec(
        figure_id="figure7_phase_diagram",
        title="Figure 7. Prompt-range M2 phase diagrams",
        caption=(
            "Strict equal-frame and all-non-oracle maps cover rho=0.001..10 "
            "and sigma_a=0.05..0.50; observed boundary fits summarize the "
            "resolved flip curves."
        ),
        panels=(
            PanelSpec("A", "Strict equal-frame winners", "m2_equal_frame_winner_map.png"),
            PanelSpec("B", "All-non-oracle winners", "m2_all_non_oracle_winner_map.png"),
            PanelSpec("C", "Observed boundary fits", "m2_observed_boundary_fit_table.png"),
        ),
    ),
)


def _font(size: int, *, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def _text_height(font: ImageFont.ImageFont, text: str) -> int:
    bbox = font.getbbox(text)
    return int(bbox[3] - bbox[1])


def _load_asset(path: Path) -> Image.Image:
    if not path.exists():
        raise FileNotFoundError(f"Missing figure asset: {path}")
    image = Image.open(path).convert("RGBA")
    background = Image.new("RGBA", image.size, (255, 255, 255, 255))
    background.alpha_composite(image)
    return background.convert("RGB")


def _fit_image(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    resampling = getattr(Image, "Resampling", Image).LANCZOS
    return ImageOps.contain(image, size, method=resampling)


def _draw_panel(
    draw: ImageDraw.ImageDraw,
    canvas: Image.Image,
    image: Image.Image,
    box: tuple[int, int, int, int],
    panel: PanelSpec,
    *,
    label_font: ImageFont.ImageFont,
    title_font: ImageFont.ImageFont,
) -> None:
    x0, y0, x1, y1 = box
    draw.rectangle(box, outline=(210, 210, 210), width=2)
    draw.text((x0 + 14, y0 + 10), panel.label, fill=(0, 0, 0), font=label_font)
    draw.text((x0 + 58, y0 + 16), panel.title, fill=(30, 30, 30), font=title_font)

    inner_margin = 18
    title_band = 64
    max_w = x1 - x0 - 2 * inner_margin
    max_h = y1 - y0 - title_band - inner_margin
    fitted = _fit_image(image, (max_w, max_h))
    px = x0 + (x1 - x0 - fitted.width) // 2
    py = y0 + title_band + (max_h - fitted.height) // 2
    canvas.paste(fitted, (px, py))


def _make_canvas(spec: FigureSpec, asset_dir: Path, *, width: int, dpi: int) -> Image.Image:
    title_font = _font(36, bold=True)
    subtitle_font = _font(24)
    panel_title_font = _font(24)
    panel_label_font = _font(36, bold=True)
    caption_font = _font(20)

    n = len(spec.panels)
    cols = 2
    rows = (n + cols - 1) // cols
    margin = 70
    gutter = 34
    title_h = 112
    caption_h = 96
    cell_w = (width - 2 * margin - gutter) // cols
    cell_h = 620 if rows == 2 else 700
    height = title_h + rows * cell_h + (rows - 1) * gutter + caption_h + margin

    canvas = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 34), spec.title, fill=(0, 0, 0), font=title_font)
    draw.text((margin, 80), "Draft multipanel assembly from audited CSV/PNG assets.", fill=(80, 80, 80), font=subtitle_font)

    for idx, panel in enumerate(spec.panels):
        row = idx // cols
        col = idx % cols
        x0 = margin + col * (cell_w + gutter)
        y0 = title_h + row * (cell_h + gutter)
        span_cols = 1
        if n % 2 == 1 and idx == n - 1:
            span_cols = 2
            x0 = margin
        x1 = x0 + cell_w * span_cols + gutter * (span_cols - 1)
        y1 = y0 + cell_h
        image = _load_asset(asset_dir / panel.asset)
        _draw_panel(
            draw,
            canvas,
            image,
            (x0, y0, x1, y1),
            panel,
            label_font=panel_label_font,
            title_font=panel_title_font,
        )

    caption_y = height - caption_h - 20
    draw.line((margin, caption_y - 18, width - margin, caption_y - 18), fill=(220, 220, 220), width=2)
    draw.text((margin, caption_y), spec.caption, fill=(30, 30, 30), font=caption_font)
    draw.text((margin, caption_y + _text_height(caption_font, spec.caption) + 14), f"Resolution: {dpi} dpi; source assets listed in paper_multipanel_manifest.csv.", fill=(90, 90, 90), font=caption_font)
    return canvas


def render_multipanels(asset_dir: Path, out_dir: Path, *, width: int, dpi: int) -> pd.DataFrame:
    manifest_path = asset_dir / "paper_figure_manifest.csv"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing source manifest: {manifest_path}")
    source_manifest = pd.read_csv(manifest_path)
    source_by_asset = {str(row.figure): row for row in source_manifest.itertuples()}

    rows: list[dict[str, str]] = []
    out_dir.mkdir(parents=True, exist_ok=True)
    for spec in FIGURES:
        canvas = _make_canvas(spec, asset_dir, width=width, dpi=dpi)
        png = out_dir / f"{spec.figure_id}.png"
        pdf = out_dir / f"{spec.figure_id}.pdf"
        svg = out_dir / f"{spec.figure_id}.svg"
        canvas.save(png, dpi=(dpi, dpi))
        canvas.save(pdf, "PDF", resolution=dpi)
        encoded = base64.b64encode(png.read_bytes()).decode("ascii")
        svg.write_text(
            "\n".join(
                [
                    f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas.width}" height="{canvas.height}" viewBox="0 0 {canvas.width} {canvas.height}">',
                    f'<image href="data:image/png;base64,{encoded}" width="{canvas.width}" height="{canvas.height}" />',
                    "</svg>",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        for panel in spec.panels:
            source = source_by_asset.get(panel.asset)
            rows.append(
                {
                    "figure_id": spec.figure_id,
                    "figure_title": spec.title,
                    "panel": panel.label,
                    "panel_title": panel.title,
                    "asset_png": str(asset_dir / panel.asset),
                    "asset_source": "" if source is None else str(source.source),
                    "asset_caption": "" if source is None else str(source.caption),
                    "output_png": str(png),
                    "output_pdf": str(pdf),
                    "output_svg": str(svg),
                    "figure_caption": spec.caption,
                }
            )
    manifest = pd.DataFrame(rows)
    manifest.to_csv(out_dir / "paper_multipanel_manifest.csv", index=False)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble audited paper-facing assets into draft multipanel figures.")
    parser.add_argument("--asset-dir", type=Path, default=Path("results/paper_figures_r1"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/paper_figures_r1/multipanels"))
    parser.add_argument("--width", type=int, default=2400)
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()

    root = project_root()
    asset_dir = args.asset_dir if args.asset_dir.is_absolute() else root / args.asset_dir
    out_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    manifest = render_multipanels(asset_dir, out_dir, width=args.width, dpi=args.dpi)
    print(f"wrote {len(manifest)} panel rows to {out_dir / 'paper_multipanel_manifest.csv'}")


if __name__ == "__main__":
    main()
