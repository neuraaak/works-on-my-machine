#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PLATFORM UTILS - Platform-Specific Utility Functions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Pure utility functions for platform-specific operations.

This module provides stateless functions for:
- Getting platform information (OS, paths, etc.)
- Getting Python paths according to OS
- Getting Node.js paths according to OS
- Getting shell commands according to OS
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import os
import platform

# Local imports
from ...exceptions.project import ProjectServiceError

# ///////////////////////////////////////////////////////////////
# PLATFORM INFORMATION
# ///////////////////////////////////////////////////////////////


def get_platform_info() -> dict[str, str | bool]:
    """Get platform information.

    Returns:
        dict[str, str | bool]: Dictionary containing:
            - system: Platform system name (Windows, Linux, Darwin)
            - system_lower: Lowercase platform system name
            - is_windows: True if Windows
            - is_linux: True if Linux
            - is_macos: True if macOS
            - path_separator: Path separator for the platform
            - line_ending: Line ending for the platform

    Raises:
        ProjectServiceError: If platform information retrieval fails
    """
    try:
        system = platform.system()
        return {
            "system": system,
            "system_lower": system.lower(),
            "is_windows": system == "Windows",
            "is_linux": system == "Linux",
            "is_macos": system == "Darwin",
            "path_separator": os.sep,
            "line_ending": "\r\n" if system == "Windows" else "\n",
        }
    except Exception as e:
        raise ProjectServiceError(
            message=f"Failed to get platform information: {e}",
            operation="get_platform_info",
            details=f"Exception type: {type(e).__name__}",
        ) from e


# ///////////////////////////////////////////////////////////////
# PYTHON PATHS
# ///////////////////////////////////////////////////////////////


def get_python_paths() -> dict[str, str]:
    """Get Python paths according to OS.

    Returns:
        dict[str, str]: Dictionary containing:
            - venv_python: Path to Python in virtual environment
            - venv_activate: Command to activate virtual environment
            - venv_pip: Path to pip in virtual environment
            - python_executable: Python executable name

    Raises:
        ProjectServiceError: If Python paths retrieval fails
    """
    try:
        platform_info = get_platform_info()

        if platform_info["is_windows"]:
            return {
                "venv_python": "./venv/Scripts/python.exe",
                "venv_activate": "./venv/Scripts/activate.bat",
                "venv_pip": "./venv/Scripts/pip.exe",
                "python_executable": "python.exe",
            }
        else:  # Linux/macOS
            return {
                "venv_python": "./venv/bin/python",
                "venv_activate": "source ./venv/bin/activate",
                "venv_pip": "./venv/bin/pip",
                "python_executable": "python3",
            }
    except Exception as e:
        raise ProjectServiceError(
            message=f"Failed to get Python paths: {e}",
            operation="get_python_paths",
            details=f"Exception type: {type(e).__name__}",
        ) from e


# ///////////////////////////////////////////////////////////////
# NODE.JS PATHS
# ///////////////////////////////////////////////////////////////


def get_node_paths() -> dict[str, str]:
    """Get Node.js paths according to OS.

    Returns:
        dict[str, str]: Dictionary containing:
            - npm_executable: npm executable name
            - node_executable: node executable name
            - npx_executable: npx executable name

    Raises:
        ProjectServiceError: If Node.js paths retrieval fails
    """
    try:
        platform_info = get_platform_info()

        if platform_info["is_windows"]:
            return {
                "npm_executable": "npm.cmd",
                "node_executable": "node.exe",
                "npx_executable": "npx.cmd",
            }
        else:  # Linux/macOS
            return {
                "npm_executable": "npm",
                "node_executable": "node",
                "npx_executable": "npx",
            }
    except Exception as e:
        raise ProjectServiceError(
            message=f"Failed to get Node.js paths: {e}",
            operation="get_node_paths",
            details=f"Exception type: {type(e).__name__}",
        ) from e


# ///////////////////////////////////////////////////////////////
# SHELL COMMANDS
# ///////////////////////////////////////////////////////////////


def get_shell_commands() -> dict[str, str]:
    """Get shell commands according to OS.

    Returns:
        dict[str, str]: Dictionary containing:
            - shell: Shell name (cmd or bash)
            - shell_extension: Shell script extension (.bat or .sh)
            - remove_dir: Command to remove a directory
            - copy_file: Command to copy a file
            - move_file: Command to move a file
            - make_executable: Command to make a file executable
            - which: Command to find executable location

    Raises:
        ProjectServiceError: If shell commands retrieval fails
    """
    try:
        platform_info = get_platform_info()

        if platform_info["is_windows"]:
            return {
                "shell": "cmd",
                "shell_extension": ".bat",
                "remove_dir": "rmdir /s /q",
                "copy_file": "copy",
                "move_file": "move",
                "make_executable": "rem",  # Not needed on Windows
                "which": "where",
            }
        else:  # Linux/macOS
            return {
                "shell": "bash",
                "shell_extension": ".sh",
                "remove_dir": "rm -rf",
                "copy_file": "cp",
                "move_file": "mv",
                "make_executable": "chmod +x",
                "which": "which",
            }
    except Exception as e:
        raise ProjectServiceError(
            message=f"Failed to get shell commands: {e}",
            operation="get_shell_commands",
            details=f"Exception type: {type(e).__name__}",
        ) from e


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "get_node_paths",
    "get_platform_info",
    "get_python_paths",
    "get_shell_commands",
]
