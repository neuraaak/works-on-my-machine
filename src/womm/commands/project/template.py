#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEMPLATE - Template Catalog Commands
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Template catalog commands for WOMM CLI.

This module manages the Copier template catalog: listing, showing, adding,
removing and updating entries. Rendering is delegated to Copier itself
(see ``womm project create``) — this vertical is catalog CRUD only.
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
from ...interfaces.project.template_store_interface import TemplateStoreInterface
from ...ui.project import (
    render_project_creation_result,
    render_template_list,
    render_template_result,
)
from .create import parse_data_options

# ///////////////////////////////////////////////////////////////
# COMMAND GROUP
# ///////////////////////////////////////////////////////////////


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help")
@click.pass_context
def template_group(ctx: click.Context) -> None:
    """Manage the Copier template catalog."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ///////////////////////////////////////////////////////////////
# COMMANDS
# ///////////////////////////////////////////////////////////////


@template_group.command("list")
@click.help_option("-h", "--help")
@click.option("-v", "--verbose", is_flag=True, help="Show detailed output.")
def template_list(verbose: bool) -> None:
    """List every known template."""
    result = TemplateStoreInterface().list_templates()
    render_template_list(result, verbose=verbose)
    if not result.success:
        raise SystemExit(1)


@template_group.command("show")
@click.help_option("-h", "--help")
@click.argument("identifier")
@click.option("-v", "--verbose", is_flag=True, help="Show detailed output.")
def template_show(identifier: str, verbose: bool) -> None:
    """Show a single catalog entry."""
    result = TemplateStoreInterface().show_template(identifier)
    render_template_result(result, verbose=verbose)
    if not result.success:
        raise SystemExit(1)


@template_group.command("add")
@click.help_option("-h", "--help")
@click.argument("identifier")
@click.argument("source", type=click.Path(path_type=Path))
@click.option("-v", "--verbose", is_flag=True, help="Show detailed output.")
def template_add(identifier: str, source: Path, verbose: bool) -> None:
    """Register a local template under the user namespace."""
    result = TemplateStoreInterface().add_template(identifier, source)
    render_template_result(result, verbose=verbose)
    if not result.success:
        raise SystemExit(1)


@template_group.command("remove")
@click.help_option("-h", "--help")
@click.argument("identifier")
@click.option("-v", "--verbose", is_flag=True, help="Show detailed output.")
def template_remove(identifier: str, verbose: bool) -> None:
    """Unregister a user template."""
    result = TemplateStoreInterface().remove_template(identifier)
    render_template_result(result, verbose=verbose)
    if not result.success:
        raise SystemExit(1)


@template_group.command("update")
@click.help_option("-h", "--help")
@click.argument("identifier")
@click.argument("source", type=click.Path(path_type=Path))
@click.option("-v", "--verbose", is_flag=True, help="Show detailed output.")
def template_update(identifier: str, source: Path, verbose: bool) -> None:
    """Point an existing user template at a new source."""
    result = TemplateStoreInterface().update_template(identifier, source)
    render_template_result(result, verbose=verbose)
    if not result.success:
        raise SystemExit(1)


@template_group.command("init")
@click.help_option("-h", "--help")
@click.argument("destination", type=click.Path(path_type=Path))
@click.option(
    "--data",
    "data",
    multiple=True,
    metavar="KEY=VALUE",
    help="Pre-fill a meta-template answer. Repeatable.",
)
@click.option(
    "--defaults",
    is_flag=True,
    help="Use meta-template defaults instead of prompting.",
)
@click.option(
    "--force",
    is_flag=True,
    help="Scaffold into a non-empty destination.",
)
@click.option("-v", "--verbose", is_flag=True, help="Show detailed output.")
def template_init(
    destination: Path,
    data: tuple[str, ...],
    defaults: bool,
    force: bool,
    verbose: bool,
) -> None:
    """Scaffold a new Copier template skeleton."""
    answers = parse_data_options(data)
    result = TemplateStoreInterface().init_template(
        destination,
        answers=answers,
        force=force,
        defaults=defaults,
    )
    render_project_creation_result(result, verbose=verbose)
    if not result.success:
        raise SystemExit(1)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["template_group"]
