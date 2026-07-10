"""Shared helpers for paper-driven mechanism experiments."""

from __future__ import annotations

from dataclasses import dataclass
import datetime
import math
import platform
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Optional

import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFilter

from src.basis import MeasurementBasis, basis_frame_budget, make_basis
from src.data_sim import synthetic_mnist_like
from src.mechanisms import make_multiplicative_channel, moving_average_1d


@dataclass
class PaperObject:
    name: str
    family: str
    vector: torch.Tensor
    image_size: int
    k_eff: float


def effective_support(values: torch.Tensor) -> float:
    vector = values.reshape(-1).to(dtype=torch.float64)
    numerator = vector.sum().pow(2)
    denominator = vector.pow(2).sum().clamp_min(1.0e-12)
    return float((numerator / denominator).item())


def _normalize_image(array: np.ndarray) -> np.ndarray:
    array = np.asarray(array, dtype=np.float32)
    array = array - float(array.min())
    max_value = float(array.max())
    if max_value > 0:
        array = array / max_value
    return np.clip(array, 0.0, 1.0)


def _draw_letter(letter: str, image_size: int) -> np.ndarray:
    image = Image.new("L", (image_size, image_size), 0)
    draw = ImageDraw.Draw(image)
    try:
        from PIL import ImageFont

        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", int(0.75 * image_size))
    except Exception:
        font = None
    bbox = draw.textbbox((0, 0), letter, font=font)
    x = (image_size - (bbox[2] - bbox[0])) // 2
    y = (image_size - (bbox[3] - bbox[1])) // 2
    draw.text((x, y), letter, fill=255, font=font)
    return np.asarray(image, dtype=np.float32) / 255.0


def _stripe(image_size: int) -> np.ndarray:
    arr = np.zeros((image_size, image_size), dtype=np.float32)
    width = max(2, image_size // 8)
    for start in range(image_size // 8, image_size, max(width * 2, 2)):
        arr[:, start : min(image_size, start + width)] = 1.0
    return arr


def _ring(image_size: int) -> np.ndarray:
    yy, xx = np.mgrid[:image_size, :image_size]
    center = (image_size - 1) / 2.0
    radius = np.sqrt((xx - center) ** 2 + (yy - center) ** 2)
    outer = image_size * 0.34
    inner = image_size * 0.22
    return ((radius <= outer) & (radius >= inner)).astype(np.float32)


def _natural_patch(image_size: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    small = rng.normal(size=(max(4, image_size // 4), max(4, image_size // 4))).astype(np.float32)
    image = Image.fromarray((_normalize_image(small) * 255.0).astype(np.uint8), mode="L").resize(
        (image_size, image_size),
        Image.Resampling.BICUBIC,
    )
    image = image.filter(ImageFilter.GaussianBlur(radius=max(0.5, image_size / 48.0)))
    arr = np.asarray(image, dtype=np.float32) / 255.0
    yy, xx = np.mgrid[:image_size, :image_size]
    vignette = np.exp(-(((xx - image_size / 2) ** 2 + (yy - image_size / 2) ** 2) / (2.0 * (0.38 * image_size) ** 2)))
    return _normalize_image(arr * vignette)


def make_paper_objects(count: int, image_size: int, seed: int) -> List[PaperObject]:
    """Create deterministic objects spanning support and texture families."""

    count = int(count)
    if count <= 0:
        raise ValueError("count must be positive.")
    objects: List[tuple[str, str, torch.Tensor]] = []

    mnist_count = max(0, min(count, max(2, count - 5)))
    mnist = synthetic_mnist_like(mnist_count, image_size=image_size, seed=seed)
    for idx in range(mnist_count):
        objects.append((f"digit_{idx}", "synthetic_digit", mnist[idx, 0].reshape(-1)))

    extras = [
        ("letter_A", "binary_letter", _draw_letter("A", image_size)),
        ("letter_L", "binary_letter", _draw_letter("L", image_size)),
        ("stripe", "stripe", _stripe(image_size)),
        ("ring", "ring", _ring(image_size)),
        ("natural_patch", "procedural_natural", _natural_patch(image_size, seed + 991)),
    ]
    for name, family, array in extras:
        if len(objects) >= count:
            break
        objects.append((name, family, torch.from_numpy(_normalize_image(array)).reshape(-1).to(dtype=torch.float32)))

    while len(objects) < count:
        idx = len(objects)
        arr = _natural_patch(image_size, seed + 1000 + idx)
        objects.append((f"natural_patch_{idx}", "procedural_natural", torch.from_numpy(arr).reshape(-1).to(dtype=torch.float32)))

    out: List[PaperObject] = []
    for name, family, vector in objects[:count]:
        vector = vector.reshape(-1).to(dtype=torch.float32).clamp_min(0.0)
        out.append(
            PaperObject(
                name=name,
                family=family,
                vector=vector,
                image_size=int(image_size),
                k_eff=effective_support(vector),
            )
        )
    return out


def make_paper_basis(name: str, num_pixels: int, seed: int) -> MeasurementBasis:
    key = name.lower().replace("-", "_")
    random_frames, _ = basis_frame_budget(num_pixels)
    if key in {"hadamard_ordered", "hadamard_natural"}:
        return make_basis("hadamard_paired", num_pixels=num_pixels)
    if key in {"hadamard_shuffled", "hadamard_random_time", "hadamard_random_paired"}:
        return make_basis("hadamard_random_paired", num_pixels=num_pixels, seed=seed)
    if key in {"srht", "srht_paired"}:
        return make_basis("srht_paired", num_pixels=num_pixels, seed=seed)
    if key in {"random_uniform", "random_binary"}:
        return make_basis(key, num_pixels=num_pixels, num_frames=random_frames, seed=seed, reconstruction="correlation")
    return make_basis(key, num_pixels=num_pixels, num_frames=random_frames, seed=seed, reconstruction="correlation")


def logspace_windows(num_frames: int, min_window: int = 4, max_fraction: float = 0.5) -> List[int]:
    max_window = max(int(min_window), int(round(num_frames * float(max_fraction))))
    values = set()
    value = int(min_window)
    while value <= max_window:
        values.add(max(1, value))
        value *= 2
    values.add(max_window)
    return sorted(values)


def mean_agc_gain(measurements: torch.Tensor, window: int, eps: float = 1.0e-8) -> torch.Tensor:
    """Prompt-specified fair estimator: movmean(R, W) / mean(R)."""

    values = measurements.reshape(-1).to(dtype=torch.float32)
    smooth = moving_average_1d(values, int(window)).clamp_min(eps)
    gain_hat = smooth / values.mean().clamp_min(eps)
    return gain_hat / gain_hat.mean().clamp_min(eps)


def log_agc_gain(measurements: torch.Tensor, window: int) -> tuple[torch.Tensor, float]:
    """Theorem-B windowed log-domain estimator.

    Theorem B analyzes windowed means of ``Y_n = log R_n``: the window mean
    estimates ``ell_n + m_T`` and the *centered* log-gain ``ell_n - mean(ell)``
    is the identifiable estimand (the gauge scalar ``m_T`` cancels). The
    faithful estimator is therefore

        ``gain_hat_n  proportional to  exp( movmean(log R, W)_n - its mean )``,

    mean-normalised to unit mean (the same gauge convention as
    :func:`mean_agc_gain`).

    Positivity guard (Theorem B assumption (iv)): the theorem requires
    ``R_n > 0`` *on the analyzed record* (positivity/offset margin, bucket
    convention (ii) of the manuscript). The guard implements exactly that
    restriction: frames with ``R_n <= 0`` are excluded from the analyzed
    record, i.e. the windowed log-mean is a masked moving average over the
    positive frames within each window (a hard floor would instead inject a
    ``log(eps)`` outlier for the exactly-zero complementary DC frame of paired
    Hadamard, which assumption (iv) never admits into the record). Windows
    containing no positive frame fall back to the gauge value (relative gain
    1). For physical nonnegative-intensity arms the mask touches at most the
    occasional zero bucket; for the raw signed Walsh arms — bucket convention
    (i), where ``log B_n`` is undefined by construction — about half the
    frames are excluded, and the returned ``frac_nonpos`` (fraction of frames
    with ``R_n <= 0``) flags those arms as diagnostic-only, per the
    manuscript.

    Returns ``(gain_hat, frac_nonpos)``.
    """

    values = measurements.reshape(-1).to(dtype=torch.float32)
    mask = (values > 0).to(dtype=torch.float32)
    frac_nonpos = float(1.0 - mask.mean().item())
    log_values = torch.log(values.clamp_min(1.0e-30)) * mask
    weight = moving_average_1d(mask, int(window))
    smooth_log = moving_average_1d(log_values, int(window)) / weight.clamp_min(1.0e-8)
    # Windows with no positive frame carry no log-domain information: pin them
    # to the record-level mean so they contribute the gauge value exp(0)=1.
    valid = weight > 1.0e-8
    if bool(valid.any()):
        record_mean = smooth_log[valid].mean()
    else:
        record_mean = torch.zeros((), dtype=smooth_log.dtype)
    smooth_log = torch.where(valid, smooth_log, record_mean)
    gain_hat = torch.exp(smooth_log - smooth_log.mean())
    return gain_hat / gain_hat.mean().clamp_min(1.0e-8), frac_nonpos


def scale_aligned_gain_error(estimated: torch.Tensor, true_gains: torch.Tensor, eps: float = 1.0e-8) -> float:
    estimate = estimated.reshape(-1).to(dtype=torch.float64)
    truth = true_gains.reshape(-1).to(dtype=torch.float64)
    estimate = estimate / estimate.mean().clamp_min(eps)
    truth = truth / truth.mean().clamp_min(eps)
    scale = (estimate @ truth) / estimate.pow(2).sum().clamp_min(eps)
    aligned = estimate * scale
    return float(((aligned - truth).pow(2).sum().sqrt() / truth.pow(2).sum().sqrt().clamp_min(eps)).item())


def make_shared_channel(num_frames: int, rho: float, sigma_a: float, seed: int) -> torch.Tensor:
    channel = make_multiplicative_channel(
        num_frames=num_frames,
        model="ou",
        rho=float(rho),
        sigma_a=float(sigma_a),
        seed=int(seed),
        device="cpu",
        dtype=torch.float32,
        normalize_mean=True,
    )
    return channel.gains.cpu()


def rel_mse(reconstruction: torch.Tensor, target: torch.Tensor, eps: float = 1.0e-12) -> float:
    recon = reconstruction.reshape(-1).to(dtype=torch.float64)
    truth = target.reshape(-1).to(dtype=torch.float64)
    scale = (recon @ truth) / recon.pow(2).sum().clamp_min(eps)
    aligned = recon * scale
    return float(((aligned - truth).pow(2).mean() / truth.pow(2).mean().clamp_min(eps)).item())


def write_caption(path: Path, title: str, lines: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = [f"# {title}", ""]
    body.extend(str(line) for line in lines)
    body.append("")
    path.write_text("\n".join(body), encoding="utf-8")


def git_commit(root: Optional[Path] = None) -> Optional[str]:
    """Return the current git HEAD commit, or None if unavailable."""

    try:
        cwd = str(root) if root is not None else None
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=cwd, stderr=subprocess.DEVNULL
        )
        return out.decode("utf-8").strip()
    except Exception:
        return None


def build_run_manifest(args, root: Optional[Path] = None, extra: Optional[dict] = None) -> dict:
    """Provenance manifest: UTC timestamp, git commit, host, versions, full args."""

    manifest = {
        "utc_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "git_commit": git_commit(root),
        "hostname": platform.node(),
        "python_version": sys.version.split()[0],
        "torch_version": torch.__version__,
        "numpy_version": np.__version__,
        "args": vars(args) if hasattr(args, "__dict__") else dict(args),
    }
    if extra:
        manifest.update(extra)
    return manifest


def _rect_shape_for_pixels(num_pixels: int) -> tuple[int, int]:
    """Factor a power-of-two pixel count into a near-square (height, width)."""

    p = int(num_pixels)
    side = int(math.isqrt(p))
    if side * side == p:
        return side, side
    k = int(round(math.log2(p)))
    if 2 ** k != p:
        raise ValueError(f"num_pixels must be a power of two, got {p}.")
    hk = k // 2
    wk = k - hk
    return 2 ** hk, 2 ** wk


def make_paper_objects_pixels(count: int, num_pixels: int, seed: int) -> List[PaperObject]:
    """Objects of an exact (power-of-two) pixel count for orthogonal N-sweeps.

    Perfect-square pixel counts delegate to :func:`make_paper_objects` so the
    N=1024 (32x32) and N=4096 (64x64) arms reproduce the square-image objects
    used elsewhere. Non-square power-of-two counts (e.g. 2048 -> 32x64) resize
    square renders onto a near-square rectangular canvas.
    """

    height, width = _rect_shape_for_pixels(num_pixels)
    if height == width:
        return make_paper_objects(count, image_size=height, seed=seed)

    base = make_paper_objects(count, image_size=width, seed=seed)
    out: List[PaperObject] = []
    for obj in base:
        square = obj.vector.reshape(width, width).cpu().numpy()
        image = Image.fromarray((_normalize_image(square) * 255.0).astype(np.uint8), mode="L").resize(
            (width, height), Image.Resampling.BILINEAR
        )
        vector = torch.from_numpy(_normalize_image(np.asarray(image, dtype=np.float32))).reshape(-1)
        vector = vector.to(dtype=torch.float32).clamp_min(0.0)
        out.append(
            PaperObject(
                name=obj.name,
                family=obj.family,
                vector=vector,
                image_size=int(width),
                k_eff=effective_support(vector),
            )
        )
    return out
