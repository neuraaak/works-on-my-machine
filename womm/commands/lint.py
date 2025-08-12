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

from womm.core.ui.console import console

# IMPORTS
########################################################
# Internal modules and dependencies
from womm.core.ui.lint import print_lint_summary
from womm.core.utils.lint_manager import LintManager

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

    # 1. Start linting process
    console.print(f"🎨 Starting Python linting for: {target_path}")

    # 2. Initialize lint manager
    lint_manager = LintManager()

    # 3. Run Python linting
    console.print("🔍 Running ruff, black, and isort...")
    summary = lint_manager.run_python_lint(target_path, fix, json_output=json_output)

    # 4. Display results (with details)
    print_lint_summary(summary)

    # 5. Show fix suggestions if needed
    if not summary.success and not fix:
        console.print("💡 Run with --fix to automatically fix issues", style="yellow")

    # 6. Exit with appropriate code
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

    # 1. Start linting process
    console.print(f"🎨 Starting WOMM project linting for: {target_path}")

    # 2. Initialize lint manager
    lint_manager = LintManager()

    # 3. Run WOMM linting
    console.print("🔍 Running ruff and bandit...")
    summary = lint_manager.run_womm_lint(target_path, fix, json_output=json_output)

    # 4. Display results (with details)
    print_lint_summary(summary)

    # 5. Show fix suggestions if needed
    if not summary.success and not fix:
        console.print("💡 Run with --fix to automatically fix issues", style="yellow")

    # 6. Exit with appropriate code
    sys.exit(0 if summary.success else 1)
