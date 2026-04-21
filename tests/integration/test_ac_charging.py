from vehron.engine import SimEngine
from vehron.loader import ConfigLoader


def test_ac_charging_run_increases_soc(project_root):
    loader = ConfigLoader(project_root=project_root)
    vehicle_cfg, testcase_cfg = loader.load(
        project_root / "src/vehron/archetypes/bev_car_sedan.yaml",
        project_root / "src/vehron/testcases/flat_highway_100kmh.yaml",
    )

    vehicle_cfg["battery"]["soc_init"] = 0.4
    vehicle_cfg["charging"]["ac_power_limit_kw"] = 7.2
    vehicle_cfg["charging"]["charge_efficiency_ac"] = 0.95
    testcase_cfg["charging"] = {
        "enabled": True,
        "mode": "ac",
        "start_s": 0.0,
        "end_s": 600.0,
        "target_soc": 0.5,
    }
    testcase_cfg["environment"]["ambient_temp_c"] = 22.0
    testcase_cfg["_internal"]["ambient_temp_k"] = 295.15
    testcase_cfg["environment"]["solar_irradiance_wm2"] = 0.0
    testcase_cfg["route"]["target_speed_kmh"] = 0.0
    testcase_cfg["_internal"]["target_speed_ms"] = 0.0
    testcase_cfg["simulation"]["max_duration_s"] = 120.0
    testcase_cfg["simulation"]["stop_on_soc_min"] = False
    testcase_cfg["payload"]["passengers"] = 0
    testcase_cfg["payload"]["cargo_kg"] = 0.0

    engine = SimEngine(vehicle_cfg, testcase_cfg, project_root=project_root)
    result = engine.run()

    assert "charger" in engine.modules
    assert result.final_state.soc > 0.4
    assert result.final_state.p_external_charge_w > 0.0
    assert result.final_state.charger_mode == "ac"
