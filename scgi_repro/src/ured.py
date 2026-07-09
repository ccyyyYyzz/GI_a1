from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
import torch.nn.functional as F

from .dgi import forward_project
from .nafnet import TinyNAFNet


@dataclass
class UredResult:
    image: torch.Tensor
    cnr_trace: list[float]
    loss_trace: list[float]


def denoise_avg_pool(x: torch.Tensor, kernel_size: int = 3) -> torch.Tensor:
    kernel_size = max(1, int(kernel_size))
    if kernel_size % 2 == 0:
        kernel_size += 1
    return F.avg_pool2d(x, kernel_size=kernel_size, stride=1, padding=kernel_size // 2)


def denoise_nlm(x: torch.Tensor, h: float = 0.08, patch_size: int = 5, patch_distance: int = 6) -> torch.Tensor:
    try:
        from skimage.restoration import denoise_nl_means
    except Exception:
        return denoise_avg_pool(x)
    arr = x.detach().squeeze().clamp(0.0, 1.0).cpu().numpy()
    denoised = denoise_nl_means(
        arr,
        h=float(h),
        patch_size=int(patch_size),
        patch_distance=int(patch_distance),
        fast_mode=True,
        channel_axis=None,
    )
    out = torch.from_numpy(np.asarray(denoised, dtype=np.float32)).to(device=x.device, dtype=x.dtype)
    return out.reshape_as(x)


def apply_denoiser(x: torch.Tensor, ured: dict) -> torch.Tensor:
    name = str(ured.get("denoiser", "avg_pool")).lower()
    if name in {"none", "identity"}:
        return x
    if name in {"nlm", "nonlocal_means", "non_local_means"}:
        return denoise_nlm(
            x,
            h=float(ured.get("nlm_h", 0.08)),
            patch_size=int(ured.get("nlm_patch_size", 5)),
            patch_distance=int(ured.get("nlm_patch_distance", 6)),
        )
    return denoise_avg_pool(x, kernel_size=int(ured.get("denoise_kernel", 3)))


def optimize_untrained(
    coarse: torch.Tensor,
    y_corrected: torch.Tensor,
    patterns: torch.Tensor,
    cfg: dict,
    target: torch.Tensor | None = None,
    metric_fn=None,
    use_regularizer: bool = True,
) -> UredResult:
    ured = cfg.get("ured", {})
    active = cfg.get("active", {})
    steps = int(active.get("ured_steps", 50))
    lr = float(active.get("ured_lr", 0.001))
    beta = float(ured.get("beta", 0.5)) if use_regularizer else 0.0
    xi = float(ured.get("xi", 0.5))
    x_step = float(ured.get("x_step", 0.5))
    net = TinyNAFNet(
        channels=int(ured.get("channels", 24)),
        blocks=int(ured.get("blocks", 3)),
        residual_scale=float(ured.get("residual_scale", 0.1)),
    ).to(coarse.device)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.StepLR(opt, step_size=50, gamma=0.9)
    inp = coarse.detach().reshape(1, 1, *coarse.shape[-2:])
    x = inp.clone().detach()
    u = torch.zeros_like(x)
    y = y_corrected.detach().reshape(1, -1)
    traces: list[float] = []
    cnrs: list[float] = []
    for _ in range(steps):
        opt.zero_grad(set_to_none=True)
        out = net(inp)
        pred_y = forward_project(out, patterns)
        pred_y = pred_y / pred_y.amax(dim=1, keepdim=True).clamp_min(1e-8)
        data_loss = 0.5 * torch.mean((pred_y - y) ** 2)
        aug_loss = 0.5 * xi * torch.mean((x - out - u) ** 2)
        loss = data_loss + aug_loss
        loss.backward()
        opt.step()
        scheduler.step()
        with torch.no_grad():
            out = net(inp)
            if beta > 0:
                fx = apply_denoiser(x, ured)
                x = x - x_step * (beta * (x - fx) + xi * (x - out - u))
            else:
                x = out.detach()
            u = u - x + out.detach()
            final = (x - u).clamp(0.0, 1.0)
        traces.append(float(loss.detach().cpu()))
        if target is not None and metric_fn is not None:
            cnrs.append(float(metric_fn(final.detach(), target)))
    return UredResult(image=final.detach().squeeze(0), cnr_trace=cnrs, loss_trace=traces)
