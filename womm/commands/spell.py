#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SPELL - Spell Checking Commands
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Spell checking commands for WOMM CLI.

This module handles CSpell configuration and spell checking functionality.
Provides commands for installing, configuring, and running spell checks on projects.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys
from pathlib import Path

# Third-party imports
import click

# Local imports
# Lazy imports - spell_manager will be imported when needed

# ///////////////////////////////////////////////////////////////
# COMMAND GROUPS
# ///////////////////////////////////////////////////////////////


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help")
@click.pass_context
def spell_group(ctx: click.Context) -> None:
    """📝 Spell checking with CSpell."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ///////////////////////////////////////////////////////////////
# INSTALLATION AND SETUP COMMANDS
# ///////////////////////////////////////////////////////////////


@spell_group.command("install")
@click.help_option("-h", "--help")
def spell_install() -> None:
    """📦 Install CSpell and dictionaries globally."""
    # Lazy import
    from ..core.managers.spell.spell_manager import spell_manager

    result = spell_manager.install_cspell()
    sys.exit(0 if result.success else 1)


@spell_group.command("setup")
@click.help_option("-h", "--help")
@click.argument("project_name")
@click.option(
    "-t",
    "--type",
    "project_type",
    type=click.Choice(["python", "javascript"]),
    help="Force project type",
)
def spell_setup(project_name: str, project_type: str | None) -> None:
    """⚙️ Set CSpell for current project."""
    # Lazy import
    from ..core.managers.spell.spell_manager import spell_manager

    result = spell_manager.perform_setup_project(project_name, project_type)
    sys.exit(0 if result.success else 1)


# ///////////////////////////////////////////////////////////////
# STATUS AND INFORMATION COMMANDS
# ///////////////////////////////////////////////////////////////


@spell_group.command("status")
@click.help_option("-h", "--help")
def spell_status() -> None:
    """📊 Display CSpell project status."""
    # Lazy import
    from ..core.managers.spell.spell_manager import spell_manager

    result = spell_manager.display_project_status()
    sys.exit(0 if result.success else 1)


# ///////////////////////////////////////////////////////////////
# DICTIONARY MANAGEMENT COMMANDS
# ///////////////////////////////////////////////////////////////


@spell_group.command("add")
@click.help_option("-h", "--help")
@click.argument("words", nargs=-1, required=False)
@click.option(
    "-f",
    "--file",
    "file_path",
    type=click.Path(exists=True),
    help="Add words from file",
)
@click.option("--interactive", is_flag=True, help="Interactive mode")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
def spell_add(
    words: tuple[str, ...],
    file_path: str | None,
    interactive: bool,
    dry_run: bool,
) -> None:
    """➕ Add words to CSpell configuration."""
    # Lazy import
    from ..core.managers.spell.spell_manager import spell_manager

    result = spell_manager.perform_add_words(
        words=list(words) if words else None,
        file_path=Path(file_path) if file_path else None,
        interactive=interactive,
        dry_run=dry_run,
    )
    sys.exit(0 if result.success else 1)


@spell_group.command("add-all")
@click.help_option("-h", "--help")
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Skip confirmation prompt",
)
def spell_add_all(force: bool) -> None:
    """📚 Add all dictionaries from .cspell-dict/ to CSpell configuration."""
    # Lazy import
    from ..core.managers.spell.spell_manager import spell_manager

    result = spell_manager.perform_add_all_dictionaries(force=force)
    sys.exit(0 if result.success else 1)


@spell_group.command("list-dicts")
@click.help_option("-h", "--help")
def spell_list_dicts() -> None:
    """📋 List available dictionaries in .cspell-dict/."""
    # Lazy import
    from ..core.managers.spell.spell_manager import spell_manager

    result = spell_manager.perform_list_dictionaries()
    sys.exit(0 if result.success else 1)


# ///////////////////////////////////////////////////////////////
# SPELL CHECKING COMMANDS
# ///////////////////////////////////////////////////////////////


@spell_group.command("check")
@click.help_option("-h", "--help")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option(
    "-j",
    "--json",
    "json_export",
    is_flag=True,
    default=False,
    help="Export results to JSON file in ~/.womm/spell-results/",
)
@click.option(
    "-d",
    "--json-dir",
    "json_output",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="Export results to JSON file in specified directory",
)
def spell_check(path: str, json_export: bool, json_output: Path | None) -> None:
    """🔍 Check spelling in files."""
    # Lazy import
    from ..core.managers.spell.spell_manager import spell_manager

    # Determine JSON export path
    export_path = None
    if json_export:
        # Use default path ~/.womm/spell-results/
        from ..core.managers.installation.installation_manager import (
            get_target_womm_path,
        )

        womm_path = get_target_womm_path()
        export_path = womm_path / "spell-results"
    elif json_output is not None:
        # Use custom path specified
        export_path = json_output

    result = spell_manager.perform_spell_check(path=Path(path), json_output=export_path)
    sys.exit(0 if result.success else 1)
