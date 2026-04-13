# Copyright (c) 2026 Subramanyam Natarajan
# SPDX-License-Identifier: AGPL-3.0-only

"""Rint battery model for BEV simulation."""

from __future__ import annotations

from vehron.modules.energy_storage.battery.base import BatteryModelBase
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class RintBatteryModel(BatteryModelBase):
    RATE_DIVISOR: int = 5

    def initialize(self, dt: float) -> None:
        self._state = {"soc": float(self.params.get("soc_init", 1.0))}
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

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        capacity_kwh = float(self.params["capacity_kwh"])
        nominal_voltage_v = float(self.params["nominal_voltage_v"])
        resistance_ohm = float(self.params["internal_resistance_ohm"])
        soc_min = float(self.params.get("soc_min", 0.05))
        soc_max = float(self.params.get("soc_max", 0.98))

        capacity_ah = capacity_kwh * 1000.0 / nominal_voltage_v
        i_discharge_max_a = capacity_ah * float(self.params.get("max_discharge_rate_c", 4.0))
        i_charge_max_a = capacity_ah * float(self.params.get("max_charge_rate_c", 2.0))

        if self._has_accumulated:
            p_drive_w = self._accumulated.get("p_drive_w", sim_state.p_drive_w)
            p_hvac_w = self._accumulated.get("p_hvac_w", sim_state.p_hvac_w)
            p_aux_w = self._accumulated.get("p_aux_w", sim_state.p_aux_w)
            p_regen_w = self._accumulated.get("p_regen_w", sim_state.p_regen_w)
        else:
            p_drive_w = sim_state.p_drive_w
            p_hvac_w = sim_state.p_hvac_w
            p_aux_w = sim_state.p_aux_w
            p_regen_w = sim_state.p_regen_w
        power_inputs = self.resolve_power_inputs(
            SimState(
                p_drive_w=p_drive_w,
                p_hvac_w=p_hvac_w,
                p_aux_w=p_aux_w,
                p_regen_w=p_regen_w,
            ),
            inputs,
        )
        p_net_w = power_inputs["p_net_w"]
        i_ideal_a = p_net_w / nominal_voltage_v if nominal_voltage_v > 0 else 0.0
        i_batt_a = self._clamp(i_ideal_a, -i_charge_max_a, i_discharge_max_a, "i_batt_a")

        soc = float(self._state.get("soc", sim_state.soc))
        if soc <= soc_min and i_batt_a > 0:
            i_batt_a = 0.0
        if soc >= soc_max and i_batt_a < 0:
            i_batt_a = 0.0

        v_batt_v = nominal_voltage_v - i_batt_a * resistance_ohm
        v_batt_v = max(v_batt_v, 1.0)
        p_batt_w = v_batt_v * i_batt_a

        soc_next = soc - (i_batt_a * dt) / (capacity_ah * 3600.0)
        soc_next = self._clamp(soc_next, soc_min, soc_max, "soc")

        self._state = {"soc": soc_next}
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
            "internal_resistance_ohm",
            "max_charge_rate_c",
            "max_discharge_rate_c",
        ):
            if float(self.params.get(key, 0.0)) <= 0:
                raise ValueError(f"battery.{key} must be > 0")

        soc_min = float(self.params.get("soc_min", 0.05))
        soc_max = float(self.params.get("soc_max", 0.98))
        if not (0 <= soc_min < soc_max <= 1):
            raise ValueError("battery SOC bounds must satisfy 0 <= soc_min < soc_max <= 1")
