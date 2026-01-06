#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS FILE - File Scanning Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
File scanning exceptions for Works On My Machine.

This package contains custom exceptions used specifically by file scanning modules:
- File utilities (womm/core/utils/file_scanner.py)

Following a pragmatic approach with focused exception types:
1. FileUtilityError - Base exception for file utilities
2. FileScanError - File scanning errors
3. FileAccessError - File access errors
4. SecurityFilterError - Security filtering errors
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .file_exceptions import (
    FileAccessError,
    FileScanError,
    FileUtilityError,
    SecurityFilterError,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Base exception
    "FileUtilityError",
    # File scanning exceptions
    "FileScanError",
    # File access exceptions
    "FileAccessError",
    # Security filtering exceptions
    "SecurityFilterError",
]
