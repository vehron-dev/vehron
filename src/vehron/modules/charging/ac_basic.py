# Copyright (C) 2026 Subramanyam Natarajan
# SPDX-License-Identifier: AGPL-3.0-only

"""Simple AC charging controller for VEHRON."""

from __future__ import annotations

from vehron.modules.base import BaseModule
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class AcBasicChargingModel(BaseModule):
    """Battery-side AC charger request model with CP/CV-style behavior."""

    RATE_DIVISOR: int = 1

    def initialize(self, dt: float) -> None:
        self._state = {
            "charge_state": "IDLE",
            "requested_charge_power_w": 0.0,
            "charger_input_power_w": 0.0,
            "ocv_est_v": 0.0,
        }
        self.t = 0.0

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        del inputs

        mode = str(self.params.get("mode", "none"))
        start_s = float(self.params.get("start_s", 0.0))
        end_s = float(self.params.get("end_s", 0.0))
        target_soc = float(self.params.get("target_soc", 0.8))
        efficiency = float(self.params.get("charge_efficiency_ac", 0.95))
        p_ac_limit_w = float(self.params.get("ac_power_limit_kw", 0.0)) * 1000.0
        p_dc_limit_w = max(p_ac_limit_w * efficiency, 0.0)
        nominal_voltage_v = float(self.params.get("nominal_voltage_v", 350.0))
        target_voltage_value = self.params.get("target_voltage_v")
        if target_voltage_value is None:
            target_voltage_value = self.params.get("ocv_full_v", nominal_voltage_v * 1.05)
        target_voltage_v = float(target_voltage_value)
        termination_current_a = float(self.params.get("termination_current_a", 5.0))
        max_charge_current_value = self.params.get("max_charge_current_a")
        max_charge_current_a = float(max_charge_current_value) if max_charge_current_value is not None else 0.0
        resistance_ohm = float(
            self.params.get(
                "charge_resistance_ohm",
                self.params.get("internal_resistance_ohm", 0.05),
            )
        )
        cv_enabled = bool(self.params.get("cv_enabled", True))

        is_window_active = mode == "ac" and end_s > start_s and start_s <= sim_state.t <= end_s
        if not is_window_active:
            self._state = {
                "charge_state": "IDLE",
                "requested_charge_power_w": 0.0,
                "charger_input_power_w": 0.0,
                "ocv_est_v": 0.0,
            }
            self.t += dt
            return ModuleOutputs(
                p_external_charge_w=0.0,
                charger_input_power_w=0.0,
                is_plugged_in=False,
                charger_mode="none",
                charge_state="IDLE",
            )

        batt_temp_c = sim_state.t_batt_k - 273.15
        temp_min_charge_c = self.params.get("temp_min_charge_c")
        temp_max_charge_c = self.params.get("temp_max_charge_c")
        if temp_min_charge_c is not None and batt_temp_c < float(temp_min_charge_c):
            charge_state = "FAULT"
            p_request_w = 0.0
        elif temp_max_charge_c is not None and batt_temp_c > float(temp_max_charge_c):
            charge_state = "FAULT"
            p_request_w = 0.0
        elif sim_state.soc >= target_soc:
            charge_state = "DONE"
            p_request_w = 0.0
        else:
            v_batt_v = sim_state.v_batt_v if sim_state.v_batt_v > 0.0 else nominal_voltage_v
            i_batt_a = sim_state.i_batt_a
            ocv_est_v = max(v_batt_v + i_batt_a * resistance_ohm, 1.0)

            p_request_w = -p_dc_limit_w
            charge_state = "AC_CP"

            if cv_enabled and v_batt_v >= target_voltage_v:
                charge_state = "AC_CV"
                i_cv_mag_a = max((target_voltage_v - ocv_est_v) / max(resistance_ohm, 1e-9), 0.0)
                if max_charge_current_a > 0.0:
                    i_cv_mag_a = min(i_cv_mag_a, max_charge_current_a)
                if i_cv_mag_a <= termination_current_a:
                    charge_state = "DONE"
                    p_request_w = 0.0
                else:
                    p_request_w = -min(target_voltage_v * i_cv_mag_a, p_dc_limit_w)

            if charge_state == "AC_CP" and max_charge_current_a > 0.0:
                p_request_w = -min(p_dc_limit_w, v_batt_v * max_charge_current_a)

            self._state["ocv_est_v"] = ocv_est_v

        charger_input_power_w = abs(p_request_w) / max(efficiency, 1e-9) if p_request_w < 0.0 else 0.0
        self._state.update(
            {
                "charge_state": charge_state,
                "requested_charge_power_w": p_request_w,
                "charger_input_power_w": charger_input_power_w,
            }
        )
        self.t += dt

        return ModuleOutputs(
            p_external_charge_w=max(-p_request_w, 0.0),
            charger_input_power_w=charger_input_power_w,
            is_plugged_in=True,
            charger_mode="ac",
            charge_state=charge_state,
        )

    def get_state(self) -> dict:
        return dict(self._state)

    def validate_params(self) -> None:
        if float(self.params.get("ac_power_limit_kw", 0.0)) <= 0.0:
            raise ValueError("charging.ac_power_limit_kw must be > 0 for AC charging")
        if float(self.params.get("charge_efficiency_ac", 0.0)) <= 0.0:
            raise ValueError("charging.charge_efficiency_ac must be > 0")
        if float(self.params.get("termination_current_a", -1.0)) < 0.0:
            raise ValueError("charging.termination_current_a must be >= 0")
        if "max_charge_current_a" in self.params:
            max_charge_current_a = self.params.get("max_charge_current_a")
            if max_charge_current_a is not None and float(max_charge_current_a) <= 0.0:
                raise ValueError("charging.max_charge_current_a must be > 0 when set")
