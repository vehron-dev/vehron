from vehron.modules.energy_storage.battery.rint import RintBatteryModel
from vehron.state import ModuleInputs, SimState


def test_rint_battery_discharges_soc_under_load():
    module = RintBatteryModel(
        {
            "capacity_kwh": 50.0,
            "nominal_voltage_v": 350.0,
            "internal_resistance_ohm": 0.08,
            "max_charge_rate_c": 2.0,
            "max_discharge_rate_c": 5.0,
            "soc_init": 0.9,
            "soc_min": 0.05,
            "soc_max": 0.98,
        }
    )
    module.validate_params()
    module.initialize(0.1)

    state = SimState(soc=0.9, p_drive_w=20000.0, p_hvac_w=2000.0, p_aux_w=500.0, p_regen_w=0.0)
    out = module.step(state, ModuleInputs(), 0.1)

    assert out.soc is not None and out.soc < 0.9
    assert out.i_batt_a is not None and out.i_batt_a > 0
