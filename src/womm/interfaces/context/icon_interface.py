#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# ICON INTERFACE - Context Icon Management
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Icon management for context menu entries.

This module provides icon detection, validation, and management for
context menu entries with automatic icon selection based on file extensions.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import os
import shutil
from pathlib import Path
from typing import ClassVar

# Local imports
from ...shared.configs.context import IconConfig

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class ContextIconInterface:
    """Manage icons for context menu entries."""

    # Use configuration from IconConfig
    EXTENSION_ICONS: ClassVar[dict[str, str | None]] = IconConfig.EXTENSION_ICONS
    SYSTEM_ICONS: ClassVar[dict[str, str | None]] = IconConfig.SYSTEM_ICONS
    SYSTEM_PATHS: ClassVar[list[str]] = IconConfig.SYSTEM_PATHS

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    @classmethod
    def get_icon_for_extension(cls, extension: str) -> str | None:
        """
        Get default icon for file extension.

        Args:
            extension: File extension (e.g., ".py", ".js")

        Returns:
            Icon path or None if not found

        Raises:
            ValueError: If extension is invalid
        """
        if not extension:
            raise ValueError("File extension cannot be None or empty")

        if not isinstance(extension, str):
            raise ValueError(
                f"Extension must be a string, got {type(extension).__name__}"
            )

        return cls.EXTENSION_ICONS.get(extension.lower())

    @classmethod
    def get_system_icon(cls, icon_name: str) -> str | None:
        """
        Get system icon by name.

        Args:
            icon_name: Name of the system icon

        Returns:
            Icon path or None if not found

        Raises:
            ValueError: If icon_name is invalid
        """
        if not icon_name:
            raise ValueError("Icon name cannot be None or empty")

        if not isinstance(icon_name, str):
            raise ValueError(
                f"Icon name must be a string, got {type(icon_name).__name__}"
            )

        return cls.SYSTEM_ICONS.get(icon_name.lower())

    @classmethod
    def validate_icon_path(cls, icon_path: str) -> bool:
        """
        Validate if icon path exists and is accessible.

        Args:
            icon_path: Path to the icon file

        Returns:
            True if icon path is valid, False otherwise

        Raises:
            ValueError: If icon_path is invalid
        """
        if not icon_path:
            raise ValueError("Icon path cannot be None or empty")

        if not isinstance(icon_path, str):
            raise ValueError(
                f"Icon path must be a string, got {type(icon_path).__name__}"
            )

        # Handle icon with index (e.g., "file.exe,0")
        file_path = (
            icon_path.split(IconConfig.ICON_SEPARATOR)[0]
            if IconConfig.ICON_SEPARATOR in icon_path
            else icon_path
        )

        # Check if it's a system icon
        if file_path in cls.SYSTEM_ICONS:
            return True

        # Check if file exists
        if os.path.exists(file_path):
            return True

        # Try to find in system paths
        for system_path in cls.SYSTEM_PATHS:
            try:
                full_path = os.path.join(system_path, file_path)
                if os.path.exists(full_path):
                    return True
            except (OSError, PermissionError) as e:
                # Log warning but continue checking other paths
                logging.getLogger(__name__).warning(
                    f"Failed to check system path {system_path}: {e}"
                )

        return False

    @classmethod
    def resolve_icon(cls, icon_input: str, file_path: str | None = None) -> str | None:
        """
        Resolve icon from various input formats.

        Args:
            icon_input: Icon input (auto, system name, or path)
            file_path: Optional file path for auto-detection

        Returns:
            Resolved icon path or None if not found

        Raises:
            ValueError: If parameters are invalid
        """
        if icon_input is not None and not isinstance(icon_input, str):
            raise ValueError(
                f"Icon input must be a string, got {type(icon_input).__name__}"
            )

        if file_path is not None and not isinstance(file_path, str):
            raise ValueError(
                f"File path must be a string, got {type(file_path).__name__}"
            )

        if not icon_input or icon_input.lower() == IconConfig.SPECIAL_ICON_VALUE_AUTO:
            # Auto-detect based on file extension
            if file_path:
                extension = Path(file_path).suffix.lower()
                return cls.get_icon_for_extension(extension)
            return None

        # Check if it's a system icon name
        try:
            system_icon = cls.get_system_icon(icon_input)
            if system_icon:
                return system_icon
        except Exception as e:
            # Log warning but continue with other resolution methods
            logging.getLogger(__name__).warning(
                f"Failed to get system icon '{icon_input}': {e}"
            )

        # Check if it's a valid path
        try:
            if cls.validate_icon_path(icon_input):
                return icon_input
        except Exception as e:
            # Log warning but continue with system path search
            logging.getLogger(__name__).warning(
                f"Failed to validate icon path '{icon_input}': {e}"
            )

        # Try to find in system paths
        for system_path in cls.SYSTEM_PATHS:
            try:
                full_path = os.path.join(system_path, icon_input)
                if os.path.exists(full_path):
                    return full_path
            except (OSError, PermissionError) as e:
                # Log warning but continue checking other paths
                logging.getLogger(__name__).warning(
                    f"Failed to check system path {system_path}: {e}"
                )

        return None

    @classmethod
    def find_icon_in_path(cls, icon_name: str) -> str | None:
        """
        Find icon file in system PATH.

        Args:
            icon_name: Name of the icon file to find

        Returns:
            Full path to icon file or None if not found

        Raises:
            ValueError: If icon_name is invalid
        """
        if not icon_name:
            raise ValueError("Icon name cannot be None or empty")

        if not isinstance(icon_name, str):
            raise ValueError(
                f"Icon name must be a string, got {type(icon_name).__name__}"
            )

        return shutil.which(icon_name)

    @classmethod
    def get_available_icons(cls) -> dict[str, str]:
        """
        Get list of available system icons.

        Returns:
            Dictionary of available system icons
        """
        return {
            name: path for name, path in cls.SYSTEM_ICONS.items() if path is not None
        }

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """
        Get list of supported file extensions.

        Returns:
            List of supported file extensions
        """
        return list(cls.EXTENSION_ICONS.keys())
