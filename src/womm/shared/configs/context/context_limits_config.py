#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT LIMITS CONFIG - Validation Limits & Extensions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Configuration for context menu validation limits and extensions.

This config class exposes validation constants used by
context menu services for input validation.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import re
from dataclasses import dataclass
from typing import ClassVar

# ///////////////////////////////////////////////////////////////
# CLASS DEFINITION
# ///////////////////////////////////////////////////////////////


@dataclass(frozen=True)
class ContextLimitsConfig:
    """Context menu validation limits configuration (static, read-only).

    Contains validation patterns, limits, and allowed extensions
    for context menu operations.
    """

    # ///////////////////////////////////////////////////////////
    # REGISTRY PATTERNS
    # ///////////////////////////////////////////////////////////

    REGISTRY_KEY_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^[a-zA-Z0-9_\-\.]+$")

    # ///////////////////////////////////////////////////////////
    # VALID EXTENSIONS
    # ///////////////////////////////////////////////////////////

    VALID_SCRIPT_EXTENSIONS: ClassVar[set[str]] = {
        ".py",
        ".ps1",
        ".bat",
        ".cmd",
        ".exe",
        ".msi",
    }

    VALID_ICON_EXTENSIONS: ClassVar[set[str]] = {
        ".ico",
        ".exe",
        ".dll",
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
    }

    # ///////////////////////////////////////////////////////////
    # MAXIMUM LENGTHS
    # ///////////////////////////////////////////////////////////

    MAX_LABEL_LENGTH: ClassVar[int] = 256
    MAX_REGISTRY_KEY_LENGTH: ClassVar[int] = 255
    MAX_PATH_LENGTH: ClassVar[int] = 260
    MAX_ICON_FILE_SIZE: ClassVar[int] = 10 * 1024 * 1024  # 10MB

    # ///////////////////////////////////////////////////////////
    # RESERVED NAMES
    # ///////////////////////////////////////////////////////////

    RESERVED_REGISTRY_NAMES: ClassVar[set[str]] = {
        "con",
        "prn",
        "aux",
        "nul",
        "com1",
        "com2",
        "com3",
        "com4",
        "com5",
        "com6",
        "com7",
        "com8",
        "com9",
        "lpt1",
        "lpt2",
        "lpt3",
        "lpt4",
        "lpt5",
        "lpt6",
        "lpt7",
        "lpt8",
        "lpt9",
    }

    # ///////////////////////////////////////////////////////////
    # INVALID CHARACTERS
    # ///////////////////////////////////////////////////////////

    INVALID_LABEL_CHARS: ClassVar[list[str]] = [
        "<",
        ">",
        ":",
        '"',
        "|",
        "?",
        "*",
        "\\",
        "/",
    ]

    # ///////////////////////////////////////////////////////////
    # SPECIAL ICON VALUES
    # ///////////////////////////////////////////////////////////

    SPECIAL_ICON_VALUES: ClassVar[set[str]] = {"auto", "default", "none"}

    # ///////////////////////////////////////////////////////////
    # HELPER METHODS
    # ///////////////////////////////////////////////////////////

    @classmethod
    def is_valid_registry_key(cls, key: str) -> bool:
        """Check if a registry key name is valid.

        Args:
            key: Registry key name to validate

        Returns:
            True if valid, False otherwise
        """
        if not key or len(key) > cls.MAX_REGISTRY_KEY_LENGTH:
            return False
        if key.lower() in cls.RESERVED_REGISTRY_NAMES:
            return False
        return bool(cls.REGISTRY_KEY_PATTERN.match(key))

    @classmethod
    def is_valid_script_extension(cls, extension: str) -> bool:
        """Check if a script extension is valid.

        Args:
            extension: File extension (with dot)

        Returns:
            True if valid script extension
        """
        return extension.lower() in cls.VALID_SCRIPT_EXTENSIONS

    @classmethod
    def is_valid_icon_extension(cls, extension: str) -> bool:
        """Check if an icon extension is valid.

        Args:
            extension: File extension (with dot)

        Returns:
            True if valid icon extension
        """
        return extension.lower() in cls.VALID_ICON_EXTENSIONS

    @classmethod
    def has_invalid_label_chars(cls, label: str) -> bool:
        """Check if a label contains invalid characters.

        Args:
            label: Label to check

        Returns:
            True if label contains invalid characters
        """
        return any(char in label for char in cls.INVALID_LABEL_CHARS)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["ContextLimitsConfig"]
