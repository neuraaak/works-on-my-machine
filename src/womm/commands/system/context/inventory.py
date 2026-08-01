#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT INVENTORY - Listing and quick setup commands
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Live-state commands for the context menu.

``list`` shows the registry's live entries, summary first. The former
``status`` command was a projection of this listing and no longer exists.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys
from typing import cast

# Third-party imports
import click
from ezpl import LogLevel
from rich.progress import TaskID

# Local imports
from ....interfaces import ContextMenuInterface
from ....ui.common import ezpl_bridge, ezprinter
from ....ui.context.display import (
    render_context_entries_result,
    render_context_setup_result,
)
from . import _check_windows, context_group

# ///////////////////////////////////////////////////////////////
# LISTING COMMANDS
# ///////////////////////////////////////////////////////////////


@context_group.command("list")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def context_list(verbose: bool) -> None:
    """📋 List registered context menu entries."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Context Menu List")

    manager = ContextMenuInterface()

    if not _check_windows(manager):
        return

    with ezprinter.create_spinner_with_status("Retrieving context menu entries...") as (
        progress,
        task,
    ):
        progress.update(cast(TaskID, task), status="Reading registry entries...")
        result = manager.list_entries()

    render_context_entries_result(result)
    sys.exit(0 if result.success else 1)


# ///////////////////////////////////////////////////////////////
# QUICK SETUP COMMANDS
# ///////////////////////////////////////////////////////////////


@context_group.command("quick-setup")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def context_quick_setup(verbose: bool) -> None:
    """⚡ Quick setup common WOMM tools in context menu."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Context Menu Quick Setup")

    manager = ContextMenuInterface()

    if not _check_windows(manager):
        return

    with ezprinter.create_spinner_with_status("Setting up common WOMM tools...") as (
        progress,
        task,
    ):
        progress.update(cast(TaskID, task), status="Registering WOMM tools...")
        result = manager.quick_setup_tools(verbose)

    render_context_setup_result(result)
    sys.exit(0 if result.success else 1)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["context_list", "context_quick_setup"]
