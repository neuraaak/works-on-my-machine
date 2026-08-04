#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CREATE - Create Project Command
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Create project command for WOMM CLI.

Renders a project from a catalog template (Copier-backed). Language and
framework choices live entirely in the template's ``copier.yml`` — this
command only forwards generic arguments.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path

# Third-party imports
import click

# Local imports
from ...interfaces.project.create_interface import ProjectCreateInterface
from ...ui.project import render_project_creation_result

# ///////////////////////////////////////////////////////////////
# HELPERS
# ///////////////////////////////////////////////////////////////


def parse_data_options(values: tuple[str, ...]) -> dict[str, str]:
    """Parse repeated ``--data KEY=VALUE`` options.

    Values stay raw strings: casting is delegated to the declared Copier
    question type.

    Args:
        values: Raw option values.

    Returns:
        dict[str, str]: Answers keyed by question name.

    Raises:
        click.BadParameter: If an entry has no "=" separator.
    """
    answers: dict[str, str] = {}
    for item in values:
        key, separator, value = item.partition("=")
        if not separator or not key:
            raise click.BadParameter(
                f"Expected KEY=VALUE, got: {item}", param_hint="--data"
            )
        answers[key] = value
    return answers


# ///////////////////////////////////////////////////////////////
# COMMAND
# ///////////////////////////////////////////////////////////////


@click.command("create")
@click.help_option("-h", "--help")
@click.argument("template")
@click.argument("destination", type=click.Path(path_type=Path))
@click.option(
    "--data",
    "data",
    multiple=True,
    metavar="KEY=VALUE",
    help="Pre-fill a template answer. Repeatable.",
)
@click.option(
    "--defaults",
    is_flag=True,
    help="Use template defaults instead of prompting.",
)
@click.option(
    "--force",
    is_flag=True,
    help="Render into a non-empty destination.",
)
@click.option(
    "--pretend",
    is_flag=True,
    help="Simulate the rendering without writing anything.",
)
@click.option(
    "--setup",
    is_flag=True,
    help="Prepare the environment after rendering (virtualenv, dependencies, git).",
)
@click.option("-v", "--verbose", is_flag=True, help="Show detailed output.")
def create_command(
    template: str,
    destination: Path,
    data: tuple[str, ...],
    defaults: bool,
    force: bool,
    pretend: bool,
    setup: bool,
    verbose: bool,
) -> None:
    """Create a project from a catalog template."""
    answers = parse_data_options(data)
    result = ProjectCreateInterface().create_project(
        template=template,
        destination=destination,
        answers=answers,
        force=force,
        pretend=pretend,
        defaults=defaults,
        setup=setup,
    )
    render_project_creation_result(result, verbose=verbose)
    if not result.success:
        raise SystemExit(1)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["create_command", "parse_data_options"]
