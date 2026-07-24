#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UTILS INSTALLATION - Installation Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Pure utility functions for installation operations.

This package contains stateless utility functions for installation
and uninstallation operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .common_utils import (
    get_current_womm_path,
    get_default_womm_path,
    get_womm_installation_path,
    is_valid_womm_installation,
)
from .installer_utils import (
    create_installation_proof,
    create_womm_executable,
    get_files_to_copy,
    should_exclude_file,
    verify_files_copied,
)
from .uninstaller_utils import (
    get_files_to_remove,
    verify_directory_removed,
    verify_files_removed,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "create_installation_proof",
    "create_womm_executable",
    "get_current_womm_path",
    "get_default_womm_path",
    "get_files_to_copy",
    "get_files_to_remove",
    "get_womm_installation_path",
    "is_valid_womm_installation",
    "should_exclude_file",
    "verify_directory_removed",
    "verify_files_copied",
    "verify_files_removed",
]
