"""Simple first-order battery thermal model."""

from __future__ import annotations

from vehron.modules.base import BaseModule
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class BatteryThermalModel(BaseModule):
    RATE_DIVISOR: int = 20

    def initialize(self, dt: float) -> None:
        self._state = {"q_loss_w": 0.0}
        self._sum_i_batt_a = 0.0
        self._sum_t_batt_k = 0.0
        self._sum_t_ambient_k = 0.0
        self._samples = 0
        self._accumulated = {"i_batt_a": 0.0, "t_batt_k": 298.15, "t_ambient_k": 298.15}
        self.t = 0.0

    def accumulate(self, sim_state: SimState) -> None:
        self._sum_i_batt_a += sim_state.i_batt_a
        self._sum_t_batt_k += sim_state.t_batt_k
        self._sum_t_ambient_k += sim_state.t_ambient_k
        self._samples += 1

    def flush_accumulator(self) -> None:
        if self._samples <= 0:
            return
        inv = 1.0 / self._samples
        self._accumulated = {
            "i_batt_a": self._sum_i_batt_a * inv,
            "t_batt_k": self._sum_t_batt_k * inv,
            "t_ambient_k": self._sum_t_ambient_k * inv,
        }
        self._sum_i_batt_a = 0.0
        self._sum_t_batt_k = 0.0
        self._sum_t_ambient_k = 0.0
        self._samples = 0

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        tau_s = float(self.params.get("tau_s", 600.0))
        i_batt_a = self._accumulated.get("i_batt_a", sim_state.i_batt_a)
        t_batt_k = self._accumulated.get("t_batt_k", sim_state.t_batt_k)
        t_ambient_k = self._accumulated.get("t_ambient_k", sim_state.t_ambient_k)
        q_loss_w = abs(i_batt_a) * 3.0
        t_next_k = t_batt_k + (t_ambient_k - t_batt_k) * dt / tau_s + q_loss_w * 2e-5 * dt
        self._state = {"q_loss_w": q_loss_w}
        self.t += dt
        return ModuleOutputs(t_batt_k=t_next_k)

    def get_state(self) -> dict:
        return dict(self._state)

    def validate_params(self) -> None:
        if float(self.params.get("tau_s", 0.0)) <= 0:
            raise ValueError("battery_thermal.tau_s must be > 0")
