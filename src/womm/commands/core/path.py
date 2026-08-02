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
from ezpl import LogLevel

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
# CONSTANTS
# ///////////////////////////////////////////////////////////////

_CANCELLED = "Restoration cancelled"

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
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def path_list(verbose: bool) -> None:
    """📋 List the entries of your current PATH."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Current PATH")
    result = SystemPathInterface().list_path_entries()
    render_path_entries_result(result)
    if not result.success:
        sys.exit(1)


# ///////////////////////////////////////////////////////////////
# PATH MODIFICATION
# ///////////////////////////////////////////////////////////////


@path_group.command("add")
@click.help_option("-h", "--help")
@click.argument("directory", type=click.Path(path_type=Path))
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def path_add(directory: Path, verbose: bool) -> None:
    """➕ Add a directory to your PATH.

    DIRECTORY must exist and hold at least one executable. The current PATH
    is backed up before the change, so 'backup restore' undoes it.
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("PATH Entry Addition")
    result = SystemPathInterface().add_to_path(directory)
    render_path_operation_result(result, context="add")
    if not result.success:
        sys.exit(1)


@path_group.command("remove")
@click.help_option("-h", "--help")
@click.argument("directory", type=click.Path(path_type=Path))
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def path_remove(directory: Path, verbose: bool) -> None:
    """➖ Remove a directory from your PATH.

    DIRECTORY does not have to exist — dropping the entry of an uninstalled
    tool is the usual reason to run this. The current PATH is backed up
    before the change.
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("PATH Entry Removal")
    result = SystemPathInterface().remove_from_path(directory)
    render_path_operation_result(result, context="remove")
    if not result.success:
        sys.exit(1)


# ///////////////////////////////////////////////////////////////
# BACKUP MANAGEMENT
# ///////////////////////////////////////////////////////////////


@path_backup_group.command("create")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def path_backup_create(verbose: bool) -> None:
    """💾 Create a backup of your current PATH."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("PATH Backup Creation")
    result = SystemPathInterface().create_backup()
    render_path_backup_result(result)
    if not result.success:
        sys.exit(1)


@path_backup_group.command("list")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def path_backup_list(verbose: bool) -> None:
    """📋 List available PATH backups."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("PATH Backup List")
    result = SystemPathInterface().list_backups()
    render_path_backup_list_result(result)
    if not result.success:
        sys.exit(1)


@path_backup_group.command("show")
@click.help_option("-h", "--help")
@click.argument("name")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def path_backup_show(name: str, verbose: bool) -> None:
    """🔍 Show the content of a PATH backup (file name, not a path)."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("PATH Backup Content")
    result = SystemPathInterface().read_backup(name)
    render_path_backup_content_result(result)
    if not result.success:
        sys.exit(1)


@path_backup_group.command("restore")
@click.help_option("-h", "--help")
@click.argument("name", required=False)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def path_backup_restore(name: str | None, verbose: bool) -> None:
    """🔄 Restore your PATH from a backup.

    NAME is a bare backup file name, as listed by 'backup list'. Without
    NAME, a backup is chosen interactively.
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("PATH Restoration")
    manager = SystemPathInterface()
    if name:
        _restore_named_backup(manager, name)
    else:
        _run_path_restore(manager)


# ///////////////////////////////////////////////////////////////
# RESTORE
# ///////////////////////////////////////////////////////////////


def _confirm_restore() -> bool:
    """Ask for an explicit confirmation before writing the user's PATH."""
    confirm_menu = InteractiveMenu(title="Confirm Restoration", border_style="yellow")
    return confirm_menu.confirm_action("Proceed with restoration?", default_yes=True)


def _restore_named_backup(manager: SystemPathInterface, name: str) -> None:
    """Restore the PATH from an explicitly named backup.

    The name stays bare on the whole path: ``read_backup()`` and
    ``restore_backup()`` each confine it inside the backup directory, and
    the readability check runs first so an unusable name stops before the
    confirmation prompt.
    """
    content = manager.read_backup(name)
    if not content.success:
        render_path_backup_content_result(content)
        ezprinter.info("Run 'womm path backup list' to see available names")
        sys.exit(1)

    ezprinter.info(f"Backup: {name} ({len(content.entries or [])} PATH entries)")

    if not _confirm_restore():
        ezprinter.system(_CANCELLED)
        return

    restore_result = manager.restore_backup(name)
    render_path_operation_result(restore_result, context="restore")
    if not restore_result.success:
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

    # The menu carries the bare name, not the path: restore_backup() confines
    # the name inside the backup directory itself.
    menu_items = [
        {
            "file": Path(backup.path),
            "name": backup.name,
            "path_entries": backup.path_entries,
        }
        for backup in backups
    ]
    menu = InteractiveMenu(title="Select Backup to Restore", border_style="cyan")
    selected = menu.select_from_list(menu_items, display_func=format_backup_item)
    if selected is None:
        ezprinter.system(_CANCELLED)
        return

    if not _confirm_restore():
        ezprinter.system(_CANCELLED)
        return

    restore_result = manager.restore_backup(selected["name"])
    render_path_operation_result(restore_result, context="restore")
    if not restore_result.success:
        sys.exit(1)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["path_group"]
