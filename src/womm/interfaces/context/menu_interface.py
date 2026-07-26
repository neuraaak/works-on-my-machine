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
from typing import cast

# Local imports
from ...exceptions.context import ContextServiceError
from ...services import (
    ContextParametersService,
    ContextRegistryService,
    ContextType,
    ContextValidationService,
)
from ...shared.configs.context import ContextTypesConfig
from ...shared.results import (
    ContextBackupResult,
    ContextEntriesResult,
    ContextRestoreResult,
    ContextSetupResult,
    ContextStatusResult,
    ContextValidationResult,
    ScriptInfoResult,
    ScriptRegistrationResult,
    ScriptUnregistrationResult,
    ScriptValidationResult,
)
from ...utils.context import ContextIconResolver
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
        self._icon_manager: ContextIconResolver | None = None
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
    def icon_manager(self) -> ContextIconResolver:
        """Lazy load ContextIconResolver when needed."""
        if self._icon_manager is None:
            self._icon_manager = ContextIconResolver()
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
    ) -> ScriptRegistrationResult:
        """
        Register a script in the Windows context menu.

        Args:
            script_path: Path to the script or executable
            label: Display name in context menu
            icon: Icon path or 'auto' for auto-detection
            dry_run: If True, show what would be done without making changes
            context_params: Context parameters for registration

        Returns:
            ScriptRegistrationResult: Result of the registration attempt
        """
        try:
            if not script_path:
                raise ValueError("Script path cannot be None or empty")
            if not label:
                raise ValueError("Label cannot be None or empty")

            # Comprehensive validation using ContextValidationService
            try:
                validation_result = self.validation_service.validate_command_parameters(
                    script_path, label, icon
                )
                if not validation_result.success:
                    raise ValueError(validation_result.error or "Validation failed")
            except ValueError:
                raise
            except Exception as e:
                raise ValueError(f"Validation process failed: {e}") from e

            # Detect script type and get info
            script_info = ContextScriptDetectorInterface.get_script_info(script_path)
            if not script_info.success:
                raise RuntimeError(f"Failed to detect script type: {script_info.error}")
            script_type = script_info.script_type

            # Resolve icon
            try:
                icon_path = self.icon_manager.resolve_icon(icon or "auto", script_path)
                if icon_path is None and icon and icon.lower() != "auto":
                    # Fallback to default icon for script type
                    icon_path = script_info.default_icon
            except (ValueError, OSError) as e:
                self.logger.warning(f"Failed to resolve icon for {script_path}: {e}")
                icon_path = None

            # Generate registry key name
            try:
                registry_key_name = self.registry_service.generate_registry_key_name(
                    script_path
                )
            except Exception as e:
                raise RuntimeError(f"Failed to generate registry key name: {e}") from e

            # Build command
            command = script_info.command

            # Default context parameters (directory + background) when none given
            if context_params is None:
                context_params = ContextParametersService.from_flags(
                    root=False,
                    file=False,
                    files=False,
                    background=True,
                    file_types=None,
                    extensions=None,
                )

            try:
                validation = context_params.validate_parameters()
                is_valid = cast(bool, validation.get("valid", False))
                if not is_valid:
                    errors = cast(list[str], validation.get("errors", []))
                    raise ValueError(
                        f"Context parameter validation failed: {'; '.join(errors)}"
                    )

                warnings = cast(list[str], validation.get("warnings", []))
                if warnings:
                    self.logger.warning(
                        f"Context parameter warnings: {'; '.join(warnings)}"
                    )
            except ValueError:
                raise
            except Exception as e:
                raise ValueError(
                    f"Context parameter validation process failed: {e}"
                ) from e

            # Build final command for display (use first context type for dry-run)
            context_types = list(context_params.context_types)
            final_command = (
                context_params.build_command(command, context_types[0])
                if context_types
                else command
            )

            if dry_run:
                return ScriptRegistrationResult(
                    success=True,
                    dry_run=True,
                    script_path=script_path,
                    script_type=script_type,
                    label=label,
                    icon_path=icon_path,
                    registry_key=registry_key_name,
                    command=final_command,
                    context_info=context_params.get_description(),
                )

            # Get registry paths and add entries
            try:
                registry_paths = context_params.get_registry_paths()
            except Exception as e:
                raise RuntimeError(f"Failed to get registry paths: {e}") from e

            success_count = 0
            total_paths = len(registry_paths)

            for registry_path in registry_paths:
                full_path = f"{registry_path}\\{registry_key_name}"

                # Build command with appropriate parameters for this context type
                context_type = self._get_context_type_from_path(registry_path)
                entry_command = context_params.build_command(command, context_type)

                try:
                    add_result = self.registry_service.add_context_menu_entry(
                        full_path,
                        entry_command,
                        label,
                        icon_path,
                    )
                    entry_success = add_result.success
                except Exception as e:
                    self.logger.warning(
                        f"Failed to add registry entry {full_path}: {e}"
                    )
                    entry_success = False

                if entry_success:
                    success_count += 1

            if success_count != total_paths:
                raise RuntimeError(
                    f"Failed to add registry entries ({success_count}/{total_paths} succeeded)"
                )

            return ScriptRegistrationResult(
                success=True,
                script_path=script_path,
                script_type=script_type,
                label=label,
                icon_path=icon_path,
                registry_key=registry_key_name,
                command=final_command,
                context_info=context_params.get_description(),
                success_count=success_count,
                total_paths=total_paths,
            )

        except (ValueError, RuntimeError) as e:
            return ScriptRegistrationResult(success=False, error=str(e))
        except Exception as e:
            return ScriptRegistrationResult(
                success=False,
                error=f"Unexpected error during script registration: {e}",
            )

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
        """
        if (
            ContextTypesConfig.REGISTRY_PATTERN_DIRECTORY_SHELL in registry_path
            and "background" not in registry_path
        ):
            return ContextType.DIRECTORY
        elif ContextTypesConfig.REGISTRY_PATTERN_DIRECTORY_BACKGROUND in registry_path:
            return ContextType.BACKGROUND
        elif ContextTypesConfig.REGISTRY_PATTERN_DRIVE_SHELL in registry_path:
            return ContextType.ROOT
        elif ContextTypesConfig.REGISTRY_PATTERN_FILE_SHELL in registry_path:
            return ContextType.FILE
        else:
            return ContextType.DIRECTORY  # Default fallback

    def unregister_script(
        self, key_name: str, dry_run: bool = False
    ) -> ScriptUnregistrationResult:
        """
        Unregister a script from the Windows context menu.

        Args:
            key_name: Registry key name to remove
            dry_run: If True, show what would be done without making changes

        Returns:
            ScriptUnregistrationResult: Result of the unregistration attempt
        """
        if not key_name:
            return ScriptUnregistrationResult(
                success=False, error="Registry key name cannot be None or empty"
            )

        if dry_run:
            return ScriptUnregistrationResult(
                success=True,
                dry_run=True,
                key_name=key_name,
                message="Dry run - no changes made",
            )

        # Try to remove from both context types
        success = False
        permission_errors: list[str] = []
        not_found_count = 0
        total_types = len(ContextTypesConfig.ALL_TYPES)

        for context_type in ContextTypesConfig.ALL_TYPES:
            try:
                registry_path = self.registry_service.get_context_path(context_type)
                if registry_path:
                    full_path = f"{registry_path}\\{key_name}"
                    result = self.registry_service.remove_context_menu_entry(full_path)
                    if result.success:
                        success = True
                    else:
                        # Entry not found in this context type
                        not_found_count += 1
                        self.logger.debug(
                            f"Entry not found in {context_type}: {result.error}"
                        )
            except ContextServiceError as e:
                error_str = str(e)
                if (
                    "Accès refusé" in error_str
                    or "Access denied" in error_str
                    or "[WinError 5]" in error_str
                ):
                    permission_errors.append(f"{context_type}: {error_str}")
                    self.logger.warning(f"Failed to remove from {context_type}: {e}")
                else:
                    self.logger.warning(f"Registry error for {context_type}: {e}")
            except Exception as e:
                self.logger.warning(f"Failed to remove from {context_type}: {e}")

        if success:
            return ScriptUnregistrationResult(
                success=True,
                key_name=key_name,
                success_count=1,
                total_types=total_types,
                permission_errors=permission_errors,
                not_found_count=not_found_count,
            )
        if permission_errors:
            error_msg = "; ".join(permission_errors)
            return ScriptUnregistrationResult(
                success=False,
                error=f"Permission denied: {error_msg}. Try running as administrator.",
                key_name=key_name,
                total_types=total_types,
                permission_errors=permission_errors,
                not_found_count=not_found_count,
            )
        return ScriptUnregistrationResult(
            success=False,
            error="Entry not found in any context type",
            key_name=key_name,
            total_types=total_types,
            not_found_count=not_found_count,
        )

    def list_entries(self) -> ContextEntriesResult:
        """
        List all registered context menu entries.

        Returns:
            ContextEntriesResult: All entries organized by context type
        """
        all_entries: dict[str, list[dict[str, str | None]]] = {}

        for context_type in ContextTypesConfig.ALL_TYPES:
            try:
                result = self.registry_service.list_context_menu_entries(context_type)
                all_entries[context_type] = (
                    result.entries or [] if result.success else []
                )
            except Exception as e:
                self.logger.warning(f"Failed to list entries for {context_type}: {e}")
                all_entries[context_type] = []

        return ContextEntriesResult(success=True, entries=all_entries)

    def get_status(self) -> ContextStatusResult:
        """
        Compute context menu registration status.

        Returns:
            ContextStatusResult: Entry counts by context type
        """
        entries_result = self.list_entries()
        if not entries_result.success:
            return ContextStatusResult(success=False, error=entries_result.error)

        entries = entries_result.entries or {}
        entries_by_type = {
            context_type: len(entries.get(context_type, []))
            for context_type in ("directory", "background")
        }
        total_entries = sum(entries_by_type.values())

        return ContextStatusResult(
            success=True,
            total_entries=total_entries,
            entries_by_type=entries_by_type,
        )

    def quick_setup_tools(self, verbose: bool = False) -> ContextSetupResult:
        """
        Register common WOMM tools in the context menu.

        Args:
            verbose: Whether to log per-tool progress

        Returns:
            ContextSetupResult: Aggregate registration outcome
        """
        from ...utils.womm_setup.common_utils import get_current_womm_path

        try:
            womm_package_path = get_current_womm_path()
            project_root = womm_package_path.parent
            womm_py_path = project_root / "womm.py"

            if not womm_py_path.exists():
                return ContextSetupResult(
                    success=False, error=f"Could not find womm.py at {womm_py_path}"
                )

            womm_py_absolute = str(womm_py_path.resolve())
        except Exception as e:
            return ContextSetupResult(
                success=False, error=f"Failed to locate womm.py: {e}"
            )

        tools = [
            {
                "target": womm_py_absolute,
                "label": "WOMM CLI",
                "description": "Main WOMM command-line interface",
            },
        ]

        context_params = ContextParametersService.from_flags(
            root=False,
            file=False,
            files=False,
            background=True,
            file_types=None,
            extensions=None,
        )

        tools_registered: list[str] = []
        for tool in tools:
            if verbose:
                self.logger.info(f"Registering: {tool['description']}")

            result = self.register_script(
                tool["target"], tool["label"], "auto", False, context_params
            )

            if result.success:
                tools_registered.append(tool["label"])
            elif verbose:
                self.logger.warning(
                    f"Failed to register: {tool['label']} - {result.error}"
                )

        return ContextSetupResult(
            success=len(tools_registered) == len(tools),
            success_count=len(tools_registered),
            total_tools=len(tools),
            tools_registered=tools_registered,
        )

    def backup_entries(self, backup_file: str) -> ContextBackupResult:
        """
        Backup current context menu entries.

        Args:
            backup_file: Path to save the backup file

        Returns:
            ContextBackupResult: Result of the backup attempt
        """
        if not backup_file:
            return ContextBackupResult(
                success=False, error="Backup file path cannot be None or empty"
            )

        entries_result = self.list_entries()
        if not entries_result.success:
            return ContextBackupResult(
                success=False,
                error=f"Failed to get current entries: {entries_result.error}",
            )

        written = self.backup_manager.create_backup_file(
            entries_result.entries or {},
            custom_filename=Path(backup_file).stem,
            add_timestamp=False,
        )
        if not written.success:
            return ContextBackupResult(
                success=False, error=f"Failed to create backup: {written.error}"
            )

        return ContextBackupResult(
            success=True,
            backup_file=written.filepath,
            entry_count=(written.metadata or {}).get("total_entries", 0),
        )

    def restore_entries(self, backup_file: str) -> ContextRestoreResult:
        """
        Restore context menu entries from backup.

        Args:
            backup_file: Path to the backup file

        Returns:
            ContextRestoreResult: Result of the restore attempt
        """
        if not backup_file:
            return ContextRestoreResult(
                success=False, error="Backup file path cannot be None or empty"
            )

        loaded = self.backup_manager.load_backup_file(backup_file)
        if not loaded.success:
            return ContextRestoreResult(
                success=False, error=f"Backup loading failed: {loaded.error}"
            )
        data = loaded.data or {}

        try:
            result = self.registry_service.restore_registry_entries(data)
        except ContextServiceError as e:
            return ContextRestoreResult(
                success=False, error=f"Failed to restore registry entries: {e}"
            )

        if not result.success:
            return ContextRestoreResult(
                success=False, error="Registry restoration failed"
            )

        return ContextRestoreResult(
            success=True,
            backup_file=backup_file,
            entry_count=data.get("metadata", {}).get("total_entries", 0),
        )

    def get_script_info(self, script_path: str) -> ScriptInfoResult:
        """
        Get comprehensive information about a script.

        Enriches the detector's result with the resolved icon and the registry
        key name. Neither enrichment can fail the call: both degrade to ``None``
        and are logged.

        Args:
            script_path: Path to the script

        Returns:
            ScriptInfoResult: script details; failure carries the error.
        """
        if not script_path:
            return ScriptInfoResult(
                success=False, error="Script path cannot be None or empty"
            )

        script_info = ContextScriptDetectorInterface.get_script_info(script_path)
        if not script_info.success:
            return script_info

        try:
            script_info.resolved_icon = self.icon_manager.resolve_icon(
                "auto", script_path
            )
        except (ValueError, OSError) as e:
            self.logger.warning(f"Failed to resolve icon for {script_path}: {e}")
            script_info.resolved_icon = None

        try:
            script_info.registry_key = self.registry_service.generate_registry_key_name(
                script_path
            )
        except (ContextServiceError, ValueError) as e:
            self.logger.warning(
                f"Failed to generate registry key for {script_path}: {e}"
            )
            script_info.registry_key = None

        return script_info

    def validate_script(self, script_path: str) -> ScriptValidationResult:
        """
        Validate if a script can be registered in context menu.

        Args:
            script_path: Path to the script

        Returns:
            ScriptValidationResult: validity plus the permission and
            compatibility findings; failure carries the error.
        """
        if not script_path:
            return ScriptValidationResult(
                success=False, error="Script path cannot be None or empty"
            )

        # Use ContextValidationService for comprehensive validation
        try:
            validation_result = self.validation_service.validate_script_path(
                script_path
            )
        except (ContextServiceError, ValueError, OSError) as e:
            return ScriptValidationResult(
                success=False,
                script_path=script_path,
                error=f"Validation process failed: {e}",
            )

        if not validation_result.success:
            return ScriptValidationResult(
                success=False,
                script_path=script_path,
                error=validation_result.error or "Validation failed",
            )

        script_info = ContextScriptDetectorInterface.get_script_info(script_path)
        if not script_info.success:
            return ScriptValidationResult(
                success=False,
                script_path=script_path,
                error=f"Failed to get script info during validation: {script_info.error}",
            )

        if script_info.script_type == ScriptType.UNKNOWN:
            return ScriptValidationResult(
                success=False,
                script_path=script_path,
                script_type=script_info.script_type,
                error=f"Unsupported script type: {Path(script_path).suffix}",
            )

        if not script_info.command:
            return ScriptValidationResult(
                success=False,
                script_path=script_path,
                script_type=script_info.script_type,
                error="Could not build execution command",
            )

        # Permission and compatibility findings are reported, not fatal
        try:
            permission_check = self.validation_service.check_permissions()
            compatibility_check = (
                self.validation_service.validate_windows_compatibility()
            )
        except (ContextServiceError, ValueError, OSError) as e:
            self.logger.warning(f"Failed to check permissions/compatibility: {e}")
            permission_check = ContextValidationResult(success=False, error=str(e))
            compatibility_check = ContextValidationResult(success=False, error=str(e))

        return ScriptValidationResult(
            success=True,
            message=f"{script_info.script_type} script can be registered",
            script_path=script_path,
            script_type=script_info.script_type,
            command=script_info.command,
            permissions_ok=permission_check.success,
            permissions_error=permission_check.error or "",
            compatibility_ok=compatibility_check.success,
            compatibility_error=compatibility_check.error or "",
        )

    # ///////////////////////////////////////////////////////////////
    # PLATFORM AND UTILITY METHODS
    # ///////////////////////////////////////////////////////////////

    def is_windows(self) -> bool:
        """Check if running on Windows platform."""
        import platform

        return platform.system().lower() == "windows"

    def get_backup_directory(self) -> Path:
        """Get the backup directory path, creating it if needed."""
        return self.backup_manager.get_backup_directory()

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

                # Entries are organized by context type (directory, background, etc.)
                entries_dict = data.get("entries", {})
                if not isinstance(entries_dict, dict):
                    # Fallback for old format where entries might be a list
                    entries_dict = {
                        "directory": (
                            entries_dict if isinstance(entries_dict, list) else []
                        )
                    }

                # Iterate through all context types
                for context_type in [
                    "directory",
                    "background",
                    "file",
                    "files",
                    "root",
                ]:
                    entries = entries_dict.get(context_type, [])
                    if not isinstance(entries, list):
                        continue

                    for entry in entries:
                        if not isinstance(entry, dict):
                            continue
                        key_name = entry.get("key_name")
                        if key_name and key_name not in all_entries:
                            entry["_source_backup"] = backup_file.name
                            entry["_context_type"] = context_type
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
        entries_result = self.list_entries()
        if not entries_result.success:
            return set()

        entries = entries_result.entries or {}
        current_keys: set[str] = set()
        for context_type in ["directory", "background"]:
            for entry in entries.get(context_type, []):
                key_name = entry.get("key_name")
                if key_name:
                    current_keys.add(key_name)
        return current_keys

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
        results: dict[str, bool] = {}

        for entry in selected_entries:
            key_name = entry.get("key_name")
            if not isinstance(key_name, str) or not key_name:
                self.logger.warning("Skipping entry with missing key_name")
                continue

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
            muiverb_value = (
                muiverb if isinstance(muiverb, str) and muiverb else key_name
            )
            icon_value = icon if isinstance(icon, str) and icon else "auto"
            result = self.register_script(script_path, muiverb_value, icon_value)
            results[key_name] = result.success

        return results
