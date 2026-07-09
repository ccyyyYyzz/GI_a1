from __future__ import annotations

import torch
from torch import nn
import torch.nn.functional as F


class ConvBlock(nn.Module):
    def __init__(self, in_ch: int, out_ch: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class UNet(nn.Module):
    def __init__(self, in_channels: int = 1, out_channels: int = 1, base_channels: int = 16, depth: int = 4):
        super().__init__()
        self.depth = int(depth)
        chans = [base_channels * (2**i) for i in range(self.depth)]
        self.downs = nn.ModuleList()
        prev = in_channels
        for ch in chans:
            self.downs.append(ConvBlock(prev, ch))
            prev = ch
        self.bottleneck = ConvBlock(chans[-1], chans[-1] * 2)
        rev = list(reversed(chans))
        self.up_trans = nn.ModuleList()
        self.ups = nn.ModuleList()
        prev = chans[-1] * 2
        for ch in rev:
            self.up_trans.append(nn.ConvTranspose2d(prev, ch, 2, stride=2))
            self.ups.append(ConvBlock(ch * 2, ch))
            prev = ch
        self.out = nn.Conv2d(base_channels, out_channels, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        skips = []
        h = x
        for down in self.downs:
            h = down(h)
            skips.append(h)
            h = F.max_pool2d(h, 2)
        h = self.bottleneck(h)
        for up_t, up, skip in zip(self.up_trans, self.ups, reversed(skips)):
            h = up_t(h)
            if h.shape[-2:] != skip.shape[-2:]:
                h = F.interpolate(h, size=skip.shape[-2:], mode="bilinear", align_corners=False)
            h = up(torch.cat([skip, h], dim=1))
        return torch.sigmoid(self.out(h))


class CoordUNet(nn.Module):
    """U-Net with normalized coordinate channels for sequence-index-aware SCGI."""

    def __init__(self, base_channels: int = 16, depth: int = 4):
        super().__init__()
        self.unet = UNet(in_channels=3, out_channels=1, base_channels=base_channels, depth=depth)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b, _c, h, w = x.shape
        yy = torch.linspace(-1.0, 1.0, h, dtype=x.dtype, device=x.device).reshape(1, 1, h, 1).expand(b, 1, h, w)
        xx = torch.linspace(-1.0, 1.0, w, dtype=x.dtype, device=x.device).reshape(1, 1, 1, w).expand(b, 1, h, w)
        return self.unet(torch.cat([x, yy, xx], dim=1))


def _row_max_normalize_image(x: torch.Tensor) -> torch.Tensor:
    return x / x.amax(dim=(2, 3), keepdim=True).clamp_min(1e-8)


class GainCorrectorUNet(nn.Module):
    """Predict a smooth gain map and output normalized ``measurement / gain``."""

    def __init__(
        self,
        base_channels: int = 16,
        depth: int = 4,
        use_coord_channels: bool = True,
        gain_min: float = 1.0e-4,
        gain_max: float = 2.0,
    ):
        super().__init__()
        self.use_coord_channels = bool(use_coord_channels)
        self.gain_min = float(gain_min)
        self.gain_max = float(gain_max)
        if not (0.0 < self.gain_min < self.gain_max):
            raise ValueError("gain_min must be positive and smaller than gain_max.")
        if self.use_coord_channels:
            self.gain_net = CoordUNet(base_channels=base_channels, depth=depth)
        else:
            self.gain_net = UNet(in_channels=1, out_channels=1, base_channels=base_channels, depth=depth)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        raw_gain = self.gain_net(x)
        gain = self.gain_min + (self.gain_max - self.gain_min) * raw_gain
        corrected = x / gain.clamp_min(1e-6)
        return _row_max_normalize_image(corrected).clamp(0.0, 1.0)


class ExponentialResidualUNet(nn.Module):
    """Physics-informed exponential gain correction with a small U-Net residual."""

    def __init__(
        self,
        base_channels: int = 16,
        depth: int = 4,
        use_coord_channels: bool = True,
        lambda_min: float = 0.95,
        lambda_max: float = 1.05,
        residual_max_blend: float = 0.10,
        residual_blend_logit: float = -8.0,
    ):
        super().__init__()
        self.lambda_min = float(lambda_min)
        self.lambda_max = float(lambda_max)
        self.residual_max_blend = float(residual_max_blend)
        if not (0.0 < self.lambda_min <= self.lambda_max):
            raise ValueError("lambda_min must be positive and no larger than lambda_max.")
        self.use_coord_channels = bool(use_coord_channels)
        if self.use_coord_channels:
            self.residual_net = CoordUNet(base_channels=base_channels, depth=depth)
        else:
            self.residual_net = UNet(in_channels=1, out_channels=1, base_channels=base_channels, depth=depth)
        self.residual_blend_logit = nn.Parameter(torch.tensor(float(residual_blend_logit)))

    def _exponential_base(self, x: torch.Tensor) -> torch.Tensor:
        b, _c, h, w = x.shape
        rows = x.reshape(b, h * w).clamp_min(1.0e-8)
        n = torch.arange(rows.shape[-1], dtype=torch.float64, device=rows.device)
        centered_n = n - n.mean()
        log_rows = torch.log(rows.to(dtype=torch.float64))
        centered_log = log_rows - log_rows.mean(dim=1, keepdim=True)
        beta = (centered_log * centered_n).sum(dim=1) / centered_n.pow(2).sum().clamp_min(1.0e-8)
        lambdas = torch.exp(beta).clamp(self.lambda_min, self.lambda_max)
        gains = torch.exp(torch.log(lambdas).unsqueeze(1) * n.unsqueeze(0)).to(dtype=x.dtype)
        corrected = rows / gains.clamp_min(1.0e-8)
        return _row_max_normalize_image(corrected.reshape(b, 1, h, w)).clamp(0.0, 1.0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        base = self._exponential_base(x)
        residual = self.residual_net(x)
        blend = torch.sigmoid(self.residual_blend_logit) * self.residual_max_blend
        return ((1.0 - blend) * base + blend * residual).clamp(0.0, 1.0)


def make_scgi_model(cfg: dict) -> UNet:
    scgi = cfg.get("scgi", {})
    active = cfg.get("active", {})
    data = cfg.get("data", {})
    base_channels = int(scgi.get("unet_base_channels", 16))
    depth = int(scgi.get("unet_depth", 4))
    kind = str(scgi.get("model_kind", "direct_unet"))
    if kind == "gain_unet":
        return GainCorrectorUNet(
            base_channels=base_channels,
            depth=depth,
            use_coord_channels=bool(scgi.get("use_coord_channels", False)),
            gain_min=float(scgi.get("gain_min", 1.0e-4)),
            gain_max=float(scgi.get("gain_max", 2.0)),
        )
    if kind in {"exponential_residual_unet", "analytic_residual_unet"}:
        return ExponentialResidualUNet(
            base_channels=base_channels,
            depth=depth,
            use_coord_channels=bool(scgi.get("use_coord_channels", False)),
            lambda_min=float(scgi.get("lambda_min", active.get("lambda_min", data.get("lambda_min", 0.95)))),
            lambda_max=float(scgi.get("lambda_max", active.get("lambda_max", data.get("lambda_max", 1.05)))),
            residual_max_blend=float(scgi.get("residual_max_blend", 0.10)),
            residual_blend_logit=float(scgi.get("residual_blend_logit", -8.0)),
        )
    if bool(scgi.get("use_coord_channels", False)):
        return CoordUNet(base_channels=base_channels, depth=depth)
    return UNet(base_channels=base_channels, depth=depth)
