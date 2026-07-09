"""Multiplicative channels and blind/oracle correction mechanisms."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Optional

import torch
import torch.nn.functional as torch_f


@dataclass
class ChannelTrace:
    """A realized multiplicative channel sequence."""

    name: str
    gains: torch.Tensor
    rho: float
    sigma_a: float
    seed: int

    @property
    def num_frames(self) -> int:
        return int(self.gains.numel())


@dataclass
class CorrectedMeasurements:
    """Output from a correction rule."""

    values: torch.Tensor
    values_are_coefficients: bool
    gain_hat: Optional[torch.Tensor]
    correction: str


def _cpu_generator(seed: int) -> torch.Generator:
    generator = torch.Generator(device="cpu")
    generator.manual_seed(int(seed))
    return generator


def make_multiplicative_channel(
    num_frames: int,
    model: str = "ou",
    rho: float = 0.01,
    sigma_a: float = 0.15,
    seed: int = 0,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    normalize_mean: bool = True,
) -> ChannelTrace:
    """Generate a positive multiplicative gain sequence.

    ``rho`` is a dimensionless frame-rate/correlation-rate parameter. Small
    values produce slow drift; values near one produce frame-to-frame variation.
    ``sigma_a`` is the log-gain scale for OU and jitter channels.
    """

    frames = int(num_frames)
    if frames <= 0:
        raise ValueError("num_frames must be positive.")

    key = model.lower()
    generator = _cpu_generator(seed)
    rho_value = float(max(rho, 0.0))
    sigma_value = float(max(sigma_a, 0.0))

    if key == "exponential":
        t = torch.linspace(-0.5, 0.5, frames, dtype=dtype)
        log_gain = rho_value * t
        if sigma_value > 0:
            log_gain = log_gain * (sigma_value / 0.15)
    elif key == "ou":
        phi = float(torch.exp(torch.tensor(-rho_value, dtype=torch.float64)).item())
        innovation_scale = sigma_value * max(1.0 - phi * phi, 0.0) ** 0.5
        noise = torch.randn((frames,), generator=generator, dtype=dtype) * innovation_scale
        log_gain = torch.empty((frames,), dtype=dtype)
        log_gain[0] = torch.randn((1,), generator=generator, dtype=dtype)[0] * sigma_value
        for idx in range(1, frames):
            log_gain[idx] = phi * log_gain[idx - 1] + noise[idx]
        log_gain = log_gain - log_gain.mean()
    elif key == "jitter":
        slow_phi = float(torch.exp(torch.tensor(-min(rho_value, 1.0), dtype=torch.float64)).item())
        slow = torch.empty((frames,), dtype=dtype)
        slow[0] = torch.randn((1,), generator=generator, dtype=dtype)[0] * sigma_value
        slow_noise = torch.randn((frames,), generator=generator, dtype=dtype) * sigma_value * 0.25
        for idx in range(1, frames):
            slow[idx] = slow_phi * slow[idx - 1] + (1.0 - slow_phi) ** 0.5 * slow_noise[idx]
        fast_scale = sigma_value * min(max(rho_value, 0.0), 1.0) ** 0.5
        fast = torch.randn((frames,), generator=generator, dtype=dtype) * fast_scale
        log_gain = slow + fast
        log_gain = log_gain - log_gain.mean()
    else:
        raise ValueError(f"Unsupported channel model: {model}")

    gains = torch.exp(log_gain).to(device=device, dtype=dtype)
    if normalize_mean:
        gains = gains / gains.mean().clamp_min(1.0e-8)
    return ChannelTrace(name=key, gains=gains, rho=float(rho), sigma_a=float(sigma_a), seed=int(seed))


def simulate_channel_measurements(
    ideal_measurements: torch.Tensor,
    channel: ChannelTrace,
    read_noise: float = 0.0,
    seed: int = 0,
) -> torch.Tensor:
    """Apply multiplicative gains and optional additive Gaussian read noise."""

    ideal = ideal_measurements.reshape(-1).to(device=channel.gains.device, dtype=channel.gains.dtype)
    if ideal.numel() != channel.num_frames:
        raise ValueError(f"Expected {channel.num_frames} measurements, got {ideal.numel()}.")

    observed = ideal * channel.gains
    if read_noise and read_noise > 0.0:
        generator = _cpu_generator(seed)
        scale = ideal.detach().abs().mean().clamp_min(1.0).cpu() * float(read_noise)
        noise = torch.randn(ideal.shape, generator=generator, dtype=ideal.dtype).to(ideal.device) * scale.to(ideal.device)
        observed = observed + noise
    return observed


def moving_average_1d(values: torch.Tensor, window: int) -> torch.Tensor:
    """Centered moving average using replicated edge padding."""

    vector = values.reshape(1, 1, -1)
    width = max(1, int(window))
    if width % 2 == 0:
        width += 1
    width = min(width, max(1, values.numel() if values.numel() % 2 == 1 else values.numel() - 1))
    if width <= 1:
        return values.clone()

    left = width // 2
    right = width - 1 - left
    padded = torch_f.pad(vector, (left, right), mode="replicate")
    kernel = torch.ones((1, 1, width), dtype=values.dtype, device=values.device) / float(width)
    return torch_f.conv1d(padded, kernel).reshape(-1)


def estimate_agc_gain(
    measurements: torch.Tensor,
    window: Optional[int] = None,
    eps: float = 1.0e-8,
    clip_min: float = 0.05,
    clip_max: float = 20.0,
) -> torch.Tensor:
    """Blind automatic-gain-control estimate from the local RMS envelope."""

    values = measurements.reshape(-1)
    frames = values.numel()
    if frames == 0:
        raise ValueError("measurements must be non-empty.")
    if window is None:
        window = max(9, int(round(0.03 * frames)))
    if window % 2 == 0:
        window += 1

    local_power = moving_average_1d(values.pow(2), window).clamp_min(eps)
    envelope = torch.sqrt(local_power)
    reference = envelope.median().clamp_min(eps)
    gain_hat = (envelope / reference).clamp(float(clip_min), float(clip_max))
    return gain_hat / gain_hat.mean().clamp_min(eps)


def estimate_pair_gain_from_sums(
    measurements: torch.Tensor,
    eps: float = 1.0e-8,
    clip_min: float = 0.05,
    clip_max: float = 20.0,
) -> torch.Tensor:
    """Estimate per-frame gain for complementary pairs from pair sums."""

    values = measurements.reshape(-1)
    if values.numel() % 2 != 0:
        raise ValueError("pairwise gain estimation requires an even number of frames.")
    pair_sums = values[0::2] + values[1::2]
    reference = pair_sums.median().abs().clamp_min(eps)
    pair_gain = (pair_sums / reference).abs().clamp(float(clip_min), float(clip_max))
    frame_gain = torch.empty_like(values)
    frame_gain[0::2] = pair_gain
    frame_gain[1::2] = pair_gain
    return frame_gain / frame_gain.mean().clamp_min(eps)


def estimate_scgi_proxy_gain(
    measurements: torch.Tensor,
    paired: bool = False,
    window: Optional[int] = None,
    eps: float = 1.0e-8,
    clip_min: float = 0.05,
    clip_max: float = 20.0,
) -> torch.Tensor:
    """Estimate a slow blind gain envelope with an SCGI-style smooth prior.

    This proxy is intentionally lighter than a trained SCGI network: it uses
    only the observed bucket sequence and the paired-frame acquisition structure
    when available. It never reads the simulator's true gains or reference
    anchors, so it remains a blind equal-frame correction for M2.
    """

    values = measurements.reshape(-1)
    frames = values.numel()
    if frames == 0:
        raise ValueError("measurements must be non-empty.")
    if window is None:
        window = max(9, int(round(0.05 * frames)))
    if window % 2 == 0:
        window += 1

    if paired and frames % 2 == 0 and frames >= 4:
        envelope_source = (values[0::2] + values[1::2]).abs().clamp_min(eps)
        pair_window = max(3, int(round(0.5 * window)))
        if pair_window % 2 == 0:
            pair_window += 1
        smooth_log = moving_average_1d(torch.log(envelope_source), pair_window)
        pair_gain = torch.exp(smooth_log - smooth_log.median()).clamp(float(clip_min), float(clip_max))
        gain_hat = torch.empty_like(values)
        gain_hat[0::2] = pair_gain
        gain_hat[1::2] = pair_gain
    else:
        magnitude = values.abs().clamp_min(eps)
        smooth_log = moving_average_1d(torch.log(magnitude), window)
        gain_hat = torch.exp(smooth_log - smooth_log.median()).clamp(float(clip_min), float(clip_max))
    return gain_hat / gain_hat.mean().clamp_min(eps)


def _parse_reference_period(correction: str, default: int = 8) -> Optional[int]:
    key = correction.lower()
    if not (key.startswith("reference") or key.startswith("ref")):
        return None
    match = re.search(r"(\d+)$", key)
    period = int(match.group(1)) if match else int(default)
    return max(1, period)


def reference_anchor_count(num_frames: int, period: int, include_terminal: bool = True) -> int:
    """Return the number of inserted reference frames used by the simulator."""

    frames = int(num_frames)
    if frames <= 0:
        raise ValueError("num_frames must be positive.")
    k = max(1, int(period))
    count = ((frames - 1) // k) + 1
    if include_terminal and (frames - 1) % k != 0:
        count += 1
    return count


def estimate_reference_gain(
    true_gains: torch.Tensor,
    period: int,
    eps: float = 1.0e-8,
) -> torch.Tensor:
    """Estimate frame gains from every-K reference samples by linear interpolation.

    This compact simulation models inserted fixed-reference frames whose ideal
    signal is known, so each sampled reference frame gives a direct gain sample.
    The caller should account for the extra reference frames in frame-budget
    reporting; this function returns the interpolated gain for measurement frames.
    """

    gains = true_gains.reshape(-1)
    frames = gains.numel()
    if frames == 0:
        raise ValueError("true_gains must be non-empty.")
    k = max(1, int(period))
    ref_idx = torch.arange(0, frames, k, device=gains.device)
    if ref_idx[-1].item() != frames - 1:
        ref_idx = torch.cat([ref_idx, torch.tensor([frames - 1], device=gains.device, dtype=ref_idx.dtype)])
    ref_vals = gains.index_select(0, ref_idx).clamp_min(eps)

    x = torch.arange(frames, device=gains.device, dtype=gains.dtype)
    xp = ref_idx.to(dtype=gains.dtype)
    right = torch.bucketize(x, xp, right=False).clamp(max=ref_idx.numel() - 1)
    left = (right - 1).clamp(min=0)
    same = right == 0
    left = torch.where(same, right, left)
    x0 = xp.index_select(0, left)
    x1 = xp.index_select(0, right)
    y0 = ref_vals.index_select(0, left)
    y1 = ref_vals.index_select(0, right)
    weight = torch.where((x1 - x0).abs() < eps, torch.zeros_like(x), (x - x0) / (x1 - x0).clamp_min(eps))
    gain_hat = y0 + weight * (y1 - y0)
    return gain_hat / gain_hat.mean().clamp_min(eps)


def apply_correction(
    measurements: torch.Tensor,
    correction: str,
    true_gains: Optional[torch.Tensor] = None,
    paired: bool = False,
    agc_window: Optional[int] = None,
    eps: float = 1.0e-8,
) -> CorrectedMeasurements:
    """Apply oracle, none, blind gain corrections, or paired-ratio correction.

    For paired-ratio correction the returned ``values`` are signed coefficients,
    not frame measurements, because the ratio directly estimates
    ``<signed_pattern, object>`` up to a global total-intensity scale.
    """

    key = correction.lower()
    values = measurements.reshape(-1)
    reference_period = _parse_reference_period(key)

    if key == "none":
        return CorrectedMeasurements(values=values.clone(), values_are_coefficients=False, gain_hat=None, correction=key)

    if key == "oracle":
        if true_gains is None:
            raise ValueError("oracle correction requires true_gains.")
        gains = true_gains.reshape(-1).to(device=values.device, dtype=values.dtype)
        if gains.numel() != values.numel():
            raise ValueError(f"Expected {values.numel()} true gains, got {gains.numel()}.")
        return CorrectedMeasurements(
            values=values / gains.clamp_min(eps),
            values_are_coefficients=False,
            gain_hat=gains,
            correction=key,
        )

    if key == "agc":
        gain_hat = estimate_agc_gain(values, window=agc_window, eps=eps)
        return CorrectedMeasurements(
            values=values / gain_hat.clamp_min(eps),
            values_are_coefficients=False,
            gain_hat=gain_hat,
            correction=key,
        )

    if key in {"scgi_proxy", "scgi_smooth"}:
        gain_hat = estimate_scgi_proxy_gain(values, paired=paired, window=agc_window, eps=eps)
        return CorrectedMeasurements(
            values=values / gain_hat.clamp_min(eps),
            values_are_coefficients=False,
            gain_hat=gain_hat,
            correction=key,
        )

    if reference_period is not None:
        if true_gains is None:
            raise ValueError("reference correction requires true_gains in the compact simulator.")
        gains = true_gains.reshape(-1).to(device=values.device, dtype=values.dtype)
        if gains.numel() != values.numel():
            raise ValueError(f"Expected {values.numel()} true gains, got {gains.numel()}.")
        gain_hat = estimate_reference_gain(gains, period=reference_period, eps=eps)
        return CorrectedMeasurements(
            values=values / gain_hat.clamp_min(eps),
            values_are_coefficients=False,
            gain_hat=gain_hat,
            correction=key,
        )

    if key == "pairwise":
        if not paired:
            raise ValueError("pairwise correction requires a paired basis.")
        if values.numel() % 2 != 0:
            raise ValueError("pairwise correction requires an even number of measurements.")
        plus = values[0::2]
        minus = values[1::2]
        pair_sum = plus + minus
        total_estimate = pair_sum.median().abs().clamp_min(eps)
        coefficients = total_estimate * (plus - minus) / pair_sum.clamp_min(eps)
        gain_hat = estimate_pair_gain_from_sums(values, eps=eps)
        return CorrectedMeasurements(
            values=coefficients,
            values_are_coefficients=True,
            gain_hat=gain_hat,
            correction=key,
        )

    raise ValueError(f"Unsupported correction: {correction}")


def gain_error_stats(estimated: Optional[torch.Tensor], true_gains: torch.Tensor) -> dict:
    """Return compact gain-estimation error statistics."""

    truth = true_gains.reshape(-1)
    if estimated is None:
        return {
            "gain_rel_mse": float("nan"),
            "gain_corr": float("nan"),
            "gain_scale": float("nan"),
        }

    estimate = estimated.reshape(-1).to(device=truth.device, dtype=truth.dtype)
    scale = (estimate @ truth) / estimate.pow(2).sum().clamp_min(1.0e-8)
    aligned = estimate * scale
    rel_mse = (aligned - truth).pow(2).mean() / truth.pow(2).mean().clamp_min(1.0e-8)
    centered_estimate = estimate - estimate.mean()
    centered_truth = truth - truth.mean()
    corr = (centered_estimate @ centered_truth) / (
        centered_estimate.pow(2).sum().sqrt() * centered_truth.pow(2).sum().sqrt()
    ).clamp_min(1.0e-8)
    return {
        "gain_rel_mse": float(rel_mse.detach().cpu().item()),
        "gain_corr": float(corr.detach().cpu().item()),
        "gain_scale": float(scale.detach().cpu().item()),
    }
