# Copyright (C) 2026 Subramanyam Natarajan
# SPDX-License-Identifier: AGPL-3.0-only

"""HVAC module slot interface for VEHRON."""

from __future__ import annotations

from abc import ABC

from vehron.modules.base import BaseModule
from vehron.state import ModuleInputs, SimState


class HvacModelBase(BaseModule, ABC):
    """Contract for all VEHRON HVAC models.

    Third-party HVAC or cabin-thermal models can be hot-swapped into VEHRON by
    subclassing this base class. The engine treats every HVAC model as a normal
    module, but the HVAC slot exposes a stable interface and helper convention.
    """

    SLOT_NAME: str = "hvac"
    INTERFACE_VERSION: str = "1.0"

    def resolve_thermal_inputs(
        self,
        sim_state: SimState,
        inputs: ModuleInputs,
    ) -> dict[str, float]:
        """Return the canonical HVAC-side thermal boundary inputs for this step."""
        extras = inputs.extras
        return {
            "t_ambient_k": float(sim_state.t_ambient_k),
            "t_cabin_k": float(sim_state.t_cabin_k),
            "vehicle_speed_ms": float(sim_state.v_ms),
            "solar_irradiance_wm2": float(extras.get("solar_irradiance_wm2", 0.0)),
            "passenger_count": float(extras.get("passenger_count", 0.0)),
        }
