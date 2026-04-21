import pytest

from vehron.exceptions import ModuleRegistrationError
from vehron.registry import get_hvac_module_class, get_module_class


def test_registry_returns_module_class():
    cls = get_module_class("battery", "rint")
    assert cls.__name__ == "RintBatteryModel"


def test_registry_returns_ecm_battery_module_class():
    cls = get_module_class("battery", "ecm_2rc")
    assert cls.__name__ == "Ecm2RcBatteryModel"


def test_registry_returns_ac_charger_module_class():
    cls = get_module_class("charging", "ac_basic")
    assert cls.__name__ == "AcBasicChargingModel"


def test_registry_unknown_module_raises():
    with pytest.raises(ModuleRegistrationError):
        get_module_class("battery", "does_not_exist")


def test_registry_returns_external_hvac_module_class(project_root):
    cls = get_hvac_module_class(
        {
            "model": "external",
            "external_module_path": "docs/examples/private_hvac_stub.py",
            "external_class_name": "PrivateHvacModel",
        },
        project_root,
    )
    assert cls.__name__ == "PrivateHvacModel"
