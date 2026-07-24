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
from datetime import datetime
from pathlib import Path
from typing import Any, cast

# Third-party imports
from rich.progress import TaskID

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
                    "Script path cannot be None or empty",
                    operation="script_registration",
                    field="script_path",
                )

            if not label:
                raise ValidationInterfaceError(
                    "Label cannot be None or empty",
                    operation="script_registration",
                    field="label",
                )

            # Comprehensive validation using ContextValidationService
            try:
                validation_result = self.validation_service.validate_command_parameters(
                    script_path, label, icon
                )
                if not validation_result.success:
                    error_message = validation_result.error or "Validation failed"
                    raise ValidationInterfaceError(
                        error_message,
                        operation="script_registration",
                        field="validation",
                    )
            except ValidationInterfaceError:
                # Re-raise validation errors as-is
                raise
            except Exception as e:
                raise ValidationInterfaceError(
                    f"Validation process failed: {e}",
                    operation="script_registration",
                    field="validation",
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
                    context_params = ContextParametersService.from_flags()
                except Exception as e:
                    raise ContextUtilityError(
                        f"Failed to create default context parameters: {e}",
                        details=f"Script path: {script_path}",
                    ) from e

            # Validate context parameters (if provided, otherwise create defaults)
            if context_params is None:
                # Create default context parameters (directory + background)
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
                    raise ValidationInterfaceError(
                        f"Context parameter validation failed: {'; '.join(errors)}",
                        operation="context_parameters",
                        field="validation",
                    )

                # Show warnings if any
                warnings = cast(list[str], validation.get("warnings", []))
                if warnings:
                    self.logger.warning(
                        f"Context parameter warnings: {'; '.join(warnings)}"
                    )
            except ValidationInterfaceError:
                raise
            except Exception as e:
                raise ValidationInterfaceError(
                    f"Context parameter validation process failed: {e}",
                    operation="context_parameters",
                    field="validation",
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
            permission_errors = []
            not_found_count = 0

            for context_type in ContextTypesConfig.ALL_TYPES:
                try:
                    registry_path = self.registry_service.get_context_path(context_type)
                    if registry_path:
                        full_path = f"{registry_path}\\{key_name}"
                        result = self.registry_service.remove_context_menu_entry(
                            full_path
                        )
                        if result.success:
                            success = True
                        else:
                            # Entry not found in this context type
                            not_found_count += 1
                            self.logger.debug(
                                f"Entry not found in {context_type}: {result.error}"
                            )
                except RegistryServiceError as e:
                    # Check if it's a permission error
                    error_str = str(e)
                    if (
                        "Accès refusé" in error_str
                        or "Access denied" in error_str
                        or "[WinError 5]" in error_str
                    ):
                        permission_errors.append(f"{context_type}: {error_str}")
                        self.logger.warning(
                            f"Failed to remove from {context_type}: {e}"
                        )
                    else:
                        # Other registry errors
                        self.logger.warning(f"Registry error for {context_type}: {e}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove from {context_type}: {e}")

            if success:
                return {
                    "success": True,
                    "key_name": key_name,
                }
            elif permission_errors:
                # If we have permission errors, raise a specific error
                error_msg = "; ".join(permission_errors)
                raise MenuInterfaceError(
                    "unregister",
                    key_name,
                    f"Permission denied: {error_msg}. Try running as administrator.",
                )
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

    def register_with_display(
        self,
        script_path: str,
        label: str,
        icon: str | None = None,
        context_params: ContextParametersService | None = None,
        verbose: bool = False,
    ) -> dict[str, object]:
        """
        Register a script with backup and UI display.

        Performs the complete registration flow:
        1. Creates backup before registration
        2. Registers the script
        3. Displays appropriate success/error messages

        Args:
            script_path: Path to the script or executable
            label: Display name in context menu
            icon: Icon path or 'auto' for auto-detection
            context_params: Context parameters for registration
            verbose: Whether to show detailed information

        Returns:
            Dict containing operation result and details
        """
        from ...ui.common import ezprinter
        from ...ui.context import ContextMenuUI

        ui = ContextMenuUI()

        # Show verbose params
        if verbose:
            ezprinter.info(f"Target: {script_path}")
            ezprinter.info(f"Label: {label}")
            ezprinter.info(f"Icon: {icon}")
            if context_params:
                ezprinter.info(f"Context: {context_params.get_description()}")

        # Create backup before registration
        backup_dir = self.get_backup_directory()
        backup_file = str(backup_dir / "context_menu_backup_before_register.json")

        with ezprinter.create_spinner_with_status(
            "Creating backup before registration..."
        ) as (progress, task):
            progress.update(cast(TaskID, task), status="Creating backup...")
            backup_result = self.backup_entries(backup_file)

        if not backup_result["success"]:
            ezprinter.error(f"Backup failed: {backup_result['error']}")
            return {"success": False, "error": backup_result["error"]}

        if verbose:
            ezprinter.info(f"Backup created: {backup_file}")

        # Perform registration
        try:
            with ezprinter.create_spinner_with_status(
                "Registering script in context menu..."
            ) as (progress, task):
                progress.update(cast(TaskID, task), status="Adding registry entries...")
                result = self.register_script(
                    script_path, label, icon, False, context_params
                )

            # Display result
            if result["success"]:
                info = cast(dict[str, Any], result["info"])
                ui.show_register_success(label, cast(str, info["registry_key"]))
            else:
                ezprinter.error(
                    f"Registration failed: {result.get('error', 'Unknown error')}"
                )
                if verbose and "info" in result:
                    info = cast(dict[str, Any], result["info"])
                    ezprinter.info(f"Script path: {info.get('script_path')}")
                    ezprinter.info(f"Script type: {info.get('script_type')}")
                    ezprinter.info(f"Registry key: {info.get('registry_key')}")

            return result
        except ValidationInterfaceError as e:
            # Convert validation errors to result dict
            error_msg = str(e)
            ezprinter.error(f"Registration failed: {error_msg}")
            return {"success": False, "error": error_msg}
        except (
            ScriptDetectorInterfaceError,
            RegistryServiceError,
            MenuInterfaceError,
        ) as e:
            # Convert other interface errors to result dict
            error_msg = str(e)
            ezprinter.error(f"Registration failed: {error_msg}")
            return {"success": False, "error": error_msg}
        except Exception as e:
            # Wrap unexpected errors
            error_msg = f"Unexpected error during registration: {e}"
            self.logger.error(error_msg)
            ezprinter.error(f"Registration failed: {error_msg}")
            return {"success": False, "error": error_msg}

    def register_context_entry(
        self,
        target_path: str | None,
        label: str | None,
        icon: str,
        root: bool,
        file: bool,
        files: bool,
        background: bool,
        file_types: tuple[str, ...],
        extensions: tuple[str, ...],
        interactive: bool,
        verbose: bool,
    ) -> dict[str, object]:
        """
        Orchestrate context menu registration with optional wizard and UI.

        Returns:
            Dict containing operation result (success/error)
        """
        from ...ui.common import ezprinter
        from ...ui.context import ContextMenuWizard

        if not self.is_windows():
            ezprinter.info("Context menu management is Windows-specific")
            ezprinter.info("Consider using symbolic links or aliases on Unix systems")
            return {"success": False, "error": "non_windows"}

        # Interactive wizard
        if interactive:
            wizard_target, wizard_label, wizard_icon, context_params = (
                ContextMenuWizard.run_setup()
            )
            if not wizard_target or not wizard_label:
                return {"success": False, "error": "cancelled"}
            target_path = wizard_target
            label = wizard_label
            icon_value: str = (
                wizard_icon if isinstance(wizard_icon, str) and wizard_icon else "auto"
            )
        else:
            # Validate required parameters in non-interactive mode
            if not target_path:
                ezprinter.error("Missing required option: --target")
                ezprinter.info("Use --interactive for guided setup")
                return {"success": False, "error": "missing_target"}
            if not label:
                ezprinter.error("Missing required option: --label")
                ezprinter.info("Use --interactive for guided setup")
                return {"success": False, "error": "missing_label"}

            context_params = ContextParametersService.from_flags(
                root=root,
                file=file,
                files=files,
                background=background,
                file_types=list(file_types) if file_types else None,
                extensions=list(extensions) if extensions else None,
            )
            icon_value = icon if isinstance(icon, str) and icon else "auto"

        target_path_value = cast(str, target_path)
        label_value = cast(str, label)

        # Perform registration with backup and UI display
        return self.register_with_display(
            script_path=target_path_value,
            label=label_value,
            icon=icon_value,
            context_params=context_params,
            verbose=verbose,
        )

    def show_entries(self, _verbose: bool = False) -> dict[str, object]:
        """
        List context menu entries with UI.
        """
        from ...ui.common import ezprinter
        from ...ui.context import ContextMenuUI

        if not self.is_windows():
            ezprinter.info("Context menu management is Windows-specific")
            return {"success": False, "error": "non_windows"}

        with ezprinter.create_spinner_with_status(
            "Retrieving context menu entries..."
        ) as (progress, task):
            progress.update(cast(TaskID, task), status="Reading registry entries...")
            result = self.list_entries()

        if result["success"]:
            ui = ContextMenuUI()
            entries = cast(dict[str, Any], result["entries"])
            ui.show_context_entries(entries)
            ui.show_list_commands()
        else:
            ezprinter.error(
                f"Failed to retrieve context menu entries: {result['error']}"
            )

        return result

    def show_status(self, _verbose: bool = False) -> dict[str, object]:
        """
        Display context menu status with tips/troubleshooting.
        """
        from ...ui.common import ezprinter
        from ...ui.context import ContextMenuUI

        if not self.is_windows():
            ezprinter.info("Context menu management is Windows-specific")
            return {"success": False, "error": "non_windows"}

        with ezprinter.create_spinner_with_status(
            "Checking context menu registration status..."
        ) as (progress, task):
            progress.update(
                cast(TaskID, task), status="Retrieving context menu entries..."
            )
            result = self.list_entries()

        if result["success"]:
            entries = cast(dict[str, list[dict[str, Any]]], result["entries"])
            total_entries = sum(
                len(entries.get(context_type, []))
                for context_type in ["directory", "background"]
            )

            ezprinter.success(f"Found {total_entries} context menu entries")

            info_content = """Context menu status information:

• Entries with descriptions are managed by external tools
• Entries without descriptions are system defaults or unmanaged
• All entries are shown for both folder and background context menus
• Backup files are stored in your WOMM installation directory"""

            ContextMenuUI().show_tip_panel(info_content, "Status Information")
        else:
            ezprinter.error("Failed to retrieve context menu status")

            troubleshoot_content = """Troubleshooting context menu issues:

• Ensure you have administrator privileges
• Check if Windows Registry access is blocked
• Try running from an elevated command prompt
• Verify WOMM installation is complete"""

            ContextMenuUI().show_tip_panel(troubleshoot_content, "Troubleshooting")

        return result

    def quick_setup_tools(self, verbose: bool = False) -> dict[str, object]:
        """
        Register common WOMM tools with UI feedback.
        """
        from ...ui.common import ezprinter
        from ...utils.womm_setup.common_utils import get_current_womm_path

        if not self.is_windows():
            ezprinter.info("Context menu management is Windows-specific")
            return {"success": False, "error": "non_windows"}

        # Find the actual path to womm.py
        try:
            womm_package_path = get_current_womm_path()
            project_root = womm_package_path.parent
            womm_py_path = project_root / "womm.py"

            if not womm_py_path.exists():
                ezprinter.error(f"Could not find womm.py at {womm_py_path}")
                return {"success": False, "error": "womm_py_not_found"}

            womm_py_absolute = str(womm_py_path.resolve())
        except Exception as e:
            ezprinter.error(f"Failed to locate womm.py: {e}")
            return {"success": False, "error": f"path_resolution_failed: {e}"}

        tools = [
            {
                "target": womm_py_absolute,
                "label": "WOMM CLI",
                "description": "Main WOMM command-line interface",
            },
        ]

        success_count = 0
        total_tools = len(tools)

        with ezprinter.create_spinner_with_status(
            "Setting up common WOMM tools..."
        ) as (progress, task):
            for i, tool in enumerate(tools, 1):
                progress.update(
                    cast(TaskID, task),
                    status=f"Registering {tool['description']} ({i}/{total_tools})...",
                )
                if verbose:
                    ezprinter.info(f"Registering: {tool['description']}")

                # Create default context parameters (directory + background)
                context_params = ContextParametersService.from_flags(
                    root=False,
                    file=False,
                    files=False,
                    background=True,
                    file_types=None,
                    extensions=None,
                )

                result = self.register_script(
                    tool["target"], tool["label"], "auto", False, context_params
                )

                if result["success"]:
                    success_count += 1
                    if verbose:
                        ezprinter.success(f"Registered: {tool['label']}")
                elif verbose:
                    ezprinter.error(
                        f"Failed to register: {tool['label']} - {result['error']}"
                    )

        if success_count == total_tools:
            ezprinter.success(f"All {total_tools} WOMM tools registered successfully!")
            ezprinter.info("Right-click in any folder to access WOMM tools")
        else:
            ezprinter.info(
                f"Registered {success_count}/{total_tools} tools successfully"
            )

        return {
            "success": success_count == total_tools,
            "success_count": success_count,
            "total": total_tools,
        }

    def backup_with_ui(
        self, backup_file: str | None = None, _verbose: bool = False
    ) -> dict[str, object]:
        """
        Create a backup with UI feedback.
        """
        from ...ui.common import ezprinter
        from ...ui.context import ContextMenuUI

        if not self.is_windows():
            ezprinter.info("Context menu management is Windows-specific")
            return {"success": False, "error": "non_windows"}

        if backup_file:
            target_backup = backup_file
            ezprinter.info(f"Backup location: {target_backup}")
        else:
            backup_dir = self.get_backup_directory()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_backup = str(backup_dir / f"context_menu_backup_{timestamp}.json")
            ezprinter.info(f"Backup location: {target_backup}")

        with ezprinter.create_spinner_with_status(
            "Creating context menu backup..."
        ) as (progress, task):
            progress.update(cast(TaskID, task), status="Reading registry entries...")
            result = self.backup_entries(target_backup)

        if result["success"]:
            entry_count = result.get("entry_count", 0)
            ContextMenuUI().show_backup_success(
                target_backup,
                int(entry_count) if isinstance(entry_count, int) else 0,
            )
        else:
            ezprinter.error(f"Backup failed: {result['error']}")

        return result

    def restore_with_ui(
        self, backup_file: str | None = None, verbose: bool = False
    ) -> dict[str, object]:
        """
        Restore context menu entries with UI.
        """
        from ...ui.common import ezprinter
        from ...ui.context import ContextMenuUI

        if not self.is_windows():
            ezprinter.info("Context menu management is Windows-specific")
            return {"success": False, "error": "non_windows"}

        ui = ContextMenuUI()
        backup_dir = self.get_backup_directory()

        if backup_file:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                ezprinter.error(f"Backup file not found: {backup_file}")
                return {"success": False, "error": "not_found"}
            selected_file = backup_path
        else:
            selected_file = ui.show_backup_selection_menu(backup_dir, verbose)
            if selected_file is None:
                return {"success": False, "error": "cancelled"}

        if not ui.confirm_restore_operation(selected_file):
            ezprinter.info("Restore cancelled")
            return {"success": False, "error": "cancelled"}

        with ezprinter.create_spinner_with_status(
            "Restoring context menu from backup..."
        ) as (progress, task):
            progress.update(cast(TaskID, task), status="Restoring from backup...")
            result = self.restore_entries(str(selected_file))

        if result["success"]:
            entry_count = result.get("entry_count", 0)
            ui.show_restore_success(
                selected_file,
                int(entry_count) if isinstance(entry_count, int) else 0,
            )
        else:
            ezprinter.error(f"Restore failed: {result['error']}")

        return result

    def cherry_pick_with_ui(self, _verbose: bool = False) -> dict[str, object]:
        """
        Cherry-pick context menu entries from backups with UI.
        """
        from ...ui.common import ezprinter
        from ...ui.context import ContextMenuUI

        if not self.is_windows():
            ezprinter.info("Context menu management is Windows-specific")
            return {"success": False, "error": "non_windows"}

        ui = ContextMenuUI()

        try:
            backup_dir = self.get_backup_directory()
            if not backup_dir.exists():
                ezprinter.error("No backup directory found")
                ezprinter.info("Create a backup first using 'womm context backup'")
                return {"success": False, "error": "no_backup_dir"}

            with ezprinter.create_spinner_with_status("Scanning backup files...") as (
                progress,
                task,
            ):
                progress.update(
                    cast(TaskID, task), status="Collecting context menu entries..."
                )
                all_entries = self.collect_entries_from_backups()

            if not all_entries:
                ezprinter.error("No context menu entries found in backups")
                return {"success": False, "error": "no_entries"}

            current_keys = self.get_current_entry_keys()
            available_entries = self.filter_available_entries(all_entries, current_keys)

            if not available_entries:
                ezprinter.info(
                    "All context menu entries from backups are already installed"
                )
                return {"success": True, "message": "already_installed"}

            selected_entries = ui.show_cherry_pick_menu(available_entries)
            if not selected_entries:
                ezprinter.info("Cherry-pick cancelled")
                return {"success": False, "error": "cancelled"}

            with ezprinter.create_spinner_with_status(
                f"Applying {len(selected_entries)} selected entries..."
            ) as (progress, task):
                results = self.apply_cherry_picked_entries(selected_entries)

            success_count = sum(1 for success in results.values() if success)
            ui.show_cherry_pick_complete(success_count)

            return {
                "success": success_count == len(selected_entries),
                "success_count": success_count,
                "total": len(selected_entries),
            }

        except Exception as e:
            ezprinter.error(f"Cherry-pick failed: {e}")
            return {"success": False, "error": str(e)}

    def unregister_with_display(
        self, key_name: str, verbose: bool = False
    ) -> dict[str, object]:
        """
        Unregister a script with UI display.

        Performs the complete unregistration flow:
        1. Shows verbose info if requested
        2. Unregisters the script
        3. Displays appropriate success/error messages

        Args:
            key_name: Registry key name to remove
            verbose: Whether to show detailed information

        Returns:
            Dict containing operation result
        """
        from ...ui.common import ezprinter
        from ...ui.context import ContextMenuUI

        ui = ContextMenuUI()

        if verbose:
            ezprinter.info(f"Removing key: {key_name}")

        # Perform unregistration
        with ezprinter.create_spinner_with_status(
            "Unregistering script from context menu..."
        ) as (progress, task):
            progress.update(cast(TaskID, task), status="Removing registry entries...")
            result = self.unregister_script(key_name)

        # Display result
        if result["success"]:
            ui.show_unregister_success(key_name)
        else:
            ezprinter.error(f"Unregistration failed: {result['error']}")

        return result

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
                    result = self.registry_service.list_context_menu_entries(
                        context_type
                    )
                    # Extract entries list from ContextRegistryResult
                    all_entries[context_type] = result.entries if result.success else []
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
                entries = cast(
                    dict[str, list[dict[str, str | None]]],
                    entries_result.get("entries", {}),
                )
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
                if not validation_result.success:
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
                permission_check = ContextValidationResult(success=False, error=str(e))
                compatibility_check = ContextValidationResult(
                    success=False, error=str(e)
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
        try:
            result = self.list_entries()
            if result["success"]:
                entries = cast(dict[str, list[dict[str, Any]]], result["entries"])
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
        results: dict[str, bool] = {}

        for entry in selected_entries:
            entry_data = cast(dict[str, Any], entry)
            key_name = entry_data.get("key_name")
            if not isinstance(key_name, str) or not key_name:
                self.logger.warning("Skipping entry with missing key_name")
                continue

            properties = cast(dict[str, Any], entry_data.get("properties", {}))
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
            results[key_name] = bool(result.get("success", False))

        return results
