#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT VALIDATION SERVICE - Project Validation Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Project Validation Service - Singleton service for project validation.

Validates project names, paths, and configurations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import re
from pathlib import Path
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.common import ValidationServiceError
from ...exceptions.project.project_service import ProjectServiceError
from ...shared.configs.project.project_config import ProjectConfig
from ...utils.project import suggest_project_name

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# PROJECT VALIDATION SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class ProjectValidationService:
    """Singleton service for project validation utilities."""

    _instance: ClassVar[ProjectValidationService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> ProjectValidationService:
        """Create or return the singleton instance.

        Returns:
            ProjectValidationService: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize project validation service (only once)."""
        if ProjectValidationService._initialized:
            return

        self.logger = logging.getLogger(__name__)
        ProjectValidationService._initialized = True

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def validate_project_name(self, project_name: str) -> None:
        """Validate a project name.

        Args:
            project_name: Name to validate

        Raises:
            ProjectValidationError: If project name is invalid
        """
        try:
            if not project_name:
                raise ValidationServiceError(
                    message="Project name cannot be empty",
                    validation_type="project_name",
                    value=project_name or "None",
                    reason="Project name cannot be empty",
                    details="Empty or None project name provided",
                )

            if len(project_name) > ProjectConfig.MAX_PROJECT_NAME_LENGTH:
                raise ValidationServiceError(
                    message=f"Project name is too long (max {ProjectConfig.MAX_PROJECT_NAME_LENGTH} characters)",
                    validation_type="project_name",
                    value=project_name,
                    reason=f"Project name is too long (max {ProjectConfig.MAX_PROJECT_NAME_LENGTH} characters)",
                    details=f"Length: {len(project_name)}, Max: {ProjectConfig.MAX_PROJECT_NAME_LENGTH}",
                )

            if project_name.startswith(".") or project_name.endswith("."):
                raise ValidationServiceError(
                    message="Project name cannot start or end with a dot",
                    validation_type="project_name",
                    value=project_name,
                    reason="Project name cannot start or end with a dot",
                    details="Project names must not begin or end with '.'",
                )

            if re.search(ProjectConfig.INVALID_CHARS, project_name):
                raise ValidationServiceError(
                    message=f"Project name contains invalid characters: {ProjectConfig.INVALID_CHARS}",
                    validation_type="project_name",
                    value=project_name,
                    reason=f"Project name contains invalid characters: {ProjectConfig.INVALID_CHARS}",
                    details="Invalid characters detected in project name",
                )

            if project_name.upper() in ProjectConfig.RESERVED_NAMES:
                raise ValidationServiceError(
                    message=f"Project name '{project_name}' is reserved on Windows",
                    validation_type="project_name",
                    value=project_name,
                    reason=f"Project name '{project_name}' is reserved on Windows",
                    details=f"Reserved name: {project_name.upper()}",
                )

            if not re.match(r"^[a-zA-Z0-9._-]+$", project_name):
                raise ValidationServiceError(
                    message="Project name can only contain letters, numbers, dots, underscores, and hyphens",
                    validation_type="project_name",
                    value=project_name,
                    reason="Project name can only contain letters, numbers, dots, underscores, and hyphens",
                    details="Invalid character pattern detected",
                )

        except ValidationServiceError:
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise ProjectServiceError(
                message=f"Unexpected error during project name validation: {e}",
                operation="validate_project_name",
                details=f"Exception type: {type(e).__name__}, Project name: {project_name}",
            ) from e

    def validate_project_path(self, project_path: Path) -> None:
        """Validate a project path.

        Args:
            project_path: Path to validate

        Raises:
            ProjectValidationError: If project path is invalid
        """
        try:
            if not project_path:
                raise ValidationServiceError(
                    message="Project path cannot be None",
                    validation_type="project_path",
                    value="None",
                    reason="Project path cannot be None",
                    details="Empty or None project path provided",
                )

            # Check if path is absolute
            if not project_path.is_absolute():
                project_path = project_path.resolve()

            # Check if parent directory exists and is writable
            parent_dir = project_path.parent
            if not parent_dir.exists():
                raise ValidationServiceError(
                    message="Parent directory does not exist",
                    validation_type="project_path",
                    value=str(project_path),
                    reason="Parent directory does not exist",
                    details=f"Parent directory: {parent_dir}",
                )

            if not parent_dir.is_dir():
                raise ValidationServiceError(
                    message="Parent path is not a directory",
                    validation_type="project_path",
                    value=str(project_path),
                    reason="Parent path is not a directory",
                    details=f"Parent path: {parent_dir}",
                )

            # Check if we can write to parent directory
            try:
                test_file = parent_dir / ".womm_test_write"
                test_file.touch()
                test_file.unlink()
            except (PermissionError, OSError) as e:
                raise ValidationServiceError(
                    message="Cannot write to directory",
                    validation_type="project_path",
                    value=str(project_path),
                    reason="Cannot write to directory",
                    details=f"Parent directory: {parent_dir}, Error: {e}",
                ) from e

            # Check if project directory already exists
            if project_path.exists():
                if not project_path.is_dir():
                    raise ValidationServiceError(
                        message="Path exists but is not a directory",
                        validation_type="project_path",
                        value=str(project_path),
                        reason="Path exists but is not a directory",
                        details=f"Path: {project_path}",
                    )

                # Check if directory is empty
                try:
                    if any(project_path.iterdir()):
                        raise ValidationServiceError(
                            message="Directory is not empty",
                            validation_type="project_path",
                            value=str(project_path),
                            reason="Directory is not empty",
                            details=f"Directory: {project_path}",
                        )
                except PermissionError as e:
                    raise ValidationServiceError(
                        message="Cannot access directory",
                        validation_type="project_path",
                        value=str(project_path),
                        reason="Cannot access directory",
                        details=f"Directory: {project_path}, Error: {e}",
                    ) from e

        except (ValidationServiceError, ProjectServiceError):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise ProjectServiceError(
                message=f"Unexpected error during project path validation: {e}",
                operation="validate_project_path",
                details=f"Exception type: {type(e).__name__}, Project path: {project_path}",
            ) from e

    def validate_project_type(self, project_type: str) -> None:
        """Validate a project type.

        Args:
            project_type: Type to validate

        Raises:
            ProjectValidationError: If project type is invalid
        """
        try:
            if not project_type:
                raise ValidationServiceError(
                    message="Project type cannot be empty",
                    validation_type="project_type",
                    value=project_type or "None",
                    reason="Project type cannot be empty",
                    details="Empty or None project type provided",
                )

            if project_type not in ProjectConfig.SUPPORTED_PROJECT_TYPES:
                raise ValidationServiceError(
                    message=f"Unsupported project type: {project_type}",
                    validation_type="project_type",
                    value=project_type,
                    reason=f"Unsupported project type: {project_type}",
                    details=f"Supported types: {', '.join(ProjectConfig.SUPPORTED_PROJECT_TYPES)}",
                )

        except ValidationServiceError:
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise ProjectServiceError(
                message=f"Unexpected error during project type validation: {e}",
                operation="validate_project_type",
                details=f"Exception type: {type(e).__name__}, Project type: {project_type}",
            ) from e

    def validate_project_config(self, config: dict[str, str]) -> None:
        """Validate a project configuration.

        Args:
            config: Configuration dictionary to validate

        Raises:
            ProjectValidationError: If project configuration is invalid
        """
        try:
            if not config:
                raise ValidationServiceError(
                    message="Project configuration cannot be None",
                    validation_type="project_config",
                    value="None",
                    reason="Project configuration cannot be None",
                    details="Empty or None configuration provided",
                )

            required_fields = ["project_name", "project_type"]

            for field in required_fields:
                if field not in config:
                    raise ValidationServiceError(
                        message=f"Missing required field: {field}",
                        validation_type="project_config",
                        value=str(config),
                        reason=f"Missing required field: {field}",
                        details=f"Required fields: {', '.join(required_fields)}",
                    )

            # Validate individual fields
            self.validate_project_name(config["project_name"])
            self.validate_project_type(config["project_type"])

        except (ValidationServiceError, ProjectServiceError):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise ProjectServiceError(
                message=f"Unexpected error during project configuration validation: {e}",
                operation="validate_project_config",
                details=f"Exception type: {type(e).__name__}, Config: {config}",
            ) from e

    def suggest_project_name(self, base_name: str) -> str:
        """Suggest a valid project name based on input.

        Args:
            base_name: Base name to suggest from

        Returns:
            str: Valid project name suggestion

        Raises:
            ProjectServiceError: If project name suggestion fails
        """
        return suggest_project_name(base_name)

    def check_project_name(self, project_name: str) -> tuple[bool, str | None]:
        """Check if a project name is valid (non-raising version for UI).

        Args:
            project_name: Name to check

        Returns:
            tuple[bool, str | None]: (is_valid, error_message)
        """
        try:
            self.validate_project_name(project_name)
            return (True, None)
        except ValidationServiceError as e:
            return (False, str(e))
        except Exception as e:
            return (False, f"Unexpected error: {e}")

    def get_validation_summary(
        self, project_name: str, project_path: Path, project_type: str
    ) -> dict[str, bool]:
        """Get validation summary for all project components.

        Args:
            project_name: Project name to validate
            project_path: Project path to validate
            project_type: Project type to validate

        Returns:
            dict[str, bool]: Validation results for each component

        Raises:
            ProjectServiceError: If validation summary generation fails
        """
        try:
            summary = {
                "project_name": True,
                "project_path": True,
                "project_type": True,
            }

            # Validate project name
            try:
                self.validate_project_name(project_name)
            except ValidationServiceError:
                summary["project_name"] = False

            # Validate project path
            try:
                self.validate_project_path(project_path)
            except ValidationServiceError:
                summary["project_path"] = False

            # Validate project type
            try:
                self.validate_project_type(project_type)
            except ValidationServiceError:
                summary["project_type"] = False

            return summary

        except Exception as e:
            raise ProjectServiceError(
                message=f"Failed to generate validation summary: {e}",
                operation="get_validation_summary",
                details=f"Exception type: {type(e).__name__}",
            ) from e
