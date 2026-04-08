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
