# Powertrain Guide

## Current Status

VEHRON's active validated runtime is BEV-focused. The repository contains some
broader powertrain scaffolding, but the production path for configuration,
validation, and tests currently centers on battery electric vehicles.

This means the right engineering priority today is to deepen BEV fidelity
before broadening into additional powertrain types.

## Active BEV Composition

The current BEV stack is composed from these model blocks:

- driver
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

## Key BEV Physics Included

- aero drag via `drag_coefficient` and `frontal_area_m2`
- rolling resistance via `rolling_resistance_coeff`
- road grade effect
- wheel-to-motor reduction mapping
- motor and inverter losses
- regenerative braking
- battery electrical response
- simplified thermal trends

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

## What Is Not Yet the Main BEV Path

- closed-loop power derating from thermal limits
- high-fidelity tyre slip integration in the active runtime
- advanced charging taper and charging-control logic
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
