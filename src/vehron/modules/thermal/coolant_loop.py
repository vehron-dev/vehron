"""Simple coolant loop thermal equalization model."""

from __future__ import annotations

from vehron.modules.base import BaseModule
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class CoolantLoopModel(BaseModule):
    RATE_DIVISOR: int = 100

    def initialize(self, dt: float) -> None:
        self._state = {"t_target_k": 0.0}
        self._sum_t_batt_k = 0.0
        self._sum_t_motor_k = 0.0
        self._sum_t_coolant_k = 0.0
        self._samples = 0
        self._accumulated = {"t_batt_k": 298.15, "t_motor_k": 298.15, "t_coolant_k": 298.15}
        self.t = 0.0

    def accumulate(self, sim_state: SimState) -> None:
        self._sum_t_batt_k += sim_state.t_batt_k
        self._sum_t_motor_k += sim_state.t_motor_k
        self._sum_t_coolant_k += sim_state.t_coolant_k
        self._samples += 1

    def flush_accumulator(self) -> None:
        if self._samples <= 0:
            return
        inv = 1.0 / self._samples
        self._accumulated = {
            "t_batt_k": self._sum_t_batt_k * inv,
            "t_motor_k": self._sum_t_motor_k * inv,
            "t_coolant_k": self._sum_t_coolant_k * inv,
        }
        self._sum_t_batt_k = 0.0
        self._sum_t_motor_k = 0.0
        self._sum_t_coolant_k = 0.0
        self._samples = 0

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        tau_s = float(self.params.get("tau_s", 900.0))
        t_batt_k = self._accumulated.get("t_batt_k", sim_state.t_batt_k)
        t_motor_k = self._accumulated.get("t_motor_k", sim_state.t_motor_k)
        t_coolant_k = self._accumulated.get("t_coolant_k", sim_state.t_coolant_k)
        t_target_k = 0.5 * (t_batt_k + t_motor_k)
        t_coolant_next_k = t_coolant_k + (t_target_k - t_coolant_k) * dt / tau_s
        self._state = {"t_target_k": t_target_k}
        self.t += dt
        return ModuleOutputs(t_coolant_k=t_coolant_next_k)

    def get_state(self) -> dict:
        return dict(self._state)

    def validate_params(self) -> None:
        if float(self.params.get("tau_s", 0.0)) <= 0:
            raise ValueError("coolant_loop.tau_s must be > 0")
