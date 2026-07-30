#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONFLICT PROMPTS - Interactive conflict resolution
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Interactive resolution of file and directory conflicts.

This is the terminal-facing half of conflict handling: it asks the user what to
do and returns a ``ConflictAction``. The service layer applies that action and
never reaches for a terminal itself.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path

# Third-party imports
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Local imports
from ....shared.conflicts import ConflictAction
from ...common.prompts import confirm

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# INTERACTIVE CONFLICT RESOLVER
# ///////////////////////////////////////////////////////////////


class InteractiveConflictResolver:
    """Asks the user how to resolve a conflict.

    Satisfies the ``ConflictResolver`` protocol, so it can be handed to
    ``ConflictResolutionService`` by the command layer.
    """

    def __init__(self, console: Console | None = None) -> None:
        """Initialize the resolver.

        Args:
            console: Console used for output; a default one is created if omitted
        """
        self.console = console or Console()

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def resolve_file(self, target_file: Path, context: str) -> ConflictAction:
        """Ask what to do about an existing file.

        Args:
            target_file: Target file that already exists
            context: Context description

        Returns:
            ConflictAction: User's choice; SKIP if the prompt cannot be shown
        """
        try:
            self.console.print(
                Panel(
                    f"[yellow]⚠️  Conflict detected![/yellow]\n\n"
                    f"File already exists: [cyan]{target_file}[/cyan]\n"
                    f"Context: {context}",
                    title="File Conflict",
                    border_style="yellow",
                )
            )

            overwrite = confirm(
                f"Overwrite existing file [cyan]{target_file.name}[/cyan]?",
                default=False,
            )
            if overwrite:
                return ConflictAction.OVERWRITE

            skip = confirm("Skip this file and continue?", default=True)
            return ConflictAction.SKIP if skip else ConflictAction.CANCEL

        except KeyboardInterrupt:
            return ConflictAction.CANCEL
        except Exception as e:
            logger.warning(f"Error prompting for file resolution: {e}")
            # Default to skip on error: never destroy an existing file
            return ConflictAction.SKIP

    def resolve_directory(self, target_dir: Path, context: str) -> ConflictAction:
        """Ask what to do about an existing directory.

        Args:
            target_dir: Target directory that already exists
            context: Context description

        Returns:
            ConflictAction: User's choice; MERGE if the prompt cannot be shown
        """
        try:
            self.console.print(
                Panel(
                    f"[yellow]⚠️  Conflict detected![/yellow]\n\n"
                    f"Directory already exists: [cyan]{target_dir}[/cyan]\n"
                    f"Context: {context}",
                    title="Directory Conflict",
                    border_style="yellow",
                )
            )

            self.console.print("\n[bold]Choose an action:[/bold]")
            self.console.print("1. [green]Merge[/green] - Add new files, keep existing")
            self.console.print(
                "2. [yellow]Overwrite[/yellow] - Replace entire directory"
            )
            self.console.print("3. [red]Skip[/red] - Don't copy this directory")
            self.console.print("4. [red]Cancel[/red] - Abort operation")

            return self._ask_directory_action()

        except KeyboardInterrupt:
            return ConflictAction.CANCEL
        except Exception as e:
            logger.warning(f"Error prompting for directory resolution: {e}")
            # Default to merge on error: never delete existing contents
            return ConflictAction.MERGE

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _ask_directory_action(self) -> ConflictAction:
        """Read the directory choice, re-asking on an unconfirmed overwrite.

        Returns:
            ConflictAction: The chosen action
        """
        while True:
            choice = Prompt.ask(
                "\nYour choice",
                choices=["1", "2", "3", "4"],
                default="1",
            )

            if choice == "1":
                return ConflictAction.MERGE
            if choice == "2":
                if confirm(
                    "[red]⚠️  This will delete all existing files in the "
                    "directory. Continue?[/red]",
                    default=False,
                ):
                    return ConflictAction.OVERWRITE
                continue
            if choice == "3":
                return ConflictAction.SKIP
            return ConflictAction.CANCEL


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "InteractiveConflictResolver",
]
