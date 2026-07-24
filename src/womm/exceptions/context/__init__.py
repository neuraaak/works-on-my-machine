#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS CONTEXT - Context Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Context exceptions for Works On My Machine.

This package exports all exceptions for context menu operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .context_interface import (
    ContextInterfaceError,
    IconInterfaceError,
    MenuInterfaceError,
    RegistryInterfaceError,
    ScriptDetectorInterfaceError,
    ValidationInterfaceError,
)
from .context_service import (
    ContextServiceError,
    ContextUtilityError,
    IconServiceError,
    MenuServiceError,
    ScriptDetectorServiceError,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [  # noqa: RUF022
    # context_interface
    "ContextInterfaceError",
    "IconInterfaceError",
    "MenuInterfaceError",
    "RegistryInterfaceError",
    "ScriptDetectorInterfaceError",
    "ValidationInterfaceError",
    # context_service
    "ContextServiceError",
    "ContextUtilityError",
    "IconServiceError",
    "MenuServiceError",
    "ScriptDetectorServiceError",
]
