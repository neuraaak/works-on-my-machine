#!/usr/bin/env python3
"""
Icon management for context menu entries.

This module provides icon detection, validation, and management for
context menu entries with automatic icon selection based on file extensions.
"""

import logging
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from ...exceptions.context.context_exceptions import (
    ContextUtilityError,
    IconError,
    ValidationError,
)


class IconManager:
    """Manage icons for context menu entries."""

    # Extension to icon mapping
    EXTENSION_ICONS = {
        # Scripts
        ".py": "python.exe,0",
        ".ps1": "powershell.exe,0",
        ".bat": "cmd.exe,0",
        ".cmd": "cmd.exe,0",
        ".js": "node.exe,0",
        ".ts": "node.exe,0",
        # Documents
        ".txt": "notepad.exe,0",
        ".md": "notepad.exe,0",
        ".doc": "wordpad.exe,0",
        ".docx": "wordpad.exe,0",
        ".pdf": "AcroRd32.exe,0",
        # Images
        ".jpg": "rundll32.exe,shell32.dll,ShellImagePreview",
        ".jpeg": "rundll32.exe,shell32.dll,ShellImagePreview",
        ".png": "rundll32.exe,shell32.dll,ShellImagePreview",
        ".gif": "rundll32.exe,shell32.dll,ShellImagePreview",
        ".bmp": "rundll32.exe,shell32.dll,ShellImagePreview",
        ".ico": "rundll32.exe,shell32.dll,ShellImagePreview",
        # Archives
        ".zip": "zipfldr.dll,0",
        ".rar": "WinRAR.exe,0",
        ".7z": "7zFM.exe,0",
        ".tar": "zipfldr.dll,0",
        ".gz": "zipfldr.dll,0",
        # Code
        ".html": "mshtml.dll,0",
        ".htm": "mshtml.dll,0",
        ".css": "mshtml.dll,0",
        ".xml": "mshtml.dll,0",
        ".json": "notepad.exe,0",
        # Executables
        ".exe": None,  # Use file's own icon
        ".msi": None,  # Use file's own icon
    }

    # System icon shortcuts
    SYSTEM_ICONS = {
        "auto": None,  # Auto-detect
        "python": "python.exe,0",
        "powershell": "powershell.exe,0",
        "cmd": "cmd.exe,0",
        "node": "node.exe,0",
        "notepad": "notepad.exe,0",
        "explorer": "explorer.exe,0",
        "folder": "shell32.dll,4",
        "file": "shell32.dll,1",
        "gear": "shell32.dll,14",
        "settings": "shell32.dll,21",
    }

    # Common system paths for icons
    SYSTEM_PATHS = [
        "C:\\Windows\\System32",
        "C:\\Windows",
        "C:\\Program Files",
        "C:\\Program Files (x86)",
    ]

    @classmethod
    def get_icon_for_extension(cls, extension: str) -> Optional[str]:
        """
        Get default icon for file extension.

        Args:
            extension: File extension (e.g., ".py", ".js")

        Returns:
            Icon path or None if not found

        Raises:
            ValidationError: If extension is invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not extension:
                raise ValidationError(
                    "icon_extension",
                    "extension",
                    "File extension cannot be None or empty",
                )

            if not isinstance(extension, str):
                raise ValidationError(
                    "icon_extension",
                    "extension",
                    f"Extension must be a string, got {type(extension).__name__}",
                )

            return cls.EXTENSION_ICONS.get(extension.lower())

        except ValidationError:
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error getting icon for extension: {e}",
                details=f"Extension: {extension}",
            ) from e

    @classmethod
    def get_system_icon(cls, icon_name: str) -> Optional[str]:
        """
        Get system icon by name.

        Args:
            icon_name: Name of the system icon

        Returns:
            Icon path or None if not found

        Raises:
            ValidationError: If icon_name is invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not icon_name:
                raise ValidationError(
                    "system_icon", "icon_name", "Icon name cannot be None or empty"
                )

            if not isinstance(icon_name, str):
                raise ValidationError(
                    "system_icon",
                    "icon_name",
                    f"Icon name must be a string, got {type(icon_name).__name__}",
                )

            return cls.SYSTEM_ICONS.get(icon_name.lower())

        except ValidationError:
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error getting system icon: {e}",
                details=f"Icon name: {icon_name}",
            ) from e

    @classmethod
    def validate_icon_path(cls, icon_path: str) -> bool:
        """
        Validate if icon path exists and is accessible.

        Args:
            icon_path: Path to the icon file

        Returns:
            True if icon path is valid, False otherwise

        Raises:
            ValidationError: If icon_path is invalid
            IconError: If icon validation fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not icon_path:
                raise ValidationError(
                    "icon_path", "icon_path", "Icon path cannot be None or empty"
                )

            if not isinstance(icon_path, str):
                raise ValidationError(
                    "icon_path",
                    "icon_path",
                    f"Icon path must be a string, got {type(icon_path).__name__}",
                )

            # Handle icon with index (e.g., "file.exe,0")
            file_path = icon_path.split(",")[0] if "," in icon_path else icon_path

            # Check if it's a system icon
            if file_path in cls.SYSTEM_ICONS:
                return True

            # Check if file exists
            try:
                if os.path.exists(file_path):
                    return True
            except (OSError, PermissionError) as e:
                raise IconError(
                    "validate", file_path, f"Failed to check file existence: {e}"
                ) from e

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

        except (ValidationError, IconError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error validating icon path: {e}",
                details=f"Icon path: {icon_path}",
            ) from e

    @classmethod
    def resolve_icon(cls, icon_input: str, file_path: str = None) -> Optional[str]:
        """
        Resolve icon from various input formats.

        Args:
            icon_input: Icon input (auto, system name, or path)
            file_path: Optional file path for auto-detection

        Returns:
            Resolved icon path or None if not found

        Raises:
            ValidationError: If parameters are invalid
            IconError: If icon resolution fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if icon_input is not None and not isinstance(icon_input, str):
                raise ValidationError(
                    "icon_resolution",
                    "icon_input",
                    f"Icon input must be a string, got {type(icon_input).__name__}",
                )

            if file_path is not None and not isinstance(file_path, str):
                raise ValidationError(
                    "icon_resolution",
                    "file_path",
                    f"File path must be a string, got {type(file_path).__name__}",
                )

            if not icon_input or icon_input.lower() == "auto":
                # Auto-detect based on file extension
                if file_path:
                    try:
                        extension = Path(file_path).suffix.lower()
                        return cls.get_icon_for_extension(extension)
                    except Exception as e:
                        raise IconError(
                            "resolve",
                            file_path,
                            f"Failed to auto-detect icon from file extension: {e}",
                        ) from e
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

        except (ValidationError, IconError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error resolving icon: {e}",
                details=f"Icon input: {icon_input}, File path: {file_path}",
            ) from e

    @classmethod
    def find_icon_in_path(cls, icon_name: str) -> Optional[str]:
        """
        Find icon file in system PATH.

        Args:
            icon_name: Name of the icon file to find

        Returns:
            Full path to icon file or None if not found

        Raises:
            ValidationError: If icon_name is invalid
            IconError: If icon search fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not icon_name:
                raise ValidationError(
                    "icon_search", "icon_name", "Icon name cannot be None or empty"
                )

            if not isinstance(icon_name, str):
                raise ValidationError(
                    "icon_search",
                    "icon_name",
                    f"Icon name must be a string, got {type(icon_name).__name__}",
                )

            try:
                return shutil.which(icon_name)
            except Exception as e:
                raise IconError(
                    "find", icon_name, f"Failed to search for icon in PATH: {e}"
                ) from e

        except (ValidationError, IconError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error finding icon in PATH: {e}",
                details=f"Icon name: {icon_name}",
            ) from e

    @classmethod
    def get_available_icons(cls) -> Dict[str, str]:
        """
        Get list of available system icons.

        Returns:
            Dictionary of available system icons

        Raises:
            ContextUtilityError: For unexpected errors
        """
        try:
            return cls.SYSTEM_ICONS.copy()
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error getting available icons: {e}",
                details="Failed to copy system icons dictionary",
            ) from e

    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """
        Get list of supported file extensions.

        Returns:
            List of supported file extensions

        Raises:
            ContextUtilityError: For unexpected errors
        """
        try:
            return list(cls.EXTENSION_ICONS.keys())
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error getting supported extensions: {e}",
                details="Failed to get extension icons keys",
            ) from e
