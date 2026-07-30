#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONFLICT RESOLUTION SERVICE - File Conflict Resolution
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Conflict Resolution Service - Singleton service for handling file conflicts.

Handles conflicts when copying files during project creation:
- Detects existing files
- Applies a deterministic policy, or defers to a caller-supplied resolver
- Manages merge strategies for directories

The service never talks to the user: an interactive resolution belongs to the
command/UI layer and reaches this service through a ``ConflictResolver``.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import shutil
from pathlib import Path
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.project import ProjectServiceError
from ...shared.conflicts import ConflictAction, ConflictResolver

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

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

    def validate_project_destination(
        self, project_path: Path, force: bool = False
    ) -> None:
        """Validate the destination of a project creation request.

        A non-empty directory is rejected by default so project creation never
        changes an existing project accidentally. ``force`` permits generators
        to merge their files into that directory; it never deletes its contents.

        Raises:
            ProjectServiceError: If the destination cannot safely receive a project.
        """
        try:
            if not project_path.exists():
                return

            if not project_path.is_dir():
                raise ProjectServiceError(
                    operation="validate_project_destination",
                    reason=f"Project destination is not a directory: {project_path}",
                )

            if not any(project_path.iterdir()) or force:
                return

            raise ProjectServiceError(
                operation="validate_project_destination",
                reason=(
                    f"Project destination already exists and is not empty: {project_path}. "
                    "Use --force to merge generated files."
                ),
            )
        except ProjectServiceError:
            raise
        except OSError as e:
            raise ProjectServiceError(
                operation="validate_project_destination",
                reason=str(e),
                details=f"Target: {project_path}",
            ) from e

    def resolve_file_conflict(
        self,
        source_file: Path,
        target_file: Path,
        force: bool = False,
        context: str = "file",
        resolver: ConflictResolver | None = None,
    ) -> ConflictAction:
        """Resolve a file conflict.

        Args:
            source_file: Source file to copy
            target_file: Target file path (may already exist)
            force: If True, automatically overwrite without asking the resolver
            context: Context description for the conflict (e.g., "config file")
            resolver: Optional decision maker consulted on a real conflict.
                Without one, an existing file is left untouched.

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

            if resolver is None:
                self.logger.info(f"No resolver: keeping existing {target_file}")
                return ConflictAction.SKIP

            return resolver.resolve_file(target_file, context)

        except Exception as e:
            raise ProjectServiceError(
                operation="resolve_file_conflict",
                reason=str(e),
                details=f"Source: {source_file}, Target: {target_file}",
            ) from e

    def resolve_directory_conflict(
        self,
        source_dir: Path,
        target_dir: Path,
        force: bool = False,
        context: str = "directory",
        resolver: ConflictResolver | None = None,
    ) -> ConflictAction:
        """Resolve a directory conflict.

        Args:
            source_dir: Source directory to copy
            target_dir: Target directory path (may already exist)
            force: If True, automatically merge without asking the resolver
            context: Context description for the conflict (e.g., ".vscode")
            resolver: Optional decision maker consulted on a real conflict.
                Without one, the directory is merged into, never replaced.

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

            if resolver is None:
                self.logger.info(f"No resolver: merging into {target_dir}")
                return ConflictAction.MERGE

            return resolver.resolve_directory(target_dir, context)

        except Exception as e:
            raise ProjectServiceError(
                operation="resolve_directory_conflict",
                reason=str(e),
                details=f"Source: {source_dir}, Target: {target_dir}",
            ) from e

    def copy_file_with_resolution(
        self,
        source_file: Path,
        target_file: Path,
        force: bool = False,
        context: str = "file",
        resolver: ConflictResolver | None = None,
    ) -> bool:
        """Copy a file with conflict resolution.

        Args:
            source_file: Source file to copy
            target_file: Target file path
            force: If True, automatically overwrite without asking the resolver
            context: Context description for the conflict
            resolver: Optional decision maker consulted on a real conflict

        Returns:
            bool: True if file was copied, False if skipped or cancelled

        Raises:
            ProjectServiceError: If file copy fails
        """
        try:
            # Resolve conflict
            action = self.resolve_file_conflict(
                source_file, target_file, force, context, resolver
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
                operation="copy_file_with_resolution",
                reason=str(e),
                details=f"Source: {source_file}, Target: {target_file}",
            ) from e

    def copy_directory_with_resolution(
        self,
        source_dir: Path,
        target_dir: Path,
        force: bool = False,
        context: str = "directory",
        resolver: ConflictResolver | None = None,
    ) -> bool:
        """Copy a directory with conflict resolution.

        Args:
            source_dir: Source directory to copy
            target_dir: Target directory path
            force: If True, automatically merge without asking the resolver
            context: Context description for the conflict
            resolver: Optional decision maker consulted on a real conflict

        Returns:
            bool: True if directory was copied, False if skipped or cancelled

        Raises:
            ProjectServiceError: If directory copy fails
        """
        try:
            # Resolve conflict
            action = self.resolve_directory_conflict(
                source_dir, target_dir, force, context, resolver
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
                operation="copy_directory_with_resolution",
                reason=str(e),
                details=f"Source: {source_dir}, Target: {target_dir}",
            ) from e
