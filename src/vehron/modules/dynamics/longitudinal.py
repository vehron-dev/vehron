"""Longitudinal vehicle dynamics for EV simulation."""

from __future__ import annotations

import math

from vehron.constants import AIR_DENSITY_KGM3, GRAVITY_MS2
from vehron.modules.base import BaseModule
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class LongitudinalDynamicsModel(BaseModule):
    RATE_DIVISOR: int = 1

    def initialize(self, dt: float) -> None:
        self._state = {
            "aero_force_n": 0.0,
            "rolling_force_n": 0.0,
            "grade_force_n": 0.0,
            "net_force_n": 0.0,
        }
        self.t = 0.0

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        mass_kg = float(self.params["mass_kg"])
        cd = float(self.params["drag_coefficient"])
        area_m2 = float(self.params["frontal_area_m2"])
        c_rr = float(self.params["rolling_resistance_coeff"])
        wheel_radius_m = float(self.params["wheel_radius_m"])
        max_drive_force_n = float(self.params["max_drive_force_n"])
        max_brake_force_n = float(self.params["max_brake_force_n"])
        drive_eta = float(self.params.get("drivetrain_efficiency", 0.95))
        wind_speed_ms = float(self.params.get("wind_speed_ms", 0.0))

        throttle = self._clamp(sim_state.throttle, 0.0, 1.0, "throttle")
        brake = self._clamp(sim_state.brake, 0.0, 1.0, "brake")

        rel_speed_ms = max(sim_state.v_ms - wind_speed_ms, 0.0)
        aero_force_n = 0.5 * AIR_DENSITY_KGM3 * cd * area_m2 * rel_speed_ms * rel_speed_ms
        rolling_force_n = mass_kg * GRAVITY_MS2 * c_rr * math.cos(sim_state.grade_rad) * (1.0 + 0.01 * sim_state.v_ms)
        grade_force_n = mass_kg * GRAVITY_MS2 * math.sin(sim_state.grade_rad)

        traction_force_n = throttle * max_drive_force_n * drive_eta
        brake_force_n = brake * max_brake_force_n

        net_force_n = traction_force_n - brake_force_n - aero_force_n - rolling_force_n - grade_force_n
        a_ms2 = net_force_n / mass_kg

        v_prev_ms = sim_state.v_ms
        v_ms = max(v_prev_ms + a_ms2 * dt, 0.0)
        v_avg_ms = 0.5 * (v_prev_ms + v_ms)
        distance_m = sim_state.distance_m + v_avg_ms * dt

        wheel_torque_nm = (traction_force_n - brake_force_n) * wheel_radius_m
        wheel_power_w = wheel_torque_nm * (v_avg_ms / wheel_radius_m) if wheel_radius_m > 0 else 0.0

        self._state = {
            "aero_force_n": aero_force_n,
            "rolling_force_n": rolling_force_n,
            "grade_force_n": grade_force_n,
            "net_force_n": net_force_n,
        }
        self.t += dt

        return ModuleOutputs(
            v_ms=v_ms,
            a_ms2=a_ms2,
            distance_m=distance_m,
            wheel_torque_nm=wheel_torque_nm,
            wheel_power_w=wheel_power_w,
        )

    def get_state(self) -> dict:
        return dict(self._state)

    def validate_params(self) -> None:
        required_positive = [
            "mass_kg",
            "frontal_area_m2",
            "drag_coefficient",
            "wheel_radius_m",
            "rolling_resistance_coeff",
            "max_drive_force_n",
            "max_brake_force_n",
        ]
        for key in required_positive:
            if float(self.params.get(key, 0.0)) <= 0:
                raise ValueError(f"{key} must be > 0")
