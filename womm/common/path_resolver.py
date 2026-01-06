#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PATH_RESOLVER - Path Management Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Path management utilities for Works On My Machine.

This module provides path resolution and validation functions for
project directories, shared modules, and script locations.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path

# Local imports
from ..core.exceptions import PathResolutionError
from .imports import get_languages_module_path, get_shared_module_path

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

LANGUAGES_PREFIX = "languages/"
LANGUAGES_PREFIX_LENGTH = len(LANGUAGES_PREFIX)

# ///////////////////////////////////////////////////////////////
# PATH RESOLUTION FUNCTIONS
# ///////////////////////////////////////////////////////////////


def get_project_root() -> Path:
    """Get the project root directory.

    Returns:
        Path: Path to the project root directory

    Raises:
        PathResolutionError: If project root cannot be resolved
    """
    try:
        return Path(__file__).parent.parent.parent
    except Exception as e:
        raise PathResolutionError(
            operation="get_project_root",
            path="project_root",
            reason="Failed to resolve project root directory",
            details=str(e),
        ) from e


def get_shared_path() -> Path:
    """Get the shared modules path.

    Returns:
        Path: Path to the shared modules directory

    Raises:
        PathResolutionError: If shared path cannot be resolved
    """
    try:
        return get_shared_module_path()
    except Exception as e:
        raise PathResolutionError(
            operation="get_shared_path",
            path="shared",
            reason="Failed to get shared modules path",
            details=str(e),
        ) from e


def resolve_script_path(relative_path: str) -> Path:
    """Resolve a script path relative to the project root.

    Args:
        relative_path: Relative path to resolve

    Returns:
        Path: Resolved absolute path

    Raises:
        PathResolutionError: If script path cannot be resolved
    """
    try:
        # Handle both development and PyPI installation
        if relative_path.startswith(LANGUAGES_PREFIX):
            languages_path = get_languages_module_path()
            return languages_path / relative_path[LANGUAGES_PREFIX_LENGTH:]
        else:
            return get_project_root() / relative_path
    except Exception as e:
        raise PathResolutionError(
            operation="resolve_script_path",
            path=relative_path,
            reason="Failed to resolve script path",
            details=str(e),
        ) from e


# ///////////////////////////////////////////////////////////////
# VALIDATION FUNCTIONS
# ///////////////////////////////////////////////////////////////


def validate_script_exists(script_path: Path) -> bool:
    """Validate that a script file exists and is executable.

    Args:
        script_path: Path to the script file

    Returns:
        bool: True if script exists and is a file, False otherwise

    Raises:
        PathResolutionError: If validation fails
    """
    try:
        return script_path.exists() and script_path.is_file()
    except Exception as e:
        raise PathResolutionError(
            operation="validate_script_exists",
            path=str(script_path),
            reason="Failed to validate script existence",
            details=str(e),
        ) from e


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "get_project_root",
    "get_shared_path",
    "resolve_script_path",
    "validate_script_exists",
]
