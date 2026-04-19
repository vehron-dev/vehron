from vehron.resources import (
    list_packaged_archetypes,
    list_packaged_testcases,
    packaged_archetype_path,
    packaged_testcase_path,
)


def test_packaged_resource_helpers_expose_core_examples():
    assert "bev_car_sedan" in list_packaged_archetypes()
    assert "flat_highway_100kmh" in list_packaged_testcases()

    assert packaged_archetype_path("bev_car_sedan").name == "bev_car_sedan.yaml"
    assert packaged_testcase_path("flat_highway_100kmh").name == "flat_highway_100kmh.yaml"
