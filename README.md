# VEHRON

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19820111.svg)](https://doi.org/10.5281/zenodo.19820111)

VEHRON stands for **VEHicle Research and Optimisation Network**.

VEHRON is an open-source, modular, configuration-driven vehicle simulation
package focused on engineering studies such as:

- Energy consumption estimation
- Range and SOC trajectory prediction
- Powertrain and subsystem sizing studies
- Thermal trend analysis
- Test-case comparison across vehicle configurations

The guiding idea is simple:

- The **engine** coordinates simulation time and module execution.
- The **physics** lives in modules.
- Vehicle and experiment definitions come from **configuration files**.

This repository is currently in active development with a working BEV-focused
simulation path and fixed multi-rate scheduling support.

Start with the documented BEV path. That is the part of the repository that is
usable, tested, and intended for public reuse today.

## Install

VEHRON is currently installed from GitHub or from a local repository checkout.
It is not currently published on PyPI.

Fastest install from GitHub:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/vehron-dev/vehron.git
```

For users evaluating VEHRON from a local repository checkout:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

For contributors working on the codebase itself:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Then sanity-check the CLI:

```bash
vehron --help
```

## Case Directory Workflow

VEHRON now supports a case-directory workflow so that inputs, outputs, and
case notes live together.

Initialise the current directory as a case:

```bash
vehron init
```

Or create a new case directory:

```bash
vehron init hvac-design-v1
```

This writes:

- `.vehron-case`
- `README.md`
- `vehicle.yaml`
- `testcase.yaml`
- `output/`

Run the case with:

```bash
vehron run --case hvac-design-v1
```

When `--case` is used, VEHRON reads `vehicle.yaml` and `testcase.yaml` from
that directory and writes each run under `<case_dir>/output/`.

## Current Scope

VEHRON v1 should be understood as a **BEV-focused research software package**.

The active supported path today is:

- battery-electric vehicles (`powertrain: bev`)
- prescribed-speed longitudinal simulation
- YAML-defined vehicles and testcases
- parametric routes and drive-cycle CSV input using `time_s,speed_kmh`
- configurable in-repo battery, HVAC, motor, reducer, regen, auxiliary-load,
  and thermal-trend models
- external battery and HVAC models loaded from local Python files through
  documented slot interfaces
- self-contained case artifacts

VEHRON currently emphasizes:

- BEV energy, thermal-trend, and subsystem-loading studies
- standard-cycle and custom-cycle replay from stated `v(t)` inputs
- YAML-defined reference vehicles with auditable assumptions
- case artifacts that are easy to inspect, compare, and archive

If you are evaluating VEHRON for reuse, treat it as a modular BEV simulation
kernel with documented extension points and a clean case workflow.

## Reference Configurations

VEHRON uses YAML-defined reference vehicle configurations with fully stated
parameters. This keeps simulation assumptions auditable from the YAML
configuration alone.

The repository ships four WLTP reference cases and two MIDC reference cases
assembled from publicly available technical data for representative production
vehicles. Each case is defined entirely by its YAML file, with every assumption
stated.

| Case | Profile | Target WLTP | VEHRON result | Gap |
|------|---------|-------------|---------------|-----|
| A | Compact fastback, 84 kWh | 13.5 kWh/100 km | 13.21 kWh/100 km | −2.1% |
| B | Large fastback, 82 kWh | 14.3 kWh/100 km | 14.02 kWh/100 km | −2.0% |
| C | Compact SUV, 65 kWh | 18.0 kWh/100 km | 17.81 kWh/100 km | −1.1% |
| D | City hatchback, 52 kWh | 13.9 kWh/100 km | 13.78 kWh/100 km | −0.9% |

All four cases are run on the full 1800 s WLTP Class 3b cycle
(`data/drive_cycles/wltp_class3b.csv`). Every case output includes a
`summary.json` with a full energy budget breakdown: aero work, rolling
resistance work, inertia work, drive energy, regen recovered, aux, HVAC,
and net consumption in kWh/100 km.

The repository also ships the full MIDC `P1x4 + P2` cycle at
`data/drive_cycles/midc_p1x4_p2.csv` for Indian passenger-BEV studies, with
reference configurations for the Mahindra BE 6 and Tata Nexon EV LR.

## Capability Matrix

| Area | Supported Today | Experimental / Partial | Planned / Not Yet Supported |
| --- | --- | --- | --- |
| Powertrain scope | BEV active path | non-BEV code scaffolding present in repo | ICE / hybrid / FCEV public support |
| Vehicle classes | BEV sedan example and BEV-style studies | placeholder archetypes in repo | broad validated archetype library |
| Route input | parametric route, `time_s,speed_kmh` drive-cycle CSV | fixed route abstractions inside engine | GPS / lat-lon / elevation route ingestion |
| Battery models | `rint`, `ecm_2rc`, external battery slot via local Python file | advisory-driven charge-stop-resume control | degradation-aware built-in battery models |
| HVAC models | `cabin_load`, external HVAC slot via local Python file | low-order lumped thermal behavior | high-fidelity AC / heat-pump runtime models |
| Auxiliary and parasitic loads | YAML-configured `aux_loads` electrical parasitics | current model family is parameterized rather than plugin-based | broader parasitics framework |
| Thermal modeling | battery, motor, coolant trend states | low-order coupled trends only | detailed thermal network calibration |
| Outputs | case package, summary, timeseries, plots | current output schema still evolving | richer comparison/report workflows |
| Public reuse story | CLI-driven BEV studies, custom YAMLs, custom drive-cycle CSVs, external battery/HVAC Python models | direct use of internal core classes by advanced users, without stable public API guarantees | larger stable plugin ecosystem |

See also:

- [Public Interface](docs/public_interface.md)
- [Getting Started](docs/getting_started.md)
- [Validation and Limitations](docs/validation.md)
- [Reference Benchmarks](docs/benchmarks.md)
- [YAML Reference](docs/yaml_reference.md)

## License

VEHRON is licensed under `AGPL-3.0-only`.

This licensing choice reflects the project's origin as independent research
and engineering work developed without dedicated institutional sponsorship,
and is intended to preserve an open commons around the simulator as it
matures. VEHRON also provides external battery and HVAC model slots so that
users can integrate specialized subsystem implementations into the same
vehicle-level execution workflow. Users employing such integrations should
evaluate licensing and deployment obligations for their own context with
appropriate legal or compliance review.

Contributor guidance:

- see [CONTRIBUTING.md](/home/sn/02_git/vehron/CONTRIBUTING.md)

---

## 1. What VEHRON Is Designed To Do

VEHRON is designed as a **component-based simulator**, not a monolithic model. You can swap component models over time as fidelity improves.

### Core design principles

- **Modularity**: each subsystem (dynamics, motor, battery, HVAC, etc.) is a separate module.
- **Determinism**: same inputs produce same outputs.
- **Boundary conversion discipline**: boundary units are converted to SI internally.
- **Extensibility**: add or upgrade models without rewriting the core engine loop.
- **Config-driven operation**: vehicle and test case are defined by YAML files.

### Supported focus today

- Primary: **BEV active path** (`powertrain: bev`)
- Public emphasis: deterministic BEV duty-cycle simulation rather than broad powertrain coverage
- Planned next: broader archetype and route support after the BEV baseline is better documented and validated

---

## 2. Current Functional Scope (As Implemented)

The current pipeline supports a complete BEV simulation loop with these active model blocks:

- Prescribed-speed longitudinal motion from route or cycle input
- Longitudinal dynamics (traction, brake, rolling resistance, aero drag, grade)
- Fixed-ratio reduction drivetrain (primary + secondary reduction + efficiency)
- Motor model (analytical and map-based variant)
- Inverter efficiency model
- Blended regenerative braking model
- Battery electrical model (`Rint` and `ECM 2RC`)
- Aux DC loads
- Cabin HVAC load model with low-order thermal balance
- Simplified battery/motor/coolant thermal trend models
- Energy channel bookkeeping

Battery slot architecture:

- VEHRON keeps reference in-repo battery models: `RintBatteryModel` and `Ecm2RcBatteryModel`
- Third-party battery models can be loaded into the battery slot from a local Python file
- Private battery code does **not** need to live in this repository
- External battery models only need to implement the VEHRON battery slot interface
- The battery slot contract is defined by `BatteryModelBase`
- VEHRON can load a private battery class at runtime from a local Python file
- This lets a battery team keep proprietary pack physics outside GitHub while still running inside VEHRON

HVAC slot architecture:

- VEHRON keeps a reference in-repo HVAC model: `CabinLoadModel`
- Third-party HVAC or AC models can be loaded into the HVAC slot from a local Python file
- Private HVAC code does **not** need to live in this repository
- External HVAC models only need to implement the VEHRON HVAC slot interface
- The HVAC slot contract is defined by `HvacModelBase`
- VEHRON can load a private HVAC class at runtime from a local Python file

### Important note on maturity

This is an **engineering MVP** with a clear path for incremental fidelity
upgrades.

---

## 3. Multi-rate Integration Logic (Implemented)

VEHRON uses **fixed-step multi-rate integration**.

- Simulation has a master clock `dt` (default `0.1 s`).
- Each module defines `RATE_DIVISOR`.
- Module run interval = `master_dt * RATE_DIVISOR`.
- Between executions, module outputs are held (zero-order hold behavior).

### Why this exists

Different physics evolve at different time scales. Running all modules at the fastest rate is wasteful and often unnecessary.

### Accumulator behavior

For slow modules:

- `accumulate(sim_state)` is called every master step.
- `flush_accumulator()` finalizes buffered inputs right before `step()`.
- `step()` uses the interval-aggregated data.

Use:

- **Averages** for intensive quantities (temperature, current, voltage, speed)
- **Sums** for extensive quantities (energy, heat, distance)

### Current active module rates in BEV 4W run

- Dynamics: divisor `1` -> `0.1 s`
- Reducer: divisor `1` -> `0.1 s`
- Motor: divisor `1` -> `0.1 s`
- Inverter: divisor `1` -> `0.1 s`
- Regen: divisor `1` -> `0.1 s`
- Battery electrical: divisor `5` -> `0.5 s`
- Aux loads: divisor `10` -> `1.0 s`
- Battery thermal: divisor `20` -> `2.0 s`
- Motor thermal: divisor `20` -> `2.0 s`
- Coolant loop: divisor `100` -> `10.0 s`
- HVAC cabin: divisor `20` -> `2.0 s`

---

## 4. Inputs and Outputs

### Inputs to VEHRON

VEHRON currently takes two primary YAML inputs:

1. **Vehicle archetype YAML**
- Vehicle mass/geometry/aero
- Reduction ratios and drivetrain efficiency
- Motor parameters
- Battery parameters
- Optional external battery implementation path/class
- Optional external HVAC implementation path/class
- Tyre/HVAC/aux load parameters

2. **Test case YAML**
- Environment (ambient, wind)
- Route mode and constraints (parametric or drive-cycle)
- Payload and occupancy (`passengers`, `passenger_mass_kg`, `cargo_kg`)
- Simulation settings (`dt`, max duration, stop criteria)
- Optional external charging window:
  - `external_charging_power_kw`
  - `external_charging_start_s`
  - `external_charging_end_s`

Payload semantics in the active path:

- `passengers` contributes both cabin occupancy gains and longitudinal mass
- effective mission payload mass is `vehicle.payload_kg + cargo_kg + passengers * passenger_mass_kg`
- `passenger_mass_kg` defaults to `75.0` if omitted

Optional:

- Drive-cycle CSV (`time_s, speed_kmh`) for cycle-driven runs

For private battery plugins, the battery section can point to a local Python file:

```yaml
battery:
  model: external
  external_module_path: /absolute/or/relative/path/to/private_battery.py
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

For private HVAC plugins, the HVAC section can point to a local Python file:

```yaml
hvac:
  model: external
  external_module_path: /absolute/or/relative/path/to/private_hvac.py
  external_class_name: PrivateHvacModel
  rated_power_kw: 4.5
  cabin_volume_m3: 2.8
  cop_cooling: 2.5
  cop_heating: 2.0
  cabin_setpoint_c: 22.0
```

What VEHRON expects from an external battery model:

- The class must inherit from `BatteryModelBase`
- The class is loaded from `battery.external_module_path`
- The class name is taken from `battery.external_class_name`
- The battery module still behaves like a normal VEHRON module: it receives `sim_state`, `inputs`, and `effective_dt`
- VEHRON owns system-level mission demand; the battery model owns pack-level electrical and thermal response inside the battery slot

What VEHRON provides to the battery slot:

- Traction-side power demand
- Regen power request
- HVAC electrical load
- Auxiliary electrical load
- Optional external charging power
- Ambient and pack/coolant trend states already present in `SimState`

What the battery slot is expected to write back:

- Pack current
- Pack terminal voltage
- Net battery power
- SOC update
- Battery temperature-related state if the model owns it
- Any battery-side limits or internal states exposed through the VEHRON state contract

What VEHRON expects from an external HVAC model:

- The class must inherit from `HvacModelBase`
- The class is loaded from `hvac.external_module_path`
- The class name is taken from `hvac.external_class_name`
- The HVAC module still behaves like a normal VEHRON module: it receives `sim_state`, `inputs`, and `effective_dt`
- VEHRON owns route and environment context; the HVAC model owns cabin thermal and AC-side behavior inside the HVAC slot

What VEHRON provides to the HVAC slot:

- Ambient temperature
- Cabin temperature state
- Vehicle speed
- Solar irradiance
- Passenger count
- Any other shared thermal context already present in `SimState`

What the HVAC slot is expected to write back:

- HVAC electrical power `p_hvac_w`
- Cabin temperature `t_cabin_k`
- Any HVAC-side internal states exposed through the VEHRON state contract

### Outputs from VEHRON

Current outputs are:

- CLI summary (steps, distance, final SOC, total net energy)
- Full in-memory time series (available during run)
- Case artifacts (when saved as a case package):
  - `summary.json`
  - `timeseries.csv`
  - plots (`speed`, `SOC`, `power channels`, `thermal channels`)
  - copied input snapshots (`vehicle.yaml`, `testcase.yaml`)
  - case `README.md` with model/rate metadata

Charging and regen observability:

- Regenerative charging appears through positive `p_regen_w` and accumulated `e_regen_wh`.
- Net battery charging appears as negative `i_batt_a` and negative `p_batt_w`.
- External charging contributes through the optional testcase charging window fields.

---

## 5. Case Packaging Convention

Case-directory runs should be saved under:

- `<case_dir>/output/<run_name>/`

Legacy explicit-path runs still write under:

- `output/cases/<case_name>/`

Current naming style includes archetype explicitly, e.g.:

- `case_bev_car_sedan_flat_highway_YYYYMMDD_HHMMSS`

A case package should include:

- `README.md` describing run context and model stack
- `summary.json` with deterministic run metadata
- `timeseries.csv`
- `plots/` images
- input snapshots

---

## 6. Repository Layout (High-level)

- `src/vehron/`: main package
- `src/vehron/modules/`: physics modules
- `src/vehron/schemas/`: pydantic config schemas
- `src/vehron/archetypes/`: vehicle YAMLs
- `src/vehron/testcases/`: testcase YAMLs
- `data/`: maps and cycle files
- `tests/`: unit and integration tests
- `docs/`: architecture and references
- `CODEX.md`: project conventions and architecture contract

---

## 7. Development Setup

### Requirements

- Python 3.10+
- Virtual environment recommended

### Fresh install from GitHub

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/vehron-dev/vehron.git
```

### Fresh install from a local checkout

```bash
git clone https://github.com/vehron-dev/vehron.git
cd vehron
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

### Install (editable)

```bash
source .venv/bin/activate
pip install -e .
```

### Run one simple BEV 4W case

```bash
vehron run \
  --vehicle src/vehron/archetypes/bev_car_sedan.yaml \
  --testcase src/vehron/testcases/flat_highway_100kmh.yaml
```

### Run a reference configuration on the WLTP Class 3b cycle

```bash
vehron run \
  --vehicle src/vehron/archetypes/bev_reference_ioniq6.yaml \
  --testcase src/vehron/testcases/wltp_class3b_standard.yaml
```

All four reference archetypes (`bev_reference_ioniq6.yaml`,
`bev_reference_tesla_m3_lr_rwd.yaml`, `bev_reference_bmw_ix1_xdrive30.yaml`,
`bev_reference_renault5_52kwh.yaml`) can be paired with any supported testcase.
Parameters are fully stated in each YAML file.

### Run a reference configuration on the MIDC cycle

```bash
vehron run \
  --vehicle src/vehron/archetypes/bev_reference_tata_nexon_ev_lr.yaml \
  --testcase src/vehron/testcases/midc_standard.yaml
```

The packaged MIDC testcase uses the full `1180 s` `P1x4 + P2` cycle.

- [docs/battery_slot_interface.md](/home/sn/02_git/vehron/docs/battery_slot_interface.md)

### Private battery model hook

External battery implementations should subclass:

- [base.py](/home/sn/02_git/vehron/src/vehron/modules/energy_storage/battery/base.py)

VEHRON will load the class from `battery.external_module_path` at runtime as long as it inherits from `BatteryModelBase`.

This is the intended workflow for a private battery team:

1. Clone VEHRON and install it in a virtual environment.
2. Keep their proprietary battery file in a private path outside this repository if they want.
3. Point the vehicle YAML battery section to that file and class name.
4. Run VEHRON normally through `vehron run ...`.

VEHRON does not need the private battery code committed into this repository.

Example private battery configuration:

```yaml
battery:
  model: external
  external_module_path: /path/to/private_battery.py
  external_class_name: PrivateBatteryModel
  capacity_kwh: 55.0
  nominal_voltage_v: 360.0
  internal_resistance_ohm: 0.08
  max_charge_rate_c: 2.0
  max_discharge_rate_c: 5.0
  soc_init: 0.95
  soc_min: 0.05
  soc_max: 0.98
```

### Battery Team Quick Start

This is the shortest path for a third-party battery team to run a private pack model inside VEHRON.

1. Clone and install VEHRON:

```bash
git clone <your-vehron-repo-url>
cd vehron
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

2. Keep the private battery file in any local path, for example:

```text
/home/user/private_models/private_battery.py
```

3. Make sure the class inherits from `BatteryModelBase`.

4. Point the vehicle YAML to that private file:

```yaml
battery:
  model: external
  external_module_path: /home/user/private_models/private_battery.py
  external_class_name: PrivateBatteryModel
  capacity_kwh: 55.0
  nominal_voltage_v: 360.0
  internal_resistance_ohm: 0.08
  max_charge_rate_c: 2.0
  max_discharge_rate_c: 5.0
  soc_init: 0.95
  soc_min: 0.05
  soc_max: 0.98
```

5. Run VEHRON normally:

```bash
vehron run \
  --vehicle path/to/vehicle_with_private_battery.yaml \
  --testcase src/vehron/testcases/flat_highway_100kmh.yaml
```

Recommended handoff from the battery team:

- private Python file or package
- class name
- required configuration parameters and units
- any extra Python dependencies
- one smoke-test scenario with expected behavior

Starter template:

- [private_battery_stub.py](/home/sn/02_git/vehron/docs/examples/private_battery_stub.py)
- [private_hvac_stub.py](/home/sn/02_git/vehron/docs/examples/private_hvac_stub.py)
- [docs/hvac_slot_interface.md](/home/sn/02_git/vehron/docs/hvac_slot_interface.md)
- [docs/models/cabin_thermal_model.md](/home/sn/02_git/vehron/docs/models/cabin_thermal_model.md)
- [docs/references.md](/home/sn/02_git/vehron/docs/references.md)

### Run tests

```bash
pytest tests/unit tests/integration/test_bev_car_flat.py -q
```

---

## 8. What Physics Is Solved Today

Current solved/approximated physics:

- Longitudinal force balance and vehicle motion integration
- Aero drag and rolling resistance force effects
- Grade effect on tractive demand
- Drivetrain reduction mapping (wheel -> motor shaft)
- Motor/inverter conversion losses
- Regenerative braking power recovery limits
- Battery SOC/voltage/current under load and during charging (`Rint`, `ECM 2RC`)
- HVAC and auxiliary electrical loads
- Low-order cabin thermal balance with solar, envelope, ventilation, and occupant gains
- Simplified first-order thermal evolution

Not yet high-fidelity:

- Detailed tyre slip dynamics (Pacejka runtime integration)
- Detailed electrochemical battery dynamics
- Advanced cooling network and thermal coupling
- Full calibration against measured datasets

Important current battery-model limitations:

- The in-repo battery models are still low-order pack models, not full electrochemical pack solvers
- OCV is currently represented in a simplified way, not as a full SOC-temperature lookup surface
- Battery thermal output today is a pack-level trend state, not a resolved cell-core temperature model
- Cross-cycle ageing progression is expected to be handled by an external workflow for now

Important current HVAC-model limitations:

- The in-repo cabin model is a low-order single-zone lumped model
- Humidity and latent cooling load are not modeled yet
- Solar geometry and orientation-specific glazing effects are simplified
- Compressor-cycle detail and heat-pump maps are expected to be handled by richer future or external HVAC models

---

## 9. Roadmap Ahead

This is the intended sequence for practical progress.

### Phase A — Stabilize 4W BEV Baseline

- Freeze I/O contract for archetype + testcase YAML
- Add robust case export command
- Improve error messaging and validation diagnostics
- Add determinism checks and golden baseline runs
- Keep a small set of stable benchmark testcases for all supported archetypes

### Phase B — Improve 4W Physics Fidelity

- Richer motor map interpolation and boundary handling
- Better battery electrical/thermal coupling
- Add richer battery interface support for OCV tables, ageing-aware parameters, and tighter thermal coupling
- Tyre model switch support in active runtime flow
- More realistic regen blending and braking transitions

### Phase C — Validation and Confidence

- Energy closure and consistency tests across scenarios
- Reference-case benchmarking and calibration workflow
- Runtime performance profiling and optimization

### Phase D — 2W Enablement

- Add dedicated 2W archetypes and recommended parameter sets
- Ensure shared modules remain common across 4W and 2W
- Add 2W-specific validation test matrix

### Phase E — Reporting and UX

- Standard report generation (CSV/JSON/plots bundle)
- Extended CLI for run + export + compare workflows
- Better post-processing utilities

---

## 10. Current Status Summary

VEHRON currently has:

- A working BEV 4W simulation path
- A modular architecture with explicit module contracts
- Fixed multi-rate scheduler implementation
- Auditable YAML-defined reference vehicle configurations
- A hot-swappable battery slot for private third-party pack models
- Case artifact generation workflow
- Passing unit/integration baseline tests

The foundation is in place. The next value is in model calibration, fidelity upgrades, and 2W rollout.

---

## 11. Contribution Notes

If you add or modify models:

- Keep engine coordination free of subsystem physics equations.
- Follow module contract in `BaseModule`.
- Keep SI units internal.
- Add tests for every model behavior change.
- Keep configuration backward compatible unless versioning is explicitly updated.

Refer to `CODEX.md` for architecture and guardrails.

---

## 12. Quick Glossary

- **Archetype**: reusable vehicle configuration YAML
- **Testcase**: experiment condition YAML
- **Master dt**: global simulation clock step
- **RATE_DIVISOR**: module update ratio relative to master dt
- **Effective dt**: actual dt seen by a module (`master_dt * RATE_DIVISOR`)
- **Accumulator**: per-module input buffer used for slow modules
