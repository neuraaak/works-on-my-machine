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
# Local imports
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

__all__ = [
    "DetectorServiceError",
    "EnvironmentServiceError",
    "FileSystemServiceError",
    "RegistryServiceError",
    "SystemServiceError",
    "UserPathServiceError",
]
