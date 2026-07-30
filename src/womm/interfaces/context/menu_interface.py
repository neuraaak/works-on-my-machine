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
from ...exceptions.context import ContextServiceError
from ...services import (
    ContextParameters,
    ContextRegistryService,
    ContextValidationService,
)
from ...services.context.backup_entries import ContextBackupEntriesReader
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
from ...shared.runtime import get_womm_executable
from ...utils.context import ContextIconResolver
from .registry_interface import ContextRegistryInterface
from .script_detector_interface import ContextScriptDetectorInterface, ScriptType
from .script_registrar import ContextScriptRegistrar

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
        self._entries_reader: ContextBackupEntriesReader | None = None

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

    @property
    def _backup_entries_reader(self) -> ContextBackupEntriesReader:
        """Lazy load the backup entries reader when needed."""
        if self._entries_reader is None:
            self._entries_reader = ContextBackupEntriesReader(self.logger)
        return self._entries_reader

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def register_script(
        self,
        script_path: str,
        label: str,
        icon: str | None = None,
        dry_run: bool = False,
        context_params: ContextParameters | None = None,
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
        return self._registrar().register(
            script_path, label, icon, dry_run, context_params
        )

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _registrar(self) -> ContextScriptRegistrar:
        """Build a registrar bound to this interface's current collaborators."""
        return ContextScriptRegistrar(
            validation_service=self.validation_service,
            icon_manager=self.icon_manager,
            registry_service=self.registry_service,
            logger=self.logger,
        )

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
        try:
            womm_executable = get_womm_executable()
            if not womm_executable.is_file():
                return ContextSetupResult(
                    success=False,
                    error=f"Could not find WOMM executable at {womm_executable}",
                )
            executable_path = str(womm_executable.resolve())
        except OSError as e:
            return ContextSetupResult(
                success=False, error=f"Failed to locate WOMM executable: {e}"
            )

        tools = [
            {
                "target": executable_path,
                "label": "WOMM CLI",
                "description": "Main WOMM command-line interface",
            },
        ]

        context_params = ContextParameters.from_flags(
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
        return self._backup_entries_reader.collect_entries(self.get_backup_directory())

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
        return self._backup_entries_reader.filter_available(all_entries, current_keys)

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

            script_path = self._backup_entries_reader.extract_script_path(command)

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
