# Copyright (c) 2026 Subramanyam Natarajan
# SPDX-License-Identifier: AGPL-3.0-only

"""Two-RC equivalent-circuit battery model for BEV simulation."""

from __future__ import annotations

import math

from vehron.modules.energy_storage.battery.base import BatteryModelBase
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class Ecm2RcBatteryModel(BatteryModelBase):
    """Battery model with ohmic resistance and two polarization branches.

    This keeps VEHRON lightweight while capturing two behaviors the plain Rint
    model misses:
    - transient voltage sag under step load
    - voltage recovery when load is reduced or reversed during regen/charging
    """

    RATE_DIVISOR: int = 5

    def initialize(self, dt: float) -> None:
        self._state = {
            "soc": float(self.params.get("soc_init", 1.0)),
            "v_rc1_v": 0.0,
            "v_rc2_v": 0.0,
            "v_ocv_v": 0.0,
        }
        self._sum_p_drive_w = 0.0
        self._sum_p_hvac_w = 0.0
        self._sum_p_aux_w = 0.0
        self._sum_p_regen_w = 0.0
        self._samples = 0
        self._accumulated = {
            "p_drive_w": 0.0,
            "p_hvac_w": 0.0,
            "p_aux_w": 0.0,
            "p_regen_w": 0.0,
        }
        self._has_accumulated = False
        self.t = 0.0

    def accumulate(self, sim_state: SimState) -> None:
        self._sum_p_drive_w += sim_state.p_drive_w
        self._sum_p_hvac_w += sim_state.p_hvac_w
        self._sum_p_aux_w += sim_state.p_aux_w
        self._sum_p_regen_w += sim_state.p_regen_w
        self._samples += 1

    def flush_accumulator(self) -> None:
        if self._samples <= 0:
            return
        inv = 1.0 / self._samples
        self._accumulated = {
            "p_drive_w": self._sum_p_drive_w * inv,
            "p_hvac_w": self._sum_p_hvac_w * inv,
            "p_aux_w": self._sum_p_aux_w * inv,
            "p_regen_w": self._sum_p_regen_w * inv,
        }
        self._has_accumulated = True
        self._sum_p_drive_w = 0.0
        self._sum_p_hvac_w = 0.0
        self._sum_p_aux_w = 0.0
        self._sum_p_regen_w = 0.0
        self._samples = 0

    def _resolved_power_inputs(self, sim_state: SimState, inputs: ModuleInputs) -> dict[str, float]:
        if self._has_accumulated:
            state_for_power = SimState(
                p_drive_w=self._accumulated.get("p_drive_w", sim_state.p_drive_w),
                p_hvac_w=self._accumulated.get("p_hvac_w", sim_state.p_hvac_w),
                p_aux_w=self._accumulated.get("p_aux_w", sim_state.p_aux_w),
                p_regen_w=self._accumulated.get("p_regen_w", sim_state.p_regen_w),
            )
        else:
            state_for_power = SimState(
                p_drive_w=sim_state.p_drive_w,
                p_hvac_w=sim_state.p_hvac_w,
                p_aux_w=sim_state.p_aux_w,
                p_regen_w=sim_state.p_regen_w,
            )
        return self.resolve_power_inputs(state_for_power, inputs)

    def _open_circuit_voltage(self, soc: float) -> float:
        nominal_voltage_v = float(self.params["nominal_voltage_v"])
        ocv_empty_v = float(self.params.get("ocv_empty_v", nominal_voltage_v * 0.90))
        ocv_full_v = float(self.params.get("ocv_full_v", nominal_voltage_v * 1.08))
        soc_shaped = min(max(soc, 0.0), 1.0)

        # Add a small S-shaped nonlinearity so mid-SOC stays flatter while the
        # ends steepen a bit, which is more realistic than a purely linear OCV.
        shape_gain = float(self.params.get("ocv_shape_gain", 0.08))
        ocv_span_v = ocv_full_v - ocv_empty_v
        s_curve = math.tanh((soc_shaped - 0.5) * 4.0)
        return ocv_empty_v + ocv_span_v * soc_shaped + shape_gain * ocv_span_v * s_curve

    @staticmethod
    def _rc_branch_next(v_prev_v: float, current_a: float, resistance_ohm: float, capacitance_f: float, dt: float) -> float:
        tau_s = resistance_ohm * capacitance_f
        if tau_s <= 0.0:
            return current_a * resistance_ohm
        alpha = math.exp(-dt / tau_s)
        return alpha * v_prev_v + (1.0 - alpha) * current_a * resistance_ohm

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        capacity_kwh = float(self.params["capacity_kwh"])
        nominal_voltage_v = float(self.params["nominal_voltage_v"])
        r0_ohm = float(self.params.get("r0_ohm", self.params.get("internal_resistance_ohm", 0.08)))
        r1_ohm = float(self.params.get("r1_ohm", r0_ohm * 0.6))
        c1_f = float(self.params.get("c1_f", 8000.0))
        r2_ohm = float(self.params.get("r2_ohm", r0_ohm * 0.9))
        c2_f = float(self.params.get("c2_f", 35000.0))
        soc_min = float(self.params.get("soc_min", 0.05))
        soc_max = float(self.params.get("soc_max", 0.98))

        capacity_ah = capacity_kwh * 1000.0 / nominal_voltage_v
        i_discharge_max_a = capacity_ah * float(self.params.get("max_discharge_rate_c", 4.0))
        i_charge_max_a = capacity_ah * float(self.params.get("max_charge_rate_c", 2.0))

        power_inputs = self._resolved_power_inputs(sim_state, inputs)
        p_net_w = power_inputs["p_net_w"]

        soc = float(self._state.get("soc", sim_state.soc))
        v_rc1_prev_v = float(self._state.get("v_rc1_v", 0.0))
        v_rc2_prev_v = float(self._state.get("v_rc2_v", 0.0))
        v_ocv_v = self._open_circuit_voltage(soc)

        v_effective_v = max(v_ocv_v - v_rc1_prev_v - v_rc2_prev_v, 1.0)
        i_ideal_a = p_net_w / v_effective_v
        i_batt_a = self._clamp(i_ideal_a, -i_charge_max_a, i_discharge_max_a, "i_batt_a")

        if soc <= soc_min and i_batt_a > 0:
            i_batt_a = 0.0
        if soc >= soc_max and i_batt_a < 0:
            i_batt_a = 0.0

        v_rc1_v = self._rc_branch_next(v_rc1_prev_v, i_batt_a, r1_ohm, c1_f, dt)
        v_rc2_v = self._rc_branch_next(v_rc2_prev_v, i_batt_a, r2_ohm, c2_f, dt)

        v_batt_v = v_ocv_v - i_batt_a * r0_ohm - v_rc1_v - v_rc2_v
        v_batt_v = max(v_batt_v, 1.0)
        p_batt_w = v_batt_v * i_batt_a

        soc_next = soc - (i_batt_a * dt) / (capacity_ah * 3600.0)
        soc_next = self._clamp(soc_next, soc_min, soc_max, "soc")

        self._state = {
            "soc": soc_next,
            "v_rc1_v": v_rc1_v,
            "v_rc2_v": v_rc2_v,
            "v_ocv_v": v_ocv_v,
        }
        self.t += dt

        return ModuleOutputs(
            soc=soc_next,
            v_batt_v=v_batt_v,
            i_batt_a=i_batt_a,
            p_batt_w=p_batt_w,
        )

    def get_state(self) -> dict:
        return dict(self._state)

    def validate_params(self) -> None:
        for key in (
            "capacity_kwh",
            "nominal_voltage_v",
            "max_charge_rate_c",
            "max_discharge_rate_c",
        ):
            if float(self.params.get(key, 0.0)) <= 0:
                raise ValueError(f"battery.{key} must be > 0")

        positive_optional = (
            "internal_resistance_ohm",
            "r0_ohm",
            "r1_ohm",
            "c1_f",
            "r2_ohm",
            "c2_f",
        )
        for key in positive_optional:
            if key in self.params and float(self.params[key]) <= 0:
                raise ValueError(f"battery.{key} must be > 0")

        soc_min = float(self.params.get("soc_min", 0.05))
        soc_max = float(self.params.get("soc_max", 0.98))
        if not (0 <= soc_min < soc_max <= 1):
            raise ValueError("battery SOC bounds must satisfy 0 <= soc_min < soc_max <= 1")
