"""CLI entrypoints for VEHRON."""

from __future__ import annotations

from datetime import datetime
import math
from pathlib import Path
from typing import Any

import click

from vehron.engine import SimEngine
from vehron.loader import ConfigLoader
from vehron.post.dashboard import generate_case_plots
from vehron.post.reports import make_case_name, write_case_package
from vehron.resources import (
    list_packaged_archetypes,
    list_packaged_testcases,
    package_data_root,
    packaged_archetype_path,
    packaged_testcase_path,
)


@click.group()
def cli() -> None:
    """VEHRON command-line interface."""


@cli.command("list-examples")
def list_examples_cmd() -> None:
    """List packaged archetypes and testcases that can be used with run-example."""
    click.echo("Packaged vehicle archetypes:")
    for name in list_packaged_archetypes():
        click.echo(f"- {name}")
    click.echo("")
    click.echo("Packaged testcases:")
    for name in list_packaged_testcases():
        click.echo(f"- {name}")


@cli.command("run")
@click.option("--vehicle", "vehicle_path", required=True, type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--testcase", "testcase_path", required=True, type=click.Path(exists=True, dir_okay=False, path_type=Path))
def run_cmd(
    vehicle_path: Path,
    testcase_path: Path,
) -> None:
    """Run a simulation and print a short summary."""
    loader = ConfigLoader(project_root=Path.cwd())
    vehicle_source = vehicle_path.read_text(encoding="utf-8")
    testcase_source = testcase_path.read_text(encoding="utf-8")
    vehicle_cfg, testcase_cfg = loader.load(vehicle_path, testcase_path)
    engine = SimEngine(vehicle_cfg, testcase_cfg, project_root=Path.cwd())
    click.echo(_render_spec_sheet(vehicle_cfg, testcase_cfg))
    result = engine.run(observer=_live_progress_reporter)

    final = result.final_state
    click.echo(f"steps={final.step_count}")
    click.echo(f"distance_km={final.distance_m / 1000.0:.3f}")
    click.echo(f"final_soc={final.soc:.4f}")
    click.echo(f"energy_wh={final.total_energy_consumed_wh():.2f}")

    case_root = Path.cwd() / "output" / "cases"
    case_dir = case_root / make_case_name(vehicle_cfg, testcase_cfg, when=datetime.now())
    summary = write_case_package(
        case_dir=case_dir,
        result=result,
        vehicle_cfg=vehicle_cfg,
        testcase_cfg=testcase_cfg,
        vehicle_source=vehicle_source,
        testcase_source=testcase_source,
    )
    plot_paths = generate_case_plots(case_dir / "plots", result.time_series)
    click.echo(f"case_dir={case_dir}")
    click.echo(f"plots_generated={len(plot_paths)}")
    click.echo(f"idle_time_s={summary['idle_time_s']:.2f}")


@cli.command("run-example")
@click.option("--vehicle", "vehicle_name", required=True, type=str)
@click.option("--testcase", "testcase_name", required=True, type=str)
def run_example_cmd(vehicle_name: str, testcase_name: str) -> None:
    """Run a packaged example vehicle and testcase."""
    project_root = package_data_root()
    vehicle_path = packaged_archetype_path(vehicle_name)
    testcase_path = packaged_testcase_path(testcase_name)
    _run_case(
        project_root=project_root,
        vehicle_path=vehicle_path,
        testcase_path=testcase_path,
    )


def _run_case(project_root: Path, vehicle_path: Path, testcase_path: Path) -> None:
    """Execute a VEHRON run for the given inputs and write the case package."""
    loader = ConfigLoader(project_root=project_root)
    vehicle_source = vehicle_path.read_text(encoding="utf-8")
    testcase_source = testcase_path.read_text(encoding="utf-8")
    vehicle_cfg, testcase_cfg = loader.load(vehicle_path, testcase_path)
    engine = SimEngine(vehicle_cfg, testcase_cfg, project_root=project_root)
    click.echo(_render_spec_sheet(vehicle_cfg, testcase_cfg))
    result = engine.run(observer=_live_progress_reporter)

    final = result.final_state
    click.echo(f"steps={final.step_count}")
    click.echo(f"distance_km={final.distance_m / 1000.0:.3f}")
    click.echo(f"final_soc={final.soc:.4f}")
    click.echo(f"energy_wh={final.total_energy_consumed_wh():.2f}")

    case_root = Path.cwd() / "output" / "cases"
    case_dir = case_root / make_case_name(vehicle_cfg, testcase_cfg, when=datetime.now())
    summary = write_case_package(
        case_dir=case_dir,
        result=result,
        vehicle_cfg=vehicle_cfg,
        testcase_cfg=testcase_cfg,
        vehicle_source=vehicle_source,
        testcase_source=testcase_source,
    )
    plot_paths = generate_case_plots(case_dir / "plots", result.time_series)
    click.echo(f"case_dir={case_dir}")
    click.echo(f"plots_generated={len(plot_paths)}")
    click.echo(f"idle_time_s={summary['idle_time_s']:.2f}")

def _render_spec_sheet(vehicle_cfg: dict[str, Any], testcase_cfg: dict[str, Any]) -> str:
    vehicle = vehicle_cfg.get("vehicle", {})
    battery = vehicle_cfg.get("battery", {})
    route = testcase_cfg.get("route", {})
    env = testcase_cfg.get("environment", {})
    sim = testcase_cfg.get("simulation", {})
    payload = testcase_cfg.get("payload", {})
    return "\n".join(
        [
            "=== VEHRON Test Spec Sheet ===",
            f"vehicle={vehicle.get('name', 'unknown')} archetype={vehicle.get('archetype', 'unknown')} powertrain={vehicle.get('powertrain', 'unknown')}",
            f"testcase={testcase_cfg.get('testcase', {}).get('name', 'unknown')}",
            f"route_mode={route.get('mode', 'unknown')} distance_km={float(route.get('distance_km', 0.0)):.3f} target_speed_kmh={float(route.get('target_speed_kmh', 0.0)):.3f}",
            f"ambient_c={float(env.get('ambient_temp_c', 0.0)):.2f} wind_ms={float(env.get('wind_speed_ms', 0.0)):.2f} solar_wm2={float(env.get('solar_irradiance_wm2', 0.0)):.2f}",
            f"battery_model={battery.get('model', 'unknown')} capacity_kwh={float(battery.get('capacity_kwh', 0.0)):.3f} soc_init={float(battery.get('soc_init', 0.0)):.4f} soc_min={float(battery.get('soc_min', 0.0)):.4f} soc_max={float(battery.get('soc_max', 0.0)):.4f}",
            f"charge_rate_c={float(battery.get('max_charge_rate_c', 0.0)):.3f} discharge_rate_c={float(battery.get('max_discharge_rate_c', 0.0)):.3f}",
            f"simulation_dt_s={float(sim.get('dt_s', 0.0)):.3f} max_duration_s={float(sim.get('max_duration_s', 0.0)):.3f} stop_on_soc_min={bool(sim.get('stop_on_soc_min', True))}",
            f"payload_passengers={int(payload.get('passengers', 0))} cargo_kg={float(payload.get('cargo_kg', 0.0)):.2f}",
            "=== Run Start ===",
        ]
    )


def _live_progress_reporter(row: dict[str, Any], module_states: dict[str, dict[str, Any]]) -> None:
    if not _should_print_progress_row(row):
        return
    vehicle_temps = _format_vehicle_temperatures(row)
    plugin_temps = _format_plugin_temperatures(row, module_states)
    details = " ".join(vehicle_temps + plugin_temps)
    click.echo(
        "ITER "
        f"step={int(row.get('step_count', 0))} "
        f"t_s={float(row.get('t', 0.0)):.2f} "
        f"distance_km={float(row.get('distance_km', 0.0)):.3f} "
        f"v_kmh={float(row.get('v_kmh', 0.0)):.2f} "
        f"a_ms2={float(row.get('a_ms2', 0.0)):.3f} "
        f"soc={float(row.get('soc', 0.0)):.4f} "
        f"{details}".rstrip()
    )


def _format_vehicle_temperatures(row: dict[str, Any]) -> list[str]:
    ordered_fields = [
        ("T_amb", "t_ambient_c"),
        ("T_HVAC_condensor", None),
        ("T_radiator", None),
        ("T_motor", "t_motor_c"),
        ("T_batt", "t_batt_c"),
        ("T_coolant", "t_coolant_c"),
        ("T_cabin", "t_cabin_c"),
    ]
    rendered: list[str] = []
    for label, key in ordered_fields:
        if key is None:
            continue
        if key in row:
            rendered.append(f"{label}={float(row[key]):.2f}C")
    return rendered


def _format_plugin_temperatures(row: dict[str, Any], module_states: dict[str, dict[str, Any]]) -> list[str]:
    seen_keys = set(row.keys())
    rendered: list[str] = []
    for module_name, state in module_states.items():
        for key, value in state.items():
            if key in seen_keys:
                continue
            if not _looks_like_temperature_key(key):
                continue
            if not isinstance(value, (int, float)):
                continue
            rendered.append(f"{module_name}.{key}={float(value):.2f}")
    return rendered


def _looks_like_temperature_key(key: str) -> bool:
    lowered = key.lower()
    return lowered.startswith("t_") or "temp" in lowered


def _should_print_progress_row(row: dict[str, Any]) -> bool:
    step_count = int(row.get("step_count", 0))
    if step_count <= 1:
        return True
    t_s = float(row.get("t", 0.0))
    rounded_bucket = round(t_s / 10.0)
    return math.isclose(t_s, rounded_bucket * 10.0, abs_tol=1e-9)


if __name__ == "__main__":
    cli()
