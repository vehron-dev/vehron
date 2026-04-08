"""CLI entrypoints for VEHRON."""

from __future__ import annotations

from pathlib import Path

import click

from vehron.engine import SimEngine
from vehron.interfaces.lfp_model_v2 import (
    apply_lfp_model_v2_feedback,
    export_lfp_model_v2_hook,
)
from vehron.loader import ConfigLoader


@click.group()
def cli() -> None:
    """VEHRON command-line interface."""


@cli.command("run")
@click.option("--vehicle", "vehicle_path", required=True, type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--testcase", "testcase_path", required=True, type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--lfp-feedback-file", "lfp_feedback_file", required=False, type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--lfp-export-dir", "lfp_export_dir", required=False, type=click.Path(file_okay=False, path_type=Path))
def run_cmd(
    vehicle_path: Path,
    testcase_path: Path,
    lfp_feedback_file: Path | None,
    lfp_export_dir: Path | None,
) -> None:
    """Run a simulation and print a short summary."""
    loader = ConfigLoader(project_root=Path.cwd())
    vehicle_cfg, testcase_cfg = loader.load(vehicle_path, testcase_path)
    vehicle_cfg, feedback_applied = apply_lfp_model_v2_feedback(vehicle_cfg, lfp_feedback_file)
    engine = SimEngine(vehicle_cfg, testcase_cfg, project_root=Path.cwd())
    result = engine.run()

    final = result.final_state
    click.echo(f"steps={final.step_count}")
    click.echo(f"distance_km={final.distance_m / 1000.0:.3f}")
    click.echo(f"final_soc={final.soc:.4f}")
    click.echo(f"energy_wh={final.total_energy_consumed_wh():.2f}")

    if lfp_export_dir is not None:
        out_dir = export_lfp_model_v2_hook(
            result=result,
            vehicle_cfg=vehicle_cfg,
            testcase_cfg=testcase_cfg,
            export_dir=lfp_export_dir,
            feedback_applied=feedback_applied,
        )
        click.echo(f"lfp_model_v2_export={out_dir}")


if __name__ == "__main__":
    cli()
