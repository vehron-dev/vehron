# ECM 2RC Battery Model

## Purpose

`ECM 2RC` is VEHRON's higher-fidelity in-repo BEV battery model compared with
the baseline `Rint` model. It remains lightweight enough for fast vehicle-level
simulation while capturing transient electrical behavior that a pure ohmic
model cannot represent well.

## What It Represents

The model includes:

- open-circuit voltage estimate as a function of SOC
- ohmic resistance term
- two RC polarization branches
- charge and discharge current limiting
- SOC integration over time

This structure captures:

- immediate voltage drop under load
- slower voltage relaxation dynamics
- recovery behavior after demand drops
- more realistic regen charging response

## Current Equation Structure

Conceptually, the terminal voltage is:

`V_terminal = V_ocv - I * R0 - V_rc1 - V_rc2`

Where:

- `V_ocv` is estimated from SOC
- `R0` is the ohmic resistance
- `V_rc1` and `V_rc2` are dynamic branch voltages

Each RC branch evolves toward `I * R` with its own time constant:

- `tau_1 = R1 * C1`
- `tau_2 = R2 * C2`

The implementation uses a stable exponential update form for each branch.

## Inputs

Required battery fields:

- `capacity_kwh`
- `nominal_voltage_v`
- `max_charge_rate_c`
- `max_discharge_rate_c`

Recommended ECM fields:

- `internal_resistance_ohm` or `r0_ohm`
- `r1_ohm`
- `c1_f`
- `r2_ohm`
- `c2_f`
- `ocv_empty_v`
- `ocv_full_v`

Optional:

- `ocv_shape_gain`
- `soc_init`
- `soc_min`
- `soc_max`

## Outputs

The model writes back:

- `soc`
- `v_batt_v`
- `i_batt_a`
- `p_batt_w`

It also keeps internal branch memory in module-private state.

## When To Use It

Use `ecm_2rc` when:

- transient battery voltage matters
- regen and load steps should look more realistic
- the plain `Rint` model is too simple
- you still want fast full-vehicle simulation

Stay with `rint` when:

- speed and simplicity matter more than transient detail
- you only need coarse energy and SOC trends

## Known Limitations

This is still a vehicle-level battery approximation, not a full
electrochemical pack model.

It does not yet include:

- temperature-dependent parameter maps
- ageing progression over repeated cycles
- explicit cell balancing behavior
- detailed charging taper physics
- full calibration workflow against measured pack datasets

## YAML Example

```yaml
battery:
  model: ecm_2rc
  capacity_kwh: 55.0
  nominal_voltage_v: 360
  internal_resistance_ohm: 0.05
  r1_ohm: 0.03
  c1_f: 6000
  r2_ohm: 0.04
  c2_f: 30000
  ocv_empty_v: 320
  ocv_full_v: 390
  max_charge_rate_c: 2.0
  max_discharge_rate_c: 5.0
  soc_init: 0.98
  soc_min: 0.05
  soc_max: 0.98
```

## Engineering Note

This page should be updated whenever the `ECM 2RC` implementation changes in a
way that affects equations, parameters, limits, or expected behavior.
