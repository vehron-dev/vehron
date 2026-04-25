# Powertrain Guide

## Current Status

VEHRON's active validated runtime is BEV-focused. The repository contains some
broader powertrain scaffolding, but the production path for configuration,
validation, and tests currently centers on battery electric vehicles.

This means the right engineering priority today is to deepen BEV fidelity
before broadening into additional powertrain types.

## Active BEV Composition

The current BEV stack is composed from these model blocks:

- longitudinal dynamics
- reducer
- motor
- inverter
- regen blending
- battery
- HVAC
- auxiliary loads
- thermal trend modules

At runtime, these are orchestrated by `SimEngine` and connected through
`SimState`.

## Motion Input Boundary

The active BEV path uses prescribed-speed motion. Route definitions and
drive-cycle CSV files provide the speed history directly, and VEHRON derives
acceleration, wheel force, torque, and power from that motion at each
timestep.

This keeps energy and thermal studies tied to the stated route or cycle
instead of to controller tuning choices.

## Key BEV Physics Included

- aero drag via `drag_coefficient` and `frontal_area_m2`
- rolling resistance via `rolling_resistance_coeff`
- road grade effect
- wheel-to-motor reduction mapping
- motor and inverter losses
- regenerative braking
- battery electrical response
- selectable AC charging request model
- simplified thermal trends
- low-order cabin thermal load with solar, envelope, ventilation, and occupant gains

The cabin-load formulation follows the literature-standard lumped-parameter
approach used for vehicle thermal models. See [Cabin Thermal Model](models/cabin_thermal_model.md).

## Motor Model Options

### `analytical`

Envelope-based EV motor model with:

- constant-torque region below base speed
- constant-power torque falloff above base speed
- explicit max-speed clamp
- configurable regen torque and regen power ceilings
- bounded scalar efficiency estimate

Use this for:

- baseline BEV studies
- runs that need a sane torque-speed envelope without a map file
- regression testing against packaged archetypes

### `efficiency_map`

The map-backed model reuses the same torque-speed envelope as `analytical` and
then replaces the efficiency estimate with CSV-backed lookup where map data is
available.

## Battery Model Options

### `rint`

Simple pack model with:

- nominal voltage
- lumped internal resistance
- SOC integration
- charge/discharge current limits

Use this for:

- baseline runs
- simple energy studies
- low-complexity comparisons

### `ecm_2rc`

Equivalent-circuit pack model with:

- open-circuit voltage estimate
- ohmic resistance
- two RC polarization branches
- transient voltage sag and recovery

Use this for:

- more realistic transient load response
- regen behavior studies
- improved voltage/current realism without a heavy electrochemical model

## HVAC Model Options

### `cabin_load`

In-repo low-order cabin thermal model with:

- solar gain
- envelope heat exchange
- ventilation load
- occupant sensible heat

### `external`

Private third-party HVAC model loaded at runtime through the HVAC slot
interface.

## Charging Model Status

VEHRON now supports a first in-repo external charging controller for AC
charging sessions.

Current boundary:

- charger selection is testcase-specific through `testcase.charging`
- charger capability and limits live in `vehicle.charging`
- the charger requests battery-side charging power
- the battery model remains the single place that updates SOC, current, and voltage

Current in-repo behavior:

- AC charging availability window
- AC charging efficiency
- target-SOC termination
- simple CP/CV-style transition using present battery voltage and a resistance-based estimate
- legacy fixed-power charging fallback through `simulation.external_charging_*`

What this is not yet:

- DC fast charging
- chemistry-aware taper maps
- temperature-based derating maps
- precise charger-side energy accounting in the main summary outputs

## What Is Not Yet the Main BEV Path

- closed-loop power derating from thermal limits
- high-fidelity tyre slip integration in the active runtime
- DC fast charging and richer charging taper behavior
- degradation-aware cross-cycle battery evolution
- production-grade calibration workflows

## Recommended BEV Roadmap

If the goal is a more useful engineering simulator, the next best upgrades are:

1. battery thermal and current derating feedback into available power
2. richer charging and charging-taper behavior
3. tyre traction and braking realism in the active runtime
4. route and environment realism for fleet and duty-cycle studies
5. calibration and benchmark workflows

## Powertrain Documentation Rule

This file should describe only the currently supported and validated behavior.
Do not blur the line between:

- implemented and tested
- present in the repo as scaffolding
- planned roadmap items
