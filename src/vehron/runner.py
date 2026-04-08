"""CLI entrypoints for VEHRON."""

from __future__ import annotations

from pathlib import Path

import click

from vehron.engine import SimEngine
from vehron.loader import ConfigLoader


@click.group()
def cli() -> None:
    """VEHRON command-line interface."""


@cli.command("run")
@click.option("--vehicle", "vehicle_path", required=True, type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--testcase", "testcase_path", required=True, type=click.Path(exists=True, dir_okay=False, path_type=Path))
def run_cmd(vehicle_path: Path, testcase_path: Path) -> None:
    """Run a simulation and print a short summary."""
    loader = ConfigLoader(project_root=Path.cwd())
    vehicle_cfg, testcase_cfg = loader.load(vehicle_path, testcase_path)
    engine = SimEngine(vehicle_cfg, testcase_cfg, project_root=Path.cwd())
    result = engine.run()

    final = result.final_state
    click.echo(f"steps={final.step_count}")
    click.echo(f"distance_km={final.distance_m / 1000.0:.3f}")
    click.echo(f"final_soc={final.soc:.4f}")
    click.echo(f"energy_wh={final.total_energy_consumed_wh():.2f}")


if __name__ == "__main__":
    cli()
