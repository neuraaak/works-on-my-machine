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
from ezpl import LogLevel
from rich.progress import TaskID

# Local imports
from ...interfaces import PythonLintInterface
from ...ui.common import ezpl_bridge, ezprinter
from ...ui.lint import render_lint_summary_result, render_tool_status_result

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

    lint_interface = PythonLintInterface(project_root=Path(path))
    target_paths = [path] if path != "." else None
    tool_names = [t.strip() for t in tools.split(",")] if tools else None
    mode = "fix" if fix else "check"

    with ezprinter.create_spinner_with_status(
        "Scanning project for Python files..."
    ) as (progress, task):
        progress.update(
            TaskID(task),
            description=f"Running Python linting tools ({mode} mode)...",
            status="Working...",
        )
        run = (
            lint_interface.fix_python_code if fix else lint_interface.check_python_code
        )
        summary = run(
            target_paths=target_paths, tools=tool_names, output_dir=output_dir
        )

    render_lint_summary_result(summary, mode=mode)
    sys.exit(0 if summary.success else 1)


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

    result = PythonLintInterface().get_tool_status()
    render_tool_status_result(result)
    sys.exit(0 if result.success else 1)
