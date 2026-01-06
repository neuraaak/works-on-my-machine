#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS SYSTEM - System Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
System exceptions for Works On My Machine.

This package contains custom exceptions used specifically by system management modules:
- PathManager (womm/core/managers/system/user_path_manager.py)
- User path utilities (womm/core/utils/system/user_path_utils.py)
- SystemDetector (womm/core/utils/system/system_detector.py)

Following a pragmatic approach with specialized exception hierarchy:
- UserPathError: Base exception for all user path operations
- RegistryError: Registry-specific errors (Windows only)
- FileSystemError: File system errors (Unix RC files)
- SystemDetectionError: Base exception for all system detection operations
- PackageManagerDetectionError: Package manager detection errors
- DevelopmentEnvironmentDetectionError: Development environment detection errors
- SystemInfoError: System information gathering errors
- ReportGenerationError: Report generation and export errors
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .system_exceptions import (
    DevelopmentEnvironmentDetectionError,
    EnvironmentRefreshError,
    PackageManagerDetectionError,
    ReportGenerationError,
    SystemDetectionError,
    SystemInfoError,
)
from .user_path_exceptions import FileSystemError, RegistryError, UserPathError

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # User path exceptions
    "UserPathError",
    "RegistryError",
    "FileSystemError",
    # System detection exceptions
    "SystemDetectionError",
    "PackageManagerDetectionError",
    "DevelopmentEnvironmentDetectionError",
    "SystemInfoError",
    "ReportGenerationError",
    # Environment refresh exceptions
    "EnvironmentRefreshError",
]
