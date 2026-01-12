#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT PATHS CONFIG - Registry Paths Configuration
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Configuration for context menu registry paths.

This config class exposes registry path constants used by
context menu services for Windows registry operations.
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
class ContextPathsConfig:
    """Context menu registry paths configuration (static, read-only).

    Contains registry paths for different context menu types
    and command parameters for each type.
    """

    # ///////////////////////////////////////////////////////////
    # REGISTRY PATHS BY CONTEXT NAME
    # ///////////////////////////////////////////////////////////

    CONTEXT_PATHS: ClassVar[dict[str, str]] = {
        "directory": "Software\\Classes\\Directory\\shell",
        "background": "Software\\Classes\\Directory\\background\\shell",
        "file": "Software\\Classes\\*\\shell",
        "image": "Software\\Classes\\SystemFileAssociations\\image\\shell",
        "text": "Software\\Classes\\SystemFileAssociations\\text\\shell",
        "archive": "Software\\Classes\\SystemFileAssociations\\compressed\\shell",
    }

    # ///////////////////////////////////////////////////////////
    # REGISTRY PATHS BY CONTEXT TYPE
    # ///////////////////////////////////////////////////////////

    REGISTRY_PATHS_BY_TYPE: ClassVar[dict[str, str]] = {
        "directory": "Software\\Classes\\Directory\\shell",
        "background": "Software\\Classes\\Directory\\background\\shell",
        "file": "Software\\Classes\\*\\shell",
        "files": "Software\\Classes\\*\\shell",
        "root": "Software\\Classes\\Drive\\shell",
    }

    # ///////////////////////////////////////////////////////////
    # COMMAND PARAMETERS
    # ///////////////////////////////////////////////////////////

    COMMAND_PARAMETERS: ClassVar[dict[str, str]] = {
        "directory": "%V",  # Selected folder
        "background": "%V",  # Background context
        "file": "%1",  # Single selected file
        "files": "%V",  # Multiple selected files
        "root": "%V",  # Root directory (drive)
    }

    # ///////////////////////////////////////////////////////////
    # HELPER METHODS
    # ///////////////////////////////////////////////////////////

    @classmethod
    def get_registry_path(cls, context_type: str) -> str | None:
        """Get registry path for a context type.

        Args:
            context_type: Type of context (directory, background, file, etc.)

        Returns:
            Registry path or None if not found
        """
        return cls.CONTEXT_PATHS.get(context_type)

    @classmethod
    def get_command_parameter(cls, context_type: str) -> str:
        """Get command parameter for a context type.

        Args:
            context_type: Type of context

        Returns:
            Command parameter (default: %V)
        """
        return cls.COMMAND_PARAMETERS.get(context_type, "%V")

    @classmethod
    def get_all_context_types(cls) -> list[str]:
        """Get all available context types.

        Returns:
            List of context type names
        """
        return list(cls.CONTEXT_PATHS.keys())


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["ContextPathsConfig"]
