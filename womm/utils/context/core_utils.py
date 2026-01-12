#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT UTILS - Consolidated Context Menu Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Consolidated context menu utilities.

Merged from:
- context_command_utils.py
- context_help_utils.py
- context_registry_utils.py
- context_validation_utils.py

Provides utilities for context menu operations including:
- Command building
- Registry key management
- Help text generation
- Input validation
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import winreg
from pathlib import Path

# Local imports
from ...exceptions.common import ValidationServiceError
from ...exceptions.context import ContextUtilityError
from ...shared.configs.context.context_config import ContextConfig

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# COMMAND BUILDING FUNCTIONS
# ///////////////////////////////////////////////////////////////


def build_command_with_parameter(base_command: str, parameter: str) -> str:
    """
    Build a command with a parameter, handling various quote formats.

    Args:
        base_command: Base command without parameters
        parameter: Parameter to append (e.g., "%V", "%1")

    Returns:
        Complete command with parameter

    Raises:
        ValidationError: If parameters are invalid
    """
    try:
        if not base_command:
            raise ValidationServiceError(
                "command_building",
                "base_command",
                "Base command cannot be empty",
            )

        # Handle quoted commands
        if base_command.startswith('"') and base_command.endswith('"'):
            # Insert parameter before closing quote
            return f'{base_command[:-1]} {parameter}"'
        else:
            # Append parameter directly
            return f"{base_command} {parameter}"

    except ValidationServiceError:
        raise
    except Exception as e:
        raise ContextUtilityError(
            f"Failed to build command with parameter: {e}",
            details=f"Base command: {base_command}, Parameter: {parameter}",
        ) from e


# ///////////////////////////////////////////////////////////////
# REGISTRY KEY GENERATION FUNCTIONS
# ///////////////////////////////////////////////////////////////


def generate_registry_key_name(file_path: str) -> str:
    """
    Generate registry key name from file path.

    Args:
        file_path: Path to the file

    Returns:
        Generated registry key name (filename without extension)

    Raises:
        ValidationError: If file_path is invalid
    """
    try:
        if not file_path:
            raise ValidationServiceError(
                "registry_key", "file_path", "File path cannot be empty"
            )

        path = Path(file_path)
        key_name = path.stem  # Filename without extension

        if not key_name:
            raise ValidationServiceError(
                "registry_key",
                "file_path",
                "Could not generate valid key name from file path",
            )

        return key_name

    except ValidationServiceError:
        raise
    except Exception as e:
        raise ContextUtilityError(
            f"Failed to generate registry key name: {e}",
            details=f"File path: {file_path}",
        ) from e


def sanitize_registry_key(key: str) -> str:
    """
    Sanitize registry key by removing invalid characters.

    Args:
        key: Registry key to sanitize

    Returns:
        Sanitized registry key

    Raises:
        ValidationError: If key is invalid
    """
    if not key:
        raise ValidationServiceError(
            "registry_key", "key", "Registry key cannot be empty"
        )

    # Remove invalid characters
    invalid_chars = ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]
    sanitized = key
    for char in invalid_chars:
        sanitized = sanitized.replace(char, "_")

    return sanitized


def sanitize_label(label: str) -> str:
    """
    Sanitize label by removing/replacing invalid characters.

    Args:
        label: Label to sanitize

    Returns:
        Sanitized label

    Raises:
        ValidationError: If label is invalid
    """
    if not label:
        raise ValidationServiceError("label", "label", "Label cannot be empty")

    # Remove control characters but keep spaces and common punctuation
    sanitized = "".join(c for c in label if c.isprintable() or c.isspace())

    return sanitized.strip()


def get_context_type_help() -> str:
    """
    Get help text for context types.

    Returns:
        Help text string describing available context types
    """
    help_text = "Available context types:\n"
    help_text += "• --root: Root directories (drives)\n"
    help_text += "• --file: Single file selection\n"
    help_text += "• --files: Multiple file selection\n"
    help_text += "• --background: Background context (empty space)\n"
    help_text += "• Default: Both directory and background contexts\n"
    return help_text


def get_file_type_help() -> str:
    """
    Get help text for file types.

    Returns:
        Help text string describing available file types

    Raises:
        ContextUtilityError: For unexpected errors
    """
    try:
        help_text = "Available file types:\n"
        for file_type, extensions in ContextConfig.FILE_TYPE_EXTENSIONS.items():
            ext_list = ", ".join(sorted(extensions))
            help_text += f"• {file_type}: {ext_list}\n"
        help_text += "• Custom extensions: Use --extensions .ext1 .ext2\n"
        return help_text
    except Exception as e:
        raise ContextUtilityError(
            f"Unexpected error getting file type help: {e}",
            details="Failed to generate help text",
        ) from e


def get_available_file_types() -> dict[str, set[str]]:
    """
    Get all available file types and their extensions.

    Returns:
        Dictionary of file types and their extensions

    Raises:
        ContextUtilityError: For unexpected errors
    """
    try:
        return ContextConfig.FILE_TYPE_EXTENSIONS.copy()
    except Exception as e:
        raise ContextUtilityError(
            f"Unexpected error getting available file types: {e}",
            details="Failed to copy file type extensions",
        ) from e


def get_registry_entry_info(
    base_path: str, key_name: str
) -> dict[str, str | None] | None:
    """
    Get information about a specific registry entry.

    Args:
        base_path: Base registry path
        key_name: Registry key name

    Returns:
        Entry information dictionary or None if failed

    Raises:
        ContextUtilityError: For unexpected errors
    """
    try:
        full_path = f"{base_path}\\{key_name}"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, full_path) as key:
            info = {"key_name": key_name, "registry_path": full_path}

            # Get MUIVerb (display name)
            try:
                mui_verb, _ = winreg.QueryValueEx(key, "MUIVerb")
                info["display_name"] = mui_verb
            except OSError:
                info["display_name"] = key_name

            # Get icon
            try:
                icon, _ = winreg.QueryValueEx(key, "Icon")
                info["icon"] = icon
            except OSError:
                info["icon"] = None

            # Get command
            try:
                with winreg.OpenKey(key, "command") as cmd_key:
                    command, _ = winreg.QueryValueEx(cmd_key, "")
                    info["command"] = command
            except OSError:
                info["command"] = None

            return info

    except Exception as e:
        raise ContextUtilityError(
            f"Unexpected error getting registry entry info: {e}",
            details=f"Base path: {base_path}, Key name: {key_name}",
        ) from e


# ///////////////////////////////////////////////////////////////
# HELP TEXT FUNCTIONS
# ///////////////////////////////////////////////////////////////


# ///////////////////////////////////////////////////////////////
# VALIDATION FUNCTIONS
# ///////////////////////////////////////////////////////////////


def validate_label(label: str) -> None:
    """
    Validate label for context menu entry.

    Args:
        label: Label to validate

    Raises:
        ValidationError: If label is invalid
    """
    if not label:
        raise ValidationServiceError("label", "label", "Label cannot be empty")

    if len(label) > 100:
        raise ValidationServiceError(
            "label",
            "label",
            f"Label is too long (max 100 characters, got {len(label)})",
        )

    # Check for at least one valid character
    if not any(c.isalnum() for c in label):
        raise ValidationServiceError(
            "label",
            "label",
            "Label must contain at least one alphanumeric character",
        )


def validate_registry_key(key: str) -> None:
    """
    Validate registry key for context menu entry.

    Args:
        key: Registry key to validate

    Raises:
        ValidationError: If key is invalid
    """
    if not key:
        raise ValidationServiceError(
            "registry_key", "key", "Registry key cannot be empty"
        )

    # Check for invalid characters
    invalid_chars = ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]
    for char in invalid_chars:
        if char in key:
            raise ValidationServiceError(
                "registry_key",
                "key",
                f"Registry key contains invalid character: {char}",
            )

    if len(key) > 255:
        raise ValidationServiceError(
            "registry_key",
            "key",
            f"Registry key is too long (max 255 characters, got {len(key)})",
        )


def validate_icon_path(icon_path: str) -> None:
    """
    Validate icon path for context menu entry.

    Args:
        icon_path: Icon path to validate

    Raises:
        ValidationError: If icon path is invalid
    """
    if not icon_path or icon_path == "auto":
        return  # "auto" is valid

    try:
        path = Path(icon_path)
        if not path.exists():
            raise ValidationServiceError(
                "icon_path",
                "icon_path",
                f"Icon file does not exist: {icon_path}",
            )

        # Check file extension
        valid_extensions = {".ico", ".png", ".bmp", ".jpg", ".exe", ".dll"}
        if path.suffix.lower() not in valid_extensions:
            raise ValidationServiceError(
                "icon_path",
                "icon_path",
                f"Unsupported icon format: {path.suffix}",
            )

    except ValidationServiceError:
        raise
    except Exception as e:
        raise ValidationServiceError(
            "icon_path",
            "icon_path",
            f"Error validating icon path: {e!s}",
        ) from e


def validate_backup_data(data: dict) -> None:
    """
    Validate backup data structure.

    Args:
        data: Backup data to validate

    Raises:
        ValidationError: If backup data is invalid
    """
    if not isinstance(data, dict):
        raise ValidationServiceError(
            "backup_data",
            "data",
            f"Backup data must be a dictionary, got {type(data).__name__}",
        )

    required_keys = {"version", "timestamp", "entries", "metadata"}
    missing_keys = required_keys - set(data.keys())

    if missing_keys:
        raise ValidationServiceError(
            "backup_data",
            "data",
            f"Backup data missing required keys: {', '.join(missing_keys)}",
        )

    if not isinstance(data["entries"], (dict, list)):
        raise ValidationServiceError(
            "backup_data",
            "entries",
            f"Entries must be dict or list, got {type(data['entries']).__name__}",
        )
