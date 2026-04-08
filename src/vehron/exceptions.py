"""Custom exception hierarchy for VEHRON."""


class VehronError(Exception):
    """Base exception for VEHRON errors."""


class ValidationError(VehronError):
    """Raised when user configuration is invalid."""


class ModuleRegistrationError(VehronError):
    """Raised when module registry lookups fail."""


class SimulationError(VehronError):
    """Raised when the simulator cannot proceed."""
