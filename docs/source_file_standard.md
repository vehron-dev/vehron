# Source File Standard

## Purpose

This document defines how VEHRON source files should be documented and labeled.
The goal is clarity, legal consistency, and maintainability without falling
into oversized academic-style file banners.

## Ownership and License

For VEHRON source files, the default compact header is:

```python
# Copyright (c) 2026 Subramanyam Natarajan
# SPDX-License-Identifier: AGPL-3.0-only
```

This project is treated as a personal project of Subramanyam Natarajan for
source-file ownership purposes.

The repository-level `LICENSE` file remains the primary legal document.

## Why VEHRON Does Not Use Large File Banners

Long 50-60 line headers are not the right default for this repository.

Reasons:

- authorship and change history already live in Git
- per-file version histories become stale quickly
- large headers reduce code readability
- repeated legal text across all files creates maintenance noise
- detailed explanation belongs in module docstrings and `docs/`, not banners

## Required Header Policy

Required for files under `src/`:

1. compact copyright line
2. SPDX license identifier
3. module docstring

Optional for `tests/`:

- module docstring only when it adds clarity
- compact header may be added, but is not required

Optional for examples and one-off scripts:

- use judgment
- prefer clarity over ceremony

Markdown documentation files do not need source headers.

## Module Docstring Standard

Every non-trivial Python source file under `src/` should begin with a short
module docstring that states:

- what the file implements
- the abstraction boundary when useful
- one important modeling or usage note if necessary

Good example:

```python
"""Two-RC equivalent-circuit battery model for BEV simulation.

Captures ohmic drop plus fast and slow polarization dynamics for improved
terminal-voltage realism over the baseline Rint model.
"""
```

## Class and Function Docstrings

Required:

- public model classes
- interface classes
- any function whose behavior is not immediately obvious

Not required:

- tiny helpers whose names are fully self-explanatory
- trivial test helpers

## Inline Comment Rules

Use inline comments sparingly.

Good uses:

- non-obvious physics
- numerical method decisions
- sign-convention reminders
- boundary-condition assumptions

Avoid:

- narrating obvious assignments
- repeating what the code already says
- keeping stale pseudo-changelogs in comments

## Version and Date Policy

VEHRON does not maintain manual per-file version history blocks.

Do not add:

- `Version: 1.2`
- `Last updated: ...`
- author modification history
- change logs inside source files

Use Git for:

- authorship
- timestamps
- modification history
- release tracking

The copyright year in the header is sufficient.

## Recommended Template

```python
# Copyright (c) 2026 Subramanyam Natarajan
# SPDX-License-Identifier: AGPL-3.0-only

"""Short description of what this file implements."""
```

## Enforcement Rule

For VEHRON engineering work:

- new files under `src/` should follow this standard
- touched source files should be normalized toward this standard when practical
- documentation changes should accompany meaningful model/interface changes
