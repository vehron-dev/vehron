"""Case report and artifact helpers for VEHRON."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from vehron.engine import SimulationResult
from vehron.post.timeseries import write_timeseries_csv


def make_case_name(vehicle_cfg: dict[str, Any], testcase_cfg: dict[str, Any], when: datetime | None = None) -> str:
    """Build a stable case package directory name."""
    when = when or datetime.now()
    powertrain = str(vehicle_cfg.get("vehicle", {}).get("powertrain", "vehicle")).strip().lower().replace(" ", "_")
    archetype = str(vehicle_cfg.get("vehicle", {}).get("archetype", "case")).strip().lower().replace(" ", "_")
    testcase_name = str(testcase_cfg.get("testcase", {}).get("name", "run")).strip().lower().replace(" ", "_")
    testcase_name = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in testcase_name)
    testcase_name = "_".join(part for part in testcase_name.split("_") if part)
    return f"case_{powertrain}_{archetype}_{testcase_name}_{when:%Y%m%d_%H%M%S}"


def build_summary(result: SimulationResult, vehicle_cfg: dict[str, Any], testcase_cfg: dict[str, Any]) -> dict[str, Any]:
    """Create a compact summary payload for the case package."""
    rows = result.time_series
    final = result.final_state
    initial_soc = float(vehicle_cfg.get("battery", {}).get("soc_init", 0.0))
    charge_steps = sum(1 for row in rows if float(row.get("i_batt_a", 0.0)) < 0.0)
    idle_steps = sum(1 for row in rows if abs(float(row.get("v_ms", 0.0))) < 0.1)
    dt_s = float(testcase_cfg.get("simulation", {}).get("dt_s", 0.0))

    return {
        "vehicle_name": vehicle_cfg.get("vehicle", {}).get("name"),
        "testcase_name": testcase_cfg.get("testcase", {}).get("name"),
        "route_mode": testcase_cfg.get("route", {}).get("mode"),
        "route_distance_km_target": testcase_cfg.get("route", {}).get("distance_km"),
        "steps": final.step_count,
        "sim_time_s": final.t,
        "distance_km": round(final.distance_m / 1000.0, 6),
        "soc_initial": initial_soc,
        "soc_final": final.soc,
        "soc_drop": initial_soc - final.soc,
        "energy_wh": final.total_energy_consumed_wh(),
        "regen_wh": final.e_regen_wh,
        "charge_steps": charge_steps,
        "idle_time_s": idle_steps * dt_s,
        "ambient_temp_c": final.t_ambient_k - 273.15,
        "battery_temp_c": final.t_batt_k - 273.15,
        "motor_temp_c": final.t_motor_k - 273.15,
        "coolant_temp_c": final.t_coolant_k - 273.15,
        "cabin_temp_c": final.t_cabin_k - 273.15,
    }


def write_case_package(
    case_dir: Path,
    result: SimulationResult,
    vehicle_cfg: dict[str, Any],
    testcase_cfg: dict[str, Any],
    vehicle_source: str,
    testcase_source: str,
) -> dict[str, Any]:
    """Write the standard VEHRON case package files."""
    case_dir.mkdir(parents=True, exist_ok=True)
    summary = build_summary(result, vehicle_cfg, testcase_cfg)

    write_timeseries_csv(case_dir / "timeseries.csv", result.time_series)
    (case_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (case_dir / "vehicle.yaml").write_text(vehicle_source, encoding="utf-8")
    (case_dir / "testcase.yaml").write_text(testcase_source, encoding="utf-8")
    (case_dir / "README.md").write_text(_build_case_readme(summary, vehicle_cfg, testcase_cfg), encoding="utf-8")
    (case_dir / "vehicle_resolved.yaml").write_text(yaml.safe_dump(vehicle_cfg, sort_keys=False), encoding="utf-8")
    (case_dir / "testcase_resolved.yaml").write_text(yaml.safe_dump(testcase_cfg, sort_keys=False), encoding="utf-8")
    return summary


def _build_case_readme(summary: dict[str, Any], vehicle_cfg: dict[str, Any], testcase_cfg: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# VEHRON Case Package",
            "",
            f"- Vehicle: {vehicle_cfg.get('vehicle', {}).get('name', 'unknown')}",
            f"- Testcase: {testcase_cfg.get('testcase', {}).get('name', 'unknown')}",
            f"- Route mode: {testcase_cfg.get('route', {}).get('mode', 'unknown')}",
            f"- Target distance: {testcase_cfg.get('route', {}).get('distance_km', 0.0)} km",
            f"- Final distance: {summary['distance_km']:.3f} km",
            f"- Initial SoC: {summary['soc_initial']:.4f}",
            f"- Final SoC: {summary['soc_final']:.4f}",
            f"- Net energy: {summary['energy_wh']:.2f} Wh",
            "",
            "Artifacts:",
            "- summary.json",
            "- timeseries.csv",
            "- plots/",
            "- vehicle.yaml / testcase.yaml",
            "- vehicle_resolved.yaml / testcase_resolved.yaml",
        ]
    ) + "\n"
