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

# Third-party imports
import click
from ezpl.types import LogLevel

# Local imports
from ...interfaces import ContextMenuInterface
from ...ui.common import ezpl_bridge, ezprinter

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# COMMAND GROUPS
# ///////////////////////////////////////////////////////////////


@click.group(invoke_without_command=True)
@click.pass_context
def context_group(ctx: click.Context) -> None:
    """Windows context menu management."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


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

    # Print header
    ezprinter.print_header("Context Menu Registration")

    try:
        manager = ContextMenuInterface()
        manager.register_context_entry(
            target_path=target_path,
            label=label,
            icon=icon,
            root=root,
            file=file,
            files=files,
            background=background,
            file_types=file_types,
            extensions=extensions,
            interactive=interactive,
            verbose=verbose,
        )
    except Exception as e:
        logger.error(f"Failed to register context menu entry: {e}")
        ezprinter.error(f"Registration failed: {e}")
        raise click.Abort() from e


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

    # Print header
    ezprinter.print_header("Context Menu Unregistration")

    try:
        # Initialize manager
        manager = ContextMenuInterface()

        if not manager.is_windows():
            ezprinter.info("Context menu management is Windows-specific")
            return

        # Perform unregistration with UI display
        manager.unregister_with_display(remove_key, verbose)
    except Exception as e:
        logger.error(f"Failed to unregister context menu entry: {e}")
        ezprinter.error(f"Unregistration failed: {e}")
        raise click.Abort() from e


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

    # Print header
    ezprinter.print_header("Context Menu List")

    try:
        manager = ContextMenuInterface()
        manager.show_entries(verbose)
    except Exception as e:
        logger.error(f"Failed to list context menu entries: {e}")
        ezprinter.error(f"List failed: {e}")
        raise click.Abort() from e


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

    # Print header
    ezprinter.print_header("Context Menu Status")

    try:
        manager = ContextMenuInterface()
        manager.show_status(verbose)
    except Exception as e:
        logger.error(f"Failed to show context menu status: {e}")
        ezprinter.error(f"Status failed: {e}")
        raise click.Abort() from e


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

    # Print header
    ezprinter.print_header("Context Menu Quick Setup")

    try:
        manager = ContextMenuInterface()
        manager.quick_setup_tools(verbose)
    except Exception as e:
        logger.error(f"Failed to setup context menu tools: {e}")
        ezprinter.error(f"Quick setup failed: {e}")
        raise click.Abort() from e


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

    # Print header
    ezprinter.print_header("Context Menu Backup")

    try:
        manager = ContextMenuInterface()
        manager.backup_with_ui(output, verbose)
    except Exception as e:
        logger.error(f"Failed to backup context menu entries: {e}")
        ezprinter.error(f"Backup failed: {e}")
        raise click.Abort() from e


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

    # Print header
    ezprinter.print_header("Context Menu Restore")

    try:
        manager = ContextMenuInterface()
        manager.restore_with_ui(backup_file, verbose)
    except Exception as e:
        logger.error(f"Failed to restore context menu entries: {e}")
        ezprinter.error(f"Restore failed: {e}")
        raise click.Abort() from e


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

    # Print header
    ezprinter.print_header("Context Menu Cherry-Pick")

    try:
        manager = ContextMenuInterface()
        manager.cherry_pick_with_ui(verbose)
    except Exception as e:
        logger.error(f"Failed to cherry-pick context menu entries: {e}")
        ezprinter.error(f"Cherry-pick failed: {e}")
        raise click.Abort() from e
