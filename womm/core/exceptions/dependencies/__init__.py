#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS DEPENDENCIES - Dependencies Management Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Dependencies management exceptions for Works On My Machine.

This package contains custom exceptions used specifically by dependency management modules:
- RuntimeManager (womm/core/managers/dependencies/runtime_manager.py)
- DevToolsManager (womm/core/managers/dependencies/dev_tools_manager.py)
- PackageManager (womm/core/managers/dependencies/package_manager.py)

Following a pragmatic approach with focused exception types:
1. DependenciesUtilityError - Base exception for dependencies utilities
2. RuntimeError - Runtime management errors
3. DevToolsError - Development tools errors
4. PackageManagerError - Package manager errors
5. InstallationError - Installation process errors
6. ValidationError - Validation errors
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .dependencies_exceptions import (
    DependenciesUtilityError,
    DevToolsError,
    InstallationError,
    PackageManagerError,
    RuntimeManagerError,
    ValidationError,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Base exception
    "DependenciesUtilityError",
    # Runtime management exceptions
    "RuntimeManagerError",
    # Development tools exceptions
    "DevToolsError",
    # Package manager exceptions
    "PackageManagerError",
    # Installation exceptions
    "InstallationError",
    # Validation exceptions
    "ValidationError",
]
