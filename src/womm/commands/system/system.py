#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM - System Commands
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
System commands for WOMM CLI.

This module handles system detection and environment refresh. It owns the
presentation (headers, spinners, renderers) and drives the interfaces, which
return Result objects.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys

# Third-party imports
import click
from ezpl import LogLevel
from rich.progress import TaskID

# Local imports
from ...interfaces import SystemDetectorInterface, SystemEnvironmentInterface
from ...ui.common import ezpl_bridge, ezprinter
from ...ui.system import (
    render_environment_refresh_result,
    render_system_detection_result,
)

# ///////////////////////////////////////////////////////////////
# COMMAND GROUPS
# ///////////////////////////////////////////////////////////////


@click.group(invoke_without_command=True)
@click.pass_context
def system_group(ctx: click.Context) -> None:
    """System detection and prerequisites."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ///////////////////////////////////////////////////////////////
# SYSTEM DETECTION COMMANDS
# ///////////////////////////////////////////////////////////////


@system_group.command("detect")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def system_detect(verbose: bool) -> None:
    """Detect system information and available tools."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("System Detection")

    interface = SystemDetectorInterface()
    with ezprinter.create_spinner_with_status("Detecting system information...") as (
        progress,
        task,
    ):
        task_id = TaskID(task)
        progress.update(
            task_id,
            description="🔍 Detecting system information...",
            status="Scanning system...",
        )
        result = interface.detect_system()
        progress.update(task_id, status="Detection complete!")

    render_system_detection_result(result)
    sys.exit(0 if result.success else 1)


# ///////////////////////////////////////////////////////////////
# ENVIRONMENT MANAGEMENT COMMANDS
# ///////////////////////////////////////////////////////////////


@system_group.command("refresh-env")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def system_refresh_env(verbose: bool) -> None:
    """Refresh environment variables (Windows only)."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Environment Refresh")

    interface = SystemEnvironmentInterface()
    with ezprinter.create_spinner_with_status(
        "Refreshing environment variables..."
    ) as (progress, task):
        task_id = TaskID(task)
        progress.update(
            task_id,
            description="Refreshing environment variables...",
            status="Reading registry/system configuration...",
        )
        result = interface.refresh_environment()
        progress.update(
            task_id,
            status=(
                "Environment refreshed successfully!"
                if result.success
                else "Environment refresh failed."
            ),
        )

    accessible = interface.verify_environment_refresh() if result.success else False
    render_environment_refresh_result(result, accessible)
    sys.exit(0 if result.success else 1)
