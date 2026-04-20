"""Route-loading and route-target helpers for VEHRON."""

from __future__ import annotations

import csv
from pathlib import Path

from vehron.resources import resolve_runtime_path


def load_drive_cycle_profile(project_root: Path, cycle_file: str | None) -> list[tuple[float, float]]:
    """Load a drive-cycle CSV into `(time_s, speed_ms)` tuples."""
    if not cycle_file:
        return [(0.0, 0.0)]

    path = Path(cycle_file)
    if not path.is_absolute():
        path = resolve_runtime_path(project_root, path)

    profile: list[tuple[float, float]] = []
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.reader(line for line in handle if not line.startswith("#"))
        for row in reader:
            if len(row) < 2:
                continue
            first = row[0].strip()
            second = row[1].strip()
            if first.lower() == "time_s" and second.lower() == "speed_kmh":
                continue
            t_s = float(first)
            speed_ms = float(second) / 3.6
            profile.append((t_s, speed_ms))

    if not profile:
        return [(0.0, 0.0)]
    return profile


def drive_cycle_target_speed(profile: list[tuple[float, float]], t_s: float) -> float:
    """Return the interpolated target speed in m/s for a repeated drive cycle."""
    if len(profile) == 1:
        return profile[0][1]

    cycle_duration_s = profile[-1][0]
    if cycle_duration_s <= 0:
        return profile[-1][1]

    t_mod = t_s % cycle_duration_s
    for idx in range(1, len(profile)):
        t0, v0 = profile[idx - 1]
        t1, v1 = profile[idx]
        if t_mod <= t1:
            ratio = 0.0 if t1 == t0 else (t_mod - t0) / (t1 - t0)
            return v0 + ratio * (v1 - v0)
    return profile[-1][1]
