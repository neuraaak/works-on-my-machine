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

# Local imports
from ...shared.results import (
    PathBackupListResult,
    PathBackupResult,
    PathOperationResult,
)
from ..common import ezpl_bridge, ezprinter

# ///////////////////////////////////////////////////////////////
# DISPLAY FUNCTIONS
# ///////////////////////////////////////////////////////////////


def render_path_operation_result(result: PathOperationResult) -> None:
    """
    Render a PATH operation Result (add/remove/restore).

    Args:
        result: Outcome returned by ``SystemPathInterface.add_to_path()``,
            ``remove_from_path()``, or ``restore_backup()``.
    """
    if result.success:
        if result.path_modified:
            ezprinter.success(result.message)
        else:
            ezprinter.info(result.message)
        return

    ezprinter.error(result.message or "PATH operation failed")
    if result.error:
        ezprinter.info(result.error)


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
        return

    ezprinter.error(result.message or "PATH backup failed")
    if result.error:
        ezprinter.info(result.error)


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
        return

    ezprinter.system(f"Backup location: {result.backup_location}")
    ezprinter.success("PATH backup information retrieved successfully!")

    if not result.backups:
        ezpl_bridge.console.print("")
        ezprinter.system("No backup files found")
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


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "render_path_backup_list_result",
    "render_path_backup_result",
    "render_path_operation_result",
]
