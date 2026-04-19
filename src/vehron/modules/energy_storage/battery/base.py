"""Battery module slot interface for VEHRON."""

from __future__ import annotations

from abc import ABC

from vehron.modules.base import BaseModule
from vehron.state import ModuleInputs, SimState


class BatteryModelBase(BaseModule, ABC):
    """Contract for all VEHRON battery electrical models.

    Third-party battery packs can be hot-swapped into VEHRON by subclassing
    this base class. The engine treats every battery model as a normal module,
    but the battery slot has a stable interface and a few common helper
    conventions documented here.
    """

    SLOT_NAME: str = "battery"
    INTERFACE_VERSION: str = "1.0"
    ADVISORY_KEYS: tuple[str, ...] = (
        "charge_recommended",
        "charge_required",
        "max_charge_power_w",
        "max_discharge_power_w",
        "preferred_charge_power_w",
        "resume_charge_soc",
        "trigger_charge_soc",
    )

    def resolve_power_inputs(
        self,
        sim_state: SimState,
        inputs: ModuleInputs,
    ) -> dict[str, float]:
        """Return the battery-relevant power channels for this step.

        External battery models should use this helper unless they intentionally
        need a custom interpretation of the pack boundary conditions.
        """
        p_external_charge_w = float(inputs.extras.get("p_external_charge_w", 0.0))
        return {
            "p_drive_w": float(sim_state.p_drive_w),
            "p_hvac_w": float(sim_state.p_hvac_w),
            "p_aux_w": float(sim_state.p_aux_w),
            "p_regen_w": float(sim_state.p_regen_w),
            "p_external_charge_w": p_external_charge_w,
            "p_net_w": (
                float(sim_state.p_drive_w)
                + float(sim_state.p_hvac_w)
                + float(sim_state.p_aux_w)
                - float(sim_state.p_regen_w)
                - p_external_charge_w
            ),
        }

    def resolve_charge_advisories(self) -> dict[str, float | bool]:
        """Return standardized battery advisories from module-private state.

        External battery models may expose these keys through ``get_state()`` or
        directly in ``self._state``. The engine uses them as soft or hard hints
        for mission-level charging control without forcing battery physics and
        routing policy into the same module.
        """
        state = self.get_state()
        return {
            key: state[key]
            for key in self.ADVISORY_KEYS
            if key in state
        }
