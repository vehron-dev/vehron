from __future__ import annotations

import json
from pathlib import Path

import yaml
from click.testing import CliRunner

from vehron.runner import cli


def _extract_case_dir_from_output(output: str) -> Path:
    for line in output.splitlines():
        if line.startswith("case_dir="):
            return Path(line.split("=", 1)[1].strip())
    raise AssertionError("CLI output did not include case_dir=...")


def test_init_with_named_directory_creates_case_files(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(cli, ["init", "hvac-design"], input="\n\n")

    assert result.exit_code == 0, result.output
    case_dir = tmp_path / "hvac-design"
    assert (case_dir / ".vehron-case").exists()
    assert (case_dir / "README.md").exists()
    assert (case_dir / "vehicle.yaml").exists()
    assert (case_dir / "testcase.yaml").exists()
    assert (case_dir / "output").is_dir()

    marker = yaml.safe_load((case_dir / ".vehron-case").read_text(encoding="utf-8"))
    assert marker["case_name"] == "hvac-design"


def test_init_without_name_initialises_current_directory(tmp_path: Path, monkeypatch):
    case_dir = tmp_path / "project-study"
    case_dir.mkdir()
    monkeypatch.chdir(case_dir)
    runner = CliRunner()

    result = runner.invoke(cli, ["init"], input="\n\n")

    assert result.exit_code == 0, result.output
    marker = yaml.safe_load((case_dir / ".vehron-case").read_text(encoding="utf-8"))
    assert marker["case_name"] == "project-study"


def test_reinit_with_no_response_makes_no_changes(tmp_path: Path, monkeypatch):
    case_dir = tmp_path / "project-study"
    case_dir.mkdir()
    monkeypatch.chdir(case_dir)
    runner = CliRunner()
    first = runner.invoke(cli, ["init"], input="\n\n")
    assert first.exit_code == 0, first.output
    original_marker = (case_dir / ".vehron-case").read_text(encoding="utf-8")

    second = runner.invoke(cli, ["init"], input="n\n")

    assert second.exit_code == 0, second.output
    assert "Aborted." in second.output
    assert (case_dir / ".vehron-case").read_text(encoding="utf-8") == original_marker


def test_reinit_with_yes_response_overwrites_files(tmp_path: Path, monkeypatch):
    case_dir = tmp_path / "project-study"
    case_dir.mkdir()
    monkeypatch.chdir(case_dir)
    runner = CliRunner()
    first = runner.invoke(cli, ["init"], input="\n\n")
    assert first.exit_code == 0, first.output
    (case_dir / "vehicle.yaml").write_text("changed: true\n", encoding="utf-8")

    second = runner.invoke(cli, ["init"], input="y\n\n\n")

    assert second.exit_code == 0, second.output
    assert "changed: true" not in (case_dir / "vehicle.yaml").read_text(encoding="utf-8")


def test_run_with_case_resolves_inputs_and_writes_inside_case_dir(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    init_result = runner.invoke(cli, ["init", "veh-case-1"], input="\n\n")
    assert init_result.exit_code == 0, init_result.output
    case_dir = tmp_path / "veh-case-1"

    result = runner.invoke(cli, ["run", "--case", str(case_dir)])

    assert result.exit_code == 0, result.output
    output_case_dir = _extract_case_dir_from_output(result.output)
    assert output_case_dir.parent == case_dir / "output"
    assert (output_case_dir / "summary.json").exists()
    summary = json.loads((output_case_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["distance_km"] > 0.0


def test_run_with_case_and_vehicle_flag_raises_clear_error(tmp_path: Path, monkeypatch, project_root: Path):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    init_result = runner.invoke(cli, ["init", "veh-case-1"], input="\n\n")
    assert init_result.exit_code == 0, init_result.output
    vehicle_path = project_root / "src/vehron/archetypes/bev_car_sedan.yaml"

    result = runner.invoke(
        cli,
        ["run", "--case", str(tmp_path / "veh-case-1"), "--vehicle", str(vehicle_path)],
    )

    assert result.exit_code != 0
    assert "--case cannot be combined with --vehicle or --testcase." in result.output
