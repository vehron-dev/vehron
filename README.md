# VEHRON

VEHRON stands for **VEHicle Research and Optimisation Network**.

VEHRON is an open-source, modular, forward-time vehicle simulation framework focused on engineering use-cases such as:

- Energy consumption estimation
- Range and SOC trajectory prediction
- Powertrain and subsystem sizing studies
- Thermal trend analysis
- Test-case comparison across vehicle configurations

The guiding idea is simple:

- The **engine** coordinates simulation time and module execution.
- The **physics** lives in modules.
- Vehicle and experiment definitions come from **configuration files**.

This repository is currently in an active build-up phase with a working BEV-focused simulation path and fixed multi-rate scheduling support.

## Current Scope

VEHRON v1 should be understood as a **BEV-focused research software package**.

The active supported path today is:

- battery-electric vehicles (`powertrain: bev`)
- forward-time longitudinal simulation
- YAML-defined vehicles and testcases
- parametric routes and speed-trace drive cycles
- configurable battery, HVAC, motor, reducer, regen, and thermal trend models
- reproducible case package outputs

VEHRON should **not** currently be interpreted as:

- a general multi-powertrain vehicle simulator
- a battery degradation inference package
- a high-fidelity electrochemical battery solver
- a GPS/lat-lon route replay framework
- a fully validated production-grade vehicle model

If you are evaluating VEHRON for reuse, treat it as a modular BEV simulation kernel with documented extension points, not as a finished broad vehicle platform.

## Capability Matrix

| Area | Supported Today | Experimental / Partial | Planned / Not Yet Supported |
| --- | --- | --- | --- |
| Powertrain scope | BEV active path | non-BEV code scaffolding present in repo | ICE / hybrid / FCEV public support |
| Vehicle classes | BEV sedan example and BEV-style studies | placeholder archetypes in repo | broad validated archetype library |
| Route input | parametric route, `time_s,speed_kmh` drive-cycle CSV | fixed route abstractions inside engine | GPS / lat-lon / elevation route ingestion |
| Battery models | `rint`, `ecm_2rc`, external battery slot | advisory-driven charge-stop-resume control | degradation-aware built-in battery models |
| HVAC models | `cabin_load`, external HVAC slot | low-order lumped thermal behavior | high-fidelity AC / heat-pump runtime models |
| Thermal modeling | battery, motor, coolant trend states | low-order coupled trends only | detailed thermal network calibration |
| Outputs | case package, summary, timeseries, plots | current output schema still evolving | richer comparison/report workflows |
| Public reuse story | CLI-driven BEV studies, custom YAMLs, external battery/HVAC models | Python API use via core classes | larger stable plugin ecosystem |

See also:

- [Public Interface](/home/sn/02_git/vehron/docs/public_interface.md)
- [Getting Started](/home/sn/02_git/vehron/docs/getting_started.md)
- [Validation and Limitations](/home/sn/02_git/vehron/docs/validation.md)
- [Reference Benchmarks](/home/sn/02_git/vehron/docs/benchmarks.md)
- [YAML Reference](/home/sn/02_git/vehron/docs/yaml_reference.md)

## License

VEHRON is licensed under `AGPL-3.0-only`.

This is an intentional copyleft choice.

VEHRON is independent work built from personal engineering effort, time, and experimentation rather than institutional sponsorship. The license choice reflects that context as well as the project's technical goals.

The aim is:

- to keep VEHRON itself open
- to discourage private SaaS capture without contribution back
- to preserve a commons around the simulator as it grows
- to keep long-term stewardship clear as the project evolves

Contributor policy:

- non-trivial contributions are expected to be made under the VEHRON CLA
- see [CONTRIBUTING.md](/home/sn/02_git/vehron/CONTRIBUTING.md)
- see [CLA.md](/home/sn/02_git/vehron/CLA.md)

---

## 1. What VEHRON Is Designed To Do

VEHRON is designed as a **component-based simulator**, not a monolithic model. You can swap component models over time as fidelity improves.

### Core design principles

- **Modularity**: each subsystem (driver, dynamics, motor, battery, HVAC, etc.) is a separate module.
- **Determinism**: same inputs produce same outputs.
- **Boundary conversion discipline**: boundary units are converted to SI internally.
- **Extensibility**: add or upgrade models without rewriting the core engine loop.
- **Config-driven operation**: vehicle and test case are defined by YAML files.

### Supported focus today

- Primary: **BEV active path** (`powertrain: bev`)
- Public emphasis: reproducible BEV duty-cycle simulation rather than broad powertrain coverage
- Planned next: broader archetype and route support after the BEV baseline is better documented and validated

---

## 2. Current Functional Scope (As Implemented)

The current pipeline supports a complete BEV simulation loop with these active model blocks:

- Driver speed tracking (PID)
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
- Third-party battery models can be hot-swapped into the battery slot
- Private battery code does **not** need to live in this repository
- External battery models only need to implement the VEHRON battery slot interface
- The battery slot contract is defined by `BatteryModelBase`
- VEHRON can load a private battery class at runtime from a local Python file
- This lets a battery team keep proprietary pack physics outside GitHub while still running inside VEHRON

HVAC slot architecture:

- VEHRON keeps a reference in-repo HVAC model: `CabinLoadModel`
- Third-party HVAC or AC models can be hot-swapped into the HVAC slot
- Private HVAC code does **not** need to live in this repository
- External HVAC models only need to implement the VEHRON HVAC slot interface
- The HVAC slot contract is defined by `HvacModelBase`
- VEHRON can load a private HVAC class at runtime from a local Python file

### Important note on maturity

This is an **engineering MVP**, not a fully calibrated production-grade simulator yet. The architecture is intentionally ready for incremental fidelity upgrades.

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

- Driver: divisor `1` -> `0.1 s`
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
- Simulation settings (`dt`, max duration, stop criteria)
- Optional external charging window:
  - `external_charging_power_kw`
  - `external_charging_start_s`
  - `external_charging_end_s`

Optional:

- Drive-cycle CSV (`time_s, speed_kmh`) for cycle-driven runs

For the public user-facing contract, see:

- [Public Interface](/home/sn/02_git/vehron/docs/public_interface.md)
- [Getting Started](/home/sn/02_git/vehron/docs/getting_started.md)
- [YAML Reference](/home/sn/02_git/vehron/docs/yaml_reference.md)

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

Optional battery advisories for mission charging control:

- `charge_recommended`
- `charge_required`
- `max_charge_power_w`
- `max_discharge_power_w`
- `preferred_charge_power_w`
- `resume_charge_soc`
- `trigger_charge_soc`

These may be exposed through the battery model `get_state()` return value. VEHRON
uses them as mission-control hints. The battery does not directly stop the
vehicle; the mission controller reads these advisories and decides whether to
pause the route, charge, and resume.

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

- CLI summary (steps, distance, final SOC, total net energy, charge sessions)
- Full in-memory time series (available during run)
- Case artifacts (when saved as a case package):
  - `summary.json`
  - `timeseries.csv`
  - plots (`motion`, `SOC + idle`, `vehicle temperatures`)
  - copied input snapshots (`vehicle.yaml`, `testcase.yaml`)
  - resolved input snapshots (`vehicle_resolved.yaml`, `testcase_resolved.yaml`)
  - case `README.md` with model/rate metadata

Current CLI run flow:

- prints a test spec sheet before simulation starts
- prints live progress at 10-second intervals
- shows distance, speed, acceleration, SOC, charging state, and available temperatures
- writes a case package under `output/cases/...`

Charging and regen observability:

- Regenerative charging appears through positive `p_regen_w` and accumulated `e_regen_wh`.
- Net battery charging appears as negative `i_batt_a` and negative `p_batt_w`.
- External charging contributes through the optional testcase charging window fields.
- Auto charge-stop-resume runs expose `auto_charge_active`, `charge_stop_requested`,
  `charge_sessions`, and `charge_time_s` in the exported time series.

---

## 5. Case Packaging Convention

Case runs should be saved under:

- `output/cases/<case_name>/`

Current naming style includes archetype explicitly, e.g.:

- `case_bev_car_sedan_flat_highway_YYYYMMDD_HHMMSS`

A case package should include:

- `README.md` describing run context and model stack
- `summary.json` with reproducible metadata
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

### Fresh install from Git

```bash
git clone <your-vehron-repo-url>
cd vehron
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
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

### Run WLTP Class 3b cycle (openly available source)

```bash
vehron run \
  --vehicle src/vehron/archetypes/bev_car_sedan.yaml \
  --testcase src/vehron/testcases/wltp_class3b_standard.yaml
```

To evaluate any vehicle on WLTP, keep the same testcase and swap `--vehicle`.

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

Example testcase charging policy:

```yaml
simulation:
  dt_s: 0.2
  max_duration_s: 4000.0
  stop_on_soc_min: true
  auto_charge:
    enabled: true
    trigger_soc: 0.18
    resume_soc: 0.80
    charger_power_kw: 60.0
    stop_speed_threshold_ms: 0.3
    max_charge_stops: 10
```

How the charging-control split works today:

1. VEHRON mission control watches SoC and battery advisories.
2. When charging is needed, VEHRON requests a stop by forcing target speed to zero.
3. Once the vehicle speed is below the configured stop threshold, VEHRON enters charging mode.
4. Charging power is limited by the testcase charger power and any battery advisory limits such as `max_charge_power_w`.
5. VEHRON resumes the mission after the resume SoC threshold is reached.

What the external battery model should do:

- own pack physics
- compute SoC, current, voltage, and power response
- optionally expose charge advisories through `get_state()`
- optionally expose richer temperature channels through `get_state()`

What VEHRON mission control should do:

- decide when to stop the route
- decide when to start charging
- cap charge power at the allowed mission and battery limits
- resume the route when charging policy says to continue

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
.venv/bin/python -m vehron.runner run \
  --vehicle path/to/vehicle_with_private_battery.yaml \
  --testcase src/vehron/testcases/wltp_class3b_standard.yaml
```

During the run, VEHRON will:

- print a test spec sheet before starting
- print live progress every 10 seconds of simulation time
- show whether the vehicle is currently charging
- show available vehicle-level temperatures
- write a case package and plots when the run finishes

6. Recommended handoff from the battery team:

- private Python file or package
- selected battery YAML or modified archetype YAML
- chosen charging policy in testcase YAML
- note of which advisory keys the private battery publishes
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
- Add reproducibility checks and golden baseline runs
- Keep a standard WLTP Class 3b benchmark testcase for all archetypes

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
