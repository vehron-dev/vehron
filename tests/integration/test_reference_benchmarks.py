from __future__ import annotations

import math
from pathlib import Path

from vehron.engine import SimEngine
from vehron.loader import ConfigLoader


REFERENCE_BENCHMARKS = [
    {
        "vehicle": "bev_car_sedan",
        "testcase": "flat_highway_100kmh",
        "distance_km": 25.000258,
        "soc_final": 0.882118,
        "energy_wh": 5384.604834,
        "regen_wh": 41.908068,
        "distance_tol": 0.05,
        "soc_tol": 0.005,
        "energy_tol": 120.0,
        "regen_tol": 25.0,
    },
    {
        "vehicle": "bev_car_sedan",
        "testcase": "city_wltp_class3",
        "distance_km": 8.000208,
        "soc_final": 0.955208,
        "energy_wh": 1365.709751,
        "regen_wh": 695.940273,
        "distance_tol": 0.05,
        "soc_tol": 0.005,
        "energy_tol": 120.0,
        "regen_tol": 120.0,
    },
]


def test_reference_benchmark_outputs_remain_within_tolerance(project_root: Path):
    loader = ConfigLoader(project_root=project_root)

    for benchmark in REFERENCE_BENCHMARKS:
        vehicle_cfg, testcase_cfg = loader.load(
            project_root / "src/vehron/archetypes" / f"{benchmark['vehicle']}.yaml",
            project_root / "src/vehron/testcases" / f"{benchmark['testcase']}.yaml",
        )

        result = SimEngine(vehicle_cfg, testcase_cfg, project_root=project_root).run()
        final = result.final_state

        assert math.isclose(
            final.distance_m / 1000.0,
            benchmark["distance_km"],
            abs_tol=benchmark["distance_tol"],
        ), benchmark
        assert math.isclose(
            final.soc,
            benchmark["soc_final"],
            abs_tol=benchmark["soc_tol"],
        ), benchmark
        assert math.isclose(
            final.total_energy_consumed_wh(),
            benchmark["energy_wh"],
            abs_tol=benchmark["energy_tol"],
        ), benchmark
        assert math.isclose(
            final.e_regen_wh,
            benchmark["regen_wh"],
            abs_tol=benchmark["regen_tol"],
        ), benchmark


def test_city_cycle_regen_exceeds_highway_regen(project_root: Path):
    loader = ConfigLoader(project_root=project_root)

    vehicle_cfg, city_testcase = loader.load(
        project_root / "src/vehron/archetypes/bev_car_sedan.yaml",
        project_root / "src/vehron/testcases/city_wltp_class3.yaml",
    )
    _, highway_testcase = loader.load(
        project_root / "src/vehron/archetypes/bev_car_sedan.yaml",
        project_root / "src/vehron/testcases/flat_highway_100kmh.yaml",
    )

    city_result = SimEngine(vehicle_cfg, city_testcase, project_root=project_root).run()
    highway_result = SimEngine(vehicle_cfg, highway_testcase, project_root=project_root).run()

    assert city_result.final_state.e_regen_wh > highway_result.final_state.e_regen_wh
    assert city_result.final_state.e_regen_wh > 100.0
