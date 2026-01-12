#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONFLICT RESOLUTION SERVICE - File Conflict Resolution
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Conflict Resolution Service - Singleton service for handling file conflicts.

Handles conflicts when copying files during project creation:
- Detects existing files
- Prompts user for resolution (unless --force is used)
- Manages merge strategies for directories
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import shutil
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.project import ProjectServiceError
from ...ui.common.prompts import confirm

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# ENUMS
# ///////////////////////////////////////////////////////////////


class ConflictAction(str, Enum):
    """Actions available for conflict resolution."""

    OVERWRITE = "overwrite"
    SKIP = "skip"
    MERGE = "merge"
    CANCEL = "cancel"


# ///////////////////////////////////////////////////////////////
# CONFLICT RESOLUTION SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class ConflictResolutionService:
    """Singleton service for handling file conflicts during project creation."""

    _instance: ClassVar[ConflictResolutionService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> ConflictResolutionService:
        """Create or return the singleton instance.

        Returns:
            ConflictResolutionService: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize conflict resolution service (only once)."""
        if ConflictResolutionService._initialized:
            return

        self.logger = logging.getLogger(__name__)
        ConflictResolutionService._initialized = True

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def resolve_file_conflict(
        self,
        source_file: Path,
        target_file: Path,
        force: bool = False,
        context: str = "file",
    ) -> ConflictAction:
        """Resolve a file conflict.

        Args:
            source_file: Source file to copy
            target_file: Target file path (may already exist)
            force: If True, automatically overwrite without prompting
            context: Context description for the conflict (e.g., "config file")

        Returns:
            ConflictAction: Action to take (OVERWRITE, SKIP, or CANCEL)

        Raises:
            ProjectServiceError: If conflict resolution fails
        """
        try:
            # If target doesn't exist, no conflict
            if not target_file.exists():
                return ConflictAction.OVERWRITE

            # If force is enabled, overwrite without asking
            if force:
                self.logger.info(f"Force mode: overwriting {target_file}")
                return ConflictAction.OVERWRITE

            # Prompt user for resolution
            return self._prompt_file_resolution(target_file, context)

        except Exception as e:
            raise ProjectServiceError(
                message=f"Failed to resolve file conflict: {e}",
                operation="resolve_file_conflict",
                details=f"Source: {source_file}, Target: {target_file}",
            ) from e

    def resolve_directory_conflict(
        self,
        source_dir: Path,
        target_dir: Path,
        force: bool = False,
        context: str = "directory",
    ) -> ConflictAction:
        """Resolve a directory conflict.

        Args:
            source_dir: Source directory to copy
            target_dir: Target directory path (may already exist)
            force: If True, automatically overwrite without prompting
            context: Context description for the conflict (e.g., ".vscode")

        Returns:
            ConflictAction: Action to take (OVERWRITE, MERGE, SKIP, or CANCEL)

        Raises:
            ProjectServiceError: If conflict resolution fails
        """
        try:
            # If target doesn't exist, no conflict
            if not target_dir.exists():
                return ConflictAction.OVERWRITE

            # If force is enabled, merge (safer than overwrite for directories)
            if force:
                self.logger.info(f"Force mode: merging into {target_dir}")
                return ConflictAction.MERGE

            # Prompt user for resolution
            return self._prompt_directory_resolution(target_dir, context)

        except Exception as e:
            raise ProjectServiceError(
                message=f"Failed to resolve directory conflict: {e}",
                operation="resolve_directory_conflict",
                details=f"Source: {source_dir}, Target: {target_dir}",
            ) from e

    def copy_file_with_resolution(
        self,
        source_file: Path,
        target_file: Path,
        force: bool = False,
        context: str = "file",
    ) -> bool:
        """Copy a file with conflict resolution.

        Args:
            source_file: Source file to copy
            target_file: Target file path
            force: If True, automatically overwrite without prompting
            context: Context description for the conflict

        Returns:
            bool: True if file was copied, False if skipped or cancelled

        Raises:
            ProjectServiceError: If file copy fails
        """
        try:
            # Resolve conflict
            action = self.resolve_file_conflict(
                source_file, target_file, force, context
            )

            if action == ConflictAction.CANCEL:
                self.logger.warning("User cancelled file copy operation")
                return False

            if action == ConflictAction.SKIP:
                self.logger.info(f"Skipping {target_file} (user choice)")
                return False

            # Ensure target directory exists
            target_file.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(source_file, target_file)
            self.logger.info(f"Copied {source_file} to {target_file}")
            return True

        except Exception as e:
            raise ProjectServiceError(
                message=f"Failed to copy file with resolution: {e}",
                operation="copy_file_with_resolution",
                details=f"Source: {source_file}, Target: {target_file}",
            ) from e

    def copy_directory_with_resolution(
        self,
        source_dir: Path,
        target_dir: Path,
        force: bool = False,
        context: str = "directory",
    ) -> bool:
        """Copy a directory with conflict resolution.

        Args:
            source_dir: Source directory to copy
            target_dir: Target directory path
            force: If True, automatically merge without prompting
            context: Context description for the conflict

        Returns:
            bool: True if directory was copied, False if skipped or cancelled

        Raises:
            ProjectServiceError: If directory copy fails
        """
        try:
            # Resolve conflict
            action = self.resolve_directory_conflict(
                source_dir, target_dir, force, context
            )

            if action == ConflictAction.CANCEL:
                self.logger.warning("User cancelled directory copy operation")
                return False

            if action == ConflictAction.SKIP:
                self.logger.info(f"Skipping {target_dir} (user choice)")
                return False

            # Ensure target directory exists
            target_dir.mkdir(parents=True, exist_ok=True)

            # Copy directory contents
            if action == ConflictAction.OVERWRITE:
                # Remove existing directory and copy fresh
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                shutil.copytree(source_dir, target_dir)
            else:  # MERGE
                # Copy files, overwriting existing ones
                for item in source_dir.rglob("*"):
                    if item.is_file():
                        rel_path = item.relative_to(source_dir)
                        target_file = target_dir / rel_path
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, target_file)

            self.logger.info(f"Copied {source_dir} to {target_dir} (action: {action})")
            return True

        except Exception as e:
            raise ProjectServiceError(
                message=f"Failed to copy directory with resolution: {e}",
                operation="copy_directory_with_resolution",
                details=f"Source: {source_dir}, Target: {target_dir}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _prompt_file_resolution(
        self, target_file: Path, context: str
    ) -> ConflictAction:
        """Prompt user for file conflict resolution.

        Args:
            target_file: Target file that already exists
            context: Context description

        Returns:
            ConflictAction: User's choice
        """
        try:
            from rich.console import Console
            from rich.panel import Panel

            console = Console()

            console.print(
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
            else:
                skip_all = confirm(
                    "Skip this file and continue?",
                    default=True,
                )
                if skip_all:
                    return ConflictAction.SKIP
                else:
                    return ConflictAction.CANCEL

        except KeyboardInterrupt:
            return ConflictAction.CANCEL
        except Exception as e:
            self.logger.warning(f"Error prompting for file resolution: {e}")
            # Default to skip on error
            return ConflictAction.SKIP

    def _prompt_directory_resolution(
        self, target_dir: Path, context: str
    ) -> ConflictAction:
        """Prompt user for directory conflict resolution.

        Args:
            target_dir: Target directory that already exists
            context: Context description

        Returns:
            ConflictAction: User's choice
        """
        try:
            from rich.console import Console
            from rich.panel import Panel

            console = Console()

            console.print(
                Panel(
                    f"[yellow]⚠️  Conflict detected![/yellow]\n\n"
                    f"Directory already exists: [cyan]{target_dir}[/cyan]\n"
                    f"Context: {context}",
                    title="Directory Conflict",
                    border_style="yellow",
                )
            )

            # Show options
            console.print("\n[bold]Choose an action:[/bold]")
            console.print("1. [green]Merge[/green] - Add new files, keep existing")
            console.print("2. [yellow]Overwrite[/yellow] - Replace entire directory")
            console.print("3. [red]Skip[/red] - Don't copy this directory")
            console.print("4. [red]Cancel[/red] - Abort operation")

            from rich.prompt import Prompt

            choice = Prompt.ask(
                "\nYour choice",
                choices=["1", "2", "3", "4"],
                default="1",
            )

            if choice == "1":
                return ConflictAction.MERGE
            elif choice == "2":
                overwrite_confirm = confirm(
                    "[red]⚠️  This will delete all existing files in the directory. Continue?[/red]",
                    default=False,
                )
                if overwrite_confirm:
                    return ConflictAction.OVERWRITE
                else:
                    return self._prompt_directory_resolution(target_dir, context)
            elif choice == "3":
                return ConflictAction.SKIP
            else:  # choice == "4"
                return ConflictAction.CANCEL

        except KeyboardInterrupt:
            return ConflictAction.CANCEL
        except Exception as e:
            self.logger.warning(f"Error prompting for directory resolution: {e}")
            # Default to merge on error (safer)
            return ConflictAction.MERGE
