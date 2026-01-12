#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS SYSTEM - System Service Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
System service exceptions for Works On My Machine.

This package exports all exceptions for system operations.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .system_interface import (
    DetectorInterfaceError,
    EnvironmentInterfaceError,
    SystemInterfaceError,
    UserPathInterfaceError,
)
from .system_service import (
    DevEnvDetectionServiceError,
    EnvironmentServiceError,
    FileSystemServiceError,
    InfoServiceError,
    PkgManagerDetectionServiceError,
    RegistryServiceError,
    ReportGenerationServiceError,
    SystemDetectionServiceError,
    SystemServiceError,
    UserPathServiceError,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [  # noqa: RUF022
    # system_interface
    "EnvironmentInterfaceError",
    "EnvironmentInterfaceError",
    "UserPathInterfaceError",
    "DetectorInterfaceError",
    "SystemInterfaceError",
    # system_service
    "DevEnvDetectionServiceError",
    "EnvironmentServiceError",
    "FileSystemServiceError",
    "PkgManagerDetectionServiceError",
    "RegistryServiceError",
    "ReportGenerationServiceError",
    "SystemDetectionServiceError",
    "InfoServiceError",
    "SystemServiceError",
    "UserPathServiceError",
]
