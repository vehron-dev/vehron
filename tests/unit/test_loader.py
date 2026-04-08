from vehron.loader import ConfigLoader


def test_loader_validates_and_converts(project_root):
    loader = ConfigLoader(project_root=project_root)
    vehicle, testcase = loader.load(
        project_root / "src/vehron/archetypes/bev_car_sedan.yaml",
        project_root / "src/vehron/testcases/flat_highway_100kmh.yaml",
    )

    assert vehicle["vehicle"]["powertrain"] == "bev"
    assert testcase["_internal"]["target_speed_ms"] > 0
    assert testcase["_internal"]["ambient_temp_k"] > 273.15
