# Output Contract

## Purpose

This page describes the default case package produced by VEHRON runs.

## Case Package Location

For the case-directory workflow, VEHRON writes case outputs under:

- `<case_dir>/output/<case_name>/`

For legacy explicit-path runs, VEHRON writes case outputs under:

- `output/cases/<case_name>/`

## Standard Artifacts

Current default artifacts are:

- `summary.json`
- `timeseries.csv`
- `plots/`
- `vehicle.yaml`
- `testcase.yaml`
- `vehicle_resolved.yaml`
- `testcase_resolved.yaml`
- `README.md`

## Artifact Meaning

### `summary.json`

Compact run summary including values such as:

- vehicle name
- testcase name
- route mode
- target distance
- final distance
- initial and final SOC
- net energy
- regen energy
- charging-related summary fields when present

### `timeseries.csv`

Flat time-series export derived from `SimState.to_dict()`.

This includes channels such as:

- time
- speed
- acceleration
- distance
- SOC
- battery voltage/current/power
- traction, regen, HVAC, and auxiliary power
- external charging request, charger mode, and charge state when present
- key temperatures

### `plots/`

Current default plots are:

- motion
- SOC and idle state
- vehicle temperatures

### Input snapshots

`vehicle.yaml` and `testcase.yaml` preserve the original user-supplied inputs.

`vehicle_resolved.yaml` and `testcase_resolved.yaml` preserve the resolved
configuration used for the run.

## Stability Note

The case package structure above is the intended public-facing default output
for VEHRON v1 BEV studies.

If a future change alters file names, meanings, or required artifacts, this
document should be updated in the same change.
