#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONFLICT RESOLUTION SERVICE - Project Destination Validation
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Conflict Resolution Service - Singleton service guarding project destinations.

Validates that a destination can safely receive a generated project. The
``--force`` contract is the only conflict policy WOMM offers: a non-empty
destination is refused by default, and ``--force`` merges generated files into
it without ever deleting user content.

The interactive per-file resolution mechanism (``ConflictResolver`` protocol,
``InteractiveConflictResolver``, ``copy_*_with_resolution``) was removed on
2026-08-02: it had no production caller and competed with that contract.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.project import ProjectServiceError

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# CONFLICT RESOLUTION SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class ConflictResolutionService:
    """Singleton service guarding destinations during project creation."""

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
