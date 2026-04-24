"""Case directory helpers for the VEHRON CLI."""

from __future__ import annotations

from datetime import datetime
from importlib.metadata import version
from pathlib import Path

import yaml

from vehron.resources import list_packaged_archetypes, list_packaged_testcases

CASE_MARKER = ".vehron-case"


def find_next_case_name(cwd: Path) -> str:
    """Return the next available veh-case-N name under the given directory."""
    next_index = 1
    for path in cwd.iterdir():
        if not path.is_dir():
            continue
        stem = path.name
        if not stem.startswith("veh-case-"):
            continue
        suffix = stem.removeprefix("veh-case-")
        if suffix.isdigit():
            next_index = max(next_index, int(suffix) + 1)
    return f"veh-case-{next_index}"


def is_case_dir(path: Path) -> bool:
    """Return True when the directory contains a VEHRON case marker."""
    return path.is_dir() and (path / CASE_MARKER).is_file()


def is_inside_case_dir(path: Path, depth: int = 3) -> bool:
    """Return True when the path or a recent parent is a VEHRON case dir."""
    current = path
    for _ in range(depth + 1):
        if is_case_dir(current):
            return True
        if current.parent == current:
            break
        current = current.parent
    return False


def write_case_dir(path: Path, name: str, archetype: str, testcase: str) -> None:
    """Create or refresh the standard VEHRON case directory layout."""
    path.mkdir(parents=True, exist_ok=True)
    marker = {
        "vehron_version": version("vehron"),
        "case_name": name,
        "archetype": archetype,
        "testcase": testcase,
        "created": datetime.now().isoformat(timespec="seconds"),
    }
    (path / CASE_MARKER).write_text(yaml.safe_dump(marker, sort_keys=False), encoding="utf-8")
    (path / "README.md").write_text(_build_case_readme(name, archetype, testcase, marker["vehron_version"]), encoding="utf-8")
    (path / "vehicle.yaml").write_text(_packaged_yaml_text("archetype", archetype), encoding="utf-8")
    (path / "testcase.yaml").write_text(_packaged_yaml_text("testcase", testcase), encoding="utf-8")
    (path / "output").mkdir(exist_ok=True)


def list_archetypes() -> list[str]:
    """List packaged archetype stems."""
    return list_packaged_archetypes()


def list_testcases() -> list[str]:
    """List packaged testcase stems."""
    return list_packaged_testcases()


def read_case_metadata(path: Path) -> dict[str, object]:
    """Read the marker file from an existing VEHRON case directory."""
    marker_path = path / CASE_MARKER
    data = yaml.safe_load(marker_path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _packaged_yaml_text(kind: str, stem: str) -> str:
    package_root = Path(__file__).resolve().parent
    if kind == "archetype":
        path = package_root / "archetypes" / f"{stem}.yaml"
    else:
        path = package_root / "testcases" / f"{stem}.yaml"
    return path.read_text(encoding="utf-8")


def _build_case_readme(name: str, archetype: str, testcase: str, vehron_version: str) -> str:
    created = datetime.now().date().isoformat()
    return (
        f"# {name}\n\n"
        f"Initialised with VEHRON {vehron_version} on {created}.\n\n"
        "## Archetype\n\n"
        f"{archetype}\n\n"
        "## Testcase\n\n"
        f"{testcase}\n\n"
        "## Notes\n\n"
        "<!-- Describe the design intent for this case here. -->\n"
    )
