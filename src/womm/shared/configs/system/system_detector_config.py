#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM DETECTOR CONFIG - System Detector Configuration
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Centralized system detector configuration for Works On My Machine.

This config class exposes constants used by system detection utilities and services:
- Package manager metadata
- Development environment definitions
- Editor and shell definitions
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass
from typing import ClassVar

# ///////////////////////////////////////////////////////////////
# PACKAGE MANAGER CONFIG CLASS
# ///////////////////////////////////////////////////////////////


class PackageManagerConfig:
    """Configuration for system package managers (unified cross-platform).

    This class provides a unified view of all system package managers
    with platform, priority, and command information.
    """

    SYSTEM_PACKAGE_MANAGERS: ClassVar[dict[str, dict[str, str | int]]] = {
        # Windows package managers
        "winget": {
            "platform": "windows",
            "command": "winget",
            "version_flag": "--version",
            "priority": 1,
            "description": "Microsoft Windows Package Manager",
            "install_command": "winget install",
            "search_command": "winget search",
            "list_command": "winget list",
        },
        "chocolatey": {
            "platform": "windows",
            "command": "choco",
            "version_flag": "--version",
            "priority": 2,
            "description": "Chocolatey Package Manager",
            "install_command": "choco install",
            "search_command": "choco search",
            "list_command": "choco list",
        },
        "scoop": {
            "platform": "windows",
            "command": "scoop",
            "version_flag": "--version",
            "priority": 3,
            "description": "Scoop Package Manager",
            "install_command": "scoop install",
            "search_command": "scoop search",
            "list_command": "scoop list",
        },
        # macOS package managers
        "homebrew": {
            "platform": "darwin",
            "command": "brew",
            "version_flag": "--version",
            "priority": 1,
            "description": "Homebrew Package Manager",
            "install_command": "brew install",
            "search_command": "brew search",
            "list_command": "brew list",
        },
        "macports": {
            "platform": "darwin",
            "command": "port",
            "version_flag": "version",
            "priority": 2,
            "description": "MacPorts Package Manager",
            "install_command": "sudo port install",
            "search_command": "port search",
            "list_command": "port installed",
        },
        # Linux package managers
        "apt": {
            "platform": "linux",
            "command": "apt",
            "version_flag": "--version",
            "priority": 1,
            "description": "Advanced Package Tool (Debian/Ubuntu)",
            "install_command": "sudo apt install",
            "search_command": "apt search",
            "list_command": "apt list --installed",
        },
        "dnf": {
            "platform": "linux",
            "command": "dnf",
            "version_flag": "--version",
            "priority": 2,
            "description": "Dandified YUM (Fedora/RHEL)",
            "install_command": "sudo dnf install",
            "search_command": "dnf search",
            "list_command": "dnf list installed",
        },
        "yum": {
            "platform": "linux",
            "command": "yum",
            "version_flag": "--version",
            "priority": 3,
            "description": "Yellowdog Updater Modified (CentOS/RHEL)",
            "install_command": "sudo yum install",
            "search_command": "yum search",
            "list_command": "yum list installed",
        },
        "pacman": {
            "platform": "linux",
            "command": "pacman",
            "version_flag": "--version",
            "priority": 2,
            "description": "Pacman Package Manager (Arch Linux)",
            "install_command": "sudo pacman -S",
            "search_command": "pacman -Ss",
            "list_command": "pacman -Q",
        },
        "zypper": {
            "platform": "linux",
            "command": "zypper",
            "version_flag": "--version",
            "priority": 4,
            "description": "Zypper Package Manager (openSUSE)",
            "install_command": "sudo zypper install",
            "search_command": "zypper search",
            "list_command": "zypper packages --installed",
        },
        "snap": {
            "platform": "linux",
            "command": "snap",
            "version_flag": "--version",
            "priority": 5,
            "description": "Snap Package Manager (Universal)",
            "install_command": "sudo snap install",
            "search_command": "snap find",
            "list_command": "snap list",
        },
    }

    @classmethod
    def get_by_platform(cls, platform: str) -> dict[str, dict[str, str | int]]:
        """Get package managers for a specific platform.

        Args:
            platform: Platform name (windows, darwin, linux)

        Returns:
            Dictionary of package managers for the platform
        """
        return {
            name: config
            for name, config in cls.SYSTEM_PACKAGE_MANAGERS.items()
            if config.get("platform") == platform
        }

    @classmethod
    def get_windows_managers(cls) -> dict[str, dict[str, str | int]]:
        """Get Windows package managers."""
        return cls.get_by_platform("windows")

    @classmethod
    def get_macos_managers(cls) -> dict[str, dict[str, str | int]]:
        """Get macOS package managers."""
        return cls.get_by_platform("darwin")

    @classmethod
    def get_linux_managers(cls) -> dict[str, dict[str, str | int]]:
        """Get Linux package managers."""
        return cls.get_by_platform("linux")


# ///////////////////////////////////////////////////////////////
# SYSTEM DETECTOR CONFIG CLASS
# ///////////////////////////////////////////////////////////////


@dataclass(frozen=True)
class SystemDetectorConfig:
    """System detector configuration (static, read-only).

    Provides editor, shell, and platform-specific package manager metadata
    for system detection operations.
    """

    # ///////////////////////////////////////////////////////////
    # EDITOR DEFINITIONS
    # ///////////////////////////////////////////////////////////

    EDITORS: ClassVar[dict[str, str]] = {
        "code": "Visual Studio Code",
        "code-insiders": "VS Code Insiders",
        "subl": "Sublime Text",
        "atom": "Atom",
        "vim": "Vim",
        "nvim": "Neovim",
        "emacs": "Emacs",
        "nano": "Nano",
    }

    # ///////////////////////////////////////////////////////////
    # SHELL DEFINITIONS
    # ///////////////////////////////////////////////////////////

    SHELLS: ClassVar[dict[str, str]] = {
        "bash": "Bash",
        "zsh": "Zsh",
        "fish": "Fish",
        "powershell": "PowerShell",
        "pwsh": "PowerShell Core",
    }

    # ///////////////////////////////////////////////////////////
    # PLATFORM-SPECIFIC PACKAGE MANAGER VIEWS
    # (Convenience accessors using PackageManagerConfig)
    # ///////////////////////////////////////////////////////////

    @classmethod
    def get_windows_package_managers(cls) -> dict[str, dict[str, str | int]]:
        """Get Windows package managers."""
        return PackageManagerConfig.get_windows_managers()

    @classmethod
    def get_macos_package_managers(cls) -> dict[str, dict[str, str | int]]:
        """Get macOS package managers."""
        return PackageManagerConfig.get_macos_managers()

    @classmethod
    def get_linux_package_managers(cls) -> dict[str, dict[str, str | int]]:
        """Get Linux package managers."""
        return PackageManagerConfig.get_linux_managers()

    # ///////////////////////////////////////////////////////////
    # RECOMMENDATION TEMPLATES
    # ///////////////////////////////////////////////////////////

    RECOMMENDATION_TEMPLATES: ClassVar[dict[str, str]] = {
        "package_manager_use": "Use {manager} for installations",
        "package_manager_install": "Install {manager} to facilitate installations",
        "package_manager_none": "No package manager detected - manual installation required",
        "editor_vscode": "VS Code detected - excellent choice for dev-tools",
        "editor_cli": "Command line editor detected - dev-tools compatible",
        "editor_install": "Install VS Code recommended for better integration",
    }


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["PackageManagerConfig", "SystemDetectorConfig"]
