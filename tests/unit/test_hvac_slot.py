from vehron.modules.hvac.base import HvacModelBase
from vehron.registry import get_hvac_module_class
from vehron.state import ModuleInputs, ModuleOutputs, SimState


class DummyHvacModel(HvacModelBase):
    def initialize(self, dt: float) -> None:
        self._state = {"mode": "off"}

    def step(self, sim_state: SimState, inputs: ModuleInputs, dt: float) -> ModuleOutputs:
        thermal_inputs = self.resolve_thermal_inputs(sim_state, inputs)
        return ModuleOutputs(
            p_hvac_w=max(thermal_inputs["solar_irradiance_wm2"] * 0.1, 0.0),
            t_cabin_k=thermal_inputs["t_cabin_k"],
        )

    def get_state(self) -> dict:
        return dict(self._state)

    def validate_params(self) -> None:
        return None


def test_hvac_slot_helper_reads_boundary_conditions():
    module = DummyHvacModel({})
    inputs = ModuleInputs(extras={"solar_irradiance_wm2": 800.0, "passenger_count": 2})
    state = SimState(t_ambient_k=308.15, t_cabin_k=300.15, v_ms=12.0)
    out = module.step(state, inputs, 1.0)

    assert out.p_hvac_w == 80.0
    assert out.t_cabin_k == 300.15


def test_hvac_slot_loads_private_stub(project_root):
    cls = get_hvac_module_class(
        {
            "model": "external",
            "external_module_path": "docs/examples/private_hvac_stub.py",
            "external_class_name": "PrivateHvacModel",
        },
        project_root,
    )
    assert issubclass(cls, HvacModelBase)
