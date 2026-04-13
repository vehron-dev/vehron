"""Minimal example of a private VEHRON HVAC model.

This file is intended as a template for third-party teams. Copy it into a
private location, rename the class if needed, and replace the placeholder
physics with your own HVAC or cabin-thermal model.
"""

from __future__ import annotations

from vehron.constants import CELSIUS_TO_KELVIN
from vehron.modules.hvac.base import HvacModelBase
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class PrivateHvacModel(HvacModelBase):
    """Example HVAC slot implementation for VEHRON.

    This template uses the same public interface as the in-repo reference cabin
    load model, but keeps the equations intentionally simple so the integration
    pattern is easy to follow.
    """

    RATE_DIVISOR: int = 20

    def initialize(self, dt: float) -> None:
        self._state = {"mode": "off"}

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        rated_power_w = float(self.params.get("rated_power_kw", 4.0)) * 1000.0
        setpoint_k = float(self.params.get("cabin_setpoint_c", 22.0)) + CELSIUS_TO_KELVIN
        cop_cooling = float(self.params.get("cop_cooling", 2.5))
        cop_heating = float(self.params.get("cop_heating", 2.0))

        thermal_inputs = self.resolve_thermal_inputs(sim_state, inputs)
        t_ambient_k = thermal_inputs["t_ambient_k"]
        t_cabin_k = thermal_inputs["t_cabin_k"]

        if t_cabin_k > setpoint_k:
            thermal_load_w = min((t_cabin_k - setpoint_k) * 400.0, rated_power_w)
            p_hvac_w = thermal_load_w / max(cop_cooling, 0.1)
            t_cabin_next_k = t_cabin_k - min((t_cabin_k - setpoint_k) * 0.15, 2.0)
            mode = "cooling"
        elif t_cabin_k < setpoint_k:
            thermal_load_w = min((setpoint_k - t_cabin_k) * 300.0, rated_power_w)
            p_hvac_w = thermal_load_w / max(cop_heating, 0.1)
            t_cabin_next_k = t_cabin_k + min((setpoint_k - t_cabin_k) * 0.15, 2.0)
            mode = "heating"
        else:
            p_hvac_w = 0.0
            t_cabin_next_k = t_cabin_k + 0.02 * (t_ambient_k - t_cabin_k)
            mode = "off"

        self._state = {"mode": mode}
        return ModuleOutputs(
            p_hvac_w=max(p_hvac_w, 0.0),
            t_cabin_k=t_cabin_next_k,
        )

    def get_state(self) -> dict:
        return dict(self._state)

    def validate_params(self) -> None:
        for key in ("rated_power_kw", "cop_cooling", "cop_heating"):
            if float(self.params.get(key, 0.0)) <= 0:
                raise ValueError(f"hvac.{key} must be > 0")
