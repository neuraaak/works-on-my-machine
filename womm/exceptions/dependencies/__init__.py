#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS DEPENDENCIES - Dependencies Service Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Dependencies service exceptions for Works On My Machine.

This package exports all exceptions for dependency management operations.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .dependencies_interface import (
    DependenciesInterfaceError,
    DevToolsInterfaceError,
    PackageManagerInterfaceError,
    RuntimeManagerInterfaceError,
)
from .dependencies_service import (
    DependenciesServiceError,
    DevToolsServiceError,
    PackageManagerServiceError,
    RuntimeManagerServiceError,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [  # noqa: RUF022
    # dependencies_interface
    "DependenciesInterfaceError",
    "DevToolsInterfaceError",
    "PackageManagerInterfaceError",
    "RuntimeManagerInterfaceError",
    # dependencies_service
    "DependenciesServiceError",
    "DevToolsServiceError",
    "PackageManagerServiceError",
    "RuntimeManagerServiceError",
]
