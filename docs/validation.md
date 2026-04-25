# Validation and Limitations

## What This Page Is For

This page exists to draw a hard line between what VEHRON currently demonstrates
and what it does not.

VEHRON currently provides:

- software verification of the documented BEV simulation path
- schema-validated configuration loading
- deterministic packaged case outputs
- runnable examples for public-facing workflows

VEHRON does **not** yet provide a broad in-repo physical validation campaign
across multiple real vehicles, climates, routes, and battery packs.

If you use VEHRON in research, keep these three ideas separate:

- **software verification**: the code runs, checks inputs, and produces
  reproducible outputs
- **model adequacy**: the implemented model form is suitable for a specific
  study question
- **physical validation**: the outputs match trusted measurements or accepted
  reference results

## What Is Verified Today

The current repository provides evidence for the following:

- vehicle and testcase YAML files are validated before runtime
- the CLI run path can execute documented BEV studies end to end
- case outputs are written in a reproducible directory structure
- drive-cycle CSV ingestion works for the public input format
  `time_s,speed_kmh`
- in-repo battery models can run through the core simulation path
- external battery and HVAC models can be loaded through documented slot
  interfaces

This is meaningful engineering verification, but it is not equivalent to
vehicle-level physical validation.

## What VEHRON Should Not Claim Yet

VEHRON should not currently claim:

- validated prediction accuracy across a broad set of EV platforms
- validated battery degradation or aging prediction
- electrochemical battery solver fidelity
- mature GPS or latitude/longitude route replay support
- production-grade thermal calibration for pack, coolant, or cabin behavior
- broad long-term public API stability across all internal modules

If any document or talk implies those claims today, the claim is ahead of the
evidence in this repository.

## Current Validation Boundary

The honest present boundary is:

- **software package level**: partially established
- **example workflow level**: established for the documented BEV path
- **model-form level**: low-order engineering approximations are documented
- **real-world experimental level**: not established in-repo

That means VEHRON is currently defensible as reusable **research software
infrastructure** for modular BEV simulation, but not yet as a validated
predictive digital twin.

## Active Supported Path

The best-supported path today is:

- battery-electric vehicle studies
- forward-time longitudinal simulation
- YAML-defined vehicle and testcase inputs
- parametric route or speed-trace drive-cycle input
- low-order battery, HVAC, and thermal trend models
- deterministic output packaging for later analysis

Public reuse claims should be judged against that path, not against future-scope
or placeholder artifacts elsewhere in the repository.

## Main Modeling Limitations

### Vehicle Scope

- The public story is BEV-centric.
- Non-BEV files or abstractions in the repo should be treated as scaffolding
  unless the docs explicitly promote them as supported.
- The examples do not yet demonstrate a broad vehicle family library.

### Route and Cycle Scope

- VEHRON supports parametric routes and drive-cycle CSV traces.
- The documented CSV format is a time-indexed speed trace, not a map format.
- Latitude/longitude route replay is not yet a mature public capability.

### Battery Scope

- In-repo battery models are low-order engineering models, not degradation
  solvers.
- The external battery slot is an extension mechanism, not proof of a validated
  advanced built-in battery stack.
- VEHRON outputs may be useful as stress-history inputs, but VEHRON itself does
  not presently infer long-term degradation pathways.

### Thermal Scope

- Thermal behavior is represented with low-order trend models.
- This is useful for comparative engineering studies and load-trend analysis,
  but not for detailed high-fidelity thermal claims.

### Motion and Controls Scope

- The active public path is oriented around prescribed-speed BEV energy flow.
- VEHRON is not yet a public framework for advanced supervisory control,
  route-planning, or autonomy research.

## Evidence Still Missing

To strengthen publication and reuse credibility, the repo still needs:

- at least one documented comparison against a trusted reference dataset or
  literature benchmark
- a stable public list of supported API and CLI guarantees
- stronger tests around extension points and output contracts
- explicit release notes distinguishing supported from experimental features

## How To Describe VEHRON Honestly Right Now

An accurate present-tense description is:

> VEHRON is a modular BEV-focused research simulation framework for generating
> deterministic vehicle and battery stress histories from configurable duty
> cycles and operating conditions, with documented extension points for custom
> battery and HVAC models.

An inaccurate overclaim would be:

> VEHRON is a validated general-purpose EV digital twin and battery degradation
> prediction platform.

## Publication Posture

For a v1 JOSS-oriented release, the strongest defensible claim is that VEHRON
contributes reusable **research software infrastructure** for modular BEV
simulation and battery-stress-history generation.

The software paper should maintain a hard boundary between:

- the VEHRON software contribution
- any downstream degradation, inference, or ML work that consumes VEHRON
  outputs

Those downstream research products should remain separate unless their code,
validation evidence, and public interfaces are also maintained here.
