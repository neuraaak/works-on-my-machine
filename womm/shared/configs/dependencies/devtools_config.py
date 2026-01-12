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
            "formatting": ["black", "isort"],
            "linting": ["ruff", "flake8"],
            "security": ["bandit"],
            "testing": ["pytest"],
            "type_checking": ["mypy"],
        },
        "javascript": {
            "formatting": ["prettier"],
            "linting": ["eslint"],
            "testing": ["jest"],
            "bundling": ["webpack", "vite"],
        },
        "universal": {
            "spell_checking": ["cspell"],
            "git_hooks": ["pre-commit"],
        },
    }

    # Default runtime_package_manager for each language
    DEFAULT_RUNTIME_PACKAGE_MANAGER: ClassVar[dict[str, str]] = {
        "python": "pip",
        "javascript": "npm",
        "universal": "auto",  # Auto-detect based on tool
    }

    # Special tool configurations
    TOOL_CONFIGS: ClassVar[dict[str, dict[str, str | list[str]]]] = {
        "cspell": {
            "check_method": "npx",  # Can be checked via npx
            "runtime_package_manager": "npm",
            "check_commands": [
                "cspell",  # Direct command in PATH
                ["npx", "cspell"],  # Via npx (npm local or global fallback)
            ],
            "version_flag": "--version",
            "install_global": "npm install -g cspell",
        },
        "pre-commit": {
            "check_method": "standard",
            "runtime_package_manager": "pip",
            "check_commands": ["pre-commit"],
            "version_flag": "--version",
        },
    }


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["DevToolsConfig"]
