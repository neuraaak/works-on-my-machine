#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT RESULTS - Context Result Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Context result classes for Works On My Machine.

This module contains result classes for context menu operations:
- Context registry operations
- Context validation operations
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass
from typing import Any

# Local imports
from .base import BaseResult
from .security_results import ValidationResult

# ///////////////////////////////////////////////////////////////
# CONTEXT REGISTRY RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class ContextRegistryResult(BaseResult):
    """Result for context menu registry operations."""

    registry_path: str = ""
    command: str = ""
    display_name: str = ""
    icon_path: str | None = None
    entries: list[dict[str, str | None]] | None = None
    backup_data: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.entries is None:
            self.entries = []
        if self.backup_data is None:
            self.backup_data = {}


# ///////////////////////////////////////////////////////////////
# CONTEXT VALIDATION RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class ContextValidationResult(ValidationResult):
    """Result for context menu validation operations."""

    script_path: str = ""
    extension: str = ""
    file_size: int = 0
    label: str = ""
    registry_key: str = ""
    icon_path: str = ""
    icon_type: str = ""  # file, special, etc.
    has_permissions: bool = False
    compatible: bool = False
    windows_version: str = ""


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ContextRegistryResult",
    "ContextValidationResult",
]
