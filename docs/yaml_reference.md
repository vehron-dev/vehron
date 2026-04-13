# YAML Reference

## Purpose

VEHRON uses two YAML inputs:

- vehicle YAML for hardware, model selection, and subsystem parameters
- testcase YAML for route, environment, and simulation settings

This split is intentional. Vehicle definition should not be copied for every
mission case.

## Vehicle YAML

### `vehicle`

Core vehicle-level properties:

- `name`: descriptive vehicle name
- `archetype`: broad category such as `car`, `bus`, or `truck`
- `powertrain`: currently `bev` in the active validated path
- `mass_kg`: curb mass
- `payload_kg`: added mission payload
- `frontal_area_m2`: frontal area used for aero drag
- `drag_coefficient`: aerodynamic drag coefficient
- `wheel_radius_m`: effective driven wheel radius
- `primary_reduction_ratio`: first reduction stage
- `secondary_reduction_ratio`: second reduction stage
- `transmission_efficiency`: mechanical reduction efficiency
- `drivetrain_efficiency`: longitudinal drive force efficiency factor

### `battery`

Common battery fields:

- `model`: `rint`, `ecm_2rc`, or `external`
- `capacity_kwh`
- `nominal_voltage_v`
- `internal_resistance_ohm`
- `thermal_mass_kjk`
- `max_charge_rate_c`
- `max_discharge_rate_c`
- `soc_init`
- `soc_min`
- `soc_max`

Fields used for `external`:

- `external_module_path`
- `external_class_name`

Additional fields commonly used for `ecm_2rc`:

- `r0_ohm`: ohmic resistance; falls back to `internal_resistance_ohm`
- `r1_ohm`: first polarization branch resistance
- `c1_f`: first polarization branch capacitance
- `r2_ohm`: second polarization branch resistance
- `c2_f`: second polarization branch capacitance
- `ocv_empty_v`: estimated open-circuit voltage near low SOC
- `ocv_full_v`: estimated open-circuit voltage near high SOC
- `ocv_shape_gain`: optional shaping factor for nonlinear OCV behavior

Example:

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

### `motor`

- `model`: `analytical` or `efficiency_map`
- `map_file`
- `peak_power_kw`
- `peak_torque_nm`
- `max_speed_rpm`
- `base_efficiency`

### `tyre`

- `model`
- `rolling_resistance_coeff`
- `tyre_size`

### `hvac`

- `model`
- `rated_power_kw`
- `cabin_volume_m3`
- `cop_cooling`
- `cop_heating`
- `cabin_setpoint_c`

### `aux_loads`

- `headlights_w`
- `adas_w`
- `infotainment_w`
- `power_steering_w`

## Testcase YAML

### `environment`

- `ambient_temp_c`
- `wind_speed_ms`

### `route`

- `mode`
- `distance_km`
- `target_speed_kmh`
- `grade_pct`
- `drive_cycle_file`

### `simulation`

- `dt_s`
- `max_duration_s`
- `stop_on_soc_min`
- `external_charging_power_kw`
- `external_charging_start_s`
- `external_charging_end_s`

## Boundary Conversions

Some values are converted at the loader boundary before entering the simulation
state:

- `ambient_temp_c` -> Kelvin
- `target_speed_kmh` -> m/s
- `grade_pct` -> radians using `atan(grade_pct / 100)`

Internal simulation values should always be interpreted in SI units.

## Documentation Rule

If a YAML field changes meaning, is added, or is removed, this file must be
updated in the same PR as the code change.
