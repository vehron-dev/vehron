"""Module registry for VEHRON."""

from __future__ import annotations

from vehron.exceptions import ModuleRegistrationError
from vehron.modules.aux_loads.dc_loads import DcLoadsModel
from vehron.modules.driver.pid_driver import PidDriverModel
from vehron.modules.dynamics.aero import AeroDragModel
from vehron.modules.dynamics.grade import GradeForceModel
from vehron.modules.dynamics.longitudinal import LongitudinalDynamicsModel
from vehron.modules.dynamics.tyre.rolling_resistance import RollingResistanceModel
from vehron.modules.energy_storage.battery.rint import RintBatteryModel
from vehron.modules.hvac.cabin_load import CabinLoadModel
from vehron.modules.powertrain.bev.inverter.simple import SimpleInverterModel
from vehron.modules.powertrain.bev.motor.analytical import AnalyticalMotorModel
from vehron.modules.powertrain.bev.motor.efficiency_map import EfficiencyMapMotorModel
from vehron.modules.powertrain.bev.regen.blended_brake import BlendedBrakeRegenModel
from vehron.modules.thermal.battery_thermal import BatteryThermalModel
from vehron.modules.thermal.coolant_loop import CoolantLoopModel
from vehron.modules.thermal.motor_thermal import MotorThermalModel

MODULE_REGISTRY = {
    "driver:pid_driver": PidDriverModel,
    "dynamics:aero": AeroDragModel,
    "dynamics:grade": GradeForceModel,
    "dynamics:rolling_resistance": RollingResistanceModel,
    "dynamics:longitudinal": LongitudinalDynamicsModel,
    "motor:analytical": AnalyticalMotorModel,
    "motor:efficiency_map": EfficiencyMapMotorModel,
    "inverter:simple": SimpleInverterModel,
    "regen:blended_brake": BlendedBrakeRegenModel,
    "battery:rint": RintBatteryModel,
    "hvac:cabin_load": CabinLoadModel,
    "aux:dc_loads": DcLoadsModel,
    "thermal:battery": BatteryThermalModel,
    "thermal:motor": MotorThermalModel,
    "thermal:coolant": CoolantLoopModel,
}


def get_module_class(kind: str, model: str):
    """Lookup a module class by kind and model name."""
    key = f"{kind}:{model}"
    try:
        return MODULE_REGISTRY[key]
    except KeyError as exc:
        available = ", ".join(sorted(MODULE_REGISTRY.keys()))
        raise ModuleRegistrationError(
            f"Unknown module '{key}'. Available modules: {available}"
        ) from exc
