#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UI DEPENDENCIES - Dependencies UI Components
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Dependencies UI components for Works On My Machine.

This module provides UI components for dependencies operations,
including devtools status displays and package manager information.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .display import (
    display_devtools_status_table,
    display_runtime_check_specific,
    display_runtime_install_result,
    display_runtime_table,
    display_runtimes_list,
    display_system_check_all,
    display_system_table,
    display_tool_check_all,
    display_tool_table,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "display_devtools_status_table",
    "display_runtime_check_specific",
    "display_runtime_install_result",
    "display_runtime_table",
    "display_runtimes_list",
    "display_system_check_all",
    "display_system_table",
    "display_tool_check_all",
    "display_tool_table",
]
