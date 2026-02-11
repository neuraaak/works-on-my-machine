#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS DEPENDENCIES - Dependencies Service Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Dependencies service exceptions for Works On My Machine.

This package exports all exceptions for dependency management operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .dependencies_interface import (
    DependenciesInterfaceError,
    DevToolsInterfaceError,
    RuntimeInterfaceError,
    SystemPkgManagerInterfaceError,
)
from .dependencies_service import (
    DependenciesServiceError,
    DevToolsServiceError,
    RuntimeServiceError,
    SystemPkgManagerServiceError,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [  # noqa: RUF022
    # dependencies_interface
    "DependenciesInterfaceError",
    "DevToolsInterfaceError",
    "SystemPkgManagerInterfaceError",
    "RuntimeInterfaceError",
    # dependencies_service
    "DependenciesServiceError",
    "DevToolsServiceError",
    "SystemPkgManagerServiceError",
    "RuntimeServiceError",
]
