#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# VALIDATION - Context Menu Validation Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Validation utilities for context menu operations.

This module provides comprehensive validation functionality
for Windows context menu operations, including input validation,
data validation, and system compatibility checks.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import os
import re
import winreg
from pathlib import Path

# Local imports
from ...exceptions.context.context_exceptions import (
    ContextUtilityError,
    ValidationError,
)


class ValidationUtils:
    """Validation utilities for context menu operations."""

    # Valid registry key name pattern
    REGISTRY_KEY_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.]+$")

    # Valid file extensions for scripts
    VALID_SCRIPT_EXTENSIONS = {".py", ".ps1", ".bat", ".cmd", ".exe", ".msi"}

    # Maximum lengths
    MAX_LABEL_LENGTH = 256
    MAX_REGISTRY_KEY_LENGTH = 255
    MAX_PATH_LENGTH = 260

    @staticmethod
    def validate_script_path(script_path: str) -> dict[str, str | bool | int]:
        """
        Validate a script path for context menu registration.

        Args:
            script_path: Path to the script to validate

        Returns:
            Validation result dictionary

        Raises:
            ValidationError: If script_path is invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not script_path:
                raise ValidationError(
                    "script_path", "script_path", "Script path is required"
                )

            if not isinstance(script_path, str):
                raise ValidationError(
                    "script_path",
                    "script_path",
                    f"Script path must be a string, got {type(script_path).__name__}",
                )

            script_path = script_path.strip()
            if not script_path:
                raise ValidationError(
                    "script_path",
                    "script_path",
                    "Script path cannot be empty after stripping",
                )

            # Convert to Path object and resolve relative paths
            try:
                path = Path(script_path).resolve()
            except Exception as e:
                raise ValidationError(
                    "script_path", "script_path", f"Invalid script path format: {e}"
                ) from e

            # Check if file exists
            try:
                if not path.exists():
                    raise ValidationError(
                        "script_path",
                        "script_path",
                        f"Script file not found: {script_path}",
                    )
            except (OSError, PermissionError) as e:
                raise ValidationError(
                    "script_path", "script_path", f"Cannot access script file: {e}"
                ) from e

            # Check if it's a file (not directory)
            try:
                if not path.is_file():
                    raise ValidationError(
                        "script_path",
                        "script_path",
                        f"Path is not a file: {script_path}",
                    )
            except (OSError, PermissionError) as e:
                raise ValidationError(
                    "script_path", "script_path", f"Cannot check if path is file: {e}"
                ) from e

            # Check file extension
            extension = path.suffix.lower()
            if extension not in ValidationUtils.VALID_SCRIPT_EXTENSIONS:
                raise ValidationError(
                    "script_path",
                    "script_path",
                    f"Unsupported file extension: {extension}. Supported: {', '.join(ValidationUtils.VALID_SCRIPT_EXTENSIONS)}",
                )

            # Check file size (prevent empty files)
            try:
                if path.stat().st_size == 0:
                    raise ValidationError(
                        "script_path", "script_path", "Script file is empty"
                    )
            except (OSError, PermissionError) as e:
                raise ValidationError(
                    "script_path", "script_path", f"Cannot access script file: {e}"
                ) from e

            # Check if file is readable
            try:
                with open(path, encoding="utf-8", errors="ignore") as f:
                    f.read(1)  # Try to read at least one character
            except (UnicodeDecodeError, PermissionError) as e:
                # For binary files like .exe, this is expected
                if extension not in {".exe", ".msi"}:
                    raise ValidationError(
                        "script_path",
                        "script_path",
                        "Script file is not readable or contains invalid characters",
                    ) from e

            # Check path length
            if len(str(path)) > ValidationUtils.MAX_PATH_LENGTH:
                raise ValidationError(
                    "script_path",
                    "script_path",
                    f"Script path is too long (max {ValidationUtils.MAX_PATH_LENGTH} characters)",
                )

            return {
                "valid": True,
                "script_path": str(path.absolute()),
                "extension": extension,
                "file_size": path.stat().st_size,
            }

        except ValidationError:
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error validating script path: {e}",
                details=f"Script path: {script_path}",
            ) from e

    @staticmethod
    def validate_label(label: str) -> dict[str, str | bool | int]:
        """
        Validate a context menu label.

        Args:
            label: Label to validate

        Returns:
            Validation result dictionary

        Raises:
            ValidationError: If label is invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not label:
                raise ValidationError("label", "label", "Label is required")

            if not isinstance(label, str):
                raise ValidationError(
                    "label",
                    "label",
                    f"Label must be a string, got {type(label).__name__}",
                )

            label = label.strip()
            if not label:
                raise ValidationError(
                    "label", "label", "Label cannot be empty after stripping"
                )

            # Check length
            if len(label) > ValidationUtils.MAX_LABEL_LENGTH:
                raise ValidationError(
                    "label",
                    "label",
                    f"Label is too long (max {ValidationUtils.MAX_LABEL_LENGTH} characters)",
                )

            # Check for invalid characters
            invalid_chars = ["<", ">", ":", '"', "|", "?", "*", "\\", "/"]
            found_invalid = [char for char in invalid_chars if char in label]
            if found_invalid:
                raise ValidationError(
                    "label",
                    "label",
                    f"Label contains invalid characters: {', '.join(found_invalid)}",
                )

            # Check for control characters
            if any(ord(char) < 32 for char in label):
                raise ValidationError(
                    "label", "label", "Label contains control characters"
                )

            return {"valid": True, "label": label, "length": len(label)}

        except ValidationError:
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error validating label: {e}", details=f"Label: {label}"
            ) from e

    @staticmethod
    def validate_registry_key(key_name: str) -> dict[str, str | bool | int]:
        """
        Validate a registry key name.

        Args:
            key_name: Registry key name to validate

        Returns:
            Validation result dictionary

        Raises:
            ValidationError: If key_name is invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not key_name:
                raise ValidationError(
                    "registry_key", "key_name", "Registry key name is required"
                )

            if not isinstance(key_name, str):
                raise ValidationError(
                    "registry_key",
                    "key_name",
                    f"Registry key name must be a string, got {type(key_name).__name__}",
                )

            key_name = key_name.strip()
            if not key_name:
                raise ValidationError(
                    "registry_key",
                    "key_name",
                    "Registry key name cannot be empty after stripping",
                )

            # Check length
            if len(key_name) > ValidationUtils.MAX_REGISTRY_KEY_LENGTH:
                raise ValidationError(
                    "registry_key",
                    "key_name",
                    f"Registry key name is too long (max {ValidationUtils.MAX_REGISTRY_KEY_LENGTH} characters)",
                )

            # Check pattern
            if not ValidationUtils.REGISTRY_KEY_PATTERN.match(key_name):
                raise ValidationError(
                    "registry_key",
                    "key_name",
                    "Registry key name contains invalid characters. Use only letters, numbers, hyphens, underscores, and dots",
                )

            # Check for reserved names
            reserved_names = {
                "con",
                "prn",
                "aux",
                "nul",
                "com1",
                "com2",
                "com3",
                "com4",
                "com5",
                "com6",
                "com7",
                "com8",
                "com9",
                "lpt1",
                "lpt2",
                "lpt3",
                "lpt4",
                "lpt5",
                "lpt6",
                "lpt7",
                "lpt8",
                "lpt9",
            }
            if key_name.lower() in reserved_names:
                raise ValidationError(
                    "registry_key",
                    "key_name",
                    f"Registry key name '{key_name}' is reserved by Windows",
                )

            return {"valid": True, "key_name": key_name, "length": len(key_name)}

        except ValidationError:
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error validating registry key: {e}",
                details=f"Key name: {key_name}",
            ) from e

    @staticmethod
    def validate_icon_path(icon_path: str) -> dict[str, str | bool | int]:
        """
        Validate an icon path.

        Args:
            icon_path: Icon path to validate

        Returns:
            Validation result dictionary

        Raises:
            ValidationError: If icon_path is invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not icon_path:
                raise ValidationError("icon_path", "icon_path", "Icon path is required")

            if not isinstance(icon_path, str):
                raise ValidationError(
                    "icon_path",
                    "icon_path",
                    f"Icon path must be a string, got {type(icon_path).__name__}",
                )

            icon_path = icon_path.strip()
            if not icon_path:
                raise ValidationError(
                    "icon_path",
                    "icon_path",
                    "Icon path cannot be empty after stripping",
                )

            # Handle special values
            if icon_path.lower() in {"auto", "default", "none"}:
                return {
                    "valid": True,
                    "icon_path": icon_path.lower(),
                    "type": "special",
                }

            # Convert to Path object
            try:
                path = Path(icon_path)
            except Exception as e:
                raise ValidationError(
                    "icon_path", "icon_path", f"Invalid icon path format: {e}"
                ) from e

            # Check if file exists
            try:
                if not path.exists():
                    raise ValidationError(
                        "icon_path", "icon_path", f"Icon file not found: {icon_path}"
                    )
            except (OSError, PermissionError) as e:
                raise ValidationError(
                    "icon_path", "icon_path", f"Cannot access icon file: {e}"
                ) from e

            # Check if it's a file
            try:
                if not path.is_file():
                    raise ValidationError(
                        "icon_path", "icon_path", f"Path is not a file: {icon_path}"
                    )
            except (OSError, PermissionError) as e:
                raise ValidationError(
                    "icon_path", "icon_path", f"Cannot check if path is file: {e}"
                ) from e

            # Check file extension
            extension = path.suffix.lower()
            valid_icon_extensions = {
                ".ico",
                ".exe",
                ".dll",
                ".png",
                ".jpg",
                ".jpeg",
                ".bmp",
            }
            if extension not in valid_icon_extensions:
                raise ValidationError(
                    "icon_path",
                    "icon_path",
                    f"Unsupported icon format: {extension}. Supported: {', '.join(valid_icon_extensions)}",
                )

            # Check file size
            try:
                file_size = path.stat().st_size
                if file_size == 0:
                    raise ValidationError(
                        "icon_path", "icon_path", "Icon file is empty"
                    )
                if file_size > 10 * 1024 * 1024:  # 10MB limit
                    raise ValidationError(
                        "icon_path", "icon_path", "Icon file is too large (max 10MB)"
                    )
            except (OSError, PermissionError) as e:
                raise ValidationError(
                    "icon_path", "icon_path", f"Cannot access icon file: {e}"
                ) from e

            return {
                "valid": True,
                "icon_path": str(path.absolute()),
                "extension": extension,
                "file_size": file_size,
            }

        except ValidationError:
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error validating icon path: {e}",
                details=f"Icon path: {icon_path}",
            ) from e

    @staticmethod
    def validate_backup_data(
        data: dict[str, str | bool | int | list | dict],
    ) -> dict[str, str | bool | int | list]:
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
        try:
            # Input validation
            if not data:
                raise ValidationError(
                    "backup_data", "data", "Backup data must be a dictionary"
                )

            if not isinstance(data, dict):
                raise ValidationError(
                    "backup_data",
                    "data",
                    f"Backup data must be a dictionary, got {type(data).__name__}",
                )

            # Check required top-level keys
            required_keys = ["metadata", "entries"]
            for key in required_keys:
                if key not in data:
                    raise ValidationError(
                        "backup_data", "data", f"Missing required key: {key}"
                    )

            # Validate metadata
            metadata = data["metadata"]
            if not isinstance(metadata, dict):
                raise ValidationError(
                    "backup_data", "data", "Metadata must be a dictionary"
                )

            required_metadata = ["version", "timestamp", "total_entries"]
            for key in required_metadata:
                if key not in metadata:
                    raise ValidationError(
                        "backup_data", "data", f"Missing metadata key: {key}"
                    )

            # Validate entries structure
            entries = data["entries"]
            if not isinstance(entries, dict):
                raise ValidationError(
                    "backup_data", "data", "Entries must be a dictionary"
                )

            # Check for expected context types
            expected_types = ["directory", "background"]
            for context_type in expected_types:
                if context_type not in entries:
                    raise ValidationError(
                        "backup_data", "data", f"Missing context type: {context_type}"
                    )

            # Validate individual entries
            for context_type, context_entries in entries.items():
                if not isinstance(context_entries, list):
                    raise ValidationError(
                        "backup_data",
                        "data",
                        f"Context entries must be a list: {context_type}",
                    )

                for entry in context_entries:
                    if not isinstance(entry, dict):
                        raise ValidationError(
                            "backup_data",
                            "data",
                            f"Entry must be a dictionary in {context_type}",
                        )

                    # Check required entry fields
                    required_entry_fields = ["key_name", "display_name"]
                    for field in required_entry_fields:
                        if field not in entry:
                            raise ValidationError(
                                "backup_data", "data", f"Missing entry field: {field}"
                            )

            return {
                "valid": True,
                "entry_count": metadata.get("total_entries", 0),
                "context_types": list(entries.keys()),
            }

        except ValidationError:
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error validating backup data: {e}",
                details="Failed to validate backup data structure",
            ) from e

    @staticmethod
    def check_permissions() -> dict[str, str | bool]:
        """
        Check if the current user has sufficient permissions for registry operations.

        Returns:
            Permission check result dictionary

        Raises:
            ContextUtilityError: For unexpected errors
        """
        try:
            # Check if running on Windows
            if os.name != "nt":
                return {
                    "has_permissions": False,
                    "error": "Registry operations are only supported on Windows",
                }

            # Try to access registry for writing
            test_key = "Software\\Classes\\Directory\\shell\\WOMM_TEST_PERMISSIONS"

            try:
                # Try to create a test key
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, test_key)
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, test_key)
                winreg.CloseKey(key)

                return {
                    "has_permissions": True,
                    "level": "user",
                    "message": "User has sufficient permissions for registry operations",
                }

            except PermissionError:
                return {
                    "has_permissions": False,
                    "error": "Insufficient permissions. Try running as administrator",
                    "level": "admin_required",
                }

            except Exception as e:
                return {
                    "has_permissions": False,
                    "error": f"Permission check failed: {str(e)}",
                }

        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error checking permissions: {e}",
                details="Failed to check registry permissions",
            ) from e

    @staticmethod
    def validate_windows_compatibility() -> dict[str, str | bool]:
        """
        Check Windows compatibility for context menu operations.

        Returns:
            Compatibility check result dictionary

        Raises:
            ContextUtilityError: For unexpected errors
        """
        try:
            # Check OS
            if os.name != "nt":
                return {
                    "compatible": False,
                    "error": "Context menu operations are only supported on Windows",
                }

            # Check Windows version
            try:
                import platform

                windows_version = platform.version()

                # Windows 7 and later are supported
                if int(windows_version.split(".")[0]) < 6:
                    return {
                        "compatible": False,
                        "error": "Windows 7 or later is required",
                    }

            except Exception as e:
                return {
                    "compatible": False,
                    "error": f"Cannot determine Windows version: {str(e)}",
                }

            # Check if registry is accessible
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, "Software\\Classes", 0, winreg.KEY_READ
                )
                winreg.CloseKey(key)
            except Exception as e:
                return {
                    "compatible": False,
                    "error": f"Cannot access Windows Registry: {str(e)}",
                }

            return {
                "compatible": True,
                "windows_version": windows_version,
                "message": "System is compatible with context menu operations",
            }

        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error checking Windows compatibility: {e}",
                details="Failed to validate system compatibility",
            ) from e

    @staticmethod
    def validate_command_parameters(
        script_path: str, label: str, icon: str | None = None
    ) -> dict[str, str | bool | list | dict]:
        """
        Validate all parameters for context menu registration.

        Args:
            script_path: Path to the script
            label: Display label
            icon: Icon path (optional)

        Returns:
            Comprehensive validation result

        Raises:
            ValidationError: If parameters are invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not script_path:
                raise ValidationError(
                    "command_parameters", "script_path", "Script path is required"
                )

            if not label:
                raise ValidationError(
                    "command_parameters", "label", "Label is required"
                )

            if not isinstance(script_path, str):
                raise ValidationError(
                    "command_parameters",
                    "script_path",
                    f"Script path must be a string, got {type(script_path).__name__}",
                )

            if not isinstance(label, str):
                raise ValidationError(
                    "command_parameters",
                    "label",
                    f"Label must be a string, got {type(label).__name__}",
                )

            if icon is not None and not isinstance(icon, str):
                raise ValidationError(
                    "command_parameters",
                    "icon",
                    f"Icon must be a string, got {type(icon).__name__}",
                )

            results = {"valid": True, "errors": [], "warnings": [], "details": {}}

            # Validate script path
            try:
                script_validation = ValidationUtils.validate_script_path(script_path)
                results["details"]["script"] = script_validation
                if not script_validation["valid"]:
                    results["valid"] = False
                    results["errors"].append(script_validation["error"])
            except ValidationError as e:
                results["valid"] = False
                results["errors"].append(str(e))

            # Validate label
            try:
                label_validation = ValidationUtils.validate_label(label)
                results["details"]["label"] = label_validation
                if not label_validation["valid"]:
                    results["valid"] = False
                    results["errors"].append(label_validation["error"])
            except ValidationError as e:
                results["valid"] = False
                results["errors"].append(str(e))

            # Validate icon if provided
            if icon:
                try:
                    icon_validation = ValidationUtils.validate_icon_path(icon)
                    results["details"]["icon"] = icon_validation
                    if not icon_validation["valid"]:
                        results["warnings"].append(
                            f"Icon validation: {icon_validation['error']}"
                        )
                except ValidationError as e:
                    results["warnings"].append(f"Icon validation: {str(e)}")

            # Check permissions
            try:
                permission_check = ValidationUtils.check_permissions()
                results["details"]["permissions"] = permission_check
                if not permission_check["has_permissions"]:
                    results["valid"] = False
                    results["errors"].append(permission_check["error"])
            except Exception as e:
                results["warnings"].append(f"Permission check failed: {str(e)}")

            # Check compatibility
            try:
                compatibility_check = ValidationUtils.validate_windows_compatibility()
                results["details"]["compatibility"] = compatibility_check
                if not compatibility_check["compatible"]:
                    results["valid"] = False
                    results["errors"].append(compatibility_check["error"])
            except Exception as e:
                results["warnings"].append(f"Compatibility check failed: {str(e)}")

            return results

        except ValidationError:
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error validating command parameters: {e}",
                details=f"Script path: {script_path}, Label: {label}, Icon: {icon}",
            ) from e

    @staticmethod
    def sanitize_registry_key(key_name: str) -> str:
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
        try:
            # Input validation
            if not key_name:
                raise ValidationError(
                    "sanitize_registry_key",
                    "key_name",
                    "Key name cannot be None or empty",
                )

            if not isinstance(key_name, str):
                raise ValidationError(
                    "sanitize_registry_key",
                    "key_name",
                    f"Key name must be a string, got {type(key_name).__name__}",
                )

            # Remove invalid characters
            sanitized = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", key_name)

            # Remove leading/trailing invalid characters
            sanitized = sanitized.strip("_")

            # Ensure it's not empty
            if not sanitized:
                sanitized = "womm_entry"

            # Limit length
            if len(sanitized) > ValidationUtils.MAX_REGISTRY_KEY_LENGTH:
                sanitized = sanitized[: ValidationUtils.MAX_REGISTRY_KEY_LENGTH]

            return sanitized

        except ValidationError:
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error sanitizing registry key: {e}",
                details=f"Key name: {key_name}",
            ) from e

    @staticmethod
    def sanitize_label(label: str) -> str:
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
        try:
            # Input validation
            if not label:
                raise ValidationError(
                    "sanitize_label", "label", "Label cannot be None or empty"
                )

            if not isinstance(label, str):
                raise ValidationError(
                    "sanitize_label",
                    "label",
                    f"Label must be a string, got {type(label).__name__}",
                )

            # Remove invalid characters
            invalid_chars = ["<", ">", ":", '"', "|", "?", "*", "\\", "/"]
            sanitized = label
            for char in invalid_chars:
                sanitized = sanitized.replace(char, " ")

            # Remove control characters
            sanitized = "".join(char for char in sanitized if ord(char) >= 32)

            # Remove extra whitespace
            sanitized = " ".join(sanitized.split())

            # Limit length
            if len(sanitized) > ValidationUtils.MAX_LABEL_LENGTH:
                sanitized = sanitized[: ValidationUtils.MAX_LABEL_LENGTH]

            return sanitized

        except ValidationError:
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error sanitizing label: {e}", details=f"Label: {label}"
            ) from e
