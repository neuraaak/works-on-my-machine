#!/usr/bin/env python3
"""
Linting commands for WOMM CLI.
Handles code quality and linting tools.
"""

import sys

import click

from ..utils.path_manager import resolve_script_path


@click.group()
def lint_group():
    """🎨 Code quality and linting tools."""


@lint_group.command("python")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option("--fix", is_flag=True, help="Automatically fix code issues")
def lint_python(path, fix):
    """Lint Python code with flake8, black, and isort."""
    script_path = resolve_script_path("languages/python/scripts/lint.py")

    cmd = [sys.executable, str(script_path), path]
    if fix:
        cmd.append("--fix")

    from shared.core.cli_manager import run_command
    result = run_command(cmd, f"Linting Python code in {path}")
    sys.exit(0 if result.success else 1)


@lint_group.command("all")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option("--fix", is_flag=True, help="Automatically fix code issues")
def lint_all(path, fix):
    """Lint all supported code in project."""
    script_path = resolve_script_path("lint.py")

    cmd = [sys.executable, str(script_path), path]
    if fix:
        cmd.append("--fix")

    from shared.core.cli_manager import run_command
    result = run_command(cmd, f"Linting all code in {path}")
    sys.exit(0 if result.success else 1)
