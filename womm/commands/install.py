#!/usr/bin/env python3
"""
Installation commands for WOMM CLI.
Handles installation, uninstallation, and PATH management.
"""

# IMPORTS
########################################################
# Standard library imports
import sys

# Third-party imports
import click

from ..core.managers.installation.installation_manager import InstallationManager
from ..core.managers.installation.uninstallation_manager import UninstallationManager
from ..core.managers.system.user_path_manager import PathManager

# Local imports
from ..core.utils.security.security_validator import security_validator

# COMMAND FUNCTIONS
########################################################
# Main CLI command implementations


@click.command()
@click.help_option("-h", "--help")
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Force installation even if .womm directory exists",
)
@click.option(
    "-t",
    "--target",
    type=click.Path(),
    help="Custom target directory (default: ~/.womm)",
)
def install(force, target):
    """🚀 Install Works On My Machine in user directory."""
    # Security validation for target path
    if target:
        is_valid, error = security_validator.validate_path(target)
        if not is_valid:
            click.echo(f"[FAIL] Invalid target path: {error}", err=True)
            sys.exit(1)

    try:
        # Use InstallationManager for installation with integrated UI
        manager = InstallationManager()
        manager.install(force=force, target=target)

    except Exception as e:
        click.echo(f"[FAIL] Error during installation: {e}", err=True)
        sys.exit(1)


@click.command()
@click.help_option("-h", "--help")
@click.option(
    "-f", "--force", is_flag=True, help="Force uninstallation without confirmation"
)
@click.option(
    "-t",
    "--target",
    type=click.Path(),
    help="Custom target directory (default: ~/.womm)",
)
def uninstall(force, target):
    """🗑️ Uninstall Works On My Machine from user directory."""
    # Security validation for target path
    if target:
        is_valid, error = security_validator.validate_path(target)
        if not is_valid:
            click.echo(f"[FAIL] Invalid target path: {error}", err=True)
            sys.exit(1)

    try:
        # Use UninstallationManager for uninstallation with integrated UI
        manager = UninstallationManager(target=target)
        manager.uninstall(force=force)

    except Exception as e:
        click.echo(f"[FAIL] Error during uninstallation: {e}", err=True)
        sys.exit(1)


@click.command("path")
@click.help_option("-h", "--help")
@click.option(
    "-b", "--backup", "backup_flag", is_flag=True, help="Create a PATH backup"
)
@click.option(
    "-r", "--restore", "restore_flag", is_flag=True, help="Restore PATH from backup"
)
@click.option(
    "-l", "--list", "list_flag", is_flag=True, help="List available PATH backups"
)
@click.option(
    "-t",
    "--target",
    type=click.Path(),
    help="Custom target directory (default: ~/.womm)",
)
def path_cmd(backup_flag, restore_flag, list_flag, target):
    """🧭 PATH utilities: backup, restore, and list backups."""
    # Security validation for target path
    if target:
        is_valid, error = security_validator.validate_path(target)
        if not is_valid:
            click.echo(f"[FAIL] Invalid target path: {error}", err=True)
            sys.exit(1)

    # Validate mutually exclusive operations
    selected = sum(bool(x) for x in (backup_flag, restore_flag, list_flag))
    if selected > 1:
        click.echo(
            "[FAIL] Choose only one action among --backup, --restore, or --list",
            err=True,
        )
        sys.exit(1)
    # Default to list if nothing selected
    if selected == 0:
        list_flag = True

    try:
        manager = PathManager(target=target)

        if list_flag:
            manager.list_backup()
        elif restore_flag:
            manager.restore_path()
        elif backup_flag:
            manager.backup_path()

    except Exception as e:
        click.echo(f"[FAIL] PATH command error: {e}", err=True)
        sys.exit(1)
