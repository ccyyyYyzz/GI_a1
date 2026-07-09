from __future__ import annotations

import json
from pathlib import Path
import time
from typing import Any

import pandas as pd


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def read_completed_unit_indexes(path: Path) -> set[int]:
    if not path.exists():
        return set()
    try:
        df = pd.read_csv(path, usecols=["unit_index"])
    except (FileNotFoundError, ValueError, pd.errors.EmptyDataError):
        return set()
    return {int(value) for value in df["unit_index"].dropna().unique()}


def append_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    frame = pd.DataFrame(rows)
    frame.to_csv(path, mode="a", header=not path.exists(), index=False)


def write_progress(
    out_dir: Path,
    *,
    state: str,
    start_time: float,
    completed_units: int,
    selected_units: int,
    total_units: int,
    last_unit_index: int | None,
    extra: dict[str, Any] | None = None,
) -> None:
    elapsed = time.time() - start_time
    payload: dict[str, Any] = {
        "state": state,
        "elapsed_seconds": round(elapsed, 3),
        "completed_units": int(completed_units),
        "selected_units": int(selected_units),
        "total_units": int(total_units),
        "last_unit_index": None if last_unit_index is None else int(last_unit_index),
    }
    if selected_units:
        payload["selected_fraction_complete"] = completed_units / selected_units
    if extra:
        payload.update(extra)
    write_json_atomic(out_dir / "progress.json", payload)
