"""PID-based driver model for speed tracking."""

from __future__ import annotations

from vehron.modules.base import BaseModule
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class PidDriverModel(BaseModule):
    def initialize(self, dt: float) -> None:
        self._state = {"integral_error": 0.0, "prev_error": 0.0}
        self.t = 0.0

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        target_v_ms = sim_state.target_v_ms
        error_ms = target_v_ms - sim_state.v_ms

        integral_error = self._state["integral_error"] + error_ms * dt
        prev_error = self._state["prev_error"]
        deriv_error = (error_ms - prev_error) / dt if dt > 0 else 0.0

        kp = float(self.params.get("kp", 1.0))
        ki = float(self.params.get("ki", 0.0))
        kd = float(self.params.get("kd", 0.0))

        command = kp * error_ms + ki * integral_error + kd * deriv_error

        throttle = min(max(command, 0.0), 1.0)
        brake = min(max(-command, 0.0), 1.0)

        self._state["integral_error"] = integral_error
        self._state["prev_error"] = error_ms
        self.t += dt

        return ModuleOutputs(throttle=throttle, brake=brake)

    def get_state(self) -> dict:
        return {
            "integral_error": float(self._state.get("integral_error", 0.0)),
            "prev_error": float(self._state.get("prev_error", 0.0)),
        }

    def validate_params(self) -> None:
        for key in ("kp", "ki", "kd"):
            if key in self.params and float(self.params[key]) < 0:
                raise ValueError(f"driver.{key} must be >= 0")
