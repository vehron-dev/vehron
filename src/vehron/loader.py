"""YAML loader and validation helpers."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError as PydanticValidationError

from vehron.constants import CELSIUS_TO_KELVIN, KMH_TO_MS
from vehron.exceptions import ValidationError
from vehron.schemas.testcase_schema import TestcaseConfig
from vehron.schemas.vehicle_schema import VehicleConfig


class ConfigLoader:
    """Loads and validates vehicle and testcase YAML files."""

    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path.cwd()

    def _read_yaml(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            raise ValidationError(f"Config file not found: {path}")
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        if not isinstance(data, dict):
            raise ValidationError(f"Expected top-level mapping in {path}")
        return data

    @staticmethod
    def _to_plain_dict(model: Any) -> dict[str, Any]:
        return model.model_dump(mode="python")

    def load_vehicle(self, path: str | Path) -> dict[str, Any]:
        yaml_path = Path(path)
        raw = self._read_yaml(yaml_path)
        try:
            vehicle = VehicleConfig.model_validate(raw)
        except PydanticValidationError as exc:
            raise ValidationError(f"Vehicle config validation failed: {exc}") from exc
        return self._to_plain_dict(vehicle)

    def load_testcase(self, path: str | Path) -> dict[str, Any]:
        yaml_path = Path(path)
        raw = self._read_yaml(yaml_path)
        try:
            testcase = TestcaseConfig.model_validate(raw)
        except PydanticValidationError as exc:
            raise ValidationError(f"Testcase config validation failed: {exc}") from exc
        testcase_dict = self._to_plain_dict(testcase)
        return self._apply_boundary_conversions(testcase_dict)

    @staticmethod
    def _apply_boundary_conversions(testcase: dict[str, Any]) -> dict[str, Any]:
        env = testcase["environment"]
        route = testcase["route"]

        ambient_temp_k = env["ambient_temp_c"] + CELSIUS_TO_KELVIN
        target_speed_ms = route["target_speed_kmh"] * KMH_TO_MS
        grade_rad = math.atan(route["grade_pct"] / 100.0)

        testcase["_internal"] = {
            "ambient_temp_k": ambient_temp_k,
            "target_speed_ms": target_speed_ms,
            "grade_rad": grade_rad,
        }
        return testcase

    def load(self, vehicle_path: str | Path, testcase_path: str | Path) -> tuple[dict[str, Any], dict[str, Any]]:
        vehicle = self.load_vehicle(vehicle_path)
        testcase = self.load_testcase(testcase_path)
        return vehicle, testcase
