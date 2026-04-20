from vehron.loader import ConfigLoader
from vehron.engine import SimEngine


def test_loader_validates_and_converts(project_root):
    loader = ConfigLoader(project_root=project_root)
    vehicle, testcase = loader.load(
        project_root / "src/vehron/archetypes/bev_car_sedan.yaml",
        project_root / "src/vehron/testcases/flat_highway_100kmh.yaml",
    )

    assert vehicle["vehicle"]["powertrain"] == "bev"
    assert testcase["_internal"]["target_speed_ms"] > 0
    assert testcase["_internal"]["ambient_temp_k"] > 273.15


def test_loader_accepts_external_hvac_config(project_root, tmp_path):
    hvac_file = tmp_path / "private_hvac.py"
    hvac_file.write_text(
        (
            "from vehron.modules.hvac.base import HvacModelBase\n"
            "from vehron.state import ModuleOutputs\n\n"
            "class PrivateHvacModel(HvacModelBase):\n"
            "    def initialize(self, dt):\n"
            "        self._state = {'mode': 'off'}\n"
            "    def step(self, sim_state, inputs, dt):\n"
            "        return ModuleOutputs(p_hvac_w=0.0, t_cabin_k=sim_state.t_cabin_k)\n"
            "    def get_state(self):\n"
            "        return dict(self._state)\n"
            "    def validate_params(self):\n"
            "        pass\n"
        ),
        encoding="utf-8",
    )
    vehicle_yaml = tmp_path / "vehicle_external_hvac.yaml"
    vehicle_yaml.write_text(
        f"""
vehicle:
  name: "External HVAC Test Vehicle"
  archetype: car
  powertrain: bev
  mass_kg: 1450
  payload_kg: 120
  frontal_area_m2: 2.25
  drag_coefficient: 0.29
  wheel_radius_m: 0.316
  primary_reduction_ratio: 3.45
  secondary_reduction_ratio: 2.85
  transmission_efficiency: 0.96
  drivetrain_efficiency: 0.94

battery:
  model: rint
  capacity_kwh: 55.0
  nominal_voltage_v: 360
  internal_resistance_ohm: 0.08
  thermal_mass_kjk: 28.0
  max_charge_rate_c: 2.0
  max_discharge_rate_c: 5.0
  soc_init: 0.98
  soc_min: 0.05
  soc_max: 0.98

motor:
  model: analytical
  peak_power_kw: 160
  peak_torque_nm: 320
  max_speed_rpm: 14000
  base_efficiency: 0.93

tyre:
  model: rolling_resistance
  rolling_resistance_coeff: 0.009

hvac:
  model: external
  external_module_path: {hvac_file}
  external_class_name: PrivateHvacModel
  rated_power_kw: 4.5
  cabin_volume_m3: 2.8
  cop_cooling: 2.5
  cop_heating: 2.0
  cabin_setpoint_c: 22.0
  interior_thermal_mass_kjk: 75.0
  body_ua_wk: 120.0
  speed_ua_per_ms_wk: 3.0
  glazed_area_m2: 2.2
  solar_transmittance: 0.55
  fresh_air_ach: 8.0
  occupant_sensible_w: 75.0
  control_tau_s: 240.0

aux_loads:
  headlights_w: 80
  adas_w: 150
  infotainment_w: 60
  power_steering_w: 100
""",
        encoding="utf-8",
    )

    loader = ConfigLoader(project_root=project_root)
    vehicle = loader.load_vehicle(vehicle_yaml)

    assert vehicle["hvac"]["model"] == "external"
    assert vehicle["hvac"]["external_class_name"] == "PrivateHvacModel"


def test_engine_accepts_headered_drive_cycle_csv(project_root, tmp_path):
    cycle_path = tmp_path / "headered_cycle.csv"
    cycle_path.write_text(
        "time_s,speed_kmh\n0,0\n10,36\n20,0\n",
        encoding="utf-8",
    )

    testcase_path = tmp_path / "headered_drive_cycle.yaml"
    testcase_path.write_text(
        f"""
testcase:
  name: "Headered drive cycle"
  description: "Headered CSV should be accepted"

environment:
  ambient_temp_c: 25.0
  wind_speed_ms: 0.0
  wind_angle_deg: 0.0
  solar_irradiance_wm2: 0.0

route:
  mode: drive_cycle
  distance_km: 1.0
  grade_pct: 0.0
  target_speed_kmh: 0.0
  drive_cycle_file: {cycle_path}

payload:
  passengers: 0
  cargo_kg: 0.0

simulation:
  dt_s: 0.1
  max_duration_s: 60.0
  stop_on_soc_min: true
""",
        encoding="utf-8",
    )

    loader = ConfigLoader(project_root=project_root)
    vehicle, testcase = loader.load(
        project_root / "src/vehron/archetypes/bev_car_sedan.yaml",
        testcase_path,
    )

    engine = SimEngine(vehicle, testcase, project_root=project_root)

    assert engine._drive_cycle_profile is not None
    assert engine._drive_cycle_profile[0] == (0.0, 0.0)
    assert engine._drive_cycle_profile[1][0] == 10.0
    assert engine._drive_cycle_profile[1][1] == 10.0


def test_engine_applies_testcase_cargo_to_effective_mass(project_root):
    loader = ConfigLoader(project_root=project_root)
    vehicle, testcase = loader.load(
        project_root / "src/vehron/archetypes/bev_car_sedan.yaml",
        project_root / "src/vehron/testcases/flat_highway_100kmh.yaml",
    )

    engine = SimEngine(vehicle, testcase, project_root=project_root)

    mass_kg = float(engine.modules["dynamics"].params["mass_kg"])
    expected_mass_kg = (
        float(vehicle["vehicle"]["mass_kg"])
        + float(vehicle["vehicle"].get("payload_kg", 0.0))
        + float(testcase["payload"].get("cargo_kg", 0.0))
    )
    assert mass_kg == expected_mass_kg
