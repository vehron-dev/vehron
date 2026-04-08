"""Simulation engine coordinating module timestep execution."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from vehron.constants import DEFAULT_DT_S
from vehron.registry import get_battery_module_class, get_module_class
from vehron.state import ModuleInputs, ModuleOutputs, SimState


@dataclass
class SimulationResult:
    time_series: list[dict[str, Any]]
    final_state: SimState


class SimEngine:
    """Coordinator for BEV forward-time simulation."""

    def __init__(self, vehicle_cfg: dict[str, Any], testcase_cfg: dict[str, Any], project_root: Path | None = None) -> None:
        self.vehicle_cfg = vehicle_cfg
        self.testcase_cfg = testcase_cfg
        self.project_root = project_root or Path.cwd()
        self.sim_state = SimState()
        self.modules: dict[str, Any] = {}

        self.dt_s = float(testcase_cfg["simulation"].get("dt_s", DEFAULT_DT_S))
        self.max_duration_s = float(testcase_cfg["simulation"]["max_duration_s"])
        self._battery_charge_sum_w = 0.0
        self._battery_charge_samples = 0

        self._setup_initial_state()
        self._build_modules()

    def _setup_initial_state(self) -> None:
        internal = self.testcase_cfg.get("_internal", {})
        route = self.testcase_cfg["route"]
        battery = self.vehicle_cfg["battery"]

        self.sim_state.t_ambient_k = float(internal.get("ambient_temp_k", 298.15))
        self.sim_state.t_cabin_k = self.sim_state.t_ambient_k
        self.sim_state.t_batt_k = self.sim_state.t_ambient_k
        self.sim_state.t_motor_k = self.sim_state.t_ambient_k
        self.sim_state.t_coolant_k = self.sim_state.t_ambient_k

        self.sim_state.target_v_ms = float(internal.get("target_speed_ms", 0.0))
        self.sim_state.grade_rad = float(internal.get("grade_rad", 0.0))
        self.sim_state.soc = float(battery["soc_init"])

        self.target_distance_m = float(route["distance_km"]) * 1000.0
        self.stop_on_soc_min = bool(self.testcase_cfg["simulation"].get("stop_on_soc_min", True))
        self.soc_min = float(battery["soc_min"])

        self._drive_cycle_profile: list[tuple[float, float]] | None = None
        if route.get("mode") == "drive_cycle":
            self._drive_cycle_profile = self._load_drive_cycle(route.get("drive_cycle_file"))

    def _load_drive_cycle(self, cycle_file: str | None) -> list[tuple[float, float]]:
        if not cycle_file:
            return [(0.0, 0.0)]

        path = Path(cycle_file)
        if not path.is_absolute():
            path = self.project_root / path

        profile: list[tuple[float, float]] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.reader(line for line in handle if not line.startswith("#"))
            for row in reader:
                if len(row) < 2:
                    continue
                t_s = float(row[0])
                speed_ms = float(row[1]) / 3.6
                profile.append((t_s, speed_ms))

        if not profile:
            profile = [(0.0, 0.0)]
        return profile

    def _drive_cycle_target_speed(self, t_s: float) -> float:
        assert self._drive_cycle_profile is not None
        profile = self._drive_cycle_profile
        if len(profile) == 1:
            return profile[0][1]

        cycle_duration_s = profile[-1][0]
        if cycle_duration_s <= 0:
            return profile[-1][1]

        t_mod = t_s % cycle_duration_s
        for idx in range(1, len(profile)):
            t0, v0 = profile[idx - 1]
            t1, v1 = profile[idx]
            if t_mod <= t1:
                ratio = 0.0 if t1 == t0 else (t_mod - t0) / (t1 - t0)
                return v0 + ratio * (v1 - v0)
        return profile[-1][1]

    def _build_modules(self) -> None:
        vehicle = self.vehicle_cfg["vehicle"]

        driver_cls = get_module_class("driver", "pid_driver")
        long_cls = get_module_class("dynamics", "longitudinal")
        reducer_cls = get_module_class("reducer", "fixed_ratio")
        motor_cls = get_module_class("motor", self.vehicle_cfg["motor"]["model"])
        inverter_cls = get_module_class("inverter", "simple")
        regen_cls = get_module_class("regen", "blended_brake")
        battery_cls = get_battery_module_class(
            self.vehicle_cfg["battery"],
            self.project_root,
        )
        hvac_cls = get_module_class("hvac", self.vehicle_cfg["hvac"]["model"])
        aux_cls = get_module_class("aux", "dc_loads")
        batt_thermal_cls = get_module_class("thermal", "battery")
        motor_thermal_cls = get_module_class("thermal", "motor")
        coolant_cls = get_module_class("thermal", "coolant")

        longitudinal_params = {
            "mass_kg": vehicle["mass_kg"] + vehicle.get("payload_kg", 0.0),
            "frontal_area_m2": vehicle["frontal_area_m2"],
            "drag_coefficient": vehicle["drag_coefficient"],
            "wheel_radius_m": vehicle["wheel_radius_m"],
            "rolling_resistance_coeff": self.vehicle_cfg["tyre"]["rolling_resistance_coeff"],
            "max_drive_force_n": self.vehicle_cfg["motor"]["peak_torque_nm"] / vehicle["wheel_radius_m"],
            "max_brake_force_n": self.vehicle_cfg["motor"]["peak_torque_nm"] * 1.8 / vehicle["wheel_radius_m"],
            "drivetrain_efficiency": vehicle.get("drivetrain_efficiency", 0.95),
            "wind_speed_ms": self.testcase_cfg["environment"].get("wind_speed_ms", 0.0),
        }

        self.modules = {
            "driver": driver_cls({"kp": 0.9, "ki": 0.08, "kd": 0.02}),
            "dynamics": long_cls(longitudinal_params),
            "reducer": reducer_cls({
                "wheel_radius_m": vehicle["wheel_radius_m"],
                "primary_reduction_ratio": vehicle.get("primary_reduction_ratio", 1.0),
                "secondary_reduction_ratio": vehicle.get("secondary_reduction_ratio", 1.0),
                "transmission_efficiency": vehicle.get("transmission_efficiency", 0.97),
            }),
            "motor": motor_cls({
                **self.vehicle_cfg["motor"],
                "wheel_radius_m": vehicle["wheel_radius_m"],
            }),
            "inverter": inverter_cls({"efficiency": 0.97}),
            "regen": regen_cls({
                "max_regen_power_w": self.vehicle_cfg["motor"]["peak_power_kw"] * 1000.0 * 0.45,
                "regen_efficiency": 0.7,
            }),
            "battery": battery_cls(self.vehicle_cfg["battery"]),
            "battery_thermal": batt_thermal_cls({"tau_s": 600.0}),
            "motor_thermal": motor_thermal_cls({"tau_s": 450.0}),
            "coolant_loop": coolant_cls({"tau_s": 900.0}),
            "hvac": hvac_cls(self.vehicle_cfg["hvac"]),
            "aux_loads": aux_cls(self.vehicle_cfg["aux_loads"]),
        }

        for module in self.modules.values():
            module.validate_params()
            module.initialize(self.dt_s)

    @staticmethod
    def _apply_outputs(sim_state: SimState, outputs: ModuleOutputs) -> None:
        for field_name, field_value in outputs.__dict__.items():
            if field_value is not None:
                setattr(sim_state, field_name, field_value)

    def _update_energy_accumulators(self, dt_s: float) -> None:
        self.sim_state.e_drive_wh += max(self.sim_state.p_drive_w, 0.0) * dt_s / 3600.0
        self.sim_state.e_regen_wh += max(self.sim_state.p_regen_w, 0.0) * dt_s / 3600.0
        self.sim_state.e_hvac_wh += max(self.sim_state.p_hvac_w, 0.0) * dt_s / 3600.0
        self.sim_state.e_aux_wh += max(self.sim_state.p_aux_w, 0.0) * dt_s / 3600.0

    def _update_target_speed(self) -> None:
        route = self.testcase_cfg["route"]
        if route.get("mode") == "drive_cycle" and self._drive_cycle_profile is not None:
            self.sim_state.target_v_ms = self._drive_cycle_target_speed(self.sim_state.t)

    def _termination_reached(self) -> bool:
        if self.sim_state.distance_m >= self.target_distance_m:
            return True
        if self.sim_state.t >= self.max_duration_s:
            return True
        if self.stop_on_soc_min and self.sim_state.soc <= self.soc_min:
            return True
        return False

    def _external_charging_power_w(self, t_s: float) -> float:
        sim_cfg = self.testcase_cfg["simulation"]
        power_kw = float(sim_cfg.get("external_charging_power_kw", 0.0))
        start_s = float(sim_cfg.get("external_charging_start_s", 0.0))
        end_s = float(sim_cfg.get("external_charging_end_s", 0.0))
        if power_kw <= 0.0:
            return 0.0
        if end_s <= start_s:
            return 0.0
        if start_s <= t_s <= end_s:
            return power_kw * 1000.0
        return 0.0

    def run(self) -> SimulationResult:
        history: list[dict[str, Any]] = []
        active_modules = list(self.modules.items())
        n_steps = int(self.max_duration_s / self.dt_s) + 1

        for step_idx in range(n_steps):
            self._update_target_speed()
            p_external_charge_w = self._external_charging_power_w(self.sim_state.t)
            self._battery_charge_sum_w += p_external_charge_w
            self._battery_charge_samples += 1

            for _, module in active_modules:
                module.accumulate(self.sim_state)

            for name, module in active_modules:
                if step_idx % module.RATE_DIVISOR == 0:
                    module.flush_accumulator()
                    effective_dt = self.dt_s * module.RATE_DIVISOR
                    inputs = ModuleInputs()
                    if name == "battery":
                        avg_external_charge_w = (
                            self._battery_charge_sum_w / self._battery_charge_samples
                            if self._battery_charge_samples > 0
                            else 0.0
                        )
                        inputs = ModuleInputs(extras={"p_external_charge_w": avg_external_charge_w})
                        self._battery_charge_sum_w = 0.0
                        self._battery_charge_samples = 0
                    outputs = module.step(self.sim_state, inputs, effective_dt)
                    self._apply_outputs(self.sim_state, outputs)
                # else: sim_state retains last output from this module

            self.sim_state.t = (step_idx + 1) * self.dt_s
            self.sim_state.step_count = step_idx + 1
            self._update_energy_accumulators(self.dt_s)
            history.append(self.sim_state.to_dict())

            if self._termination_reached():
                break

        return SimulationResult(time_series=history, final_state=self.sim_state)
