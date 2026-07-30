#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT - Context Menu Commands
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Context menu commands for WOMM CLI.

This module handles Windows context menu management for scripts and tools.
Provides commands for registering, unregistering, and managing context menu entries.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import cast

# Third-party imports
import click
from ezpl import LogLevel
from rich.progress import TaskID

# Local imports
from ...interfaces import ContextMenuInterface
from ...services.context import ContextParameters
from ...shared.results.context_results import ContextCherryPickResult
from ...ui.common import ezpl_bridge, ezprinter
from ...ui.context import ContextMenuUI, ContextMenuWizard
from ...ui.context.display import (
    render_context_backup_result,
    render_context_cherry_pick_result,
    render_context_entries_result,
    render_context_restore_result,
    render_context_setup_result,
    render_context_status_result,
    render_script_registration_result,
    render_script_unregistration_result,
)

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

_NON_WINDOWS_MESSAGE = "Context menu management is Windows-specific"

# ///////////////////////////////////////////////////////////////
# COMMAND GROUPS
# ///////////////////////////////////////////////////////////////


@click.group(invoke_without_command=True)
@click.pass_context
def context_group(ctx: click.Context) -> None:
    """Windows context menu management."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


def _check_windows(manager: ContextMenuInterface) -> bool:
    """Print the non-Windows notice and report support status.

    Returns:
        True when running on Windows, False otherwise.
    """
    if manager.is_windows():
        return True
    ezprinter.info(_NON_WINDOWS_MESSAGE)
    return False


def _resolve_registration_target(
    target_path: str | None,
    label: str | None,
    icon: str,
    root: bool,
    file: bool,
    files: bool,
    background: bool,
    file_types: tuple[str, ...],
    extensions: tuple[str, ...],
    interactive: bool,
) -> tuple[str, str, str, ContextParameters] | None:
    """Resolve the (target, label, icon, context_params) tuple for registration.

    Runs the interactive wizard or validates the non-interactive flags.

    Returns:
        The resolved tuple, or None if the user cancelled (interactive) or a
        required option is missing (non-interactive).
    """
    if interactive:
        wizard_target, wizard_label, wizard_icon, context_params = (
            ContextMenuWizard.run_setup()
        )
        if not wizard_target or not wizard_label or context_params is None:
            return None
        resolved_icon = (
            wizard_icon if isinstance(wizard_icon, str) and wizard_icon else "auto"
        )
        return wizard_target, wizard_label, resolved_icon, context_params

    if not target_path:
        ezprinter.error("Missing required option: --target")
        ezprinter.info("Use --interactive for guided setup")
        return None
    if not label:
        ezprinter.error("Missing required option: --label")
        ezprinter.info("Use --interactive for guided setup")
        return None

    resolved_icon = icon if isinstance(icon, str) and icon else "auto"
    context_params = ContextParameters.from_flags(
        root=root,
        file=file,
        files=files,
        background=background,
        file_types=list(file_types) if file_types else None,
        extensions=list(extensions) if extensions else None,
    )
    return target_path, label, resolved_icon, context_params


# ///////////////////////////////////////////////////////////////
# REGISTRATION COMMANDS
# ///////////////////////////////////////////////////////////////


@context_group.command("register")
@click.help_option("-h", "--help")
@click.option(
    "--target",
    "target_path",
    type=click.Path(),
    help="Script or executable to register in context menu",
)
@click.option(
    "-l",
    "--label",
    help="Label to display in context menu",
)
@click.option(
    "--icon",
    default="auto",
    help="Icon path or 'auto' for auto-detection (default: auto)",
)
@click.option(
    "--root",
    is_flag=True,
    help="Register for root directories (drives) only",
)
@click.option(
    "--file",
    is_flag=True,
    help="Register for single file selection",
)
@click.option(
    "-F",
    "--files",
    is_flag=True,
    help="Register for multiple file selection",
)
@click.option(
    "--background",
    is_flag=True,
    help="Register for background context only",
)
@click.option(
    "--file-types",
    multiple=True,
    help="File types to register for (e.g., image, text, archive)",
)
@click.option(
    "--extension",
    "extensions",
    multiple=True,
    help="Custom file extensions (e.g., .py, .js)",
)
@click.option(
    "-I",
    "--interactive",
    is_flag=True,
    help="Interactive mode - guided setup",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Verbose mode",
)
def context_register(
    target_path: str | None,
    label: str | None,
    icon: str,
    root: bool,
    file: bool,
    files: bool,
    background: bool,
    file_types: tuple[str, ...],
    extensions: tuple[str, ...],
    interactive: bool,
    verbose: bool,
) -> None:
    """📝 Register scripts in Windows context menu."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Context Menu Registration")

    manager = ContextMenuInterface()

    if not _check_windows(manager):
        ezprinter.info("Consider using symbolic links or aliases on Unix systems")
        sys.exit(1)

    resolved = _resolve_registration_target(
        target_path,
        label,
        icon,
        root,
        file,
        files,
        background,
        file_types,
        extensions,
        interactive,
    )
    if resolved is None:
        if interactive:
            ezprinter.info("Registration cancelled")
            return
        sys.exit(1)
    resolved_target, resolved_label, resolved_icon, context_params = resolved

    if verbose:
        ezprinter.info(f"Target: {resolved_target}")
        ezprinter.info(f"Label: {resolved_label}")
        ezprinter.info(f"Icon: {resolved_icon}")
        if context_params:
            ezprinter.info(f"Context: {context_params.get_description()}")

    backup_dir = manager.get_backup_directory()
    backup_file = str(backup_dir / "context_menu_backup_before_register.json")
    with ezprinter.create_spinner_with_status(
        "Creating backup before registration..."
    ) as (progress, task):
        progress.update(cast(TaskID, task), status="Creating backup...")
        backup_result = manager.backup_entries(backup_file)

    if not backup_result.success:
        ezprinter.error(f"Backup failed: {backup_result.error}")
        sys.exit(1)

    if verbose:
        ezprinter.info(f"Backup created: {backup_file}")

    with ezprinter.create_spinner_with_status(
        "Registering script in context menu..."
    ) as (progress, task):
        progress.update(cast(TaskID, task), status="Adding registry entries...")
        result = manager.register_script(
            resolved_target, resolved_label, resolved_icon, False, context_params
        )

    render_script_registration_result(result)
    sys.exit(0 if result.success else 1)


# ///////////////////////////////////////////////////////////////
# UNREGISTRATION COMMANDS
# ///////////////////////////////////////////////////////////////


@context_group.command("unregister")
@click.help_option("-h", "--help")
@click.option(
    "--remove",
    "remove_key",
    required=True,
    help="Key name to remove (as stored in registry)",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def context_unregister(remove_key: str, verbose: bool) -> None:
    """🗑️ Unregister scripts from Windows context menu."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Context Menu Unregistration")

    manager = ContextMenuInterface()

    if not _check_windows(manager):
        return

    if verbose:
        ezprinter.info(f"Removing key: {remove_key}")

    with ezprinter.create_spinner_with_status(
        "Unregistering script from context menu..."
    ) as (progress, task):
        progress.update(cast(TaskID, task), status="Removing registry entries...")
        result = manager.unregister_script(remove_key)

    render_script_unregistration_result(result)
    sys.exit(0 if result.success else 1)


# ///////////////////////////////////////////////////////////////
# LISTING AND STATUS COMMANDS
# ///////////////////////////////////////////////////////////////


@context_group.command("list")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def context_list(verbose: bool) -> None:
    """📋 List registered context menu entries."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Context Menu List")

    manager = ContextMenuInterface()

    if not _check_windows(manager):
        return

    with ezprinter.create_spinner_with_status("Retrieving context menu entries...") as (
        progress,
        task,
    ):
        progress.update(cast(TaskID, task), status="Reading registry entries...")
        result = manager.list_entries()

    render_context_entries_result(result)
    sys.exit(0 if result.success else 1)


@context_group.command("status")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def context_status(verbose: bool) -> None:
    """📊 Show context menu registration status (Windows only)."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Context Menu Status")

    manager = ContextMenuInterface()

    if not _check_windows(manager):
        return

    with ezprinter.create_spinner_with_status(
        "Checking context menu registration status..."
    ) as (progress, task):
        progress.update(cast(TaskID, task), status="Retrieving context menu entries...")
        result = manager.get_status()

    render_context_status_result(result)
    sys.exit(0 if result.success else 1)


# ///////////////////////////////////////////////////////////////
# QUICK SETUP COMMANDS
# ///////////////////////////////////////////////////////////////


@context_group.command("quick-setup")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def context_quick_setup(verbose: bool) -> None:
    """⚡ Quick setup common WOMM tools in context menu."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Context Menu Quick Setup")

    manager = ContextMenuInterface()

    if not _check_windows(manager):
        return

    with ezprinter.create_spinner_with_status("Setting up common WOMM tools...") as (
        progress,
        task,
    ):
        progress.update(cast(TaskID, task), status="Registering WOMM tools...")
        result = manager.quick_setup_tools(verbose)

    render_context_setup_result(result)
    sys.exit(0 if result.success else 1)


# ///////////////////////////////////////////////////////////////
# BACKUP AND RESTORE COMMANDS
# ///////////////////////////////////////////////////////////////


@context_group.command("backup")
@click.help_option("-h", "--help")
@click.option(
    "-o",
    "--output",
    help="Custom backup file path (default: auto-generated)",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def context_backup(output: str | None, verbose: bool) -> None:
    """💾 Create backup of current context menu entries."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Context Menu Backup")

    manager = ContextMenuInterface()

    if not _check_windows(manager):
        return

    if output:
        target_backup = output
    else:
        backup_dir = manager.get_backup_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_backup = str(backup_dir / f"context_menu_backup_{timestamp}.json")
    ezprinter.info(f"Backup location: {target_backup}")

    with ezprinter.create_spinner_with_status("Creating context menu backup...") as (
        progress,
        task,
    ):
        progress.update(cast(TaskID, task), status="Reading registry entries...")
        result = manager.backup_entries(target_backup)

    render_context_backup_result(result)
    sys.exit(0 if result.success else 1)


@context_group.command("restore")
@click.help_option("-h", "--help")
@click.option(
    "-f",
    "--backup-file",
    help="Specific backup file to restore (default: interactive selection)",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def context_restore(backup_file: str | None, verbose: bool) -> None:
    """🔄 Restore context menu entries from backup."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Context Menu Restore")

    manager = ContextMenuInterface()

    if not _check_windows(manager):
        return

    if backup_file:
        backup_path = Path(backup_file)
        if not backup_path.exists():
            ezprinter.error(f"Backup file not found: {backup_file}")
            sys.exit(1)
        selected_file = backup_path
    else:
        backup_dir = manager.get_backup_directory()
        selected = ContextMenuUI.show_backup_selection_menu(backup_dir, verbose)
        if selected is None:
            ezprinter.info("Restore cancelled")
            return
        selected_file = selected

    if not ContextMenuUI.confirm_restore_operation(selected_file):
        ezprinter.info("Restore cancelled")
        return

    with ezprinter.create_spinner_with_status(
        "Restoring context menu from backup..."
    ) as (progress, task):
        progress.update(cast(TaskID, task), status="Restoring from backup...")
        result = manager.restore_entries(str(selected_file))

    render_context_restore_result(result)
    sys.exit(0 if result.success else 1)


# ///////////////////////////////////////////////////////////////
# CHERRY-PICK COMMANDS
# ///////////////////////////////////////////////////////////////


@context_group.command("cherry-pick")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def context_cherry_pick(verbose: bool) -> None:
    """🍒 Cherry-pick specific context menu entries from backups."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Context Menu Cherry-Pick")

    manager = ContextMenuInterface()

    if not _check_windows(manager):
        return

    backup_dir = manager.get_backup_directory()
    if not backup_dir.exists():
        ezprinter.error("No backup directory found")
        ezprinter.info("Create a backup first using 'womm context backup'")
        sys.exit(1)

    with ezprinter.create_spinner_with_status("Scanning backup files...") as (
        progress,
        task,
    ):
        progress.update(cast(TaskID, task), status="Collecting context menu entries...")
        all_entries = manager.collect_entries_from_backups()

    if not all_entries:
        ezprinter.error("No context menu entries found in backups")
        sys.exit(1)

    current_keys = manager.get_current_entry_keys()
    available_entries = manager.filter_available_entries(all_entries, current_keys)

    if not available_entries:
        ezprinter.info("All context menu entries from backups are already installed")
        result = ContextCherryPickResult(success=True, message="already_installed")
        render_context_cherry_pick_result(result)
        return

    selected_entries = ContextMenuUI.show_cherry_pick_menu(available_entries)
    if not selected_entries:
        ezprinter.info("Cherry-pick cancelled")
        return

    with ezprinter.create_spinner_with_status(
        f"Applying {len(selected_entries)} selected entries..."
    ) as (progress, task):
        results = manager.apply_cherry_picked_entries(selected_entries)

    success_count = sum(1 for success in results.values() if success)
    result = ContextCherryPickResult(
        success=success_count == len(selected_entries),
        success_count=success_count,
        total_selected=len(selected_entries),
        selected_entries=list(results.keys()),
    )
    render_context_cherry_pick_result(result)
    sys.exit(0 if result.success else 1)
