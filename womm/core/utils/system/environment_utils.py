#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# ENVIRONMENT UTILS - Environment Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Environment utilities for Works On My Machine.

Provides utility functions for environment variable management and refresh operations.
Cross-platform environment utilities for system operations.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import os
import platform
from pathlib import Path

# Local imports
from ...exceptions.system import EnvironmentRefreshError

# ///////////////////////////////////////////////////////////////
# UTILITY FUNCTIONS
# ///////////////////////////////////////////////////////////////


def get_environment_variable(name: str, default: str | None = None) -> str | None:
    """
    Get an environment variable with optional default value.

    Args:
        name: Environment variable name
        default: Default value if variable is not set

    Returns:
        Optional[str]: Environment variable value or default
    """
    return os.environ.get(name, default)


def set_environment_variable(name: str, value: str) -> None:
    """
    Set an environment variable in the current process.

    Args:
        name: Environment variable name
        value: Environment variable value
    """
    os.environ[name] = value


def get_path_variable() -> str:
    """
    Get the current PATH environment variable.

    Returns:
        str: Current PATH value
    """
    return os.environ.get("PATH", "")


def set_path_variable(path: str) -> None:
    """
    Set the PATH environment variable.

    Args:
        path: New PATH value
    """
    os.environ["PATH"] = path


def read_windows_registry_path() -> tuple[str | None, str | None]:
    """
    Read PATH from Windows registry (HKLM and HKCU).

    Returns:
        Tuple[Optional[str], Optional[str]]: (HKLM_PATH, HKCU_PATH)

    Raises:
        EnvironmentRefreshError: If registry access fails
    """
    if platform.system().lower() != "windows":
        raise EnvironmentRefreshError(
            operation="registry_read",
            reason="Registry access is only available on Windows",
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
        raise EnvironmentRefreshError(
            operation="registry_read",
            reason="winreg module not available",
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
    elif hklm_path:
        return hklm_path
    elif hkcu_path:
        return hkcu_path
    else:
        return ""


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
            set_path_variable(combined_path)
            return True
        else:
            return False
    except EnvironmentRefreshError:
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


def get_environment_info() -> dict[str, str]:
    """
    Get comprehensive environment information.

    Returns:
        Dict[str, str]: Dictionary of environment information
    """
    return {
        "platform": platform.system().lower(),
        "path": get_path_variable(),
        "home": os.environ.get("HOME", os.environ.get("USERPROFILE", "")),
        "shell": os.environ.get("SHELL", os.environ.get("COMSPEC", "")),
        "user": os.environ.get("USER", os.environ.get("USERNAME", "")),
        "temp": os.environ.get("TEMP", os.environ.get("TMP", "")),
    }


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
