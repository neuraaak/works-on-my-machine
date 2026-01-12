#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# LINT - Linting Commands
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Linting commands for WOMM CLI.

This module handles code quality and linting tools for Python projects.
Provides commands for running various linting tools like ruff, black, isort, and bandit.
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
from ...exceptions.lint import PythonLintInterfaceError
from ...interfaces import PythonLintInterface
from ...ui.common import ezpl_bridge, ezprinter

# ///////////////////////////////////////////////////////////////
# COMMAND GROUPS
# ///////////////////////////////////////////////////////////////


@click.group(invoke_without_command=True)
@click.pass_context
def lint_group(ctx: click.Context) -> None:
    """Code quality and linting tools."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ///////////////////////////////////////////////////////////////
# PYTHON LINTING COMMANDS
# ///////////////////////////////////////////////////////////////


@lint_group.command("python")
@click.help_option("-h", "--help")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option(
    "--fix",
    is_flag=True,
    help="Automatically fix code issues",
)
@click.option(
    "--tools",
    help="Comma-separated list of tools to run (ruff,black,isort,bandit)",
)
@click.option(
    "-o",
    "--output",
    "output_dir",
    type=click.Path(file_okay=False, dir_okay=True),
    help="Output directory for detailed reports (one file per tool)",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def lint_python(
    path: str,
    fix: bool,
    tools: str | None,
    output_dir: str | None,
    verbose: bool,
) -> None:
    """Lint Python code with ruff, black, isort, and bandit."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Print header
    ezprinter.print_header("Python Linting")

    try:
        # Initialize lint interface (lazy loading)
        lint_interface = PythonLintInterface(project_root=Path(path))

        # Run linting (interface handles UI display)
        if fix:
            summary = lint_interface.fix_python_code(
                target_paths=[path] if path != "." else None,
                tools=[t.strip() for t in tools.split(",")] if tools else None,
                output_dir=output_dir,
            )
        else:
            summary = lint_interface.check_python_code(
                target_paths=[path] if path != "." else None,
                tools=[t.strip() for t in tools.split(",")] if tools else None,
                output_dir=output_dir,
            )

        # Exit with appropriate code
        sys.exit(0 if summary.success else 1)

    except PythonLintInterfaceError as e:
        ezprinter.error(f"Linting failed: {e.message}")
        if e.details:
            ezprinter.error(f"Details: {e.details}")
        sys.exit(1)
    except Exception as e:
        ezprinter.error(f"Unexpected error during linting: {e}")
        sys.exit(1)


# ///////////////////////////////////////////////////////////////
# STATUS AND UTILITY COMMANDS
# ///////////////////////////////////////////////////////////////


@lint_group.command("status")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def lint_status(verbose: bool) -> None:
    """Show status of available linting tools."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Print header
    ezprinter.print_header("Linting Tools Status")

    try:
        # Interface handles UI display
        lint_interface = PythonLintInterface()
        lint_interface.get_tool_status()

    except PythonLintInterfaceError as e:
        ezprinter.error(f"Tool status check failed: {e.message}")
        if e.details:
            ezprinter.error(f"Details: {e.details}")
        sys.exit(1)
    except Exception as e:
        ezprinter.error(f"Unexpected error during tool status check: {e}")
        sys.exit(1)
