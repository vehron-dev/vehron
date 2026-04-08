from vehron.modules.powertrain.bev.reduction.fixed_ratio import FixedRatioReducerModel
from vehron.state import ModuleInputs, SimState


def test_fixed_ratio_reducer_maps_wheel_to_motor():
    module = FixedRatioReducerModel(
        {
            "wheel_radius_m": 0.3,
            "primary_reduction_ratio": 3.0,
            "secondary_reduction_ratio": 2.0,
            "transmission_efficiency": 0.95,
        }
    )
    module.validate_params()
    module.initialize(0.1)

    state = SimState(v_ms=12.0, wheel_torque_nm=240.0)
    out = module.step(state, ModuleInputs(), 0.1)

    assert out.motor_speed_rads is not None
    assert out.motor_torque_nm is not None
    assert out.motor_speed_rads > 0
    assert out.motor_torque_nm < state.wheel_torque_nm
