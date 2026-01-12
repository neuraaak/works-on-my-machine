#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UI SYSTEM - System UI Components
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
System UI components for Works On My Machine.

This module provides UI components for system operations,
including system detection displays.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .display import (
    display_available_managers,
    display_best_manager,
    display_system_detection_results,
    display_system_managers_list,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "display_available_managers",
    "display_best_manager",
    "display_system_detection_results",
    "display_system_managers_list",
]
