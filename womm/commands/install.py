#!/usr/bin/env python3
"""
Installation commands for WOMM CLI.
Handles installation, uninstallation, and PATH management.
"""

import sys
from pathlib import Path

import click

from ..utils.path_manager import resolve_script_path
from ..utils.security import SECURITY_AVAILABLE, run_secure_command, security_validator


@click.group()
def install_group():
    """📦 Installation and uninstallation commands."""


@install_group.command("install")
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force installation even if .womm directory exists",
)
@click.option(
    "--no-prerequisites", is_flag=True, help="Skip prerequisites installation"
)
@click.option(
    "--no-context-menu", is_flag=True, help="Skip Windows context menu integration"
)
@click.option(
    "--target", type=click.Path(), help="Custom target directory (default: ~/.womm)"
)
def install(force, no_prerequisites, no_context_menu, target):
    """Install Works On My Machine in user directory."""
    # Security validation for target path
    if target and SECURITY_AVAILABLE:
        is_valid, error = security_validator.validate_path(target)
        if not is_valid:
            click.echo(f"❌ Invalid target path: {error}", err=True)
            sys.exit(1)

    script_path = resolve_script_path("shared/installation/installer.py")

    cmd = [sys.executable, str(script_path)]

    if force:
        cmd.append("--force")
    if no_prerequisites:
        cmd.append("--no-prerequisites")
    if no_context_menu:
        cmd.append("--no-context-menu")
    if target:
        cmd.extend(["--target", target])

    # Use secure command execution if available
    if SECURITY_AVAILABLE:
        result = run_secure_command(cmd, "Installing Works On My Machine")
    else:
        from shared.core.cli_manager import run_command
        result = run_command(cmd, "Installing Works On My Machine")

    sys.exit(0 if result.success else 1)


@install_group.command("uninstall")
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
    """Uninstall Works On My Machine from user directory."""
    # Security validation for target path
    if target and SECURITY_AVAILABLE:
        is_valid, error = security_validator.validate_path(target)
        if not is_valid:
            click.echo(f"❌ Invalid target path: {error}", err=True)
            sys.exit(1)

    script_path = resolve_script_path("shared/installation/uninstaller.py")

    cmd = [sys.executable, str(script_path)]

    if force:
        cmd.append("--force")
    if target:
        cmd.extend(["--target", target])

    # Use secure command execution if available
    if SECURITY_AVAILABLE:
        result = run_secure_command(cmd, "Uninstalling Works On My Machine")
    else:
        from shared.core.cli_manager import run_command
        result = run_command(cmd, "Uninstalling Works On My Machine")

    sys.exit(0 if result.success else 1)


@install_group.command("restore-path")
@click.option(
    "--target", type=click.Path(), help="Custom target directory (default: ~/.womm)"
)
def restore_path(target):
    """Restore user PATH from backup created during installation."""
    # Security validation for target path
    if target and SECURITY_AVAILABLE:
        is_valid, error = security_validator.validate_path(target)
        if not is_valid:
            click.echo(f"❌ Invalid target path: {error}", err=True)
            sys.exit(1)

    # Import the restore function from installer
    try:
        from shared.installation.installer import (
            get_target_womm_path,
            restore_user_path,
        )

        # Use custom target if specified
        if target:
            target_path = Path(target).expanduser().resolve()
        else:
            target_path = get_target_womm_path()

        if restore_user_path(target_path):
            click.echo("✅ PATH restored successfully")
            sys.exit(0)
        else:
            click.echo("❌ Failed to restore PATH", err=True)
            sys.exit(1)

    except ImportError as e:
        click.echo(f"❌ Error importing restore function: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error during PATH restoration: {e}", err=True)
        sys.exit(1)


@install_group.command("backup-info")
@click.option(
    "--target", type=click.Path(), help="Custom target directory (default: ~/.womm)"
)
def backup_info(target):
    """Show information about PATH backup."""
    # Security validation for target path
    if target and SECURITY_AVAILABLE:
        is_valid, error = security_validator.validate_path(target)
        if not is_valid:
            click.echo(f"❌ Invalid target path: {error}", err=True)
            sys.exit(1)

    try:
        from shared.installation.installer import get_target_womm_path

        # Use custom target if specified
        if target:
            target_path = Path(target).expanduser().resolve()
        else:
            target_path = get_target_womm_path()

        backup_dir = target_path / ".backup"
        latest_backup = backup_dir / ".path"

        if not backup_dir.exists():
            click.echo("❌ No backup directory found")
            sys.exit(1)

        if not latest_backup.exists():
            click.echo("❌ No PATH backup found")
            sys.exit(1)

        # Read backup info
        with open(latest_backup, encoding="utf-8") as f:
            lines = f.readlines()

        click.echo("📋 PATH Backup Information:")
        click.echo("=" * 40)

        for line in lines[:5]:  # Show first 5 lines (header info)
            if line.startswith("#"):
                click.echo(line.strip())

        click.echo(f"\n📁 Backup location: {backup_dir}")
        click.echo(f"📄 Latest backup: {latest_backup}")

        # Show all backup files
        backup_files = list(backup_dir.glob(".path_*"))
        if backup_files:
            click.echo(f"\n📚 Available backups ({len(backup_files)}):")
            for backup_file in sorted(backup_files, reverse=True):
                click.echo(f"  - {backup_file.name}")

        sys.exit(0)

    except ImportError as e:
        click.echo(f"❌ Error importing functions: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error reading backup info: {e}", err=True)
        sys.exit(1)
