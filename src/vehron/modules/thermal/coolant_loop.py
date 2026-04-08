"""Simple coolant loop thermal equalization model."""

from __future__ import annotations

from vehron.modules.base import BaseModule
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class CoolantLoopModel(BaseModule):
    def initialize(self, dt: float) -> None:
        self._state = {"t_target_k": 0.0}
        self.t = 0.0

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        tau_s = float(self.params.get("tau_s", 900.0))
        t_target_k = 0.5 * (sim_state.t_batt_k + sim_state.t_motor_k)
        t_coolant_next_k = sim_state.t_coolant_k + (t_target_k - sim_state.t_coolant_k) * dt / tau_s
        self._state = {"t_target_k": t_target_k}
        self.t += dt
        return ModuleOutputs(t_coolant_k=t_coolant_next_k)

    def get_state(self) -> dict:
        return dict(self._state)

    def validate_params(self) -> None:
        if float(self.params.get("tau_s", 0.0)) <= 0:
            raise ValueError("coolant_loop.tau_s must be > 0")
