#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS CONTEXT - Context Menu Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Context menu exceptions for Works On My Machine.

This package contains custom exceptions used specifically by context menu modules:
- ContextMenuManager (womm/core/managers/context/managers/context_menu.py)
- BackupManager (womm/core/managers/context/managers/backup_manager.py)
- IconManager (womm/core/managers/context/managers/icon_manager.py)
- ScriptDetector (womm/core/managers/context/managers/script_detector.py)
- RegistryUtils (womm/core/utils/context/registry_utils.py)
- ValidationUtils (womm/core/utils/context/validation.py)

Following a pragmatic approach with focused exception types:
1. ContextUtilityError - Base exception for context utilities
2. ContextMenuError - Context menu management errors
3. BackupError - Backup management errors
4. IconError - Icon management errors
5. ScriptError - Script detection errors
6. RegistryError - Registry operation errors
7. ValidationError - Validation errors
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .context_exceptions import (
    BackupError,
    ContextMenuError,
    ContextUtilityError,
    IconError,
    RegistryError,
    ScriptError,
    ValidationError,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Base exception
    "ContextUtilityError",
    # Context menu exceptions
    "ContextMenuError",
    # Backup exceptions
    "BackupError",
    # Icon exceptions
    "IconError",
    # Script exceptions
    "ScriptError",
    # Registry exceptions
    "RegistryError",
    # Validation exceptions
    "ValidationError",
]
