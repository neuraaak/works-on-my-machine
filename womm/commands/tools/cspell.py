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

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys
from pathlib import Path

# Third-party imports
import click
from ezpl.types import LogLevel

# Local imports
from ...exceptions.cspell import (
    CSpellDictionaryInterfaceError,
    CSpellInterfaceError,
)
from ...interfaces import (
    CSpellCheckerInterface,
    CSpellDictionaryInterface,
)
from ...ui.common.ezpl_bridge import ezpl_bridge, ezprinter
from ...utils.womm_setup import get_default_womm_path

# ///////////////////////////////////////////////////////////////
# COMMAND GROUPS
# ///////////////////////////////////////////////////////////////


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
@click.pass_context
def cspell_group(ctx: click.Context, verbose: bool) -> None:
    """📝 CSpell checking with CSpell."""
    # Configure verbose mode if requested
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ///////////////////////////////////////////////////////////////
# INSTALLATION AND SETUP COMMANDS
# ///////////////////////////////////////////////////////////////


@cspell_group.command("install")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def spell_install(verbose: bool) -> None:
    """📦 Install CSpell and dictionaries globally."""
    # Configure verbose mode if requested
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    try:
        # Initialize interfaces (lazy loading)
        checker = CSpellCheckerInterface()
        dictionary = CSpellDictionaryInterface()

        # Install CSpell
        result = checker.install_cspell()
        if not result.success:
            sys.exit(1)

        # Setup dictionaries
        dict_result = dictionary.setup_dictionaries()
        sys.exit(0 if dict_result.success else 1)
    except (CSpellInterfaceError, CSpellDictionaryInterfaceError) as e:
        ezprinter.error(f"CSpell installation failed: {e}")
        sys.exit(1)
    except Exception as e:
        ezprinter.error(f"Unexpected error during CSpell installation: {e}")
        sys.exit(1)


@cspell_group.command("setup")
@click.help_option("-h", "--help")
@click.argument("project_name")
@click.option(
    "-t",
    "--type",
    "project_type",
    type=click.Choice(["python", "javascript"]),
    help="Force project type",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def spell_setup(project_name: str, project_type: str | None, verbose: bool) -> None:
    """⚙️ Set CSpell for current project."""
    # Configure verbose mode if requested
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    try:
        # Initialize interface (lazy loading)
        checker = CSpellCheckerInterface()
        result = checker.perform_setup_project(project_name, project_type)
        sys.exit(0 if result.success else 1)
    except CSpellInterfaceError as e:
        ezprinter.error(f"Project setup failed: {e}")
        sys.exit(1)
    except Exception as e:
        ezprinter.error(f"Unexpected error during project setup: {e}")
        sys.exit(1)


# ///////////////////////////////////////////////////////////////
# STATUS AND INFORMATION COMMANDS
# ///////////////////////////////////////////////////////////////


@cspell_group.command("status")
@click.help_option("-h", "--help")
def spell_status() -> None:
    """📊 Display CSpell project status."""
    try:
        checker = CSpellCheckerInterface()
        result = checker.display_project_status()
        sys.exit(0 if result.success else 1)
    except CSpellInterfaceError as e:
        ezprinter.error(f"Status check failed: {e}")
        sys.exit(1)
    except Exception as e:
        ezprinter.error(f"Unexpected error during status check: {e}")
        sys.exit(1)


# ///////////////////////////////////////////////////////////////
# DICTIONARY MANAGEMENT COMMANDS
# ///////////////////////////////////////////////////////////////


@cspell_group.command("add")
@click.help_option("-h", "--help")
@click.argument("words", nargs=-1, required=False)
@click.option(
    "-F",
    "--file",
    "file_path",
    type=click.Path(exists=True),
    help="Add words from file",
)
@click.option("--interactive", is_flag=True, help="Interactive mode")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def spell_add(
    words: tuple[str, ...],
    file_path: str | None,
    interactive: bool,
    _verbose: bool,
) -> None:
    """➕ Add words to CSpell configuration."""  # noqa: RUF002
    try:
        dictionary = CSpellDictionaryInterface()
        result = dictionary.perform_add_words(
            words=list(words) if words else None,
            file_path=Path(file_path) if file_path else None,
            interactive=interactive,
        )
        sys.exit(0 if result.success else 1)
    except CSpellDictionaryInterfaceError as e:
        ezprinter.error(f"Word addition failed: {e}")
        sys.exit(1)
    except Exception as e:
        ezprinter.error(f"Unexpected error during word addition: {e}")
        sys.exit(1)


@cspell_group.command("add-all")
@click.help_option("-h", "--help")
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Skip confirmation prompt",
)
def spell_add_all(force: bool) -> None:
    """📚 Add all dictionaries from .cspell-dict/ to CSpell configuration."""
    try:
        dictionary = CSpellDictionaryInterface()
        result = dictionary.perform_add_all_dictionaries(force=force)
        sys.exit(0 if result.success else 1)
    except CSpellDictionaryInterfaceError as e:
        ezprinter.error(f"Dictionary addition failed: {e}")
        sys.exit(1)
    except Exception as e:
        ezprinter.error(f"Unexpected error during dictionary addition: {e}")
        sys.exit(1)


@cspell_group.command("list-dicts")
@click.help_option("-h", "--help")
def spell_list_dicts() -> None:
    """📋 List available dictionaries in .cspell-dict/."""
    try:
        dictionary = CSpellDictionaryInterface()
        result = dictionary.perform_list_dictionaries()
        sys.exit(0 if result.success else 1)
    except CSpellDictionaryInterfaceError as e:
        ezprinter.error(f"Dictionary listing failed: {e}")
        sys.exit(1)
    except Exception as e:
        ezprinter.error(f"Unexpected error during dictionary listing: {e}")
        sys.exit(1)


# ///////////////////////////////////////////////////////////////
# SPELL CHECKING COMMANDS
# ///////////////////////////////////////////////////////////////


@cspell_group.command("check")
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
    try:
        # Determine JSON export path
        export_path = None
        if json_export:
            # Use default path ~/.womm/spell-results/
            womm_path = get_default_womm_path()
            export_path = womm_path / "spell-results"
        elif json_output is not None:
            # Use custom path specified
            export_path = json_output

        checker = CSpellCheckerInterface()
        result = checker.perform_spell_check(path=Path(path), json_output=export_path)
        sys.exit(0 if result.success else 1)
    except CSpellInterfaceError as e:
        ezprinter.error(f"CSpell check failed: {e}")
        sys.exit(1)
    except Exception as e:
        ezprinter.error(f"Unexpected error during spell check: {e}")
        sys.exit(1)
