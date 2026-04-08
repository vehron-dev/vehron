"""Simple first-order motor thermal model."""

from __future__ import annotations

from vehron.modules.base import BaseModule
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class MotorThermalModel(BaseModule):
    RATE_DIVISOR: int = 20

    def initialize(self, dt: float) -> None:
        self._state = {"q_loss_w": 0.0}
        self._sum_motor_torque_nm = 0.0
        self._sum_motor_speed_rads = 0.0
        self._sum_motor_efficiency = 0.0
        self._sum_t_motor_k = 0.0
        self._sum_t_ambient_k = 0.0
        self._samples = 0
        self._accumulated = {
            "motor_torque_nm": 0.0,
            "motor_speed_rads": 0.0,
            "motor_efficiency": 1.0,
            "t_motor_k": 298.15,
            "t_ambient_k": 298.15,
        }
        self.t = 0.0

    def accumulate(self, sim_state: SimState) -> None:
        self._sum_motor_torque_nm += sim_state.motor_torque_nm
        self._sum_motor_speed_rads += sim_state.motor_speed_rads
        self._sum_motor_efficiency += sim_state.motor_efficiency
        self._sum_t_motor_k += sim_state.t_motor_k
        self._sum_t_ambient_k += sim_state.t_ambient_k
        self._samples += 1

    def flush_accumulator(self) -> None:
        if self._samples <= 0:
            return
        inv = 1.0 / self._samples
        self._accumulated = {
            "motor_torque_nm": self._sum_motor_torque_nm * inv,
            "motor_speed_rads": self._sum_motor_speed_rads * inv,
            "motor_efficiency": self._sum_motor_efficiency * inv,
            "t_motor_k": self._sum_t_motor_k * inv,
            "t_ambient_k": self._sum_t_ambient_k * inv,
        }
        self._sum_motor_torque_nm = 0.0
        self._sum_motor_speed_rads = 0.0
        self._sum_motor_efficiency = 0.0
        self._sum_t_motor_k = 0.0
        self._sum_t_ambient_k = 0.0
        self._samples = 0

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        tau_s = float(self.params.get("tau_s", 450.0))
        motor_torque_nm = self._accumulated.get("motor_torque_nm", sim_state.motor_torque_nm)
        motor_speed_rads = self._accumulated.get("motor_speed_rads", sim_state.motor_speed_rads)
        motor_efficiency = self._accumulated.get("motor_efficiency", sim_state.motor_efficiency)
        t_motor_k = self._accumulated.get("t_motor_k", sim_state.t_motor_k)
        t_ambient_k = self._accumulated.get("t_ambient_k", sim_state.t_ambient_k)
        mech_power_w = abs(motor_torque_nm * motor_speed_rads)
        loss_frac = max(1.0 - motor_efficiency, 0.0)
        q_loss_w = mech_power_w * loss_frac
        t_next_k = t_motor_k + (t_ambient_k - t_motor_k) * dt / tau_s + q_loss_w * 1e-5 * dt
        self._state = {"q_loss_w": q_loss_w}
        self.t += dt
        return ModuleOutputs(t_motor_k=t_next_k)

    def get_state(self) -> dict:
        return dict(self._state)

    def validate_params(self) -> None:
        if float(self.params.get("tau_s", 0.0)) <= 0:
            raise ValueError("motor_thermal.tau_s must be > 0")
