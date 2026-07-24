#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEPENDENCIES CONFIG - Base Dependencies Configuration
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Base configuration for all dependency operations.

This config class exposes fundamental constants used across
all dependency-related utilities and services.
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
class DependenciesConfig:
    """Base configuration for all dependency operations (static, read-only).

    Contains fundamental constants for dependency management:
    - Supported languages
    - Timeout values
    - Retry policies
    - Installation modes
    """

    # ///////////////////////////////////////////////////////////
    # SUPPORTED LANGUAGES
    # ///////////////////////////////////////////////////////////

    SUPPORTED_LANGUAGES: ClassVar[list[str]] = ["python", "javascript"]

    # Language display names
    LANGUAGE_DISPLAY_NAMES: ClassVar[dict[str, str]] = {
        "python": "Python",
        "javascript": "JavaScript/Node.js",
    }

    # Language file extensions (primary)
    LANGUAGE_EXTENSIONS: ClassVar[dict[str, str]] = {
        "python": ".py",
        "javascript": ".js",
    }

    # ///////////////////////////////////////////////////////////
    # TIMEOUT CONFIGURATION
    # ///////////////////////////////////////////////////////////

    DEFAULT_TIMEOUT: ClassVar[int] = 300  # 5 minutes
    INSTALL_TIMEOUT: ClassVar[int] = 600  # 10 minutes for installations
    SEARCH_TIMEOUT: ClassVar[int] = 60  # 1 minute for searches
    CHECK_TIMEOUT: ClassVar[int] = 30  # 30 seconds for availability checks

    # ///////////////////////////////////////////////////////////
    # RETRY CONFIGURATION
    # ///////////////////////////////////////////////////////////

    MAX_RETRIES: ClassVar[int] = 3
    RETRY_DELAY: ClassVar[int] = 2  # seconds between retries
    RETRY_BACKOFF_MULTIPLIER: ClassVar[float] = 1.5  # exponential backoff

    # ///////////////////////////////////////////////////////////
    # INSTALLATION MODES
    # ///////////////////////////////////////////////////////////

    INSTALL_MODE_USER: ClassVar[str] = "user"
    INSTALL_MODE_SYSTEM: ClassVar[str] = "system"
    INSTALL_MODE_DEV: ClassVar[str] = "dev"

    INSTALLATION_MODES: ClassVar[list[str]] = [
        INSTALL_MODE_USER,
        INSTALL_MODE_SYSTEM,
        INSTALL_MODE_DEV,
    ]

    # Default installation mode per language
    DEFAULT_INSTALL_MODES: ClassVar[dict[str, str]] = {
        "python": INSTALL_MODE_USER,
        "javascript": INSTALL_MODE_DEV,
    }

    # ///////////////////////////////////////////////////////////
    # VERSION REQUIREMENTS
    # ///////////////////////////////////////////////////////////

    MINIMUM_VERSIONS: ClassVar[dict[str, str]] = {
        "python": "3.10",
        "node": "18.0",
        "npm": "8.0",
        "git": "2.30",
    }

    # ///////////////////////////////////////////////////////////
    # HELPER METHODS
    # ///////////////////////////////////////////////////////////

    @classmethod
    def is_supported_language(cls, language: str) -> bool:
        """Check if a language is supported.

        Args:
            language: Language name to check

        Returns:
            True if language is supported
        """
        return language.lower() in cls.SUPPORTED_LANGUAGES

    @classmethod
    def get_display_name(cls, language: str) -> str:
        """Get display name for a language.

        Args:
            language: Language code

        Returns:
            Display name or language code if not found
        """
        return cls.LANGUAGE_DISPLAY_NAMES.get(language.lower(), language)

    @classmethod
    def get_timeout(cls, operation: str = "default") -> int:
        """Get timeout for an operation type.

        Args:
            operation: Operation type (default, install, search, check)

        Returns:
            Timeout in seconds
        """
        timeouts = {
            "default": cls.DEFAULT_TIMEOUT,
            "install": cls.INSTALL_TIMEOUT,
            "search": cls.SEARCH_TIMEOUT,
            "check": cls.CHECK_TIMEOUT,
        }
        return timeouts.get(operation, cls.DEFAULT_TIMEOUT)

    @classmethod
    def get_minimum_version(cls, tool: str) -> str | None:
        """Get minimum required version for a tool.

        Args:
            tool: Tool name (python, node, npm, git)

        Returns:
            Minimum version string or None if not defined
        """
        return cls.MINIMUM_VERSIONS.get(tool.lower())


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["DependenciesConfig"]
