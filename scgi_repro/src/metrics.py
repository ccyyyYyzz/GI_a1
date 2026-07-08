from __future__ import annotations

import math
from dataclasses import dataclass

import torch
import torch.nn.functional as F


@dataclass
class MetricBundle:
    cnr: float
    psnr: float
    ssim: float
    ks_d: float
    ks_p: float


def cnr(recon: torch.Tensor, target: torch.Tensor, threshold: float = 0.5) -> float:
    r = recon.detach().float().reshape(-1)
    t = target.detach().float().reshape(-1)
    mask = t > threshold
    bg = ~mask
    if mask.sum() < 2 or bg.sum() < 2:
        return float("nan")
    os = r[mask]
    ob = r[bg]
    denom = (os.std(unbiased=False) + ob.std(unbiased=False)).clamp_min(1e-8) / 2.0
    return float((os.mean() - ob.mean()) / denom)


def psnr(recon: torch.Tensor, target: torch.Tensor, eps: float = 1e-8) -> float:
    mse = torch.mean((recon.detach().float() - target.detach().float()) ** 2).clamp_min(eps)
    return float(10.0 * torch.log10(torch.tensor(1.0, device=mse.device) / mse))


def ssim(recon: torch.Tensor, target: torch.Tensor) -> float:
    x = recon.detach().float().reshape(1, 1, *recon.shape[-2:])
    y = target.detach().float().reshape(1, 1, *target.shape[-2:])
    c1, c2 = 0.01**2, 0.03**2
    mu_x = F.avg_pool2d(x, 7, stride=1, padding=3)
    mu_y = F.avg_pool2d(y, 7, stride=1, padding=3)
    sig_x = F.avg_pool2d(x * x, 7, stride=1, padding=3) - mu_x * mu_x
    sig_y = F.avg_pool2d(y * y, 7, stride=1, padding=3) - mu_y * mu_y
    sig_xy = F.avg_pool2d(x * y, 7, stride=1, padding=3) - mu_x * mu_y
    val = ((2 * mu_x * mu_y + c1) * (2 * sig_xy + c2)) / ((mu_x**2 + mu_y**2 + c1) * (sig_x + sig_y + c2))
    return float(val.mean().clamp(-1.0, 1.0))


def normal_ks_test(x: torch.Tensor) -> tuple[float, float]:
    vals = x.detach().float().flatten()
    vals = vals[torch.isfinite(vals)]
    n = vals.numel()
    if n < 4:
        return float("nan"), float("nan")
    z = (vals - vals.mean()) / vals.std(unbiased=False).clamp_min(1e-8)
    z, _ = torch.sort(z)
    cdf = 0.5 * (1.0 + torch.erf(z / math.sqrt(2.0)))
    empirical_hi = torch.arange(1, n + 1, device=z.device, dtype=z.dtype) / n
    empirical_lo = torch.arange(0, n, device=z.device, dtype=z.dtype) / n
    d = torch.max(torch.maximum(torch.abs(empirical_hi - cdf), torch.abs(cdf - empirical_lo)))
    p = min(1.0, max(0.0, 2.0 * math.exp(-2.0 * n * float(d) ** 2)))
    return float(d), float(p)


def slope_vs_index(y: torch.Tensor) -> float:
    vals = y.detach().float().flatten()
    x = torch.linspace(0.0, 1.0, vals.numel(), device=vals.device)
    xm = x - x.mean()
    ym = vals - vals.mean()
    return float((xm * ym).sum() / (xm.pow(2).sum().clamp_min(1e-8)))


def bundle(recon: torch.Tensor, target: torch.Tensor, measurements: torch.Tensor) -> MetricBundle:
    d, p = normal_ks_test(measurements)
    return MetricBundle(cnr=cnr(recon, target), psnr=psnr(recon, target), ssim=ssim(recon, target), ks_d=d, ks_p=p)

