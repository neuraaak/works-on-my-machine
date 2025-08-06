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

# Local imports
from ..utils.security import SECURITY_AVAILABLE, security_validator

# COMMAND FUNCTIONS
########################################################
# Main CLI command implementations


@click.command()
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force installation even if .womm directory exists",
)
@click.option(
    "--target", type=click.Path(), help="Custom target directory (default: ~/.womm)"
)
def install(force, target):
    """🚀 Install Works On My Machine in user directory."""
    # Security validation for target path
    if target and SECURITY_AVAILABLE:
        is_valid, error = security_validator.validate_path(target)
        if not is_valid:
            click.echo(f"[FAIL] Invalid target path: {error}", err=True)
            sys.exit(1)

    try:
        from shared.installation.installer import InstallationManager

        # Use InstallationManager for installation with integrated UI
        manager = InstallationManager()
        manager.install(force=force, target=target)

    except ImportError as e:
        click.echo(f"[FAIL] Error importing installer: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"[FAIL] Error during installation: {e}", err=True)
        sys.exit(1)


@click.command()
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force uninstallation without confirmation",
)
@click.option(
    "--target", type=click.Path(), help="Custom target directory (default: ~/.womm)"
)
def uninstall(force, target):
    """🗑️ Uninstall Works On My Machine from user directory."""
    # Security validation for target path
    if target and SECURITY_AVAILABLE:
        is_valid, error = security_validator.validate_path(target)
        if not is_valid:
            click.echo(f"[FAIL] Invalid target path: {error}", err=True)
            sys.exit(1)

    try:
        from shared.installation.uninstaller import UninstallationManager

        # Use UninstallationManager for uninstallation with integrated UI
        manager = UninstallationManager(target=target)
        manager.uninstall(force=force)

    except ImportError as e:
        click.echo(f"[FAIL] Error importing uninstaller: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"[FAIL] Error during uninstallation: {e}", err=True)
        sys.exit(1)


@click.command()
@click.option(
    "--target", type=click.Path(), help="Custom target directory (default: ~/.womm)"
)
@click.option(
    "--list",
    "-l",
    is_flag=True,
    help="List available PATH backups instead of creating a new one",
)
def restore_path(target, list):
    """🔄 Restore user PATH from backup created during installation."""
    # Security validation for target path
    if target and SECURITY_AVAILABLE:
        is_valid, error = security_validator.validate_path(target)
        if not is_valid:
            click.echo(f"[FAIL] Invalid target path: {error}", err=True)
            sys.exit(1)

    try:
        from shared.installation.path_manager import PathManager

        # Use PathManager with integrated UI
        manager = PathManager(target=target)

        if list:
            # List existing backups
            manager.list_backup()
        else:
            # Restore PATH from backup
            manager.restore_path()

    except ImportError as e:
        click.echo(f"[FAIL] Error importing path manager: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"[FAIL] Error during PATH restoration: {e}", err=True)
        sys.exit(1)


@click.command()
@click.option(
    "--target", type=click.Path(), help="Custom target directory (default: ~/.womm)"
)
@click.option(
    "--list",
    "-l",
    is_flag=True,
    help="List available PATH backups instead of creating a new one",
)
def backup_path(target, list):
    """💾 Show information about PATH backup."""
    # Security validation for target path
    if target and SECURITY_AVAILABLE:
        is_valid, error = security_validator.validate_path(target)
        if not is_valid:
            click.echo(f"[FAIL] Invalid target path: {error}", err=True)
            sys.exit(1)

    try:
        from shared.installation.path_manager import PathManager

        # Use PathManager with integrated UI
        manager = PathManager(target=target)

        if list:
            # List existing backups
            manager.list_backup()
        else:
            # Create new backup
            manager.backup_path()

    except ImportError as e:
        click.echo(f"[FAIL] Error importing path manager: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"[FAIL] Error reading backup info: {e}", err=True)
        sys.exit(1)
