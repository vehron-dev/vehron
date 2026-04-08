from vehron.modules.powertrain.bev.motor.efficiency_map import EfficiencyMapMotorModel
from vehron.state import ModuleInputs, SimState


def test_efficiency_map_motor_uses_csv(project_root):
    module = EfficiencyMapMotorModel(
        {
            "peak_power_kw": 100.0,
            "peak_torque_nm": 220.0,
            "max_speed_rpm": 12000.0,
            "wheel_radius_m": 0.31,
            "map_file": str(project_root / "data/motor_maps/pmsm_160kw.csv"),
            "base_efficiency": 0.92,
        }
    )
    module.validate_params()
    module.initialize(0.1)

    state = SimState(v_ms=10.0, wheel_torque_nm=100.0)
    out = module.step(state, ModuleInputs(), 0.1)

    assert out.motor_efficiency is not None
    assert 0.7 <= out.motor_efficiency <= 0.98
