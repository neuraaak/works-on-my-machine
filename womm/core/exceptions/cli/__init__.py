#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS CLI - CLI Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
CLI exceptions for Works On My Machine.

This package contains custom exceptions used specifically by CLI modules:
- CLI utilities (womm/core/utils/cli_utils.py)

Following a pragmatic approach with focused exception types:
1. CLIUtilityError - Base exception for CLI utilities
2. CommandExecutionError - Command execution errors
3. CommandValidationError - Command validation errors
4. TimeoutError - Command timeout errors
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .cli_exceptions import (
    CLIUtilityError,
    CommandExecutionError,
    CommandValidationError,
    TimeoutError,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Base exception
    "CLIUtilityError",
    # Command execution exceptions
    "CommandExecutionError",
    # Command validation exceptions
    "CommandValidationError",
    # Timeout exceptions
    "TimeoutError",
]
