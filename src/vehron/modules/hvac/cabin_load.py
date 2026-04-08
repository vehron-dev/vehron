"""Cabin HVAC load model."""

from __future__ import annotations

from vehron.constants import CELSIUS_TO_KELVIN
from vehron.modules.base import BaseModule
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class CabinLoadModel(BaseModule):
    def initialize(self, dt: float) -> None:
        self._state = {"mode": "off"}
        self.t = 0.0

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        rated_power_w = float(self.params.get("rated_power_kw", 4.0)) * 1000.0
        setpoint_k = float(self.params.get("cabin_setpoint_c", 22.0)) + CELSIUS_TO_KELVIN
        cop_cooling = float(self.params.get("cop_cooling", 2.5))
        cop_heating = float(self.params.get("cop_heating", 2.0))

        delta_k = sim_state.t_ambient_k - setpoint_k

        if delta_k > 0.5:
            cooling_frac = min(delta_k / 15.0, 1.0)
            thermal_load_w = rated_power_w * cooling_frac
            p_hvac_w = thermal_load_w / max(cop_cooling, 0.1)
            mode = "cooling"
        elif delta_k < -0.5:
            heating_frac = min(abs(delta_k) / 20.0, 1.0)
            thermal_load_w = rated_power_w * heating_frac
            p_hvac_w = thermal_load_w / max(cop_heating, 0.1)
            mode = "heating"
        else:
            p_hvac_w = 0.0
            mode = "off"

        cabin_tau_s = 600.0
        t_cabin_next_k = sim_state.t_cabin_k + (setpoint_k - sim_state.t_cabin_k) * dt / cabin_tau_s

        self._state = {"mode": mode}
        self.t += dt
        return ModuleOutputs(p_hvac_w=max(p_hvac_w, 0.0), t_cabin_k=t_cabin_next_k)

    def get_state(self) -> dict:
        return dict(self._state)

    def validate_params(self) -> None:
        if float(self.params.get("rated_power_kw", 0.0)) <= 0:
            raise ValueError("hvac.rated_power_kw must be > 0")
