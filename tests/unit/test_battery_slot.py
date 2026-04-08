import textwrap

from vehron.engine import SimEngine
from vehron.loader import ConfigLoader
from vehron.registry import get_battery_module_class
from vehron.state import ModuleOutputs


def test_external_battery_class_loads_from_private_file(tmp_path, project_root):
    external_file = tmp_path / "private_battery.py"
    external_file.write_text(
        textwrap.dedent(
            """
            from vehron.modules.energy_storage.battery.base import BatteryModelBase
            from vehron.state import ModuleOutputs


            class PrivateBatteryModel(BatteryModelBase):
                RATE_DIVISOR = 3

                def initialize(self, dt: float) -> None:
                    self._state = {"soc": self.params.get("soc_init", 1.0)}

                def step(self, sim_state, inputs, dt):
                    soc = float(self._state["soc"]) - 0.0001
                    self._state["soc"] = soc
                    return ModuleOutputs(
                        soc=soc,
                        v_batt_v=float(self.params["nominal_voltage_v"]),
                        i_batt_a=1.23,
                        p_batt_w=456.0,
                    )

                def get_state(self):
                    return dict(self._state)

                def validate_params(self) -> None:
                    pass
            """
        ),
        encoding="utf-8",
    )

    cls = get_battery_module_class(
        {
            "model": "external",
            "external_module_path": str(external_file),
            "external_class_name": "PrivateBatteryModel",
            "capacity_kwh": 55.0,
            "nominal_voltage_v": 360.0,
            "internal_resistance_ohm": 0.08,
            "max_charge_rate_c": 2.0,
            "max_discharge_rate_c": 5.0,
            "soc_init": 0.98,
            "soc_min": 0.05,
            "soc_max": 0.98,
        },
        project_root,
    )

    assert cls.__name__ == "PrivateBatteryModel"


def test_engine_can_use_external_battery_model(tmp_path, project_root):
    external_file = tmp_path / "private_battery.py"
    external_file.write_text(
        textwrap.dedent(
            """
            from vehron.modules.energy_storage.battery.base import BatteryModelBase
            from vehron.state import ModuleOutputs


            class PrivateBatteryModel(BatteryModelBase):
                def initialize(self, dt: float) -> None:
                    self._state = {"soc": float(self.params.get("soc_init", 1.0))}

                def step(self, sim_state, inputs, dt):
                    soc = max(float(self._state["soc"]) - 0.00005, float(self.params.get("soc_min", 0.05)))
                    self._state["soc"] = soc
                    return ModuleOutputs(
                        soc=soc,
                        v_batt_v=float(self.params["nominal_voltage_v"]),
                        i_batt_a=2.0,
                        p_batt_w=720.0,
                    )

                def get_state(self):
                    return dict(self._state)

                def validate_params(self) -> None:
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

    result = SimEngine(vehicle_cfg, testcase_cfg, project_root=project_root).run()

    assert result.final_state.step_count > 0
    assert result.final_state.v_batt_v == vehicle_cfg["battery"]["nominal_voltage_v"]
    assert result.final_state.soc < vehicle_cfg["battery"]["soc_init"]
