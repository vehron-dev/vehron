# Copyright (C) 2026 Subramanyam Natarajan
# SPDX-License-Identifier: AGPL-3.0-only

"""Low-order cabin thermal and HVAC load model.

This implementation follows the standard lumped-parameter vehicle-cabin model
family used in the literature: passive cabin heat flow is decomposed into
solar gain, envelope exchange, ventilation / air-renewal load, and occupant
heat, with HVAC power computed from the thermal load and system COP.

VEHRON currently uses a deliberately simplified single-zone realization of that
model family for fast vehicle-level simulation rather than a paper-exact
multi-node reproduction.
"""

from __future__ import annotations

from vehron.constants import AIR_CP_JKGK, AIR_DENSITY_KGM3, CELSIUS_TO_KELVIN
from vehron.modules.hvac.base import HvacModelBase
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class CabinLoadModel(HvacModelBase):
    """Low-order cabin thermal model with passive heat gains and HVAC control.

    The model represents the cabin as a single lumped thermal mass. Net cabin
    heat flow is composed of:
    - body/glass transmission and convection to ambient
    - speed-sensitive exterior heat transfer
    - solar gain through glazing
    - ventilation / infiltration load
    - occupant sensible heat
    - HVAC heating or cooling capacity
    """

    RATE_DIVISOR: int = 20

    def initialize(self, dt: float) -> None:
        self._state = {
            "mode": "off",
            "q_solar_w": 0.0,
            "q_envelope_w": 0.0,
            "q_ventilation_w": 0.0,
            "q_occupants_w": 0.0,
            "q_hvac_thermal_w": 0.0,
        }
        self._sum_t_ambient_k = 0.0
        self._sum_t_cabin_k = 0.0
        self._sum_v_ms = 0.0
        self._samples = 0
        self._accumulated = {
            "t_ambient_k": 298.15,
            "t_cabin_k": 298.15,
            "v_ms": 0.0,
        }
        self.t = 0.0

    def accumulate(self, sim_state: SimState) -> None:
        self._sum_t_ambient_k += sim_state.t_ambient_k
        self._sum_t_cabin_k += sim_state.t_cabin_k
        self._sum_v_ms += sim_state.v_ms
        self._samples += 1

    def flush_accumulator(self) -> None:
        if self._samples <= 0:
            return
        inv = 1.0 / self._samples
        self._accumulated = {
            "t_ambient_k": self._sum_t_ambient_k * inv,
            "t_cabin_k": self._sum_t_cabin_k * inv,
            "v_ms": self._sum_v_ms * inv,
        }
        self._sum_t_ambient_k = 0.0
        self._sum_t_cabin_k = 0.0
        self._sum_v_ms = 0.0
        self._samples = 0

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        rated_thermal_power_w = float(self.params.get("rated_power_kw", 4.0)) * 1000.0
        setpoint_k = float(self.params.get("cabin_setpoint_c", 22.0)) + CELSIUS_TO_KELVIN
        cop_cooling = float(self.params.get("cop_cooling", 2.5))
        cop_heating = float(self.params.get("cop_heating", 2.0))
        cabin_volume_m3 = float(self.params.get("cabin_volume_m3", 2.8))
        interior_thermal_mass_kjk = float(self.params.get("interior_thermal_mass_kjk", 75.0))
        body_ua_wk = float(self.params.get("body_ua_wk", 120.0))
        speed_ua_per_ms_wk = float(self.params.get("speed_ua_per_ms_wk", 3.0))
        glazed_area_m2 = float(self.params.get("glazed_area_m2", 2.2))
        solar_transmittance = float(self.params.get("solar_transmittance", 0.55))
        fresh_air_ach = float(self.params.get("fresh_air_ach", 8.0))
        passenger_count = int(self.params.get("passenger_count", 1))
        occupant_sensible_w = float(self.params.get("occupant_sensible_w", 75.0))
        solar_irradiance_wm2 = float(self.params.get("solar_irradiance_wm2", 0.0))
        control_tau_s = float(self.params.get("control_tau_s", 240.0))

        thermal_inputs = self.resolve_thermal_inputs(sim_state, inputs)
        t_ambient_k = self._accumulated.get("t_ambient_k", thermal_inputs["t_ambient_k"])
        t_cabin_k = self._accumulated.get("t_cabin_k", thermal_inputs["t_cabin_k"])
        vehicle_speed_ms = self._accumulated.get("v_ms", thermal_inputs["vehicle_speed_ms"])
        solar_irradiance_wm2 = float(
            self.params.get("solar_irradiance_wm2", thermal_inputs["solar_irradiance_wm2"])
        )
        passenger_count = int(self.params.get("passenger_count", thermal_inputs["passenger_count"]))

        cabin_air_thermal_mass_jk = AIR_DENSITY_KGM3 * cabin_volume_m3 * AIR_CP_JKGK
        interior_thermal_mass_jk = interior_thermal_mass_kjk * 1000.0
        total_thermal_mass_jk = max(cabin_air_thermal_mass_jk + interior_thermal_mass_jk, 1.0)

        ua_total_wk = body_ua_wk + speed_ua_per_ms_wk * max(vehicle_speed_ms, 0.0)
        q_envelope_w = ua_total_wk * (t_ambient_k - t_cabin_k)
        q_solar_w = solar_irradiance_wm2 * glazed_area_m2 * solar_transmittance

        fresh_air_mdot_kgs = AIR_DENSITY_KGM3 * cabin_volume_m3 * fresh_air_ach / 3600.0
        q_ventilation_w = fresh_air_mdot_kgs * AIR_CP_JKGK * (t_ambient_k - t_cabin_k)
        q_occupants_w = passenger_count * occupant_sensible_w

        q_passive_w = q_envelope_w + q_solar_w + q_ventilation_w + q_occupants_w
        control_correction_w = total_thermal_mass_jk * (setpoint_k - t_cabin_k) / max(control_tau_s, 1.0)

        q_hvac_thermal_w = 0.0
        temp_deadband_k = 0.25
        if t_cabin_k >= setpoint_k - temp_deadband_k:
            cooling_request_w = max(q_passive_w - control_correction_w, 0.0)
            q_hvac_thermal_w = -min(cooling_request_w, rated_thermal_power_w)
        elif t_cabin_k <= setpoint_k + temp_deadband_k:
            heating_request_w = max(-q_passive_w + control_correction_w, 0.0)
            q_hvac_thermal_w = min(heating_request_w, rated_thermal_power_w)

        if q_hvac_thermal_w < 0.0:
            p_hvac_w = abs(q_hvac_thermal_w) / max(cop_cooling, 0.1)
            mode = "cooling"
        elif q_hvac_thermal_w > 0.0:
            p_hvac_w = q_hvac_thermal_w / max(cop_heating, 0.1)
            mode = "heating"
        else:
            p_hvac_w = 0.0
            mode = "off"

        q_net_w = q_passive_w + q_hvac_thermal_w
        t_cabin_next_k = t_cabin_k + (q_net_w * dt) / total_thermal_mass_jk

        self._state = {
            "mode": mode,
            "q_solar_w": q_solar_w,
            "q_envelope_w": q_envelope_w,
            "q_ventilation_w": q_ventilation_w,
            "q_occupants_w": q_occupants_w,
            "q_hvac_thermal_w": q_hvac_thermal_w,
        }
        self.t += dt
        return ModuleOutputs(p_hvac_w=max(p_hvac_w, 0.0), t_cabin_k=t_cabin_next_k)

    def get_state(self) -> dict:
        return dict(self._state)

    def validate_params(self) -> None:
        required_positive = (
            "rated_power_kw",
            "cabin_volume_m3",
            "cop_cooling",
            "cop_heating",
            "interior_thermal_mass_kjk",
            "body_ua_wk",
            "glazed_area_m2",
            "solar_transmittance",
            "fresh_air_ach",
            "occupant_sensible_w",
            "control_tau_s",
        )
        for key in required_positive:
            if float(self.params.get(key, 0.0)) <= 0:
                raise ValueError(f"hvac.{key} must be > 0")

        if float(self.params.get("speed_ua_per_ms_wk", 0.0)) < 0:
            raise ValueError("hvac.speed_ua_per_ms_wk must be >= 0")
        if int(self.params.get("passenger_count", 0)) < 0:
            raise ValueError("hvac.passenger_count must be >= 0")
        if float(self.params.get("solar_irradiance_wm2", 0.0)) < 0:
            raise ValueError("hvac.solar_irradiance_wm2 must be >= 0")
