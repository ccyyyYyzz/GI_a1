from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | Path = "config.yaml", profile: str | None = None) -> dict[str, Any]:
    cfg_path = Path(path)
    with cfg_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    selected = profile or cfg.get("profile", "smoke")
    if selected not in cfg["profiles"]:
        raise KeyError(f"Unknown profile {selected!r}. Available: {sorted(cfg['profiles'])}")
    merged = dict(cfg)
    merged["profile"] = selected
    merged["active"] = dict(cfg["profiles"][selected])
    return merged


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]

