from vehron.modules.hvac.cabin_load import CabinLoadModel
from vehron.state import ModuleInputs, SimState


def test_hvac_draws_power_when_hot():
    module = CabinLoadModel(
        {
            "rated_power_kw": 4.0,
            "cabin_volume_m3": 2.8,
            "cop_cooling": 2.5,
            "cop_heating": 2.0,
            "cabin_setpoint_c": 22.0,
            "interior_thermal_mass_kjk": 75.0,
            "body_ua_wk": 120.0,
            "speed_ua_per_ms_wk": 3.0,
            "glazed_area_m2": 2.2,
            "solar_transmittance": 0.55,
            "fresh_air_ach": 8.0,
            "occupant_sensible_w": 75.0,
            "control_tau_s": 240.0,
            "solar_irradiance_wm2": 850.0,
            "passenger_count": 1,
        }
    )
    module.validate_params()
    module.initialize(0.1)

    state = SimState(t_ambient_k=310.15, t_cabin_k=307.15, v_ms=10.0)
    out = module.step(state, ModuleInputs(), 2.0)

    assert out.p_hvac_w is not None
    assert out.p_hvac_w > 0


def test_hvac_solar_gain_increases_cooling_power():
    common = {
        "rated_power_kw": 4.0,
        "cabin_volume_m3": 2.8,
        "cop_cooling": 2.5,
        "cop_heating": 2.0,
        "cabin_setpoint_c": 22.0,
        "interior_thermal_mass_kjk": 75.0,
        "body_ua_wk": 120.0,
        "speed_ua_per_ms_wk": 3.0,
        "glazed_area_m2": 2.2,
        "solar_transmittance": 0.55,
        "fresh_air_ach": 8.0,
        "occupant_sensible_w": 75.0,
        "control_tau_s": 240.0,
        "passenger_count": 1,
    }
    no_solar = CabinLoadModel({**common, "solar_irradiance_wm2": 0.0})
    high_solar = CabinLoadModel({**common, "solar_irradiance_wm2": 900.0})

    for module in (no_solar, high_solar):
        module.validate_params()
        module.initialize(0.1)

    state = SimState(t_ambient_k=307.15, t_cabin_k=299.15, v_ms=15.0)
    out_no_solar = no_solar.step(state, ModuleInputs(), 2.0)
    out_high_solar = high_solar.step(state, ModuleInputs(), 2.0)

    assert out_no_solar.p_hvac_w is not None
    assert out_high_solar.p_hvac_w is not None
    assert out_high_solar.p_hvac_w > out_no_solar.p_hvac_w


def test_hvac_heats_when_cabin_is_cold():
    module = CabinLoadModel(
        {
            "rated_power_kw": 4.0,
            "cabin_volume_m3": 2.8,
            "cop_cooling": 2.5,
            "cop_heating": 2.0,
            "cabin_setpoint_c": 22.0,
            "interior_thermal_mass_kjk": 75.0,
            "body_ua_wk": 120.0,
            "speed_ua_per_ms_wk": 3.0,
            "glazed_area_m2": 2.2,
            "solar_transmittance": 0.55,
            "fresh_air_ach": 8.0,
            "occupant_sensible_w": 75.0,
            "control_tau_s": 240.0,
            "solar_irradiance_wm2": 0.0,
            "passenger_count": 1,
        }
    )
    module.validate_params()
    module.initialize(0.1)

    state = SimState(t_ambient_k=273.15, t_cabin_k=289.15, v_ms=0.0)
    out = module.step(state, ModuleInputs(), 2.0)

    assert out.p_hvac_w is not None
    assert out.p_hvac_w > 0
    assert out.t_cabin_k is not None
    assert out.t_cabin_k > 289.15
