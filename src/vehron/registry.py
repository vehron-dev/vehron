# Copyright (C) 2026 Subramanyam Natarajan
# SPDX-License-Identifier: AGPL-3.0-only

"""Module registry for VEHRON."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from vehron.exceptions import ModuleRegistrationError
from vehron.modules.aux_loads.dc_loads import DcLoadsModel
from vehron.modules.driver.pid_driver import PidDriverModel
from vehron.modules.dynamics.aero import AeroDragModel
from vehron.modules.dynamics.grade import GradeForceModel
from vehron.modules.dynamics.longitudinal import LongitudinalDynamicsModel
from vehron.modules.dynamics.tyre.rolling_resistance import RollingResistanceModel
from vehron.modules.energy_storage.battery.base import BatteryModelBase
from vehron.modules.energy_storage.battery.ecm_2rc import Ecm2RcBatteryModel
from vehron.modules.energy_storage.battery.rint import RintBatteryModel
from vehron.modules.hvac.base import HvacModelBase
from vehron.modules.hvac.cabin_load import CabinLoadModel
from vehron.modules.powertrain.bev.inverter.simple import SimpleInverterModel
from vehron.modules.powertrain.bev.motor.analytical import AnalyticalMotorModel
from vehron.modules.powertrain.bev.motor.efficiency_map import EfficiencyMapMotorModel
from vehron.modules.powertrain.bev.reduction.fixed_ratio import FixedRatioReducerModel
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
    "reducer:fixed_ratio": FixedRatioReducerModel,
    "inverter:simple": SimpleInverterModel,
    "regen:blended_brake": BlendedBrakeRegenModel,
    "battery:rint": RintBatteryModel,
    "battery:ecm_2rc": Ecm2RcBatteryModel,
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


def get_battery_module_class(
    battery_cfg: dict[str, object],
    project_root: Path,
):
    """Resolve an in-repo or external private battery implementation."""
    model = str(battery_cfg.get("model", "rint"))
    if model != "external":
        return get_module_class("battery", model)

    module_path_value = battery_cfg.get("external_module_path")
    class_name_value = battery_cfg.get("external_class_name")
    if not module_path_value or not class_name_value:
        raise ModuleRegistrationError(
            "battery.external_module_path and battery.external_class_name "
            "must be set for external battery models"
        )

    module_path = Path(str(module_path_value))
    if not module_path.is_absolute():
        module_path = project_root / module_path
    if not module_path.exists():
        raise ModuleRegistrationError(
            f"External battery module file not found: {module_path}"
        )

    spec = importlib.util.spec_from_file_location(
        f"vehron_external_battery_{module_path.stem}",
        module_path,
    )
    if spec is None or spec.loader is None:
        raise ModuleRegistrationError(
            f"Unable to load external battery module from {module_path}"
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    class_name = str(class_name_value)
    if not hasattr(module, class_name):
        raise ModuleRegistrationError(
            f"External battery class '{class_name}' not found in {module_path}"
        )

    cls = getattr(module, class_name)
    if not isinstance(cls, type) or not issubclass(cls, BatteryModelBase):
        raise ModuleRegistrationError(
            f"External battery class '{class_name}' must inherit from "
            "BatteryModelBase"
        )

    return cls


def get_hvac_module_class(
    hvac_cfg: dict[str, object],
    project_root: Path,
):
    """Resolve an in-repo or external private HVAC implementation."""
    model = str(hvac_cfg.get("model", "cabin_load"))
    if model != "external":
        return get_module_class("hvac", model)

    module_path_value = hvac_cfg.get("external_module_path")
    class_name_value = hvac_cfg.get("external_class_name")
    if not module_path_value or not class_name_value:
        raise ModuleRegistrationError(
            "hvac.external_module_path and hvac.external_class_name "
            "must be set for external hvac models"
        )

    module_path = Path(str(module_path_value))
    if not module_path.is_absolute():
        module_path = project_root / module_path
    if not module_path.exists():
        raise ModuleRegistrationError(
            f"External hvac module file not found: {module_path}"
        )

    spec = importlib.util.spec_from_file_location(
        f"vehron_external_hvac_{module_path.stem}",
        module_path,
    )
    if spec is None or spec.loader is None:
        raise ModuleRegistrationError(
            f"Unable to load external hvac module from {module_path}"
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    class_name = str(class_name_value)
    if not hasattr(module, class_name):
        raise ModuleRegistrationError(
            f"External hvac class '{class_name}' not found in {module_path}"
        )

    cls = getattr(module, class_name)
    if not isinstance(cls, type) or not issubclass(cls, HvacModelBase):
        raise ModuleRegistrationError(
            f"External hvac class '{class_name}' must inherit from "
            "HvacModelBase"
        )

    return cls
