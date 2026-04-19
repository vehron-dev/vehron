# Battery Slot Interface

VEHRON treats the battery electrical model as a pluggable slot.

## Goal

- Keep the reference `RintBatteryModel` in this repository.
- Allow private third-party battery models to be loaded locally at runtime.
- Avoid committing proprietary battery code into the VEHRON codebase.

## Required base class

External battery models must inherit from:

- [base.py](/home/sn/02_git/vehron/src/vehron/modules/energy_storage/battery/base.py)

The required class today is:

- `BatteryModelBase`

That means the external model must implement the normal VEHRON module contract:

- `initialize(dt)`
- `step(sim_state, inputs, dt)`
- `get_state()`
- `validate_params()`

Optional:

- `RATE_DIVISOR`
- `accumulate(sim_state)`
- `flush_accumulator()`

Optional but strongly recommended for mission charging control:

- expose battery advisories through `get_state()`

## Runtime loading

Set battery config as:

```yaml
battery:
  model: external
  external_module_path: /path/to/private_battery.py
  external_class_name: PrivateBatteryModel
  capacity_kwh: 55.0
  nominal_voltage_v: 360
  internal_resistance_ohm: 0.08
  max_charge_rate_c: 2.0
  max_discharge_rate_c: 5.0
  soc_init: 0.98
  soc_min: 0.05
  soc_max: 0.98
```

Notes:

- `external_module_path` may be absolute or relative to the VEHRON project root.
- `external_class_name` must exist in that Python file.
- The class must inherit from `BatteryModelBase`.

## Power boundary helper

`BatteryModelBase` includes a helper:

- `resolve_power_inputs(sim_state, inputs)`

This returns the canonical battery-side power channels:

- `p_drive_w`
- `p_hvac_w`
- `p_aux_w`
- `p_regen_w`
- `p_external_charge_w`
- `p_net_w`

Use it unless the external battery model intentionally defines a custom boundary interpretation.

## Optional charge advisories

`BatteryModelBase` also supports standardized advisory keys that the engine can
read from the battery model `get_state()` output:

- `charge_recommended`
- `charge_required`
- `max_charge_power_w`
- `max_discharge_power_w`
- `preferred_charge_power_w`
- `resume_charge_soc`
- `trigger_charge_soc`

These are mission-control hints, not direct routing commands.

The intended split is:

- the battery model owns pack physics and pack-side limits
- VEHRON mission control owns route stop, charge, and resume behavior

So the battery model does not directly stop the vehicle. It publishes state and
advisories, and VEHRON decides how to operate the simulated vehicle.

## Typical external battery workflow

1. Implement a battery class that inherits from `BatteryModelBase`.
2. Use `resolve_power_inputs()` inside `step()` unless a custom boundary is truly required.
3. Return `soc`, `v_batt_v`, `i_batt_a`, and `p_batt_w`.
4. Optionally expose advisories such as `charge_required` and `max_charge_power_w`.
5. Point the vehicle YAML battery section to the local file and class name.
6. Configure route and charging policy in the testcase YAML.
7. Run VEHRON through the CLI and inspect the case package under `output/cases/...`.

## Ownership split

- VEHRON owns the slot contract and integration.
- Third-party teams own their internal battery physics.
- VEHRON only requires slot compatibility, not source-code inclusion.
