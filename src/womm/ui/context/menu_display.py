#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT - Context Menu UI Components
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Context menu UI components.

Pure presentation: these components receive backup records that a command
has already read through the interface layer, and never touch the
filesystem themselves. The `interfaces` and `ui` layers are siblings and
must not import each other.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import re
from pathlib import Path
from typing import TYPE_CHECKING

# Third-party imports
from rich.panel import Panel

# Local imports
from ..common.ezpl_bridge import ezconsole, ezprinter
from ..common.prompts import confirm, prompt_choice

if TYPE_CHECKING:
    from ...shared.results import BackupFileInfo

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def _describe(backup: BackupFileInfo) -> str:
    """Build the one-line label of a backup, used both in the menu and the panel.

    Args:
        backup: Backup record as produced by the interface layer.

    Returns:
        Label of the form ``name - 📅 date | 📦 size KB (n entries)``.
    """
    modified = (
        backup.modified_time.strftime("%Y-%m-%d %H:%M:%S")
        if backup.modified_time
        else "unknown"
    )
    return (
        f"{backup.filename} - 📅 {modified} | "
        f"📦 {backup.size_kb:.1f} KB ({backup.entry_count} entries)"
    )


def format_entry_display(entry: dict) -> str:
    """
    Format a backup entry for display in a selection menu.

    Args:
        entry: Backup entry as read from a backup file

    Returns:
        Label of the form ``MUIVerb (exe) [key: key_name]``.
    """
    key_name = entry.get("key_name", "Unknown")
    properties = entry.get("properties", {})

    display_text = properties.get("MUIVerb") or properties.get("@", key_name)

    command = properties.get("Command", "")
    if command:
        exe_match = re.search(r'"([^"]*\.exe)"', command)
        if exe_match:
            exe_name = Path(exe_match.group(1)).name
            display_text = f"{display_text} ({exe_name})"

    return f"{display_text} [key: {key_name}]"


# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class ContextMenuUI:
    """UI components for context menu operations."""

    @staticmethod
    def show_backup_selection_menu(
        backups: list[BackupFileInfo],
    ) -> BackupFileInfo | None:
        """
        Show interactive menu for selecting a backup to restore.

        Args:
            backups: Backups to choose from, newest first, as produced by
                ``ContextMenuInterface.list_backups()``.

        Returns:
            Selected backup or None if the list is empty or the user
            cancelled.
        """
        if not backups:
            ezprinter.error("No context menu backups found")
            return None

        choices = [_describe(backup) for backup in backups]

        try:
            selected_choice = prompt_choice("Choose a backup to restore:", choices)
            return backups[choices.index(selected_choice)]
        except (KeyboardInterrupt, ValueError):
            ezprinter.info("Restore cancelled")
            return None

    @staticmethod
    def confirm_restore_operation(backup: BackupFileInfo) -> bool:
        """
        Ask user to confirm the restore operation.

        Args:
            backup: Backup about to be restored

        Returns:
            True if user confirms, False otherwise
        """
        modified = (
            backup.modified_time.strftime("%Y-%m-%d %H:%M:%S")
            if backup.modified_time
            else "unknown"
        )
        details_panel = Panel(
            f"""Backup Details:
• File: {backup.filename}
• Entries: {backup.entry_count}
• Created: {modified}
• Size: {backup.size_kb:.1f} KB""",
            title="Backup Information",
            border_style="blue",
            style="bright_blue",
            padding=(1, 1),
            width=60,
        )
        ezconsole.print("")
        ezconsole.print(details_panel)
        ezconsole.print("")

        return confirm(
            "This will overwrite current context menu entries. Proceed?", default=False
        )

    @staticmethod
    def show_cherry_pick_menu(available_entries: list[dict]) -> list[dict]:
        """
        Show interactive menu for selecting entries to install.

        Args:
            available_entries: List of available entries

        Returns:
            List of selected entries
        """
        from ..common import InteractiveMenu

        ezprinter.info("Select context menu entries to install:")

        menu = InteractiveMenu(
            title="Cherry-pick Context Menu Entries",
            instruction="Use space to select/deselect, enter to confirm, q to quit",
        )

        selected = menu.select_multiple_from_list(
            available_entries, display_func=format_entry_display
        )

        return selected if selected else []


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["ContextMenuUI", "format_entry_display"]
