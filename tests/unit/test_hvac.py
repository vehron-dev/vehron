from vehron.modules.hvac.cabin_load import CabinLoadModel
from vehron.state import ModuleInputs, SimState


def test_hvac_draws_power_when_hot():
    module = CabinLoadModel(
        {
            "rated_power_kw": 4.0,
            "cop_cooling": 2.5,
            "cop_heating": 2.0,
            "cabin_setpoint_c": 22.0,
        }
    )
    module.validate_params()
    module.initialize(0.1)

    state = SimState(t_ambient_k=310.15, t_cabin_k=307.15)
    out = module.step(state, ModuleInputs(), 0.1)

    assert out.p_hvac_w is not None
    assert out.p_hvac_w > 0
