# Contributing to VEHRON

Thank you for considering a contribution to VEHRON.

VEHRON is an engineering-first open-source project, and thoughtful
contributions are welcome.

This project is being built as independent work rather than
institution-sponsored work. Because of that, the licensing and contribution
terms are designed to do two things at once:

- keep VEHRON itself in the open
- preserve clear long-term stewardship of the project

## License

VEHRON is licensed under `AGPL-3.0-only`.

The project uses AGPL because the goal is to keep the simulator and its
improvements in the commons, including in networked or hosted use cases.

By contributing code, documentation, tests, examples, or other material to
this repository, you agree that:

- your contribution may be distributed under the project license
- you have the right to submit the contribution

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
