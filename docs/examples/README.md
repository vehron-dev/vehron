# VEHRON Examples

This directory contains small public-facing examples for the active VEHRON v1
BEV workflow.

## Example Set

### 1. Baseline BEV Sedan

Run the baseline sedan on the built-in flat highway testcase:

```bash
vehron run \
  --vehicle src/vehron/archetypes/bev_car_sedan.yaml \
  --testcase src/vehron/testcases/flat_highway_100kmh.yaml
```

Use this when you want the simplest working baseline.

### 2. Custom Drive-Cycle Example

Files:

- `custom_drive_cycle.csv`
- `custom_drive_cycle_testcase.yaml`

Run:

```bash
vehron run \
  --vehicle src/vehron/archetypes/bev_car_sedan.yaml \
  --testcase docs/examples/custom_drive_cycle_testcase.yaml
```

Use this when you want to supply your own speed trace in the active CSV route
format.

### 3. External Battery Slot Example

Files:

- `private_battery_stub.py`
- `external_battery_vehicle.yaml`

Run:

```bash
vehron run \
  --vehicle docs/examples/external_battery_vehicle.yaml \
  --testcase src/vehron/testcases/flat_highway_100kmh.yaml
```

Use this when you want to see how an external battery model plugs into VEHRON.

### 4. External HVAC Slot Template

File:

- `private_hvac_stub.py`

This file is a template for custom HVAC integration. It is currently provided
as a slot example rather than a full vehicle+testcase workflow example.

## Notes

- The active route CSV format is positional: `time_s,speed_kmh`
- Lines starting with `#` are ignored by the current loader
- The notebooks in this directory are exploratory examples, not part of the
  minimal public onboarding path
