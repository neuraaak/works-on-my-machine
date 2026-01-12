#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM DETECTOR UTILS - Pure System Detection Functions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Pure system detector utility functions for Works On My Machine.

This module contains stateless utility functions for system detection
operations that can be used independently without class instantiation.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from typing import Any

# Local imports
from ...shared.configs.system import SystemDetectorConfig

# ///////////////////////////////////////////////////////////////
# VERSION PARSING FUNCTIONS
# ///////////////////////////////////////////////////////////////


def extract_version_from_stdout(stdout: str | None, fallback: str = "unknown") -> str:
    """
    Extract version string from command stdout.

    Args:
        stdout: Command stdout string (can be None)
        fallback: Fallback value if stdout is empty or None

    Returns:
        str: Extracted version string or fallback
    """
    if not stdout:
        return fallback

    # Strip whitespace and get first line
    version = stdout.strip()
    if "\n" in version:
        version = version.split("\n")[0]

    return version if version else fallback


def extract_version_first_line(stdout: str | None, fallback: str = "unknown") -> str:
    """
    Extract first line from command stdout (for multi-line output).

    Args:
        stdout: Command stdout string (can be None)
        fallback: Fallback value if stdout is empty or None

    Returns:
        str: First line of stdout or fallback
    """
    if not stdout:
        return fallback

    lines = stdout.strip().split("\n")
    return lines[0] if lines else fallback


# ///////////////////////////////////////////////////////////////
# PACKAGE MANAGER STRUCTURE FUNCTIONS
# ///////////////////////////////////////////////////////////////


def create_package_manager_entry(
    _name: str,
    version: str,
    metadata: dict[str, str | int],
    available: bool = True,
) -> dict[str, str | bool | None]:
    """
    Create a standardized package manager entry dictionary.

    Args:
        name: Package manager name (e.g., "chocolatey")
        version: Package manager version string
        metadata: Metadata dict from SystemDetectorConfig (command, description, etc.)
        available: Whether the package manager is available

    Returns:
        Dict[str, str | bool | None]: Standardized package manager entry
    """
    return {
        "available": available,
        "version": version if version else None,
        "command": metadata.get("command", ""),
        "description": metadata.get("description", ""),
        "install_cmd": metadata.get("install_cmd", ""),
        "priority": metadata.get("priority", 999),
    }


def get_package_manager_metadata(
    platform: str, manager_name: str
) -> dict[str, str | int] | None:
    """
    Get package manager metadata from config based on platform.

    Args:
        platform: Platform name ("Windows", "Darwin", "Linux")
        manager_name: Package manager name (e.g., "chocolatey")

    Returns:
        Optional[Dict[str, str | int]]: Metadata dict or None if not found
    """
    if platform == "Windows":
        return SystemDetectorConfig.get_windows_package_managers().get(manager_name)
    elif platform == "Darwin":
        return SystemDetectorConfig.get_macos_package_managers().get(manager_name)
    elif platform == "Linux":
        return SystemDetectorConfig.get_linux_package_managers().get(manager_name)

    return None


# ///////////////////////////////////////////////////////////////
# DEVELOPMENT ENVIRONMENT STRUCTURE FUNCTIONS
# ///////////////////////////////////////////////////////////////


def create_editor_entry(
    command: str, name: str, version: str = "unknown"
) -> dict[str, str | bool]:
    """
    Create a standardized editor entry dictionary.

    Args:
        command: Editor command (e.g., "code")
        name: Editor display name (e.g., "Visual Studio Code")
        version: Editor version string

    Returns:
        Dict[str, str | bool]: Standardized editor entry
    """
    return {
        "available": True,
        "name": name,
        "version": version,
        "command": command,
    }


def create_shell_entry(command: str, name: str) -> dict[str, str | bool]:
    """
    Create a standardized shell entry dictionary.

    Args:
        command: Shell command (e.g., "bash")
        name: Shell display name (e.g., "Bash")

    Returns:
        Dict[str, str | bool]: Standardized shell entry
    """
    return {
        "available": True,
        "name": name,
        "command": command,
        "type": "shell",
    }


def get_editor_name(command: str) -> str | None:
    """
    Get editor display name from command.

    Args:
        command: Editor command (e.g., "code")

    Returns:
        Optional[str]: Editor display name or None if not found
    """
    return SystemDetectorConfig.EDITORS.get(command)


def get_shell_name(command: str) -> str | None:
    """
    Get shell display name from command.

    Args:
        command: Shell command (e.g., "bash")

    Returns:
        Optional[str]: Shell display name or None if not found
    """
    return SystemDetectorConfig.SHELLS.get(command)


# ///////////////////////////////////////////////////////////////
# PACKAGE MANAGER SELECTION FUNCTIONS
# ///////////////////////////////////////////////////////////////


def get_best_package_manager(package_managers: dict[str, dict[str, Any]]) -> str | None:
    """
    Get the best available package manager based on priority.

    Args:
        package_managers: Dictionary of package managers with their info

    Returns:
        Optional[str]: Name of the best package manager or None
    """
    available = {
        name: info
        for name, info in package_managers.items()
        if info.get("available", False)
    }

    if not available:
        return None

    # Sort by priority (lower is better)
    sorted_managers = sorted(available.items(), key=lambda x: x[1].get("priority", 999))
    return sorted_managers[0][0]


# ///////////////////////////////////////////////////////////////
# RECOMMENDATION GENERATION FUNCTIONS
# ///////////////////////////////////////////////////////////////


def generate_package_manager_recommendation(
    best_manager: str | None,
    installable_manager: str | None,
) -> str:
    """
    Generate package manager recommendation text.

    Args:
        best_manager: Best available package manager name or None
        installable_manager: Installable package manager name or None

    Returns:
        str: Recommendation text
    """
    if best_manager:
        return SystemDetectorConfig.RECOMMENDATION_TEMPLATES[
            "package_manager_use"
        ].format(manager=best_manager)
    elif installable_manager:
        return SystemDetectorConfig.RECOMMENDATION_TEMPLATES[
            "package_manager_install"
        ].format(manager=installable_manager)
    else:
        return SystemDetectorConfig.RECOMMENDATION_TEMPLATES["package_manager_none"]


def generate_editor_recommendation(dev_environments: dict[str, dict[str, Any]]) -> str:
    """
    Generate editor recommendation text based on detected environments.

    Args:
        dev_environments: Dictionary of detected development environments

    Returns:
        str: Recommendation text
    """
    if "code" in dev_environments:
        return SystemDetectorConfig.RECOMMENDATION_TEMPLATES["editor_vscode"]
    elif any("vim" in env or "nvim" in env for env in dev_environments):
        return SystemDetectorConfig.RECOMMENDATION_TEMPLATES["editor_cli"]
    else:
        return SystemDetectorConfig.RECOMMENDATION_TEMPLATES["editor_install"]


def generate_recommendations(
    _package_managers: dict[str, dict[str, Any]],
    dev_environments: dict[str, dict[str, Any]],
    best_manager: str | None,
    installable_manager: str | None,
) -> dict[str, str]:
    """
    Generate all recommendations based on detection results.

    Args:
        package_managers: Dictionary of detected package managers
        dev_environments: Dictionary of detected development environments
        best_manager: Best available package manager name or None
        installable_manager: Installable package manager name or None

    Returns:
        Dict[str, str]: Dictionary of recommendations
    """
    return {
        "package_manager": generate_package_manager_recommendation(
            best_manager, installable_manager
        ),
        "editor": generate_editor_recommendation(dev_environments),
    }
