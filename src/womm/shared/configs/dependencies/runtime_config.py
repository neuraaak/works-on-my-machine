#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# RUNTIME CONFIG - Runtime Configuration
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Runtime configuration for Works On My Machine.

Defines runtime dependencies (Python, Node.js, Git) and their package manager mappings.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from typing import ClassVar

# ///////////////////////////////////////////////////////////////
# RUNTIME DEFINITIONS
# ///////////////////////////////////////////////////////////////


class RuntimeConfig:
    """Configuration for runtime dependencies."""

    RUNTIMES: ClassVar[dict[str, dict[str, str | int | list[str] | dict[str, str]]]] = {
        "python": {
            "version": "3.10+",
            "priority": 1,
            "package_managers": [
                "winget",
                "chocolatey",
                "homebrew",
                "apt",
                "dnf",
                "pacman",
            ],
            "package_names": {
                "winget": "Python.Python.3.11",
                "chocolatey": "python",
                "homebrew": "python@3.11",
                "apt": "python3",
                "dnf": "python3",
                "pacman": "python",
            },
        },
        "node": {
            "version": "18+",
            "priority": 2,
            "package_managers": [
                "winget",
                "chocolatey",
                "homebrew",
                "apt",
                "dnf",
                "pacman",
            ],
            "package_names": {
                "winget": "OpenJS.NodeJS",
                "chocolatey": "nodejs",
                "homebrew": "node",
                "apt": "nodejs",
                "dnf": "nodejs",
                "pacman": "nodejs",
            },
        },
        "git": {
            "version": "2.30+",
            "priority": 3,
            "package_managers": [
                "winget",
                "chocolatey",
                "homebrew",
                "apt",
                "dnf",
                "pacman",
            ],
            "package_names": {
                "winget": "Git.Git",
                "chocolatey": "git",
                "homebrew": "git",
                "apt": "git",
                "dnf": "git",
                "pacman": "git",
            },
        },
    }
