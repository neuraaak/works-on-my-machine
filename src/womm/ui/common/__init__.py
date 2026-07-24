#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UI COMMON - Common UI Components
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Common UI components for Works On My Machine.

This module re-exports UI utilities from ezpl_bridge, prompts, and interactive_menu.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .ezpl_bridge import (
    DynamicLayeredProgress,
    ExtendedPrinter,
    EzplBridge,
    ezconsole,
    ezlogger,
    ezpl,
    ezpl_bridge,
    ezprinter,
    ezwizard,
)
from .interactive_menu import InteractiveMenu, format_backup_item
from .prompts import confirm, prompt_choice, prompt_path

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "DynamicLayeredProgress",
    "ExtendedPrinter",
    "EzplBridge",
    "InteractiveMenu",
    "confirm",
    "ezconsole",
    "ezlogger",
    "ezpl",
    "ezpl_bridge",
    "ezprinter",
    "ezwizard",
    "format_backup_item",
    "prompt_choice",
    "prompt_path",
]
