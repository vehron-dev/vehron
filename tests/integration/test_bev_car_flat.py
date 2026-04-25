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


def test_bev_flat_highway_reaches_and_holds_target_speed(project_root):
    loader = ConfigLoader(project_root=project_root)
    vehicle_cfg, testcase_cfg = loader.load(
        project_root / "src/vehron/archetypes/bev_car_sedan.yaml",
        project_root / "src/vehron/testcases/flat_highway_100kmh.yaml",
    )

    engine = SimEngine(vehicle_cfg, testcase_cfg, project_root=project_root)
    result = engine.run()

    target_speed_kmh = 100.0
    max_speed_kmh = max(float(row["v_kmh"]) for row in result.time_series)
    assert max_speed_kmh <= 100.1
    assert all(abs(float(row["v_kmh"]) - target_speed_kmh) <= 1e-9 for row in result.time_series)

def test_engine_uses_prescribed_speed_without_driver_module(project_root):
    loader = ConfigLoader(project_root=project_root)
    vehicle_cfg, testcase_cfg = loader.load(
        project_root / "src/vehron/archetypes/bev_car_sedan.yaml",
        project_root / "src/vehron/testcases/flat_highway_100kmh.yaml",
    )

    engine = SimEngine(vehicle_cfg, testcase_cfg, project_root=project_root)

    assert "driver" not in engine.modules
    assert float(testcase_cfg["_internal"]["target_speed_ms"]) > 0.0
