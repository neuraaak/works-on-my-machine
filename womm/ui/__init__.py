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

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .common.ezpl_bridge import ezprinter
from .common.interactive_menu import InteractiveMenu, format_backup_item
from .common.prompts import confirm, prompt_choice, prompt_path

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "InteractiveMenu",
    "confirm",
    "ezprinter",
    "format_backup_item",
    "prompt_choice",
    "prompt_path",
]
