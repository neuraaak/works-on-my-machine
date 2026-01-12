#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT MENU MANAGER - Windows Context Menu Management
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Context menu manager.

This module orchestrates context menu operations using the modular architecture.
It coordinates ScriptDetector, IconManager, and ContextRegistryService to provide
a unified interface for context menu management.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path

# Local imports
from ...exceptions.context import (
    ContextUtilityError,
    MenuInterfaceError,
    ScriptDetectorInterfaceError,
    ValidationInterfaceError,
)
from ...exceptions.system import RegistryServiceError
from ...services import (
    ContextParametersService,
    ContextRegistryService,
    ContextType,
    ContextValidationService,
)
from ...shared.configs.context import ContextTypesConfig
from ...shared.result_models import ContextValidationResult
from .icon_interface import ContextIconInterface
from .registry_interface import ContextRegistryInterface
from .script_detector_interface import ContextScriptDetectorInterface, ScriptType

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class ContextMenuInterface:
    """Context menu manager - orchestrates all context menu operations."""

    def __init__(self):
        """Initialize the context menu manager with all required components."""
        self.logger = logging.getLogger(__name__)
        self._script_detector: ContextScriptDetectorInterface | None = None
        self._icon_manager: ContextIconInterface | None = None
        self._registry_service: ContextRegistryService | None = None
        self._backup_manager: ContextRegistryInterface | None = None
        self._validation_service: ContextValidationService | None = None

    # ///////////////////////////////////////////////////////////////
    # SERVICE PROPERTIES (LAZY INITIALIZATION)
    # ///////////////////////////////////////////////////////////////

    @property
    def script_detector(self) -> ContextScriptDetectorInterface:
        """Lazy load ContextScriptDetectorInterface when needed."""
        if self._script_detector is None:
            self._script_detector = ContextScriptDetectorInterface()
        return self._script_detector

    @property
    def icon_manager(self) -> ContextIconInterface:
        """Lazy load ContextIconInterface when needed."""
        if self._icon_manager is None:
            self._icon_manager = ContextIconInterface()
        return self._icon_manager

    @property
    def registry_service(self) -> ContextRegistryService:
        """Lazy load ContextRegistryService when needed."""
        if self._registry_service is None:
            self._registry_service = ContextRegistryService()
        return self._registry_service

    @property
    def backup_manager(self) -> ContextRegistryInterface:
        """Lazy load ContextRegistryInterface when needed."""
        if self._backup_manager is None:
            self._backup_manager = ContextRegistryInterface()
        return self._backup_manager

    @property
    def validation_service(self) -> ContextValidationService:
        """Lazy load ContextValidationService when needed."""
        if self._validation_service is None:
            self._validation_service = ContextValidationService()
        return self._validation_service

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def register_script(
        self,
        script_path: str,
        label: str,
        icon: str | None = None,
        dry_run: bool = False,
        context_params: ContextParametersService | None = None,
    ) -> dict[str, object]:
        """
        Register a script in the Windows context menu.

        Args:
            script_path: Path to the script or executable
            label: Display name in context menu
            icon: Icon path or 'auto' for auto-detection
            dry_run: If True, show what would be done without making changes
            context_params: Context parameters for registration

        Returns:
            Dict containing operation result and details

        Raises:
            ValidationError: If parameters are invalid
            ScriptError: If script detection fails
            RegistryError: If registry operations fail
            ContextMenuError: If registration fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not script_path:
                raise ValidationInterfaceError(
                    "script_registration",
                    "script_path",
                    "Script path cannot be None or empty",
                )

            if not label:
                raise ValidationInterfaceError(
                    "script_registration", "label", "Label cannot be None or empty"
                )

            # Comprehensive validation using ContextValidationService
            try:
                validation_result = self.validation_service.validate_command_parameters(
                    script_path, label, icon
                )
                if not validation_result["valid"]:
                    error_message = "; ".join(validation_result["errors"])
                    raise ValidationInterfaceError(
                        "script_registration",
                        "parameters",
                        f"Validation failed: {error_message}",
                    )
            except Exception as e:
                if isinstance(e, ValidationInterfaceError):
                    raise
                raise ValidationInterfaceError(
                    "script_registration",
                    "validation",
                    f"Validation process failed: {e}",
                ) from e

            # Detect script type and get info
            try:
                script_info = ContextScriptDetectorInterface.get_script_info(
                    script_path
                )
                script_type = script_info["type"]
            except Exception as e:
                raise ScriptDetectorInterfaceError(
                    "detect", script_path, f"Failed to detect script type: {e}"
                ) from e

            # Resolve icon
            try:
                icon_path = self.icon_manager.resolve_icon(icon or "auto", script_path)
                if icon_path is None and icon and icon.lower() != "auto":
                    # Fallback to default icon for script type
                    icon_path = script_info["default_icon"]
            except Exception as e:
                self.logger.warning(f"Failed to resolve icon for {script_path}: {e}")
                icon_path = None

            # Generate registry key name
            try:
                registry_key_name = self.registry_service.generate_registry_key_name(
                    script_path
                )
            except Exception as e:
                raise RegistryServiceError(
                    "generate_key",
                    script_path,
                    f"Failed to generate registry key name: {e}",
                ) from e

            # Build command
            command = script_info["command"]

            # Use context parameters if provided, otherwise use defaults
            if context_params is None:
                try:
                    context_params = (
                        self.registry_service.from_flags()
                        if hasattr(self.registry_service, "from_flags")
                        else ContextParametersService()
                    )
                except Exception as e:
                    raise ContextUtilityError(
                        f"Failed to create default context parameters: {e}",
                        details=f"Script path: {script_path}",
                    ) from e

            # Validate context parameters
            try:
                validation = context_params.validate_parameters()
                if not validation["valid"]:
                    raise ValidationInterfaceError(
                        "context_parameters",
                        "validation",
                        f"Context parameter validation failed: {'; '.join(validation['errors'])}",
                    )

                # Show warnings if any
                if validation["warnings"]:
                    self.logger.warning(
                        f"Context parameter warnings: {'; '.join(validation['warnings'])}"
                    )
            except Exception as e:
                if isinstance(e, ValidationInterfaceError):
                    raise
                raise ValidationInterfaceError(
                    "context_parameters",
                    "validation",
                    f"Context parameter validation process failed: {e}",
                ) from e

            # Build final command for display (use first context type for dry-run)
            context_types = list(context_params.context_types)
            if context_types:
                final_command = context_params.build_command(command, context_types[0])
            else:
                final_command = command

            # Prepare result info
            result_info = {
                "script_path": script_path,
                "script_type": script_type,
                "label": label,
                "icon_path": icon_path,
                "registry_key": registry_key_name,
                "command": final_command,
                "context_info": context_params.get_description(),
            }

            if dry_run:
                return {
                    "success": True,
                    "dry_run": True,
                    "info": result_info,
                }

            # Get registry paths and add entries
            try:
                registry_paths = context_params.get_registry_paths()
            except Exception as e:
                raise RegistryServiceError(
                    "get_paths", "context_params", f"Failed to get registry paths: {e}"
                ) from e

            success_count = 0
            total_paths = len(registry_paths)

            for registry_path in registry_paths:
                full_path = f"{registry_path}\\{registry_key_name}"

                # Build command with appropriate parameters for this context type
                context_type = self._get_context_type_from_path(registry_path)
                final_command = context_params.build_command(command, context_type)

                try:
                    success = self.registry_service.add_context_menu_entry(
                        full_path,
                        final_command,
                        label,
                        icon_path,
                    )
                except Exception as e:
                    self.logger.warning(
                        f"Failed to add registry entry {full_path}: {e}"
                    )
                    success = False

                if success:
                    success_count += 1

            if success_count == total_paths:
                return {
                    "success": True,
                    "info": result_info,
                }
            else:
                raise MenuInterfaceError(
                    "register",
                    script_path,
                    f"Failed to add registry entries ({success_count}/{total_paths} succeeded)",
                )

        except (
            ValidationInterfaceError,
            ScriptDetectorInterfaceError,
            RegistryServiceError,
            MenuInterfaceError,
        ):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error during script registration: {e}",
                details=f"Script path: {script_path}, Label: {label}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _get_context_type_from_path(self, registry_path: str) -> ContextType:
        """
        Determine context type from registry path.

        Args:
            registry_path: Registry path

        Returns:
            ContextType enum value

        Raises:
            ContextUtilityError: For unexpected errors
        """
        try:
            if (
                ContextTypesConfig.REGISTRY_PATTERN_DIRECTORY_SHELL in registry_path
                and "background" not in registry_path
            ):
                return ContextType.DIRECTORY
            elif (
                ContextTypesConfig.REGISTRY_PATTERN_DIRECTORY_BACKGROUND
                in registry_path
            ):
                return ContextType.BACKGROUND
            elif ContextTypesConfig.REGISTRY_PATTERN_DRIVE_SHELL in registry_path:
                return ContextType.ROOT
            elif ContextTypesConfig.REGISTRY_PATTERN_FILE_SHELL in registry_path:
                return ContextType.FILE
            else:
                return ContextType.DIRECTORY  # Default fallback
        except Exception as e:
            raise ContextUtilityError(
                f"Failed to determine context type from registry path: {e}",
                details=f"Registry path: {registry_path}",
            ) from e

    def unregister_script(
        self, key_name: str, dry_run: bool = False
    ) -> dict[str, object]:
        """
        Unregister a script from the Windows context menu.

        Args:
            key_name: Registry key name to remove
            dry_run: If True, show what would be done without making changes

        Returns:
            Dict containing operation result

        Raises:
            ValidationError: If key_name is invalid
            RegistryError: If registry operations fail
            ContextMenuError: If unregistration fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not key_name:
                raise ValidationInterfaceError(
                    "script_unregistration",
                    "key_name",
                    "Registry key name cannot be None or empty",
                )

            if dry_run:
                return {
                    "success": True,
                    "dry_run": True,
                    "key_name": key_name,
                }

            # Try to remove from both context types
            success = False
            for context_type in ContextTypesConfig.ALL_TYPES:
                try:
                    registry_path = self.registry_service.get_context_path(context_type)
                    if registry_path:
                        full_path = f"{registry_path}\\{key_name}"
                        if self.registry_service.remove_context_menu_entry(full_path):
                            success = True
                except Exception as e:
                    self.logger.warning(f"Failed to remove from {context_type}: {e}")

            if success:
                return {
                    "success": True,
                    "key_name": key_name,
                }
            else:
                raise MenuInterfaceError(
                    "unregister", key_name, "Entry not found in any context type"
                )

        except (
            ValidationInterfaceError,
            RegistryServiceError,
            MenuInterfaceError,
        ):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error during script unregistration: {e}",
                details=f"Key name: {key_name}",
            ) from e

    def list_entries(self) -> dict[str, object]:
        """
        List all registered context menu entries.

        Returns:
            Dict containing all entries organized by context type

        Raises:
            RegistryError: If registry access fails
            ContextUtilityError: For unexpected errors
        """
        try:
            all_entries = {}

            for context_type in ContextTypesConfig.ALL_TYPES:
                try:
                    entries = self.registry_service.list_context_menu_entries(
                        context_type
                    )
                    all_entries[context_type] = entries
                except Exception as e:
                    self.logger.warning(
                        f"Failed to list entries for {context_type}: {e}"
                    )
                    all_entries[context_type] = []

            return {
                "success": True,
                "entries": all_entries,
            }

        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error listing context menu entries: {e}",
                details="Registry access failed",
            ) from e

    def backup_entries(self, backup_file: str) -> dict[str, object]:
        """
        Backup current context menu entries.

        Args:
            backup_file: Path to save the backup file

        Returns:
            Dict containing operation result

        Raises:
            ValidationError: If backup_file is invalid
            ContextMenuError: If backup operation fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not backup_file:
                raise ValidationInterfaceError(
                    "backup_operation",
                    "backup_file",
                    "Backup file path cannot be None or empty",
                )

            # Get current entries
            try:
                entries_result = self.list_entries()
                entries = entries_result["entries"]
            except Exception as e:
                raise MenuInterfaceError(
                    "backup", "entries", f"Failed to get current entries: {e}"
                ) from e

            # Use BackupManager to create backup
            try:
                success, filepath, metadata = self.backup_manager.create_backup_file(
                    entries, custom_filename=Path(backup_file).stem, add_timestamp=False
                )
            except Exception as e:
                raise MenuInterfaceError(
                    "backup", backup_file, f"Failed to create backup: {e}"
                ) from e

            if success:
                return {
                    "success": True,
                    "backup_file": filepath,
                    "entry_count": metadata.get("total_entries", 0),
                }
            else:
                raise MenuInterfaceError(
                    "backup", backup_file, f"Backup creation failed: {filepath}"
                )

        except (ValidationInterfaceError, MenuInterfaceError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error during backup operation: {e}",
                details=f"Backup file: {backup_file}",
            ) from e

    def restore_entries(self, backup_file: str) -> dict[str, object]:
        """
        Restore context menu entries from backup.

        Args:
            backup_file: Path to the backup file

        Returns:
            Dict containing operation result

        Raises:
            ValidationError: If backup_file is invalid
            ContextMenuError: If restore operation fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not backup_file:
                raise ValidationInterfaceError(
                    "restore_operation",
                    "backup_file",
                    "Backup file path cannot be None or empty",
                )

            # Use BackupManager to load and validate backup
            try:
                success, data, error = self.backup_manager.load_backup_file(backup_file)
                if not success:
                    raise MenuInterfaceError(
                        "restore", backup_file, f"Failed to load backup: {error}"
                    )
            except Exception as e:
                if isinstance(e, MenuInterfaceError):
                    raise
                raise MenuInterfaceError(
                    "restore", backup_file, f"Backup loading failed: {e}"
                ) from e

            # Restore entries using RegistryService
            try:
                success = self.registry_service.restore_registry_entries(data)
            except Exception as e:
                raise MenuInterfaceError(
                    "restore", backup_file, f"Failed to restore registry entries: {e}"
                ) from e

            if success:
                return {
                    "success": True,
                    "backup_file": backup_file,
                    "entry_count": data.get("metadata", {}).get("total_entries", 0),
                }
            else:
                raise MenuInterfaceError(
                    "restore", backup_file, "Registry restoration failed"
                )

        except (ValidationInterfaceError, MenuInterfaceError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error during restore operation: {e}",
                details=f"Backup file: {backup_file}",
            ) from e

    def get_script_info(self, script_path: str) -> dict[str, object]:
        """
        Get comprehensive information about a script.

        Args:
            script_path: Path to the script

        Returns:
            Dict containing script information

        Raises:
            ValidationError: If script_path is invalid
            ScriptError: If script detection fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not script_path:
                raise ValidationInterfaceError(
                    "script_info", "script_path", "Script path cannot be None or empty"
                )

            # Get script info
            try:
                script_info = ContextScriptDetectorInterface.get_script_info(
                    script_path
                )
            except Exception as e:
                raise ScriptDetectorInterfaceError(
                    "get_info", script_path, f"Failed to get script information: {e}"
                ) from e

            # Add icon information
            try:
                icon_path = self.icon_manager.resolve_icon("auto", script_path)
                script_info["resolved_icon"] = icon_path
            except Exception as e:
                self.logger.warning(f"Failed to resolve icon for {script_path}: {e}")
                script_info["resolved_icon"] = None

            # Add registry key name
            try:
                registry_key = self.registry_service.generate_registry_key_name(
                    script_path
                )
                script_info["registry_key"] = registry_key
            except Exception as e:
                self.logger.warning(
                    f"Failed to generate registry key for {script_path}: {e}"
                )
                script_info["registry_key"] = None

            return {
                "success": True,
                "info": script_info,
            }

        except (ValidationInterfaceError, ScriptDetectorInterfaceError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error getting script info: {e}",
                details=f"Script path: {script_path}",
            ) from e

    def validate_script(self, script_path: str) -> dict[str, object]:
        """
        Validate if a script can be registered in context menu.

        Args:
            script_path: Path to the script

        Returns:
            Dict containing validation result

        Raises:
            ValidationError: If script_path is invalid or validation fails
            ScriptError: If script detection fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not script_path:
                raise ValidationInterfaceError(
                    "script_validation",
                    "script_path",
                    "Script path cannot be None or empty",
                )

            # Use ContextValidationService for comprehensive validation
            try:
                validation_result = self.validation_service.validate_script_path(
                    script_path
                )
                if not validation_result.is_valid:
                    raise ValidationInterfaceError(
                        "script_validation",
                        "script_path",
                        validation_result.error or "Validation failed",
                    )
            except Exception as e:
                if isinstance(e, ValidationInterfaceError):
                    raise
                raise ValidationInterfaceError(
                    "script_validation",
                    "validation_process",
                    f"Validation process failed: {e}",
                ) from e

            # Get script info
            try:
                script_info = ContextScriptDetectorInterface.get_script_info(
                    script_path
                )
                script_type = script_info["type"]
            except Exception as e:
                raise ScriptDetectorInterfaceError(
                    "validate",
                    script_path,
                    f"Failed to get script info during validation: {e}",
                ) from e

            # Check if script type is supported
            if script_type == ScriptType.UNKNOWN:
                raise ValidationInterfaceError(
                    "script_validation",
                    "script_type",
                    f"Unsupported script type: {Path(script_path).suffix}",
                )

            # Check if command can be built
            command = script_info["command"]
            if not command:
                raise ValidationInterfaceError(
                    "script_validation", "command", "Could not build execution command"
                )

            # Check permissions and compatibility
            try:
                permission_check = self.validation_service.check_permissions()
                compatibility_check = (
                    self.validation_service.validate_windows_compatibility()
                )
            except Exception as e:
                self.logger.warning(f"Failed to check permissions/compatibility: {e}")
                permission_check = ContextValidationResult(is_valid=False, error=str(e))
                compatibility_check = ContextValidationResult(
                    is_valid=False, error=str(e)
                )

            return {
                "valid": True,
                "script_type": script_type,
                "command": command,
                "validation_details": validation_result,
                "permissions": permission_check,
                "compatibility": compatibility_check,
            }

        except (ValidationInterfaceError, ScriptDetectorInterfaceError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error during script validation: {e}",
                details=f"Script path: {script_path}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PLATFORM AND UTILITY METHODS
    # ///////////////////////////////////////////////////////////////

    def is_windows(self) -> bool:
        """Check if running on Windows platform."""
        import platform

        return platform.system().lower() == "windows"

    def get_backup_directory(self) -> Path:
        """Get the backup directory path, creating it if needed."""
        return self.backup_manager._get_backup_directory()

    def collect_entries_from_backups(self) -> list[dict]:
        """
        Collect all unique context menu entries from backup files.

        Returns:
            List of unique entries with metadata
        """
        import json

        backup_dir = self.get_backup_directory()
        all_entries: dict[str, dict] = {}
        backup_files = sorted(backup_dir.glob("context_menu_backup_*.json"))

        for backup_file in backup_files:
            try:
                with open(backup_file, encoding="utf-8") as f:
                    data = json.load(f)

                entries = data.get("entries", [])
                for entry in entries:
                    key_name = entry.get("key_name")
                    if key_name and key_name not in all_entries:
                        entry["_source_backup"] = backup_file.name
                        entry["_display_name"] = self._format_entry_display(entry)
                        all_entries[key_name] = entry

            except Exception as e:
                self.logger.debug(f"Error reading {backup_file.name}: {e}")

        return list(all_entries.values())

    def _format_entry_display(self, entry: dict) -> str:
        """Format entry for display in selection menu."""
        import re

        key_name = entry.get("key_name", "Unknown")
        properties = entry.get("properties", {})

        display_text = properties.get("MUIVerb") or properties.get("@", key_name)

        command = properties.get("Command", "")
        if command:
            exe_match = re.search(r'"([^"]*\.exe)"', command)
            if exe_match:
                exe_name = Path(exe_match.group(1)).name
                display_text = f"{display_text} ({exe_name})"

        return f"{display_text} [key: {key_name}]"

    def get_current_entry_keys(self) -> set[str]:
        """
        Get set of currently installed context menu entry keys.

        Returns:
            Set of key names currently installed
        """
        try:
            result = self.list_entries()
            if result["success"]:
                entries = result["entries"]
                current_keys = set()
                for context_type in ["directory", "background"]:
                    for entry in entries.get(context_type, []):
                        key_name = entry.get("key_name")
                        if key_name:
                            current_keys.add(key_name)
                return current_keys
        except Exception as e:
            self.logger.debug(f"Error checking current entries: {e}")
        return set()

    def filter_available_entries(
        self, all_entries: list[dict], current_keys: set[str]
    ) -> list[dict]:
        """
        Filter out entries that are already installed.

        Args:
            all_entries: All entries from backups
            current_keys: Set of currently installed entry keys

        Returns:
            List of entries not yet installed
        """
        return [
            entry
            for entry in all_entries
            if entry.get("key_name") and entry.get("key_name") not in current_keys
        ]

    def apply_cherry_picked_entries(
        self, selected_entries: list[dict]
    ) -> dict[str, bool]:
        """
        Apply selected context menu entries.

        Args:
            selected_entries: List of entries to apply

        Returns:
            Dict mapping key names to success status
        """
        results = {}

        for entry in selected_entries:
            key_name = entry.get("key_name")
            properties = entry.get("properties", {})
            command = properties.get("Command", "")
            muiverb = properties.get("MUIVerb")
            icon = properties.get("Icon")

            if not command:
                self.logger.warning(f"Skipping {key_name}: no command found")
                results[key_name] = False
                continue

            # Extract script path from command
            script_path = None
            if '"' in command:
                script_match = command.split('"')[1]
                if script_match and Path(script_match).exists():
                    script_path = script_match

            if not script_path:
                self.logger.warning(
                    f"Skipping {key_name}: could not extract script path"
                )
                results[key_name] = False
                continue

            # Execute registration
            result = self.register_script(
                script_path, muiverb or key_name, icon or "auto"
            )
            results[key_name] = result.get("success", False)

        return results
