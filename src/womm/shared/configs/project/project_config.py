#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT CONFIG - Project Detection Configuration
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Configuration for project detection and validation.

This config class exposes constants used by project services:
- Project type indicators (files, directories, extensions)
- Reserved names for Windows
- Invalid characters for project names
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
class ProjectConfig:
    """Project detection and validation configuration (static, read-only)."""

    # ///////////////////////////////////////////////////////////
    # PROJECT TYPE INDICATORS
    # ///////////////////////////////////////////////////////////

    PROJECT_INDICATORS: ClassVar[dict[str, dict[str, list[str]]]] = {
        "python": {
            "files": ["setup.py", "pyproject.toml", "requirements.txt", "Pipfile"],
            "dirs": ["__pycache__", ".pytest_cache", ".mypy_cache"],
            "extensions": [".py", ".pyi"],
        },
        "javascript": {
            "files": ["package.json", "yarn.lock", "pnpm-lock.yaml"],
            "dirs": ["node_modules", ".next", ".nuxt"],
            "extensions": [".js", ".jsx", ".ts", ".tsx"],
        },
        "java": {
            "files": ["pom.xml", "build.gradle", "gradle.properties"],
            "dirs": ["target", "build", ".gradle"],
            "extensions": [".java", ".kt"],
        },
        "go": {
            "files": ["go.mod", "go.sum", "Gopkg.toml"],
            "dirs": ["vendor", "bin"],
            "extensions": [".go"],
        },
        "rust": {
            "files": ["Cargo.toml", "Cargo.lock"],
            "dirs": ["target", ".cargo"],
            "extensions": [".rs"],
        },
        "csharp": {
            "files": ["*.csproj", "*.sln", "packages.config"],
            "dirs": ["bin", "obj", "packages"],
            "extensions": [".cs", ".csx"],
        },
    }

    # ///////////////////////////////////////////////////////////
    # VALIDATION CONSTANTS
    # ///////////////////////////////////////////////////////////

    INVALID_CHARS: ClassVar[str] = r'[<>:"/\\|?*]'

    RESERVED_NAMES: ClassVar[set[str]] = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    }

    MAX_PROJECT_NAME_LENGTH: ClassVar[int] = 50

    SUPPORTED_PROJECT_TYPES: ClassVar[list[str]] = [
        "python",
        "javascript",
        "react",
        "vue",
    ]

    # ///////////////////////////////////////////////////////////
    # UI DISPLAY CONFIGURATION
    # ///////////////////////////////////////////////////////////

    # Project type descriptions for UI (with emojis)
    PROJECT_TYPE_DESCRIPTIONS: ClassVar[dict[str, str]] = {
        "python": "🐍 Python project with virtual environment and development tools",
        "javascript": "🟨 JavaScript/Node.js project with npm and development tools",
        "react": "⚛️ React.js project with modern development setup",
        "vue": "💚 Vue.js project with modern development setup",
    }

    @classmethod
    def get_project_types_for_ui(cls) -> list[tuple[str, str]]:
        """Get list of project types with descriptions for UI display.

        Returns:
            List of tuples (project_type, description) ordered by SUPPORTED_PROJECT_TYPES
        """
        return [
            (ptype, cls.PROJECT_TYPE_DESCRIPTIONS.get(ptype, ptype))
            for ptype in cls.SUPPORTED_PROJECT_TYPES
        ]


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["ProjectConfig"]
