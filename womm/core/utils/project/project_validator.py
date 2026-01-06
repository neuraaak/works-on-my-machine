#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT VALIDATOR - Project Validation Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Project validation utilities for WOMM CLI.
Validates project names, paths, and configurations.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import re
from pathlib import Path

# Local imports
from ...exceptions.project import ProjectUtilityError, ProjectValidationError


class ProjectValidator:
    """Project validation utilities."""

    # Invalid characters for project names
    INVALID_CHARS = r'[<>:"/\\|?*]'

    # Reserved names on Windows
    RESERVED_NAMES = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    }

    @classmethod
    def validate_project_name(cls, project_name: str) -> None:
        """
        Validate a project name.

        Args:
            project_name: Name to validate

        Raises:
            ProjectValidationError: If project name is invalid
        """
        try:
            if not project_name:
                raise ProjectValidationError(
                    validation_type="project_name",
                    value=project_name or "None",
                    reason="Project name cannot be empty",
                    details="Empty or None project name provided",
                )

            if len(project_name) > 50:
                raise ProjectValidationError(
                    validation_type="project_name",
                    value=project_name,
                    reason="Project name is too long (max 50 characters)",
                    details=f"Length: {len(project_name)}, Max: 50",
                )

            if project_name.startswith(".") or project_name.endswith("."):
                raise ProjectValidationError(
                    validation_type="project_name",
                    value=project_name,
                    reason="Project name cannot start or end with a dot",
                    details="Project names must not begin or end with '.'",
                )

            if re.search(cls.INVALID_CHARS, project_name):
                raise ProjectValidationError(
                    validation_type="project_name",
                    value=project_name,
                    reason=f"Project name contains invalid characters: {cls.INVALID_CHARS}",
                    details="Invalid characters detected in project name",
                )

            if project_name.upper() in cls.RESERVED_NAMES:
                raise ProjectValidationError(
                    validation_type="project_name",
                    value=project_name,
                    reason=f"Project name '{project_name}' is reserved on Windows",
                    details=f"Reserved name: {project_name.upper()}",
                )

            if not re.match(r"^[a-zA-Z0-9._-]+$", project_name):
                raise ProjectValidationError(
                    validation_type="project_name",
                    value=project_name,
                    reason="Project name can only contain letters, numbers, dots, underscores, and hyphens",
                    details="Invalid character pattern detected",
                )

        except ProjectValidationError:
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise ProjectUtilityError(
                message=f"Unexpected error during project name validation: {e}",
                details=f"Exception type: {type(e).__name__}, Project name: {project_name}",
            ) from e

    @classmethod
    def validate_project_path(cls, project_path: Path) -> None:
        """
        Validate a project path.

        Args:
            project_path: Path to validate

        Raises:
            ProjectValidationError: If project path is invalid
        """
        try:
            if not project_path:
                raise ProjectValidationError(
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
                raise ProjectValidationError(
                    validation_type="project_path",
                    value=str(project_path),
                    reason="Parent directory does not exist",
                    details=f"Parent directory: {parent_dir}",
                )

            if not parent_dir.is_dir():
                raise ProjectValidationError(
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
                raise ProjectValidationError(
                    validation_type="project_path",
                    value=str(project_path),
                    reason="Cannot write to directory",
                    details=f"Parent directory: {parent_dir}, Error: {e}",
                ) from e

            # Check if project directory already exists
            if project_path.exists():
                if not project_path.is_dir():
                    raise ProjectValidationError(
                        validation_type="project_path",
                        value=str(project_path),
                        reason="Path exists but is not a directory",
                        details=f"Path: {project_path}",
                    )

                # Check if directory is empty
                try:
                    if any(project_path.iterdir()):
                        raise ProjectValidationError(
                            validation_type="project_path",
                            value=str(project_path),
                            reason="Directory is not empty",
                            details=f"Directory: {project_path}",
                        )
                except PermissionError as e:
                    raise ProjectValidationError(
                        validation_type="project_path",
                        value=str(project_path),
                        reason="Cannot access directory",
                        details=f"Directory: {project_path}, Error: {e}",
                    ) from e

        except (ProjectValidationError, ProjectUtilityError):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise ProjectUtilityError(
                message=f"Unexpected error during project path validation: {e}",
                details=f"Exception type: {type(e).__name__}, Project path: {project_path}",
            ) from e

    @classmethod
    def validate_project_type(cls, project_type: str) -> None:
        """
        Validate a project type.

        Args:
            project_type: Type to validate

        Raises:
            ProjectValidationError: If project type is invalid
        """
        try:
            supported_types = ["python", "javascript", "react", "vue"]

            if not project_type:
                raise ProjectValidationError(
                    validation_type="project_type",
                    value=project_type or "None",
                    reason="Project type cannot be empty",
                    details="Empty or None project type provided",
                )

            if project_type not in supported_types:
                raise ProjectValidationError(
                    validation_type="project_type",
                    value=project_type,
                    reason=f"Unsupported project type: {project_type}",
                    details=f"Supported types: {', '.join(supported_types)}",
                )

        except ProjectValidationError:
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise ProjectUtilityError(
                message=f"Unexpected error during project type validation: {e}",
                details=f"Exception type: {type(e).__name__}, Project type: {project_type}",
            ) from e

    @classmethod
    def validate_project_config(cls, config: dict[str, str]) -> None:
        """
        Validate a project configuration.

        Args:
            config: Configuration dictionary to validate

        Raises:
            ProjectValidationError: If project configuration is invalid
        """
        try:
            if not config:
                raise ProjectValidationError(
                    validation_type="project_config",
                    value="None",
                    reason="Project configuration cannot be None",
                    details="Empty or None configuration provided",
                )

            required_fields = ["project_name", "project_type"]

            for field in required_fields:
                if field not in config:
                    raise ProjectValidationError(
                        validation_type="project_config",
                        value=str(config),
                        reason=f"Missing required field: {field}",
                        details=f"Required fields: {', '.join(required_fields)}",
                    )

            # Validate individual fields
            cls.validate_project_name(config["project_name"])
            cls.validate_project_type(config["project_type"])

        except (ProjectValidationError, ProjectUtilityError):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise ProjectUtilityError(
                message=f"Unexpected error during project configuration validation: {e}",
                details=f"Exception type: {type(e).__name__}, Config: {config}",
            ) from e

    @classmethod
    def suggest_project_name(cls, base_name: str) -> str:
        """
        Suggest a valid project name based on input.

        Args:
            base_name: Base name to suggest from

        Returns:
            Valid project name suggestion

        Raises:
            ProjectUtilityError: If project name suggestion fails
        """
        try:
            if not base_name:
                return "my-project"

            # Remove invalid characters
            suggested = re.sub(cls.INVALID_CHARS, "-", base_name)

            # Remove leading/trailing dots
            suggested = suggested.strip(".")

            # Convert to lowercase
            suggested = suggested.lower()

            # Replace spaces with hyphens
            suggested = re.sub(r"\s+", "-", suggested)

            # Remove multiple consecutive hyphens
            suggested = re.sub(r"-+", "-", suggested)

            # Ensure it's not empty
            if not suggested:
                suggested = "my-project"

            # Ensure it's not too long
            if len(suggested) > 50:
                suggested = suggested[:50].rstrip("-")

            # Ensure it doesn't start with a number
            if suggested and suggested[0].isdigit():
                suggested = f"project-{suggested}"

            return suggested

        except Exception as e:
            # Wrap unexpected external exceptions
            raise ProjectUtilityError(
                message=f"Failed to suggest project name: {e}",
                details=f"Exception type: {type(e).__name__}, Base name: {base_name}",
            ) from e

    @classmethod
    def get_validation_summary(
        cls, project_name: str, project_path: Path, project_type: str
    ) -> dict[str, bool]:
        """
        Get validation summary for all project components.

        Args:
            project_name: Project name to validate
            project_path: Project path to validate
            project_type: Project type to validate

        Returns:
            Dict[str, bool]: Validation results for each component

        Raises:
            ProjectUtilityError: If validation summary generation fails
        """
        try:
            summary = {
                "project_name": True,
                "project_path": True,
                "project_type": True,
            }

            # Validate project name
            try:
                cls.validate_project_name(project_name)
            except ProjectValidationError:
                summary["project_name"] = False

            # Validate project path
            try:
                cls.validate_project_path(project_path)
            except ProjectValidationError:
                summary["project_path"] = False

            # Validate project type
            try:
                cls.validate_project_type(project_type)
            except ProjectValidationError:
                summary["project_type"] = False

            return summary

        except Exception as e:
            # Wrap unexpected external exceptions
            raise ProjectUtilityError(
                message=f"Failed to generate validation summary: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e
