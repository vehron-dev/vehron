# Adding a Module

## Goal

VEHRON modules are designed to be small, testable, and replaceable. The right
way to add a model is to fit it into the existing engine and state contract,
not to bypass the framework with special-case logic.

## Module Design Rules

Every module should:

- own one clear domain responsibility
- read from `SimState`
- return only its computed fields through `ModuleOutputs`
- validate its own parameters
- avoid mutating global state
- avoid hidden coupling to unrelated modules

Do not add logic directly into `SimEngine` just because a new model needs data.
If multiple modules need a new state variable, extend the state contract
deliberately and document it.

## Implementation Steps

1. Choose the subsystem and folder location under `src/vehron/modules/`.
2. Subclass the appropriate base pattern, usually `BaseModule` or
   `BatteryModelBase`.
3. Implement `initialize()`, `step()`, `get_state()`, and `validate_params()`.
4. Set `RATE_DIVISOR` if the model should run slower than the master timestep.
5. Register the module in `src/vehron/registry.py`.
6. Ensure the YAML schema can carry the needed parameters.
7. Add unit tests and, when useful, integration coverage.
8. Update the relevant docs in `docs/` in the same change.

## File-Level Expectations

A typical new module change touches:

- module implementation file
- registry
- schema or loader if new parameters are introduced
- archetype or example YAML if the feature should be demonstrated
- tests
- docs

## State and I/O Guidance

Before adding a new state field, ask:

- is this required for multiple modules or only one?
- is this a persistent state, a transient output, or a derived report field?
- does it belong in `SimState`, module-private state, or post-processing?

Use:

- `SimState` for shared runtime information across modules
- module private state for internal dynamics such as integrator memory
- post-processing outputs for derived metrics that are not needed in the loop

## Parameter Guidance

Parameters should enter through YAML and be validated explicitly.

Good:

- `r1_ohm`
- `rolling_resistance_coeff`
- `cop_cooling`

Bad:

- hidden hard-coded coefficients with no documentation
- parameters accepted by code but silently dropped by schema

If a model needs optional advanced parameters, make sure validation preserves
them rather than stripping them away.

## Testing Guidance

At minimum, new modules should have unit tests covering:

- parameter validation
- one nominal operating case
- one edge or limit case
- expected sign conventions

Add integration tests when the module changes system-level behavior in a way
that unit tests alone cannot protect.

## Documentation Requirement

Every new module or material fidelity change should update documentation in the
same PR. At minimum:

- what the model does
- what assumptions it makes
- what inputs it expects
- what outputs it writes
- what limitations remain

This is a hard requirement, not a nice-to-have.
