#!/usr/bin/env python3
"""
Interactive UI components for Works On My Machine.
Provides interactive menus and dialogs using Rich and keyboard libraries.
"""

# IMPORTS
########################################################
# Standard library imports
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

# Third-party imports
# (None for this file)

# Local imports
# (None for this file)


# MAIN CLASS
########################################################
# Core interactive menu functionality


class InteractiveMenu:
    """Interactive menu with checkbox selection using Rich and keyboard."""

    def __init__(self, title: str = "Menu", border_style: str = "cyan"):
        """Initialize the interactive menu.

        Args:
            title: Menu title
            border_style: Rich border style
        """
        self.title = title
        self.border_style = border_style

    # PUBLIC METHODS
    ########################################################
    # Main interface methods for interactive menus

    def select_from_list(
        self,
        items: List[Dict[str, Any]],
        display_func: Optional[Callable[[Dict[str, Any]], str]] = None,
        default_index: int = 0,
        width: int = 80,
    ) -> Optional[Dict[str, Any]]:
        """Display an interactive menu and return the selected item.

        Args:
            items: List of items to display
            display_func: Function to format each item for display
            default_index: Default selected index

        Returns:
            Selected item or None if cancelled
        """
        try:
            import keyboard
            from rich.live import Live
            from rich.panel import Panel
            from rich.text import Text
        except ImportError:
            # Fallback to simple input-based selection
            return self._select_from_list_fallback(items, display_func, default_index)

        if not items:
            return None

        selected_idx = default_index

        def create_menu():
            menu_text = Text()
            for i, item in enumerate(items):
                checkbox = "☒" if i == selected_idx else "☐"

                display_text = display_func(item) if display_func else str(item)

                if i == selected_idx:
                    menu_text.append(f"{checkbox} ", style="bold cyan")
                    menu_text.append(display_text, style="bold white")
                else:
                    menu_text.append(f"{checkbox} ", style="dim")
                    menu_text.append(display_text, style="dim")
                menu_text.append("\n")

            menu_text.append(
                "\nUse ↑/↓ arrows to navigate, Enter to select, Ctrl+C to cancel",
                style="dim",
            )
            return Panel(
                menu_text,
                title=self.title,
                border_style=self.border_style,
                width=width,
            )

        with Live(create_menu(), refresh_per_second=10) as live:
            while True:
                try:
                    event = keyboard.read_event(suppress=False)

                    if event.event_type == keyboard.KEY_DOWN:
                        if event.name == "up":
                            selected_idx = (selected_idx - 1) % len(items)
                            live.update(create_menu())
                        elif event.name == "down":
                            selected_idx = (selected_idx + 1) % len(items)
                            live.update(create_menu())
                        elif event.name == "enter":
                            # Clean up keyboard before returning
                            keyboard.unhook_all()
                            return items[selected_idx]
                        elif event.name == "c" and event.modifiers:
                            # Clean up keyboard before returning
                            keyboard.unhook_all()
                            return None
                except KeyboardInterrupt:
                    # Clean up keyboard before returning
                    keyboard.unhook_all()
                    return None
                except Exception as e:
                    # Ensure keyboard is released in case of any error
                    keyboard.unhook_all()
                    raise e

    def confirm_action(
        self, message: str = "Confirm action", default_yes: bool = True
    ) -> bool:
        """Display a confirmation dialog.

        Args:
            message: Confirmation message
            default_yes: Whether "Yes" should be the default selection

        Returns:
            True if confirmed, False if cancelled or denied
        """
        try:
            import keyboard
            from rich.live import Live
            from rich.panel import Panel
            from rich.text import Text
        except ImportError:
            # Fallback to simple input-based confirmation
            return self._confirm_action_fallback(message, default_yes)

        options = ["Yes, proceed", "No, cancel"]
        confirm_selection = 0 if default_yes else 1

        def create_confirm_menu():
            menu_text = Text()
            for i, option in enumerate(options):
                checkbox = "☒" if i == confirm_selection else "☐"

                if i == confirm_selection:
                    menu_text.append(f"{checkbox} ", style="bold cyan")
                    menu_text.append(option, style="bold white")
                else:
                    menu_text.append(f"{checkbox} ", style="dim")
                    menu_text.append(option, style="dim")
                menu_text.append("\n")

            menu_text.append(
                "\nUse ↑/↓ arrows to navigate, Enter to select, Ctrl+C to cancel",
                style="dim",
            )
            return Panel(menu_text, title=message, border_style="yellow")

        with Live(create_confirm_menu(), refresh_per_second=10) as live:
            while True:
                try:
                    event = keyboard.read_event(suppress=False)

                    if event.event_type == keyboard.KEY_DOWN:
                        if event.name == "up":
                            confirm_selection = (confirm_selection - 1) % 2
                            live.update(create_confirm_menu())
                        elif event.name == "down":
                            confirm_selection = (confirm_selection + 1) % 2
                            live.update(create_confirm_menu())
                        elif event.name == "enter":
                            # Clean up keyboard before returning
                            keyboard.unhook_all()
                            return confirm_selection == 0
                        elif event.name == "c" and event.modifiers:
                            # Clean up keyboard before returning
                            keyboard.unhook_all()
                            return False
                except KeyboardInterrupt:
                    # Clean up keyboard before returning
                    keyboard.unhook_all()
                    return False
                except Exception as e:
                    # Ensure keyboard is released in case of any error
                    keyboard.unhook_all()
                    raise e

    # PRIVATE METHODS
    ########################################################
    # Internal fallback methods for when dependencies are not available

    def _select_from_list_fallback(
        self,
        items: List[Dict[str, Any]],
        display_func: Optional[Callable[[Dict[str, Any]], str]] = None,
        default_index: int = 0,  # noqa: ARG002
    ) -> Optional[Dict[str, Any]]:
        """Fallback method using simple input for selection."""
        if not items:
            return None

        print(f"\n{self.title}")
        print("=" * len(self.title))

        for i, item in enumerate(items):
            display_text = display_func(item) if display_func else str(item)
            print(f"{i + 1}. {display_text}")

        while True:
            try:
                choice = input(
                    f"\nSelect an option (1-{len(items)}) or 'q' to quit: "
                ).strip()
                if choice.lower() == "q":
                    return None

                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(items):
                    return items[choice_idx]
                else:
                    print(f"Please enter a number between 1 and {len(items)}")
            except ValueError:
                print("Please enter a valid number or 'q' to quit")
            except KeyboardInterrupt:
                return None

    def _confirm_action_fallback(
        self, message: str = "Confirm action", default_yes: bool = True
    ) -> bool:
        """Fallback method using simple input for confirmation."""
        default_text = "Y/n" if default_yes else "y/N"
        while True:
            try:
                choice = input(f"{message} [{default_text}]: ").strip().lower()
                if not choice:
                    return default_yes
                elif choice in ["y", "yes"]:
                    return True
                elif choice in ["n", "no"]:
                    return False
                else:
                    print("Please enter 'y' for yes or 'n' for no")
            except KeyboardInterrupt:
                return False


# UTILITY FUNCTIONS
########################################################
# Helper functions for formatting and display


def format_backup_item(backup_info: Dict[str, Any]) -> str:
    """Format a backup item for display in the menu.

    Args:
        backup_info: Backup information dictionary

    Returns:
        Formatted string for display
    """
    file_info = f"{backup_info['file'].name} ({backup_info['path_entries']} entries)"
    date_info = datetime.fromtimestamp(backup_info["file"].stat().st_mtime).strftime(
        "%Y-%m-%d %H:%M"
    )
    return f"{file_info} - {date_info}"
