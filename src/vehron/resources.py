"""Packaged resource helpers for VEHRON."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

import yaml


def package_data_root() -> Path:
    """Return a filesystem path to the packaged VEHRON data directory."""
    return Path(files("vehron"))


def resolve_runtime_path(project_root: Path, path_value: str | Path) -> Path:
    """Resolve a runtime asset path from the project root or packaged data root."""
    path = Path(path_value)
    if path.is_absolute():
        return path

    project_candidate = project_root / path
    if project_candidate.exists():
        return project_candidate

    package_candidate = package_data_root() / path
    if package_candidate.exists():
        return package_candidate

    return project_candidate


def _valid_yaml_file_stems(directory: Path) -> list[str]:
    valid: list[str] = []
    for path in sorted(directory.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        if isinstance(data, dict):
            valid.append(path.stem)
    return valid


def _valid_testcase_file_stems(directory: Path) -> list[str]:
    valid: list[str] = []
    package_root = package_data_root()
    for path in sorted(directory.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        if not isinstance(data, dict):
            continue
        route = data.get("route", {})
        if isinstance(route, dict):
            drive_cycle_file = route.get("drive_cycle_file")
            if isinstance(drive_cycle_file, str) and drive_cycle_file:
                if not (package_root / drive_cycle_file).exists():
                    continue
        valid.append(path.stem)
    return valid


def packaged_archetype_path(name: str) -> Path:
    """Resolve a packaged vehicle archetype by file stem or filename."""
    filename = name if name.endswith(".yaml") else f"{name}.yaml"
    path = package_data_root() / "archetypes" / filename
    if not path.exists():
        available = ", ".join(sorted(p.stem for p in (package_data_root() / "archetypes").glob("*.yaml")))
        raise FileNotFoundError(
            f"Unknown packaged vehicle archetype '{name}'. Available archetypes: {available}"
        )
    return path


def packaged_testcase_path(name: str) -> Path:
    """Resolve a packaged testcase by file stem or filename."""
    filename = name if name.endswith(".yaml") else f"{name}.yaml"
    path = package_data_root() / "testcases" / filename
    if not path.exists():
        available = ", ".join(sorted(p.stem for p in (package_data_root() / "testcases").glob("*.yaml")))
        raise FileNotFoundError(
            f"Unknown packaged testcase '{name}'. Available testcases: {available}"
        )
    return path


def list_packaged_archetypes() -> list[str]:
    """List packaged vehicle archetype file stems."""
    return _valid_yaml_file_stems(package_data_root() / "archetypes")


def list_packaged_testcases() -> list[str]:
    """List packaged testcase file stems."""
    return _valid_testcase_file_stems(package_data_root() / "testcases")
