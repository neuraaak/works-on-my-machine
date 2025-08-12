#!/usr/bin/env python3
"""
Linting commands for WOMM CLI.
Handles code quality and linting tools.
"""

# IMPORTS
########################################################
# External modules and dependencies

import sys
from pathlib import Path

import click

# IMPORTS
########################################################
# Internal modules and dependencies
from ..core.ui.console import print_info
from ..core.ui.lint import print_lint_summary
from ..core.utils.lint_manager import LintManager

# MAIN FUNCTIONS
########################################################
# Core CLI functionality and command groups


@click.group()
def lint_group():
    """🎨 Code quality and linting tools."""


# UTILITY FUNCTIONS
########################################################
# Helper functions and utilities


@lint_group.command("python")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option("--fix", is_flag=True, help="Automatically fix code issues")
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Output detailed JSON diagnostics when available",
)
def lint_python(path, fix, json_output):
    """🐍 Lint Python code with ruff, black, and isort."""
    target_path = Path(path)

    # Initialize lint manager and run Python linting
    lint_manager = LintManager()
    summary = lint_manager.run_python_lint(target_path, fix, json_output=json_output)

    # Display results (with details)
    print_lint_summary(summary)

    # Show fix suggestions if needed
    if not summary.success and not fix:
        print_info("💡 Run with --fix to automatically fix issues")

    # Exit with appropriate code
    sys.exit(0 if summary.success else 1)


@lint_group.command("all")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option("--fix", is_flag=True, help="Automatically fix code issues")
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Output detailed JSON diagnostics when available",
)
def lint_all(path, fix, json_output):
    """🔍 Lint all supported code in project."""
    target_path = Path(path)

    # Initialize lint manager and run WOMM linting
    lint_manager = LintManager()
    summary = lint_manager.run_womm_lint(target_path, fix, json_output=json_output)

    # Display results (with details)
    print_lint_summary(summary)

    # Show fix suggestions if needed
    if not summary.success and not fix:
        print_info("💡 Run with --fix to automatically fix issues")

    # Exit with appropriate code
    sys.exit(0 if summary.success else 1)
