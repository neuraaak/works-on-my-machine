#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT EXCEPTIONS - Context Menu Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Context menu exceptions for Works On My Machine.

This module contains custom exceptions used specifically by context menu modules:
- ContextMenuManager (womm/core/managers/context/managers/context_menu.py)
- BackupManager (womm/core/managers/context/managers/backup_manager.py)
- IconManager (womm/core/managers/context/managers/icon_manager.py)
- ScriptDetector (womm/core/managers/context/managers/script_detector.py)
- RegistryUtils (womm/core/utils/context/registry_utils.py)
- ValidationUtils (womm/core/utils/context/validation.py)

Following a pragmatic approach with focused exception types:
1. ContextUtilityError - Base exception for context utilities
2. ContextMenuError - Context menu management errors
3. BackupError - Backup management errors
4. IconError - Icon management errors
5. ScriptError - Script detection errors
6. RegistryError - Registry operation errors
7. ValidationError - Validation errors
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION
# ///////////////////////////////////////////////////////////////


class ContextUtilityError(Exception):
    """Base exception for all context utility errors.

    This is the main exception class for all context utility operations.
    Used for general errors like invalid arguments, unexpected failures, etc.
    """

    def __init__(self, message: str, details: str | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Error message
            details: Additional error details
        """
        self.message = message
        self.details = details
        super().__init__(self.message)


# ///////////////////////////////////////////////////////////////
# CONTEXT MENU EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class ContextMenuError(ContextUtilityError):
    """Exception for context menu management errors.

    Used for errors related to context menu registration, unregistration, and management.
    """

    def __init__(
        self,
        operation: str,
        script_path: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize the context menu error.

        Args:
            operation: Operation that failed (register, unregister, list)
            script_path: Path to the script
            reason: Reason for failure
            details: Additional error details
        """
        self.operation = operation
        self.script_path = script_path
        self.reason = reason
        message = f"Context menu {operation} failed for {script_path}: {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# BACKUP EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class BackupError(ContextUtilityError):
    """Exception for backup management errors.

    Used for errors related to backup creation, restoration, and management.
    """

    def __init__(
        self,
        operation: str,
        backup_file: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize the backup error.

        Args:
            operation: Operation that failed (create, restore, list)
            backup_file: Path to the backup file
            reason: Reason for failure
            details: Additional error details
        """
        self.operation = operation
        self.backup_file = backup_file
        self.reason = reason
        message = f"Backup {operation} failed for {backup_file}: {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# ICON EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class IconError(ContextUtilityError):
    """Exception for icon management errors.

    Used for errors related to icon detection, validation, and management.
    """

    def __init__(
        self,
        operation: str,
        icon_path: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize the icon error.

        Args:
            operation: Operation that failed (resolve, validate)
            icon_path: Path to the icon
            reason: Reason for failure
            details: Additional error details
        """
        self.operation = operation
        self.icon_path = icon_path
        self.reason = reason
        message = f"Icon {operation} failed for {icon_path}: {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# SCRIPT EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class ScriptError(ContextUtilityError):
    """Exception for script detection errors.

    Used for errors related to script type detection and command building.
    """

    def __init__(
        self,
        operation: str,
        script_path: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize the script error.

        Args:
            operation: Operation that failed (detect, build_command)
            script_path: Path to the script
            reason: Reason for failure
            details: Additional error details
        """
        self.operation = operation
        self.script_path = script_path
        self.reason = reason
        message = f"Script {operation} failed for {script_path}: {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# REGISTRY EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class RegistryError(ContextUtilityError):
    """Exception for registry operation errors.

    Used for errors related to Windows registry operations.
    """

    def __init__(
        self,
        operation: str,
        registry_path: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize the registry error.

        Args:
            operation: Operation that failed (add, remove, list)
            registry_path: Registry path
            reason: Reason for failure
            details: Additional error details
        """
        self.operation = operation
        self.registry_path = registry_path
        self.reason = reason
        message = f"Registry {operation} failed for {registry_path}: {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# VALIDATION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class ValidationError(ContextUtilityError):
    """Exception for validation errors.

    Used for errors during validation of context menu parameters.
    """

    def __init__(
        self,
        validation_type: str,
        component: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize the validation error.

        Args:
            validation_type: Type of validation that failed
            component: Component being validated
            reason: Reason for failure
            details: Additional error details
        """
        self.validation_type = validation_type
        self.component = component
        self.reason = reason
        message = f"Validation {validation_type} failed for {component}: {reason}"
        super().__init__(message, details)
