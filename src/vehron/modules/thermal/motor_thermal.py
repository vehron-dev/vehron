"""Simple first-order motor thermal model."""

from __future__ import annotations

from vehron.modules.base import BaseModule
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class MotorThermalModel(BaseModule):
    def initialize(self, dt: float) -> None:
        self._state = {"q_loss_w": 0.0}
        self.t = 0.0

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        tau_s = float(self.params.get("tau_s", 450.0))
        mech_power_w = abs(sim_state.motor_torque_nm * sim_state.motor_speed_rads)
        loss_frac = max(1.0 - sim_state.motor_efficiency, 0.0)
        q_loss_w = mech_power_w * loss_frac
        t_next_k = sim_state.t_motor_k + (sim_state.t_ambient_k - sim_state.t_motor_k) * dt / tau_s + q_loss_w * 1e-5 * dt
        self._state = {"q_loss_w": q_loss_w}
        self.t += dt
        return ModuleOutputs(t_motor_k=t_next_k)

    def get_state(self) -> dict:
        return dict(self._state)

    def validate_params(self) -> None:
        if float(self.params.get("tau_s", 0.0)) <= 0:
            raise ValueError("motor_thermal.tau_s must be > 0")
