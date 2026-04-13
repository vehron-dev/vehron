# VEHRON Documentation

## Role of This Directory

This `docs/` directory is the canonical technical documentation source for
VEHRON. It is intended to be consumed by:

- engineering contributors
- validation and modeling teams
- the website/docs team building the public documentation section

The website team should render and reorganize this content as needed, but the
technical meaning should originate here.

## Recommended Reading Order

- [Architecture](architecture.md)
- [Powertrain Guide](powertrain_guide.md)
- [YAML Reference](yaml_reference.md)
- [Adding a Module](adding_a_module.md)
- [Source File Standard](source_file_standard.md)
- [References](references.md)
- [Battery Slot Interface](battery_slot_interface.md)
- [HVAC Slot Interface](hvac_slot_interface.md)
- [ECM 2RC Battery Model](models/battery_ecm_2rc.md)
- [Cabin Thermal Model](models/cabin_thermal_model.md)
- [Website Handoff](website_handoff.md)

## Current Documentation Scope

This documentation set is focused on the active BEV simulation path and the
core extension contracts needed to grow VEHRON safely.

It should be treated as:

- canonical for technical behavior
- version-controlled with the codebase
- updated in the same PR as behavior changes

It should not be treated as:

- marketing copy
- a roadmap-only narrative
- a separate wiki that can drift from implementation

## Notes for the Website Team

If you are building the website documentation section:

- consume these markdown files directly
- preserve code samples and units
- preserve the distinction between implemented and planned features
- route technical meaning changes back to engineering review
