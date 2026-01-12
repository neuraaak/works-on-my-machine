#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM - System Commands
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
System commands for WOMM CLI.

This module handles system detection and prerequisites installation.
Provides commands for detecting system information and installing required tools.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys

# Third-party imports
import click
from ezpl.types import LogLevel

# Local imports
from ...exceptions.system import DetectorInterfaceError, EnvironmentInterfaceError
from ...interfaces import SystemDetectorInterface, SystemEnvironmentInterface
from ...ui.common import ezpl_bridge, ezprinter

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

    # Print header
    ezprinter.print_header("System Detection")

    try:
        system_detector = SystemDetectorInterface()
        result = system_detector.detect_system()
        sys.exit(0 if result.success else 1)
    except DetectorInterfaceError as e:
        ezprinter.error(f"System detection failed: {e}")
        sys.exit(1)
    except Exception as e:
        ezprinter.error(f"Unexpected error during system detection: {e}")
        sys.exit(1)


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

    # Print header
    ezprinter.print_header("Environment Refresh")

    try:
        environment_manager = SystemEnvironmentInterface()
        result = environment_manager.refresh_environment_with_ui()
        sys.exit(0 if result else 1)
    except EnvironmentInterfaceError as e:
        ezprinter.error(f"Environment refresh failed: {e}")
        sys.exit(1)
    except Exception as e:
        ezprinter.error(f"Unexpected environment refresh error: {e}")
        sys.exit(1)
