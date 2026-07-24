#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UI RUNTIME - Runtime UI Components
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Runtime UI components for Works On My Machine.

This module provides UI components for runtime operations,
including runtime checks, installations, and listings.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .display import (
    display_runtime_check_all,
    display_runtime_check_specific,
    display_runtime_install_result,
    display_runtimes_list,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "display_runtime_check_all",
    "display_runtime_check_specific",
    "display_runtime_install_result",
    "display_runtimes_list",
]
