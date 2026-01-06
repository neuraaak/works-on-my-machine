#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# REGISTRY UTILS - Windows Registry Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Registry utilities for Windows context menu management.

This module provides low-level registry operations for managing
Windows context menu entries.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import winreg
from pathlib import Path

# Local imports
from ...exceptions.context.context_exceptions import (
    ContextUtilityError,
    RegistryError,
    ValidationError,
)


class RegistryUtils:
    """Windows Registry utilities for context menu management."""

    # Registry paths for context menus
    CONTEXT_PATHS = {
        "directory": "Software\\Classes\\Directory\\shell",
        "background": "Software\\Classes\\Directory\\background\\shell",
        "file": "Software\\Classes\\*\\shell",
        "image": "Software\\Classes\\SystemFileAssociations\\image\\shell",
        "text": "Software\\Classes\\SystemFileAssociations\\text\\shell",
        "archive": "Software\\Classes\\SystemFileAssociations\\compressed\\shell",
    }

    @classmethod
    def generate_registry_key_name(cls, file_path: str) -> str:
        """
        Generate registry key name from file path.

        Args:
            file_path: Path to the file

        Returns:
            Generated registry key name

        Raises:
            ValidationError: If file_path is invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not file_path:
                raise ValidationError(
                    "registry_key", "file_path", "File path cannot be None or empty"
                )

            if not isinstance(file_path, str):
                raise ValidationError(
                    "registry_key",
                    "file_path",
                    f"File path must be a string, got {type(file_path).__name__}",
                )

            # Extract filename and extension
            try:
                path_obj = Path(file_path)
                filename = path_obj.stem
                extension = path_obj.suffix.lower()
            except Exception as e:
                raise ValidationError(
                    "registry_key", "file_path", f"Invalid file path format: {e}"
                ) from e

            # Normalize filename: replace spaces and special chars with underscores
            normalized_name = "".join(c if c.isalnum() else "_" for c in filename)
            # Remove consecutive underscores and leading/trailing underscores
            normalized_name = "_".join(
                part for part in normalized_name.split("_") if part
            )
            # Convert to lowercase for consistency
            normalized_name = normalized_name.lower()

            # Get extension without dot and normalize
            ext_clean = extension.replace(".", "").lower()

            # Format: womm_{extension}_{filename}
            return f"womm_{ext_clean}_{normalized_name}"

        except (ValidationError, ContextUtilityError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error generating registry key name: {e}",
                details=f"File path: {file_path}",
            ) from e

    @classmethod
    def add_context_menu_entry(
        cls,
        registry_path: str,
        command: str,
        mui_verb: str,
        icon_path: str | None = None,
    ) -> bool:
        """
        Add context menu entry to registry.

        Args:
            registry_path: Registry path for the entry
            command: Command to execute
            mui_verb: Display name for the menu item
            icon_path: Optional icon path

        Returns:
            True if successful, False otherwise

        Raises:
            ValidationError: If parameters are invalid
            RegistryError: If registry operation fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not registry_path:
                raise ValidationError(
                    "registry_entry",
                    "registry_path",
                    "Registry path cannot be None or empty",
                )

            if not command:
                raise ValidationError(
                    "registry_entry", "command", "Command cannot be None or empty"
                )

            if not mui_verb:
                raise ValidationError(
                    "registry_entry", "mui_verb", "Display name cannot be None or empty"
                )

            if not isinstance(registry_path, str):
                raise ValidationError(
                    "registry_entry",
                    "registry_path",
                    f"Registry path must be a string, got {type(registry_path).__name__}",
                )

            if not isinstance(command, str):
                raise ValidationError(
                    "registry_entry",
                    "command",
                    f"Command must be a string, got {type(command).__name__}",
                )

            if not isinstance(mui_verb, str):
                raise ValidationError(
                    "registry_entry",
                    "mui_verb",
                    f"Display name must be a string, got {type(mui_verb).__name__}",
                )

            if icon_path is not None and not isinstance(icon_path, str):
                raise ValidationError(
                    "registry_entry",
                    "icon_path",
                    f"Icon path must be a string, got {type(icon_path).__name__}",
                )

            # Create the registry key
            try:
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, registry_path) as key:
                    # Set the display name
                    winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, mui_verb)

                    # Set the command
                    with winreg.CreateKey(key, "command") as cmd_key:
                        winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, command)

                    # Set icon if provided
                    if icon_path:
                        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_path)

                return True

            except (OSError, PermissionError) as e:
                raise RegistryError(
                    "add", registry_path, f"Failed to create registry entry: {e}"
                ) from e

        except (ValidationError, RegistryError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error adding registry entry: {e}",
                details=f"Registry path: {registry_path}, Command: {command}",
            ) from e

    @classmethod
    def remove_context_menu_entry(cls, registry_path: str) -> bool:
        """
        Remove context menu entry from registry.

        Args:
            registry_path: Registry path to remove

        Returns:
            True if successful, False otherwise

        Raises:
            ValidationError: If registry_path is invalid
            RegistryError: If registry operation fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not registry_path:
                raise ValidationError(
                    "registry_removal",
                    "registry_path",
                    "Registry path cannot be None or empty",
                )

            if not isinstance(registry_path, str):
                raise ValidationError(
                    "registry_removal",
                    "registry_path",
                    f"Registry path must be a string, got {type(registry_path).__name__}",
                )

            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, registry_path)
                return True
            except (OSError, PermissionError) as e:
                raise RegistryError(
                    "remove", registry_path, f"Failed to remove registry entry: {e}"
                ) from e

        except (ValidationError, RegistryError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error removing registry entry: {e}",
                details=f"Registry path: {registry_path}",
            ) from e

    @classmethod
    def list_context_menu_entries(
        cls, context_type: str = "directory"
    ) -> list[dict[str, str | None]]:
        """
        List context menu entries for given type.

        Args:
            context_type: Type of context to list

        Returns:
            List of registry entries

        Raises:
            ValidationError: If context_type is invalid
            RegistryError: If registry operation fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not context_type:
                raise ValidationError(
                    "registry_listing",
                    "context_type",
                    "Context type cannot be None or empty",
                )

            if not isinstance(context_type, str):
                raise ValidationError(
                    "registry_listing",
                    "context_type",
                    f"Context type must be a string, got {type(context_type).__name__}",
                )

            entries = []
            registry_path = cls.CONTEXT_PATHS.get(context_type)

            if not registry_path:
                return entries

            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path) as key:
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            entry_info = cls._get_entry_info(registry_path, subkey_name)
                            if entry_info:
                                entries.append(entry_info)
                            i += 1
                        except OSError:
                            break

            except (OSError, PermissionError) as e:
                raise RegistryError(
                    "list", registry_path, f"Failed to list registry entries: {e}"
                ) from e

            return entries

        except (ValidationError, RegistryError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error listing registry entries: {e}",
                details=f"Context type: {context_type}",
            ) from e

    @classmethod
    def _get_entry_info(
        cls, base_path: str, key_name: str
    ) -> dict[str, str | None] | None:
        """
        Get information about a specific registry entry.

        Args:
            base_path: Base registry path
            key_name: Registry key name

        Returns:
            Entry information dictionary or None if failed

        Raises:
            RegistryError: If registry operation fails
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

        except (OSError, PermissionError) as e:
            # Log warning but don't raise exception for individual entry failures
            logging.getLogger(__name__).warning(
                f"Failed to get entry info for {key_name}: {e}"
            )
            return None
        except Exception as e:
            # Log warning for unexpected errors
            logging.getLogger(__name__).warning(
                f"Unexpected error getting entry info for {key_name}: {e}"
            )
            return None

    @classmethod
    def backup_registry_entries(
        cls, context_types: list[str] | None = None
    ) -> dict[str, str | None | dict[str, list]]:
        """
        Backup context menu entries to dictionary.

        Args:
            context_types: List of context types to backup

        Returns:
            Backup data dictionary

        Raises:
            ValidationError: If context_types is invalid
            RegistryError: If registry operation fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if context_types is not None and not isinstance(context_types, list):
                raise ValidationError(
                    "registry_backup",
                    "context_types",
                    f"Context types must be a list, got {type(context_types).__name__}",
                )

            if context_types is None:
                context_types = ["directory", "background"]

            backup_data = {
                "timestamp": None,
                "context_types": {},
            }

            for context_type in context_types:
                try:
                    entries = cls.list_context_menu_entries(context_type)
                    backup_data["context_types"][context_type] = entries
                except Exception as e:
                    # Log warning but continue with other context types
                    logging.getLogger(__name__).warning(
                        f"Failed to backup context type {context_type}: {e}"
                    )
                    backup_data["context_types"][context_type] = []

            return backup_data

        except (ValidationError, RegistryError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error backing up registry entries: {e}",
                details=f"Context types: {context_types}",
            ) from e

    @classmethod
    def restore_registry_entries(
        cls, backup_data: dict[str, str | None | dict[str, list]]
    ) -> bool:
        """
        Restore context menu entries from backup data.

        Args:
            backup_data: Backup data dictionary

        Returns:
            True if successful, False otherwise

        Raises:
            ValidationError: If backup_data is invalid
            RegistryError: If registry operation fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not backup_data:
                raise ValidationError(
                    "registry_restore",
                    "backup_data",
                    "Backup data cannot be None or empty",
                )

            if not isinstance(backup_data, dict):
                raise ValidationError(
                    "registry_restore",
                    "backup_data",
                    f"Backup data must be a dictionary, got {type(backup_data).__name__}",
                )

            try:
                for _context_type, entries in backup_data.get(
                    "context_types", {}
                ).items():
                    for entry in entries:
                        registry_path = entry.get("registry_path")
                        command = entry.get("command")
                        display_name = entry.get("display_name")
                        icon = entry.get("icon")

                        if registry_path and command and display_name:
                            cls.add_context_menu_entry(
                                registry_path, command, display_name, icon
                            )

                return True

            except (OSError, PermissionError) as e:
                raise RegistryError(
                    "restore", "backup_data", f"Failed to restore registry entries: {e}"
                ) from e

        except (ValidationError, RegistryError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error restoring registry entries: {e}",
                details="Failed to restore from backup data",
            ) from e

    @classmethod
    def get_context_path(cls, context_type: str) -> str | None:
        """
        Get registry path for context type.

        Args:
            context_type: Type of context

        Returns:
            Registry path or None if not found

        Raises:
            ValidationError: If context_type is invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not context_type:
                raise ValidationError(
                    "context_path",
                    "context_type",
                    "Context type cannot be None or empty",
                )

            if not isinstance(context_type, str):
                raise ValidationError(
                    "context_path",
                    "context_type",
                    f"Context type must be a string, got {type(context_type).__name__}",
                )

            return cls.CONTEXT_PATHS.get(context_type)

        except ValidationError:
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error getting context path: {e}",
                details=f"Context type: {context_type}",
            ) from e

    @classmethod
    def get_supported_context_types(cls) -> list[str]:
        """
        Get list of supported context types.

        Returns:
            List of supported context types

        Raises:
            ContextUtilityError: For unexpected errors
        """
        try:
            return list(cls.CONTEXT_PATHS.keys())
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error getting supported context types: {e}",
                details="Failed to get context paths keys",
            ) from e
