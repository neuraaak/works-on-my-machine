#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT REGISTRY PATHS - Registry path to context type mapping
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Registry path interpretation for context menu entries.

Pure mapping helpers: they read a registry path and tell which context type it
belongs to. No registry access, no side effects.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from ...shared.configs.context import ContextTypesConfig
from .parameters import ContextType

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def context_type_from_registry_path(registry_path: str) -> ContextType:
    """
    Determine the context type a registry path belongs to.

    Args:
        registry_path: Registry path to interpret

    Returns:
        ContextType: matching type, defaulting to ``DIRECTORY``.
    """
    if (
        ContextTypesConfig.REGISTRY_PATTERN_DIRECTORY_SHELL in registry_path
        and "background" not in registry_path
    ):
        return ContextType.DIRECTORY
    if ContextTypesConfig.REGISTRY_PATTERN_DIRECTORY_BACKGROUND in registry_path:
        return ContextType.BACKGROUND
    if ContextTypesConfig.REGISTRY_PATTERN_DRIVE_SHELL in registry_path:
        return ContextType.ROOT
    if ContextTypesConfig.REGISTRY_PATTERN_FILE_SHELL in registry_path:
        return ContextType.FILE
    return ContextType.DIRECTORY


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["context_type_from_registry_path"]
