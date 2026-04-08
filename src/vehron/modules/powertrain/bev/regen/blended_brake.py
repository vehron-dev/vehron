"""Blended braking model for regenerative braking."""

from __future__ import annotations

from vehron.modules.base import BaseModule
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class BlendedBrakeRegenModel(BaseModule):
    def initialize(self, dt: float) -> None:
        self._state = {"friction_brake_frac": 0.0}
        self.t = 0.0

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        max_regen_power_w = float(self.params.get("max_regen_power_w", 0.0))
        regen_efficiency = self._clamp(float(self.params.get("regen_efficiency", 0.7)), 0.1, 1.0, "regen_efficiency")

        if sim_state.v_ms < 0.5 or sim_state.brake <= 0.0 or sim_state.soc >= 0.99:
            p_regen_w = 0.0
            friction_brake_frac = 1.0 if sim_state.brake > 0.0 else 0.0
        else:
            requested_regen_w = sim_state.brake * max_regen_power_w
            kinetic_limited_w = max(-sim_state.wheel_power_w, 0.0)
            p_regen_w = min(requested_regen_w, kinetic_limited_w) * regen_efficiency
            friction_brake_frac = 0.0 if requested_regen_w <= kinetic_limited_w else 1.0 - kinetic_limited_w / requested_regen_w

        self._state = {"friction_brake_frac": friction_brake_frac}
        self.t += dt
        return ModuleOutputs(p_regen_w=max(p_regen_w, 0.0))

    def get_state(self) -> dict:
        return dict(self._state)

    def validate_params(self) -> None:
        if float(self.params.get("max_regen_power_w", -1.0)) < 0:
            raise ValueError("regen.max_regen_power_w must be >= 0")
