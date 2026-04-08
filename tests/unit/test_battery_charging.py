from vehron.modules.energy_storage.battery.rint import RintBatteryModel
from vehron.state import ModuleInputs, SimState


def test_rint_battery_external_charging_increases_soc():
    module = RintBatteryModel(
        {
            "capacity_kwh": 50.0,
            "nominal_voltage_v": 350.0,
            "internal_resistance_ohm": 0.08,
            "max_charge_rate_c": 2.0,
            "max_discharge_rate_c": 5.0,
            "soc_init": 0.5,
            "soc_min": 0.05,
            "soc_max": 0.98,
        }
    )
    module.validate_params()
    module.initialize(0.1)

    state = SimState(soc=0.5, p_drive_w=0.0, p_hvac_w=0.0, p_aux_w=0.0, p_regen_w=0.0)
    out = module.step(state, ModuleInputs(extras={"p_external_charge_w": 7000.0}), 1.0)

    assert out.soc is not None and out.soc > 0.5
    assert out.i_batt_a is not None and out.i_batt_a < 0.0
