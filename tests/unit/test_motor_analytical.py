from vehron.constants import RPM_TO_RADS
from vehron.modules.powertrain.bev.motor.analytical import AnalyticalMotorModel
from vehron.state import ModuleInputs, SimState


def _module(**overrides):
    params = {
        "peak_power_kw": 100.0,
        "peak_torque_nm": 200.0,
        "max_speed_rpm": 12000.0,
        "wheel_radius_m": 0.31,
        "base_efficiency": 0.92,
    }
    params.update(overrides)
    module = AnalyticalMotorModel(params)
    module.validate_params()
    module.initialize(0.1)
    return module


def test_analytical_motor_holds_constant_torque_below_base_speed():
    module = _module()
    state = SimState(motor_speed_rads=200.0, motor_torque_nm=200.0)

    out = module.step(state, ModuleInputs(), 0.1)

    assert out.motor_torque_nm == 200.0
    assert module.get_state()["envelope_region"] == "constant_torque"


def test_analytical_motor_transitions_to_constant_power_above_base_speed():
    module = _module(base_speed_rpm=3000.0)
    motor_speed_rads = 6000.0 * RPM_TO_RADS
    requested_torque_nm = 250.0

    out = module.step(
        SimState(motor_speed_rads=motor_speed_rads, motor_torque_nm=requested_torque_nm),
        ModuleInputs(),
        0.1,
    )

    expected_limit_nm = (100.0 * 1000.0) / motor_speed_rads
    assert out.motor_torque_nm is not None
    assert abs(out.motor_torque_nm - expected_limit_nm) < 1e-6
    assert module.get_state()["envelope_region"] == "constant_power"


def test_analytical_motor_clamps_regen_with_regen_limits():
    module = _module(base_speed_rpm=3000.0, max_regen_power_kw=40.0, max_regen_torque_nm=120.0, regen_efficiency=0.8)
    motor_speed_rads = 6000.0 * RPM_TO_RADS

    out = module.step(
        SimState(motor_speed_rads=motor_speed_rads, motor_torque_nm=-150.0),
        ModuleInputs(),
        0.1,
    )

    expected_limit_nm = (40.0 * 1000.0) / motor_speed_rads
    assert out.motor_torque_nm is not None
    assert abs(out.motor_torque_nm + expected_limit_nm) < 1e-6
    assert out.p_drive_w == 0.0
    assert out.motor_efficiency == 0.8
    assert module.get_state()["envelope_region"] == "regen_constant_power"
