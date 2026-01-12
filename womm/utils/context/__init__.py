#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UTILS CONTEXT - Context Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Pure utility functions for context menu operations.

This package contains stateless utility functions for context menu
validation and registry operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .core_utils import (
    build_command_with_parameter,
    generate_registry_key_name,
    get_available_file_types,
    get_context_type_help,
    get_file_type_help,
    get_registry_entry_info,
    sanitize_label,
    sanitize_registry_key,
    validate_backup_data,
    validate_icon_path,
    validate_label,
    validate_registry_key,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "build_command_with_parameter",
    "generate_registry_key_name",
    "get_available_file_types",
    "get_context_type_help",
    "get_file_type_help",
    "get_registry_entry_info",
    "sanitize_label",
    "sanitize_registry_key",
    "validate_backup_data",
    "validate_icon_path",
    "validate_label",
    "validate_registry_key",
]
