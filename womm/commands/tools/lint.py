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
from ...exceptions.lint import (
    PythonLintInterfaceError,
)
from ...interfaces import PythonLintInterface
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
def lint_group(ctx: click.Context, verbose: bool) -> None:
    """Code quality and linting tools."""
    # Configure verbose mode if requested
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

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
    # Configure verbose mode if requested
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    try:
        target_path = Path(path)

        # Parse tools if provided
        tool_list = None
        if tools:
            tool_list = [tool.strip() for tool in tools.split(",")]

        # Determine project root and target paths
        if target_path.is_file():
            # If it's a file, use parent as project root and file as target
            project_root = target_path.parent
            target_paths = [str(target_path)]
        else:
            # If it's a directory, use it as both project root and scan it
            project_root = target_path
            target_paths = None  # Will scan entire project

        # Initialize lint interface (lazy loading)
        lint_interface = PythonLintInterface(project_root=project_root)

        # Run linting
        if fix:
            summary = lint_interface.fix_python_code(
                target_paths=target_paths,
                tools=tool_list,
                output_dir=output_dir,
            )
            _display_lint_summary(summary, mode="fix")
        else:
            summary = lint_interface.check_python_code(
                target_paths=target_paths,
                tools=tool_list,
                output_dir=output_dir,
            )
            _display_lint_summary(summary, mode="check")

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
# GENERAL LINTING COMMANDS
# ///////////////////////////////////////////////////////////////


@lint_group.command("all")
@click.help_option("-h", "--help")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option(
    "--fix",
    is_flag=True,
    help="Automatically fix code issues",
)
@click.option(
    "-t",
    "--tools",
    help="Comma-separated list of tools to run",
)
def lint_all(path: str, fix: bool, tools: str | None) -> None:
    """Lint all supported code in project (alias for python)."""
    try:
        # For now, "all" is the same as "python" since we only support Python
        # This can be extended later for other languages

        target_path = Path(path)

        # Parse tools if provided
        tool_list = None
        if tools:
            tool_list = [tool.strip() for tool in tools.split(",")]

        # Determine project root and target paths
        if target_path.is_file():
            # If it's a file, use parent as project root and file as target
            project_root = target_path.parent
            target_paths = [str(target_path)]
        else:
            # If it's a directory, use it as both project root and scan it
            project_root = target_path
            target_paths = None  # Will scan entire project

        # Initialize lint interface
        lint_interface = PythonLintInterface(project_root=project_root)

        # Run linting
        if fix:
            summary = lint_interface.fix_python_code(
                target_paths=target_paths, tools=tool_list
            )
            _display_lint_summary(summary, mode="fix")
        else:
            summary = lint_interface.check_python_code(
                target_paths=target_paths, tools=tool_list
            )
            _display_lint_summary(summary, mode="check")

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
def lint_status() -> None:
    """Show status of available linting tools."""
    try:
        lint_interface = PythonLintInterface()
        result = lint_interface.get_tool_status()

        _display_tool_status(result.tool_summary)

    except PythonLintInterfaceError as e:
        ezprinter.error(f"Tool status check failed: {e.message}")
        if e.details:
            ezprinter.error(f"Details: {e.details}")
        sys.exit(1)
    except Exception as e:
        ezprinter.error(f"Unexpected error during tool status check: {e}")
        sys.exit(1)


# ///////////////////////////////////////////////////////////////
# HELPER FUNCTIONS
# ///////////////////////////////////////////////////////////////


def _display_lint_summary(summary, mode: str = "check") -> None:
    """
    Display linting summary results.

    Args:
        summary: LintSummary object with results
        mode: Operation mode ("check" or "fix")
    """
    if mode == "fix":
        print(f"\nSummary: {summary.message}")
        print(f"Files processed: {summary.total_files}")
        print(f"Issues fixed: {summary.total_fixed}")
    else:
        print(f"\nSummary: {summary.message}")
        print(f"Files checked: {summary.total_files}")
        print(f"Issues found: {summary.total_issues}")

    if summary.tool_results:
        print("\nTool Results:")
        for tool_name, result in summary.tool_results.items():
            # Use checkmark for successful execution, regardless of issues found
            status = "✓"
            if mode == "fix":
                print(
                    f"  {status} {tool_name}: {result.fixed_issues} issues fixed"
                    f" ({result.files_checked} files)"
                )
            else:
                print(
                    f"  {status} {tool_name}: {result.issues_found} issues found"
                    f" ({result.files_checked} files)"
                )


def _display_tool_status(tool_summary: dict[str, str]) -> None:
    """
    Display linting tool status.

    Args:
        tool_summary: Dictionary mapping tool names to status strings
    """
    print("\nLinting Tools Status:")
    for tool_name, status in tool_summary.items():
        status_icon = "✓" if "Available" in status else "✗"
        print(f"  {status_icon} {tool_name}: {status}")
