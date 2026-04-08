"""Road grade force helper model."""

from __future__ import annotations

import math

from vehron.constants import GRAVITY_MS2
from vehron.modules.base import BaseModule
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class GradeForceModel(BaseModule):
    def initialize(self, dt: float) -> None:
        self._state = {"grade_force_n": 0.0}
        self.t = 0.0

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        mass_kg = float(self.params["mass_kg"])
        grade_force_n = mass_kg * GRAVITY_MS2 * math.sin(sim_state.grade_rad)
        self._state = {"grade_force_n": grade_force_n}
        self.t += dt
        return ModuleOutputs()

    def get_state(self) -> dict:
        return dict(self._state)

    def validate_params(self) -> None:
        if float(self.params.get("mass_kg", 0.0)) <= 0:
            raise ValueError("mass_kg must be > 0")
