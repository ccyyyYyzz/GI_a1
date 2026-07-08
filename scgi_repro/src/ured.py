from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn.functional as F

from .dgi import forward_project
from .nafnet import TinyNAFNet


@dataclass
class UredResult:
    image: torch.Tensor
    cnr_trace: list[float]
    loss_trace: list[float]


def denoise_fallback(x: torch.Tensor) -> torch.Tensor:
    return F.avg_pool2d(x, kernel_size=3, stride=1, padding=1)


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
    net = TinyNAFNet(channels=int(ured.get("channels", 24)), blocks=int(ured.get("blocks", 3))).to(coarse.device)
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
                fx = denoise_fallback(x)
                x = x - x_step * (beta * (x - fx) + xi * (x - out - u))
            else:
                x = out.detach()
            u = u - x + out.detach()
            final = (x - u).clamp(0.0, 1.0)
        traces.append(float(loss.detach().cpu()))
        if target is not None and metric_fn is not None:
            cnrs.append(float(metric_fn(final.detach(), target)))
    return UredResult(image=final.detach().squeeze(0), cnr_trace=cnrs, loss_trace=traces)
