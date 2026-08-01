#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PATH DISPLAY - PATH Backup UI Display Functions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
PATH backup display functions for Works On My Machine.

Provides display functions for PATH backup, restore and listing results.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path

# Third-party imports
from rich.panel import Panel

# Local imports
from ...shared.results import (
    PathBackupContentResult,
    PathBackupListResult,
    PathBackupResult,
    PathOperationResult,
)
from ..common import ezconsole, ezpl_bridge, ezprinter

# ///////////////////////////////////////////////////////////////
# PANEL HELPERS
# ///////////////////////////////////////////////////////////////


def _show_panel(content: str, title: str, border_style: str) -> None:
    """Print a bordered panel using the shared WOMM panel styling.

    Args:
        content: Body text of the panel.
        title: Panel title.
        border_style: Rich colour name; also drives the ``bright_`` body style.
    """
    panel = Panel(
        content,
        title=title,
        border_style=border_style,
        style=f"bright_{border_style}",
        padding=(1, 1),
        width=80,
    )
    ezconsole.print("")
    ezconsole.print(panel)
    ezconsole.print("")


# ///////////////////////////////////////////////////////////////
# DISPLAY FUNCTIONS
# ///////////////////////////////////////////////////////////////


def render_path_operation_result(
    result: PathOperationResult,
    context: str = "operation",
) -> None:
    """
    Render a PATH operation Result (add/remove/restore).

    Args:
        result: Outcome returned by ``SystemPathInterface.add_to_path()``,
            ``remove_from_path()``, or ``restore_backup()``.
        context: ``"restore"`` adds the restore-specific panel; any other
            value, including the default, renders lines only.
    """
    if result.success:
        if result.path_modified:
            ezprinter.success(result.message)
        else:
            ezprinter.info(result.message)

        if context == "restore":
            _show_panel(
                """PATH restored successfully from backup.

- Restart your terminal for the changes to take effect
- Use womm path backup list to list available backups
- Use womm path backup create to snapshot the restored PATH""",
                "Restore Complete",
                "green",
            )
        return

    ezprinter.error(result.message or "PATH operation failed")
    if result.error:
        ezprinter.info(result.error)

    if context == "restore":
        _show_panel(
            """The PATH could not be restored from the selected backup.

- Check that the backup file is readable and not corrupted
- Check permissions on the user environment variables
- Use womm path backup list to pick another backup""",
            "Troubleshooting",
            "yellow",
        )


def render_path_backup_result(result: PathBackupResult) -> None:
    """
    Render a PATH backup creation Result.

    Args:
        result: Outcome returned by ``SystemPathInterface.create_backup()``.
    """
    if result.success:
        ezprinter.success("PATH backup (JSON) created successfully!")
        ezprinter.system(f"Backup location: {result.backup_location}")
        if result.backup_file:
            ezprinter.system(f"Backup file: {Path(result.backup_file).name}")

        file_name = Path(result.backup_file).name if result.backup_file else "unknown"
        _show_panel(
            f"""PATH backup created successfully.

- Location: {result.backup_location}
- File: {file_name}
- Use womm path backup restore to restore this backup later
- Use womm path backup list to list every available backup""",
            "Backup Information",
            "yellow",
        )
        return

    ezprinter.error(result.message or "PATH backup failed")
    if result.error:
        ezprinter.info(result.error)

    _show_panel(
        """The PATH backup could not be created.

- Check write permissions on the backup directory
- Check available disk space
- Use womm path backup list to inspect the backup location""",
        "Troubleshooting",
        "yellow",
    )


def render_path_backup_list_result(result: PathBackupListResult) -> None:
    """
    Render a PATH backup list Result.

    Args:
        result: Outcome returned by ``SystemPathInterface.list_backups()``.
    """
    if not result.success:
        ezprinter.error(result.message or "Failed to retrieve PATH backups")
        if result.error:
            ezprinter.info(result.error)

        _show_panel(
            """The PATH backup list could not be retrieved.

- Check that the backup directory exists and is readable
- Check permissions on the WOMM data directory
- Use womm path backup create to create a first backup""",
            "Troubleshooting",
            "yellow",
        )
        return

    ezprinter.system(f"Backup location: {result.backup_location}")
    ezprinter.success("PATH backup information retrieved successfully!")

    if not result.backups:
        ezpl_bridge.console.print("")
        ezprinter.system("No backup files found")

        _show_panel(
            """No PATH backup has been created yet.

- Use womm path backup create to create your first backup
- Backups are stored in the WOMM data directory
- Use womm path backup restore to restore one once it exists""",
            "Getting Started",
            "blue",
        )
        return

    ezpl_bridge.console.print("")
    backup_table = ezprinter.create_backup_table(
        [
            {
                "name": backup.name,
                "size": backup.size,
                "modified": backup.modified,
                "description": f"{backup.path_entries} PATH entries",
            }
            for backup in result.backups
        ]
    )
    ezpl_bridge.console.print(backup_table)

    _show_panel(
        """PATH backup management commands:

- womm path list - Show the entries of your current PATH
- womm path backup create - Create a new PATH backup
- womm path backup list - List available PATH backups
- womm path backup show <name> - Inspect a backup's content
- womm path backup restore - Restore PATH from a backup""",
        "PATH Commands",
        "blue",
    )


def render_path_entries_result(result: PathOperationResult) -> None:
    """
    Render the entries of the current PATH.

    Args:
        result: Outcome returned by ``SystemPathInterface.list_path_entries()``.
    """
    if not result.success:
        ezprinter.error(result.message or "Failed to read the current PATH")
        if result.error:
            ezprinter.info(result.error)

        _show_panel(
            """The current PATH could not be read.

- Check permissions on the user environment variables
- Use womm path backup list to inspect available backups""",
            "Troubleshooting",
            "yellow",
        )
        return

    entries = result.path_entries or []
    ezprinter.success(f"{len(entries)} entries in PATH")

    if not entries:
        ezpl_bridge.console.print("")
        ezprinter.system("PATH is empty")
    else:
        table = ezprinter.create_table(
            title="Current PATH",
            columns=[
                ("#", "cyan", True),
                ("Entry", "green", False),
                ("Exists", "yellow", True),
            ],
        )
        for index, entry in enumerate(entries, 1):
            table.add_row(str(index), entry, "yes" if Path(entry).exists() else "no")
        ezpl_bridge.console.print("")
        ezpl_bridge.console.print(table)

    _show_panel(
        """PATH management commands:

- womm path backup create - Snapshot the current PATH
- womm path backup list - List available PATH backups
- womm path backup show <name> - Inspect a backup's content""",
        "PATH Commands",
        "blue",
    )


def render_path_backup_content_result(result: PathBackupContentResult) -> None:
    """
    Render the content of a single PATH backup.

    Args:
        result: Outcome returned by ``SystemPathInterface.read_backup()``.
    """
    if not result.success:
        ezprinter.error(result.message or "Failed to read the backup")
        if result.error:
            ezprinter.info(result.error)

        _show_panel(
            """The requested backup could not be read.

- Use womm path backup list to see the available backup names
- Pass the file name only, not a path
- The backup file may be corrupted""",
            "Troubleshooting",
            "yellow",
        )
        return

    entries = result.entries or []
    ezprinter.success(f"Backup {result.name} contains {len(entries)} entries")
    ezprinter.system(f"Created: {result.timestamp}")
    ezprinter.system(f"Platform: {result.platform}")
    ezprinter.system(f"PATH length: {result.length} chars")

    if entries:
        table = ezprinter.create_table(
            title=f"Entries in {result.name}",
            columns=[
                ("#", "cyan", True),
                ("Entry", "green", False),
            ],
        )
        for index, entry in enumerate(entries, 1):
            table.add_row(str(index), entry)
        ezpl_bridge.console.print("")
        ezpl_bridge.console.print(table)

    _show_panel(
        """Backup inspection commands:

- womm path backup restore - Restore your PATH from a backup
- womm path backup list - List available PATH backups
- womm path list - Compare against your current PATH""",
        "Backup Content",
        "blue",
    )


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "render_path_backup_content_result",
    "render_path_backup_list_result",
    "render_path_backup_result",
    "render_path_entries_result",
    "render_path_operation_result",
]
