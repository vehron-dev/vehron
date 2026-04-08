"""Rolling resistance helper model."""

from __future__ import annotations

import math

from vehron.constants import GRAVITY_MS2
from vehron.modules.base import BaseModule
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class RollingResistanceModel(BaseModule):
    def initialize(self, dt: float) -> None:
        self._state = {"rolling_force_n": 0.0}
        self.t = 0.0

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        mass_kg = float(self.params["mass_kg"])
        c_rr = float(self.params["rolling_resistance_coeff"])
        speed_factor = 1.0 + 0.01 * max(sim_state.v_ms, 0.0)
        rolling_force_n = mass_kg * GRAVITY_MS2 * c_rr * math.cos(sim_state.grade_rad) * speed_factor
        self._state = {"rolling_force_n": rolling_force_n}
        self.t += dt
        return ModuleOutputs()

    def get_state(self) -> dict:
        return dict(self._state)

    def validate_params(self) -> None:
        if float(self.params.get("mass_kg", 0.0)) <= 0:
            raise ValueError("mass_kg must be > 0")
        if float(self.params.get("rolling_resistance_coeff", 0.0)) <= 0:
            raise ValueError("rolling_resistance_coeff must be > 0")
