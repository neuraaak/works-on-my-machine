#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS SYSTEM - System Service Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
System service exceptions for Works On My Machine.

This package exports all exceptions for system operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .system_interface import (
    SystemInterfaceError,
    UserPathInterfaceError,
)
from .system_service import (
    DetectorServiceError,
    EnvironmentServiceError,
    FileSystemServiceError,
    RegistryServiceError,
    SystemServiceError,
    UserPathServiceError,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [  # noqa: RUF022
    # system_interface
    "UserPathInterfaceError",
    "SystemInterfaceError",
    # system_service
    "DetectorServiceError",
    "EnvironmentServiceError",
    "FileSystemServiceError",
    "RegistryServiceError",
    "SystemServiceError",
    "UserPathServiceError",
]
