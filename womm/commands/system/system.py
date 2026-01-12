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
from ...exceptions.system import (
    DetectorInterfaceError,
    EnvironmentInterfaceError,
)
from ...interfaces import (
    SystemDetectorInterface,
    SystemEnvironmentInterface,
)
from ...ui.common.ezpl_bridge import ezpl_bridge, ezprinter

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
def system_group(_ctx: click.Context, verbose: bool) -> None:
    """System detection and prerequisites."""
    # Configure verbose mode if requested
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # If no subcommand is provided, show help
    if _ctx.invoked_subcommand is None:
        ezprinter.info(_ctx.get_help())


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
@click.pass_context
def system_detect(_ctx: click.Context, verbose: bool) -> None:
    """Detect system information and available tools."""
    # Configure verbose mode if requested
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    try:
        system_detector = SystemDetectorInterface()
        result = system_detector.detect_system()
        if not result.success:
            ezprinter.error(
                f"System detection failed: {result.error or result.message}"
            )
            sys.exit(1)
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
@click.pass_context
def system_refresh_env(_ctx: click.Context, verbose: bool) -> None:
    """Refresh environment variables (Windows only)."""
    # Configure verbose mode if requested
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    try:
        # Check platform (Windows only)
        import platform

        if platform.system().lower() != "windows":
            ezprinter.info("Environment refresh is only available on Windows")
            sys.exit(0)

        environment_manager = SystemEnvironmentInterface()
        success = environment_manager.refresh_environment_with_ui()

        if not success:
            sys.exit(1)

    except EnvironmentInterfaceError as e:
        ezprinter.error(f"Environment refresh failed: {e}")
        sys.exit(1)
    except Exception as e:
        ezprinter.error(f"Unexpected environment refresh error: {e}")
        sys.exit(1)
