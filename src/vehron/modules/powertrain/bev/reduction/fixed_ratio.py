"""Fixed-ratio primary+secondary reduction model for BEV drivetrains."""

from __future__ import annotations

from vehron.modules.base import BaseModule
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class FixedRatioReducerModel(BaseModule):
    """Maps wheel interface torque/speed to motor shaft torque/speed."""
    RATE_DIVISOR: int = 1

    def initialize(self, dt: float) -> None:
        self._state = {
            "total_ratio": 1.0,
            "motor_power_mech_w": 0.0,
        }
        self.t = 0.0

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        primary_ratio = float(self.params.get("primary_reduction_ratio", 1.0))
        secondary_ratio = float(self.params.get("secondary_reduction_ratio", 1.0))
        transmission_efficiency = self._clamp(
            float(self.params.get("transmission_efficiency", 0.97)),
            0.5,
            1.0,
            "transmission_efficiency",
        )
        wheel_radius_m = float(self.params["wheel_radius_m"])

        total_ratio = primary_ratio * secondary_ratio
        wheel_speed_rads = sim_state.v_ms / wheel_radius_m if wheel_radius_m > 0 else 0.0
        motor_speed_rads = wheel_speed_rads * total_ratio

        wheel_torque_nm = sim_state.wheel_torque_nm
        if wheel_torque_nm >= 0.0:
            motor_torque_nm = wheel_torque_nm / max(total_ratio * transmission_efficiency, 1e-9)
        else:
            # Regen path carries gearbox losses in reverse direction.
            motor_torque_nm = wheel_torque_nm * transmission_efficiency / max(total_ratio, 1e-9)

        motor_power_mech_w = motor_torque_nm * motor_speed_rads

        self._state = {
            "total_ratio": total_ratio,
            "motor_power_mech_w": motor_power_mech_w,
        }
        self.t += dt

        return ModuleOutputs(
            motor_torque_nm=motor_torque_nm,
            motor_speed_rads=motor_speed_rads,
        )

    def get_state(self) -> dict:
        return dict(self._state)

    def validate_params(self) -> None:
        required_positive = [
            "wheel_radius_m",
            "primary_reduction_ratio",
            "secondary_reduction_ratio",
            "transmission_efficiency",
        ]
        for key in required_positive:
            if float(self.params.get(key, 0.0)) <= 0.0:
                raise ValueError(f"reduction.{key} must be > 0")
