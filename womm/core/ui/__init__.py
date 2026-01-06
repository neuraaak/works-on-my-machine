#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UI - User Interface Module
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
User Interface module for Works On My Machine.

This package contains UI components using Rich for beautiful terminal output.
Provides console utilities, interactive components, and display functions.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .common.console import (
    LogLevel,
    console,
    get_log_level,
    print_command,
    print_config,
    print_deps,
    print_detect,
    print_error,
    print_header,
    print_info,
    print_install,
    print_pattern,
    print_result,
    print_separator,
    print_success,
    print_system,
    print_tip,
    print_warn,
    set_critical_level,
    set_debug_level,
    set_error_level,
    set_info_level,
    set_log_level,
    set_warn_level,
)
from .common.tables import create_backup_table
from .interactive import InteractiveMenu, format_backup_item

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Console and display functions
    "console",
    "LogLevel",
    "print_success",
    "print_error",
    "print_warn",
    "print_tip",
    "print_system",
    "print_install",
    "print_detect",
    "print_config",
    "print_deps",
    "print_pattern",
    "print_header",
    "print_info",
    "print_separator",
    "print_command",
    "print_result",
    # Logging level configuration functions
    "set_log_level",
    "get_log_level",
    "set_debug_level",
    "set_info_level",
    "set_warn_level",
    "set_error_level",
    "set_critical_level",
    # Table utilities
    "create_backup_table",
    # Interactive components
    "InteractiveMenu",
    "format_backup_item",
]
