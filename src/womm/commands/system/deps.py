#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEPS COMMAND - Dependencies Diagnostic
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Dependencies command for Works On My Machine.

Read-only diagnostic across the 2-strata dependency model:
- Strata 1: Runtimes (python, node, git)
- Strata 2: Runtime package managers (pip, uv, npm, yarn)

Installation is intentionally out of scope: WOMM reports what is present on the
machine, it does not install runtimes for you. System package managers (winget,
homebrew, apt) and a project's own packages are out of scope too.
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

# Local imports
from ...interfaces import DepsInterface
from ...ui.common import ezpl_bridge, ezprinter
from ...ui.system import (
    render_deps_check_result,
    render_deps_inventory_result,
    render_deps_status_result,
)

# ///////////////////////////////////////////////////////////////
# MAIN DEPS GROUP
# ///////////////////////////////////////////////////////////////


@click.group(invoke_without_command=True)
@click.pass_context
def deps_group(ctx: click.Context) -> None:
    """
    Inspect the runtimes and runtime package managers WOMM relies on.

    The dependency model has 2 hierarchical strata:

    \b
    Strata 1: Runtimes (python, node, git)
    Strata 2: Runtime package managers (pip, uv, npm, yarn)

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
    🔍 Check availability of all dependencies across both strata.

    Probes the runtimes and the runtime package managers, then reports which
    are present. Exit status is 0 when every runtime is installed and at least
    one runtime package manager is available.

    \b
    Example:
        womm deps check
        womm deps check -v
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Dependencies Check")

    result = DepsInterface().check_all(detect_versions=verbose)
    render_deps_check_result(result, verbose)
    if not result.success:
        sys.exit(1)
    sys.exit(0 if (result.runtime_ok and result.package_managers_ok) else 1)


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
    📊 Show a comprehensive dependency status table.

    Renders a table with the status of every component across the two
    strata, including versions and availability.

    \b
    Example:
        womm deps status
        womm deps status -v
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Dependency Status")

    result = DepsInterface().show_status(detect_versions=verbose)
    render_deps_status_result(result, verbose)
    sys.exit(0 if result.success else 1)


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
    📋 List the dependencies WOMM knows about (static inventory).

    Shows the configured runtimes and runtime package managers, without
    probing the machine.

    \b
    Example:
        womm deps list
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Dependency Inventory")

    result = DepsInterface().list_all()
    render_deps_inventory_result(result)
    sys.exit(0 if result.success else 1)


# ///////////////////////////////////////////////////////////////
# EXPORT
# ///////////////////////////////////////////////////////////////

__all__ = ["deps_group"]
