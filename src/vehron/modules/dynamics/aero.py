"""Aerodynamic drag helper model."""

from __future__ import annotations

from vehron.constants import AIR_DENSITY_KGM3
from vehron.modules.base import BaseModule
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class AeroDragModel(BaseModule):
    def initialize(self, dt: float) -> None:
        self._state = {"drag_force_n": 0.0, "drag_power_w": 0.0}
        self.t = 0.0

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        cd = float(self.params["drag_coefficient"])
        area_m2 = float(self.params["frontal_area_m2"])
        wind_speed_ms = float(self.params.get("wind_speed_ms", 0.0))

        rel_speed_ms = max(sim_state.v_ms - wind_speed_ms, 0.0)
        drag_force_n = 0.5 * AIR_DENSITY_KGM3 * cd * area_m2 * rel_speed_ms * rel_speed_ms
        drag_power_w = drag_force_n * rel_speed_ms

        self._state = {"drag_force_n": drag_force_n, "drag_power_w": drag_power_w}
        self.t += dt
        return ModuleOutputs()

    def get_state(self) -> dict:
        return dict(self._state)

    def validate_params(self) -> None:
        if float(self.params.get("drag_coefficient", 0.0)) <= 0:
            raise ValueError("drag_coefficient must be > 0")
        if float(self.params.get("frontal_area_m2", 0.0)) <= 0:
            raise ValueError("frontal_area_m2 must be > 0")
