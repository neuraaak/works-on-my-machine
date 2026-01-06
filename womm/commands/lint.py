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

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys
from pathlib import Path

# Third-party imports
import click

# Local imports
# Lazy imports - modules will be imported when needed

# ///////////////////////////////////////////////////////////////
# COMMAND GROUPS
# ///////////////////////////////////////////////////////////////


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help")
@click.pass_context
def lint_group(ctx: click.Context) -> None:
    """🎨 Code quality and linting tools."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ///////////////////////////////////////////////////////////////
# PYTHON LINTING COMMANDS
# ///////////////////////////////////////////////////////////////


@lint_group.command("python")
@click.help_option("-h", "--help")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option(
    "-f",
    "--fix",
    is_flag=True,
    help="Automatically fix code issues",
)
@click.option(
    "-t",
    "--tools",
    help="Comma-separated list of tools to run (ruff,black,isort,bandit)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
@click.option(
    "-o",
    "--output",
    "output_dir",
    type=click.Path(file_okay=False, dir_okay=True),
    help="Output directory for detailed reports (one file per tool)",
)
def lint_python(
    path: str, fix: bool, tools: str | None, dry_run: bool, output_dir: str | None
) -> None:
    """🐍 Lint Python code with ruff, black, isort, and bandit."""
    # Lazy imports
    from ..core.managers.lint.lint_manager import LintManager
    from ..core.ui.lint.lint import display_lint_summary

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

    # Initialize lint manager
    lint_manager = LintManager(project_root=project_root)

    # Run linting
    if fix:
        summary = lint_manager.fix_python_code(
            target_paths=target_paths,
            tools=tool_list,
            dry_run=dry_run,
            output_dir=output_dir,
        )
        display_lint_summary(summary, mode="fix")
    else:
        summary = lint_manager.check_python_code(
            target_paths=target_paths,
            tools=tool_list,
            dry_run=dry_run,
            output_dir=output_dir,
        )
        display_lint_summary(summary, mode="check")

    # Exit with appropriate code
    sys.exit(0 if summary.success else 1)


# ///////////////////////////////////////////////////////////////
# GENERAL LINTING COMMANDS
# ///////////////////////////////////////////////////////////////


@lint_group.command("all")
@click.help_option("-h", "--help")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option(
    "-f",
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
    """🔍 Lint all supported code in project (alias for python)."""
    # Lazy imports
    from ..core.managers.lint.lint_manager import LintManager
    from ..core.ui.lint.lint import display_lint_summary

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

    # Initialize lint manager
    lint_manager = LintManager(project_root=project_root)

    # Run linting
    if fix:
        summary = lint_manager.fix_python_code(
            target_paths=target_paths, tools=tool_list
        )
        display_lint_summary(summary, mode="fix")
    else:
        summary = lint_manager.check_python_code(
            target_paths=target_paths, tools=tool_list
        )
        display_lint_summary(summary, mode="check")

    # Exit with appropriate code
    sys.exit(0 if summary.success else 1)


# ///////////////////////////////////////////////////////////////
# STATUS AND UTILITY COMMANDS
# ///////////////////////////////////////////////////////////////


@lint_group.command("status")
@click.help_option("-h", "--help")
def lint_status() -> None:
    """🔧 Show status of available linting tools."""
    # Lazy imports
    from ..core.managers.lint.lint_manager import LintManager
    from ..core.ui.common.console import print_info
    from ..core.ui.lint.lint import display_tool_status

    print_info("🔍 Checking linting tools availability...")

    lint_manager = LintManager()
    tool_summary = lint_manager.get_tool_status()

    display_tool_status(tool_summary)
