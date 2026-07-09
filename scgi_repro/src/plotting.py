"""PIL-based plotting helpers for SCGI smoke runs.

The project intentionally avoids matplotlib in the lightweight local runtime.
These helpers cover the simple artifacts needed by the stage scripts: image
grids, compact line plots, and metric tables.
"""

from __future__ import annotations

from html import escape as html_escape
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


Color = tuple[int, int, int]

DEFAULT_PALETTE: tuple[Color, ...] = (
    (34, 94, 168),
    (214, 89, 40),
    (46, 139, 87),
    (131, 93, 165),
    (190, 134, 32),
    (47, 121, 127),
)


def ensure_parent(path: str | Path) -> Path:
    """Create the parent directory for an output path and return a Path."""

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    return out


def to_numpy_2d(image: object) -> np.ndarray:
    """Convert an image-like object to a finite 2-D float64 array."""

    arr = np.asarray(image, dtype=np.float64)
    if arr.ndim == 3 and arr.shape[-1] in (1, 3, 4):
        arr = arr[..., 0]
    if arr.ndim != 2:
        raise ValueError(f"Expected a 2-D image, got shape {arr.shape!r}.")
    return np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)


def normalize_to_uint8(
    image: object,
    *,
    vmin: float | None = None,
    vmax: float | None = None,
    percentile: tuple[float, float] | None = None,
    invert: bool = False,
) -> np.ndarray:
    """Map an image to uint8 using stable dynamic scaling.

    Constant and near-constant images are mapped to zeros instead of producing
    NaNs. Percentile limits are useful for noisy reconstructions with outliers.
    """

    arr = to_numpy_2d(image)
    if percentile is not None:
        lo, hi = percentile
        if not 0 <= lo < hi <= 100:
            raise ValueError("percentile must satisfy 0 <= low < high <= 100")
        finite = arr[np.isfinite(arr)]
        if finite.size:
            pmin, pmax = np.percentile(finite, [lo, hi])
            vmin = float(pmin) if vmin is None else vmin
            vmax = float(pmax) if vmax is None else vmax

    low = float(np.min(arr) if vmin is None else vmin)
    high = float(np.max(arr) if vmax is None else vmax)
    scale = high - low
    if not np.isfinite(scale) or scale <= np.finfo(np.float64).eps:
        out = np.zeros(arr.shape, dtype=np.uint8)
    else:
        out = np.clip((arr - low) / scale, 0.0, 1.0)
        if invert:
            out = 1.0 - out
        out = np.rint(out * 255.0).astype(np.uint8)
    return out


def array_to_image(
    image: object,
    *,
    scale_each: bool = True,
    vmin: float | None = None,
    vmax: float | None = None,
    percentile: tuple[float, float] | None = None,
    invert: bool = False,
) -> Image.Image:
    """Convert an array-like image to an 8-bit grayscale PIL image."""

    arr = to_numpy_2d(image)
    if scale_each:
        pixels = normalize_to_uint8(
            arr, vmin=vmin, vmax=vmax, percentile=percentile, invert=invert
        )
    else:
        pixels = normalize_to_uint8(arr, vmin=vmin, vmax=vmax, invert=invert)
    return Image.fromarray(pixels, mode="L")


def make_image_grid(
    images: Sequence[object],
    *,
    labels: Sequence[str] | None = None,
    columns: int | None = None,
    cell_size: int | tuple[int, int] | None = None,
    pad: int = 6,
    background: int = 255,
    label_height: int = 18,
    scale_each: bool = True,
    percentile: tuple[float, float] | None = None,
) -> Image.Image:
    """Create a labeled grayscale image grid."""

    if not images:
        raise ValueError("images must contain at least one image")
    if labels is not None and len(labels) != len(images):
        raise ValueError("labels must have the same length as images")

    pil_images = [
        array_to_image(img, scale_each=scale_each, percentile=percentile).convert("L")
        for img in images
    ]
    if cell_size is None:
        width = max(img.width for img in pil_images)
        height = max(img.height for img in pil_images)
    elif isinstance(cell_size, int):
        width = height = int(cell_size)
    else:
        width, height = int(cell_size[0]), int(cell_size[1])

    cols = columns or int(np.ceil(np.sqrt(len(pil_images))))
    cols = max(1, min(cols, len(pil_images)))
    rows = int(np.ceil(len(pil_images) / cols))
    top = label_height if labels is not None else 0
    canvas = Image.new(
        "L",
        (cols * width + (cols + 1) * pad, rows * (height + top) + (rows + 1) * pad),
        color=int(background),
    )
    draw = ImageDraw.Draw(canvas)
    font = _default_font()

    for idx, img in enumerate(pil_images):
        row, col = divmod(idx, cols)
        x = pad + col * (width + pad)
        y = pad + row * (height + top + pad)
        if labels is not None:
            draw.text((x, y), _short_label(labels[idx], width, font), fill=0, font=font)
            y += label_height
        fitted = _fit_image(img, (width, height))
        ox = x + (width - fitted.width) // 2
        oy = y + (height - fitted.height) // 2
        canvas.paste(fitted, (ox, oy))

    return canvas


def save_image_grid(path: str | Path, images: Sequence[object], **kwargs: object) -> Path:
    """Save an image grid and return the output path."""

    out = ensure_parent(path)
    make_image_grid(images, **kwargs).save(out)
    return out


def make_series_plot(
    series: pd.DataFrame | pd.Series | Mapping[str, Sequence[float]] | Sequence[float],
    *,
    width: int = 720,
    height: int = 360,
    title: str | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
    y_range: tuple[float, float] | None = None,
    colors: Sequence[Color] = DEFAULT_PALETTE,
    background: Color = (255, 255, 255),
) -> Image.Image:
    """Render one or more numeric series as a compact RGB line plot."""

    frame = _coerce_series_frame(series)
    if frame.empty:
        raise ValueError("series must contain at least one numeric value")

    margin_left, margin_right = 58, 18
    margin_top = 34 if title else 18
    margin_bottom = 42
    plot_w = max(1, width - margin_left - margin_right)
    plot_h = max(1, height - margin_top - margin_bottom)
    image = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(image)
    font = _default_font()

    values = frame.to_numpy(dtype=np.float64)
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        y_min, y_max = 0.0, 1.0
    elif y_range is None:
        y_min, y_max = float(finite.min()), float(finite.max())
        if y_max - y_min <= np.finfo(np.float64).eps:
            pad = max(1.0, abs(y_min) * 0.05)
            y_min -= pad
            y_max += pad
    else:
        y_min, y_max = float(y_range[0]), float(y_range[1])
        if y_max <= y_min:
            raise ValueError("y_range must satisfy min < max")

    x0, y0 = margin_left, margin_top + plot_h
    x1, y1 = margin_left + plot_w, margin_top
    _draw_axes(draw, (x0, y0, x1, y1), y_min, y_max, font)

    x_count = max(1, len(frame.index) - 1)
    for col_idx, column in enumerate(frame.columns):
        color = colors[col_idx % len(colors)]
        points: list[tuple[int, int]] = []
        for i, value in enumerate(frame[column].to_numpy(dtype=np.float64)):
            if not np.isfinite(value):
                continue
            x = x0 + int(round(plot_w * (i / x_count if x_count else 0.0)))
            y_frac = (value - y_min) / (y_max - y_min)
            y = y0 - int(round(plot_h * np.clip(y_frac, 0.0, 1.0)))
            points.append((x, y))
        if len(points) == 1:
            x, y = points[0]
            draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=color)
        elif len(points) > 1:
            draw.line(points, fill=color, width=2)

    if title:
        draw.text((margin_left, 8), title, fill=(0, 0, 0), font=font)
    if x_label:
        draw.text((margin_left, height - 20), x_label, fill=(0, 0, 0), font=font)
    if y_label:
        draw.text((8, margin_top), y_label, fill=(0, 0, 0), font=font)
    _draw_legend(draw, frame.columns, colors, (margin_left + 8, margin_top + 8), font)
    return image


def save_series_plot(path: str | Path, series: object, **kwargs: object) -> Path:
    """Save a line plot and return the output path."""

    out = ensure_parent(path)
    make_series_plot(series, **kwargs).save(out)
    return out


def save_series_plot_svg(
    path: str | Path,
    series: object,
    *,
    width: int = 720,
    height: int = 360,
    title: str | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
    y_range: tuple[float, float] | None = None,
    colors: Sequence[Color] = DEFAULT_PALETTE,
    background: Color = (255, 255, 255),
) -> Path:
    """Save one or more numeric series as a lightweight SVG line plot."""

    frame = _coerce_series_frame(series)
    if frame.empty:
        raise ValueError("series must contain at least one numeric value")

    margin_left, margin_right = 58, 18
    margin_top = 34 if title else 18
    margin_bottom = 42
    plot_w = max(1, width - margin_left - margin_right)
    plot_h = max(1, height - margin_top - margin_bottom)
    values = frame.to_numpy(dtype=np.float64)
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        y_min, y_max = 0.0, 1.0
    elif y_range is None:
        y_min, y_max = float(finite.min()), float(finite.max())
        if y_max - y_min <= np.finfo(np.float64).eps:
            pad = max(1.0, abs(y_min) * 0.05)
            y_min -= pad
            y_max += pad
    else:
        y_min, y_max = float(y_range[0]), float(y_range[1])
        if y_max <= y_min:
            raise ValueError("y_range must satisfy min < max")

    x0, y0 = margin_left, margin_top + plot_h
    x1, y1 = margin_left + plot_w, margin_top
    parts = [_svg_open(width, height, background)]
    parts.append(_svg_line(x0, y0, x1, y0, (80, 80, 80), 1))
    parts.append(_svg_line(x0, y0, x0, y1, (80, 80, 80), 1))
    for i in range(5):
        frac = i / 4
        y = y0 - int(round((y0 - y1) * frac))
        value = y_min + (y_max - y_min) * frac
        parts.append(_svg_line(x0 - 4, y, x1, y, (225, 225, 225), 1))
        parts.append(_svg_text(4, y + 4, f"{value:.3g}", size=12, fill=(55, 55, 55)))

    x_count = max(1, len(frame.index) - 1)
    for col_idx, column in enumerate(frame.columns):
        color = colors[col_idx % len(colors)]
        points: list[tuple[int, int]] = []
        for i, value in enumerate(frame[column].to_numpy(dtype=np.float64)):
            if not np.isfinite(value):
                continue
            x = x0 + int(round(plot_w * (i / x_count if x_count else 0.0)))
            y_frac = (value - y_min) / (y_max - y_min)
            y = y0 - int(round(plot_h * np.clip(y_frac, 0.0, 1.0)))
            points.append((x, y))
        if len(points) == 1:
            x, y = points[0]
            parts.append(
                f'<circle cx="{x}" cy="{y}" r="2.5" fill="{color_to_hex(color)}" />'
            )
        elif len(points) > 1:
            point_text = " ".join(f"{x},{y}" for x, y in points)
            parts.append(
                f'<polyline points="{point_text}" fill="none" '
                f'stroke="{color_to_hex(color)}" stroke-width="2" />'
            )

    if title:
        parts.append(_svg_text(margin_left, 18, title, size=13, weight="bold"))
    if x_label:
        parts.append(_svg_text(margin_left, height - 10, x_label, size=12))
    if y_label:
        parts.append(_svg_text(8, margin_top + 8, y_label, size=12))
    legend_x, legend_y = margin_left + 8, margin_top + 8
    for idx, label in enumerate(frame.columns):
        y = legend_y + 16 * idx
        color = colors[idx % len(colors)]
        parts.append(_svg_line(legend_x, y, legend_x + 18, y, color, 2))
        parts.append(_svg_text(legend_x + 24, y + 4, str(label), size=12))
    parts.append("</svg>\n")
    out = ensure_parent(path)
    out.write_text("\n".join(parts), encoding="utf-8")
    return out


def make_metrics_table(
    metrics: pd.DataFrame | Mapping[str, object] | Sequence[Mapping[str, object]],
    *,
    title: str | None = None,
    max_rows: int = 20,
    background: Color = (255, 255, 255),
) -> Image.Image:
    """Render a small metrics table as an RGB image."""

    frame = _coerce_metrics_frame(metrics).head(max_rows)
    font = _default_font()
    headers = [str(c) for c in frame.columns]
    rows = [[_format_cell(v) for v in row] for row in frame.to_numpy(dtype=object)]

    padding_x, padding_y = 8, 5
    title_h = 24 if title else 0
    col_widths = []
    for idx, header in enumerate(headers):
        cells = [header] + [row[idx] for row in rows]
        col_widths.append(max(_text_width(font, cell) for cell in cells) + 2 * padding_x)
    row_h = max(18, _text_height(font, "Ag") + 2 * padding_y)
    width = max(220, sum(col_widths) + 2)
    height = title_h + row_h * (len(rows) + 1) + 2
    image = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(image)

    y = 0
    if title:
        draw.text((padding_x, 5), title, fill=(0, 0, 0), font=font)
        y += title_h

    x = 0
    for col_idx, header in enumerate(headers):
        w = col_widths[col_idx]
        draw.rectangle((x, y, x + w, y + row_h), fill=(235, 238, 242), outline=(180, 180, 180))
        draw.text((x + padding_x, y + padding_y), header, fill=(0, 0, 0), font=font)
        x += w
    y += row_h

    for row_idx, row in enumerate(rows):
        x = 0
        fill = (255, 255, 255) if row_idx % 2 == 0 else (247, 248, 250)
        for col_idx, cell in enumerate(row):
            w = col_widths[col_idx]
            draw.rectangle((x, y, x + w, y + row_h), fill=fill, outline=(215, 215, 215))
            draw.text((x + padding_x, y + padding_y), cell, fill=(0, 0, 0), font=font)
            x += w
        y += row_h
    return image


def save_metrics_table(path: str | Path, metrics: object, **kwargs: object) -> Path:
    """Save a metrics table image and return the output path."""

    out = ensure_parent(path)
    make_metrics_table(metrics, **kwargs).save(out)
    return out


def save_metrics_table_svg(
    path: str | Path,
    metrics: object,
    *,
    title: str | None = None,
    max_rows: int = 20,
    background: Color = (255, 255, 255),
) -> Path:
    """Save a small metrics table as SVG for paper-facing vector assets."""

    frame = _coerce_metrics_frame(metrics).head(max_rows)
    font = _default_font()
    headers = [str(c) for c in frame.columns]
    rows = [[_format_cell(v) for v in row] for row in frame.to_numpy(dtype=object)]

    padding_x, padding_y = 8, 5
    title_h = 24 if title else 0
    col_widths = []
    for idx, header in enumerate(headers):
        cells = [header] + [row[idx] for row in rows]
        col_widths.append(max(_text_width(font, cell) for cell in cells) + 2 * padding_x)
    row_h = max(18, _text_height(font, "Ag") + 2 * padding_y)
    width = max(220, sum(col_widths) + 2)
    height = title_h + row_h * (len(rows) + 1) + 2
    parts = [_svg_open(width, height, background)]

    y = 0
    if title:
        parts.append(_svg_text(padding_x, 16, title, size=13, weight="bold"))
        y += title_h

    x = 0
    for col_idx, header in enumerate(headers):
        w = col_widths[col_idx]
        parts.append(_svg_rect(x, y, w, row_h, (235, 238, 242), (180, 180, 180)))
        parts.append(_svg_text(x + padding_x, y + padding_y + 11, header, size=12))
        x += w
    y += row_h

    for row_idx, row in enumerate(rows):
        x = 0
        fill = (255, 255, 255) if row_idx % 2 == 0 else (247, 248, 250)
        for col_idx, cell in enumerate(row):
            w = col_widths[col_idx]
            parts.append(_svg_rect(x, y, w, row_h, fill, (215, 215, 215)))
            parts.append(_svg_text(x + padding_x, y + padding_y + 11, cell, size=12))
            x += w
        y += row_h
    parts.append("</svg>\n")
    out = ensure_parent(path)
    out.write_text("\n".join(parts), encoding="utf-8")
    return out


def save_metrics_csv(path: str | Path, metrics: object) -> Path:
    """Write metrics to CSV through pandas and return the output path."""

    out = ensure_parent(path)
    _coerce_metrics_frame(metrics).to_csv(out, index=False)
    return out


def _coerce_series_frame(
    series: pd.DataFrame | pd.Series | Mapping[str, Sequence[float]] | Sequence[float],
) -> pd.DataFrame:
    if isinstance(series, pd.DataFrame):
        frame = series.copy()
    elif isinstance(series, pd.Series):
        frame = series.to_frame(name=series.name or "value")
    elif isinstance(series, Mapping):
        frame = pd.DataFrame(series)
    else:
        frame = pd.DataFrame({"value": list(series)})
    numeric = frame.apply(pd.to_numeric, errors="coerce")
    return numeric.dropna(axis=1, how="all")


def _coerce_metrics_frame(
    metrics: pd.DataFrame | Mapping[str, object] | Sequence[Mapping[str, object]],
) -> pd.DataFrame:
    if isinstance(metrics, pd.DataFrame):
        return metrics.copy()
    if isinstance(metrics, Mapping):
        if all(np.isscalar(v) or isinstance(v, str) for v in metrics.values()):
            return pd.DataFrame([metrics])
        return pd.DataFrame(metrics)
    return pd.DataFrame(list(metrics))


def _fit_image(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    if image.size == size:
        return image
    resampling = getattr(Image.Resampling, "BILINEAR", Image.BILINEAR)
    return image.resize(size, resampling)


def _draw_axes(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    y_min: float,
    y_max: float,
    font: ImageFont.ImageFont,
) -> None:
    x0, y0, x1, y1 = box
    draw.line((x0, y0, x1, y0), fill=(80, 80, 80), width=1)
    draw.line((x0, y0, x0, y1), fill=(80, 80, 80), width=1)
    for i in range(5):
        frac = i / 4
        y = y0 - int(round((y0 - y1) * frac))
        value = y_min + (y_max - y_min) * frac
        draw.line((x0 - 4, y, x1, y), fill=(225, 225, 225), width=1)
        draw.text((4, y - 7), f"{value:.3g}", fill=(55, 55, 55), font=font)


def _draw_legend(
    draw: ImageDraw.ImageDraw,
    labels: Iterable[object],
    colors: Sequence[Color],
    origin: tuple[int, int],
    font: ImageFont.ImageFont,
) -> None:
    x, y = origin
    for idx, label in enumerate(labels):
        text = str(label)
        color = colors[idx % len(colors)]
        draw.line((x, y + 7, x + 18, y + 7), fill=color, width=2)
        draw.text((x + 24, y), text, fill=(0, 0, 0), font=font)
        y += 16


def _format_cell(value: object) -> str:
    if isinstance(value, (float, np.floating)):
        if not np.isfinite(value):
            return str(value)
        return f"{float(value):.5g}"
    return str(value)


def _short_label(text: str, width: int, font: ImageFont.ImageFont) -> str:
    if _text_width(font, text) <= width:
        return text
    suffix = "..."
    available = max(0, width - _text_width(font, suffix))
    out = ""
    for char in text:
        if _text_width(font, out + char) > available:
            break
        out += char
    return out + suffix


def _default_font() -> ImageFont.ImageFont:
    return ImageFont.load_default()


def _text_width(font: ImageFont.ImageFont, text: str) -> int:
    bbox = font.getbbox(text)
    return int(bbox[2] - bbox[0])


def _text_height(font: ImageFont.ImageFont, text: str) -> int:
    bbox = font.getbbox(text)
    return int(bbox[3] - bbox[1])


def color_to_hex(color: Color) -> str:
    return f"#{int(color[0]):02x}{int(color[1]):02x}{int(color[2]):02x}"


def _svg_open(width: int, height: int, background: Color) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(width)}" '
        f'height="{int(height)}" viewBox="0 0 {int(width)} {int(height)}">'
        f'<rect width="100%" height="100%" fill="{color_to_hex(background)}" />'
    )


def _svg_rect(
    x: int | float,
    y: int | float,
    width: int | float,
    height: int | float,
    fill: Color,
    stroke: Color | None = None,
) -> str:
    stroke_attr = f' stroke="{color_to_hex(stroke)}"' if stroke is not None else ""
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
        f'fill="{color_to_hex(fill)}"{stroke_attr} />'
    )


def _svg_line(
    x0: int | float,
    y0: int | float,
    x1: int | float,
    y1: int | float,
    color: Color,
    width: int | float,
) -> str:
    return (
        f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" '
        f'stroke="{color_to_hex(color)}" stroke-width="{width}" />'
    )


def _svg_text(
    x: int | float,
    y: int | float,
    text: str,
    *,
    size: int = 12,
    fill: Color = (0, 0, 0),
    weight: str = "normal",
) -> str:
    safe = html_escape(str(text), quote=True)
    return (
        f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{color_to_hex(fill)}">{safe}</text>'
    )
