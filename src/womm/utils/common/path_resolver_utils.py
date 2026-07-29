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
    return Path(__file__).parent.parent.parent / "assets"


# ///////////////////////////////////////////////////////////////
# SCRIPT PATH HELPERS
# ///////////////////////////////////////////////////////////////


def resolve_script_path(relative_path: str) -> Path:
    """Resolve a script path relative to assets, bin, or the working directory.

    The path is resolved based on its prefix:
    - ``\"languages/\"``: resolved against `womm/assets/languages/`
    - ``\"bin/\"``: resolved against `womm/bin/`
    - ``\"assets/\"``: resolved against `womm/assets/`
    - Otherwise: resolved against the current working directory

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
    return Path(relative_path).resolve()


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


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "get_assets_module_path",
    "get_bin_module_path",
    "get_shared_module_path",
    "resolve_script_path",
    "validate_script_exists",
]
