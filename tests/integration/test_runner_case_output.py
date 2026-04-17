from __future__ import annotations

import json
from pathlib import Path

import yaml
from click.testing import CliRunner

from vehron.runner import cli


def test_run_cli_prints_spec_live_progress_and_writes_case_package(project_root: Path, monkeypatch, tmp_path: Path):
    vehicle_path = project_root / "src/vehron/archetypes/bev_car_sedan.yaml"
    testcase_path = tmp_path / "tiny_flat_highway.yaml"

    testcase = {
        "testcase": {
            "name": "Tiny Flat Highway",
            "description": "Short run for CLI output verification",
        },
        "environment": {
            "ambient_temp_c": 30.0,
            "wind_speed_ms": 0.0,
            "wind_angle_deg": 0.0,
            "solar_irradiance_wm2": 500.0,
        },
        "route": {
            "mode": "parametric",
            "distance_km": 0.2,
            "grade_pct": 0.0,
            "target_speed_kmh": 36.0,
        },
        "payload": {
            "passengers": 1,
            "cargo_kg": 0.0,
        },
        "simulation": {
            "dt_s": 0.5,
            "max_duration_s": 120.0,
            "stop_on_soc_min": True,
            "external_charging_power_kw": 0.0,
            "external_charging_start_s": 0.0,
            "external_charging_end_s": 0.0,
        },
        "outputs": {
            "time_series": True,
            "energy_audit": True,
            "plots": ["speed", "soc", "temperatures"],
            "report": True,
        },
    }
    testcase_path.write_text(yaml.safe_dump(testcase, sort_keys=False), encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "run",
            "--vehicle",
            str(vehicle_path),
            "--testcase",
            str(testcase_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "=== VEHRON Test Spec Sheet ===" in result.output
    assert "=== Run Start ===" in result.output
    assert "ITER step=1" in result.output
    assert "t_s=10.00" in result.output
    assert "distance_km=" in result.output
    assert "soc=" in result.output
    assert "T_amb=" in result.output
    assert "T_motor=" in result.output
    assert "case_dir=" in result.output
    assert "plots_generated=3" in result.output
    assert result.output.count("ITER ") < 10

    case_root = tmp_path / "output" / "cases"
    case_dirs = [path for path in case_root.iterdir() if path.is_dir()]
    assert len(case_dirs) == 1
    case_dir = case_dirs[0]

    assert (case_dir / "summary.json").exists()
    assert (case_dir / "timeseries.csv").exists()
    assert (case_dir / "vehicle.yaml").exists()
    assert (case_dir / "testcase.yaml").exists()
    assert (case_dir / "README.md").exists()
    assert (case_dir / "plots" / "motion.png").exists()
    assert (case_dir / "plots" / "soc_idle.png").exists()
    assert (case_dir / "plots" / "temperatures.png").exists()

    summary = json.loads((case_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["distance_km"] > 0.0
    assert 0.0 <= summary["soc_final"] <= 1.0
