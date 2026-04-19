# Paper Assets

This directory now contains figure assets and a small helper script used by the
VEHRON paper workflow.

The actual JOSS submission files live at the repository root:

- `paper.md`
- `paper.bib`

The benchmark figures can be regenerated locally from existing case outputs
with:

```bash
python paper/generate_figures.py
```

The script looks for the latest local highway and city benchmark case packages
under `output/cases/` and rewrites the PNG assets in `paper/figures/` using a
paper-oriented plotting style.
