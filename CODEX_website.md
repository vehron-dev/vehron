# CODEX_website.md — VEHRON Website Source Of Truth

> This file is the website-facing companion to `CODEX.md`.
> It is written for the separate VEHRON website repository and for anyone
> building or updating vehron.org.
>
> Purpose:
> - explain what VEHRON is in plain language
> - define what the website should communicate
> - capture the current technical state accurately
> - reduce drift between the simulator repo and the website repo

Important:

- this file is a source-of-truth document, not website copy to be pasted verbatim
- do not publish internal planning phrases such as "what the site should say" or "for v1, the site can..."
- public-facing website pages must read as finished product copy, not planning notes

---

## 1. What VEHRON Is

VEHRON stands for **VEHicle Research and Optimisation Network**.

VEHRON is an open-source, modular, forward-time vehicle simulation software
for engineering analysis. It is intended to help teams study how vehicles
consume energy, respond thermally, and behave over drive cycles and test cases.

The key idea behind VEHRON is:

- the **engine** controls simulation time and orchestration
- the **physics** lives in modular subsystem models
- vehicles and experiments are defined by **YAML configuration files**

VEHRON is not intended to be a flashy black-box calculator. It is meant to be
an engineering tool with transparent structure, swappable models, and a clear
path from simple to higher-fidelity simulation.

---

## 2. Current Product Positioning

The website should present VEHRON as:

- open-source
- copyleft
- engineering-first
- modular and extensible
- configuration-driven
- suitable for BEV studies today
- designed to grow toward broader vehicle classes later

The website should **not** present VEHRON as fully mature across all
powertrains yet. The honest current position is:

- **working today**: BEV 4W simulation pipeline
- **planned next**: BEV 2W support
- **future direction**: richer battery, tyre, thermal, and validation workflows

This honesty is important. It builds trust.

Licensing direction:

- VEHRON is intended to be released under **GNU AGPL v3**
- this is deliberate, to keep improvements in the commons and discourage private SaaS capture
- contributions are expected to be governed by a CLA so the founder retains future relicensing flexibility

Canonical public links:

- GitHub: `https://github.com/vehron-dev/vehron`
- Website: `https://vehron.org`

Do not substitute a different GitHub org or repository name unless it has been updated in the main VEHRON repo first.

---

## 3. What VEHRON Currently Does

The present implementation supports a functioning BEV 4W simulation path with:

- driver speed tracking
- longitudinal dynamics
- fixed-ratio drivetrain reduction
- motor model
- inverter model
- blended regenerative braking
- battery electrical model
- HVAC load model
- auxiliary electrical loads
- simplified thermal trend models
- energy bookkeeping

This should be described publicly as a **working engineering MVP**, not as a fully mature all-powertrain platform.

Important current battery status:

- the in-repo reference battery model is a simple `Rint` model
- charging is supported
- regenerative braking is supported
- a proper battery slot interface now exists for private third-party battery models

Important benchmarking status:

- an openly available **WLTP Class 3b** cycle is included
- any supported vehicle archetype should be able to run on this standard cycle

---

## 4. What Makes VEHRON Different

The website should emphasize the following differentiators:

### 4.1 Modular Physics Architecture

Each subsystem is a separate module. This makes it easier to:

- improve one model without rewriting the whole simulator
- compare model variants
- keep physics and software structure clean

### 4.2 Fixed Multi-rate Integration

VEHRON runs on a master simulation clock and allows each subsystem to run at
its own natural rate.

Example:

- driver at `0.1 s`
- battery electrical at `0.5 s`
- thermal subsystems slower than that

This is a major architectural feature and should appear on the website because
it shows that VEHRON is being built with real engineering simulation needs in mind.

### 4.3 Config-driven Workflow

Users define:

- a vehicle archetype
- a testcase
- optional drive cycle data

Then they run the simulation from the CLI.

This mirrors how serious engineering tools are used in practice.

### 4.4 Hot-swappable Battery Slot

VEHRON now supports a dedicated battery interface. The default reference battery
model stays in the repo, but private battery teams can integrate their own model
locally without publishing it in GitHub.

This is especially important for:

- cell teams
- pack teams
- degradation research workflows
- proprietary battery IP

---

## 5. Current Inputs To VEHRON

The website should explain VEHRON inputs in simple terms.

### 5.1 Vehicle Archetype YAML

Defines the vehicle itself:

- mass
- geometry
- aero parameters
- reduction ratios
- drivetrain efficiency
- motor parameters
- battery parameters
- tyre parameters
- HVAC parameters
- auxiliary loads

### 5.2 Testcase YAML

Defines the experiment:

- route mode
- target speed or drive cycle
- environment conditions
- simulation settings
- stop conditions
- optional charging window

### 5.3 Optional Drive-cycle CSV

For standard cycles or custom recorded traces, VEHRON can use time-based speed data.

Examples:

- WLTP
- future custom cycles
- future GPS-derived traces

---

## 6. Current Outputs From VEHRON

The website should explain that VEHRON produces:

- run summary
- distance traveled
- final SOC
- energy consumption
- time-series outputs
- case directories with metadata
- plots and machine-readable artifacts

Be precise in public copy:

- a normal run should be described as producing a run summary and in-memory simulation results
- `summary.json`, `timeseries.csv`, copied inputs, and plots should be described as **case package artifacts** or **saved run artifacts**
- do not imply that every plain CLI run automatically emits the full packaged artifact set unless that is actually true in the current implementation

Typical case package contents:

- `summary.json`
- `timeseries.csv`
- copied `vehicle.yaml`
- copied `testcase.yaml`
- plots
- a case README

This is useful because VEHRON is not only a calculator. It is also being shaped
as a reproducible experiment framework.

---

## 7. Current Technical Highlights To Surface On The Website

These points are worth calling out prominently:

1. **Working BEV 4W simulation path**
2. **Fixed multi-rate time stepping**
3. **Open WLTP benchmark support**
4. **Charging + regenerative braking**
5. **Case packaging for reproducibility**
6. **Hot-swappable private battery model slot**
7. **Hot-swappable external battery model slot**

These points are also worth stating carefully:

- VEHRON is currently strongest on the BEV 4W path
- BEV 2W is the next major path, not the current primary mature path
- the default shipped battery model is still simple

---

## 8. Current Limitations The Website Should Acknowledge

The website should not oversell. It should say clearly that VEHRON is still in
an active build-up phase.

Important limitations today:

- BEV 4W is the main working path
- 2W is planned but not yet the main active path
- the default battery model is still simple
- battery OCV behavior is not yet a rich SOC-dependent table
- battery thermal output is currently a pack-level trend, not a resolved cell-core model
- tyre and cooling fidelity are still early
- validation/calibration is still growing

This kind of transparency increases credibility.

---

## 9. Website Audience

The website should speak to three groups at once:

### 9.1 Engineers

They care about:

- architecture
- assumptions
- inputs/outputs
- reproducibility
- model extensibility

### 9.2 Collaborators / Research Teams

They care about:

- how to integrate their own model
- whether proprietary code can remain private
- how VEHRON interfaces with external workflows

### 9.3 Newcomers / Potential Users

They care about:

- what VEHRON is
- whether it is useful for their problem
- how fast they can install and run something

---

## 10. Suggested Website Information Architecture

Recommended top-level pages:

1. **Home**
2. **Docs**
3. **Examples**
4. **Roadmap**
5. **GitHub**

Suggested Home page sections:

1. Hero
2. What VEHRON is
3. Why VEHRON exists
4. Key capabilities
5. Architecture overview
6. Example workflow
7. Standard benchmark cycles
8. Battery-team / model integration story
9. Roadmap
10. Footer with links

Suggested Docs sections:

- installation
- quick start
- vehicle YAML
- testcase YAML
- architecture
- modules
- battery slot interface
- examples
- FAQ

---

## 11. Visual Direction Recommendation

VEHRON should not look like a generic startup landing page.

Recommended tone:

- technical
- modern
- credible
- clean
- slightly bold, but not noisy

Reference direction:

- OpenFOAM has strong engineering seriousness
- VEHRON should keep that seriousness
- but improve onboarding, readability, and visual hierarchy

Recommended website traits:

- strong typography
- restrained color palette
- diagrams instead of excessive marketing copy
- command-line examples
- plots or simulation outputs
- benchmark references

---

## 12. Messaging Recommendations

Good high-level message:

> Open-source modular vehicle simulation for engineers.

Good supporting message:

> Define a vehicle. Define a test case. Run. Inspect energy, thermal, and
> subsystem behavior with a modular physics architecture.

Things the site should say often:

- modular
- engineering-first
- open-source
- multi-rate
- reproducible
- benchmark-ready

Things the site should avoid implying:

- that all vehicle types are fully mature already
- that every subsystem is already high-fidelity
- that VEHRON is a black-box turnkey commercial suite

---

## 13. Battery-team Story The Website Should Explain

VEHRON now supports two battery-related workflows:

### 13.1 In-repo Reference Battery Model

This is the baseline battery model that ships with VEHRON.

### 13.2 Private External Battery Model

A third-party battery team can:

- keep their model private
- implement the VEHRON battery interface
- run their model inside VEHRON locally

This is a major collaboration feature.

The website should also mention:

- VEHRON can export mission traces for battery-team studies
- VEHRON can accept battery-related feedback inputs
- this enables pack ageing, electro-thermal, and degradation workflows outside the public repo

---

## 14. Recommended Communication Mode Between The Code Repo And The Website Repo

This matters. Without a process, the website will drift.

### Recommendation: use a lightweight source-of-truth + release-note workflow

The best practical approach is:

1. keep this file, `CODEX_website.md`, in the main VEHRON simulator repo
2. treat it as the **canonical website handoff document**
3. when major simulator changes happen, update this file in the simulator repo
4. in the website repo, mirror or pull from this file when content is refreshed

This works better than relying on memory or chat history.

### Recommended supporting process

Every meaningful simulator change that affects the website should update one or more of:

- `README.md`
- `CHANGELOG.md`
- `CODEX_website.md`

Then the website repo should pull those changes into its own content updates.

### Recommended communication artifacts

For the website repo, I recommend three content inputs from the simulator repo:

1. `CODEX_website.md`
   - human-readable source of truth
2. `CHANGELOG.md`
   - chronological update feed
3. a small machine-readable status file in future
   - recommended future filename: `website_sync.json`

The future `website_sync.json` can expose fields such as:

- current version
- maturity status
- supported archetypes
- supported cycles
- latest notable features
- known limitations

This would make the website easier to automate later.

### What not to do

- do not duplicate long technical truth in many places without a sync plan
- do not let the website become the only source of product truth
- do not update the website without updating the simulator repo docs first

### Best immediate workflow

For now, I recommend this exact rule:

> If a change affects what the public should know, update `README.md`,
> `CHANGELOG.md`, and `CODEX_website.md` in the simulator repo first.
> Then update the website repo.

This is simple and robust.

---

## 15. Suggested Deployment Relationship Between The Two Repos

Because the website repo is separate, the cleanest arrangement is:

- simulator repo stays focused on software and docs truth
- website repo stays focused on presentation and deployment

The website repo should **not** re-explain everything manually if that can be
avoided. Instead it should derive its content from stable source documents in
the simulator repo.

Practical options:

### Option A — Manual but disciplined

- update simulator repo docs
- copy the relevant content into website repo pages

Good for early stage, but easy to drift if discipline slips.

### Option B — Pull raw source docs from GitHub

- website build process reads raw markdown or JSON from the simulator repo
- website pages are partly generated from that source

This is better long-term if the site stack supports it.

### Option C — Shared content package later

- create a tiny shared content layer or export file
- website consumes it directly

This is best if the project grows.

### My recommendation

Right now:

- use **Option A**, but disciplined
- and prepare for **Option B** by keeping this file well structured

That gives you low complexity now and better automation later.

---

## 16. Website Build Priority

If the website is starting from scratch, the highest-value order is:

1. Home page
2. Install / Quick Start
3. Docs landing page
4. Architecture page
5. WLTP benchmark page or example section
6. Battery integration page
7. Roadmap page

This order gives credibility quickly.

---

## 17. Current Statement Of Truth

As of now, the website may truthfully say:

- VEHRON is an open-source modular vehicle simulation project
- VEHRON has a working BEV 4W path
- VEHRON supports fixed multi-rate integration
- VEHRON supports charging and regenerative braking
- VEHRON includes an openly available WLTP benchmark cycle
- VEHRON can package simulation cases with outputs and metadata
- VEHRON supports hot-swappable private battery models through a stable battery slot interface
- VEHRON is licensed under GNU AGPL v3 (`AGPL-3.0-only`)
- VEHRON is independent work rather than institution-sponsored work

The website should not yet claim:

- full production-grade validation across all use-cases
- complete maturity across 2W, 3W, truck, bus, ICE, HEV, and FCEV
- high-fidelity battery electrochemistry in the default shipped model

For homepage-quality wording, a good accurate summary is:

> VEHRON is an open-source modular vehicle simulation project with a working BEV 4W engineering MVP, fixed multi-rate integration, WLTP benchmark support, and a hot-swappable private battery model interface.

---

## 18. Maintenance Rule

Whenever any of the following changes, this file should be reviewed:

- supported vehicle classes
- benchmark cycles
- battery integration workflow
- simulation outputs
- public positioning
- roadmap

If this file is kept current, the website repo becomes much easier to maintain.
