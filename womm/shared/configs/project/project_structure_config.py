#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT STRUCTURE CONFIG - Common Project Structure Configuration
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Configuration for common project structure elements.

This module provides:
- Common directory structures
- Standard file patterns
- Shared project organization rules
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
class ProjectStructureConfig:
    """Common project structure configuration (static, read-only)."""

    # ///////////////////////////////////////////////////////////
    # COMMON DIRECTORY STRUCTURE
    # ///////////////////////////////////////////////////////////

    # Standard directories created for all project types
    COMMON_DIRECTORIES: ClassVar[list[str]] = [
        "src",
        "tests",
        "docs",
        "scripts",
        ".vscode",
    ]

    # Source directory name
    SOURCE_DIR: ClassVar[str] = "src"

    # Tests directory name
    TESTS_DIR: ClassVar[str] = "tests"

    # Documentation directory name
    DOCS_DIR: ClassVar[str] = "docs"

    # Scripts directory name
    SCRIPTS_DIR: ClassVar[str] = "scripts"

    # VSCode configuration directory
    VSCODE_DIR: ClassVar[str] = ".vscode"

    # ///////////////////////////////////////////////////////////
    # FILE PATTERNS
    # ///////////////////////////////////////////////////////////

    # Common ignore patterns
    COMMON_IGNORE_PATTERNS: ClassVar[list[str]] = [
        "**/__pycache__",
        "**/*.pyc",
        "**/.pytest_cache",
        "**/node_modules",
        "**/.git",
        "**/.env*",
        "**/.secret*",
        "**/*password*",
        "**/*secret*",
        "**/*.key",
        "**/*.pem",
        "**/*.crt",
        "**/credentials",
    ]


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["ProjectStructureConfig"]
