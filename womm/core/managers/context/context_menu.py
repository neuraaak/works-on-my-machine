#!/usr/bin/env python3
"""
Context menu manager.

This module orchestrates context menu operations using the modular architecture.
It coordinates ScriptDetector, IconManager, and RegistryUtils to provide
a unified interface for context menu management.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from ...exceptions.context.context_exceptions import (
    ContextMenuError,
    ContextUtilityError,
    RegistryError,
    ScriptError,
    ValidationError,
)
from ...utils.context.context_parameters import ContextParameters, ContextType
from ...utils.context.registry_utils import RegistryUtils
from ...utils.context.validation import ValidationUtils
from .backup_manager import BackupManager
from .icon_manager import IconManager
from .script_detector import ScriptDetector, ScriptType


class ContextMenuManager:
    """Context menu manager - orchestrates all context menu operations."""

    def __init__(self):
        """Initialize the context menu manager with all required components."""
        self.logger = logging.getLogger(__name__)
        self.script_detector = ScriptDetector()
        self.icon_manager = IconManager()
        self.registry_utils = RegistryUtils()
        self.backup_manager = BackupManager()
        self.validation_utils = ValidationUtils()

    def register_script(
        self,
        script_path: str,
        label: str,
        icon: Optional[str] = None,
        dry_run: bool = False,
        context_params: Optional[ContextParameters] = None,
    ) -> Dict[str, Any]:
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
                raise ValidationError(
                    "script_registration",
                    "script_path",
                    "Script path cannot be None or empty",
                )

            if not label:
                raise ValidationError(
                    "script_registration", "label", "Label cannot be None or empty"
                )

            # Comprehensive validation using ValidationUtils
            try:
                validation_result = ValidationUtils.validate_command_parameters(
                    script_path, label, icon
                )
                if not validation_result["valid"]:
                    error_message = "; ".join(validation_result["errors"])
                    raise ValidationError(
                        "script_registration",
                        "parameters",
                        f"Validation failed: {error_message}",
                    )
            except Exception as e:
                if isinstance(e, ValidationError):
                    raise
                raise ValidationError(
                    "script_registration",
                    "validation",
                    f"Validation process failed: {e}",
                ) from e

            # Detect script type and get info
            try:
                script_info = ScriptDetector.get_script_info(script_path)
                script_type = script_info["type"]
            except Exception as e:
                raise ScriptError(
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
                registry_key_name = self.registry_utils.generate_registry_key_name(
                    script_path
                )
            except Exception as e:
                raise RegistryError(
                    "generate_key",
                    script_path,
                    f"Failed to generate registry key name: {e}",
                ) from e

            # Build command
            command = script_info["command"]

            # Use context parameters if provided, otherwise use defaults
            if context_params is None:
                try:
                    context_params = ContextParameters.from_flags()
                except Exception as e:
                    raise ContextUtilityError(
                        f"Failed to create default context parameters: {e}",
                        details=f"Script path: {script_path}",
                    ) from e

            # Validate context parameters
            try:
                validation = context_params.validate_parameters()
                if not validation["valid"]:
                    raise ValidationError(
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
                if isinstance(e, ValidationError):
                    raise
                raise ValidationError(
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
                raise RegistryError(
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
                    success = self.registry_utils.add_context_menu_entry(
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
                raise ContextMenuError(
                    "register",
                    script_path,
                    f"Failed to add registry entries ({success_count}/{total_paths} succeeded)",
                )

        except (ValidationError, ScriptError, RegistryError, ContextMenuError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error during script registration: {e}",
                details=f"Script path: {script_path}, Label: {label}",
            ) from e

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
                "Directory\\shell" in registry_path
                and "background" not in registry_path
            ):
                return ContextType.DIRECTORY
            elif "Directory\\background" in registry_path:
                return ContextType.BACKGROUND
            elif "Drive\\shell" in registry_path:
                return ContextType.ROOT
            elif "*\\shell" in registry_path:
                return ContextType.FILE
            else:
                return ContextType.DIRECTORY  # Default fallback
        except Exception as e:
            raise ContextUtilityError(
                f"Failed to determine context type from registry path: {e}",
                details=f"Registry path: {registry_path}",
            ) from e

    def unregister_script(self, key_name: str, dry_run: bool = False) -> Dict[str, Any]:
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
                raise ValidationError(
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
            for context_type in ["directory", "background"]:
                try:
                    registry_path = self.registry_utils.get_context_path(context_type)
                    if registry_path:
                        full_path = f"{registry_path}\\{key_name}"
                        if self.registry_utils.remove_context_menu_entry(full_path):
                            success = True
                except Exception as e:
                    self.logger.warning(f"Failed to remove from {context_type}: {e}")

            if success:
                return {
                    "success": True,
                    "key_name": key_name,
                }
            else:
                raise ContextMenuError(
                    "unregister", key_name, "Entry not found in any context type"
                )

        except (ValidationError, RegistryError, ContextMenuError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error during script unregistration: {e}",
                details=f"Key name: {key_name}",
            ) from e

    def list_entries(self) -> Dict[str, Any]:
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

            for context_type in ["directory", "background"]:
                try:
                    entries = self.registry_utils.list_context_menu_entries(
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

    def backup_entries(self, backup_file: str) -> Dict[str, Any]:
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
                raise ValidationError(
                    "backup_operation",
                    "backup_file",
                    "Backup file path cannot be None or empty",
                )

            # Get current entries
            try:
                entries_result = self.list_entries()
                entries = entries_result["entries"]
            except Exception as e:
                raise ContextMenuError(
                    "backup", "entries", f"Failed to get current entries: {e}"
                ) from e

            # Use BackupManager to create backup
            try:
                success, filepath, metadata = self.backup_manager.create_backup_file(
                    entries, custom_filename=Path(backup_file).stem, add_timestamp=False
                )
            except Exception as e:
                raise ContextMenuError(
                    "backup", backup_file, f"Failed to create backup: {e}"
                ) from e

            if success:
                return {
                    "success": True,
                    "backup_file": filepath,
                    "entry_count": metadata.get("total_entries", 0),
                }
            else:
                raise ContextMenuError(
                    "backup", backup_file, f"Backup creation failed: {filepath}"
                )

        except (ValidationError, ContextMenuError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error during backup operation: {e}",
                details=f"Backup file: {backup_file}",
            ) from e

    def restore_entries(self, backup_file: str) -> Dict[str, Any]:
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
                raise ValidationError(
                    "restore_operation",
                    "backup_file",
                    "Backup file path cannot be None or empty",
                )

            # Use BackupManager to load and validate backup
            try:
                success, data, error = self.backup_manager.load_backup_file(backup_file)
                if not success:
                    raise ContextMenuError(
                        "restore", backup_file, f"Failed to load backup: {error}"
                    )
            except Exception as e:
                if isinstance(e, ContextMenuError):
                    raise
                raise ContextMenuError(
                    "restore", backup_file, f"Backup loading failed: {e}"
                ) from e

            # Restore entries using RegistryUtils
            try:
                success = self.registry_utils.restore_registry_entries(data)
            except Exception as e:
                raise ContextMenuError(
                    "restore", backup_file, f"Failed to restore registry entries: {e}"
                ) from e

            if success:
                return {
                    "success": True,
                    "backup_file": backup_file,
                    "entry_count": data.get("metadata", {}).get("total_entries", 0),
                }
            else:
                raise ContextMenuError(
                    "restore", backup_file, "Registry restoration failed"
                )

        except (ValidationError, ContextMenuError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error during restore operation: {e}",
                details=f"Backup file: {backup_file}",
            ) from e

    def get_script_info(self, script_path: str) -> Dict[str, Any]:
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
                raise ValidationError(
                    "script_info", "script_path", "Script path cannot be None or empty"
                )

            # Get script info
            try:
                script_info = ScriptDetector.get_script_info(script_path)
            except Exception as e:
                raise ScriptError(
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
                registry_key = self.registry_utils.generate_registry_key_name(
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

        except (ValidationError, ScriptError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error getting script info: {e}",
                details=f"Script path: {script_path}",
            ) from e

    def validate_script(self, script_path: str) -> Dict[str, Any]:
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
                raise ValidationError(
                    "script_validation",
                    "script_path",
                    "Script path cannot be None or empty",
                )

            # Use ValidationUtils for comprehensive validation
            try:
                validation_result = ValidationUtils.validate_script_path(script_path)
                if not validation_result["valid"]:
                    raise ValidationError(
                        "script_validation", "script_path", validation_result["error"]
                    )
            except Exception as e:
                if isinstance(e, ValidationError):
                    raise
                raise ValidationError(
                    "script_validation",
                    "validation_process",
                    f"Validation process failed: {e}",
                ) from e

            # Get script info
            try:
                script_info = ScriptDetector.get_script_info(script_path)
                script_type = script_info["type"]
            except Exception as e:
                raise ScriptError(
                    "validate",
                    script_path,
                    f"Failed to get script info during validation: {e}",
                ) from e

            # Check if script type is supported
            if script_type == ScriptType.UNKNOWN:
                raise ValidationError(
                    "script_validation",
                    "script_type",
                    f"Unsupported script type: {Path(script_path).suffix}",
                )

            # Check if command can be built
            command = script_info["command"]
            if not command:
                raise ValidationError(
                    "script_validation", "command", "Could not build execution command"
                )

            # Check permissions and compatibility
            try:
                permission_check = ValidationUtils.check_permissions()
                compatibility_check = ValidationUtils.validate_windows_compatibility()
            except Exception as e:
                self.logger.warning(f"Failed to check permissions/compatibility: {e}")
                permission_check = {"valid": False, "error": str(e)}
                compatibility_check = {"valid": False, "error": str(e)}

            return {
                "valid": True,
                "script_type": script_type,
                "command": command,
                "validation_details": validation_result,
                "permissions": permission_check,
                "compatibility": compatibility_check,
            }

        except (ValidationError, ScriptError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error during script validation: {e}",
                details=f"Script path: {script_path}",
            ) from e
