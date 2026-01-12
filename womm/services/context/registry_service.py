#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT REGISTRY SERVICE - Context Menu Registry Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Context Registry Service - Singleton service for context menu registry operations.

This module provides low-level registry operations for managing
Windows context menu entries.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import winreg
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.common import ValidationServiceError
from ...exceptions.context import ContextUtilityError
from ...exceptions.system import RegistryServiceError
from ...shared.configs.context.context_config import ContextConfig
from ...shared.result_models import ContextRegistryResult
from ...utils.context import (
    generate_registry_key_name,
    get_registry_entry_info,
)

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# CONTEXT REGISTRY SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class ContextRegistryService:
    """Singleton service for context menu registry operations."""

    _instance: ClassVar[ContextRegistryService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> ContextRegistryService:
        """Create or return the singleton instance.

        Returns:
            ContextRegistryService: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize context registry service (only once)."""
        if ContextRegistryService._initialized:
            return

        self.logger = logging.getLogger(__name__)
        ContextRegistryService._initialized = True

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def generate_registry_key_name(self, file_path: str) -> str:
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
        return generate_registry_key_name(file_path)

    def add_context_menu_entry(
        self,
        registry_path: str,
        command: str,
        mui_verb: str,
        icon_path: str | None = None,
    ) -> ContextRegistryResult:
        """
        Add context menu entry to registry.

        Args:
            registry_path: Registry path for the entry
            command: Command to execute
            mui_verb: Display name for the menu item
            icon_path: Optional icon path

        Returns:
            ContextRegistryResult: Result of the operation

        Raises:
            ValidationError: If parameters are invalid
            RegistryError: If registry operation fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not registry_path:
                raise ValidationServiceError(
                    "registry_entry",
                    "registry_path",
                    "Registry path cannot be None or empty",
                )

            if not command:
                raise ValidationServiceError(
                    "registry_entry", "command", "Command cannot be None or empty"
                )

            if not mui_verb:
                raise ValidationServiceError(
                    "registry_entry", "mui_verb", "Display name cannot be None or empty"
                )

            if not isinstance(registry_path, str):
                raise ValidationServiceError(
                    "registry_entry",
                    "registry_path",
                    f"Registry path must be a string, got {type(registry_path).__name__}",
                )

            if not isinstance(command, str):
                raise ValidationServiceError(
                    "registry_entry",
                    "command",
                    f"Command must be a string, got {type(command).__name__}",
                )

            if not isinstance(mui_verb, str):
                raise ValidationServiceError(
                    "registry_entry",
                    "mui_verb",
                    f"Display name must be a string, got {type(mui_verb).__name__}",
                )

            if icon_path is not None and not isinstance(icon_path, str):
                raise ValidationServiceError(
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

                return ContextRegistryResult(
                    success=True,
                    message=f"Context menu entry added successfully: {mui_verb}",
                    registry_path=registry_path,
                    command=command,
                    display_name=mui_verb,
                    icon_path=icon_path,
                )

            except (OSError, PermissionError) as e:
                raise RegistryServiceError(
                    "add", registry_path, f"Failed to create registry entry: {e}"
                ) from e

        except (ValidationServiceError, RegistryServiceError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error adding registry entry: {e}",
                details=f"Registry path: {registry_path}, Command: {command}",
            ) from e

    def remove_context_menu_entry(self, registry_path: str) -> ContextRegistryResult:
        """
        Remove context menu entry from registry.

        Args:
            registry_path: Registry path to remove

        Returns:
            ContextRegistryResult: Result of the operation

        Raises:
            ValidationError: If registry_path is invalid
            RegistryError: If registry operation fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not registry_path:
                raise ValidationServiceError(
                    "registry_removal",
                    "registry_path",
                    "Registry path cannot be None or empty",
                )

            if not isinstance(registry_path, str):
                raise ValidationServiceError(
                    "registry_removal",
                    "registry_path",
                    f"Registry path must be a string, got {type(registry_path).__name__}",
                )

            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, registry_path)
                return ContextRegistryResult(
                    success=True,
                    message=f"Context menu entry removed successfully: {registry_path}",
                    registry_path=registry_path,
                )
            except (OSError, PermissionError) as e:
                raise RegistryServiceError(
                    "remove", registry_path, f"Failed to remove registry entry: {e}"
                ) from e

        except (ValidationServiceError, RegistryServiceError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error removing registry entry: {e}",
                details=f"Registry path: {registry_path}",
            ) from e

    def list_context_menu_entries(
        self, context_type: str = "directory"
    ) -> ContextRegistryResult:
        """
        List context menu entries for given type.

        Args:
            context_type: Type of context to list

        Returns:
            ContextRegistryResult: Result with list of entries

        Raises:
            ValidationError: If context_type is invalid
            RegistryError: If registry operation fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not context_type:
                raise ValidationServiceError(
                    "registry_listing",
                    "context_type",
                    "Context type cannot be None or empty",
                )

            if not isinstance(context_type, str):
                raise ValidationServiceError(
                    "registry_listing",
                    "context_type",
                    f"Context type must be a string, got {type(context_type).__name__}",
                )

            entries = []
            registry_path = ContextConfig.CONTEXT_PATHS.get(context_type)

            if not registry_path:
                return ContextRegistryResult(
                    success=True,
                    message=f"No entries found for context type: {context_type}",
                    registry_path="",
                    entries=[],
                )

            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path) as key:
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            entry_info = get_registry_entry_info(
                                registry_path, subkey_name
                            )
                            if entry_info:
                                entries.append(entry_info)
                            i += 1
                        except OSError:
                            break

            except (OSError, PermissionError) as e:
                raise RegistryServiceError(
                    "list", registry_path, f"Failed to list registry entries: {e}"
                ) from e

            return ContextRegistryResult(
                success=True,
                message=f"Found {len(entries)} entries for context type: {context_type}",
                registry_path=registry_path,
                entries=entries,
            )

        except (ValidationServiceError, RegistryServiceError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error listing registry entries: {e}",
                details=f"Context type: {context_type}",
            ) from e

    def backup_registry_entries(
        self, context_types: list[str] | None = None
    ) -> ContextRegistryResult:
        """
        Backup context menu entries to dictionary.

        Args:
            context_types: List of context types to backup

        Returns:
            ContextRegistryResult: Result with backup data

        Raises:
            ValidationError: If context_types is invalid
            RegistryError: If registry operation fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if context_types is not None and not isinstance(context_types, list):
                raise ValidationServiceError(
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
                    entries_result = self.list_context_menu_entries(context_type)
                    if entries_result.success and entries_result.entries:
                        backup_data["context_types"][context_type] = (
                            entries_result.entries
                        )
                    else:
                        backup_data["context_types"][context_type] = []
                except Exception as e:
                    # Log warning but continue with other context types
                    logging.getLogger(__name__).warning(
                        f"Failed to backup context type {context_type}: {e}"
                    )
                    backup_data["context_types"][context_type] = []

            return ContextRegistryResult(
                success=True,
                message=f"Backup completed for {len(context_types)} context types",
                backup_data=backup_data,
            )

        except (ValidationServiceError, RegistryServiceError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error backing up registry entries: {e}",
                details=f"Context types: {context_types}",
            ) from e

    def restore_registry_entries(
        self, backup_data: dict[str, str | None | dict[str, list]]
    ) -> ContextRegistryResult:
        """
        Restore context menu entries from backup data.

        Args:
            backup_data: Backup data dictionary

        Returns:
            ContextRegistryResult: Result of the operation

        Raises:
            ValidationError: If backup_data is invalid
            RegistryError: If registry operation fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not backup_data:
                raise ValidationServiceError(
                    "registry_restore",
                    "backup_data",
                    "Backup data cannot be None or empty",
                )

            if not isinstance(backup_data, dict):
                raise ValidationServiceError(
                    "registry_restore",
                    "backup_data",
                    f"Backup data must be a dictionary, got {type(backup_data).__name__}",
                )

            restored_count = 0
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
                            result = self.add_context_menu_entry(
                                registry_path, command, display_name, icon
                            )
                            if result.success:
                                restored_count += 1

                return ContextRegistryResult(
                    success=True,
                    message=f"Restored {restored_count} registry entries",
                    backup_data=backup_data,
                )

            except (OSError, PermissionError) as e:
                raise RegistryServiceError(
                    "restore", "backup_data", f"Failed to restore registry entries: {e}"
                ) from e

        except (ValidationServiceError, RegistryServiceError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error restoring registry entries: {e}",
                details="Failed to restore from backup data",
            ) from e

    def get_context_path(self, context_type: str) -> str | None:
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
                raise ValidationServiceError(
                    "context_path",
                    "context_type",
                    "Context type cannot be None or empty",
                )

            if not isinstance(context_type, str):
                raise ValidationServiceError(
                    "context_path",
                    "context_type",
                    f"Context type must be a string, got {type(context_type).__name__}",
                )

            return ContextConfig.CONTEXT_PATHS.get(context_type)

        except ValidationServiceError:
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error getting context path: {e}",
                details=f"Context type: {context_type}",
            ) from e

    def get_supported_context_types(self) -> list[str]:
        """
        Get list of supported context types.

        Returns:
            List of supported context types

        Raises:
            ContextUtilityError: For unexpected errors
        """
        try:
            return list(ContextConfig.CONTEXT_PATHS.keys())
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error getting supported context types: {e}",
                details="Failed to get context paths keys",
            ) from e
