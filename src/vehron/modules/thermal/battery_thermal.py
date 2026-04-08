"""Simple first-order battery thermal model."""

from __future__ import annotations

from vehron.modules.base import BaseModule
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class BatteryThermalModel(BaseModule):
    def initialize(self, dt: float) -> None:
        self._state = {"q_loss_w": 0.0}
        self.t = 0.0

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        tau_s = float(self.params.get("tau_s", 600.0))
        q_loss_w = abs(sim_state.i_batt_a) * 3.0
        t_next_k = sim_state.t_batt_k + (sim_state.t_ambient_k - sim_state.t_batt_k) * dt / tau_s + q_loss_w * 2e-5 * dt
        self._state = {"q_loss_w": q_loss_w}
        self.t += dt
        return ModuleOutputs(t_batt_k=t_next_k)

    def get_state(self) -> dict:
        return dict(self._state)

    def validate_params(self) -> None:
        if float(self.params.get("tau_s", 0.0)) <= 0:
            raise ValueError("battery_thermal.tau_s must be > 0")
