# VEHRON Architecture

## Purpose

VEHRON is a modular forward-time vehicle simulation framework aimed at rapid
engineering studies for road vehicles, with the active validated path currently
focused on battery electric vehicles (BEV). The project is designed around a
shared simulation state, interchangeable subsystem models, and fixed-step
execution so fidelity can be increased incrementally without rewriting the
engine loop.

The most important architectural principle is separation of concerns:

- `SimEngine` owns orchestration and time stepping.
- `SimState` is the shared state bus seen by all modules.
- Each module owns one domain behavior and returns only the outputs it computes.
- Configuration enters through validated YAML, not ad hoc runtime code.

## Active BEV Flow

The current active simulation path is:

1. Vehicle YAML and testcase YAML are loaded and validated.
2. Boundary-unit conversions are applied at the loader edge.
3. `SimEngine` builds the configured modules.
4. At each master timestep, modules accumulate inputs and execute according to
   their `RATE_DIVISOR`.
5. Module outputs are written back onto `SimState`.
6. Energy bookkeeping and termination checks are performed.
7. A flat timeseries history is emitted for reporting and exports.

The active BEV modules include:

- Driver speed tracking
- Longitudinal vehicle dynamics
- Fixed-ratio reduction drivetrain
- Motor model
- Inverter model
- Regen blending
- Battery model
- HVAC load
- Auxiliary DC loads
- Simplified thermal trend models

## Core Files

- `src/vehron/engine.py`: builds modules and runs the timestep loop.
- `src/vehron/state.py`: shared simulation bus and module I/O contract.
- `src/vehron/registry.py`: maps YAML `model` selections to module classes.
- `src/vehron/loader.py`: YAML loading, validation, and boundary conversions.
- `src/vehron/modules/`: domain models grouped by subsystem.

## Shared State Contract

`SimState` is the canonical interface between modules. Modules read the full
state and return `ModuleOutputs`, which the engine writes back to the shared
state after each module step. This pattern makes it easy to:

- replace one module without changing unrelated modules
- log a flat timeseries without special-case adapters
- export traces for external tools such as private battery models

Important conventions:

- All internal values are SI units.
- Temperature is stored in Kelvin.
- Positive battery current means discharge.
- Positive battery power means battery delivering power.
- Positive regen power means recovered power into the battery boundary.
- Positive grade means uphill.

## Multi-Rate Execution

VEHRON uses a fixed-step master clock and per-module execution divisors.

- Master timestep is `dt_s`, typically `0.1 s`.
- Every module declares `RATE_DIVISOR`.
- Effective module interval = `dt_s * RATE_DIVISOR`.
- Between executions, the last module outputs remain active.

This allows slower domains such as battery electrical updates or thermal trends
to run less often than fast control and vehicle-dynamics loops.

The engine also supports accumulation for slower modules:

- averaged quantities for power-like channels and intensive states
- buffered values are flushed just before the slow module executes

## Configuration Boundary

Vehicle definition and mission definition are intentionally separated:

- vehicle YAML describes the hardware and model selections
- testcase YAML describes route, environment, and simulation settings

This separation makes it possible to reuse the same vehicle across many duty
cycles and environments without touching the hardware definition.

## What Is Implemented vs Planned

Implemented today:

- BEV longitudinal energy simulation
- aero drag, rolling resistance, and grade
- motor, inverter, reducer, regen, HVAC, and aux loads
- in-repo `Rint` and `ECM 2RC` battery models
- thermal trend states for battery, motor, and coolant
- external private battery slot integration

Present in the repository but not the main validated path yet:

- broader non-BEV module scaffolding
- richer tyre dynamics beyond the active simplified runtime
- more advanced multi-energy powertrain composition

## Documentation Ownership Note

This file is part of VEHRON's canonical technical documentation. It should be
updated by engineering when simulation behavior or module boundaries change.
The website team may reformat, cross-link, and present this content, but they
should not reinterpret the technical meaning without engineering review.
