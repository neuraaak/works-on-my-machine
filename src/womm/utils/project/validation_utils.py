#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT VALIDATION UTILS - Pure Project Validation Functions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Pure utility functions for project validation.

This module provides stateless functions for:
- Project name validation and suggestion
- Project path validation
- Project type validation
- Project configuration validation
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import re
from pathlib import Path

# Local imports
from ...shared.configs.project import ProjectConfig

# ///////////////////////////////////////////////////////////////
# VALIDATION FUNCTIONS
# ///////////////////////////////////////////////////////////////


def suggest_project_name(base_name: str) -> str:
    """Suggest a valid project name based on input.

    Args:
        base_name: Base name to suggest from

    Returns:
        str: Valid project name suggestion
    """
    if not base_name:
        return "my-project"

    # Remove invalid characters
    suggested = re.sub(ProjectConfig.INVALID_CHARS, "-", base_name)

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
    if len(suggested) > ProjectConfig.MAX_PROJECT_NAME_LENGTH:
        suggested = suggested[: ProjectConfig.MAX_PROJECT_NAME_LENGTH].rstrip("-")

    # Ensure it doesn't start with a number
    if suggested and suggested[0].isdigit():
        suggested = f"project-{suggested}"

    return suggested


def validate_project_name(project_name: str) -> None:
    """Validate a project name.

    Args:
        project_name: Name to validate

    Raises:
        ValueError: If project name is invalid
    """
    if not project_name:
        raise ValueError("Project name cannot be empty")

    if len(project_name) > ProjectConfig.MAX_PROJECT_NAME_LENGTH:
        raise ValueError(
            f"Project name is too long (max "
            f"{ProjectConfig.MAX_PROJECT_NAME_LENGTH} characters): "
            f"length={len(project_name)}"
        )

    if project_name.startswith(".") or project_name.endswith("."):
        raise ValueError("Project name cannot start or end with a dot")

    if re.search(ProjectConfig.INVALID_CHARS, project_name):
        raise ValueError(
            f"Project name contains invalid characters: {ProjectConfig.INVALID_CHARS}"
        )

    if project_name.upper() in ProjectConfig.RESERVED_NAMES:
        raise ValueError(f"Project name '{project_name}' is reserved on Windows")

    if not re.match(r"^[a-zA-Z0-9._-]+$", project_name):
        raise ValueError(
            "Project name can only contain letters, numbers, dots, "
            "underscores, and hyphens"
        )


def validate_project_path(project_path: Path) -> None:
    """Validate a project path.

    Args:
        project_path: Path to validate

    Raises:
        ValueError: If project path is invalid
        OSError: If the parent directory cannot be accessed
    """
    if not project_path:
        raise ValueError("Project path cannot be None")

    # Check if path is absolute
    if not project_path.is_absolute():
        project_path = project_path.resolve()

    # Check if parent directory exists and is writable
    parent_dir = project_path.parent
    if not parent_dir.exists():
        raise ValueError(f"Parent directory does not exist: {parent_dir}")

    if not parent_dir.is_dir():
        raise ValueError(f"Parent path is not a directory: {parent_dir}")

    # Check if we can write to parent directory
    test_file = parent_dir / ".womm_test_write"
    test_file.touch()
    test_file.unlink()

    # Check if project directory already exists
    if project_path.exists():
        if not project_path.is_dir():
            raise ValueError(f"Path exists but is not a directory: {project_path}")

        # Check if directory is empty
        if any(project_path.iterdir()):
            raise ValueError(f"Directory is not empty: {project_path}")


def validate_project_type(project_type: str) -> None:
    """Validate a project type.

    Args:
        project_type: Type to validate

    Raises:
        ValueError: If project type is invalid
    """
    if not project_type:
        raise ValueError("Project type cannot be empty")

    if project_type not in ProjectConfig.SUPPORTED_PROJECT_TYPES:
        raise ValueError(
            f"Unsupported project type: {project_type}. "
            f"Supported types: {', '.join(ProjectConfig.SUPPORTED_PROJECT_TYPES)}"
        )


def validate_project_config(config: dict[str, str]) -> None:
    """Validate a project configuration.

    Args:
        config: Configuration dictionary to validate

    Raises:
        ValueError: If project configuration is invalid
    """
    if not config:
        raise ValueError("Project configuration cannot be None")

    required_fields = ["project_name", "project_type"]

    for field in required_fields:
        if field not in config:
            raise ValueError(
                f"Missing required field: {field}. "
                f"Required fields: {', '.join(required_fields)}"
            )

    # Validate individual fields
    validate_project_name(config["project_name"])
    validate_project_type(config["project_type"])


def check_project_name(project_name: str) -> tuple[bool, str | None]:
    """Check if a project name is valid (non-raising version for UI).

    Args:
        project_name: Name to check

    Returns:
        tuple[bool, str | None]: (is_valid, error_message)
    """
    try:
        validate_project_name(project_name)
        return (True, None)
    except ValueError as e:
        return (False, str(e))


def get_validation_summary(
    project_name: str, project_path: Path, project_type: str
) -> dict[str, bool]:
    """Get validation summary for all project components.

    Args:
        project_name: Project name to validate
        project_path: Project path to validate
        project_type: Project type to validate

    Returns:
        dict[str, bool]: Validation results for each component
    """
    summary = {
        "project_name": True,
        "project_path": True,
        "project_type": True,
    }

    # Validate project name
    try:
        validate_project_name(project_name)
    except ValueError:
        summary["project_name"] = False

    # Validate project path
    try:
        validate_project_path(project_path)
    except (ValueError, OSError):
        summary["project_path"] = False

    # Validate project type
    try:
        validate_project_type(project_type)
    except ValueError:
        summary["project_type"] = False

    return summary


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "check_project_name",
    "get_validation_summary",
    "suggest_project_name",
    "validate_project_config",
    "validate_project_name",
    "validate_project_path",
    "validate_project_type",
]
