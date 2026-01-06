#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS SECURITY - Security Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Security exceptions for Works On My Machine.

This package contains custom exceptions used specifically by security modules:
- SecurityValidator (womm/core/utils/security/security_validator.py)

Following a pragmatic approach with focused exception types:
1. SecurityUtilityError - Base exception for security utilities
2. ValidationError - Security validation errors
3. CommandValidationError - Command validation errors
4. PathValidationError - Path validation errors
5. FileValidationError - File validation errors
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .security_exceptions import (
    CommandValidationError,
    FileValidationError,
    PathValidationError,
    SecurityUtilityError,
    ValidationError,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Base exception
    "SecurityUtilityError",
    # Validation exceptions
    "ValidationError",
    "CommandValidationError",
    "PathValidationError",
    "FileValidationError",
]
