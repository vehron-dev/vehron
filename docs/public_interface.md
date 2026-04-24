# VEHRON Public Interface

## Purpose

This page defines the supported public-facing interfaces for VEHRON v1.

If you are using VEHRON as an outsider, this is the contract you should rely
on. Other internal files and helper functions may change more freely.

## Supported Public Interfaces

VEHRON v1 is primarily a CLI-driven, YAML-configured BEV simulation package.

The supported public interfaces are:

- the `vehron init` command
- the `vehron run` command
- the `vehron run --case <case_dir>` workflow
- vehicle YAML files
- testcase YAML files
- drive-cycle CSV input using `time_s,speed_kmh`
- case package outputs under `<case_dir>/output/...` or `output/cases/...`
- the external battery model slot
- the external HVAC model slot

## CLI

Current user-facing commands:

```bash
vehron init [case_dir_name]
```

```bash
vehron run --case <case_dir>
```

```bash
vehron run --vehicle <vehicle.yaml> --testcase <testcase.yaml>
```

`vehron init` creates a case directory containing:

- `.vehron-case`
- `README.md`
- `vehicle.yaml`
- `testcase.yaml`
- `output/`

`vehron run --case <case_dir>`:

- reads `<case_dir>/vehicle.yaml`
- reads `<case_dir>/testcase.yaml`
- writes run outputs under `<case_dir>/output/<run_name>/`

Legacy explicit-path form:

- `--vehicle`: path to a vehicle YAML file
- `--testcase`: path to a testcase YAML file

The CLI:

- validates configs
- runs the active BEV simulation path
- prints a spec sheet and live progress
- writes a case package with outputs

## Vehicle YAML Contract

Vehicle YAML defines:

- vehicle mass and geometry
- driver model and driver gains
- powertrain selection
- battery model and pack parameters
- motor model and motor parameters
- tyre model parameters
- HVAC parameters
- auxiliary electrical loads

Important scope note:

- `vehicle.powertrain` is currently supported only as `bev`

For field details see:

- [YAML Reference](yaml_reference.md)

## Testcase YAML Contract

Testcase YAML defines:

- testcase metadata
- environment conditions
- route mode and route inputs
- simulation settings
- payload including passenger count, passenger mass assumption, and cargo mass
- output preferences

Supported route forms today:

- parametric route definition
- drive-cycle speed trace CSV

For field details see:

- [YAML Reference](yaml_reference.md)

## Drive-Cycle CSV Contract

The active CSV route format is positional and expects:

- first column: `time_s`
- second column: `speed_kmh`

Notes:

- `time_s` is elapsed time from cycle start
- a literal header row `time_s,speed_kmh` is accepted
- lines starting with `#` are ignored
- extra columns are ignored by the active loader

## Output Contract

For the case-directory workflow, the default case package is written under:

- `<case_dir>/output/<case_name>/`

For legacy explicit-path runs, the default case package is written under:

- `output/cases/<case_name>/`

Current public output artifacts are:

- `summary.json`
- `timeseries.csv`
- plots under `plots/`
- copied input YAML files
- resolved YAML files
- case `README.md`

The output contract is documented in:

- [Output Contract](output_contract.md)

## External Battery Model Slot

External battery models are supported through:

- `battery.model: external`
- `battery.external_module_path`
- `battery.external_class_name`

The class must inherit from:

- `BatteryModelBase`

Further details:

- [Battery Slot Interface](battery_slot_interface.md)

## External HVAC Model Slot

External HVAC models are supported through:

- `hvac.model: external`
- `hvac.external_module_path`
- `hvac.external_class_name`

The class must inherit from:

- `HvacModelBase`

Further details:

- [HVAC Slot Interface](hvac_slot_interface.md)

## Internal vs Public

The following should be treated as public for v1:

- the CLI invocation above
- documented YAML fields
- documented route CSV format
- documented case package outputs
- documented battery/HVAC slot contracts

The following should be treated as internal implementation detail unless later
documented otherwise:

- internal helper functions
- undocumented module ordering assumptions
- placeholder module families outside the active BEV path
- repository presence of non-BEV folders or archetypes

## Scope Reminder

VEHRON v1 is a reusable BEV research software package if you use it within its
documented active scope. It is not yet a broad public vehicle-platform
framework across all powertrain classes.
