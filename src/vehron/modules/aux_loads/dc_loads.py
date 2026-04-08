"""Auxiliary DC loads model."""

from __future__ import annotations

from vehron.modules.base import BaseModule
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class DcLoadsModel(BaseModule):
    RATE_DIVISOR: int = 10

    def initialize(self, dt: float) -> None:
        self._state = {"p_aux_w": 0.0}
        self.t = 0.0

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        p_aux_w = (
            float(self.params.get("headlights_w", 0.0))
            + float(self.params.get("adas_w", 0.0))
            + float(self.params.get("infotainment_w", 0.0))
            + float(self.params.get("power_steering_w", 0.0))
        )
        self._state = {"p_aux_w": p_aux_w}
        self.t += dt
        return ModuleOutputs(p_aux_w=p_aux_w)

    def get_state(self) -> dict:
        return dict(self._state)

    def validate_params(self) -> None:
        for key in ("headlights_w", "adas_w", "infotainment_w", "power_steering_w"):
            if float(self.params.get(key, 0.0)) < 0:
                raise ValueError(f"aux_loads.{key} must be >= 0")
