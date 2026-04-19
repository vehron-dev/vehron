# VEHRON Codebase Map

## Purpose

- Modular forward-time vehicle simulation framework
- Current strongest validated path: `[ACTIVE]` BEV 4W
- Core idea
  - `engine.py` orchestrates time and module execution
  - `modules/` contains the physics and subsystem models
  - YAML files define vehicle hardware and testcases
  - `state.py` is the shared simulation bus

## Reading Legend

- `[CORE]` central runtime code
- `[ACTIVE]` part of the default main BEV 4W path
- `[OPTIONAL]` available alternate implementation
- `[EXTENSION]` integration point or external hook
- `[DATA]` input or lookup asset
- `[TEST]` verification coverage
- `[PLACEHOLDER]` present in repo but not mainline runtime today

## Runtime Flow

- `[CORE]` CLI entrypoint
  - `src/vehron/runner.py`
  - Loads configs
  - Applies optional LFP feedback
  - Builds and runs `SimEngine`
- `[CORE]` Config loading
  - `src/vehron/loader.py`
  - Reads YAML
  - Validates with Pydantic schemas
  - Applies boundary unit conversions
    - ambient C to K
    - speed km/h to m/s
    - grade percent to radians
- `[CORE]` Config contracts
  - `src/vehron/schemas/vehicle_schema.py`
  - `src/vehron/schemas/testcase_schema.py`
  - Defines allowed structure for vehicle and testcase files
- `[CORE]` Module resolution
  - `src/vehron/registry.py`
  - Maps `kind:model` keys to Python classes
  - Can load external battery and HVAC modules
- `[CORE]` Orchestration engine
  - `src/vehron/engine.py`
  - Builds configured modules
  - Runs fixed-step multi-rate loop
  - Calls `accumulate()`, `flush_accumulator()`, and `step()`
  - Applies `ModuleOutputs` back into `SimState`
  - Collects flat time-series history
- `[CORE]` Shared state contract
  - `src/vehron/state.py`
  - `SimState`
    - shared bus read by all modules
  - `ModuleInputs`
    - module-specific extras passed in by the engine
  - `ModuleOutputs`
    - writeback payload returned by modules

## Active BEV 4W Simulation Path

- `[ACTIVE]` Driver
  - `src/vehron/modules/driver/pid_driver.py`
  - Converts target speed error into throttle and brake
- `[ACTIVE]` Longitudinal dynamics
  - `src/vehron/modules/dynamics/longitudinal.py`
  - Computes aero, rolling, grade, traction, braking
  - Updates speed, acceleration, distance
  - Produces wheel torque and wheel power
- `[ACTIVE]` Reduction drivetrain
  - `src/vehron/modules/powertrain/bev/reduction/fixed_ratio.py`
  - Maps wheel-side torque and speed to motor-side torque and speed
- `[ACTIVE]` Motor subsystem
  - `[ACTIVE]` `src/vehron/modules/powertrain/bev/motor/analytical.py`
    - Default motor model in active archetype
    - Uses peak torque, peak power, speed limit, base efficiency
  - `[OPTIONAL]` `src/vehron/modules/powertrain/bev/motor/efficiency_map.py`
    - Uses nearest-point lookup from motor map CSV
    - Only used if vehicle YAML selects `model: efficiency_map`
- `[ACTIVE]` Inverter
  - `src/vehron/modules/powertrain/bev/inverter/simple.py`
  - Converts motor-side electrical demand to DC-side demand using efficiency
- `[ACTIVE]` Regenerative braking
  - `src/vehron/modules/powertrain/bev/regen/blended_brake.py`
  - Blends friction braking and regen opportunity
  - Produces `p_regen_w`
- `[ACTIVE]` Battery subsystem
  - `[ACTIVE]` `src/vehron/modules/energy_storage/battery/rint.py`
    - Default in-repo battery model
  - `[OPTIONAL]` `src/vehron/modules/energy_storage/battery/ecm_2rc.py`
    - Alternate in-repo battery model
  - `[EXTENSION]` `src/vehron/modules/energy_storage/battery/base.py`
    - External battery model contract
  - Battery responsibilities
    - combines traction demand
    - combines HVAC load
    - combines aux load
    - subtracts regen power
    - applies optional external charging
    - updates SOC, battery current, voltage, and battery power
- `[ACTIVE]` HVAC subsystem
  - `[ACTIVE]` `src/vehron/modules/hvac/cabin_load.py`
    - Cabin thermal model and HVAC electrical load
  - `[EXTENSION]` `src/vehron/modules/hvac/base.py`
    - External HVAC model contract
- `[ACTIVE]` Aux loads
  - `src/vehron/modules/aux_loads/dc_loads.py`
  - Aggregates headlights, ADAS, infotainment, steering loads
- `[ACTIVE]` Thermal trend models
  - `src/vehron/modules/thermal/battery_thermal.py`
    - Battery bulk temperature trend
  - `src/vehron/modules/thermal/motor_thermal.py`
    - Motor temperature trend
  - `src/vehron/modules/thermal/coolant_loop.py`
    - Slow coolant equalization between battery and motor

## Key Runtime Connections

- Target speed path
  - testcase route -> `engine.py`
  - `engine.py` -> `SimState.target_v_ms`
  - `pid_driver.py` reads target speed and current speed
  - outputs throttle and brake
- Motion path
  - `longitudinal.py` reads throttle, brake, vehicle state
  - outputs speed, acceleration, distance, wheel torque
  - `fixed_ratio.py` maps wheel outputs to motor outputs
  - `motor/*.py` computes motor efficiency and drive power
  - `simple.py` inverter adjusts power to DC bus side
- Energy path
  - `blended_brake.py` creates regen power
  - `cabin_load.py` creates HVAC power demand
  - `dc_loads.py` creates aux power demand
  - battery model combines all of them into electrical state
- Thermal path
  - battery current influences battery thermal model
  - motor torque, speed, and efficiency influence motor thermal model
  - battery and motor temperatures influence coolant model
  - cabin temperature evolves inside HVAC subsystem
- Communication rule
  - modules do not call each other directly
  - modules read from `SimState`
  - modules return `ModuleOutputs`
  - only `SimEngine` writes results back into `SimState`

## Core Source Files

- `[CORE]` `src/vehron/runner.py`
  - user-facing CLI
- `[CORE]` `src/vehron/loader.py`
  - YAML loading and unit conversion
- `[CORE]` `src/vehron/registry.py`
  - model class lookup and external plugin loading
- `[CORE]` `src/vehron/engine.py`
  - main orchestration loop
- `[CORE]` `src/vehron/state.py`
  - shared bus and module I/O contract
- `[CORE]` `src/vehron/modules/base.py`
  - base contract for all modules
- `[CORE]` `src/vehron/constants.py`
  - unit conversions and simulation constants
- `[CORE]` `src/vehron/exceptions.py`
  - custom exceptions

## Module Families

- Driver
  - `[ACTIVE]` `src/vehron/modules/driver/pid_driver.py`
  - `[PLACEHOLDER or helper]` `src/vehron/modules/driver/pedal_map.py`
- Dynamics
  - `[ACTIVE]` `src/vehron/modules/dynamics/longitudinal.py`
  - `[PLACEHOLDER or helper]` `src/vehron/modules/dynamics/aero.py`
  - `[PLACEHOLDER or helper]` `src/vehron/modules/dynamics/grade.py`
  - `[ACTIVE helper]` `src/vehron/modules/dynamics/tyre/rolling_resistance.py`
  - `[PLACEHOLDER or future]` `src/vehron/modules/dynamics/tyre/pacejka.py`
- BEV powertrain
  - `[ACTIVE]` reducer
  - `[ACTIVE]` motor analytical
  - `[OPTIONAL]` motor efficiency map
  - `[ACTIVE]` inverter simple
  - `[ACTIVE]` regen blended brake
- Battery and energy storage
  - `[ACTIVE]` battery base contract
  - `[ACTIVE]` `rint.py`
  - `[OPTIONAL]` `ecm_2rc.py`
  - `[PLACEHOLDER or future]` `pybamm_wrap.py`
  - `[PLACEHOLDER or future]` `supercap.py`
- HVAC
  - `[ACTIVE]` `cabin_load.py`
  - `[ACTIVE]` `base.py`
  - `[PLACEHOLDER or future]` `heat_pump.py`
- Thermal
  - `[ACTIVE]` `battery_thermal.py`
  - `[ACTIVE]` `motor_thermal.py`
  - `[ACTIVE]` `coolant_loop.py`
  - `[PLACEHOLDER or future]` `ice_thermal.py`
- Other powertrain branches
  - `[PLACEHOLDER or future]` `src/vehron/modules/powertrain/ice/*`
  - `[PLACEHOLDER or future]` `src/vehron/modules/powertrain/hybrid/*`
  - `[PLACEHOLDER or future]` `src/vehron/modules/powertrain/fcev/*`

## Configs And Inputs

- Vehicle archetypes
  - `[ACTIVE]` `src/vehron/archetypes/bev_car_sedan.yaml`
    - current working BEV 4W example
  - `[PLACEHOLDER or future]` other archetypes
    - `bev_two_wheeler.yaml`
    - `bev_three_wheeler.yaml`
    - `bev_bus_city.yaml`
    - `bev_truck_heavy.yaml`
    - `ice_car_petrol.yaml`
    - `hybrid_car_parallel.yaml`
    - `fcev_bus.yaml`
- Testcases
  - `src/vehron/testcases/flat_highway_100kmh.yaml`
  - `src/vehron/testcases/wltp_class3b_standard.yaml`
  - `src/vehron/testcases/city_wltp_class3.yaml`
  - `src/vehron/testcases/urban_stop_start.yaml`
  - `src/vehron/testcases/ghat_climb_6pct.yaml`
  - `src/vehron/testcases/indian_drive_cycle.yaml`
  - thermal ambient variants
    - `hot_ambient_45c.yaml`
    - `cold_ambient_minus10c.yaml`
- `[DATA]` Drive cycles
  - `data/drive_cycles/wltp_class3b_eupl.csv`
  - `data/drive_cycles/wltp_class3.csv`
  - `data/drive_cycles/indian_drive_cycle.csv`
  - `data/drive_cycles/nedc.csv`
- `[DATA]` Motor maps
  - `data/motor_maps/pmsm_160kw.csv`
  - only used by optional efficiency-map motor model
- `[DATA]` Broader future-scope maps
  - `data/engine_maps/petrol_110kw.csv`
  - `data/fuel_cell_curves/pem_80kw.csv`

## Extension Points

- `[EXTENSION]` External battery integration
  - selected in vehicle YAML with `battery.model: external`
  - loaded by `registry.py`
  - must inherit from battery base class
- `[EXTENSION]` External HVAC integration
  - selected in vehicle YAML with `hvac.model: external`
  - loaded by `registry.py`
  - must inherit from HVAC base class
## Outputs And Postprocessing

- `[ACTIVE]` Flat time-series history
  - produced by `SimEngine.run()`
  - each timestep serialized from `SimState.to_dict()`
- `[PLACEHOLDER]` post-processing package
  - `src/vehron/post/reports.py`
  - `src/vehron/post/timeseries.py`
  - `src/vehron/post/energy_audit.py`
  - `src/vehron/post/dashboard.py`

## Tests

- `[TEST]` Unit tests
  - loader validation and boundary conversion
  - registry behavior
  - battery models
  - motor map path
  - HVAC behavior
  - reducer behavior
  - longitudinal dynamics
- `[TEST]` Integration tests
  - BEV flat run
  - regen city cycle
  - energy balance
  - ICE path checks
  - bus or ghat scenarios

## Active Vs Present

- `[ACTIVE]` The default validated path is the BEV 4W sedan flow
- `[OPTIONAL]` Some alternate models are usable but not the default
  - battery `ecm_2rc`
  - motor `efficiency_map`
- `[EXTENSION]` Some capabilities are designed for private external models
  - battery slot
  - HVAC slot
- `[PLACEHOLDER]` Some files show intended future scope more than active runtime use
  - ICE modules
  - hybrid modules
  - FCEV modules
  - several post-processing files

## Suggested Next Maps

- Runtime sequence map
  - one simulation tick from target speed to battery state update
- File dependency map
  - which source files import which other source files
- Implemented vs future capability map
  - good for roadmap and communication
