#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM ENVIRONMENT UTILS - Environment Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Environment utilities for Works On My Machine.

Provides utility functions for environment variable management and
refresh operations. Cross-platform environment utilities for system
operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import os
import platform
from pathlib import Path

# Local imports
from ...exceptions.system import EnvironmentServiceError

# ///////////////////////////////////////////////////////////////
# WINDOWS REGISTRY FUNCTIONS
# ///////////////////////////////////////////////////////////////


def read_windows_registry_path() -> tuple[str | None, str | None]:
    """
    Read PATH from Windows registry (HKLM and HKCU).

    Returns:
        Tuple[Optional[str], Optional[str]]: (HKLM_PATH, HKCU_PATH)

    Raises:
        EnvironmentRefreshError: If registry access fails
    """
    if platform.system().lower() != "windows":
        raise EnvironmentServiceError(
            operation="registry_read",
            message="Registry access is only available on Windows",
            details="Current platform is not Windows",
        )

    try:
        import winreg

        hklm_path = None
        hkcu_path = None

        # Read HKLM PATH
        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"System\CurrentControlSet\Control\Session Manager\Environment",
            ) as key:
                hklm_path = winreg.QueryValueEx(key, "Path")[0]
        except (FileNotFoundError, OSError):
            pass

        # Read HKCU PATH
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                hkcu_path = winreg.QueryValueEx(key, "Path")[0]
        except (FileNotFoundError, OSError):
            pass

        return hklm_path, hkcu_path

    except ImportError as e:
        raise EnvironmentServiceError(
            operation="registry_read",
            message="winreg module not available",
            details="Windows registry access requires winreg module",
        ) from e


def combine_paths(hklm_path: str | None, hkcu_path: str | None) -> str:
    """
    Combine HKLM and HKCU paths into a single PATH string.

    Args:
        hklm_path: HKLM PATH value
        hkcu_path: HKCU PATH value

    Returns:
        str: Combined PATH value
    """
    if hklm_path and hkcu_path:
        return f"{hklm_path};{hkcu_path}"
    if hklm_path:
        return hklm_path
    if hkcu_path:
        return hkcu_path
    return ""


# ///////////////////////////////////////////////////////////////
# PATH MANAGEMENT FUNCTIONS
# ///////////////////////////////////////////////////////////////


def refresh_path_from_registry() -> bool:
    """
    Refresh PATH from Windows registry.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        hklm_path, hkcu_path = read_windows_registry_path()
        combined_path = combine_paths(hklm_path, hkcu_path)

        if combined_path:
            os.environ["PATH"] = combined_path
            return True
        return False
    except EnvironmentServiceError:
        return False


def get_shell_config_files() -> list[Path]:
    """
    Get list of shell configuration files for Unix systems.

    Returns:
        List[Path]: List of shell configuration file paths
    """
    home = Path.home()
    config_files = [
        home / ".bashrc",
        home / ".zshrc",
        home / ".profile",
        home / ".bash_profile",
        home / ".zprofile",
    ]

    return [f for f in config_files if f.exists()]


# ///////////////////////////////////////////////////////////////
# SYSTEM INFORMATION FUNCTIONS
# ///////////////////////////////////////////////////////////////


def get_environment_info() -> dict[str, str]:
    """
    Get comprehensive environment information.

    Returns:
        Dict[str, str]: Dictionary of environment information
    """
    return {
        "platform": platform.system().lower(),
        "path": os.environ.get("PATH", ""),
        "home": os.environ.get("HOME", os.environ.get("USERPROFILE", "")),
        "shell": os.environ.get("SHELL", os.environ.get("COMSPEC", "")),
        "user": os.environ.get("USER", os.environ.get("USERNAME", "")),
        "temp": os.environ.get("TEMP", os.environ.get("TMP", "")),
    }


# ///////////////////////////////////////////////////////////////
# COMMAND ACCESSIBILITY FUNCTIONS
# ///////////////////////////////////////////////////////////////


def is_command_accessible(command: str) -> bool:
    """
    Check if a command is accessible in the current environment.

    Args:
        command: Command to check

    Returns:
        bool: True if command is accessible, False otherwise
    """
    import shutil

    return shutil.which(command) is not None
