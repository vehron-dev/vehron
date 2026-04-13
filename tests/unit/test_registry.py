import pytest

from vehron.exceptions import ModuleRegistrationError
from vehron.registry import get_module_class


def test_registry_returns_module_class():
    cls = get_module_class("battery", "rint")
    assert cls.__name__ == "RintBatteryModel"


def test_registry_returns_ecm_battery_module_class():
    cls = get_module_class("battery", "ecm_2rc")
    assert cls.__name__ == "Ecm2RcBatteryModel"


def test_registry_unknown_module_raises():
    with pytest.raises(ModuleRegistrationError):
        get_module_class("battery", "does_not_exist")
