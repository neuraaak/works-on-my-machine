#!/usr/bin/env python3
"""
Context menu commands for WOMM CLI.
Handles Windows context menu management.
"""

# IMPORTS
########################################################
# External modules and dependencies

import platform
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
@click.option(
    "--target",
    "target_path",
    type=click.Path(exists=True),
    required=True,
    help="Script or executable to register in context menu",
)
@click.option("--label", required=True, help="Label to display in context menu")
@click.option(
    "--registrator-args",
    multiple=True,
    help="Extra args passed to registrator (e.g., shell type, icon)",
)
@click.option("--backup", is_flag=True, help="Create backup before registration")
@click.option("--dry-run", is_flag=True, help="Show command without executing")
@click.option("--verbose", is_flag=True, help="Verbose mode")
def context_register(target_path, label, registrator_args, backup, dry_run, verbose):
    """➕ Register WOMM tools in Windows context menu."""
    if platform.system().lower() != "windows":
        click.echo("This command is only available on Windows.")
        sys.exit(0)
    script_path = resolve_script_path("womm/core/system/registrator.py")

    # Optional pre-backup of context entries
    if backup:
        from ..core.utils.cli_manager import run_command as _run

        _ = _run(
            [sys.executable, str(script_path), "--backup", "context_menu_backup.json"],
            "Backing up context menu entries",
        )

    # Build registrator command: python registrator.py <target> <label> [extra]
    cmd = [sys.executable, str(script_path), str(target_path), str(label)]
    for extra in registrator_args:
        cmd.extend(extra.split())

    from ..core.utils.cli_manager import run_command

    if dry_run:
        click.echo(f"$ {' '.join(map(str, cmd))}")
        sys.exit(0)

    if verbose:
        from womm.core.ui.console import print_system

        print_system(f"Executing: {' '.join(map(str, cmd))}")

    result = run_command(cmd, "Registering context menu tools")
    if not result.success:
        from womm.core.ui.console import print_error

        print_error(
            f"Registration failed (code {result.returncode}).\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    sys.exit(0 if result.success else 1)


@context_group.command("unregister")
@click.option(
    "--remove",
    "remove_key",
    required=True,
    help="Key name to remove (as stored in registry)",
)
@click.option("--dry-run", is_flag=True, help="Show command without executing")
@click.option("--verbose", is_flag=True, help="Verbose mode")
def context_unregister(remove_key, dry_run, verbose):
    """➖ Unregister WOMM tools from Windows context menu."""
    if platform.system().lower() != "windows":
        click.echo("This command is only available on Windows.")
        sys.exit(0)
    script_path = resolve_script_path("womm/core/system/registrator.py")

    cmd = [sys.executable, str(script_path), "--remove", str(remove_key)]
    from ..core.utils.cli_manager import run_command

    if dry_run:
        click.echo(f"$ {' '.join(map(str, cmd))}")
        sys.exit(0)

    if verbose:
        from womm.core.ui.console import print_system

        print_system(f"Executing: {' '.join(map(str, cmd))}")

    result = run_command(cmd, "Unregistering context menu tools")
    if not result.success:
        from womm.core.ui.console import print_error

        print_error(
            f"Unregistration failed (code {result.returncode}).\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    sys.exit(0 if result.success else 1)


@context_group.command("list")
@click.option("--dry-run", is_flag=True, help="Show command without executing")
@click.option("--verbose", is_flag=True, help="Verbose mode")
def context_list(dry_run, verbose):
    """📋 List registered context menu entries."""
    if platform.system().lower() != "windows":
        click.echo("This command is only available on Windows.")
        sys.exit(0)

    script_path = resolve_script_path("womm/core/system/registrator.py")

    cmd = [sys.executable, str(script_path), "--list"]
    from ..core.utils.cli_manager import run_command

    if dry_run:
        click.echo(f"$ {' '.join(map(str, cmd))}")
        sys.exit(0)

    if verbose:
        from womm.core.ui.console import print_system

        print_system(f"Executing: {' '.join(map(str, cmd))}")

    result = run_command(cmd, "Listing context menu entries")
    if not result.success:
        from womm.core.ui.console import print_error

        print_error(
            f"List failed (code {result.returncode}).\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    sys.exit(0 if result.success else 1)


@context_group.command("status")
def context_status():
    """ℹ️ Show context menu registration status (Windows only)."""
    if platform.system().lower() != "windows":
        click.echo("This command is only available on Windows.")
        sys.exit(0)

    script_path = resolve_script_path("womm/core/system/registrator.py")
    cmd = [sys.executable, str(script_path), "--list"]
    from ..core.utils.cli_manager import run_command

    result = run_command(cmd, "Context menu status")
    sys.exit(0 if result.success else 1)
