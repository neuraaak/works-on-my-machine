#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEPS COMMAND - Dependencies Diagnostic
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Dependencies command for Works On My Machine.

Read-only diagnostic across the 3-strata dependency model:
- Strata 1: System Package Managers (winget, choco, homebrew, apt)
- Strata 2: Runtimes (python, node, git)
- Strata 3: DevTools (ruff, eslint, pytest)

Installation is intentionally out of scope: WOMM reports what is present on the
machine, it does not install runtimes or tools for you.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import sys

# Third-party imports
import click
from ezpl import LogLevel

# Local imports
from ...interfaces import DepsInterface
from ...ui.common import ezpl_bridge, ezprinter

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)


# ///////////////////////////////////////////////////////////////
# MAIN DEPS GROUP
# ///////////////////////////////////////////////////////////////


@click.group(invoke_without_command=True)
@click.pass_context
def deps_group(ctx: click.Context) -> None:
    """
    Inspect dependencies across all strata (system, runtime, tools).

    The dependency model has 3 hierarchical strata:

    \b
    Strata 1: System Package Managers (winget, chocolatey, homebrew, apt)
    Strata 2: Runtimes (python, node, git)
    Strata 3: Development Tools (ruff, eslint, pytest)

    This command is read-only: it reports what is installed, it does not
    install anything. Use your OS package manager to install what is missing.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ///////////////////////////////////////////////////////////////
# COMMANDS
# ///////////////////////////////////////////////////////////////


@deps_group.command(name="check")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show version details for each component.",
)
def deps_check(verbose: bool) -> None:
    """
    Check availability of all dependencies across all strata.

    Probes system package managers, runtimes, and development tools, then
    reports which are present. Exit status is 0 when at least one system
    package manager is available and every runtime is installed; development
    tools are informational and never fail the check.

    \b
    Example:
        womm deps check
        womm deps check -v
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Dependencies Check")

    try:
        interface = DepsInterface()
        results = interface.check_all(verbose)

        system_ok = any(r.available for r in results["system"].values())
        runtime_ok = all(r.available for r in results["runtime"].values())
        sys.exit(0 if (system_ok and runtime_ok) else 1)

    except Exception as e:
        logger.error(f"Failed to check dependencies: {e}")
        ezprinter.error(f"Check failed: {e}")
        raise click.Abort() from e


@deps_group.command(name="status")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show additional details in the status report.",
)
def deps_status(verbose: bool) -> None:
    """
    Show a comprehensive dependency status table.

    Renders a table with the status of every component across the three
    strata, including versions and availability.

    \b
    Example:
        womm deps status
        womm deps status -v
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Dependency Status")

    try:
        interface = DepsInterface()
        interface.show_status(verbose)
        sys.exit(0)

    except Exception as e:
        logger.error(f"Failed to generate status report: {e}")
        ezprinter.error(f"Status failed: {e}")
        raise click.Abort() from e


@deps_group.command(name="list")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Reserved for future use.",
)
def deps_list(verbose: bool) -> None:
    """
    List the dependencies WOMM knows about (static inventory).

    Shows the configured system package managers, runtimes, and development
    tools for the current platform, without probing the machine.

    \b
    Example:
        womm deps list
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Dependency Inventory")

    try:
        interface = DepsInterface()
        interface.list_all(verbose)
        sys.exit(0)

    except Exception as e:
        logger.error(f"Failed to list dependencies: {e}")
        ezprinter.error(f"List failed: {e}")
        raise click.Abort() from e


# ///////////////////////////////////////////////////////////////
# EXPORT
# ///////////////////////////////////////////////////////////////

__all__ = ["deps_group"]
