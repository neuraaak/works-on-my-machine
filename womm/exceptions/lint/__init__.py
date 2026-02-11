#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS LINT - Lint Service Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Lint service exceptions for Works On My Machine.

This package exports all exceptions for linting operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .lint_interface import LintInterfaceError, PythonLintInterfaceError
from .lint_service import (
    LintServiceError,
    ToolAvailabilityServiceError,
    ToolExecutionServiceError,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [  # noqa: RUF022
    # lint_interface
    "PythonLintInterfaceError",
    "PythonLintInterfaceError",
    "LintInterfaceError",
    "PythonLintInterfaceError",
    "PythonLintInterfaceError",
    # lint_service
    "LintServiceError",
    "ToolAvailabilityServiceError",
    "ToolExecutionServiceError",
]
