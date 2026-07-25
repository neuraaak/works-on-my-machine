#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT - Context Menu UI Components
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Context menu UI components.

This module provides UI components for context menu operations,
including backup selection and restoration interfaces.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
from datetime import datetime
from pathlib import Path

# Third-party imports
from rich.panel import Panel

# Local imports
from ..common.ezpl_bridge import ezconsole, ezprinter
from ..common.prompts import confirm, prompt_choice

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class ContextMenuUI:
    """UI components for context menu operations."""

    @staticmethod
    def show_backup_selection_menu(
        backup_dir: Path,
        _verbose: bool = False,
    ) -> Path | None:
        """
        Show interactive menu for selecting a backup file to restore.

        Args:
            backup_dir: Directory containing backup files
            verbose: Enable verbose output

        Returns:
            Selected backup file path or None if cancelled
        """
        # Find all backup files
        backup_files = list(backup_dir.glob("context_menu_backup_*.json"))
        if not backup_files:
            ezprinter.error("No context menu backups found")
            ezprinter.info(f"Checked directory: {backup_dir}")
            return None

        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        ezprinter.info("Available context menu backups:")

        # Display backup options
        for i, file in enumerate(backup_files, 1):
            try:
                stat = file.stat()
                modified_date = datetime.fromtimestamp(stat.st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                size_kb = stat.st_size / 1024

                # Try to read backup info
                try:
                    with open(file, encoding="utf-8") as f:
                        data = json.load(f)
                    entry_count = len(data.get("entries", []))
                    info = f" ({entry_count} entries)"
                except Exception:
                    info = ""

                ezprinter.info(f"  {i}. {file.name}")
                ezprinter.info(f"     📅 {modified_date} | 📦 {size_kb:.1f} KB{info}")

            except Exception as e:
                ezprinter.debug(f"Error reading backup {file.name}: {e}")
                continue

        ezconsole.print("")

        # Create backup file choices
        backup_choices = []
        for file in backup_files:
            try:
                size_kb = file.stat().st_size / 1024
                modified_date = datetime.fromtimestamp(file.stat().st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                # Try to read entry count from backup
                info = ""
                try:
                    with open(file, encoding="utf-8") as f:
                        data = json.load(f)
                    entry_count = len(data.get("entries", []))
                    info = f" ({entry_count} entries)"
                except Exception:
                    info = ""

                choice_text = (
                    f"{file.name} - 📅 {modified_date} | 📦 {size_kb:.1f} KB{info}"
                )
                backup_choices.append(choice_text)

            except Exception as e:
                ezprinter.debug(f"Error reading backup {file.name}: {e}")
                continue

        # Show selection menu
        try:
            selected_choice = prompt_choice(
                "Choose a backup to restore:", backup_choices
            )

            # Find the corresponding file
            selected_index = backup_choices.index(selected_choice)
            selected_file = backup_files[selected_index]

            return selected_file

        except (KeyboardInterrupt, ValueError):
            ezprinter.info("📤 Restore cancelled")
            return None

    @staticmethod
    def confirm_restore_operation(backup_file: Path) -> bool:
        """
        Ask user to confirm the restore operation.

        Args:
            backup_file: Path to the backup file to restore

        Returns:
            True if user confirms, False otherwise
        """
        ezprinter.info(f"Selected backup: {backup_file.name}")

        # Show backup details
        try:
            with open(backup_file, encoding="utf-8") as f:
                data = json.load(f)

            entry_count = len(data.get("entries", []))
            timestamp = data.get("timestamp", "Unknown")

            # Format timestamp for display
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                formatted_time = timestamp

            details_panel = Panel(
                f"""Backup Details:
• File: {backup_file.name}
• Entries: {entry_count}
• Created: {formatted_time}
• Size: {backup_file.stat().st_size / 1024:.1f} KB""",
                title="Backup Information",
                border_style="blue",
                style="bright_blue",
                padding=(1, 1),
                width=60,
            )
            ezconsole.print("")
            ezconsole.print(details_panel)
            ezconsole.print("")

        except Exception as e:
            ezprinter.debug(f"Could not read backup details: {e}")

        # Ask for confirmation
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

        def format_entry(entry: dict) -> str:
            return entry.get("_display_name", entry.get("key_name", "Unknown"))

        selected = menu.select_multiple_from_list(
            available_entries, display_func=format_entry
        )

        return selected if selected else []


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["ContextMenuUI"]
