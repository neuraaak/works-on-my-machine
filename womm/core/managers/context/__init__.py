#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# MANAGERS CONTEXT - Context Menu Management
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Context menu management for Works On My Machine.

This module provides Windows context menu management functionality including
registration, backup/restore, and script type detection.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .backup_manager import BackupManager
from .context_menu import ContextMenuManager
from .icon_manager import IconManager
from .script_detector import ScriptDetector

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ContextMenuManager",
    "BackupManager",
    "IconManager",
    "ScriptDetector",
]
