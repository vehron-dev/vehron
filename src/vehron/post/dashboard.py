"""Plot generation helpers for VEHRON case packages."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def generate_case_plots(output_dir: Path, rows: list[dict[str, Any]]) -> list[Path]:
    """Generate a compact default plot set for a simulation run."""
    output_dir.mkdir(parents=True, exist_ok=True)
    if not rows:
        return []

    os.environ.setdefault("MPLCONFIGDIR", "/tmp/vehron-mpl")

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    t_s = [float(row.get("t", 0.0)) for row in rows]
    v_kmh = [float(row.get("v_kmh", 0.0)) for row in rows]
    a_ms2 = [float(row.get("a_ms2", 0.0)) for row in rows]
    distance_km = [float(row.get("distance_km", 0.0)) for row in rows]
    soc_pct = [float(row.get("soc", 0.0)) * 100.0 for row in rows]
    idle_flag = [1.0 if abs(float(row.get("v_ms", 0.0))) < 0.1 else 0.0 for row in rows]

    t_amb_c = [float(row.get("t_ambient_c", 0.0)) for row in rows]
    t_batt_c = [float(row.get("t_batt_c", 0.0)) for row in rows]
    t_motor_c = [float(row.get("t_motor_c", 0.0)) for row in rows]
    t_coolant_c = [float(row.get("t_coolant_c", 0.0)) for row in rows]
    t_cabin_c = [float(row.get("t_cabin_c", 0.0)) for row in rows]

    created: list[Path] = []

    fig, axes = plt.subplots(3, 1, figsize=(11, 10), sharex=True)
    axes[0].plot(t_s, v_kmh, label="Velocity")
    axes[0].set_ylabel("km/h")
    axes[0].set_title("Velocity")
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(t_s, a_ms2, color="tab:orange", label="Acceleration")
    axes[1].set_ylabel("m/s²")
    axes[1].set_title("Acceleration")
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(t_s, distance_km, color="tab:green", label="Distance")
    axes[2].set_ylabel("km")
    axes[2].set_xlabel("Time [s]")
    axes[2].set_title("Distance")
    axes[2].grid(True, alpha=0.3)

    path = output_dir / "motion.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    created.append(path)

    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    axes[0].plot(t_s, soc_pct, color="tab:purple")
    axes[0].set_ylabel("SoC [%]")
    axes[0].set_title("State of Charge")
    axes[0].grid(True, alpha=0.3)

    axes[1].step(t_s, idle_flag, where="post", color="tab:red")
    axes[1].set_ylabel("Idle")
    axes[1].set_xlabel("Time [s]")
    axes[1].set_title("Idle State")
    axes[1].set_yticks([0, 1], labels=["moving", "idle"])
    axes[1].grid(True, alpha=0.3)

    path = output_dir / "soc_idle.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    created.append(path)

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(t_s, t_amb_c, label="T_amb")
    ax.plot(t_s, t_batt_c, label="T_batt")
    ax.plot(t_s, t_motor_c, label="T_motor")
    ax.plot(t_s, t_coolant_c, label="T_coolant")
    ax.plot(t_s, t_cabin_c, label="T_cabin")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Temperature [C]")
    ax.set_title("Vehicle Temperatures")
    ax.grid(True, alpha=0.3)
    ax.legend()

    path = output_dir / "temperatures.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    created.append(path)

    return created
