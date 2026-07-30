#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# INTERFACES CONTEXT - Context Menu Interfaces
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Context menu interfaces for Works On My Machine.

This module provides Windows context menu interface modules that orchestrate services
for registration, backup/restore, and script type detection.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .menu_interface import ContextMenuInterface
from .registry_interface import ContextRegistryInterface
from .script_detector_interface import ContextScriptDetectorInterface
from .script_registrar import ContextScriptRegistrar

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ContextMenuInterface",
    "ContextRegistryInterface",
    "ContextScriptDetectorInterface",
    "ContextScriptRegistrar",
]
