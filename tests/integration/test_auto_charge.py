from __future__ import annotations

import textwrap

import yaml

from vehron.engine import SimEngine
from vehron.loader import ConfigLoader


def test_engine_auto_charge_with_builtin_battery(tmp_path, project_root):
    loader = ConfigLoader(project_root=project_root)
    vehicle_cfg, _ = loader.load(
        project_root / "src/vehron/archetypes/bev_car_sedan.yaml",
        project_root / "src/vehron/testcases/flat_highway_100kmh.yaml",
    )
    vehicle_cfg["battery"]["soc_init"] = 0.09

    testcase_path = tmp_path / "auto_charge_case.yaml"
    testcase_path.write_text(
        yaml.safe_dump(
            {
                "testcase": {"name": "Auto charge route", "description": "exercise stop charge resume"},
                "environment": {
                    "ambient_temp_c": 30.0,
                    "wind_speed_ms": 0.0,
                    "wind_angle_deg": 0.0,
                    "solar_irradiance_wm2": 0.0,
                },
                "route": {
                    "mode": "parametric",
                    "distance_km": 1.0,
                    "grade_pct": 0.0,
                    "target_speed_kmh": 60.0,
                },
                "payload": {"passengers": 1, "cargo_kg": 0.0},
                "simulation": {
                    "dt_s": 0.2,
                    "max_duration_s": 2000.0,
                    "stop_on_soc_min": True,
                    "external_charging_power_kw": 0.0,
                    "external_charging_start_s": 0.0,
                    "external_charging_end_s": 0.0,
                    "auto_charge": {
                        "enabled": True,
                        "trigger_soc": 0.1,
                        "resume_soc": 0.12,
                        "charger_power_kw": 60.0,
                    },
                },
                "outputs": {"time_series": True, "energy_audit": True, "plots": [], "report": False},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    testcase_cfg = loader.load_testcase(testcase_path)

    result = SimEngine(vehicle_cfg, testcase_cfg, project_root=project_root).run()

    assert result.final_state.distance_m >= 1000.0
    assert any(bool(row.get("auto_charge_active", False)) for row in result.time_series)
    assert max(int(row.get("charge_sessions", 0)) for row in result.time_series) >= 1


def test_external_battery_can_request_charge_via_advisories(tmp_path, project_root):
    external_file = tmp_path / "private_battery.py"
    external_file.write_text(
        textwrap.dedent(
            """
            from vehron.modules.energy_storage.battery.base import BatteryModelBase
            from vehron.state import ModuleOutputs


            class PrivateBatteryModel(BatteryModelBase):
                def initialize(self, dt: float) -> None:
                    self._state = {
                        "soc": float(self.params.get("soc_init", 0.2)),
                        "charge_required": False,
                        "max_charge_power_w": 25000.0,
                        "resume_charge_soc": 0.22,
                        "trigger_charge_soc": 0.18,
                    }

                def step(self, sim_state, inputs, dt):
                    nominal_voltage_v = float(self.params["nominal_voltage_v"])
                    capacity_kwh = float(self.params["capacity_kwh"])
                    capacity_ah = capacity_kwh * 1000.0 / nominal_voltage_v
                    power_inputs = self.resolve_power_inputs(sim_state, inputs)
                    i_batt_a = power_inputs["p_net_w"] / nominal_voltage_v if nominal_voltage_v > 0 else 0.0
                    soc = float(self._state["soc"])
                    soc_next = soc - (i_batt_a * dt) / (capacity_ah * 3600.0)
                    soc_next = min(max(soc_next, float(self.params.get("soc_min", 0.05))), float(self.params.get("soc_max", 0.98)))
                    self._state["soc"] = soc_next
                    self._state["charge_required"] = soc_next <= 0.18
                    return ModuleOutputs(
                        soc=soc_next,
                        v_batt_v=nominal_voltage_v,
                        i_batt_a=i_batt_a,
                        p_batt_w=nominal_voltage_v * i_batt_a,
                    )

                def get_state(self):
                    return dict(self._state)

                def validate_params(self):
                    pass
            """
        ),
        encoding="utf-8",
    )

    loader = ConfigLoader(project_root=project_root)
    vehicle_cfg, testcase_cfg = loader.load(
        project_root / "src/vehron/archetypes/bev_car_sedan.yaml",
        project_root / "src/vehron/testcases/flat_highway_100kmh.yaml",
    )
    vehicle_cfg["battery"]["model"] = "external"
    vehicle_cfg["battery"]["external_module_path"] = str(external_file)
    vehicle_cfg["battery"]["external_class_name"] = "PrivateBatteryModel"
    vehicle_cfg["battery"]["soc_init"] = 0.17

    testcase_cfg["route"]["distance_km"] = 0.8
    testcase_cfg["route"]["target_speed_kmh"] = 40.0
    testcase_cfg["simulation"]["dt_s"] = 0.2
    testcase_cfg["simulation"]["max_duration_s"] = 2000.0
    testcase_cfg["simulation"]["auto_charge"] = {
        "enabled": True,
        "trigger_soc": 0.18,
        "resume_soc": 0.21,
        "charger_power_kw": 80.0,
    }

    result = SimEngine(vehicle_cfg, testcase_cfg, project_root=project_root).run()

    assert result.final_state.distance_m >= 800.0
    assert max(int(row.get("charge_sessions", 0)) for row in result.time_series) >= 1
    assert max(float(row.get("charge_time_s", 0.0)) for row in result.time_series) > 0.0
