#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS COMMON - Common Service Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Common service exceptions for Works On My Machine.

This package exports all exceptions for common services:
- Command/CLI service exceptions
- File service exceptions
- Security service exceptions
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .command_service import (
    CommandExecutionError,
    CommandServiceError,
    CommandUtilityError,
    TimeoutError,
)
from .file_service import (
    DirectoryAccessError,
    FileAccessError,
    FileScanError,
    FileServiceError,
    FileValidationError,
    SecurityFilterError,
)
from .security_service import (
    CommandValidationError,
    PathValidationError,
    SecurityServiceError,
)
from .validation_service import ValidationServiceError

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [  # noqa: RUF022
    # command_service
    "CommandExecutionError",
    "CommandServiceError",
    "CommandUtilityError",
    "TimeoutError",
    # file_service
    "DirectoryAccessError",
    "FileAccessError",
    "FileScanError",
    "FileServiceError",
    "FileValidationError",
    "SecurityFilterError",
    # security_service
    "CommandValidationError",
    "PathValidationError",
    "SecurityServiceError",
    # validation_service
    "ValidationServiceError",
]
