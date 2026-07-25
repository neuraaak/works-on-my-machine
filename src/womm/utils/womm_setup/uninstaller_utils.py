#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UNINSTALLATION UTILS - Uninstallation Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Uninstallation utilities for Works On My Machine.

This module provides pure utility functions for WOMM uninstallation operations.
All functions here are stateless and can be used independently.
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

EMPTY_TARGET_PATH = "Target path cannot be empty"

# ///////////////////////////////////////////////////////////////
# FILE SCANNING UTILITIES
# ///////////////////////////////////////////////////////////////


def get_files_to_remove(target_path: Path) -> list[str]:
    """
    Get list of files and directories to remove for progress tracking.

    Args:
        target_path: Target installation directory

    Returns:
        List[str]: List of relative file and directory paths to remove

    Raises:
        ValueError: If `target_path` is empty.
        NotADirectoryError: If `target_path` exists but is not a directory.
        PermissionError: If the directory cannot be traversed.
    """
    if not target_path:
        raise ValueError(EMPTY_TARGET_PATH)

    if not target_path.exists():
        return []

    if not target_path.is_dir():
        raise NotADirectoryError(
            f"Target path exists but is not a directory: {target_path}"
        )

    files_to_remove: list[str] = []

    # Get all files and directories recursively
    for item_path in target_path.rglob("*"):
        relative_path = item_path.relative_to(target_path)
        if item_path.is_file():
            files_to_remove.append(str(relative_path))
        elif item_path.is_dir():
            # Keep a trailing slash so directories sort after their contents
            files_to_remove.append(f"{relative_path}/")

    # Sort to ensure files are removed before their parent directories
    files_to_remove.sort(key=lambda x: (x.endswith("/"), x))

    return files_to_remove


# ///////////////////////////////////////////////////////////////
# VERIFICATION UTILITIES
# ///////////////////////////////////////////////////////////////


def _verify_removed(target_path: Path, success_message: str) -> dict[str, str | bool]:
    """
    Verify that `target_path` no longer exists on disk.

    A path that exists but cannot be stat'ed is treated as removed: the
    uninstall left nothing this process can reach.

    Args:
        target_path: Target installation directory
        success_message: Message to report when the path is gone

    Returns:
        Dict: Dictionary with success status and details

    Raises:
        ValueError: If `target_path` is empty.
        PermissionError: If the path exists but access is denied.
        FileExistsError: If the path still exists and is reachable.
    """
    if not target_path:
        raise ValueError(EMPTY_TARGET_PATH)

    if not target_path.exists():
        return {"success": True, "message": success_message}

    try:
        target_path.stat()
    except PermissionError:
        raise
    except OSError as e:
        logger.warning(f"Failed to stat target path {target_path}: {e}")
        return {
            "success": True,
            "message": "Target path not accessible (considered removed)",
        }

    raise FileExistsError(f"Installation directory still exists: {target_path}")


def verify_files_removed(target_path: Path) -> dict[str, str | bool]:
    """
    Verify that WOMM files were removed successfully.

    Args:
        target_path: Target installation directory

    Returns:
        Dict: Dictionary with success status and details

    Raises:
        ValueError: If `target_path` is empty.
        PermissionError: If the path exists but access is denied.
        FileExistsError: If files remain at the target path.
    """
    return _verify_removed(target_path, "All WOMM files removed successfully")


def verify_directory_removed(target_path: Path) -> dict[str, str | bool]:
    """
    Verify that the installation directory was removed.

    Args:
        target_path: Target installation directory

    Returns:
        Dict: Dictionary with success status and details

    Raises:
        ValueError: If `target_path` is empty.
        PermissionError: If the path exists but access is denied.
        FileExistsError: If the directory still exists.
    """
    return _verify_removed(target_path, "WOMM directory removed successfully")
