#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PYTHON LINTING CONFIG - Python Linting Tools Configuration
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Configuration for Python linting tools.

This config class exposes constants used by Python linting services:
- Tool configurations (ruff, black, isort, bandit)
- Check and fix arguments
- JSON support flags
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass
from typing import ClassVar

# ///////////////////////////////////////////////////////////////
# CLASS DEFINITION
# ///////////////////////////////////////////////////////////////


@dataclass(frozen=True)
class PythonLintingConfig:
    """Python linting tools configuration (static, read-only)."""

    # ///////////////////////////////////////////////////////////
    # TOOLS CONFIGURATION
    # ///////////////////////////////////////////////////////////

    TOOLS_CONFIG: ClassVar[dict[str, dict[str, list[str] | bool]]] = {
        "ruff": {
            "check_args": ["check", "--no-fix", "--output-format", "json"],
            "fix_args": ["check", "--fix"],
            "json_support": True,
        },
        "black": {
            "check_args": ["--check", "--diff"],
            "fix_args": [],
            "json_support": False,
        },
        "isort": {
            "check_args": ["--check-only", "--diff"],
            "fix_args": [],
            "json_support": False,
        },
        "bandit": {
            "check_args": ["-r", "-f", "json"],
            "fix_args": [],  # bandit doesn't have fix mode
            "json_support": True,
        },
    }

    # ///////////////////////////////////////////////////////////
    # FIXABLE TOOLS
    # ///////////////////////////////////////////////////////////

    FIXABLE_TOOLS: ClassVar[list[str]] = ["black", "isort"]


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["PythonLintingConfig"]
