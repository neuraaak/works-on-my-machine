#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEV TOOLS CONFIG - Development Tools Configuration
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Development tools configuration for Works On My Machine.

Defines devtools_dependencies (Strata 3) and their installation methods.

For complete dependency chains (devtools_dependencies → runtime_package_manager → runtime),
see dependency_hierarchy.py
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from typing import ClassVar

# ///////////////////////////////////////////////////////////////
# DEVELOPMENT TOOLS DEFINITIONS
# ///////////////////////////////////////////////////////////////


class DevToolsConfig:
    """
    Configuration for devtools_dependencies (Strata 3).

    These tools depend on:
    - runtime_package_manager (Strata 2b): pip, uv, npm, yarn
    - runtime (Strata 2a): python, node, git

    See DependencyHierarchy for explicit dependency mappings.
    """

    DEVTOOLS_DEPENDENCIES: ClassVar[dict[str, dict[str, list[str]]]] = {
        "python": {
            # ruff covers formatting, import sorting and linting on its own:
            # black / isort / flake8 were dropped on 2026-08-02.
            "linting": ["ruff"],
            "security": ["bandit"],
            "testing": ["pytest"],
        },
        "javascript": {
            "formatting": ["prettier"],
            "linting": ["eslint"],
            "testing": ["jest"],
            "bundling": ["webpack", "vite"],
        },
        "universal": {
            "git_hooks": ["pre-commit"],
        },
    }

    # Default runtime_package_manager for each language
    DEFAULT_RUNTIME_PACKAGE_MANAGER: ClassVar[dict[str, str]] = {
        "python": "pip",
        "javascript": "npm",
        "universal": "auto",  # Auto-detect based on tool
    }


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["DevToolsConfig"]
