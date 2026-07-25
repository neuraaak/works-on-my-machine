#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# COMMON UTILS - Common Installation Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Common utilities for Works On My Machine installation operations.

This module provides shared utility functions used by both installation
and uninstallation operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import sys
from pathlib import Path

# Local imports
from ..common.path_resolver_utils import get_project_root

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

# Entry-point module that marks a directory as the womm package root.
MAIN_MODULE = "__main__.py"

# ///////////////////////////////////////////////////////////////
# COMMON PATH UTILITIES
# ///////////////////////////////////////////////////////////////


def get_default_womm_path() -> Path:
    """
    Get the standard default path for Works On My Machine.

    Returns:
        Path: Path object pointing to the .womm directory in user's home.

    Raises:
        RuntimeError: If the home directory cannot be determined.
    """
    return Path.home() / ".womm"


def get_current_womm_path() -> Path:
    """
    Get the womm package directory by finding __main__.py.

    Returns:
        Path: Path object pointing to the womm package directory (parent of __main__.py).

    Raises:
        RuntimeError: If the womm package directory cannot be found.
    """
    # First try: use project root if we're in development
    potential_womm = get_project_root() / "womm" / MAIN_MODULE
    if potential_womm.exists():
        return potential_womm.parent

    # Second try: import womm.__main__ directly
    try:
        import womm.__main__

        return Path(womm.__main__.__file__).parent
    except ImportError as import_error:
        logger.warning(f"Failed to import womm.__main__: {import_error}")

    # Third try: search sys.path for the package's __main__.py
    for path in sys.path:
        if path and (Path(path) / "womm" / MAIN_MODULE).exists():
            return Path(path) / "womm"

    # Last resort: walk up from this file looking for a package root
    for parent in Path(__file__).parents:
        if (parent / MAIN_MODULE).exists():
            return parent

    raise RuntimeError(
        "Could not find womm package directory (__main__.py not found): "
        "project root, import, sys.path scan and parent walk all failed"
    )


def get_womm_installation_path() -> Path:
    """
    Get the WOMM installation directory path.

    This function determines the actual installation directory by:
    1. Getting the current womm package path
    2. Checking if its parent is a valid installation directory
    3. Falling back to the default target path if in development or if detection fails

    Returns:
        Path: Path object pointing to the WOMM installation directory
            (e.g., ~/.womm or custom installation path).

    Raises:
        RuntimeError: If neither the current nor the default path can be determined.
    """
    try:
        # Get the current womm package directory
        current_womm = get_current_womm_path()
        installation_parent = current_womm.parent

        # Check if we're in a development environment
        # (where womm is in the project root, not in an installation directory)
        project_root = get_project_root()
        if installation_parent == project_root:
            # We're in development, use default target path
            logger.debug("Development environment detected, using default target path")
            return get_default_womm_path()

        # Check if the parent directory looks like an installation directory
        # (it should contain the womm subdirectory)
        if (installation_parent / "womm" / MAIN_MODULE).exists():
            # This looks like a valid installation directory
            logger.debug(f"Installation directory detected: {installation_parent}")
            return installation_parent

        # If parent doesn't look like installation, but we're not in development,
        # it might be a custom installation. Still use the parent as it's likely correct.
        logger.debug(
            f"Using parent directory as installation path: {installation_parent}"
        )
        return installation_parent

    except RuntimeError:
        # If get_current_womm_path() fails, fall back to default target path
        logger.warning(
            "Could not determine current womm path, using default target path"
        )
        return get_default_womm_path()


def is_valid_womm_installation(installation_path: Path | None = None) -> bool:
    """
    Check if a directory is a valid WOMM installation.

    A valid WOMM installation must have:
    - A womm/ subdirectory with __main__.py
    - A .proof file in womm/ directory (created during successful installation)

    Args:
        installation_path: Optional path to check. If None, uses get_womm_installation_path()

    Returns:
        bool: True if the installation is valid, False otherwise.
    """
    try:
        if installation_path is None:
            installation_path = get_womm_installation_path()

        installation_path = Path(installation_path)

        # Check 1: womm directory with __main__.py exists
        womm_dir = installation_path / "womm"
        if not womm_dir.is_dir():
            logger.debug(
                f"Invalid WOMM installation: womm directory not found at {womm_dir}"
            )
            return False

        main_file = womm_dir / MAIN_MODULE
        if not main_file.is_file():
            logger.debug(
                f"Invalid WOMM installation: __main__.py not found at {main_file}"
            )
            return False

        # Check 2: .proof file exists (marks successful installation)
        proof_file = womm_dir / ".proof"
        if not proof_file.is_file():
            logger.debug(
                f"Invalid WOMM installation: .proof file not found at {proof_file}"
            )
            return False

        # All checks passed
        logger.debug(f"Valid WOMM installation detected at {installation_path}")
        return True

    except (RuntimeError, OSError) as e:
        logger.debug(f"Error validating WOMM installation: {e}")
        return False
