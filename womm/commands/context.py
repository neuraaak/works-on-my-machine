#!/usr/bin/env python3
"""
Context menu commands for WOMM CLI.
Handles Windows context menu management.
"""

# IMPORTS
########################################################
# External modules and dependencies

import sys

import click

# IMPORTS
########################################################
# Internal modules and dependencies
from ..utils.path_manager import resolve_script_path

# MAIN FUNCTIONS
########################################################
# Core CLI functionality and command groups


@click.group()
def context_group():
    """🖱️ Windows context menu management."""


# COMMAND FUNCTIONS
########################################################
# Command implementations


@context_group.command("register")
@click.option("--backup", is_flag=True, help="Create backup before registration")
def context_register(backup):
    """➕ Register WOMM tools in Windows context menu."""
    script_path = resolve_script_path("shared/system/register_wom_tools.py")

    cmd = [sys.executable, str(script_path), "--register"]
    if backup:
        cmd.append("--backup")

    from shared.core.cli_manager import run_command

    result = run_command(cmd, "Registering context menu tools")
    sys.exit(0 if result.success else 1)


@context_group.command("unregister")
def context_unregister():
    """➖ Unregister WOMM tools from Windows context menu."""
    script_path = resolve_script_path("shared/system/register_wom_tools.py")

    cmd = [sys.executable, str(script_path), "--unregister"]
    from shared.core.cli_manager import run_command

    result = run_command(cmd, "Unregistering context menu tools")
    sys.exit(0 if result.success else 1)


@context_group.command("list")
def context_list():
    """📋 List registered context menu entries."""
    script_path = resolve_script_path("shared/system/registrator.py")

    cmd = [sys.executable, str(script_path), "--list"]
    from shared.core.cli_manager import run_command

    result = run_command(cmd, "Listing context menu entries")
    sys.exit(0 if result.success else 1)
