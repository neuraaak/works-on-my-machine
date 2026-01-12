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
from ...ui.common import ezpl_bridge, ezprinter

# ///////////////////////////////////////////////////////////////
# COMMAND GROUPS
# ///////////////////////////////////////////////////////////////


@click.group(invoke_without_command=True)
@click.pass_context
def cspell_group(ctx: click.Context) -> None:
    """📝 CSpell checking with CSpell."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cspell_group.group(invoke_without_command=True)
@click.pass_context
def dict(ctx: click.Context) -> None:
    """📚 Manage dictionaries in .cspell-dict/."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cspell_group.group(invoke_without_command=True)
@click.pass_context
def word(ctx: click.Context) -> None:
    """📝 Manage words in CSpell configuration."""
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
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Print header
    ezprinter.print_header("CSpell Installation")

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


# ///////////////////////////////////////////////////////////////
# STATUS AND INFORMATION COMMANDS
# ///////////////////////////////////////////////////////////////


@cspell_group.command("status")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def spell_status(verbose: bool) -> None:
    """📊 Display CSpell project status."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Print header
    ezprinter.print_header("CSpell Project Status")

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


@word.command("add")
@click.help_option("-h", "--help")
@click.argument("words", nargs=-1, required=False)
@click.option(
    "-F",
    "--file",
    "file_path",
    type=click.Path(exists=True),
    help="Add words from file",
)
@click.option(
    "-I",
    "--interactive",
    is_flag=True,
    help="Interactive mode",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def word_add(
    words: tuple[str, ...],
    file_path: str | None,
    interactive: bool,
    verbose: bool,
) -> None:
    """➕ Add words to CSpell configuration."""  # noqa: RUF002
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Print header
    ezprinter.print_header("Add Words to CSpell Configuration")

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


@dict.command("add-all")
@click.help_option("-h", "--help")
@click.option(
    "-d",
    "--dir",
    "dict_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="Directory containing dictionary files (default: .cspell-dict/)",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def dict_add_all(dict_dir: Path | None, force: bool, verbose: bool) -> None:
    """📚 Add all dictionaries to CSpell configuration (scans .cspell-dict/ by default)."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Print header
    ezprinter.print_header("Add All Dictionaries")

    try:
        dictionary = CSpellDictionaryInterface()
        result = dictionary.perform_add_all_dictionaries(force=force, dict_dir=dict_dir)
        sys.exit(0 if result.success else 1)
    except CSpellDictionaryInterfaceError as e:
        ezprinter.error(f"Dictionary addition failed: {e}")
        sys.exit(1)
    except Exception as e:
        ezprinter.error(f"Unexpected error during dictionary addition: {e}")
        sys.exit(1)


@dict.command("list")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def dict_list(verbose: bool) -> None:
    """📋 List available dictionaries in .cspell-dict/."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Print header
    ezprinter.print_header("Available Dictionaries")

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


@cspell_group.command("lint")
@click.help_option("-h", "--help")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option(
    "--json",
    "json_export",
    is_flag=True,
    default=False,
    help="Export results to JSON file in ~/.womm/spell-results/",
)
@click.option(
    "-D",
    "--dir",
    "directory",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="Export results to JSON file in specified directory",
)
@click.option(
    "--add-words",
    "add_words",
    is_flag=True,
    default=False,
    help="Add detected unknown words to cspell.json",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def spell_lint(
    path: str, json_export: bool, directory: Path | None, add_words: bool, verbose: bool
) -> None:
    """🔍 Lint spelling in files."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Print header
    ezprinter.print_header("CSpell Lint")

    try:
        checker = CSpellCheckerInterface()
        result = checker.perform_cspell_lint(
            path=Path(path),
            json_export=json_export,
            directory=directory,
            add_words=add_words,
        )
        sys.exit(0 if result.success else 1)
    except CSpellInterfaceError as e:
        ezprinter.error(f"CSpell lint failed: {e}")
        sys.exit(1)
    except Exception as e:
        ezprinter.error(f"Unexpected error during spell lint: {e}")
        sys.exit(1)
