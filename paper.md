---
title: "VEHRON: a modular forward-time vehicle simulation framework for BEV energy, thermal, and subsystem studies"
tags:
  - Python
  - vehicle simulation
  - battery electric vehicle
  - drive cycle
  - thermal modeling
  - battery stress history
authors:
  - name: Subramanyam Natarajan
    affiliation: 1
affiliations:
  - name: Independent Researcher
    index: 1
date: 19 April 2026
bibliography: paper.bib
---

# Summary

VEHRON is an open-source Python framework for forward-time road-vehicle
simulation with an active focus on battery-electric passenger vehicles. The
software is organized around a small orchestration core, a shared state bus,
validated YAML configuration, and interchangeable subsystem modules for driver,
longitudinal dynamics, drivetrain reduction, electric motor, inverter,
regenerative braking, battery, HVAC, auxiliary loads, and low-order thermal
trends.

The current repository is intentionally narrow. VEHRON v1 should be understood
as a BEV-focused research software package, not as a general multi-powertrain
vehicle platform. The supported path today is CLI-driven, YAML-configured,
forward-time longitudinal simulation for battery-electric vehicles using either
parametric routes or drive-cycle CSV input in the public `time_s,speed_kmh`
format. The software writes reproducible case packages including summary
metadata, time series, copied and resolved inputs, and standard plots.

VEHRON is designed to be reusable within that bounded scope. It includes
reference in-repo battery and HVAC models, YAML-configured auxiliary electrical
loads, and documented slots for loading custom battery or HVAC models from
external Python files at runtime. This lets teams keep proprietary subsystem
models outside the public repository while still running them inside a
transparent vehicle-level simulation loop.

# Statement of Need

Vehicle-simulation workflows often fall into an unhelpful middle ground.
High-fidelity commercial tools can be expensive, opaque, or difficult to
automate, while one-off notebooks and lab scripts rarely mature into reusable
research software. Researchers working on battery-electric vehicle studies
often need something in between: a simulation stack that is transparent,
scriptable, modular, and good enough to support repeatable engineering studies
without claiming unrealistic fidelity.

VEHRON targets that use case. It is intended for:

- early-stage BEV sizing and trade studies
- duty-cycle comparison under different operating conditions
- generation of battery stress histories for later downstream analysis
- subsystem sensitivity checks around battery, HVAC, and auxiliary electrical
  loads
- integration of private battery or HVAC models into an otherwise open vehicle
  simulation workflow

The final point is especially important for this project. VEHRON is being
developed alongside a broader research direction involving battery degradation
analysis, but VehRON itself is not a degradation-inference package. Its role is
to stand on its own as reusable research software for generating vehicle-level
and battery-relevant simulation histories under configurable missions.

# Software Architecture

The VEHRON architecture follows a small set of explicit design rules. First,
`SimEngine` owns orchestration and time stepping only; it does not carry
subsystem physics internally. Second, `SimState` acts as the shared state bus
between modules. Third, each module owns a bounded physical domain and returns
only the outputs it computes. Fourth, vehicle hardware and mission definitions
are provided through validated YAML configuration rather than runtime code.

At a high level, one run proceeds as follows:

1. Vehicle and testcase YAML files are loaded and validated.
2. Boundary-unit conversions are applied at the loader edge.
3. `SimEngine` instantiates the configured subsystem modules.
4. The engine advances a fixed master clock and schedules modules according to
   their execution divisors.
5. Module outputs are written back onto `SimState`.
6. Energy bookkeeping, logging, and termination checks are applied.
7. A flat time series and case package are emitted for post-processing.

The present runtime uses fixed-step multi-rate execution. If the master
timestep is $\Delta t$ and a module declares a divisor $d$, its effective
update interval is:

$$
\Delta t_{\mathrm{eff}} = d \, \Delta t
$$

Fast domains such as the driver, longitudinal dynamics, motor, inverter, and
regenerative braking run every master step in the active BEV chain, while
slower domains such as battery electrical updates, HVAC, and thermal trends run
less often. To reduce the distortion that would come from sampling slow modules
on a single instantaneous input, VEHRON accumulates intermediate signals across
master steps and flushes the accumulator immediately before the slower module is
stepped.

# Implemented Models

The supported BEV path currently includes:

- a PID-style driver for speed tracking
- longitudinal dynamics with traction, braking, rolling resistance, drag, and
  grade effects
- fixed-ratio reduction drivetrain modeling
- analytical and map-based motor variants
- inverter efficiency modeling
- blended regenerative braking
- in-repo battery models (`rint` and `ecm_2rc`)
- auxiliary electrical loads
- a low-order cabin HVAC model
- low-order battery, motor, and coolant thermal trend models

The active longitudinal force balance follows the standard low-order form:

$$
F_{\mathrm{net}} =
F_{\mathrm{trac}} - F_{\mathrm{brake}} - F_{\mathrm{aero}} - F_{\mathrm{roll}} - F_{\mathrm{grade}}
$$

with acceleration:

$$
a = \frac{F_{\mathrm{net}}}{m}
$$

The equivalent-circuit battery implementation includes a two-RC ECM family
[@hu2012ecm; @su2019ecm], with terminal voltage represented conceptually as:

$$
V_{\mathrm{term}} = V_{\mathrm{ocv}} - I R_0 - V_{\mathrm{rc1}} - V_{\mathrm{rc2}}
$$

The cabin HVAC model follows the low-order vehicle-cabin thermal-model family
used in comparative energy studies [@marcos2014cabin; @torregrosa2015cabin;
@noreen2019thermal; @cabreview2024]. This gives VEHRON enough thermal structure
to support comparative subsystem studies while staying lightweight enough for
routine simulation workflows.

# Example Workflows

The current public workflow is CLI-first. A user can install VEHRON, run a
baseline BEV case, inspect the generated case package, and then move on to
custom drive-cycle or external-model studies. The repository now includes:

- documented public CLI usage
- a getting-started guide
- runnable custom drive-cycle examples using `time_s,speed_kmh` CSV input
- an external battery-slot example
- an external HVAC slot contract and template
- YAML-configured auxiliary electrical parasitics through `aux_loads`
- packaged example resources accessible through `vehron list-examples` and
  `vehron run-example`

Two current software regression benchmarks illustrate the supported path:

- a flat-highway BEV sedan case covering about 25 km with final SoC near 0.887
  and net energy use near 5104 Wh
- a stop-start city cycle covering about 8 km with final SoC near 0.956 and
  visibly larger regenerative recovery

These benchmarks are useful as software regression references, not as proof of
broad physical validation.

# Reuse and Extensibility

VEHRON is structured as a reusable research kernel within a deliberately narrow
scope. Outsiders can:

- define a new BEV using YAML configuration
- run a new duty cycle using a simple `time_s,speed_kmh` CSV speed trace
- swap in a custom battery model through the external battery slot using a
  local Python file
- swap in a custom HVAC model through the external HVAC slot using a local
  Python file
- change auxiliary electrical parasitics through YAML `aux_loads` parameters
- inspect reproducible case-package outputs for downstream analysis

The public reuse story is intentionally bounded. VEHRON should not currently be
presented as:

- a broad multi-powertrain simulation platform
- a GPS or latitude/longitude route replay framework
- a degradation-inference package
- a fully validated production-grade digital twin

That boundary matters to the software contribution. VEHRON's claim is not
maximum physical fidelity. Its contribution is a reusable, inspectable, and
modular BEV research simulation framework with a documented public interface.

# Quality and Validation Status

The repository includes unit and integration tests for the active public
workflow, including:

- CLI run behavior
- case-package output generation
- packaged-resource resolution
- documented example runs
- benchmark regression ranges for the active BEV path

The current validation boundary is software verification plus low-order model
documentation, not broad real-world vehicle validation. VEHRON should therefore
be understood as reusable research software infrastructure for BEV simulation,
not as a validated predictive platform across many vehicle classes and
conditions.

# Availability

VEHRON is distributed as Python source under the AGPL-3.0-only license in this
repository. The codebase includes runnable examples, tests, public interface
documentation, and a companion LaTeX manuscript in `paper/` that records a
longer-form software paper draft.

# Acknowledgements

The project reflects sustained independent engineering effort toward an open,
modular vehicle-simulation stack that can host both in-repo and externally
supplied subsystem models.
