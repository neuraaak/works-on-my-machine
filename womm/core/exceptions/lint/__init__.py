#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS LINT - Linting Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Linting exceptions for Works On My Machine.

This package contains custom exceptions used specifically by linting modules:
- LintManager (womm/core/managers/lint/lint_manager.py)
- Lint utilities (womm/core/utils/lint/*.py)

Following a pragmatic approach with focused exception types:
1. LintUtilityError - Base exception for linting utilities
2. ToolExecutionError - Tool execution errors
3. ToolAvailabilityError - Tool availability errors
4. LintManagerError - Base exception for lint manager
5. LintValidationError - Lint validation errors
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .lint_exceptions import (
    LintManagerError,
    LintUtilityError,
    LintValidationError,
    ToolAvailabilityError,
    ToolExecutionError,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Base exception
    "LintUtilityError",
    # Tool execution exceptions
    "ToolExecutionError",
    # Tool availability exceptions
    "ToolAvailabilityError",
    # Manager exceptions
    "LintManagerError",
    "LintValidationError",
]
