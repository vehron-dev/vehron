"""Analytical EV motor model."""

from __future__ import annotations

from vehron.constants import RPM_TO_RADS
from vehron.modules.base import BaseModule
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class AnalyticalMotorModel(BaseModule):
    def initialize(self, dt: float) -> None:
        self._state = {"motor_power_mech_w": 0.0, "motor_power_elec_w": 0.0}
        self.t = 0.0

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        peak_torque_nm = float(self.params["peak_torque_nm"])
        peak_power_w = float(self.params["peak_power_kw"]) * 1000.0
        max_speed_rads = float(self.params["max_speed_rpm"]) * RPM_TO_RADS
        wheel_radius_m = float(self.params["wheel_radius_m"])

        motor_speed_rads = sim_state.v_ms / wheel_radius_m if wheel_radius_m > 0 else 0.0
        motor_speed_rads = min(max(motor_speed_rads, 0.0), max_speed_rads)

        requested_torque_nm = sim_state.wheel_torque_nm
        motor_torque_nm = self._clamp(requested_torque_nm, -peak_torque_nm, peak_torque_nm, "motor_torque_nm")

        mech_power_w = motor_torque_nm * motor_speed_rads
        mech_power_w = self._clamp(mech_power_w, -peak_power_w, peak_power_w, "motor_mech_power_w")

        load_frac = min(abs(motor_torque_nm) / peak_torque_nm, 1.0) if peak_torque_nm > 0 else 0.0
        speed_frac = min(motor_speed_rads / max_speed_rads, 1.0) if max_speed_rads > 0 else 0.0
        eta = float(self.params.get("base_efficiency", 0.93)) - 0.06 * (1.0 - load_frac) - 0.03 * speed_frac
        eta = self._clamp(eta, 0.7, 0.98, "motor_efficiency")

        if mech_power_w > 0:
            p_drive_w = mech_power_w / eta
        else:
            p_drive_w = 0.0

        self._state = {
            "motor_power_mech_w": mech_power_w,
            "motor_power_elec_w": p_drive_w,
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
