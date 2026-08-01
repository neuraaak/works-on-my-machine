#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT - Context Menu Command Group
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Context menu commands for WOMM CLI.

Wires the ``context`` group and its ``backup`` subgroup. The commands
themselves live in the sibling modules, grouped by responsibility.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Third-party imports
import click

# Local imports
from ....interfaces import ContextMenuInterface
from ....ui.common import ezprinter

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

_NON_WINDOWS_MESSAGE = "Context menu management is Windows-specific"

# ///////////////////////////////////////////////////////////////
# COMMAND GROUPS
# ///////////////////////////////////////////////////////////////


@click.group(invoke_without_command=True)
@click.pass_context
def context_group(ctx: click.Context) -> None:
    """Windows context menu management."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@context_group.group("backup", invoke_without_command=True)
@click.help_option("-h", "--help")
@click.pass_context
def context_backup_group(ctx: click.Context) -> None:
    """Manage context menu backups."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def _check_windows(manager: ContextMenuInterface) -> bool:
    """Print the non-Windows notice and report support status.

    Args:
        manager: Interface used to detect the platform.

    Returns:
        True when running on Windows, False otherwise.
    """
    if manager.is_windows():
        return True
    ezprinter.info(_NON_WINDOWS_MESSAGE)
    return False


# The command modules register themselves on the groups above at import
# time; they must be imported after the groups exist.
from . import backup, inventory, registration  # noqa: E402,F401

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["context_backup_group", "context_group"]
