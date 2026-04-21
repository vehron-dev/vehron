from vehron.modules.charging.ac_basic import AcBasicChargingModel
from vehron.state import ModuleInputs, SimState


def test_ac_charger_requests_power_in_cp_mode():
    module = AcBasicChargingModel(
        {
            "mode": "ac",
            "start_s": 0.0,
            "end_s": 3600.0,
            "target_soc": 0.8,
            "ac_power_limit_kw": 7.2,
            "charge_efficiency_ac": 0.95,
            "nominal_voltage_v": 350.0,
            "internal_resistance_ohm": 0.08,
            "termination_current_a": 5.0,
        }
    )
    module.validate_params()
    module.initialize(0.1)

    state = SimState(t=10.0, soc=0.5, v_batt_v=340.0, i_batt_a=0.0, t_batt_k=298.15)
    out = module.step(state, ModuleInputs(), 0.1)

    assert out.p_external_charge_w is not None and out.p_external_charge_w > 0.0
    assert out.charger_input_power_w is not None and out.charger_input_power_w > out.p_external_charge_w
    assert out.charge_state == "AC_CP"
    assert out.charger_mode == "ac"
    assert out.is_plugged_in is True


def test_ac_charger_stops_at_target_soc():
    module = AcBasicChargingModel(
        {
            "mode": "ac",
            "start_s": 0.0,
            "end_s": 3600.0,
            "target_soc": 0.6,
            "ac_power_limit_kw": 7.2,
            "charge_efficiency_ac": 0.95,
            "nominal_voltage_v": 350.0,
            "internal_resistance_ohm": 0.08,
            "termination_current_a": 5.0,
        }
    )
    module.validate_params()
    module.initialize(0.1)

    state = SimState(t=10.0, soc=0.61, v_batt_v=350.0, i_batt_a=0.0, t_batt_k=298.15)
    out = module.step(state, ModuleInputs(), 0.1)

    assert out.p_external_charge_w == 0.0
    assert out.charge_state == "DONE"
