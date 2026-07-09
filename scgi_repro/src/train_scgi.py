from __future__ import annotations

from dataclasses import dataclass
import math

import torch
from torch.utils.data import DataLoader, TensorDataset

from .data_sim import SimulatedData, normalize_rows


@dataclass
class TrainHistory:
    train_loss: list[float]
    val_mse: list[float]


def as_images(seq: torch.Tensor, image_size: int) -> torch.Tensor:
    return seq.reshape(seq.shape[0], 1, image_size, image_size)


def _as_rows(seq: torch.Tensor) -> tuple[torch.Tensor, torch.Size]:
    if seq.ndim == 0:
        raise ValueError("measurement sequence must have at least one dimension")
    original_shape = seq.shape
    return seq.reshape(-1, original_shape[-1]), original_shape


def apply_gain_correction(
    r_dynamic: torch.Tensor,
    gains: torch.Tensor,
    normalize_mode: str = "max",
    eps: float = 1e-8,
) -> torch.Tensor:
    """Undo a per-pattern multiplicative gain and restore row normalization."""
    rows, original_shape = _as_rows(r_dynamic)
    gain_rows = gains.reshape(rows.shape).to(device=rows.device, dtype=rows.dtype)
    corrected = rows / gain_rows.clamp_min(float(eps))
    return normalize_rows(corrected, normalize_mode).reshape(original_shape)


def oracle_gain_correct(
    r_dynamic: torch.Tensor,
    true_factors: torch.Tensor,
    normalize_mode: str = "max",
    eps: float = 1e-8,
) -> torch.Tensor:
    """Physical positive control: undo the simulator's known dynamic factors."""
    return apply_gain_correction(r_dynamic, true_factors, normalize_mode=normalize_mode, eps=eps)


def fit_exponential_gains(
    r_dynamic: torch.Tensor,
    eps: float = 1e-6,
    lambda_min: float = 0.95,
    lambda_max: float = 1.05,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Fit row-wise gains of the form ``gain[n] = lambda**n`` from buckets.

    The fit uses only the measured dynamic sequence. Random illumination
    fluctuations are treated as zero-mean residuals in log space, which is a
    useful Stage 0 diagnostic because the simulated channel is exponential.
    """
    rows, original_shape = _as_rows(r_dynamic)
    fit_rows = rows.detach().to(torch.float64).clamp_min(float(eps))
    n = torch.arange(rows.shape[-1], device=rows.device, dtype=torch.float64)
    x = n - n.mean()
    log_rows = torch.log(fit_rows)
    centered = log_rows - log_rows.mean(dim=1, keepdim=True)
    beta = (centered * x).sum(dim=1) / x.pow(2).sum().clamp_min(float(eps))
    lambdas = torch.exp(beta).clamp(float(lambda_min), float(lambda_max))
    gains = torch.exp(torch.log(lambdas).unsqueeze(1) * n.unsqueeze(0))
    return gains.to(device=rows.device, dtype=rows.dtype).reshape(original_shape), lambdas.to(device=rows.device, dtype=rows.dtype)


def analytic_gain_correct(
    r_dynamic: torch.Tensor,
    normalize_mode: str = "max",
    eps: float = 1e-8,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Blind exponential gain correction for the Stage 0 simulated channel."""
    gains, lambdas = fit_exponential_gains(r_dynamic, eps=max(float(eps), 1e-6))
    corrected = apply_gain_correction(r_dynamic, gains, normalize_mode=normalize_mode, eps=eps)
    return corrected, lambdas


def scgi_loss(y_hat: torch.Tensor, b: torch.Tensor, sigma2: torch.Tensor, gamma: float) -> torch.Tensor:
    mse = torch.mean((y_hat - b) ** 2)
    sigma = sigma2.reshape(-1, 1, 1, 1).clamp_min(1e-8)
    gaussian = torch.mean(((y_hat - b) ** 2) / (2.0 * sigma) + 0.5 * torch.log(2.0 * torch.pi * sigma))
    return mse + float(gamma) * gaussian


def train_scgi(
    model: torch.nn.Module,
    train: SimulatedData,
    val: SimulatedData,
    epochs: int,
    batch_size: int,
    lr: float,
    gamma: float,
) -> TrainHistory:
    image_size = train.image_size
    x_train = as_images(train.r_dynamic, image_size)
    y_train = as_images(train.b_static, image_size)
    ds = TensorDataset(x_train, y_train, train.sigma2)
    loader = DataLoader(ds, batch_size=batch_size, shuffle=True)
    opt = torch.optim.Adam(model.parameters(), lr=float(lr))
    hist = TrainHistory(train_loss=[], val_mse=[])
    model.train()
    for _epoch in range(int(epochs)):
        losses = []
        for xb, yb, sig in loader:
            opt.zero_grad(set_to_none=True)
            pred = model(xb)
            loss = scgi_loss(pred, yb, sig, gamma)
            loss.backward()
            opt.step()
            losses.append(float(loss.detach().cpu()))
        hist.train_loss.append(float(sum(losses) / max(1, len(losses))))
        with torch.no_grad():
            model.eval()
            pred = model(as_images(val.r_dynamic, image_size))
            mse = torch.mean((pred - as_images(val.b_static, image_size)) ** 2)
            hist.val_mse.append(float(mse.detach().cpu()))
            model.train()
    return hist


@torch.no_grad()
def correct_measurements(
    model: torch.nn.Module,
    r_dynamic: torch.Tensor,
    image_size: int,
    clamp: bool = True,
) -> torch.Tensor:
    model.eval()
    y = model(as_images(r_dynamic, image_size)).reshape(r_dynamic.shape)
    return y.clamp(0.0, 1.0) if clamp else y


@torch.no_grad()
def correct_measurements_padded(
    model: torch.nn.Module,
    r_dynamic: torch.Tensor,
    clamp: bool = True,
) -> torch.Tensor:
    """Apply a fully convolutional SCGI model to any sequence length.

    The original SCGI training data uses square measurement maps. M2 mechanism
    scans often use frame budgets such as 2048, so this helper pads each row to
    the nearest square with its row mean, applies the frozen model, and crops
    back to the original frame count.
    """

    rows, original_shape = _as_rows(r_dynamic)
    frames = int(rows.shape[-1])
    side = int(math.ceil(math.sqrt(frames)))
    padded_frames = side * side
    if padded_frames == frames:
        padded = rows
    else:
        pad = rows.mean(dim=1, keepdim=True).expand(rows.shape[0], padded_frames - frames)
        padded = torch.cat([rows, pad], dim=1)
    model.eval()
    y = model(as_images(padded, side)).reshape(rows.shape[0], padded_frames)[:, :frames]
    if clamp:
        y = y.clamp(0.0, 1.0)
    return y.reshape(original_shape)
