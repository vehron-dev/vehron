# HVAC Slot Interface

VEHRON treats the HVAC model as a pluggable slot, just like the battery model.

For the literature basis of the in-repo reference cabin model, see
[Cabin Thermal Model](models/cabin_thermal_model.md) and [References](references.md).

## Goal

- Keep the reference `CabinLoadModel` in this repository.
- Allow private third-party HVAC or AC models to be loaded locally at runtime.
- Avoid committing proprietary HVAC code into the VEHRON codebase.

## Required Base Class

External HVAC models must inherit from:

- [base.py](/home/sn/02_git/vehron/src/vehron/modules/hvac/base.py)

The required class today is:

- `HvacModelBase`

That means the external model must implement the normal VEHRON module contract:

- `initialize(dt)`
- `step(sim_state, inputs, dt)`
- `get_state()`
- `validate_params()`

Optional:

- `RATE_DIVISOR`
- `accumulate(sim_state)`
- `flush_accumulator()`

## Runtime Loading

Set HVAC config as:

```yaml
hvac:
  model: external
  external_module_path: /path/to/private_hvac.py
  external_class_name: PrivateHvacModel
  rated_power_kw: 4.5
  cabin_volume_m3: 2.8
  cop_cooling: 2.5
  cop_heating: 2.0
  cabin_setpoint_c: 22.0
```

Notes:

- `external_module_path` may be absolute or relative to the VEHRON project root.
- `external_class_name` must exist in that Python file.
- The class must inherit from `HvacModelBase`.

Example stub:

- [private_hvac_stub.py](/home/sn/02_git/vehron/docs/examples/private_hvac_stub.py)

## Thermal Boundary Helper

`HvacModelBase` includes a helper:

- `resolve_thermal_inputs(sim_state, inputs)`

This returns the canonical HVAC-side boundary inputs:

- `t_ambient_k`
- `t_cabin_k`
- `vehicle_speed_ms`
- `solar_irradiance_wm2`
- `passenger_count`

Use it unless the external HVAC model intentionally defines a custom boundary interpretation.

## Ownership Split

- VEHRON owns the slot contract and integration.
- Third-party teams own their internal HVAC or AC physics.
- VEHRON only requires slot compatibility, not source-code inclusion.
