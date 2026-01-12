#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PACKAGE MANAGER COMMANDS CONFIG
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Package manager install commands configuration.

Defines installation command templates and installation instructions
for various system package managers across platforms.
"""

from __future__ import annotations

from typing import ClassVar

# ///////////////////////////////////////////////////////////////
# PACKAGE MANAGER INSTALL COMMANDS
# ///////////////////////////////////////////////////////////////


class SystemPackageManagerConfig:
    """Configuration for package manager installation commands."""

    # ///////////////////////////////////////////////////////////
    # SYSTEM PACKAGE MANAGERS DEFINITIONS
    # ///////////////////////////////////////////////////////////

    SYSTEM_PACKAGE_MANAGERS: ClassVar[dict[str, dict[str, str | int]]] = {
        "winget": {
            "platform": "windows",
            "command": "winget",
            "priority": 1,
        },
        "chocolatey": {
            "platform": "windows",
            "command": "choco",
            "priority": 2,
        },
        "scoop": {
            "platform": "windows",
            "command": "scoop",
            "priority": 3,
        },
        "homebrew": {
            "platform": "darwin",
            "command": "brew",
            "priority": 1,
        },
        "apt": {
            "platform": "linux",
            "command": "apt",
            "priority": 1,
        },
        "dnf": {
            "platform": "linux",
            "command": "dnf",
            "priority": 2,
        },
        "pacman": {
            "platform": "linux",
            "command": "pacman",
            "priority": 3,
        },
        "zypper": {
            "platform": "linux",
            "command": "zypper",
            "priority": 4,
        },
    }

    # ///////////////////////////////////////////////////////////
    # INSTALL COMMAND TEMPLATES
    # ///////////////////////////////////////////////////////////

    INSTALL_COMMANDS: ClassVar[dict[str, list[str]]] = {
        "winget": ["winget", "install", "{package_name}", "--accept-source-agreements"],
        "chocolatey": ["choco", "install", "{package_name}", "-y"],
        "scoop": ["scoop", "install", "{package_name}"],
        "homebrew": ["brew", "install", "{package_name}"],
        "apt": [
            "sudo",
            "apt",
            "update",
            "&&",
            "sudo",
            "apt",
            "install",
            "-y",
            "{package_name}",
        ],
        "dnf": ["sudo", "dnf", "install", "-y", "{package_name}"],
        "pacman": ["sudo", "pacman", "-S", "--noconfirm", "{package_name}"],
        "zypper": ["sudo", "zypper", "install", "-y", "{package_name}"],
    }

    # ///////////////////////////////////////////////////////////
    # INSTALLATION INSTRUCTIONS (FOR UI)
    # ///////////////////////////////////////////////////////////

    INSTALLATION_INSTRUCTIONS: ClassVar[dict[str, dict[str, list[str]]]] = {
        "windows": {
            "header": [
                "Aucun gestionnaire de paquets détecté.",
                "Recommandé:",
            ],
            "body": [
                "- winget (Microsoft Store): ouvrez le Microsoft Store et installez 'App Installer'.",
                "- Chocolatey: PowerShell (Run as Administrator):",
                "  Set-ExecutionPolicy Bypass -Scope Process -Force;",
                "  [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12;",
                "  iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))",
                "- Scoop: PowerShell (Run as Administrator):",
                "  iwr -useb get.scoop.sh | iex",
            ],
        },
        "darwin": {
            "header": [
                "Aucun gestionnaire de paquets détecté.",
                "Installez Homebrew:",
            ],
            "body": [
                "- Ouvrez le Terminal puis exécutez:",
                '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
            ],
        },
        "linux": {
            "header": [
                "Aucun gestionnaire de paquets détecté.",
            ],
            "body": [
                "Vérifiez votre distribution Linux et assurez-vous que l'outil par défaut est installé et accessible dans le PATH.",
            ],
        },
    }

    # ///////////////////////////////////////////////////////////
    # HELPER METHODS
    # ///////////////////////////////////////////////////////////

    @classmethod
    def get_install_command(cls, manager_name: str, package_name: str) -> list[str]:
        """Get install command for a package manager.

        Args:
            manager_name: Name of the package manager
            package_name: Name of the package to install

        Returns:
            List of command tokens

        Raises:
            KeyError: If manager not found
        """
        if manager_name not in cls.INSTALL_COMMANDS:
            raise KeyError(f"Unknown package manager: {manager_name}")

        template = cls.INSTALL_COMMANDS[manager_name]
        return [token.replace("{package_name}", package_name) for token in template]

    @classmethod
    def get_installation_instructions(cls, platform: str) -> dict[str, list[str]]:
        """Get installation instructions for a platform.

        Args:
            platform: Platform name (windows, darwin, linux)

        Returns:
            Dictionary with header and body instruction lists

        Raises:
            KeyError: If platform not found
        """
        if platform not in cls.INSTALLATION_INSTRUCTIONS:
            raise KeyError(f"Unknown platform: {platform}")

        return cls.INSTALLATION_INSTRUCTIONS[platform]


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["SystemPackageManagerConfig"]
