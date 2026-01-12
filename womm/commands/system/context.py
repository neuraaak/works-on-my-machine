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
import traceback
from datetime import datetime
from pathlib import Path

# Third-party imports
import click
from ezpl.types import LogLevel

# Local imports
from ...interfaces import ContextMenuInterface
from ...services import ContextParametersService
from ...ui.common import ezpl_bridge, ezprinter
from ...ui.context import ContextMenuUI, ContextMenuWizard

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

    # Initialize manager
    manager = ContextMenuInterface()
    ui = ContextMenuUI()

    if not manager.is_windows():
        ezprinter.info("Context menu management is Windows-specific")
        ezprinter.info("Consider using symbolic links or aliases on Unix systems")
        return

    # Handle interactive mode
    if interactive:
        target_path, label, icon, context_params = ContextMenuWizard.run_setup()
        if not target_path:  # User cancelled
            return
    else:
        # Validate required parameters in non-interactive mode
        if not target_path:
            ezprinter.error("Missing required option: --target")
            ezprinter.info("Use --interactive for guided setup")
            return
        if not label:
            ezprinter.error("Missing required option: --label")
            ezprinter.info("Use --interactive for guided setup")
            return

    # Create context parameters from flags
    context_params = ContextParametersService.from_flags(
        root=root,
        file=file,
        files=files,
        background=background,
        file_types=list(file_types) if file_types else None,
        extensions=list(extensions) if extensions else None,
    )

    # TODO: Migrate verbose output to interface method (display_registration_params)
    if verbose:
        ezprinter.info(f"Target: {target_path}")
        ezprinter.info(f"Label: {label}")
        ezprinter.info(f"Icon: {icon}")
        ezprinter.info(f"Context: {context_params.get_description()}")

    # TODO: Migrate entire registration flow to interface method
    # (register_with_backup) that handles backup + registration + UI display
    backup_dir = manager.get_backup_directory()
    backup_file = str(backup_dir / "context_menu_backup_before_register.json")

    with ezprinter.create_spinner_with_status(
        "Creating backup before registration..."
    ) as (
        progress,
        task,
    ):
        progress.update(task, status="Creating backup...")
        backup_result = manager.backup_entries(backup_file)

    if not backup_result["success"]:
        ezprinter.error(f"Backup failed: {backup_result['error']}")
        return

    if verbose:
        ezprinter.info(f"Backup created: {backup_file}")

    with ezprinter.create_spinner_with_status(
        "Registering script in context menu..."
    ) as (
        progress,
        task,
    ):
        progress.update(task, status="Adding registry entries...")
        result = manager.register_script(target_path, label, icon, context_params)

    # TODO: Migrate result handling to UI module (show_register_result)
    if result["success"]:
        info = result["info"]
        ui.show_register_success(label, info["registry_key"])
    else:
        ezprinter.error(f"Registration failed: {result['error']}")
        if verbose and "info" in result:
            info = result["info"]
            ezprinter.info(f"Script path: {info.get('script_path')}")
            ezprinter.info(f"Script type: {info.get('script_type')}")
            ezprinter.info(f"Registry key: {info.get('registry_key')}")


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

    # Initialize manager
    manager = ContextMenuInterface()

    if not manager.is_windows():
        ezprinter.info("Context menu management is Windows-specific")
        return

    # TODO: Migrate verbose output to interface
    if verbose:
        ezprinter.info(f"Removing key: {remove_key}")

    # TODO: Migrate unregistration flow to interface method that handles
    # spinner + unregister + UI display
    with ezprinter.create_spinner_with_status(
        "Unregistering script from context menu..."
    ) as (
        progress,
        task,
    ):
        progress.update(task, status="Removing registry entries...")
        result = manager.unregister_script(remove_key)

    # TODO: Migrate result handling to UI module (show_unregister_result)
    if result["success"]:
        ui = ContextMenuUI()
        ui.show_unregister_success(remove_key)
    else:
        ezprinter.error(f"Unregistration failed: {result['error']}")


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

    # Initialize manager and UI
    manager = ContextMenuInterface()
    ui = ContextMenuUI()

    if not manager.is_windows():
        ezprinter.info("Context menu management is Windows-specific")
        return

    # List entries
    with ezprinter.create_spinner_with_status("Retrieving context menu entries...") as (
        progress,
        task,
    ):
        progress.update(task, status="Reading registry entries...")
        result = manager.list_entries()

    if result["success"]:
        # Display entries via UI
        ui.show_context_entries(result["entries"])
        ui.show_list_commands()
    else:
        ezprinter.error(f"Failed to retrieve context menu entries: {result['error']}")


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

    # Initialize manager and UI
    manager = ContextMenuInterface()
    ui = ContextMenuUI()

    if not manager.is_windows():
        ezprinter.info("Context menu management is Windows-specific")
        return

    # Get context menu entries
    with ezprinter.create_spinner_with_status(
        "Checking context menu registration status..."
    ) as (
        progress,
        task,
    ):
        progress.update(task, status="Retrieving context menu entries...")
        result = manager.list_entries()

    if result["success"]:
        entries = result["entries"]
        total_entries = sum(
            len(entries.get(context_type, []))
            for context_type in ["directory", "background"]
        )

        ezprinter.success(f"Found {total_entries} context menu entries")

        info_content = """Context menu status information:

• Entries with descriptions are managed by external tools
• Entries without descriptions are system defaults or unmanaged
• All entries are shown for both folder and background context menus
• Backup files are stored in your WOMM installation directory"""

        ui.show_tip_panel(info_content, "Status Information")

    else:
        ezprinter.error("Failed to retrieve context menu status")

        troubleshoot_content = """Troubleshooting context menu issues:

• Ensure you have administrator privileges
• Check if Windows Registry access is blocked
• Try running from an elevated command prompt
• Verify WOMM installation is complete"""

        ui.show_tip_panel(troubleshoot_content, "Troubleshooting")


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

    # Initialize manager
    manager = ContextMenuInterface()

    if not manager.is_windows():
        ezprinter.info("Context menu management is Windows-specific")
        return

    # Common WOMM tools to register
    tools = [
        {
            "target": "womm.py",
            "label": "WOMM CLI",
            "description": "Main WOMM command-line interface",
        },
        # Add more tools as needed
    ]

    success_count = 0
    total_tools = len(tools)

    with ezprinter.create_spinner_with_status("Setting up common WOMM tools...") as (
        progress,
        task,
    ):
        for i, tool in enumerate(tools, 1):
            progress.update(
                task, status=f"Registering {tool['description']} ({i}/{total_tools})..."
            )
            if verbose:
                ezprinter.info(f"Registering: {tool['description']}")

            # Register using ContextMenuManager
            result = manager.register_script(tool["target"], tool["label"], "auto")

            if result["success"]:
                success_count += 1
                if verbose:
                    ezprinter.success(f"Registered: {tool['label']}")
            elif verbose:
                ezprinter.error(
                    f"Failed to register: {tool['label']} - {result['error']}"
                )

    if success_count == total_tools:
        ezprinter.success(f"All {total_tools} WOMM tools registered successfully!")
        ezprinter.info("Right-click in any folder to access WOMM tools")
    else:
        ezprinter.info(f"Registered {success_count}/{total_tools} tools successfully")


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

    # Initialize manager
    manager = ContextMenuInterface()

    if not manager.is_windows():
        ezprinter.info("Context menu management is Windows-specific")
        return

    # Determine backup file path
    if output:
        backup_file = output
        ezprinter.info(f"Backup location: {backup_file}")
    else:
        backup_dir = manager.get_backup_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = str(backup_dir / f"context_menu_backup_{timestamp}.json")
        ezprinter.info(f"Backup location: {backup_file}")

    # Create backup
    with ezprinter.create_spinner_with_status("Creating context menu backup...") as (
        progress,
        task,
    ):
        progress.update(task, status="Reading registry entries...")
        result = manager.backup_entries(backup_file)

    if result["success"]:
        # Show success message
        ui = ContextMenuUI()
        ui.show_backup_success(backup_file, result["entry_count"])
    else:
        ezprinter.error(f"Backup failed: {result['error']}")


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

    # Initialize manager and UI
    manager = ContextMenuInterface()
    ui = ContextMenuUI()

    if not manager.is_windows():
        ezprinter.info("Context menu management is Windows-specific")
        return

    backup_dir = manager.get_backup_directory()

    # If specific backup file provided, use it
    if backup_file:
        backup_path = Path(backup_file)
        if not backup_path.exists():
            ezprinter.error(f"Backup file not found: {backup_file}")
            return
        selected_file = backup_path
    else:
        # Interactive selection from available backups
        selected_file = ui.show_backup_selection_menu(backup_dir, verbose)
        if selected_file is None:
            return

    # Confirm restore operation
    if not ui.confirm_restore_operation(selected_file):
        ezprinter.info("Restore cancelled")
        return

    # Execute restore
    with ezprinter.create_spinner_with_status(
        "Restoring context menu from backup..."
    ) as (
        progress,
        task,
    ):
        progress.update(task, status="Restoring from backup...")
        result = manager.restore_entries(str(selected_file))

    if result["success"]:
        ui.show_restore_success(selected_file, result["entry_count"])
    else:
        ezprinter.error(f"Restore failed: {result['error']}")


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

    # Initialize manager and UI
    manager = ContextMenuInterface()
    ui = ContextMenuUI()

    if not manager.is_windows():
        ezprinter.info("Context menu management is Windows-specific")
        return

    try:
        backup_dir = manager.get_backup_directory()
        if not backup_dir.exists():
            ezprinter.error("No backup directory found")
            ezprinter.info("Create a backup first using 'womm context backup'")
            return

        # Collect entries from backups via interface
        with ezprinter.create_spinner_with_status("Scanning backup files...") as (
            progress,
            task,
        ):
            progress.update(task, status="Collecting context menu entries...")
            all_entries = manager.collect_entries_from_backups()

        if not all_entries:
            ezprinter.error("No context menu entries found in backups")
            return

        # Get current entries and filter available
        current_keys = manager.get_current_entry_keys()
        available_entries = manager.filter_available_entries(all_entries, current_keys)

        if not available_entries:
            ezprinter.info(
                "All context menu entries from backups are already installed"
            )
            return

        # Show selection menu via UI
        selected_entries = ui.show_cherry_pick_menu(available_entries)
        if not selected_entries:
            ezprinter.info("Cherry-pick cancelled")
            return

        # Apply selected entries via interface
        with ezprinter.create_spinner_with_status(
            f"Applying {len(selected_entries)} selected entries..."
        ) as (progress, task):
            results = manager.apply_cherry_picked_entries(selected_entries)

        # Show results
        success_count = sum(1 for success in results.values() if success)
        ui.show_cherry_pick_complete(success_count)

    except Exception as e:
        ezprinter.error(f"Cherry-pick failed: {e}")
        if verbose:
            traceback.print_exc()
