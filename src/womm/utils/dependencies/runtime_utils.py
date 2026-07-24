#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# RUNTIME MANAGER UTILS - Pure Runtime Manager Functions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Pure utility functions for runtime manager operations.

This module provides stateless functions for:
- Version comparison
- Runtime path resolution
- Package name resolution
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import re
from typing import Any

# ///////////////////////////////////////////////////////////////
# VERSION COMPARISON FUNCTIONS
# ///////////////////////////////////////////////////////////////


def parse_version(version_str: str) -> list[int]:
    """
    Parse version string into list of integers.

    Args:
        version_str: Version string (e.g., "3.11.0", "v18.2.1")

    Returns:
        list[int]: List of version components
    """
    # Remove 'v' prefix if present
    version_str = version_str.lstrip("v")

    # Extract numeric parts
    parts = re.findall(r"\d+", version_str)
    return [int(p) for p in parts]


def compare_versions(version1: str, version2: str) -> int:
    """
    Compare two version strings.

    Args:
        version1: First version string
        version2: Second version string

    Returns:
        int: -1 if version1 < version2, 0 if equal, 1 if version1 > version2
    """
    v1_parts = parse_version(version1)
    v2_parts = parse_version(version2)

    # Pad shorter version with zeros
    max_len = max(len(v1_parts), len(v2_parts))
    v1_parts.extend([0] * (max_len - len(v1_parts)))
    v2_parts.extend([0] * (max_len - len(v2_parts)))

    for v1, v2 in zip(v1_parts, v2_parts, strict=False):
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1

    return 0


def satisfies_min_version(actual: str, min_spec: str) -> bool:
    """
    Check if actual version satisfies minimum version requirement.

    Args:
        actual: Actual version string (e.g., "3.11.0")
        min_spec: Minimum version specification (e.g., "3.9+")

    Returns:
        bool: True if version satisfies requirement
    """
    if not actual or not min_spec:
        return False

    # Remove 'v' prefix and '+' suffix
    actual = actual.lstrip("v")
    min_spec = min_spec.rstrip("+")

    return compare_versions(actual, min_spec) >= 0


# ///////////////////////////////////////////////////////////////
# PACKAGE NAME RESOLUTION FUNCTIONS
# ///////////////////////////////////////////////////////////////


def get_package_name_for_manager(
    _runtime: str, manager_name: str, config: dict[str, Any] | None = None
) -> str | None:
    """
    Get package name for a runtime and package manager.

    Args:
        runtime: Runtime name (python, node, git)
        manager_name: Package manager name
        config: Runtime configuration

    Returns:
        str | None: Package name or None if not found
    """
    if not config:
        return None

    package_names = config.get("package_names", {})
    return package_names.get(manager_name)
