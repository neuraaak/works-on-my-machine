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
from pathlib import Path

# Third-party imports
import click
from ezpl import LogLevel

# Local imports
from ...interfaces import (
    SystemPathInterface,
    WommInstallerInterface,
    WommUninstallerInterface,
)
from ...services import SecurityValidatorService
from ...ui.common import (
    InteractiveMenu,
    confirm,
    ezconsole,
    ezpl_bridge,
    ezprinter,
    format_backup_item,
)
from ...ui.system import (
    render_path_backup_list_result,
    render_path_backup_result,
    render_path_operation_result,
)
from ...ui.womm_setup import (
    render_install_plan_failure,
    render_installation_result,
    render_uninstall_cancelled,
    render_uninstall_plan_failure,
    render_uninstallation_result,
    render_windows_install_tips,
)

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

    ezprinter.print_header("W.O.M.M Installation")

    manager = WommInstallerInterface()
    plan = manager.precheck_install(target=target, force=force)
    if not plan.success:
        render_install_plan_failure(plan)
        sys.exit(1)

    stages = _build_install_stages(len(plan.files_to_copy or []))
    with ezprinter.create_dynamic_layered_progress(stages) as progress:
        result = manager.execute_install(
            plan, progress, refresh_env=not no_refresh_env, verbose=verbose
        )

    render_installation_result(result)
    if result.success and manager.platform == "Windows":
        render_windows_install_tips()

    sys.exit(0 if result.success else 1)


def _build_install_stages(file_count: int) -> list[dict]:
    """Build the DynamicLayeredProgress stage configuration for an install run.

    Args:
        file_count: Number of files to copy, used to size the "file_copy" bar

    Returns:
        list[dict]: Stage configuration for ``create_dynamic_layered_progress``
    """
    return [
        {
            "name": "main_installation",
            "type": "main",
            "steps": [
                "Preparation",
                "File Copy",
                "Executable",
                "Backup",
                "PATH Setup",
                "Verification",
            ],
            "description": "WOMM Installation Progress",
            "style": "bold bright_white",
        },
        {
            "name": "preparation",
            "type": "spinner",
            "description": "Preparing installation environment...",
            "style": "bright_blue",
        },
        {
            "name": "file_copy",
            "type": "progress",
            "total": file_count,
            "description": "Copying project files...",
            "style": "bright_blue",
        },
        {
            "name": "executable",
            "type": "spinner",
            "description": "Creating executable script...",
            "style": "bright_blue",
        },
        {
            "name": "backup",
            "type": "spinner",
            "description": "Creating PATH backup...",
            "style": "bright_blue",
        },
        {
            "name": "path_setup",
            "type": "spinner",
            "description": "Configuring PATH environment...",
            "style": "bright_blue",
        },
        {
            "name": "verification",
            "type": "steps",
            "steps": [
                "File integrity check",
                "Essential files verification",
                "Command accessibility test",
                "PATH configuration test",
            ],
            "description": "Verifying installation...",
            "style": "bright_blue",
        },
    ]


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

    ezprinter.print_header("W.O.M.M Uninstallation")

    manager = WommUninstallerInterface(target)
    plan = manager.plan_uninstall()
    if not plan.success:
        render_uninstall_plan_failure(plan)
        sys.exit(1)

    if not force:
        ezconsole.print("")
        warning_panel = ezprinter.create_warning_panel(
            title="Uninstallation Confirmation",
            content=f"This will completely remove WOMM from {plan.target_path}.\n\n"
            "This action cannot be undone.",
        )
        ezconsole.print("")
        ezconsole.print(warning_panel)

        if not confirm(
            "Do you want to continue and remove WOMM completely?", default=False
        ):
            render_uninstall_cancelled()
            return

        ezconsole.print("")
        ezprinter.system("Proceeding with uninstallation...")

    stages = _build_uninstall_stages(len(plan.files_to_remove or []))
    ezconsole.print("")
    with ezprinter.create_dynamic_layered_progress(stages) as progress:
        result = manager.execute_uninstall(plan, progress, verbose=verbose)

    render_uninstallation_result(result)
    sys.exit(0 if result.success else 1)


def _build_uninstall_stages(file_count: int) -> list[dict]:
    """Build the DynamicLayeredProgress stage configuration for an uninstall run.

    Args:
        file_count: Number of files/directories to remove, used to size the
            "file_removal" bar

    Returns:
        list[dict]: Stage configuration for ``create_dynamic_layered_progress``
    """
    return [
        {
            "name": "main_uninstallation",
            "type": "main",
            "steps": [
                "Preparation",
                "PATH Cleanup",
                "File Removal",
                "Verification",
            ],
            "description": "WOMM Uninstallation Progress",
            "style": "bold bright_white",
        },
        {
            "name": "preparation",
            "type": "spinner",
            "description": "Preparing uninstallation environment...",
            "style": "bright_blue",
        },
        {
            "name": "path_cleanup",
            "type": "spinner",
            "description": "Removing from PATH...",
            "style": "bright_blue",
        },
        {
            "name": "file_removal",
            "type": "progress",
            "total": file_count,
            "description": "Removing installation files...",
            "style": "bright_blue",
        },
        {
            "name": "verification",
            "type": "steps",
            "steps": [
                "File removal check",
                "Command accessibility test",
            ],
            "description": "Verifying uninstallation...",
            "style": "bright_blue",
        },
    ]


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
            ezprinter.print_header("W.O.M.M PATH Backup List")
            result = manager.list_backups()
            render_path_backup_list_result(result)
            if not result.success:
                sys.exit(1)

        elif backup_flag:
            ezprinter.print_header("W.O.M.M PATH Backup Creation")
            backup_result = manager.create_backup()
            render_path_backup_result(backup_result)
            if not backup_result.success:
                sys.exit(1)

        elif restore_flag:
            ezprinter.print_header("W.O.M.M PATH Restoration")
            _run_path_restore(manager)

    except Exception as e:
        ezprinter.error(f"Unexpected PATH command error: {e}")
        sys.exit(1)


def _run_path_restore(manager: SystemPathInterface) -> None:
    """Interactively select a PATH backup and restore it.

    Args:
        manager: PATH interface used to list backups and perform the restore.
    """
    list_result = manager.list_backups()
    if not list_result.success:
        render_path_backup_list_result(list_result)
        sys.exit(1)

    backups = list_result.backups or []
    if not backups:
        ezprinter.system("No PATH backups found")
        return

    table = ezprinter.create_table(
        title="Available PATH Backups",
        columns=[
            ("Index", "cyan", True),
            ("Backup File", "green", False),
            ("Date", "yellow", False),
            ("Size", "blue", False),
            ("PATH Entries", "magenta", False),
        ],
    )
    for i, backup in enumerate(backups, 1):
        table.add_row(
            str(i),
            backup.name,
            backup.modified,
            f"{backup.size} bytes",
            str(backup.path_entries),
        )
    ezpl_bridge.console.print(table)
    ezpl_bridge.console.print("")

    menu_items = [
        {"file": Path(backup.path), "path_entries": backup.path_entries}
        for backup in backups
    ]
    menu = InteractiveMenu(title="Select Backup to Restore", border_style="cyan")
    selected = menu.select_from_list(menu_items, display_func=format_backup_item)
    if selected is None:
        ezprinter.system("Restoration cancelled")
        return

    confirm_menu = InteractiveMenu(title="Confirm Restoration", border_style="yellow")
    if not confirm_menu.confirm_action("Proceed with restoration?", default_yes=True):
        ezprinter.system("Restoration cancelled")
        return

    restore_result = manager.restore_backup(selected["file"])
    render_path_operation_result(restore_result)
    if restore_result.success:
        ezprinter.info(
            "You may need to restart your terminal for changes to take effect"
        )
    else:
        sys.exit(1)
