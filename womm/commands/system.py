#!/usr/bin/env python3
"""
System commands for WOMM CLI.
Handles system detection and prerequisites installation.
"""

import sys

import click

from ..utils.path_manager import resolve_script_path


@click.group()
def system_group():
    """🔧 System detection and prerequisites."""


@system_group.command("detect")
@click.option("--export", type=click.Path(), help="Export report to file")
def system_detect(export):
    """Detect system information and available tools."""
    script_path = resolve_script_path("shared/core/system_detector.py")

    cmd = [sys.executable, str(script_path)]
    if export:
        cmd.extend(["--export", export])

    from shared.core.cli_manager import run_command
    result = run_command(cmd, "Detecting system information")
    sys.exit(0 if result.success else 1)


@system_group.command("install")
@click.option("--check", is_flag=True, help="Only check prerequisites")
@click.option("--interactive", is_flag=True, help="Interactive installation mode")
@click.argument(
    "tools", nargs=-1, type=click.Choice(["python", "node", "git", "npm", "all"])
)
def system_install(check, interactive, tools):
    """Install system prerequisites."""
    script_path = resolve_script_path("shared/installation/prerequisite_installer.py")

    cmd = [sys.executable, str(script_path)]
    if check:
        cmd.append("--check")
    if interactive:
        cmd.append("--interactive")
    if tools:
        cmd.extend(["--install"] + list(tools))

    from shared.core.cli_manager import run_command
    result = run_command(cmd, "Managing system prerequisites")
    sys.exit(0 if result.success else 1)
