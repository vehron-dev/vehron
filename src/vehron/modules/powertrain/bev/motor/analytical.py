"""Analytical EV motor model."""

from __future__ import annotations

from vehron.constants import RPM_TO_RADS
from vehron.modules.base import BaseModule
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class AnalyticalMotorModel(BaseModule):
    RATE_DIVISOR: int = 1

    def initialize(self, dt: float) -> None:
        self._state = {
            "motor_power_mech_w": 0.0,
            "motor_power_elec_w": 0.0,
            "torque_limit_nm": 0.0,
            "envelope_region": "idle",
        }
        self.t = 0.0

    @staticmethod
    def _torque_limit_from_power(power_w: float, speed_rads: float, fallback_torque_nm: float) -> float:
        if speed_rads <= 1e-9:
            return fallback_torque_nm
        return power_w / speed_rads

    def _motoring_torque_limit_nm(
        self,
        peak_torque_nm: float,
        peak_power_w: float,
        base_speed_rads: float,
        motor_speed_rads: float,
    ) -> tuple[float, str]:
        if motor_speed_rads <= 0.0:
            return peak_torque_nm, "constant_torque"
        if motor_speed_rads <= base_speed_rads:
            return peak_torque_nm, "constant_torque"
        return (
            min(
                peak_torque_nm,
                self._torque_limit_from_power(peak_power_w, motor_speed_rads, peak_torque_nm),
            ),
            "constant_power",
        )

    def _regen_torque_limit_nm(
        self,
        max_regen_torque_nm: float,
        max_regen_power_w: float,
        base_speed_rads: float,
        motor_speed_rads: float,
    ) -> tuple[float, str]:
        if motor_speed_rads <= 0.0:
            return max_regen_torque_nm, "regen_constant_torque"
        if motor_speed_rads <= base_speed_rads:
            return max_regen_torque_nm, "regen_constant_torque"
        return (
            min(
                max_regen_torque_nm,
                self._torque_limit_from_power(max_regen_power_w, motor_speed_rads, max_regen_torque_nm),
            ),
            "regen_constant_power",
        )

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        peak_torque_nm = float(self.params["peak_torque_nm"])
        peak_power_w = float(self.params["peak_power_kw"]) * 1000.0
        max_speed_rads = float(self.params["max_speed_rpm"]) * RPM_TO_RADS
        wheel_radius_m = float(self.params["wheel_radius_m"])

        motor_speed_rads = sim_state.motor_speed_rads
        if motor_speed_rads <= 0.0:
            motor_speed_rads = sim_state.v_ms / wheel_radius_m if wheel_radius_m > 0 else 0.0
        motor_speed_rads = min(max(motor_speed_rads, 0.0), max_speed_rads)

        base_speed_rpm_value = self.params.get("base_speed_rpm")
        if base_speed_rpm_value is None:
            derived_base_speed_rads = peak_power_w / max(peak_torque_nm, 1e-9)
            base_speed_rads = min(max(derived_base_speed_rads, 1e-9), max_speed_rads)
        else:
            base_speed_rads = min(float(base_speed_rpm_value) * RPM_TO_RADS, max_speed_rads)

        max_regen_torque_value = self.params.get("max_regen_torque_nm")
        max_regen_torque_nm = float(max_regen_torque_value) if max_regen_torque_value is not None else peak_torque_nm
        max_regen_power_value = self.params.get("max_regen_power_kw")
        max_regen_power_w = (
            float(max_regen_power_value) * 1000.0
            if max_regen_power_value is not None
            else peak_power_w
        )

        requested_torque_nm = sim_state.motor_torque_nm
        if requested_torque_nm == 0.0:
            requested_torque_nm = sim_state.wheel_torque_nm

        if requested_torque_nm >= 0.0:
            torque_limit_nm, envelope_region = self._motoring_torque_limit_nm(
                peak_torque_nm,
                peak_power_w,
                base_speed_rads,
                motor_speed_rads,
            )
            motor_torque_nm = self._clamp(requested_torque_nm, 0.0, torque_limit_nm, "motor_torque_nm")
        else:
            torque_limit_nm, envelope_region = self._regen_torque_limit_nm(
                max_regen_torque_nm,
                max_regen_power_w,
                base_speed_rads,
                motor_speed_rads,
            )
            motor_torque_nm = self._clamp(requested_torque_nm, -torque_limit_nm, 0.0, "motor_torque_nm")

        mech_power_w = motor_torque_nm * motor_speed_rads

        load_frac = min(abs(motor_torque_nm) / peak_torque_nm, 1.0) if peak_torque_nm > 0 else 0.0
        speed_frac = min(motor_speed_rads / max_speed_rads, 1.0) if max_speed_rads > 0 else 0.0
        eta = float(self.params.get("base_efficiency", 0.93)) - 0.06 * (1.0 - load_frac) - 0.03 * speed_frac
        regen_efficiency_value = self.params.get("regen_efficiency")
        if mech_power_w < 0.0 and regen_efficiency_value is not None:
            eta = float(regen_efficiency_value)
        eta = self._clamp(
            eta,
            float(self.params.get("min_efficiency", 0.70)),
            float(self.params.get("max_efficiency", 0.98)),
            "motor_efficiency",
        )

        if mech_power_w > 0:
            p_drive_w = mech_power_w / eta
        else:
            p_drive_w = 0.0

        self._state = {
            "motor_power_mech_w": mech_power_w,
            "motor_power_elec_w": p_drive_w,
            "torque_limit_nm": torque_limit_nm,
            "envelope_region": envelope_region,
        }
        self.t += dt

        return ModuleOutputs(
            motor_torque_nm=motor_torque_nm,
            motor_speed_rads=motor_speed_rads,
            motor_efficiency=eta,
            p_drive_w=p_drive_w,
        )

    def get_state(self) -> dict:
        return dict(self._state)

    def validate_params(self) -> None:
        for key in ("peak_power_kw", "peak_torque_nm", "max_speed_rpm", "wheel_radius_m"):
            if float(self.params.get(key, 0.0)) <= 0:
                raise ValueError(f"motor.{key} must be > 0")
        for key in ("base_speed_rpm", "max_regen_power_kw", "max_regen_torque_nm"):
            if key in self.params and self.params.get(key) is not None and float(self.params[key]) <= 0:
                raise ValueError(f"motor.{key} must be > 0")
        for key in ("base_efficiency", "regen_efficiency", "min_efficiency", "max_efficiency"):
            if key in self.params and self.params.get(key) is not None:
                value = float(self.params[key])
                if not (0.0 < value <= 1.0):
                    raise ValueError(f"motor.{key} must satisfy 0 < value <= 1")
        min_efficiency = float(self.params.get("min_efficiency", 0.70))
        max_efficiency = float(self.params.get("max_efficiency", 0.98))
        if min_efficiency > max_efficiency:
            raise ValueError("motor.min_efficiency must be <= motor.max_efficiency")
