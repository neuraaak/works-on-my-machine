#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UTILS SYSTEM - System Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Pure utility functions for system operations.

This package contains stateless utility functions for system path
and environment management operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .detector_utils import (
    create_editor_entry,
    create_package_manager_entry,
    create_shell_entry,
    extract_version_first_line,
    extract_version_from_stdout,
    generate_editor_recommendation,
    generate_package_manager_recommendation,
    generate_recommendations,
    get_best_package_manager,
    get_editor_name,
    get_package_manager_metadata,
    get_shell_name,
)
from .environment_utils import (
    combine_paths,
    get_environment_info,
    get_shell_config_files,
    is_command_accessible,
    read_windows_registry_path,
    refresh_path_from_registry,
)
from .path_utils import (
    deduplicate_path_entries,
    extract_path_from_reg_output,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "combine_paths",
    "create_editor_entry",
    "create_package_manager_entry",
    "create_shell_entry",
    "deduplicate_path_entries",
    "extract_path_from_reg_output",
    "extract_version_first_line",
    "extract_version_from_stdout",
    "generate_editor_recommendation",
    "generate_package_manager_recommendation",
    "generate_recommendations",
    "get_best_package_manager",
    "get_editor_name",
    "get_environment_info",
    "get_package_manager_metadata",
    "get_shell_config_files",
    "get_shell_name",
    "is_command_accessible",
    "read_windows_registry_path",
    "refresh_path_from_registry",
]
