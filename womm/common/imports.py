#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# IMPORTS - Import Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Import utilities for Works On My Machine.

This module handles imports for both development and PyPI installation.
Provides utility functions for dynamic module imports and path resolution.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import importlib
from pathlib import Path
from typing import Any

# Local imports
from ..core.exceptions import ImportUtilityError

# ///////////////////////////////////////////////////////////////
# MODULE IMPORT FUNCTIONS
# ///////////////////////////////////////////////////////////////


def import_shared_module(module_name: str) -> Any:
    """Import a module from `shared` directory (strict, no fallback).

    Args:
        module_name: Name of the module to import

    Returns:
        Any: The imported module

    Raises:
        ImportUtilityError: If module import fails
    """
    try:
        return importlib.import_module(f"shared.{module_name}")
    except ImportError as e:
        raise ImportUtilityError(
            module_name=module_name,
            operation="import_shared_module",
            reason="Module not found or import failed",
            details=str(e),
        ) from e
    except Exception as e:
        raise ImportUtilityError(
            module_name=module_name,
            operation="import_shared_module",
            reason="Unexpected error during import",
            details=str(e),
        ) from e


# ///////////////////////////////////////////////////////////////
# PATH RESOLUTION FUNCTIONS
# ///////////////////////////////////////////////////////////////


def get_shared_module_path() -> Path:
    """Get strict path to the project `shared` directory (no fallback).

    Returns:
        Path: Path to the shared module directory

    Raises:
        ImportUtilityError: If path resolution fails
    """
    try:
        return Path(__file__).parent.parent.parent / "shared"
    except Exception as e:
        raise ImportUtilityError(
            module_name="shared",
            operation="get_shared_module_path",
            reason="Failed to resolve shared module path",
            details=str(e),
        ) from e


def get_languages_module_path() -> Path:
    """Get strict path to the `womm/languages` directory (no fallback).

    Returns:
        Path: Path to the languages module directory

    Raises:
        ImportUtilityError: If path resolution fails
    """
    try:
        return Path(__file__).parent.parent / "languages"
    except Exception as e:
        raise ImportUtilityError(
            module_name="languages",
            operation="get_languages_module_path",
            reason="Failed to resolve languages module path",
            details=str(e),
        ) from e


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "import_shared_module",
    "get_shared_module_path",
    "get_languages_module_path",
]
