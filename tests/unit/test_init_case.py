from __future__ import annotations

from pathlib import Path

import yaml

from vehron.init_case import (
    find_next_case_name,
    is_case_dir,
    is_inside_case_dir,
    write_case_dir,
)


def test_find_next_case_name_returns_first_when_no_cases_exist(tmp_path: Path):
    assert find_next_case_name(tmp_path) == "veh-case-1"


def test_find_next_case_name_skips_to_next_integer(tmp_path: Path):
    (tmp_path / "veh-case-1").mkdir()
    (tmp_path / "veh-case-2").mkdir()

    assert find_next_case_name(tmp_path) == "veh-case-3"


def test_is_case_dir_returns_true_when_marker_exists(tmp_path: Path):
    case_dir = tmp_path / "study"
    case_dir.mkdir()
    (case_dir / ".vehron-case").write_text("case_name: study\n", encoding="utf-8")

    assert is_case_dir(case_dir) is True


def test_is_case_dir_returns_false_without_marker(tmp_path: Path):
    case_dir = tmp_path / "study"
    case_dir.mkdir()

    assert is_case_dir(case_dir) is False


def test_is_inside_case_dir_checks_recent_parents(tmp_path: Path):
    case_dir = tmp_path / "study"
    case_dir.mkdir()
    (case_dir / ".vehron-case").write_text("case_name: study\n", encoding="utf-8")
    nested = case_dir / "a" / "b"
    nested.mkdir(parents=True)

    assert is_inside_case_dir(nested) is True
    assert is_inside_case_dir(tmp_path / "outside") is False


def test_write_case_dir_creates_expected_files(tmp_path: Path):
    case_dir = tmp_path / "hvac-design"

    write_case_dir(case_dir, "hvac-design", "bev_car_sedan", "flat_highway_100kmh")

    assert (case_dir / ".vehron-case").exists()
    assert (case_dir / "README.md").exists()
    assert (case_dir / "vehicle.yaml").exists()
    assert (case_dir / "testcase.yaml").exists()
    assert (case_dir / "output").is_dir()


def test_write_case_dir_populates_marker_and_readme(tmp_path: Path):
    case_dir = tmp_path / "hvac-design"

    write_case_dir(case_dir, "hvac-design", "bev_car_sedan", "flat_highway_100kmh")

    marker = yaml.safe_load((case_dir / ".vehron-case").read_text(encoding="utf-8"))
    readme = (case_dir / "README.md").read_text(encoding="utf-8")

    assert marker["case_name"] == "hvac-design"
    assert marker["archetype"] == "bev_car_sedan"
    assert marker["testcase"] == "flat_highway_100kmh"
    assert "vehron_version" in marker
    assert "created" in marker
    assert "# hvac-design" in readme
    assert "bev_car_sedan" in readme
