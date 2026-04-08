from vehron.modules.dynamics.longitudinal import LongitudinalDynamicsModel
from vehron.state import ModuleInputs, SimState


def test_longitudinal_accelerates_with_throttle():
    module = LongitudinalDynamicsModel(
        {
            "mass_kg": 1500,
            "frontal_area_m2": 2.2,
            "drag_coefficient": 0.3,
            "wheel_radius_m": 0.31,
            "rolling_resistance_coeff": 0.01,
            "max_drive_force_n": 4000,
            "max_brake_force_n": 6000,
        }
    )
    module.validate_params()
    module.initialize(0.1)

    state = SimState(v_ms=0.0, throttle=0.5, brake=0.0, grade_rad=0.0)
    out = module.step(state, ModuleInputs(), 0.1)

    assert out.v_ms is not None and out.v_ms > 0
    assert out.a_ms2 is not None and out.a_ms2 > 0
