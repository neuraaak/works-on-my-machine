#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM ENVIRONMENT CONFIG - System Environment Configuration
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Centralized system environment configuration for Works On My Machine.

This config class exposes constants used by system environment utilities and services:
- Refresh script paths
- Timeouts
- Shell configuration files
- Verification settings
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

# ///////////////////////////////////////////////////////////////
# CLASS DEFINITION
# ///////////////////////////////////////////////////////////////


@dataclass(frozen=True)
class SystemEnvironmentConfig:
    """System environment-related configuration (static, read-only)."""

    # ///////////////////////////////////////////////////////////
    # REFRESH SCRIPT PATHS
    # ///////////////////////////////////////////////////////////

    REFRESH_ENV_SCRIPT_NAME: ClassVar[str] = "refresh_env.cmd"
    REFRESH_ENV_SCRIPT_RELATIVE_PATH: ClassVar[str] = "bin/refresh_env.cmd"

    # ///////////////////////////////////////////////////////////
    # TIMEOUTS
    # ///////////////////////////////////////////////////////////

    VERIFICATION_TIMEOUT: ClassVar[int] = 30  # seconds
    REFRESH_TIMEOUT: ClassVar[int] = 60  # seconds

    # ///////////////////////////////////////////////////////////
    # SHELL CONFIGURATION FILES
    # ///////////////////////////////////////////////////////////

    UNIX_SHELL_CONFIG_FILES: ClassVar[list[str]] = [
        ".bashrc",
        ".zshrc",
        ".profile",
        ".bash_profile",
        ".zprofile",
    ]

    # ///////////////////////////////////////////////////////////
    # WINDOWS REGISTRY PATHS
    # ///////////////////////////////////////////////////////////

    WINDOWS_HKLM_ENVIRONMENT_PATH: ClassVar[str] = (
        r"System\CurrentControlSet\Control\Session Manager\Environment"
    )
    WINDOWS_HKCU_ENVIRONMENT_PATH: ClassVar[str] = "Environment"

    # ///////////////////////////////////////////////////////////
    # VERIFICATION SETTINGS
    # ///////////////////////////////////////////////////////////

    DEFAULT_VERIFICATION_COMMAND: ClassVar[str] = "womm"
    VERIFICATION_COMMAND_ARGS: ClassVar[list[str]] = ["--version"]

    # ///////////////////////////////////////////////////////////
    # STATIC METHODS
    # ///////////////////////////////////////////////////////////

    @staticmethod
    def get_shell_config_files() -> list[Path]:
        """Get list of shell configuration files for Unix systems.

        Returns:
            List[Path]: List of shell configuration file paths that exist
        """
        home = Path.home()
        config_files = [
            home / config_file
            for config_file in SystemEnvironmentConfig.UNIX_SHELL_CONFIG_FILES
        ]
        return [f for f in config_files if f.exists()]


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["SystemEnvironmentConfig"]
