from __future__ import annotations

import math
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image, ImageDraw, ImageFont


@dataclass
class SimulatedData:
    images: torch.Tensor
    patterns: torch.Tensor
    b_static: torch.Tensor
    r_dynamic: torch.Tensor
    y_factors: torch.Tensor
    lambdas: torch.Tensor
    sigma2: torch.Tensor

    @property
    def image_size(self) -> int:
        return int(self.images.shape[-1])


def seed_everything(seed: int) -> torch.Generator:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    g = torch.Generator()
    g.manual_seed(seed)
    return g


def _font(size: int) -> ImageFont.ImageFont:
    for name in ("arial.ttf", "DejaVuSans-Bold.ttf", "C:/Windows/Fonts/arial.ttf"):
        try:
            return ImageFont.truetype(name, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def synthetic_mnist_like(num_samples: int, image_size: int, seed: int) -> torch.Tensor:
    rng = np.random.default_rng(seed)
    out: list[np.ndarray] = []
    font = _font(max(10, int(image_size * 0.72)))
    for i in range(num_samples):
        canvas = Image.new("L", (image_size, image_size), 0)
        draw = ImageDraw.Draw(canvas)
        kind = i % 4
        if kind == 0:
            digit = str(int(rng.integers(0, 10)))
            bbox = draw.textbbox((0, 0), digit, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x = int((image_size - tw) / 2 + rng.integers(-3, 4))
            y = int((image_size - th) / 2 + rng.integers(-3, 4))
            draw.text((x, y), digit, fill=255, font=font)
        elif kind == 1:
            margin = int(image_size * 0.18)
            draw.ellipse(
                [
                    margin + int(rng.integers(-2, 3)),
                    margin,
                    image_size - margin,
                    image_size - margin + int(rng.integers(-2, 3)),
                ],
                outline=255,
                width=max(2, image_size // 12),
            )
        elif kind == 2:
            for k in range(4, image_size - 4, max(3, image_size // 8)):
                draw.rectangle([k, image_size // 4, k + max(1, image_size // 20), 3 * image_size // 4], fill=255)
        else:
            draw.rectangle(
                [image_size // 5, image_size // 3, 4 * image_size // 5, 2 * image_size // 3],
                outline=255,
                width=max(2, image_size // 12),
            )
            draw.line([image_size // 5, image_size // 2, 4 * image_size // 5, image_size // 2], fill=255, width=max(1, image_size // 18))
        arr = np.asarray(canvas, dtype=np.float32) / 255.0
        arr = np.clip(arr + rng.normal(0.0, 0.01, size=arr.shape).astype(np.float32), 0.0, 1.0)
        out.append(arr)
    return torch.from_numpy(np.stack(out, axis=0)).unsqueeze(1).float()


def load_mnist_or_synthetic(
    num_samples: int,
    image_size: int,
    data_dir: str | Path,
    seed: int,
    synthetic_fallback: bool = True,
    source: str = "mnist",
) -> torch.Tensor:
    if source == "synthetic":
        return synthetic_mnist_like(num_samples, image_size, seed)
    try:
        from torchvision import datasets, transforms

        ds = datasets.MNIST(str(data_dir), train=True, download=True, transform=transforms.ToTensor())
        idx = torch.randperm(len(ds), generator=seed_everything(seed))[:num_samples]
        imgs = torch.stack([ds[int(i)][0] for i in idx], dim=0)
        if imgs.shape[-1] != image_size:
            imgs = F.interpolate(imgs, size=(image_size, image_size), mode="bilinear", align_corners=False)
        return imgs.clamp(0.0, 1.0)
    except Exception:
        if not synthetic_fallback:
            raise
        return synthetic_mnist_like(num_samples, image_size, seed)


def generate_patterns(
    num_patterns: int,
    image_size: int,
    generator: torch.Generator,
    distribution: str = "uniform",
    device: str | torch.device = "cpu",
) -> torch.Tensor:
    shape = (num_patterns, image_size * image_size)
    if distribution == "uniform":
        p = torch.rand(shape, generator=generator, dtype=torch.float32)
    elif distribution == "binary":
        p = torch.randint(0, 2, shape, generator=generator, dtype=torch.float32)
    elif distribution == "gaussian":
        p = torch.randn(shape, generator=generator, dtype=torch.float32)
        p = (p - p.amin(dim=1, keepdim=True)) / (p.amax(dim=1, keepdim=True) - p.amin(dim=1, keepdim=True) + 1e-8)
    else:
        raise ValueError(f"Unknown pattern distribution: {distribution}")
    return p.to(device)


def normalize_rows(x: torch.Tensor, mode: str = "max") -> torch.Tensor:
    if mode == "max":
        return x / x.amax(dim=1, keepdim=True).clamp_min(1e-8)
    if mode == "minmax":
        return (x - x.amin(dim=1, keepdim=True)) / (
            x.amax(dim=1, keepdim=True) - x.amin(dim=1, keepdim=True) + 1e-8
        )
    raise ValueError(f"Unknown normalize mode: {mode}")


def compute_static_measurements(flat_images: torch.Tensor, patterns: torch.Tensor, chunk_size: int = 128) -> torch.Tensor:
    """Compute B = T @ I.T in sample chunks.

    The paper-scale matrix uses 16,384 patterns and 16,384 pixels. Chunking over
    samples keeps peak memory predictable while retaining the exact forward model.
    """
    outs = []
    for start in range(0, flat_images.shape[0], int(chunk_size)):
        outs.append(flat_images[start : start + int(chunk_size)] @ patterns.t())
    return torch.cat(outs, dim=0)


def dynamic_factors(
    num_samples: int,
    num_patterns: int,
    lambda_min: float,
    lambda_max: float,
    generator: torch.Generator,
    device: str | torch.device = "cpu",
) -> tuple[torch.Tensor, torch.Tensor]:
    lambdas = torch.empty(num_samples, dtype=torch.float64).uniform_(lambda_min, lambda_max, generator=generator)
    n = torch.arange(num_patterns, dtype=torch.float64).unsqueeze(0)
    factors = torch.exp(n * torch.log(lambdas.unsqueeze(1))).to(torch.float32)
    return factors.to(device), lambdas.to(torch.float32).to(device)


def simulate_scgi_dataset(cfg: dict, profile: str | None = None) -> SimulatedData:
    active = cfg["active"]
    data_cfg = cfg.get("data", {})
    seed = int(cfg.get("seed", 0))
    device_name = active.get("device", "cpu")
    device = torch.device("cuda" if device_name == "cuda" and torch.cuda.is_available() else "cpu")
    g = seed_everything(seed)

    h = int(active["image_size"])
    m = int(active["num_samples"])
    n = int(active["num_patterns"])
    images = load_mnist_or_synthetic(
        num_samples=m,
        image_size=h,
        data_dir=Path(cfg.get("paths", {}).get("data_dir", "data")),
        seed=seed,
        synthetic_fallback=bool(data_cfg.get("synthetic_fallback", True)),
        source=str(active.get("data_source", data_cfg.get("source", "mnist"))),
    ).to(device)
    patterns = generate_patterns(n, h, g, data_cfg.get("pattern_distribution", "uniform"), device=device)
    flat = images.reshape(m, h * h)
    b = compute_static_measurements(flat, patterns, int(active.get("measurement_chunk", 128)))
    b = normalize_rows(b, data_cfg.get("normalize", "max"))
    factors, lambdas = dynamic_factors(
        m,
        n,
        float(active.get("lambda_min", data_cfg.get("lambda_min", 0.9995))),
        float(active.get("lambda_max", data_cfg.get("lambda_max", 1.0))),
        g,
        device=device,
    )
    r = normalize_rows(factors * b, data_cfg.get("normalize", "max"))
    sigma2 = b.var(dim=1, unbiased=False).clamp_min(1e-8)
    return SimulatedData(images=images, patterns=patterns, b_static=b, r_dynamic=r, y_factors=factors, lambdas=lambdas, sigma2=sigma2)


def train_val_split(data: SimulatedData, train_samples: int) -> tuple[SimulatedData, SimulatedData]:
    train_samples = int(train_samples)

    def sl(s: slice) -> SimulatedData:
        return SimulatedData(
            images=data.images[s],
            patterns=data.patterns,
            b_static=data.b_static[s],
            r_dynamic=data.r_dynamic[s],
            y_factors=data.y_factors[s],
            lambdas=data.lambdas[s],
            sigma2=data.sigma2[s],
        )

    return sl(slice(0, train_samples)), sl(slice(train_samples, None))
