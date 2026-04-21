"""
vehron/state.py
---------------
SimState — the shared data bus passed to every module every timestep.

Rules:
- Modules READ from SimState. Only SimEngine WRITES to it.
- Think of this as the CAN bus of the simulation.
- All internal values are in SI units. No exceptions.
- Do not add fields without a MINOR version bump and CHANGELOG entry.
- Temperature fields are in Kelvin. Power fields are in Watts.
- Positive battery current = discharging. Negative = charging.
- Positive motor torque = driving. Negative = regenerating.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SimState:
    """
    Complete simulation state at a single timestep.
    Passed read-only to every module. Written by SimEngine only.
    """

    # ── Time ──────────────────────────────────────────────────────────────────
    t: float = 0.0
    """Simulation time, seconds."""

    step_count: int = 0
    """Number of timesteps completed."""

    # ── Vehicle motion ─────────────────────────────────────────────────────────
    v_ms: float = 0.0
    """Vehicle speed, m/s."""

    a_ms2: float = 0.0
    """Vehicle acceleration, m/s²."""

    distance_m: float = 0.0
    """Odometer distance travelled, metres."""

    grade_rad: float = 0.0
    """
    Road grade, radians. Positive = uphill. Negative = downhill.
    Convert from percent at YAML boundary: grade_rad = arctan(grade_pct / 100).
    """

    # ── Driver demand ──────────────────────────────────────────────────────────
    throttle: float = 0.0
    """Normalised throttle pedal position, 0.0 to 1.0."""

    brake: float = 0.0
    """Normalised brake pedal position, 0.0 to 1.0."""

    target_v_ms: float = 0.0
    """Speed demanded by the drive cycle or route profile, m/s."""

    # ── Wheel interface ────────────────────────────────────────────────────────
    wheel_torque_nm: float = 0.0
    """Net torque at the driven wheels, Nm. Positive = drive. Negative = regen."""

    wheel_power_w: float = 0.0
    """Net mechanical power at the driven wheels, W."""

    # ── Electrical bus (BEV / FCEV / hybrid) ──────────────────────────────────
    soc: float = 1.0
    """Battery state of charge, dimensionless, 0.0 to 1.0."""

    v_batt_v: float = 0.0
    """Battery terminal voltage, V."""

    i_batt_a: float = 0.0
    """
    Battery current, A.
    Positive = discharging (current flowing out to motor/loads).
    Negative = charging (regen or external charger).
    """

    p_batt_w: float = 0.0
    """
    Battery power, W.
    Positive = discharging. Negative = charging.
    p_batt_w = v_batt_v * i_batt_a
    """

    # ── Motor / inverter (BEV and HEV) ────────────────────────────────────────
    motor_torque_nm: float = 0.0
    """Motor shaft torque, Nm. Positive = motoring. Negative = generating."""

    motor_speed_rads: float = 0.0
    """Motor shaft angular speed, rad/s."""

    motor_efficiency: float = 1.0
    """Motor efficiency at current operating point, 0.0 to 1.0."""

    inverter_efficiency: float = 1.0
    """Inverter efficiency at current operating point, 0.0 to 1.0."""

    # ── ICE (internal combustion engine — ICE and HEV only) ───────────────────
    engine_speed_rads: float = 0.0
    """Engine crankshaft speed, rad/s."""

    engine_torque_nm: float = 0.0
    """Engine output torque, Nm."""

    fuel_flow_kgs: float = 0.0
    """Instantaneous fuel mass flow rate, kg/s."""

    fuel_consumed_kg: float = 0.0
    """Cumulative fuel consumed since simulation start, kg."""

    # ── Fuel cell (FCEV only) ──────────────────────────────────────────────────
    fc_power_w: float = 0.0
    """Fuel cell stack net electrical output power, W."""

    h2_consumed_kg: float = 0.0
    """Cumulative hydrogen consumed since simulation start, kg."""

    # ── Thermal ────────────────────────────────────────────────────────────────
    t_batt_k: float = 298.15
    """Battery pack bulk temperature, K."""

    t_motor_k: float = 298.15
    """Motor winding temperature, K."""

    t_coolant_k: float = 298.15
    """Coolant circuit bulk temperature, K."""

    t_cabin_k: float = 298.15
    """Cabin air temperature, K."""

    t_ambient_k: float = 298.15
    """Ambient air temperature, K. Set from testcase YAML at sim start."""

    # ── Power channels ─────────────────────────────────────────────────────────
    # Positive = power consumed from the primary energy source (battery/tank).
    # Regen is positive when energy is being recovered INTO the battery.

    p_drive_w: float = 0.0
    """Traction power drawn from battery/source, W."""

    p_regen_w: float = 0.0
    """Regenerated power recovered into battery, W. Positive = recovering."""

    p_hvac_w: float = 0.0
    """HVAC system power draw, W."""

    p_aux_w: float = 0.0
    """Total DC auxiliary loads (lighting, ADAS, infotainment, etc.), W."""

    p_thermal_mgmt_w: float = 0.0
    """Thermal management power (cooling pump, fans, heaters), W."""

    p_external_charge_w: float = 0.0
    """External battery-side charging power request, W. Positive = into battery."""

    charger_input_power_w: float = 0.0
    """Estimated charger input power on the wall/grid side, W."""

    is_plugged_in: bool = False
    """Whether the vehicle is presently connected to an external charger."""

    charger_mode: str = "none"
    """Selected charger mode for the current run, e.g. none or ac."""

    charge_state: str = "IDLE"
    """Charging controller state for logging and post-processing."""

    # ── Energy accumulators ────────────────────────────────────────────────────
    # Integrated over the run. Updated by the energy bookkeeper each timestep.

    e_drive_wh: float = 0.0
    """Cumulative traction energy, Wh."""

    e_regen_wh: float = 0.0
    """Cumulative regenerated energy recovered, Wh."""

    e_hvac_wh: float = 0.0
    """Cumulative HVAC energy, Wh."""

    e_aux_wh: float = 0.0
    """Cumulative auxiliary loads energy, Wh."""

    def total_energy_consumed_wh(self) -> float:
        """
        Total energy drawn from the primary source since start.
        e_regen_wh is subtracted because it was recovered back.
        """
        return (
            self.e_drive_wh
            + self.e_hvac_wh
            + self.e_aux_wh
            - self.e_regen_wh
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Serialise state to a flat dict for logging.
        Called by the logger every timestep.
        """
        return {
            "t": self.t,
            "step_count": self.step_count,
            "v_ms": self.v_ms,
            "v_kmh": self.v_ms * 3.6,
            "a_ms2": self.a_ms2,
            "distance_m": self.distance_m,
            "distance_km": self.distance_m / 1000.0,
            "grade_rad": self.grade_rad,
            "throttle": self.throttle,
            "brake": self.brake,
            "soc": self.soc,
            "v_batt_v": self.v_batt_v,
            "i_batt_a": self.i_batt_a,
            "p_batt_w": self.p_batt_w,
            "motor_torque_nm": self.motor_torque_nm,
            "motor_speed_rads": self.motor_speed_rads,
            "motor_efficiency": self.motor_efficiency,
            "engine_speed_rads": self.engine_speed_rads,
            "fuel_flow_kgs": self.fuel_flow_kgs,
            "fuel_consumed_kg": self.fuel_consumed_kg,
            "fc_power_w": self.fc_power_w,
            "h2_consumed_kg": self.h2_consumed_kg,
            "t_batt_k": self.t_batt_k,
            "t_batt_c": self.t_batt_k - 273.15,
            "t_motor_k": self.t_motor_k,
            "t_motor_c": self.t_motor_k - 273.15,
            "t_coolant_k": self.t_coolant_k,
            "t_coolant_c": self.t_coolant_k - 273.15,
            "t_cabin_k": self.t_cabin_k,
            "t_cabin_c": self.t_cabin_k - 273.15,
            "t_ambient_k": self.t_ambient_k,
            "t_ambient_c": self.t_ambient_k - 273.15,
            "p_drive_w": self.p_drive_w,
            "p_regen_w": self.p_regen_w,
            "p_hvac_w": self.p_hvac_w,
            "p_aux_w": self.p_aux_w,
            "p_thermal_mgmt_w": self.p_thermal_mgmt_w,
            "p_external_charge_w": self.p_external_charge_w,
            "charger_input_power_w": self.charger_input_power_w,
            "is_plugged_in": self.is_plugged_in,
            "charger_mode": self.charger_mode,
            "charge_state": self.charge_state,
            "e_drive_wh": self.e_drive_wh,
            "e_regen_wh": self.e_regen_wh,
            "e_hvac_wh": self.e_hvac_wh,
            "e_aux_wh": self.e_aux_wh,
            "total_energy_wh": self.total_energy_consumed_wh(),
        }


@dataclass
class ModuleInputs:
    """
    Explicit inputs passed to a specific module's step() call.
    Populated by SimEngine from SimState before calling each module.
    Modules should prefer reading SimState directly, but ModuleInputs
    can be used to pass pre-computed values or module-specific signals.
    """
    extras: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModuleOutputs:
    """
    Outputs returned by a module's step() call.
    SimEngine reads these and writes them back to SimState.
    Only populate the fields your module actually computes.
    Unpopulated fields stay as None and are ignored by the engine.
    """

    # Motion
    v_ms: float | None = None
    a_ms2: float | None = None
    distance_m: float | None = None

    # Driver
    throttle: float | None = None
    brake: float | None = None

    # Wheel
    wheel_torque_nm: float | None = None
    wheel_power_w: float | None = None

    # Electrical
    soc: float | None = None
    v_batt_v: float | None = None
    i_batt_a: float | None = None
    p_batt_w: float | None = None

    # Motor
    motor_torque_nm: float | None = None
    motor_speed_rads: float | None = None
    motor_efficiency: float | None = None
    inverter_efficiency: float | None = None

    # ICE
    engine_speed_rads: float | None = None
    engine_torque_nm: float | None = None
    fuel_flow_kgs: float | None = None
    fuel_consumed_kg: float | None = None

    # Fuel cell
    fc_power_w: float | None = None
    h2_consumed_kg: float | None = None

    # Thermal
    t_batt_k: float | None = None
    t_motor_k: float | None = None
    t_coolant_k: float | None = None
    t_cabin_k: float | None = None

    # Power channels
    p_drive_w: float | None = None
    p_regen_w: float | None = None
    p_hvac_w: float | None = None
    p_aux_w: float | None = None
    p_thermal_mgmt_w: float | None = None
    p_external_charge_w: float | None = None
    charger_input_power_w: float | None = None
    is_plugged_in: bool | None = None
    charger_mode: str | None = None
    charge_state: str | None = None

    # Energy accumulators
    e_drive_wh: float | None = None
    e_regen_wh: float | None = None
    e_hvac_wh: float | None = None
    e_aux_wh: float | None = None
