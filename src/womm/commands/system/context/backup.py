#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT BACKUP - Backup file commands
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Backup commands for the context menu.

Everything under this group addresses backup *files*. Names are resolved
inside the backup directory and never treated as paths: ``restore`` writes
to the Windows registry, so an unresolved name must stop before it.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys
from datetime import datetime
from pathlib import Path
from typing import cast

# Third-party imports
import click
from ezpl import LogLevel
from rich.progress import TaskID

# Local imports
from ....interfaces import ContextMenuInterface
from ....shared.results.context_results import (
    BackupDataResult,
    BackupFileInfo,
    ContextCherryPickResult,
)
from ....ui.common import ezpl_bridge, ezprinter
from ....ui.context import ContextMenuUI
from ....ui.context.display import (
    render_context_backup_content_result,
    render_context_backup_list_result,
    render_context_backup_result,
    render_context_cherry_pick_result,
    render_context_restore_result,
)
from . import _check_windows, context_backup_group

# ///////////////////////////////////////////////////////////////
# BACKUP CREATION
# ///////////////////////////////////////////////////////////////


@context_backup_group.command("create")
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
def context_backup_create(output: str | None, verbose: bool) -> None:
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


# ///////////////////////////////////////////////////////////////
# BACKUP INSPECTION
# ///////////////////////////////////////////////////////////////


@context_backup_group.command("list")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def context_backup_list(verbose: bool) -> None:
    """📋 List available context menu backup files."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Context Menu Backups")

    manager = ContextMenuInterface()

    if not _check_windows(manager):
        return

    result = manager.list_backups()

    render_context_backup_list_result(result)
    sys.exit(0 if result.success else 1)


@context_backup_group.command("show")
@click.help_option("-h", "--help")
@click.argument("name")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def context_backup_show(name: str, verbose: bool) -> None:
    """🔍 Show the content of a context menu backup.

    NAME is a bare backup file name, as listed by 'backup list'.
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Context Menu Backup Content")

    manager = ContextMenuInterface()

    if not _check_windows(manager):
        return

    result = manager.read_backup(name)

    render_context_backup_content_result(result)
    sys.exit(0 if result.success else 1)


# ///////////////////////////////////////////////////////////////
# RESTORE
# ///////////////////////////////////////////////////////////////


def _describe_resolved_backup(
    resolved: Path, content: BackupDataResult
) -> BackupFileInfo:
    """Describe an already resolved and readable backup file.

    Built from the confined path and the parsed content only: the backup
    listing is deliberately not consulted, so a readable backup whose name
    falls outside the listing glob stays restorable.

    Args:
        resolved: Confined path returned by ``resolve_backup_path``.
        content: Successful result returned by ``read_backup``.

    Returns:
        The metadata record expected by the restore confirmation prompt.
    """
    try:
        stat = resolved.stat()
        size_bytes = stat.st_size
        modified_time = datetime.fromtimestamp(stat.st_mtime)
    except OSError:
        size_bytes = 0
        modified_time = None

    return BackupFileInfo(
        filename=resolved.name,
        filepath=str(resolved),
        size_bytes=size_bytes,
        modified_time=modified_time,
        entry_count=(content.metadata or {}).get("total_entries", 0),
    )


@context_backup_group.command("restore")
@click.help_option("-h", "--help")
@click.argument("name", required=False)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def context_backup_restore(name: str | None, verbose: bool) -> None:
    """🔄 Restore context menu entries from a backup.

    NAME is a bare backup file name, as listed by 'backup list'. Without
    NAME, a backup is chosen interactively.
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Context Menu Restore")

    manager = ContextMenuInterface()

    if not _check_windows(manager):
        return

    if name:
        content = manager.read_backup(name)
        if not content.success:
            ezprinter.error(str(content.error))
            ezprinter.info("Run 'womm context backup list' to see available names")
            sys.exit(1)

        resolved = manager.resolve_backup_path(name)
        if resolved is None:
            ezprinter.error(f"No readable backup named {name!r}")
            ezprinter.info("Run 'womm context backup list' to see available names")
            sys.exit(1)

        selected = _describe_resolved_backup(resolved, content)
        target = str(resolved)
    else:
        listing = manager.list_backups()
        if not listing.success:
            ezprinter.error(f"Could not list backups: {listing.error}")
            sys.exit(1)

        selected = ContextMenuUI.show_backup_selection_menu(listing.backups or [])
        if selected is None:
            ezprinter.info("Restore cancelled")
            return
        target = selected.filepath

    if not ContextMenuUI.confirm_restore_operation(selected):
        ezprinter.info("Restore cancelled")
        return

    with ezprinter.create_spinner_with_status(
        "Restoring context menu from backup..."
    ) as (progress, task):
        progress.update(cast(TaskID, task), status="Restoring from backup...")
        result = manager.restore_entries(target)

    render_context_restore_result(result)
    sys.exit(0 if result.success else 1)


# ///////////////////////////////////////////////////////////////
# CHERRY-PICK COMMANDS
# ///////////////////////////////////////////////////////////////


@context_backup_group.command("cherry-pick")
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
        ezprinter.info("Create a backup first using 'womm context backup create'")
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


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "context_backup_create",
    "context_backup_list",
    "context_backup_restore",
    "context_backup_show",
    "context_cherry_pick",
]
