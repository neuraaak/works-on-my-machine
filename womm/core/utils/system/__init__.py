#!/usr/bin/env python3
"""
System utility modules for Works On My Machine.

This package contains pure utility functions for system management operations.
"""

# Import utility functions for external use
from .registrator_utils import (
    ScriptType,
    add_context_menu_entry,
    backup_registry_entries,
    generate_registry_key_name,
    list_context_menu_entries,
    remove_context_menu_entry,
    restore_from_backup,
    save_backup,
    validate_icon_path,
    validate_script_path,
)
from .system_detector import SystemDetector
from .user_path_utils import deduplicate_path_entries, extract_path_from_reg_output

__all__ = [
    "SystemDetector",
    "ScriptType",
    "add_context_menu_entry",
    "backup_registry_entries",
    "generate_registry_key_name",
    "list_context_menu_entries",
    "remove_context_menu_entry",
    "restore_from_backup",
    "save_backup",
    "validate_icon_path",
    "validate_script_path",
    "deduplicate_path_entries",
    "extract_path_from_reg_output",
]
