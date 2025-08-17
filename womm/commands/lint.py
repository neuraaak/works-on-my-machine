#!/usr/bin/env python3
"""
Linting commands for WOMM CLI.
Handles code quality and linting tools.
Refactored to use new modular architecture.
"""

import sys
from pathlib import Path

import click

from ..core.ui.console import print_info
from ..core.ui.lint import display_lint_summary, display_tool_status
from ..core.utils.lint_manager import LintManager


@click.group()
def lint_group():
    """🎨 Code quality and linting tools."""


@lint_group.command("python")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option("--fix", is_flag=True, help="Automatically fix code issues")
@click.option(
    "--tools", help="Comma-separated list of tools to run (ruff,black,isort,bandit)"
)
def lint_python(path, fix, tools):
    """🐍 Lint Python code with ruff, black, isort, and bandit."""
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
    else:
        summary = lint_manager.check_python_code(
            target_paths=target_paths, tools=tool_list
        )

    # Exit with appropriate code
    sys.exit(0 if summary.success else 1)


@lint_group.command("all")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option("--fix", is_flag=True, help="Automatically fix code issues")
@click.option("--tools", help="Comma-separated list of tools to run")
def lint_all(path, fix, tools):
    """🔍 Lint all supported code in project (alias for python)."""
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
    else:
        summary = lint_manager.check_python_code(
            target_paths=target_paths, tools=tool_list
        )

    # Exit with appropriate code
    sys.exit(0 if summary.success else 1)


@lint_group.command("status")
def lint_status():
    """🔧 Show status of available linting tools."""
    print_info("� Checking linting tools availability...")

    lint_manager = LintManager()
    tool_summary = lint_manager.get_tool_status()

    display_tool_status(tool_summary)
