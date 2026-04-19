# Contributing to VEHRON

Thank you for considering a contribution to VEHRON.

VEHRON is an engineering-first open-source project, and thoughtful contributions are welcome.

This project is being built as independent work rather than institution-sponsored work. Because of that, the licensing and contribution terms are designed to do two things at once:

- keep VEHRON itself in the open
- preserve clear long-term stewardship of the project

To support that, non-trivial contributions are expected to be made under the VEHRON Contributor License Agreement (CLA).

## Before You Contribute

Please read:

- [README.md](/home/sn/02_git/vehron/README.md)
- [CODEX.md](/home/sn/02_git/vehron/CODEX.md)
- [CLA.md](/home/sn/02_git/vehron/CLA.md)

## License

VEHRON is licensed under `AGPL-3.0-only`.

The project uses AGPL because the goal is to keep the simulator and its improvements in the commons, including in networked or hosted use cases.

By contributing code, documentation, tests, examples, or other material to this
repository, you agree that:

- your contribution may be distributed under the project license
- you have the right to submit the contribution
- you agree to the VEHRON CLA for non-trivial contributions

## CLA Requirement

The project maintainer may request explicit CLA acceptance before accepting a
pull request or patch.

The CLA is not meant to be hostile to contributors. Its purpose is to keep governance clear early, while the project is still founder-led and independently developed.

In practical terms, the CLA helps:

- to keep contribution rights clear
- to allow the project to be relicensed in future if needed
- to reduce long-term legal uncertainty for the project

## Practical Contribution Expectations

- Keep physics in modules, not in the engine.
- Follow `BaseModule` contracts and current `SimState` conventions.
- Keep SI units internal.
- Add or update tests with every meaningful behavior change.
- Avoid unrelated refactors in focused changes.
- Keep documentation in sync when public behavior changes.

## Good First Contributions

- tests
- documentation improvements
- small module fixes
- validation checks
- CLI polish
- case export/reporting improvements

## Discussion First For Larger Changes

Please discuss before making large changes such as:

- new public interfaces
- schema-breaking changes
- engine scheduling changes
- licensing/legal text changes
- broad refactors across multiple modules

## No Warranty

Unless separately agreed in writing, contributions are accepted into the
project on an `as is` basis without warranty.
