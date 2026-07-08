from __future__ import annotations

import torch


def minmax(x: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    return (x - x.amin()) / (x.amax() - x.amin() + eps)


def dgi_reconstruct(y: torch.Tensor, patterns: torch.Tensor, image_size: int, normalize: bool = True) -> torch.Tensor:
    """Differential ghost imaging reconstruction for one measurement sequence.

    Args:
        y: shape [N].
        patterns: shape [N, H*W] with amplitude-only illumination values.
        image_size: H = W.
    """
    if y.ndim != 1:
        raise ValueError(f"y must be [N], got {tuple(y.shape)}")
    if patterns.ndim != 2:
        raise ValueError(f"patterns must be [N, P], got {tuple(patterns.shape)}")
    q = patterns.sum(dim=1).clamp_min(1e-8)
    term1 = (y[:, None] * patterns).mean(dim=0)
    term2 = (y.mean() / q.mean()) * (q[:, None] * patterns).mean(dim=0)
    out = (term1 - term2).reshape(1, image_size, image_size)
    return minmax(out).clamp(0.0, 1.0) if normalize else out


def forward_project(image: torch.Tensor, patterns: torch.Tensor) -> torch.Tensor:
    if image.ndim == 3:
        image = image.unsqueeze(0)
    flat = image.reshape(image.shape[0], -1)
    return flat @ patterns.t()


def reconstruct_batch(y_batch: torch.Tensor, patterns: torch.Tensor, image_size: int) -> torch.Tensor:
    return torch.stack([dgi_reconstruct(y, patterns, image_size) for y in y_batch], dim=0)

