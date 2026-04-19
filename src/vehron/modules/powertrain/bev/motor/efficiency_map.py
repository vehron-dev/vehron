"""CSV-backed efficiency-map motor model."""

from __future__ import annotations

import csv
from pathlib import Path

from vehron.modules.powertrain.bev.motor.analytical import AnalyticalMotorModel
from vehron.resources import resolve_runtime_path


class EfficiencyMapMotorModel(AnalyticalMotorModel):
    def initialize(self, dt: float) -> None:
        super().initialize(dt)
        self._eta_map: list[tuple[float, float, float]] = []

        map_file = self.params.get("map_file")
        if map_file:
            project_root = Path(self.params.get("project_root", Path.cwd()))
            path = resolve_runtime_path(project_root, Path(map_file))
            if path.exists():
                with path.open("r", encoding="utf-8") as handle:
                    reader = csv.reader(line for line in handle if not line.startswith("#"))
                    for row in reader:
                        if len(row) >= 3:
                            self._eta_map.append((float(row[0]), float(row[1]), float(row[2])))

    def _lookup_efficiency(self, speed_rpm: float, torque_nm: float) -> float | None:
        if not self._eta_map:
            return None
        best_dist = float("inf")
        best_eta = None
        for row_speed_rpm, row_torque_nm, row_eta in self._eta_map:
            dist = (row_speed_rpm - speed_rpm) ** 2 + (row_torque_nm - torque_nm) ** 2
            if dist < best_dist:
                best_dist = dist
                best_eta = row_eta
        return best_eta

    def step(self, sim_state, inputs, dt):
        outputs = super().step(sim_state, inputs, dt)
        speed_rpm = outputs.motor_speed_rads * 60.0 / (2.0 * 3.141592653589793)
        eta_map = self._lookup_efficiency(speed_rpm, abs(outputs.motor_torque_nm or 0.0))
        if eta_map is not None:
            eta = self._clamp(float(eta_map), 0.7, 0.98, "motor_efficiency_map")
            if (outputs.p_drive_w or 0.0) > 0 and (outputs.motor_efficiency or 1.0) > 0:
                mech_power_w = outputs.p_drive_w * (outputs.motor_efficiency or 1.0)
                outputs.p_drive_w = mech_power_w / eta
            outputs.motor_efficiency = eta
        return outputs
