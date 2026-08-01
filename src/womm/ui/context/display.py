#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT DISPLAY - Context Result Display Functions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Context result display functions.

Provides display functions for context menu operation results.
These functions render Result objects to the console using rich.
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
    BackupDataResult,
    BackupFileListResult,
    ContextBackupResult,
    ContextCherryPickResult,
    ContextEntriesResult,
    ContextRestoreResult,
    ContextSetupResult,
    ContextStatusResult,
    ScriptRegistrationResult,
    ScriptUnregistrationResult,
)
from ..common.ezpl_bridge import ezconsole, ezprinter

# ///////////////////////////////////////////////////////////////
# SCRIPT REGISTRATION DISPLAY FUNCTIONS
# ///////////////////////////////////////////////////////////////


def render_script_registration_result(result: ScriptRegistrationResult) -> None:
    """Render a script registration result.

    Args:
        result: The ScriptRegistrationResult to render
    """
    if result.success:
        if result.dry_run:
            ezprinter.info("Dry run - no changes made")
            ezprinter.info(f"Would register: {result.label}")
        else:
            ezprinter.success(
                f"Tool '{result.label}' registered successfully in context menu"
            )

            tip_content = """Right-click in any folder to see your new context menu entry.

- The entry will appear in both folder and background context menus
- Use womm context list to see all registered entries
- Use womm context unregister --remove <key> to remove entries later"""

            tip_panel = Panel(
                tip_content,
                title="Context Menu Usage",
                border_style="green",
                style="bright_green",
                padding=(1, 1),
                width=80,
            )
            ezconsole.print("")
            ezconsole.print(tip_panel)
            ezconsole.print("")
    else:
        ezprinter.error(f"Registration failed: {result.error}")


# ///////////////////////////////////////////////////////////////
# SCRIPT UNREGISTRATION DISPLAY FUNCTIONS
# ///////////////////////////////////////////////////////////////


def render_script_unregistration_result(result: ScriptUnregistrationResult) -> None:
    """Render a script unregistration result.

    Args:
        result: The ScriptUnregistrationResult to render
    """
    if result.success:
        ezprinter.success(
            f"Entry '{result.key_name}' removed successfully from context menu"
        )

        tip_content = """Context menu entry has been removed successfully.

- Changes will be visible after refreshing File Explorer
- Use womm context list to verify the removal
- Use womm context register to add new entries"""

        tip_panel = Panel(
            tip_content,
            title="Unregistration Complete",
            border_style="green",
            style="bright_green",
            padding=(1, 1),
            width=80,
        )
        ezconsole.print("")
        ezconsole.print(tip_panel)
        ezconsole.print("")

        if result.permission_errors:
            for error in result.permission_errors:
                ezprinter.warning(f"Permission error: {error}")
    else:
        ezprinter.error(f"Unregistration failed: {result.error}")
        if result.permission_errors:
            for error in result.permission_errors:
                ezprinter.error(f"  Permission error: {error}")


# ///////////////////////////////////////////////////////////////
# BACKUP DISPLAY FUNCTIONS
# ///////////////////////////////////////////////////////////////


def render_context_backup_result(result: ContextBackupResult) -> None:
    """Render a context backup result.

    Args:
        result: The ContextBackupResult to render
    """
    if result.success:
        ezprinter.success("Backup completed successfully!")
        if result.backup_file:
            ezprinter.info(f"Backup saved to: {result.backup_file}")
        ezprinter.info(f"{result.entry_count} entries backed up")

        tip_content = f"""Context menu backup completed successfully.

- Backup file: {result.backup_file or "default location"}
- {result.entry_count} entries backed up
- Use this backup to restore context menu entries if needed
- You can specify a custom backup location with --output"""

        tip_panel = Panel(
            tip_content,
            title="Backup Information",
            border_style="yellow",
            style="bright_yellow",
            padding=(1, 1),
            width=80,
        )
        ezconsole.print("")
        ezconsole.print(tip_panel)
        ezconsole.print("")
    else:
        ezprinter.error(f"Backup failed: {result.error}")


# //://:obe/////////////////////////////
# RESTORE DISPLAY FUNCTIONS
# ///////////////////////////////////////////////////////////////


def render_context_restore_result(result: ContextRestoreResult) -> None:
    """Render a context restore result.

    Args:
        result: The ContextRestoreResult to render
    """
    if result.success:
        ezprinter.success("Context menu restored successfully!")
        if result.backup_file:
            ezprinter.info(f"Restored from: {result.backup_file}")

        tip_content = f"""Context menu restore completed successfully.

- Restored from: {result.backup_file or "default backup"}
- {result.entry_count} entries restored
- Changes should be visible immediately in File Explorer
- Use womm context list to verify the restored entries"""

        tip_panel = Panel(
            tip_content,
            title="Restore Complete",
            border_style="green",
            style="bright_green",
            padding=(1, 1),
            width=80,
        )
        ezconsole.print("")
        ezconsole.print(tip_panel)
        ezconsole.print("")
    else:
        ezprinter.error(f"Restore failed: {result.error}")


# //://:obe/////////////////////////////
# ENTRIES DISPLAY FUNCTIONS
# ///////////////////////////////////////////////////////////////


def render_context_entries_result(result: ContextEntriesResult) -> None:
    """Render a context entries result, summary first.

    Args:
        result: The ContextEntriesResult to render
    """
    if not result.success:
        ezprinter.error(f"Failed to retrieve context menu entries: {result.error}")
        return

    ezprinter.print_header("Context Menu Entries")

    ezconsole.print(f"[bold]Total: {result.total_entries}[/bold]")
    for context_type, count in result.entries_by_type.items():
        ezconsole.print(f"  {context_type}: {count}")

    entries = result.entries or {}
    for context_type in entries:
        ezconsole.print(f"\n[bold]{context_type.upper()} CONTEXT:[/bold]")
        context_entries = entries[context_type]

        if not context_entries:
            ezconsole.print("  No entries found")
            continue

        for entry in context_entries:
            ezconsole.print(f"  Key: {entry.get('key_name', 'Unknown')}")
            display_name = entry.get("display_name", entry.get("key_name", "Unknown"))
            ezconsole.print(f"    Display: {display_name}")
            if entry.get("command"):
                ezconsole.print(f"    Command: {entry['command']}")
            if entry.get("icon"):
                ezconsole.print(f"    Icon: {entry['icon']}")
            ezconsole.print("")

    show_list_commands()


# //://:obe
# STATUS DISPLAY FUNCTIONS
# ///////////////////////////////////////////////////////////////


def render_context_status_result(result: ContextStatusResult) -> None:
    """Render a context status result.

    Args:
        result: The ContextStatusResult to render
    """
    if result.success:
        ezprinter.success(f"Found {result.total_entries} context menu entries")

        info_content = """Context menu status information:

- Entries with descriptions are managed by external tools
- Entries without descriptions are system defaults or unmanaged
- All entries are shown for both folder and background context menus
- Backup files are stored in your WOMM installation directory"""

        show_tip_panel(info_content, "Status Information")
    else:
        ezprinter.error("Failed to retrieve context menu status")
        if result.error:
            ezprinter.info(f"Error: {result.error}")

        troubleshoot_content = """Troubleshooting context menu issues:

- Ensure you have administrator privileges
- Check if Windows Registry access is blocked
- Try running from an elevated command prompt
- Verify WOMM installation is complete"""

        show_tip_panel(troubleshoot_content, "Troubleshooting")


# ///////////////////////////////////////////////////////////////
# BACKUP LISTING AND CONTENT DISPLAY FUNCTIONS
# ///////////////////////////////////////////////////////////////


def render_context_backup_list_result(result: BackupFileListResult) -> None:
    """Render the list of available context menu backup files.

    Args:
        result: The BackupFileListResult to render
    """
    if not result.success:
        ezprinter.error(f"Failed to list backups: {result.error}")
        show_tip_panel(
            """Troubleshooting backup listing:

- Check that the backup directory exists and is readable
- Create a first backup with womm context backup create""",
            "Troubleshooting",
        )
        return

    backups = result.backups or []
    if not backups:
        ezprinter.info(f"No backups found in {result.backup_directory}")
        getting_started = Panel(
            """No context menu backup yet.

- womm context backup create - Create your first backup
- womm context list - See what would be backed up""",
            title="Getting Started",
            border_style="blue",
            style="bright_blue",
            padding=(1, 1),
            width=80,
        )
        ezconsole.print("")
        ezconsole.print(getting_started)
        ezconsole.print("")
        return

    ezprinter.success(f"Found {len(backups)} backup(s) in {result.backup_directory}")
    for backup in backups:
        modified = (
            backup.modified_time.strftime("%Y-%m-%d %H:%M:%S")
            if backup.modified_time
            else "unknown"
        )
        ezconsole.print(f"  {backup.filename}")
        ezconsole.print(
            f"    {modified} | {backup.size_kb:.1f} KB | {backup.entry_count} entries"
        )

    commands_panel = Panel(
        """Backup commands:

- womm context backup show <name> - Inspect a backup's content
- womm context backup restore <name> - Restore a backup
- womm context backup cherry-pick - Pick individual entries""",
        title="Backup Commands",
        border_style="blue",
        style="bright_blue",
        padding=(1, 1),
        width=80,
    )
    ezconsole.print("")
    ezconsole.print(commands_panel)
    ezconsole.print("")


def render_context_backup_content_result(result: BackupDataResult) -> None:
    """Render the content of a single context menu backup file.

    Args:
        result: The BackupDataResult to render
    """
    if not result.success:
        ezprinter.error(f"Could not read backup: {result.error}")
        show_tip_panel(
            """Troubleshooting backup reading:

- Backups are named, not path-addressed: pass a bare file name
- Run womm context backup list to see the available names""",
            "Troubleshooting",
        )
        return

    metadata = result.metadata or {}
    ezprinter.success(f"Backup: {Path(result.filepath).name}")
    ezconsole.print(f"  Created: {metadata.get('timestamp', 'unknown')}")
    ezconsole.print(f"  Version: {metadata.get('version', 'unknown')}")
    ezconsole.print(f"  Entries: {metadata.get('total_entries', 0)}")

    for context_type, stats in (result.entry_stats or {}).items():
        ezconsole.print(f"\n[bold]{context_type.upper()} CONTEXT:[/bold]")
        ezconsole.print(f"  Count: {stats.get('count', 0)}")
        for key in stats.get("sample_keys", []):
            ezconsole.print(f"    - {key}")

    restore_panel = Panel(
        f"""To restore this backup:

- womm context backup restore {Path(result.filepath).name}
- womm context backup cherry-pick - Pick individual entries instead""",
        title="Backup Content",
        border_style="blue",
        style="bright_blue",
        padding=(1, 1),
        width=80,
    )
    ezconsole.print("")
    ezconsole.print(restore_panel)
    ezconsole.print("")


# //://:obe
# SETUP DISPLAY FUNCTIONS
# ///////////////////////////////////////////////////////////////


def render_context_setup_result(result: ContextSetupResult) -> None:
    """Render a context setup result.

    Args:
        result: The ContextSetupResult to render
    """
    if result.success:
        ezprinter.success(
            f"All {result.total_tools} WOMM tools registered successfully!"
        )
        ezprinter.info("Right-click in any folder to access WOMM tools")
    else:
        ezprinter.info(
            f"Registered {result.success_count}/{result.total_tools} tools successfully"
        )
        if result.error:
            ezprinter.error(f"Setup error: {result.error}")


# //://:obe
# CHERRY-PICK DISPLAY FUNCTIONS
# ///////////////////////////////////////////////////////////////


def render_context_cherry_pick_result(result: ContextCherryPickResult) -> None:
    """Render a cherry-pick result.

    Args:
        result: The ContextCherryPickResult to render
    """
    if result.success:
        ezprinter.success(
            f"Cherry-pick completed! {result.success_count} entries installed"
        )

        tip_content = f"""Cherry-pick installation completed successfully.

- {result.success_count} context menu entries installed
- Changes should be visible immediately in File Explorer
- Use womm context list to verify the new entries
- If an entry does not work, check the original script path"""

        tip_panel = Panel(
            tip_content,
            title="Cherry-pick Complete",
            border_style="green",
            style="bright_green",
            padding=(1, 1),
            width=80,
        )
        ezconsole.print("")
        ezconsole.print(tip_panel)
        ezconsole.print("")
    else:
        ezprinter.error(f"Cherry-pick failed: {result.error}")


# //://:obe
# HELPER DISPLAY FUNCTIONS
# ///////////////////////////////////////////////////////////////


def show_list_commands() -> None:
    """Show helpful commands panel after listing entries."""
    tip_content = """Context menu management commands:

- womm context register --target <file> --label "<name>" - Add new entry
- womm context unregister --remove <key> - Remove existing entry
- womm context backup create - Create backup of current entries
- womm context backup list - List available backups
- womm context backup restore <name> - Restore entries from backup"""

    tip_panel = Panel(
        tip_content,
        title="Context Menu Commands",
        border_style="blue",
        style="bright_blue",
        padding=(1, 1),
        width=80,
    )
    ezconsole.print("")
    ezconsole.print(tip_panel)
    ezconsole.print("")


def show_tip_panel(content: str, title: str = "Tip") -> None:
    """Show a tip panel with consistent formatting.

    Args:
        content: The content to display in the panel
        title: The title of the panel
    """
    tip_panel = Panel(
        content,
        title=title,
        border_style="yellow",
        style="bright_yellow",
        padding=(1, 1),
        width=80,
    )
    ezconsole.print("")
    ezconsole.print(tip_panel)
    ezconsole.print("")


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "render_context_backup_content_result",
    "render_context_backup_list_result",
    "render_context_backup_result",
    "render_context_cherry_pick_result",
    "render_context_entries_result",
    "render_context_restore_result",
    "render_context_setup_result",
    "render_context_status_result",
    "render_script_registration_result",
    "render_script_unregistration_result",
    "show_list_commands",
    "show_tip_panel",
]
