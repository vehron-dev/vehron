"""Time-series export helpers for VEHRON case packages."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def write_timeseries_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write the simulation time series to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
