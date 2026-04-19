# Reference Benchmarks

## Purpose

This page defines the current in-repo reference benchmark suite for VEHRON v1.

The goal is modest but important:

- give outsiders a few named cases they can rerun
- provide expected output ranges for regression checking
- distinguish real runnable reference studies from placeholder files

These benchmarks are **software regression references**, not proof of broad
physical validation.

## Reference Benchmark Set

The current v1 benchmark set is intentionally small and limited to the active
BEV path that actually runs in this repository.

### Benchmark 1: Flat Highway Sedan

- Vehicle: `bev_car_sedan`
- Testcase: `flat_highway_100kmh`
- Purpose: steady-state BEV highway cruise reference

Reference outputs from the current implementation:

- distance: about `25.00 km`
- final SoC: about `0.887`
- net energy: about `5104 Wh`
- regen energy: low but non-zero, about `33 Wh`

Expected interpretation:

- the vehicle should complete the full route
- energy use should be substantially higher than the city cycle benchmark
- regen should remain small because this is mostly steady cruise

### Benchmark 2: City Stop-Start Sedan

- Vehicle: `bev_car_sedan`
- Testcase: `city_wltp_class3`
- Purpose: stop-start urban duty cycle with visible regen contribution

Reference outputs from the current implementation:

- distance: about `8.00 km`
- final SoC: about `0.956`
- net energy: about `1337 Wh`
- regen energy: significant, about `692 Wh`

Expected interpretation:

- the cycle should complete successfully
- regen should be clearly non-zero and materially larger than in the highway
  case
- total energy use should be lower than the highway benchmark because the route
  is shorter and lower-speed

## Current Regression Policy

VEHRON integration tests currently treat these benchmark values as regression
references with tolerances rather than exact immutable scientific truths.

That means:

- small numerical movement is acceptable when justified by implementation
  changes
- large unexplained drift should fail tests and be investigated
- benchmark updates should happen in the same change that intentionally alters
  the model behavior

## What Is Not In The Benchmark Set

The following files are **not** part of the current benchmark set:

- placeholder archetypes that are not yet valid runnable mappings
- placeholder testcases that exist only as future-scope stubs
- non-BEV scaffolding not documented as supported

In practical terms, this means the benchmark set is currently narrower than the
set of filenames present in the repository.

## Placeholder Status

Several archetype and testcase YAML files still exist as placeholders. They
should not be interpreted as supported public studies until they are replaced by
real runnable configurations and added to tests and docs.

That is an honest limitation of the current repository.

## Recommended Use

If you are evaluating VEHRON after installation, the fastest reproducible
commands are:

```bash
vehron run-example --vehicle bev_car_sedan --testcase flat_highway_100kmh
vehron run-example --vehicle bev_car_sedan --testcase city_wltp_class3
```

If these do not run or their outputs drift well outside the documented ranges,
the public BEV reference path should be treated as unstable until explained.
