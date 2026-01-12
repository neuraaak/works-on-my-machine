#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PACKAGE MANAGER UTILS - Pure Package Manager Functions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Pure utility functions for package manager operations.

This module provides stateless functions for:
- Package manager selection
- Version extraction
- Command building
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import re
from typing import Any

# ///////////////////////////////////////////////////////////////
# VERSION EXTRACTION FUNCTIONS
# ///////////////////////////////////////////////////////////////


def extract_version_from_output(output: str) -> str | None:
    """
    Extract version from command output.

    Args:
        output: Command output string

    Returns:
        str | None: Extracted version or None
    """
    if not output:
        return None

    # Try to find version pattern (e.g., "1.2.3", "v1.2.3", "version 1.2.3")
    patterns = [
        r"v?(\d+\.\d+\.\d+)",  # v1.2.3 or 1.2.3
        r"version\s+(\d+\.\d+)",  # version 1.2
        r"(\d+\.\d+)",  # 1.2
    ]

    for pattern in patterns:
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def extract_first_line_version(output: str) -> str | None:
    """
    Extract version from first line of output.

    Args:
        output: Command output string

    Returns:
        str | None: Extracted version or None
    """
    if not output:
        return None

    first_line = output.split("\n")[0].strip()
    return extract_version_from_output(first_line)


# ///////////////////////////////////////////////////////////////
# COMMAND BUILDING FUNCTIONS
# ///////////////////////////////////////////////////////////////


def build_install_command(
    manager_name: str,
    package_name: str,
    extra_args: list[str] | None = None,
    config: dict[str, Any] | None = None,
) -> list[str]:
    """
    Build install command for a package manager.

    Args:
        manager_name: Name of the package manager
        package_name: Name of the package to install
        extra_args: Additional arguments
        config: Package manager configuration

    Returns:
        list[str]: Command as list of strings
    """
    if config:
        install_cmd = config.get("install_command", f"{manager_name} install")
    else:
        install_cmd = f"{manager_name} install"

    command = [*install_cmd.split(), package_name]

    if extra_args:
        command.extend(extra_args)

    return command


def build_search_command(
    manager_name: str,
    package_name: str,
    config: dict[str, Any] | None = None,
) -> list[str]:
    """
    Build search command for a package manager.

    Args:
        manager_name: Name of the package manager
        package_name: Name of the package to search
        config: Package manager configuration

    Returns:
        list[str]: Command as list of strings
    """
    if config:
        search_cmd = config.get("search_command", f"{manager_name} search")
    else:
        search_cmd = f"{manager_name} search"

    return [*search_cmd.split(), package_name]


# ///////////////////////////////////////////////////////////////
# SELECTION FUNCTIONS
# ///////////////////////////////////////////////////////////////


def select_best_manager(
    available_managers: list[tuple[str, dict[str, Any]]],
) -> str | None:
    """
    Select the best package manager from available ones based on priority.

    Args:
        available_managers: List of (manager_name, config) tuples

    Returns:
        str | None: Name of best manager or None
    """
    if not available_managers:
        return None

    # Sort by priority (lower is better)
    sorted_managers = sorted(
        available_managers, key=lambda x: x[1].get("priority", 999)
    )

    return sorted_managers[0][0]
