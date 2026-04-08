"""Simple inverter efficiency model."""

from __future__ import annotations

from vehron.modules.base import BaseModule
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class SimpleInverterModel(BaseModule):
    def initialize(self, dt: float) -> None:
        self._state = {"p_inverter_in_w": 0.0}
        self.t = 0.0

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        eta = float(self.params.get("efficiency", 0.97))
        eta = self._clamp(eta, 0.8, 0.999, "inverter_efficiency")

        p_drive_w = sim_state.p_drive_w
        if p_drive_w > 0:
            p_drive_dc_w = p_drive_w / eta
        else:
            p_drive_dc_w = 0.0

        self._state = {"p_inverter_in_w": p_drive_dc_w}
        self.t += dt

        return ModuleOutputs(inverter_efficiency=eta, p_drive_w=p_drive_dc_w)

    def get_state(self) -> dict:
        return dict(self._state)

    def validate_params(self) -> None:
        efficiency = float(self.params.get("efficiency", 0.97))
        if not (0 < efficiency <= 1):
            raise ValueError("inverter.efficiency must be in (0, 1]")
