# Getting Started

## Goal

This guide is the fastest outsider path to a successful first VEHRON run.

By the end you will:

- install VEHRON
- run a baseline BEV case
- inspect the outputs
- swap in a custom drive-cycle CSV

## 1. Install

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

If you intend to modify VEHRON itself rather than just evaluate it, use an
editable install instead:

```bash
pip install -e .
```

If you want to sanity-check the installed CLI, run:

```bash
vehron --help
```

## 2. Run The Baseline BEV Case

If you are working from a repository checkout, run:

```bash
vehron run \
  --vehicle src/vehron/archetypes/bev_car_sedan.yaml \
  --testcase src/vehron/testcases/flat_highway_100kmh.yaml
```

What this does:

- loads the active BEV sedan archetype
- runs a simple constant-speed highway testcase
- prints run progress in the terminal
- writes a case package under `output/cases/...`

## 3. Inspect The Output

After the run, inspect the newest case directory under:

```text
output/cases/
```

A case package includes:

- `summary.json`
- `timeseries.csv`
- `plots/`
- `vehicle.yaml`
- `testcase.yaml`
- `vehicle_resolved.yaml`
- `testcase_resolved.yaml`

## 4. Run A Standard Drive Cycle

```bash
vehron run \
  --vehicle src/vehron/archetypes/bev_car_sedan.yaml \
  --testcase src/vehron/testcases/wltp_class3b_standard.yaml
```

This uses the built-in drive-cycle route mode instead of a simple parametric
target speed.

## 5. Create A Custom Drive-Cycle CSV

Use the runnable example file:

```text
docs/examples/custom_drive_cycle.csv
```

Its contents are:

```csv
# time_s,speed_kmh
0,0
10,15
20,35
30,50
40,30
50,0
```

The active loader expects:

- column 1: elapsed time in seconds
- column 2: speed in km/h

## 6. Point A Testcase To Your Custom CSV

Use the runnable example testcase:

```text
docs/examples/custom_drive_cycle_testcase.yaml
```

Its structure is:

```yaml
testcase:
  name: Custom Cycle Demo
  description: Simple custom drive-cycle example

environment:
  ambient_temp_c: 25.0
  wind_speed_ms: 0.0
  solar_irradiance_wm2: 0.0

route:
  mode: drive_cycle
  distance_km: 5.0
  grade_pct: 0.0
  target_speed_kmh: 0.0
  drive_cycle_file: docs/examples/custom_drive_cycle.csv

simulation:
  dt_s: 0.1
  max_duration_s: 600.0
  stop_on_soc_min: true
```

Then run:

```bash
vehron run \
  --vehicle src/vehron/archetypes/bev_car_sedan.yaml \
  --testcase docs/examples/custom_drive_cycle_testcase.yaml
```

## 7. Change Vehicle Parameters

To study a different BEV, copy the sedan archetype and edit fields such as:

- `mass_kg`
- `drag_coefficient`
- `battery.capacity_kwh`
- `battery.model`
- `motor.peak_power_kw`
- `motor.peak_torque_nm`

Then rerun with your modified vehicle YAML.

## 8. Next Documents

Once the baseline workflow is working, continue with:

- [Examples](examples/README.md)
- [Public Interface](public_interface.md)
- [YAML Reference](yaml_reference.md)
- [Battery Slot Interface](battery_slot_interface.md)
- [HVAC Slot Interface](hvac_slot_interface.md)
- [Architecture](architecture.md)
