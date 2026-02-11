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

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys

# Third-party imports
import click
from ezpl.types import LogLevel

# Local imports
from ...exceptions.system import (
    FileSystemServiceError,
    RegistryServiceError,
    UserPathServiceError,
)
from ...exceptions.womm_deployment import DeploymentUtilityError, WommUninstallerError
from ...interfaces import (
    SystemPathInterface,
    WommInstallerInterface,
    WommUninstallerInterface,
)
from ...services import SecurityValidatorService
from ...ui.common import ezpl_bridge, ezprinter

# ///////////////////////////////////////////////////////////////
# INSTALLATION COMMANDS
# ///////////////////////////////////////////////////////////////


@click.command()
@click.help_option("-h", "--help")
@click.option(
    "--force",
    is_flag=True,
    help="Force installation even if .womm directory exists",
)
@click.option(
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
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def install(
    force: bool, target: str | None, no_refresh_env: bool, verbose: bool
) -> None:
    """🚀 Install Works On My Machine in user directory."""
    # Configure verbose mode if requested
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Security validation for target path
    if target:
        validator = SecurityValidatorService()
        validation_result = validator.validate_directory_path(target)
        if not validation_result.is_valid:
            ezprinter.error(
                f"Invalid target path: {target} - {validation_result.validation_reason}"
            )
            sys.exit(1)

    try:
        # Use InstallationManager for installation with integrated UI
        manager = WommInstallerInterface()
        manager.install(force=force, target=target, refresh_env=not no_refresh_env)

    except DeploymentUtilityError as e:
        ezprinter.error(f"Installation error: {e.message}")
        if e.details:
            ezprinter.error(f"Details: {e.details}")
        sys.exit(1)
    except RegistryServiceError as e:
        ezprinter.error(
            f"PATH utility error: Registry {e.operation} failed for {e.registry_key}: {e.reason}"
        )
        if e.details:
            ezprinter.error(f"Details: {e.details}")
        sys.exit(1)
    except FileSystemServiceError as e:
        ezprinter.error(
            f"PATH utility error: File {e.operation} failed for {e.path}: {e.reason}"
        )
        if e.details:
            ezprinter.error(f"Details: {e.details}")
        sys.exit(1)
    except UserPathServiceError as e:
        ezprinter.error(f"PATH utility error: {e.message}")
        if e.details:
            ezprinter.error(f"Details: {e.details}")
        sys.exit(1)
    except Exception as e:
        ezprinter.error(f"Unexpected installation error: {e}")
        sys.exit(1)


# ///////////////////////////////////////////////////////////////
# UNINSTALLATION COMMANDS
# ///////////////////////////////////////////////////////////////


@click.command()
@click.help_option("-h", "--help")
@click.option("--force", is_flag=True, help="Force uninstallation without confirmation")
@click.option(
    "--target",
    type=click.Path(),
    help="Custom target directory (default: ~/.womm)",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def uninstall(force: bool, target: str | None, verbose: bool) -> None:
    """🗑️ Uninstall Works On My Machine from user directory."""
    # Configure verbose mode if requested
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Security validation for target path
    if target:
        validator = SecurityValidatorService()
        validation_result = validator.validate_directory_path(target)
        if not validation_result.is_valid:
            ezprinter.error(
                f"Invalid target path: {target} - {validation_result.validation_reason}"
            )
            sys.exit(1)

    try:
        # Use UninstallationManager for uninstallation with integrated UI
        manager = WommUninstallerInterface(target)
        manager.uninstall(force=force)

    except WommUninstallerError as e:
        ezprinter.error(f"Uninstallation error: {e.message}")
        if e.details:
            ezprinter.error(f"Details: {e.details}")
        sys.exit(1)
    except DeploymentUtilityError as e:
        ezprinter.error(f"Uninstallation utility error: {e.message}")
        if e.details:
            ezprinter.error(f"Details: {e.details}")
        sys.exit(1)
    except Exception as e:
        ezprinter.error(f"Unexpected uninstallation error: {e}")
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
        validator = SecurityValidatorService()
        validation_result = validator.validate_directory_path(target)
        if not validation_result.is_valid:
            ezprinter.error(
                f"Invalid target path: {target} - {validation_result.validation_reason}"
            )
            sys.exit(1)

    # Validate mutually exclusive operations
    selected = sum(bool(x) for x in (backup_flag, restore_flag, list_flag))
    if selected > 1:
        ezprinter.error("Choose only one action among --backup, --restore, or --list")
        sys.exit(1)
    # Default to list if nothing selected
    if selected == 0:
        list_flag = True

    try:
        manager = SystemPathInterface(target=target)

        if list_flag:
            manager.list_backup()
        elif restore_flag:
            manager.restore_path()
        elif backup_flag:
            manager.backup_path()

    except Exception as e:
        ezprinter.error(f"Unexpected PATH command error: {e}")
        sys.exit(1)
