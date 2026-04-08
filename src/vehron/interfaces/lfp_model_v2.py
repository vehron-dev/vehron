"""Integration hooks for the external LFP_model_v2 battery team workflow."""

from __future__ import annotations

import csv
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from vehron import __version__
from vehron.engine import SimulationResult


def apply_lfp_model_v2_feedback(
    vehicle_cfg: dict[str, Any],
    feedback_file: Path | None,
) -> tuple[dict[str, Any], list[str]]:
    """Apply optional battery parameter overrides from LFP_model_v2 feedback JSON."""
    if feedback_file is None:
        return vehicle_cfg, []

    payload = json.loads(feedback_file.read_text(encoding="utf-8"))
    if payload.get("model") != "LFP_model_v2":
        raise ValueError("feedback model must be 'LFP_model_v2'")

    out = deepcopy(vehicle_cfg)
    battery = out.setdefault("battery", {})
    overrides = payload.get("pack_overrides", {})

    allowed_keys = {
        "capacity_kwh",
        "internal_resistance_ohm",
        "soc_init",
        "soc_min",
        "soc_max",
        "max_charge_rate_c",
        "max_discharge_rate_c",
    }

    applied: list[str] = []
    for key, value in overrides.items():
        if key in allowed_keys:
            battery[key] = value
            applied.append(key)

    return out, applied


def export_lfp_model_v2_hook(
    *,
    result: SimulationResult,
    vehicle_cfg: dict[str, Any],
    testcase_cfg: dict[str, Any],
    export_dir: Path,
    feedback_applied: list[str] | None = None,
) -> Path:
    """Export VEHRON run traces in a stable interface format for LFP_model_v2."""
    export_dir.mkdir(parents=True, exist_ok=True)

    csv_path = export_dir / "lfp_model_v2_input.csv"
    fieldnames = [
        "time_s",
        "step_count",
        "speed_kmh",
        "soc",
        "v_batt_v",
        "i_batt_a",
        "p_batt_w",
        "p_drive_w",
        "p_regen_w",
        "p_hvac_w",
        "p_aux_w",
        "t_batt_k",
        "t_ambient_k",
        "t_coolant_k",
        "distance_m",
    ]

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in result.time_series:
            writer.writerow(
                {
                    "time_s": row["t"],
                    "step_count": row["step_count"],
                    "speed_kmh": row["v_kmh"],
                    "soc": row["soc"],
                    "v_batt_v": row["v_batt_v"],
                    "i_batt_a": row["i_batt_a"],
                    "p_batt_w": row["p_batt_w"],
                    "p_drive_w": row["p_drive_w"],
                    "p_regen_w": row["p_regen_w"],
                    "p_hvac_w": row["p_hvac_w"],
                    "p_aux_w": row["p_aux_w"],
                    "t_batt_k": row["t_batt_k"],
                    "t_ambient_k": row["t_ambient_k"],
                    "t_coolant_k": row["t_coolant_k"],
                    "distance_m": row["distance_m"],
                }
            )

    manifest = {
        "model_interface": "LFP_model_v2",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "vehron_version": __version__,
        "vehicle_name": vehicle_cfg.get("vehicle", {}).get("name"),
        "vehicle_powertrain": vehicle_cfg.get("vehicle", {}).get("powertrain"),
        "testcase_name": testcase_cfg.get("testcase", {}).get("name"),
        "route_mode": testcase_cfg.get("route", {}).get("mode"),
        "master_dt_s": testcase_cfg.get("simulation", {}).get("dt_s"),
        "rows": len(result.time_series),
        "feedback_applied": feedback_applied or [],
        "files": {
            "timeseries_csv": "lfp_model_v2_input.csv",
        },
        "units": {
            "time_s": "s",
            "speed_kmh": "km/h",
            "soc": "-",
            "v_batt_v": "V",
            "i_batt_a": "A (positive discharge, negative charge)",
            "p_batt_w": "W (positive discharge, negative charge)",
            "p_drive_w": "W",
            "p_regen_w": "W (positive recovered)",
            "p_hvac_w": "W",
            "p_aux_w": "W",
            "t_batt_k": "K",
            "t_ambient_k": "K",
            "t_coolant_k": "K",
            "distance_m": "m",
        },
    }

    (export_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return export_dir
