# Cabin Thermal Model

## Purpose

VEHRON's cabin thermal model is a low-order, control-oriented model intended
for vehicle energy simulation. It is designed to estimate HVAC electrical power
and cabin air temperature trends without the computational cost of CFD or a
high-node thermal network.

## Literature Basis

The current VEHRON formulation is based on the standard lumped-parameter cabin
thermal modeling approach used in the vehicle thermal-management literature.
The closest reference models for the current implementation are:

1. Marcos, Pino, Bordons, and Guerra, 2014
   "The development and validation of a thermal model for the cabin of a vehicle"
   Applied Thermal Engineering 66, 646-656
   DOI: https://doi.org/10.1016/j.applthermaleng.2014.02.054

2. Torregrosa-Jaime, Bjurling, Corberan, and Di Sciullo, 2015
   "Transient thermal model of a vehicle's cabin validated under variable ambient conditions"
   Applied Thermal Engineering 75, 45-53
   DOI: https://doi.org/10.1016/j.applthermaleng.2014.05.074

These papers are good anchors because they use dynamic lumped cabin models and
explicitly account for the main physical load contributors that matter for HVAC
energy prediction.

## Why These References

These references match VEHRON's use case better than CFD-heavy studies because
VEHRON needs:

- fast runtime inside a whole-vehicle loop
- explicit ambient and solar sensitivity
- parameters that can be carried in YAML
- a structure suitable for BEV energy studies

The broader modeling context is summarized well by:

- Marshall, Mahony, Rhodes, Daniewicz, Tsolas, and Thompson, 2019
  "Thermal Management of Vehicle Cabins, External Surfaces, and Onboard Electronics: An Overview"
  Engineering 5(5), 954-969
  DOI: https://doi.org/10.1016/j.eng.2019.02.009

- Zhao, Zhou, and Wang, 2024
  "A systematic review on modelling the thermal environment of vehicle cabins"
  Applied Thermal Engineering 257, 124142
  DOI: https://doi.org/10.1016/j.applthermaleng.2024.124142

These are also collected centrally in [References](../references.md).

## Governing Structure In VEHRON

The current VEHRON model treats the cabin as one lumped thermal mass. Net heat
flow into the cabin is represented as:

`Q_net = Q_envelope + Q_solar + Q_ventilation + Q_occupants + Q_hvac`

Where:

- `Q_envelope` represents combined ambient exchange through the cabin body and
  glazing, including a speed-sensitive term to reflect stronger exterior
  convection during motion
- `Q_solar` is solar load through glazing
- `Q_ventilation` is the sensible load from fresh-air exchange
- `Q_occupants` is passenger sensible heat gain
- `Q_hvac` is heating or cooling delivered by the HVAC system

Cabin temperature evolves according to the lumped thermal capacity:

`dT_cabin/dt = Q_net / C_total`

HVAC electrical demand is then estimated from thermal demand and COP:

- cooling power = `|Q_hvac| / COP_cooling`
- heating power = `Q_hvac / COP_heating`

## Relationship To The Literature

VEHRON is aligned with the literature at the term-decomposition level:

- solar load is represented explicitly
- ambient exchange is represented explicitly
- air-renewal / ventilation load is represented explicitly
- occupancy heat gain is represented explicitly
- cabin thermal inertia is represented explicitly

However, VEHRON is not yet a paper-exact reproduction of Marcos 2014 or
Torregrosa-Jaime 2015.

Current simplifications include:

- one lumped cabin node instead of a richer multi-node network
- lumped `UA` representation instead of detailed wall/glass layer models
- no humidity or latent-load modeling
- no explicit mean radiant temperature calculation
- no sun-angle tracking or orientation-dependent glazing loads
- no direct compressor-cycle model

## Why This Is Still Defensible

This is still a meaningful model for BEV simulation because the literature
shows that low-order cabin models can be useful when the goal is energy demand
prediction rather than local comfort-field resolution.

For example, Torregrosa-Jaime et al. reported that in real outdoor conditions
air renewal contributed 7% to 53% of the thermal load, while solar radiation
contributed 18% to 31%, which strongly supports keeping those terms explicit in
VEHRON's model.

## Current VEHRON Parameters

Vehicle-side HVAC parameters:

- `cabin_volume_m3`
- `interior_thermal_mass_kjk`
- `body_ua_wk`
- `speed_ua_per_ms_wk`
- `glazed_area_m2`
- `solar_transmittance`
- `fresh_air_ach`
- `occupant_sensible_w`
- `rated_power_kw`
- `cop_cooling`
- `cop_heating`
- `cabin_setpoint_c`
- `control_tau_s`

Testcase-side environmental drivers:

- `ambient_temp_c`
- `solar_irradiance_wm2`

Payload-side internal-gain driver:

- `passengers`

## Recommended Next Refinements

If VEHRON wants closer paper-level fidelity, the next upgrades should be:

1. separate cabin air and interior/surface thermal nodes
2. explicit wall and glazing thermal states
3. orientation-aware solar gain and sun-angle handling
4. humidity and latent-load treatment
5. recirculation vs fresh-air mode
6. compressor or heat-pump capacity and COP maps

## Documentation Rule

Any future change to the cabin model should state clearly whether it is:

- a literature-faithful implementation
- a literature-inspired simplification
- or a purely engineering approximation

That distinction should never be left implicit.
