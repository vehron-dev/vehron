"""Minimal example of a private VEHRON battery model.

This file is intended as a template for third-party teams. Copy it into a
private location, rename the class if needed, and replace the placeholder
physics with your own pack model.
"""

from __future__ import annotations

from vehron.modules.energy_storage.battery.base import BatteryModelBase
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class PrivateBatteryModel(BatteryModelBase):
    """Example battery slot implementation for VEHRON.

    This template uses the same public interface as the in-repo reference Rint
    model, but keeps the equations intentionally simple so the integration
    pattern is easy to follow.
    """

    RATE_DIVISOR: int = 5

    def initialize(self, dt: float) -> None:
        self._state = {
            "soc": float(self.params.get("soc_init", 0.95)),
        }

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        nominal_voltage_v = float(self.params["nominal_voltage_v"])
        capacity_kwh = float(self.params["capacity_kwh"])
        internal_resistance_ohm = float(self.params.get("internal_resistance_ohm", 0.08))
        soc_min = float(self.params.get("soc_min", 0.05))
        soc_max = float(self.params.get("soc_max", 0.98))

        # Use the canonical VEHRON battery-side power boundary unless your
        # private model intentionally needs a different interpretation.
        power_inputs = self.resolve_power_inputs(sim_state, inputs)
        p_net_w = power_inputs["p_net_w"]

        capacity_ah = capacity_kwh * 1000.0 / nominal_voltage_v
        i_batt_a = p_net_w / nominal_voltage_v if nominal_voltage_v > 0 else 0.0
        v_batt_v = max(nominal_voltage_v - i_batt_a * internal_resistance_ohm, 1.0)
        p_batt_w = v_batt_v * i_batt_a

        soc = float(self._state["soc"])
        soc_next = soc - (i_batt_a * dt) / (capacity_ah * 3600.0)
        soc_next = min(max(soc_next, soc_min), soc_max)
        self._state["soc"] = soc_next

        return ModuleOutputs(
            soc=soc_next,
            v_batt_v=v_batt_v,
            i_batt_a=i_batt_a,
            p_batt_w=p_batt_w,
        )

    def get_state(self) -> dict:
        return dict(self._state)

    def validate_params(self) -> None:
        for key in ("capacity_kwh", "nominal_voltage_v"):
            if float(self.params.get(key, 0.0)) <= 0:
                raise ValueError(f"battery.{key} must be > 0")
