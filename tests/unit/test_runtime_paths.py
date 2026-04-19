from pathlib import Path

from vehron.resources import package_data_root, resolve_runtime_path


def test_resolve_runtime_path_prefers_project_root_when_present(project_root: Path):
    resolved = resolve_runtime_path(project_root, "docs/examples/custom_drive_cycle.csv")
    assert resolved == project_root / "docs/examples/custom_drive_cycle.csv"


def test_resolve_runtime_path_falls_back_to_packaged_data(tmp_path: Path):
    resolved = resolve_runtime_path(tmp_path, "data/drive_cycles/wltp_class3.csv")
    assert resolved == package_data_root() / "data/drive_cycles/wltp_class3.csv"
