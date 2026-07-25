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

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .command_service import (
    CommandExecutionError,
    CommandServiceError,
    CommandTimeoutError,
    CommandUtilityError,
)
from .file_service import (
    FileServiceError,
)
from .security_service import (
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
    "CommandTimeoutError",
    # file_service
    "FileServiceError",
    # security_service
    "SecurityServiceError",
    # validation_service
    "ValidationServiceError",
]
