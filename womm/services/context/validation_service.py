#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT VALIDATION SERVICE - Context Menu Validation Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Context Validation Service - Singleton service for context menu validation operations.

This module provides comprehensive validation functionality
for Windows context menu operations, including input validation,
data validation, and system compatibility checks.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import winreg
from pathlib import Path
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.common import ValidationServiceError
from ...exceptions.context import ContextUtilityError
from ...shared.configs.context import ContextConfig
from ...shared.result_models import ContextValidationResult
from ...utils.context import (
    sanitize_label,
    sanitize_registry_key,
    validate_backup_data,
    validate_icon_path,
    validate_label,
    validate_registry_key,
)
from ..common.security_validator_service import SecurityValidatorService
from ..system.detector_service import SystemDetectorService

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# CONTEXT VALIDATION SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class ContextValidationService:
    """Singleton service for context menu validation operations."""

    _instance: ClassVar[ContextValidationService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> ContextValidationService:
        """Create or return the singleton instance.

        Returns:
            ContextValidationService: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize context validation service (only once)."""
        if ContextValidationService._initialized:
            return

        self.logger = logging.getLogger(__name__)
        self.security_validator = SecurityValidatorService()
        self.system_detector = SystemDetectorService()
        ContextValidationService._initialized = True

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def validate_script_path(self, script_path: str) -> ContextValidationResult:
        """
        Validate a script path for context menu registration.

        Args:
            script_path: Path to the script to validate

        Returns:
            ContextValidationResult: Validation result

        Raises:
            ValidationError: If script_path is invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not script_path:
                raise ValidationServiceError(
                    "script_path", "script_path", "Script path is required"
                )

            if not isinstance(script_path, str):
                raise ValidationServiceError(
                    "script_path",
                    "script_path",
                    f"Script path must be a string, got {type(script_path).__name__}",
                )

            script_path = script_path.strip()
            if not script_path:
                raise ValidationServiceError(
                    "script_path",
                    "script_path",
                    "Script path cannot be empty after stripping",
                )

            # Security validation using SecurityValidatorService
            try:
                validation_result = self.security_validator.validate_file_path(
                    script_path
                )
                if not validation_result.is_valid:
                    raise ValidationServiceError(
                        "script_path",
                        "script_path",
                        f"Security validation failed: {validation_result.validation_reason}",
                    )
            except ValidationServiceError:
                raise
            except Exception as e:
                raise ValidationServiceError(
                    "script_path",
                    "script_path",
                    f"Security validation failed: {e}",
                ) from e

            # Convert to Path object and resolve relative paths
            try:
                path = Path(script_path).resolve()
            except Exception as e:
                raise ValidationServiceError(
                    "script_path", "script_path", f"Invalid script path format: {e}"
                ) from e

            # Check if file exists
            try:
                if not path.exists():
                    raise ValidationServiceError(
                        "script_path",
                        "script_path",
                        f"Script file not found: {script_path}",
                    )
            except (OSError, PermissionError) as e:
                raise ValidationServiceError(
                    "script_path", "script_path", f"Cannot access script file: {e}"
                ) from e

            # Check if it's a file (not directory)
            try:
                if not path.is_file():
                    raise ValidationServiceError(
                        "script_path",
                        "script_path",
                        f"Path is not a file: {script_path}",
                    )
            except (OSError, PermissionError) as e:
                raise ValidationServiceError(
                    "script_path", "script_path", f"Cannot check if path is file: {e}"
                ) from e

            # Check file extension
            extension = path.suffix.lower()
            if extension not in ContextConfig.VALID_SCRIPT_EXTENSIONS:
                raise ValidationServiceError(
                    "script_path",
                    "script_path",
                    f"Unsupported file extension: {extension}. Supported: {', '.join(ContextConfig.VALID_SCRIPT_EXTENSIONS)}",
                )

            # Check file size (prevent empty files)
            try:
                if path.stat().st_size == 0:
                    raise ValidationServiceError(
                        "script_path", "script_path", "Script file is empty"
                    )
            except (OSError, PermissionError) as e:
                raise ValidationServiceError(
                    "script_path", "script_path", f"Cannot access script file: {e}"
                ) from e

            # Check if file is readable
            try:
                with open(path, encoding="utf-8", errors="ignore") as f:
                    f.read(1)  # Try to read at least one character
            except (UnicodeDecodeError, PermissionError) as e:
                # For binary files like .exe, this is expected
                if extension not in {".exe", ".msi"}:
                    raise ValidationServiceError(
                        "script_path",
                        "script_path",
                        "Script file is not readable or contains invalid characters",
                    ) from e

            # Check path length
            if len(str(path)) > ContextConfig.MAX_PATH_LENGTH:
                raise ValidationServiceError(
                    "script_path",
                    "script_path",
                    f"Script path is too long (max {ContextConfig.MAX_PATH_LENGTH} characters)",
                )

            return ContextValidationResult(
                success=True,
                message="Script path validation successful",
                input_type="script_path",
                input_value=str(path.absolute()),
                script_path=str(path.absolute()),
                extension=extension,
                file_size=path.stat().st_size,
            )

        except ValidationServiceError:
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error validating script path: {e}",
                details=f"Script path: {script_path}",
            ) from e

    @staticmethod
    def validate_label(label: str) -> ContextValidationResult:
        """
        Validate a context menu label.

        Args:
            label: Label to validate

        Returns:
            ContextValidationResult: Validation result

        Raises:
            ValidationError: If label is invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Utility function raises exception if invalid, returns None if valid
            validate_label(label)
            return ContextValidationResult(
                success=True,
                message="Label validation successful",
                input_type="label",
                input_value=label,
                label=label,
            )
        except ValidationServiceError as e:
            return ContextValidationResult(
                success=False,
                error=str(e),
                input_type="label",
                input_value=label,
                label=label,
            )

    @staticmethod
    def validate_registry_key(key_name: str) -> ContextValidationResult:
        """
        Validate a registry key name.

        Args:
            key_name: Registry key name to validate

        Returns:
            ContextValidationResult: Validation result

        Raises:
            ValidationError: If key_name is invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Utility function raises exception if invalid, returns None if valid
            validate_registry_key(key_name)
            return ContextValidationResult(
                success=True,
                message="Registry key validation successful",
                input_type="registry_key",
                input_value=key_name,
                registry_key=key_name,
            )
        except ValidationServiceError as e:
            return ContextValidationResult(
                success=False,
                error=str(e),
                input_type="registry_key",
                input_value=key_name,
                registry_key=key_name,
            )

    def validate_icon_path(self, icon_path: str) -> ContextValidationResult:
        """
        Validate an icon path.

        Args:
            icon_path: Icon path to validate

        Returns:
            ContextValidationResult: Validation result

        Raises:
            ValidationError: If icon_path is invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Utility function raises exception if invalid, returns None if valid
            validate_icon_path(icon_path)

            # Determine icon type
            icon_type = "special" if icon_path == "auto" or not icon_path else "file"

            # Additional security validation for non-special values
            if icon_type != "special":
                try:
                    validation_result = self.security_validator.validate_file_path(
                        icon_path
                    )
                    if not validation_result.is_valid:
                        return ContextValidationResult(
                            success=False,
                            error=f"Security validation failed: {validation_result.validation_reason}",
                            input_type="icon_path",
                            input_value=icon_path,
                            icon_path=icon_path,
                            icon_type=icon_type,
                        )
                except Exception as e:
                    return ContextValidationResult(
                        success=False,
                        error=f"Security validation failed: {e}",
                        input_type="icon_path",
                        input_value=icon_path,
                        icon_path=icon_path,
                        icon_type=icon_type,
                    )

            return ContextValidationResult(
                success=True,
                message="Icon path validation successful",
                input_type="icon_path",
                input_value=icon_path,
                icon_path=icon_path,
                icon_type=icon_type,
            )

        except ValidationServiceError as e:
            return ContextValidationResult(
                success=False,
                error=str(e),
                input_type="icon_path",
                input_value=icon_path,
                icon_path=icon_path,
                icon_type="",
            )
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error validating icon path: {e}",
                details=f"Icon path: {icon_path}",
            ) from e

    @staticmethod
    def validate_backup_data(
        data: dict[str, str | bool | int | list | dict],
    ) -> dict[str, str | bool | int | list | dict]:
        """
        Validate backup data structure.

        Args:
            data: Backup data to validate

        Returns:
            Validation result dictionary

        Raises:
            ValidationError: If data is invalid
            ContextUtilityError: For unexpected errors
        """
        validate_backup_data(data)
        return data

    def check_permissions(self) -> ContextValidationResult:
        """
        Check if the current user has sufficient permissions for registry operations.

        Returns:
            ContextValidationResult: Permission check result

        Raises:
            ContextUtilityError: For unexpected errors
        """
        try:
            # Check if running on Windows using SystemDetectorService
            system_info = self.system_detector.get_system_info()
            if not system_info.success:
                return ContextValidationResult(
                    success=False,
                    error="Failed to get system information",
                    input_type="permissions",
                    has_permissions=False,
                )
            platform_name = system_info.platform or ""

            if platform_name != "Windows":
                return ContextValidationResult(
                    success=False,
                    error="Registry operations are only supported on Windows",
                    input_type="permissions",
                    has_permissions=False,
                )

            # Try to access registry for writing
            test_key = "Software\\Classes\\Directory\\shell\\WOMM_TEST_PERMISSIONS"

            try:
                # Try to create a test key
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, test_key)
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, test_key)
                winreg.CloseKey(key)

                return ContextValidationResult(
                    success=True,
                    message="User has sufficient permissions for registry operations",
                    input_type="permissions",
                    has_permissions=True,
                )

            except PermissionError:
                return ContextValidationResult(
                    success=False,
                    error="Insufficient permissions. Try running as administrator",
                    input_type="permissions",
                    has_permissions=False,
                )

            except Exception as e:
                return ContextValidationResult(
                    success=False,
                    error=f"Permission check failed: {e!s}",
                    input_type="permissions",
                    has_permissions=False,
                )

        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error checking permissions: {e}",
                details="Failed to check registry permissions",
            ) from e

    def validate_windows_compatibility(self) -> ContextValidationResult:
        """
        Check Windows compatibility for context menu operations.

        Returns:
            ContextValidationResult: Compatibility check result

        Raises:
            ContextUtilityError: For unexpected errors
        """
        try:
            # Get system info using SystemDetectorService
            system_info = self.system_detector.get_system_info()
            if not system_info.success:
                return ContextValidationResult(
                    success=False,
                    error="Failed to get system information",
                    input_type="compatibility",
                    compatible=False,
                )
            platform_name = system_info.platform or ""

            # Check OS
            if platform_name != "Windows":
                return ContextValidationResult(
                    success=False,
                    error="Context menu operations are only supported on Windows",
                    input_type="compatibility",
                    compatible=False,
                )

            # Check Windows version
            platform_version = ""
            try:
                platform_version = system_info.platform_version or ""
                if platform_version:
                    # Windows 7 and later are supported (version 6.0+)
                    major_version = int(platform_version.split(".")[0])
                    if major_version < 6:
                        return ContextValidationResult(
                            success=False,
                            error="Windows 7 or later is required",
                            input_type="compatibility",
                            compatible=False,
                        )
                else:
                    return ContextValidationResult(
                        success=False,
                        error="Cannot determine Windows version",
                        input_type="compatibility",
                        compatible=False,
                    )

            except (ValueError, AttributeError) as e:
                return ContextValidationResult(
                    success=False,
                    error=f"Cannot determine Windows version: {e!s}",
                    input_type="compatibility",
                    compatible=False,
                )

            # Check if registry is accessible
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, "Software\\Classes", 0, winreg.KEY_READ
                )
                winreg.CloseKey(key)
            except Exception as e:
                return ContextValidationResult(
                    success=False,
                    error=f"Cannot access Windows Registry: {e!s}",
                    input_type="compatibility",
                    compatible=False,
                )

            return ContextValidationResult(
                success=True,
                message="System is compatible with context menu operations",
                input_type="compatibility",
                compatible=True,
                windows_version=platform_version,
            )

        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error checking Windows compatibility: {e}",
                details="Failed to validate system compatibility",
            ) from e

    def validate_command_parameters(
        self, script_path: str, label: str, icon: str | None = None
    ) -> ContextValidationResult:
        """
        Validate all parameters for context menu registration.

        Args:
            script_path: Path to the script
            label: Display label
            icon: Icon path (optional)

        Returns:
            ContextValidationResult: Comprehensive validation result

        Raises:
            ValidationError: If parameters are invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not script_path:
                raise ValidationServiceError(
                    "command_parameters", "script_path", "Script path is required"
                )

            if not label:
                raise ValidationServiceError(
                    "command_parameters", "label", "Label is required"
                )

            if not isinstance(script_path, str):
                raise ValidationServiceError(
                    "command_parameters",
                    "script_path",
                    f"Script path must be a string, got {type(script_path).__name__}",
                )

            if not isinstance(label, str):
                raise ValidationServiceError(
                    "command_parameters",
                    "label",
                    f"Label must be a string, got {type(label).__name__}",
                )

            if icon is not None and not isinstance(icon, str):
                raise ValidationServiceError(
                    "command_parameters",
                    "icon",
                    f"Icon must be a string, got {type(icon).__name__}",
                )

            errors = []
            warnings = []
            result = ContextValidationResult(
                success=True,
                message="All parameters validated successfully",
                input_type="command_parameters",
                script_path=script_path,
                label=label,
            )

            # Validate script path
            try:
                script_validation = self.validate_script_path(script_path)
                result.script_path = script_validation.script_path
                result.extension = script_validation.extension
                result.file_size = script_validation.file_size
                if not script_validation.success:
                    result.success = False
                    errors.append(script_validation.error)
            except ValidationServiceError as e:
                result.success = False
                errors.append(str(e))

            # Validate label
            try:
                label_validation = self.validate_label(label)
                result.label = label_validation.label
                if not label_validation.success:
                    result.success = False
                    errors.append(label_validation.error)
            except ValidationServiceError as e:
                result.success = False
                errors.append(str(e))

            # Validate icon if provided
            if icon:
                try:
                    icon_validation = self.validate_icon_path(icon)
                    result.icon_path = icon_validation.icon_path
                    result.icon_type = icon_validation.icon_type
                    if not icon_validation.success:
                        warnings.append(f"Icon validation: {icon_validation.error}")
                except ValidationServiceError as e:
                    warnings.append(f"Icon validation: {e!s}")

            # Check permissions
            try:
                permission_check = self.check_permissions()
                result.has_permissions = permission_check.has_permissions
                if not permission_check.has_permissions:
                    result.success = False
                    errors.append(permission_check.error)
            except Exception as e:
                warnings.append(f"Permission check failed: {e!s}")

            # Check compatibility
            try:
                compatibility_check = self.validate_windows_compatibility()
                result.compatible = compatibility_check.compatible
                result.windows_version = compatibility_check.windows_version
                if not compatibility_check.compatible:
                    result.success = False
                    errors.append(compatibility_check.error)
            except Exception as e:
                warnings.append(f"Compatibility check failed: {e!s}")

            # Update message and error based on results
            if errors:
                result.error = "; ".join(errors)
            if warnings:
                result.message = (
                    f"Validation completed with warnings: {'; '.join(warnings)}"
                )

            return result

        except ValidationServiceError:
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error validating command parameters: {e}",
                details=f"Script path: {script_path}, Label: {label}, Icon: {icon}",
            ) from e

    def sanitize_registry_key(self, key_name: str) -> str:
        """
        Sanitize a registry key name to make it valid.

        Args:
            key_name: Original key name

        Returns:
            Sanitized key name

        Raises:
            ValidationError: If key_name is invalid
            ContextUtilityError: For unexpected errors
        """
        return sanitize_registry_key(key_name)

    def sanitize_label(self, label: str) -> str:
        """
        Sanitize a context menu label to make it valid.

        Args:
            label: Original label

        Returns:
            Sanitized label

        Raises:
            ValidationError: If label is invalid
            ContextUtilityError: For unexpected errors
        """
        return sanitize_label(label)
