from vehron.modules.energy_storage.battery.ecm_2rc import Ecm2RcBatteryModel
from vehron.state import ModuleInputs, SimState


def test_ecm_2rc_battery_discharges_and_sags_under_load():
    module = Ecm2RcBatteryModel(
        {
            "capacity_kwh": 55.0,
            "nominal_voltage_v": 360.0,
            "internal_resistance_ohm": 0.05,
            "r1_ohm": 0.03,
            "c1_f": 6000.0,
            "r2_ohm": 0.04,
            "c2_f": 30000.0,
            "max_charge_rate_c": 2.0,
            "max_discharge_rate_c": 5.0,
            "soc_init": 0.9,
            "soc_min": 0.05,
            "soc_max": 0.98,
        }
    )
    module.validate_params()
    module.initialize(0.1)

    state = SimState(soc=0.9, p_drive_w=25000.0, p_hvac_w=1500.0, p_aux_w=500.0, p_regen_w=0.0)
    out_1 = module.step(state, ModuleInputs(), 0.5)
    out_2 = module.step(state, ModuleInputs(), 0.5)

    assert out_1.soc is not None and out_1.soc < 0.9
    assert out_1.i_batt_a is not None and out_1.i_batt_a > 0.0
    assert out_1.v_batt_v is not None and out_1.v_batt_v > 0.0
    assert out_2.v_batt_v is not None and out_1.v_batt_v > out_2.v_batt_v


def test_ecm_2rc_battery_charges_under_regen():
    module = Ecm2RcBatteryModel(
        {
            "capacity_kwh": 55.0,
            "nominal_voltage_v": 360.0,
            "internal_resistance_ohm": 0.05,
            "max_charge_rate_c": 2.0,
            "max_discharge_rate_c": 5.0,
            "soc_init": 0.6,
            "soc_min": 0.05,
            "soc_max": 0.98,
        }
    )
    module.validate_params()
    module.initialize(0.1)

    state = SimState(soc=0.6, p_drive_w=0.0, p_hvac_w=0.0, p_aux_w=0.0, p_regen_w=12000.0)
    out = module.step(state, ModuleInputs(), 0.5)

    assert out.soc is not None and out.soc > 0.6
    assert out.i_batt_a is not None and out.i_batt_a < 0.0
    assert out.p_batt_w is not None and out.p_batt_w < 0.0
