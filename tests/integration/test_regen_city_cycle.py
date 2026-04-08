from vehron.engine import SimEngine
from vehron.loader import ConfigLoader


def test_city_cycle_produces_regen_energy(project_root):
    loader = ConfigLoader(project_root=project_root)
    vehicle_cfg, testcase_cfg = loader.load(
        project_root / "src/vehron/archetypes/bev_car_sedan.yaml",
        project_root / "src/vehron/testcases/city_wltp_class3.yaml",
    )

    engine = SimEngine(vehicle_cfg, testcase_cfg, project_root=project_root)
    result = engine.run()

    assert result.final_state.e_regen_wh > 0.0
