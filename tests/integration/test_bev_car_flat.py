from vehron.engine import SimEngine
from vehron.loader import ConfigLoader


def test_bev_flat_run_completes(project_root):
    loader = ConfigLoader(project_root=project_root)
    vehicle_cfg, testcase_cfg = loader.load(
        project_root / "src/vehron/archetypes/bev_car_sedan.yaml",
        project_root / "src/vehron/testcases/flat_highway_100kmh.yaml",
    )

    engine = SimEngine(vehicle_cfg, testcase_cfg, project_root=project_root)
    result = engine.run()

    assert result.final_state.step_count > 0
    assert result.final_state.distance_m > 0
    assert 0.0 <= result.final_state.soc <= 1.0


def test_engine_uses_driver_pid_gains_from_vehicle_yaml(project_root):
    loader = ConfigLoader(project_root=project_root)
    vehicle_cfg, testcase_cfg = loader.load(
        project_root / "src/vehron/archetypes/bev_car_sedan.yaml",
        project_root / "src/vehron/testcases/flat_highway_100kmh.yaml",
    )
    vehicle_cfg["driver"]["kp"] = 1.25
    vehicle_cfg["driver"]["ki"] = 0.11
    vehicle_cfg["driver"]["kd"] = 0.04

    engine = SimEngine(vehicle_cfg, testcase_cfg, project_root=project_root)

    assert engine.modules["driver"].params["kp"] == 1.25
    assert engine.modules["driver"].params["ki"] == 0.11
    assert engine.modules["driver"].params["kd"] == 0.04
