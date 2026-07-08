from __future__ import annotations

import torch
from torch import nn
import torch.nn.functional as F


class LayerNorm2d(nn.Module):
    def __init__(self, channels: int, eps: float = 1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(1, channels, 1, 1))
        self.bias = nn.Parameter(torch.zeros(1, channels, 1, 1))
        self.eps = eps

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        mean = x.mean(dim=1, keepdim=True)
        var = (x - mean).pow(2).mean(dim=1, keepdim=True)
        return (x - mean) / torch.sqrt(var + self.eps) * self.weight + self.bias


class SimpleGate(nn.Module):
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        a, b = x.chunk(2, dim=1)
        return a * b


class SCA(nn.Module):
    def __init__(self, channels: int):
        super().__init__()
        self.conv = nn.Conv2d(channels, channels, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x * self.conv(F.adaptive_avg_pool2d(x, 1))


class NAFBlock(nn.Module):
    def __init__(self, channels: int):
        super().__init__()
        dw = channels * 2
        self.norm1 = LayerNorm2d(channels)
        self.conv1 = nn.Conv2d(channels, dw, 1)
        self.dconv = nn.Conv2d(dw, dw, 3, padding=1, groups=dw)
        self.sg = SimpleGate()
        self.sca = SCA(channels)
        self.conv2 = nn.Conv2d(channels, channels, 1)
        self.norm2 = LayerNorm2d(channels)
        self.ffn1 = nn.Conv2d(channels, dw, 1)
        self.ffn2 = nn.Conv2d(channels, channels, 1)
        self.beta = nn.Parameter(torch.zeros(1, channels, 1, 1))
        self.gamma = nn.Parameter(torch.zeros(1, channels, 1, 1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = self.conv1(self.norm1(x))
        y = self.dconv(y)
        y = self.sg(y)
        y = self.sca(y)
        y = self.conv2(y)
        x = x + y * self.beta
        y = self.ffn1(self.norm2(x))
        y = self.sg(y)
        y = self.ffn2(y)
        return x + y * self.gamma


class TinyNAFNet(nn.Module):
    def __init__(self, channels: int = 24, blocks: int = 3):
        super().__init__()
        self.intro = nn.Conv2d(1, channels, 3, padding=1)
        self.blocks = nn.Sequential(*[NAFBlock(channels) for _ in range(blocks)])
        self.ending = nn.Conv2d(channels, 1, 3, padding=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = self.ending(self.blocks(self.intro(x)))
        return (x + 0.1 * torch.tanh(y)).clamp(0.0, 1.0)
