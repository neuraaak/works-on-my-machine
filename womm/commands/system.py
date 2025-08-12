#!/usr/bin/env python3
"""
System commands for WOMM CLI.
Handles system detection and prerequisites installation.
"""

# IMPORTS
########################################################
# Standard library imports

# Third-party imports
import click

# Local imports
# (None for this file)


# MAIN FUNCTIONS
########################################################
# Core CLI functionality and command groups


@click.group()
def system_group():
    """🔧 System detection and prerequisites."""


# COMMAND FUNCTIONS
########################################################
# Command implementations


@system_group.command("detect")
def system_detect():
    """🔍 Detect system information and available tools."""
    from womm.core.system import system_manager

    # Use SystemManager for system detection with integrated UI
    system_manager.detect_system()


@system_group.command("install")
@click.option("--check", is_flag=True, help="Only check prerequisites")
@click.option(
    "--pm-args",
    help="Extra arguments passed to the package manager (quoted string)",
    multiple=True,
)
@click.option(
    "--ask-path",
    is_flag=True,
    help="Interactively ask for an installation path (best-effort, Windows only)",
)
@click.argument("tools", nargs=-1, type=click.Choice(["python", "node", "git", "all"]))
def system_install(check, pm_args, ask_path, tools):
    """📦 Install system prerequisites."""
    from womm.core.system import system_manager

    # Use SystemManager for prerequisites management with integrated UI
    if check:
        system_manager.check_prerequisites(list(tools))
    else:
        # Flatten pm_args (Click multiple=True yields a tuple of strings)
        extra_args = [a for a in pm_args if a]
        system_manager.install_prerequisites(
            list(tools), pm_args=extra_args, ask_path=ask_path
        )
