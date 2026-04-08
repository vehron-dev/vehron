"""
vehron/modules/base.py
----------------------
BaseModule — the contract every physics module must honour.

Rules:
- This file is frozen. Do not modify without a MAJOR version bump
  and explicit maintainer sign-off.
- Every physics module in vehron/modules/ must inherit from BaseModule.
- The engine only knows how to talk to BaseModule. Nothing else.
- Read the docstrings. They are the spec.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from vehron.state import SimState, ModuleInputs, ModuleOutputs


class BaseModule(ABC):
    """
    Abstract base class for all VEHRON physics modules.

    A module is a self-contained unit of physics. It receives the current
    simulation state, computes its outputs, and returns them. It never
    modifies SimState directly — the engine does that after collecting
    all outputs.

    Lifecycle:
        1. __init__(params)     — called once at simulation setup
        2. validate_params()    — called once, before initialize()
        3. initialize(dt)       — called once, after validate_params()
        4. step(...) x N        — called every timestep
        5. reset()              — called between runs if reusing the module

    Threading:
        Modules are not thread-safe by default. The engine calls them
        sequentially in the canonical order defined in CODEX.md.
    """

    def __init__(self, params: dict[str, Any]) -> None:
        """
        Store parameters and initialise internal state container.

        Args:
            params: Module configuration dict, loaded from vehicle YAML.
                    Schema validated by pydantic before this is called.
        """
        self.params: dict[str, Any] = params
        self.t: float = 0.0
        self._state: dict[str, Any] = {}
        self._logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

    # ── Abstract methods — every subclass must implement these ────────────────

    @abstractmethod
    def initialize(self, dt: float) -> None:
        """
        Prepare the module for simulation.

        Called once after validate_params() and before the first step().
        Use this to:
        - Pre-compute lookup tables or interpolators from params
        - Set initial conditions (temperatures, SOC, etc.)
        - Allocate internal arrays sized to dt

        Args:
            dt: Master timestep in seconds. Some modules need this to
                pre-size internal buffers or tune integrators.

        Raises:
            RuntimeError: If the module cannot initialise from its params.
                          Use clear, human-readable messages.
        """
        ...

    @abstractmethod
    def step(
        self,
        sim_state: SimState,
        inputs: ModuleInputs,
        dt: float,
    ) -> ModuleOutputs:
        """
        Advance the module by one timestep.

        This is the hot path. It is called thousands of times per simulation.
        Keep it fast. No file I/O, no allocations if avoidable, no pandas.

        Contract:
        - MUST be deterministic: same inputs → same outputs, always.
        - MUST NOT modify sim_state. Read from it, never write to it.
        - MUST NOT raise for physically plausible inputs.
          Clamp out-of-range values and log a warning instead.
        - MUST update self._state and self.t internally.
        - MUST return a ModuleOutputs — never a raw dict or None.

        Args:
            sim_state: Current simulation state. Read-only.
            inputs:    Module-specific inputs from the engine. Usually empty.
            dt:        Timestep in seconds.

        Returns:
            ModuleOutputs with the fields this module computes populated.
            Leave other fields as None — the engine ignores them.
        """
        ...

    @abstractmethod
    def get_state(self) -> dict[str, Any]:
        """
        Return the current internal state for logging.

        Called by the logger after each step(). Must return a flat dict
        with JSON-serialisable values only: float, int, str, bool, list.
        No numpy arrays, no nested dicts, no None values.

        Returns:
            Flat dict of internal state variables with descriptive keys.
            Include units in key names: e.g. "cell_temp_k", "soc_internal".
        """
        ...

    @abstractmethod
    def validate_params(self) -> None:
        """
        Validate module parameters before simulation starts.

        Called once by the loader after pydantic schema validation.
        Use this for cross-field validation that pydantic cannot express,
        and for physics-domain checks (e.g. capacity > 0, eta in 0–1).

        Raises:
            ValueError: With a clear, human-readable message describing
                        exactly which parameter is wrong and why.
                        Bad: raise ValueError("invalid params")
                        Good: raise ValueError(
                            f"battery.soc_min ({soc_min}) must be less than "
                            f"battery.soc_max ({soc_max})"
                        )
        """
        ...

    # ── Concrete methods — override only if needed ────────────────────────────

    def reset(self) -> None:
        """
        Reset module to initial conditions for a fresh simulation run.

        The default implementation clears internal state and resets time.
        Override this if your module has non-trivial initial conditions
        that need to be restored (e.g. SOC, temperature, integrator state).
        """
        self._state = {}
        self.t = 0.0

    def accumulate(self, sim_state: SimState) -> None:
        """
        Called every master step regardless of RATE_DIVISOR.
        Slow modules override this to buffer relevant SimState values
        between activations. Use averaging for intensive quantities
        (temperature, voltage, current) and summation for extensive
        quantities (heat generated, energy consumed).
        Default implementation does nothing — correct for fast modules
        with RATE_DIVISOR of 1.
        """
        pass

    def flush_accumulator(self) -> None:
        """
        Called by the engine immediately before step() on activation steps.
        Finalises buffered inputs into self._accumulated for step() to read.
        Default implementation does nothing.
        """
        pass

    # ── Protected helpers — available to all subclasses ───────────────────────

    def _clamp(self, value: float, low: float, high: float, name: str) -> float:
        """
        Clamp a value to [low, high] and log a warning if it was out of range.

        Use this inside step() instead of raising exceptions. Physically
        implausible inputs (e.g. SOC > 1.0 due to integration drift) should
        be clamped and noted, not crash the simulation.

        Args:
            value: The value to clamp.
            low:   Lower bound.
            high:  Upper bound.
            name:  Human-readable name for the warning message.

        Returns:
            Clamped value.
        """
        if value < low:
            self._logger.warning(
                "%s clamped from %.6g to lower bound %.6g",
                name, value, low,
            )
            return low
        if value > high:
            self._logger.warning(
                "%s clamped from %.6g to upper bound %.6g",
                name, value, high,
            )
            return high
        return value

    def _require_param(self, key: str) -> Any:
        """
        Retrieve a required parameter, raising clearly if it is missing.

        Args:
            key: Parameter key in self.params.

        Returns:
            Parameter value.

        Raises:
            ValueError: If the key is not present in self.params.
        """
        if key not in self.params:
            raise ValueError(
                f"{self.__class__.__name__}: required parameter "
                f"'{key}' is missing from module config."
            )
        return self.params[key]

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"t={self.t:.3f}s, "
            f"params={list(self.params.keys())})"
        )
    RATE_DIVISOR: int = 1
    """Module scheduling divisor relative to master timestep."""
