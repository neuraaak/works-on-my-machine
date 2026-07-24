#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT TYPES CONFIG - Context Types Constants
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Context types configuration for context menu operations.

This config class exposes constants for context types used throughout
context menu utilities and services.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass
from typing import ClassVar

# ///////////////////////////////////////////////////////////////
# CLASS DEFINITION
# ///////////////////////////////////////////////////////////////


@dataclass(frozen=True)
class ContextTypesConfig:
    """Context types configuration (static, read-only).

    Contains context type constants and registry patterns
    for context menu operations.
    """

    # ///////////////////////////////////////////////////////////
    # CONTEXT TYPE CONSTANTS
    # ///////////////////////////////////////////////////////////

    DIRECTORY: ClassVar[str] = "directory"
    BACKGROUND: ClassVar[str] = "background"
    FILE: ClassVar[str] = "file"
    FILES: ClassVar[str] = "files"
    ROOT: ClassVar[str] = "root"

    # List of all interface context types
    ALL_TYPES: ClassVar[list[str]] = [
        "directory",
        "background",
    ]

    # ///////////////////////////////////////////////////////////
    # REGISTRY PATH PATTERNS
    # ///////////////////////////////////////////////////////////

    REGISTRY_PATTERN_DIRECTORY_SHELL: ClassVar[str] = "Directory\\shell"
    REGISTRY_PATTERN_DIRECTORY_BACKGROUND: ClassVar[str] = "Directory\\background"
    REGISTRY_PATTERN_DRIVE_SHELL: ClassVar[str] = "Drive\\shell"
    REGISTRY_PATTERN_FILE_SHELL: ClassVar[str] = "*\\shell"

    # Path separators
    REGISTRY_PATH_SEPARATOR: ClassVar[str] = "\\"


__all__ = ["ContextTypesConfig"]
