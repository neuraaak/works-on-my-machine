#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PATH - PATH Inspection and Backup Commands
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""User-facing PATH inspection, backup and restore commands."""

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
    render_path_backup_content_result,
    render_path_backup_list_result,
    render_path_backup_result,
    render_path_entries_result,
    render_path_operation_result,
)

# ///////////////////////////////////////////////////////////////
# COMMAND GROUPS
# ///////////////////////////////////////////////////////////////


@click.group("path", invoke_without_command=True)
@click.help_option("-h", "--help")
@click.pass_context
def path_group(ctx: click.Context) -> None:
    """🧭 PATH utilities: inspect, back up and restore your PATH."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@path_group.group("backup")
@click.help_option("-h", "--help")
def path_backup_group() -> None:
    """💾 Manage PATH backups."""


# ///////////////////////////////////////////////////////////////
# PATH INSPECTION
# ///////////////////////////////////////////////////////////////


@path_group.command("list")
@click.help_option("-h", "--help")
def path_list() -> None:
    """📋 List the entries of your current PATH."""
    ezprinter.print_header("W.O.M.M Current PATH")
    result = SystemPathInterface().list_path_entries()
    render_path_entries_result(result)
    if not result.success:
        sys.exit(1)


# ///////////////////////////////////////////////////////////////
# BACKUP MANAGEMENT
# ///////////////////////////////////////////////////////////////


@path_backup_group.command("create")
@click.help_option("-h", "--help")
def path_backup_create() -> None:
    """💾 Create a backup of your current PATH."""
    ezprinter.print_header("W.O.M.M PATH Backup Creation")
    result = SystemPathInterface().create_backup()
    render_path_backup_result(result)
    if not result.success:
        sys.exit(1)


@path_backup_group.command("list")
@click.help_option("-h", "--help")
def path_backup_list() -> None:
    """📋 List available PATH backups."""
    ezprinter.print_header("W.O.M.M PATH Backup List")
    result = SystemPathInterface().list_backups()
    render_path_backup_list_result(result)
    if not result.success:
        sys.exit(1)


@path_backup_group.command("show")
@click.help_option("-h", "--help")
@click.argument("name")
def path_backup_show(name: str) -> None:
    """🔍 Show the content of a PATH backup (file name, not a path)."""
    ezprinter.print_header("W.O.M.M PATH Backup Content")
    result = SystemPathInterface().read_backup(name)
    render_path_backup_content_result(result)
    if not result.success:
        sys.exit(1)


@path_backup_group.command("restore")
@click.help_option("-h", "--help")
def path_backup_restore() -> None:
    """🔄 Restore your PATH from a backup."""
    ezprinter.print_header("W.O.M.M PATH Restoration")
    _run_path_restore(SystemPathInterface())


# ///////////////////////////////////////////////////////////////
# INTERACTIVE RESTORE
# ///////////////////////////////////////////////////////////////


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


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["path_group"]
