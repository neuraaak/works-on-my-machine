#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# INSTALL - Installation Commands
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Installation commands for WOMM CLI.

This module handles installation, uninstallation, and PATH management commands
for the Works On My Machine CLI interface.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys

# Third-party imports
import click

# Local imports
from ..core.exceptions.installation import (
    InstallationUtilityError,
    UninstallationManagerError,
    UninstallationUtilityError,
)
from ..core.exceptions.system import FileSystemError, RegistryError, UserPathError
from ..core.managers.installation.installation_manager import InstallationManager
from ..core.managers.installation.uninstallation_manager import UninstallationManager
from ..core.managers.system.user_path_manager import PathManager
from ..core.ui.common.console import print_error
from ..core.utils.security.security_validator import security_validator

# ///////////////////////////////////////////////////////////////
# INSTALLATION COMMANDS
# ///////////////////////////////////////////////////////////////


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
@click.option(
    "--no-refresh-env",
    is_flag=True,
    help="Skip environment refresh after PATH configuration (Windows only)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
def install(
    force: bool, target: str | None, no_refresh_env: bool, dry_run: bool
) -> None:
    """🚀 Install Works On My Machine in user directory."""
    # Security validation for target path
    if target:
        is_valid = security_validator.validate_directory_path(target)
        if not is_valid:
            print_error(f"Invalid target path: {target}")
            sys.exit(1)

    try:
        # Use InstallationManager for installation with integrated UI
        manager = InstallationManager()
        manager.install(
            force=force, target=target, refresh_env=not no_refresh_env, dry_run=dry_run
        )

    except InstallationUtilityError as e:
        print_error(f"Installation error: {e.message}")
        if e.details:
            print_error(f"Details: {e.details}")
        sys.exit(1)
    except RegistryError as e:
        print_error(
            f"PATH utility error: Registry {e.operation} failed for {e.registry_key}: {e.reason}"
        )
        if e.details:
            print_error(f"Details: {e.details}")
        sys.exit(1)
    except FileSystemError as e:
        print_error(
            f"PATH utility error: File {e.operation} failed for {e.file_path}: {e.reason}"
        )
        if e.details:
            print_error(f"Details: {e.details}")
        sys.exit(1)
    except UserPathError as e:
        print_error(f"PATH utility error: {e.message}")
        if e.details:
            print_error(f"Details: {e.details}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected installation error: {e}")
        sys.exit(1)


# ///////////////////////////////////////////////////////////////
# UNINSTALLATION COMMANDS
# ///////////////////////////////////////////////////////////////


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
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
def uninstall(force: bool, target: str | None, dry_run: bool) -> None:
    """🗑️ Uninstall Works On My Machine from user directory."""
    # Security validation for target path
    if target:
        is_valid = security_validator.validate_directory_path(target)
        if not is_valid:
            print_error(f"Invalid target path: {target}")
            sys.exit(1)

    try:
        # Use UninstallationManager for uninstallation with integrated UI
        manager = UninstallationManager(target=target)
        manager.uninstall(force=force, dry_run=dry_run)

    except UninstallationManagerError as e:
        print_error(f"Uninstallation error: {e.message}")
        if e.details:
            print_error(f"Details: {e.details}")
        sys.exit(1)
    except UninstallationUtilityError as e:
        print_error(f"Uninstallation utility error: {e.message}")
        if e.details:
            print_error(f"Details: {e.details}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected uninstallation error: {e}")
        sys.exit(1)


# ///////////////////////////////////////////////////////////////
# PATH MANAGEMENT COMMANDS
# ///////////////////////////////////////////////////////////////


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
def path_cmd(
    backup_flag: bool, restore_flag: bool, list_flag: bool, target: str | None
) -> None:
    """🧭 PATH utilities: backup, restore, and list backups."""
    # Security validation for target path
    if target:
        is_valid = security_validator.validate_directory_path(target)
        if not is_valid:
            print_error(f"Invalid target path: {target}")
            sys.exit(1)

    # Validate mutually exclusive operations
    selected = sum(bool(x) for x in (backup_flag, restore_flag, list_flag))
    if selected > 1:
        print_error("Choose only one action among --backup, --restore, or --list")
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
        print_error(f"Unexpected PATH command error: {e}")
        sys.exit(1)
