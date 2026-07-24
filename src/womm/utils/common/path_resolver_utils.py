#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PATH RESOLVER UTILS - Path & Module Path Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Path and module path utilities for Works On My Machine.

This module centralizes path resolution logic that was previously in
`womm/shared/path_resolver.py` and `womm/shared/imports.py` (path part).
All helpers are stateless and safe to use from anywhere.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

LANGUAGES_PREFIX = "languages/"
LANGUAGES_PREFIX_LENGTH = len(LANGUAGES_PREFIX)
BIN_PREFIX = "bin/"
BIN_PREFIX_LENGTH = len(BIN_PREFIX)
ASSETS_PREFIX = "assets/"
ASSETS_PREFIX_LENGTH = len(ASSETS_PREFIX)


# ///////////////////////////////////////////////////////////////
# PROJECT & SHARED PATH HELPERS
# ///////////////////////////////////////////////////////////////


def get_project_root() -> Path:
    """Return the project root directory.

    Returns:
        Path: Path to the project root directory.
    """
    return Path(__file__).parent.parent.parent


def get_shared_module_path() -> Path:
    """Return the path to the `womm/shared` directory.

    Returns:
        Path: Path to the shared module directory.
    """
    return Path(__file__).parent.parent.parent / "shared"


def get_bin_module_path() -> Path:
    """Return the path to the `womm/bin` directory.

    Returns:
        Path: Path to the bin module directory.
    """
    return Path(__file__).parent.parent / "bin"


def get_assets_module_path() -> Path:
    """Return the path to the `womm/assets` directory.

    Returns:
        Path: Path to the assets module directory.
    """
    return Path(__file__).parent.parent / "assets"


# ///////////////////////////////////////////////////////////////
# SCRIPT PATH HELPERS
# ///////////////////////////////////////////////////////////////


def resolve_script_path(relative_path: str) -> Path:
    """Resolve a script path relative to assets, bin, or project root.

    The path is resolved based on its prefix:
    - ``\"languages/\"``: resolved against `womm/assets/languages/`
    - ``\"bin/\"``: resolved against `womm/bin/`
    - ``\"assets/\"``: resolved against `womm/assets/`
    - Otherwise: resolved against the project root

    Args:
        relative_path: Relative path to resolve.

    Returns:
        Path: Resolved absolute path.
    """
    if relative_path.startswith(LANGUAGES_PREFIX):
        assets_path = get_assets_module_path()
        return assets_path / "languages" / relative_path[LANGUAGES_PREFIX_LENGTH:]
    if relative_path.startswith(BIN_PREFIX):
        bin_path = get_bin_module_path()
        return bin_path / relative_path[BIN_PREFIX_LENGTH:]
    if relative_path.startswith(ASSETS_PREFIX):
        assets_path = get_assets_module_path()
        return assets_path / relative_path[ASSETS_PREFIX_LENGTH:]
    return get_project_root() / relative_path


def validate_script_exists(script_path: Path) -> bool:
    """Return True if a script file exists and is a regular file.

    Args:
        script_path: Path to the script file.

    Returns:
        bool: True if the path exists and is a file, False otherwise.
    """
    return script_path.exists() and script_path.is_file()


# ///////////////////////////////////////////////////////////////
# ENVIRONMENT DETECTION
# ///////////////////////////////////////////////////////////////


def is_pip_installation() -> bool:
    """Detect if WOMM is running from a pip-installed package.

    Returns True if:
    - womm module is in site-packages or similar (not development directory)
    - No .git directory exists in parent directories

    Returns:
        bool: True if pip installation, False if development environment
    """
    try:
        # Get womm module location
        womm_path = get_assets_module_path().parent.parent

        # Check if running from site-packages or dist-packages
        womm_path_str = str(womm_path).lower()
        if "site-packages" in womm_path_str or "dist-packages" in womm_path_str:
            return True

        # Check if .git exists in parents (development indicator)
        current = womm_path
        for _ in range(5):  # Check up to 5 levels
            if (current / ".git").exists():
                return False
            current = current.parent

        # If we get here, assume pip installation
        return True
    except Exception:
        # If detection fails, assume pip installation (safer fallback)
        return True


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "get_assets_module_path",
    "get_bin_module_path",
    "get_project_root",
    "get_shared_module_path",
    "is_pip_installation",
    "resolve_script_path",
    "validate_script_exists",
]
