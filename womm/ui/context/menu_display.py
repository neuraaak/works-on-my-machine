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

from ..common.ezpl_bridge import ezconsole, ezprinter

# Local imports
from ..common.prompts import confirm, prompt_choice


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
    def show_restore_success(backup_file: Path, entry_count: int) -> None:
        """
        Show success message after restore operation.

        Args:
            backup_file: Path to the restored backup file
            entry_count: Number of entries restored
        """
        ezprinter.success("Context menu restored successfully!")
        ezprinter.info(f"Restored from: {backup_file.name}")

        # Show helpful tip panel
        tip_content = f"""Context menu restore completed successfully.

• Restored from: {backup_file.name}
• {entry_count} entries restored
• Changes should be visible immediately in File Explorer
• Use 'womm context list' to verify the restored entries"""

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

    @staticmethod
    def show_backup_success(backup_file: str, entry_count: int) -> None:
        """
        Show success message after backup operation.

        Args:
            backup_file: Path to the created backup file
            entry_count: Number of entries backed up
        """
        ezprinter.success("Backup completed successfully!")
        ezprinter.info(f"📄 Backup saved to: {backup_file}")
        ezprinter.info(f"📦 {entry_count} entries backed up")

        # Show helpful tip panel
        tip_content = f"""Context menu backup completed successfully.

• Backup file: {backup_file}
• {entry_count} entries backed up
• Use this backup to restore context menu entries if needed
• You can specify a custom backup location with --output"""

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

    @staticmethod
    def show_register_success(label: str, registry_key: str) -> None:
        """
        Show success message after registration operation.

        Args:
            label: Display label of the registered entry
            registry_key: Registry key name
        """
        ezprinter.success(f"Tool '{label}' registered successfully in context menu")
        ezprinter.info(f"Registry key: {registry_key}")

        # Show helpful tip panel
        tip_content = """Right-click in any folder to see your new context menu entry.

• The entry will appear in both folder and background context menus
• Use 'womm context list' to see all registered entries
• Use 'womm context unregister --remove <key>' to remove entries later"""

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

    @staticmethod
    def show_unregister_success(registry_key: str) -> None:
        """
        Show success message after unregistration operation.

        Args:
            registry_key: Registry key name that was removed
        """
        ezprinter.success(
            f"Entry '{registry_key}' removed successfully from context menu"
        )

        # Show helpful tip panel
        tip_content = """Context menu entry has been removed successfully.

• Changes will be visible after refreshing File Explorer
• Use 'womm context list' to verify the removal
• Use 'womm context register' to add new entries"""

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

    @staticmethod
    def show_list_commands() -> None:
        """Show helpful commands panel after listing entries."""
        tip_content = """Context menu management commands:

• womm context register --target <file> --label "<name>" - Add new entry
• womm context unregister --remove <key> - Remove existing entry
• womm context backup - Create backup of current entries
• womm context restore - Restore entries from backup"""

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

    @staticmethod
    def show_tip_panel(content: str, title: str = "Tip") -> None:
        """Show a tip panel with consistent formatting."""
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

    @staticmethod
    def show_cherry_pick_complete(entry_count: int) -> None:
        """Show success message after cherry-pick operation."""
        ezprinter.success(f"Cherry-pick completed! {entry_count} entries installed")

        tip_content = f"""Cherry-pick installation completed successfully.

• {entry_count} context menu entries installed
• Changes should be visible immediately in File Explorer
• Use 'womm context list' to verify the new entries
• If an entry doesn't work, check the original script path"""

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

    @staticmethod
    def show_context_entries(entries: dict) -> None:
        """
        Display context menu entries in formatted output.

        Args:
            entries: Dictionary of entries by context type
        """
        ezprinter.section("Context Menu Entries")

        for context_type in ["directory", "background"]:
            ezconsole.print(f"\n[bold]{context_type.upper()} CONTEXT:[/bold]")
            context_entries = entries.get(context_type, [])

            if not context_entries:
                ezconsole.print("  No entries found")
            else:
                for entry in context_entries:
                    ezconsole.print(f"  Key: {entry['key_name']}")
                    ezconsole.print(f"    Display: {entry['display_name']}")
                    if entry.get("command"):
                        ezconsole.print(f"    Command: {entry['command']}")
                    if entry.get("icon"):
                        ezconsole.print(f"    Icon: {entry['icon']}")
                    ezconsole.print()


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["ContextMenuUI"]
