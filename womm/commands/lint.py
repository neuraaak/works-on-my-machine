#!/usr/bin/env python3
"""
Linting commands for WOMM CLI.
Handles code quality and linting tools.
"""

import sys
from pathlib import Path

import click

from shared.core.lint_manager import LintManager
from shared.ui import (
    print_lint_fix_suggestions,
    print_lint_progress,
    print_lint_start,
    print_lint_summary,
)


@click.group()
def lint_group():
    """🎨 Code quality and linting tools."""


@lint_group.command("python")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option("--fix", is_flag=True, help="Automatically fix code issues")
def lint_python(path, fix):
    """Lint Python code with ruff, black, and isort."""
    target_path = Path(path)

    # 1. Start linting process
    print_lint_start("Python", str(target_path))

    # 2. Initialize lint manager
    lint_manager = LintManager()

    # 3. Run Python linting
    print_lint_progress("Python linting", "Running ruff, black, and isort")
    summary = lint_manager.run_python_lint(target_path, fix)

    # 4. Display results
    print_lint_summary(summary)

    # 5. Show fix suggestions if needed
    if not summary.success and not fix:
        # Get target directories from summary details
        target_dirs_str = summary.error.replace("Target directories: ", "")
        target_dirs = target_dirs_str.split(", ")
        print_lint_fix_suggestions(str(target_path), target_dirs)

    # 6. Exit with appropriate code
    sys.exit(0 if summary.success else 1)


@lint_group.command("all")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option("--fix", is_flag=True, help="Automatically fix code issues")
def lint_all(path, fix):
    """Lint all supported code in project."""
    target_path = Path(path)

    # 1. Start linting process
    print_lint_start("WOMM project", str(target_path))

    # 2. Initialize lint manager
    lint_manager = LintManager()

    # 3. Run WOMM linting
    print_lint_progress("WOMM linting", "Running ruff and bandit")
    summary = lint_manager.run_womm_lint(target_path, fix)

    # 4. Display results
    print_lint_summary(summary)

    # 5. Show fix suggestions if needed
    if not summary.success and not fix:
        # Get target directories from summary details
        target_dirs_str = summary.error.replace("Target directories: ", "")
        target_dirs = target_dirs_str.split(", ")
        print_lint_fix_suggestions(str(target_path), target_dirs)

    # 6. Exit with appropriate code
    sys.exit(0 if summary.success else 1)
