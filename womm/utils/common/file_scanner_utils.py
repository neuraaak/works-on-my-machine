#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# FILE SCANNER UTILS - Pure File Scanner Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Pure utility functions for file scanning operations.

This module provides stateless functions for:
- Python file detection
- Path exclusion checking
- File extension validation
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path

# Local imports
from ...shared.configs.security import FileScannerConfig

# ///////////////////////////////////////////////////////////////
# FILE DETECTION FUNCTIONS
# ///////////////////////////////////////////////////////////////


def is_python_file(file_path: Path) -> bool:
    """Check if a file is a Python file.

    Args:
        file_path: File path to check

    Returns:
        bool: True if file is a Python file, False otherwise
    """
    try:
        if not file_path.exists():
            return False

        if not file_path.is_file():
            return False

        return file_path.suffix.lower() in FileScannerConfig.PYTHON_EXTENSIONS

    except Exception:
        # Return False on any error - this is a pure utility function
        return False


# ///////////////////////////////////////////////////////////////
# PATH EXCLUSION FUNCTIONS
# ///////////////////////////////////////////////////////////////


def should_exclude_path(path: Path) -> bool:
    """Check if a path should be excluded from scanning.

    Args:
        path: Path to check

    Returns:
        bool: True if path should be excluded, False otherwise
    """
    try:
        # Check if any part of the path matches excluded patterns
        return any(part in FileScannerConfig.EXCLUDED_DIRS for part in path.parts)
    except Exception:
        # Exclude on error for safety
        return True


# ///////////////////////////////////////////////////////////////
# SECURITY PATTERN FUNCTIONS
# ///////////////////////////////////////////////////////////////


def contains_security_sensitive_pattern(file_path: Path | str) -> bool:
    """Check if a file path contains security-sensitive patterns.

    Args:
        file_path: File path to check (Path or string)

    Returns:
        bool: True if path contains security-sensitive patterns, False otherwise
    """
    try:
        file_str = str(file_path).lower()
        return any(
            pattern in file_str
            for pattern in FileScannerConfig.SECURITY_SENSITIVE_PATTERNS
        )
    except Exception:
        # Return False on error - conservative approach
        return False


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "contains_security_sensitive_pattern",
    "is_python_file",
    "should_exclude_path",
]
