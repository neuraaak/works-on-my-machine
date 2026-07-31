#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PATH - PATH Backup Commands
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""User-facing PATH backup and restore commands."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys
from pathlib import Path

# Third-party imports
import click

# Local imports
from ...interfaces import SystemPathInterface
from ...ui.common import (
    InteractiveMenu,
    ezpl_bridge,
    ezprinter,
    format_backup_item,
)
from ...ui.system import (
    render_path_backup_list_result,
    render_path_backup_result,
    render_path_operation_result,
)

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
def path_cmd(backup_flag: bool, restore_flag: bool, list_flag: bool) -> None:
    """🧭 PATH utilities: backup, restore, and list backups."""
    selected = sum(bool(value) for value in (backup_flag, restore_flag, list_flag))
    if selected > 1:
        ezprinter.error("Choose only one action among --backup, --restore, or --list")
        sys.exit(1)
    if selected == 0:
        list_flag = True

    try:
        manager = SystemPathInterface()

        if list_flag:
            ezprinter.print_header("W.O.M.M PATH Backup List")
            result = manager.list_backups()
            render_path_backup_list_result(result)
            if not result.success:
                sys.exit(1)
        elif backup_flag:
            ezprinter.print_header("W.O.M.M PATH Backup Creation")
            result = manager.create_backup()
            render_path_backup_result(result)
            if not result.success:
                sys.exit(1)
        elif restore_flag:
            ezprinter.print_header("W.O.M.M PATH Restoration")
            _run_path_restore(manager)
    except Exception as error:
        ezprinter.error(f"Unexpected PATH command error: {error}")
        sys.exit(1)


def _run_path_restore(manager: SystemPathInterface) -> None:
    """Interactively select a PATH backup and restore it."""
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
    for index, backup in enumerate(backups, 1):
        table.add_row(
            str(index),
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
    render_path_operation_result(restore_result, context="restore")
    if not restore_result.success:
        sys.exit(1)


__all__ = ["path_cmd"]
