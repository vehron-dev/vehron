# Website Handoff

## Recommended Operating Model

The website team should build VEHRON's documentation section from the markdown
files in this repository. These files are the canonical technical source.

The right division of responsibility is:

- engineering owns technical truth
- website/docs team owns presentation, navigation, search, and publishing

This is not a wiki-first workflow.

## What The Website Team Should Do

- read from `docs/`
- render these markdown files into the website docs section
- improve layout, hierarchy, diagrams, and discoverability
- keep examples and code blocks intact
- ask engineering to review any meaning-changing edits

## What The Website Team Should Not Do

- rewrite technical behavior independently
- merge planned features into implemented-feature descriptions
- maintain a separate canonical wiki
- manually copy content into a CMS that can drift from the repo

## Preferred Delivery Models

Good options:

- Docusaurus
- MkDocs Material
- Astro or Next.js with markdown-backed docs

Not recommended as the canonical source:

- GitHub wiki
- Notion
- manually maintained website copy

## Handoff Contract

When the website team consumes this repo, they should treat the following as
authoritative:

- equations and sign conventions
- YAML field definitions
- model limitations
- implemented-vs-planned boundaries
- engineering examples

When they want to improve readability, they may:

- reorder pages in navigation
- add callouts and summaries
- redraw diagrams
- improve typography and layout
- add search and sidebar structure

## Review Rule

Any website edit that changes the meaning of a model, parameter, interface, or
limitation should be reviewed by engineering before publication.

## Minimum Page Set For Website Launch

- `docs/index.md`
- `docs/architecture.md`
- `docs/powertrain_guide.md`
- `docs/yaml_reference.md`
- `docs/adding_a_module.md`
- `docs/battery_slot_interface.md`
- `docs/models/battery_ecm_2rc.md`

## Practical Instruction To Share

If you need a single sentence to give the website team, use this:

"Build the documentation section from the repository `docs/` markdown files and
treat those files as the canonical technical source."
