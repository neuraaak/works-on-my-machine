#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT SCRIPT REGISTRAR - Registration workflow for a single script
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Registration workflow for one script in the Windows context menu.

``ContextScriptRegistrar`` owns the sequence validate -> detect -> resolve icon
-> build command -> write registry entries. It receives its collaborators so it
stays testable, and like the rest of the interface layer it never raises: every
outcome is a ``ScriptRegistrationResult``.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from typing import cast

# Local imports
from ...services.context.parameters import ContextParameters
from ...services.context.registry_paths import context_type_from_registry_path
from ...shared.results import ScriptRegistrationResult
from .script_detector_interface import ContextScriptDetectorInterface

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class ContextScriptRegistrar:
    """Registers a single script in the Windows context menu."""

    def __init__(
        self,
        validation_service,
        icon_manager,
        registry_service,
        logger: logging.Logger | None = None,
    ):
        """
        Initialize the registrar with the collaborators it drives.

        Args:
            validation_service: ContextValidationService-like collaborator
            icon_manager: ContextIconResolver-like collaborator
            registry_service: ContextRegistryService-like collaborator
            logger: Logger for non-fatal findings
        """
        self.validation_service = validation_service
        self.icon_manager = icon_manager
        self.registry_service = registry_service
        self.logger = logger or logging.getLogger(__name__)

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def register(
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
        try:
            if not script_path:
                raise ValueError("Script path cannot be None or empty")
            if not label:
                raise ValueError("Label cannot be None or empty")

            self._validate_command_parameters(script_path, label, icon)

            script_info = ContextScriptDetectorInterface.get_script_info(script_path)
            if not script_info.success:
                raise RuntimeError(f"Failed to detect script type: {script_info.error}")

            icon_path = self._resolve_icon(script_path, icon, script_info.default_icon)

            try:
                registry_key_name = self.registry_service.generate_registry_key_name(
                    script_path
                )
            except Exception as e:
                raise RuntimeError(f"Failed to generate registry key name: {e}") from e

            command = script_info.command
            context_params = context_params or self._default_context_params()
            self._validate_context_params(context_params)

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
                    script_type=script_info.script_type,
                    label=label,
                    icon_path=icon_path,
                    registry_key=registry_key_name,
                    command=final_command,
                    context_info=context_params.get_description(),
                )

            success_count, total_paths = self._write_entries(
                context_params, registry_key_name, command, label, icon_path
            )
            if success_count != total_paths:
                raise RuntimeError(
                    f"Failed to add registry entries ({success_count}/{total_paths} succeeded)"
                )

            return ScriptRegistrationResult(
                success=True,
                script_path=script_path,
                script_type=script_info.script_type,
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

    def _validate_command_parameters(
        self, script_path: str, label: str, icon: str | None
    ) -> None:
        """Run the comprehensive parameter validation, raising on rejection."""
        try:
            validation_result = self.validation_service.validate_command_parameters(
                script_path, label, icon
            )
        except Exception as e:
            raise ValueError(f"Validation process failed: {e}") from e

        if not validation_result.success:
            raise ValueError(validation_result.error or "Validation failed")

    def _resolve_icon(
        self, script_path: str, icon: str | None, default_icon: str | None
    ) -> str | None:
        """Resolve the icon, degrading to the type default then to ``None``."""
        try:
            icon_path = self.icon_manager.resolve_icon(icon or "auto", script_path)
        except (ValueError, OSError) as e:
            self.logger.warning(f"Failed to resolve icon for {script_path}: {e}")
            return None

        if icon_path is None and icon and icon.lower() != "auto":
            return default_icon
        return icon_path

    @staticmethod
    def _default_context_params() -> ContextParameters:
        """Default context parameters used when the caller supplies none."""
        return ContextParameters.from_flags(
            root=False,
            file=False,
            files=False,
            background=True,
            file_types=None,
            extensions=None,
        )

    def _validate_context_params(self, context_params: ContextParameters) -> None:
        """Validate context parameters, raising on errors and logging warnings."""
        try:
            validation = context_params.validate_parameters()
        except Exception as e:
            raise ValueError(f"Context parameter validation process failed: {e}") from e

        if not cast(bool, validation.get("valid", False)):
            errors = cast("list[str]", validation.get("errors", []))
            raise ValueError(
                f"Context parameter validation failed: {'; '.join(errors)}"
            )

        warnings = cast("list[str]", validation.get("warnings", []))
        if warnings:
            self.logger.warning(f"Context parameter warnings: {'; '.join(warnings)}")

    def _write_entries(
        self,
        context_params: ContextParameters,
        registry_key_name: str,
        command: str,
        label: str,
        icon_path: str | None,
    ) -> tuple[int, int]:
        """Write one registry entry per context path; return (written, total)."""
        try:
            registry_paths = context_params.get_registry_paths()
        except Exception as e:
            raise RuntimeError(f"Failed to get registry paths: {e}") from e

        success_count = 0
        for registry_path in registry_paths:
            full_path = f"{registry_path}\\{registry_key_name}"
            entry_command = context_params.build_command(
                command, context_type_from_registry_path(registry_path)
            )

            try:
                add_result = self.registry_service.add_context_menu_entry(
                    full_path,
                    entry_command,
                    label,
                    icon_path,
                )
                entry_success = add_result.success
            except Exception as e:
                self.logger.warning(f"Failed to add registry entry {full_path}: {e}")
                entry_success = False

            if entry_success:
                success_count += 1

        return success_count, len(registry_paths)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["ContextScriptRegistrar"]
