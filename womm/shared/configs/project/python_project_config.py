#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PYTHON PROJECT CONFIG - Python Project Configuration
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Configuration for Python project creation and setup.

This module provides:
- Python-specific directory structures
- Development dependencies
- Default file templates
- Python project conventions
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
class PythonProjectConfig:
    """Python project configuration (static, read-only)."""

    # ///////////////////////////////////////////////////////////
    # DIRECTORY STRUCTURE
    # ///////////////////////////////////////////////////////////

    # Python-specific directories (in addition to common ones)
    PYTHON_DIRECTORIES: ClassVar[list[str]] = []

    # ///////////////////////////////////////////////////////////
    # DEVELOPMENT DEPENDENCIES
    # ///////////////////////////////////////////////////////////

    # Core development dependencies
    DEV_DEPENDENCIES: ClassVar[dict[str, str]] = {
        # Testing
        "pytest": ">=7.0.0",
        "pytest-cov": ">=4.0.0",
        "pytest-mock": ">=3.10.0",
        # Code quality
        "black": ">=23.0.0",
        "flake8": ">=6.0.0",
        "isort": ">=5.12.0",
        "mypy": ">=1.0.0",
        # Pre-commit
        "pre-commit": ">=3.0.0",
        # Documentation
        "sphinx": ">=6.0.0",
        "sphinx-rtd-theme": ">=1.2.0",
    }

    # ///////////////////////////////////////////////////////////
    # FILE TEMPLATES
    # ///////////////////////////////////////////////////////////

    # Requirements file template
    REQUIREMENTS_TEMPLATE: ClassVar[str] = """# Core dependencies
# Add your project dependencies here
# Example:
# requests>=2.28.0
# pandas>=1.5.0
"""

    # Development requirements file template
    DEV_REQUIREMENTS_TEMPLATE: ClassVar[str] = """# Development dependencies
-r requirements.txt

# Testing
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0

# Code quality
black>=23.0.0
flake8>=6.0.0
isort>=5.12.0
mypy>=1.0.0

# Pre-commit
pre-commit>=3.0.0

# Documentation
sphinx>=6.0.0
sphinx-rtd-theme>=1.2.0
"""

    # ///////////////////////////////////////////////////////////
    # FILE NAMES
    # ///////////////////////////////////////////////////////////

    # Requirements file name
    REQUIREMENTS_FILE: ClassVar[str] = "requirements.txt"

    # Development requirements file name
    DEV_REQUIREMENTS_FILE: ClassVar[str] = "requirements-dev.txt"

    # Pyproject file name
    PYPROJECT_FILE: ClassVar[str] = "pyproject.toml"

    # ///////////////////////////////////////////////////////////
    # PYTHON CONVENTIONS
    # ///////////////////////////////////////////////////////////

    # Default Python version
    DEFAULT_PYTHON_VERSION: ClassVar[str] = "3.10"

    # Virtual environment directory name
    VENV_DIR: ClassVar[str] = "venv"

    # Alternative virtual environment directory name
    ALT_VENV_DIR: ClassVar[str] = ".venv"

    # ///////////////////////////////////////////////////////////
    # STATIC METHODS
    # ///////////////////////////////////////////////////////////

    @staticmethod
    def get_dev_requirements_content() -> str:
        """Get the content for requirements-dev.txt.

        Returns:
            str: Formatted development requirements content
        """
        return PythonProjectConfig.DEV_REQUIREMENTS_TEMPLATE

    @staticmethod
    def get_requirements_content() -> str:
        """Get the content for requirements.txt.

        Returns:
            str: Formatted requirements content
        """
        return PythonProjectConfig.REQUIREMENTS_TEMPLATE

    @staticmethod
    def format_dependency(name: str, version: str) -> str:
        """Format a dependency for requirements file.

        Args:
            name: Package name
            version: Version constraint

        Returns:
            str: Formatted dependency line
        """
        return f"{name}{version}"


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["PythonProjectConfig"]
