#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UTILS SYSTEM - System Utility Modules
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
System utility modules for Works On My Machine.

This package contains pure utility functions for system management operations.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .system_detector import SystemDetector
from .user_path_utils import (
    deduplicate_path_entries,
    extract_path_from_reg_output,
    remove_from_path,
    remove_from_unix_path,
    remove_from_windows_path,
    setup_unix_path,
    setup_windows_path,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "SystemDetector",
    "deduplicate_path_entries",
    "extract_path_from_reg_output",
    "remove_from_path",
    "remove_from_unix_path",
    "remove_from_windows_path",
    "setup_unix_path",
    "setup_windows_path",
]
