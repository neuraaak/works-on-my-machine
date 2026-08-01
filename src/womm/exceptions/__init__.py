#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS - Custom Exceptions by Domain
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Custom exceptions for Works On My Machine.

This package contains all custom exceptions organized by domain.
Import exceptions from the appropriate domain:

    from exceptions.common import CommandServiceError, FileServiceError
    from exceptions.context import ContextServiceError
    from exceptions.project import ProjectServiceError
    from exceptions.system import SystemServiceError

Available domains:
- common: Command, file, and security service exceptions
- context: Context menu service exceptions
- project: Project management exceptions
- system: System management exceptions
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS BY DOMAIN
# ///////////////////////////////////////////////////////////////
# Local imports - Common exceptions
from .common import (
    CommandExecutionError,
    CommandServiceError,
    CommandTimeoutError,
    CommandUtilityError,
    FileServiceError,
    SecurityServiceError,
    ValidationServiceError,
)

# Local imports - Context exceptions
from .context import ContextServiceError

# Local imports - Project exceptions
from .project import ProjectServiceError

# Local imports - System exceptions
from .system import SystemServiceError

# ///////////////////////////////////////////////////////////////
# PUBLIC API - All Exceptions
# ///////////////////////////////////////////////////////////////

__all__ = [  # noqa: RUF022
    # Common exceptions
    "CommandExecutionError",
    "CommandServiceError",
    "CommandUtilityError",
    "FileServiceError",
    "SecurityServiceError",
    "CommandTimeoutError",
    "ValidationServiceError",
    # Context exceptions
    "ContextServiceError",
    # Project exceptions
    "ProjectServiceError",
    # System exceptions
    "SystemServiceError",
]
