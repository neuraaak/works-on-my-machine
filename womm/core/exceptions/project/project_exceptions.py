#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT EXCEPTIONS - Project Management Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Project management exceptions for Works On My Machine.

This module contains custom exceptions used specifically by project management modules:
- ProjectManager (womm/core/managers/project/project_manager.py)
- Project utilities (womm/core/utils/project/*.py)

Following a pragmatic approach with focused exception types:
1. ProjectUtilityError - Base exception for project utilities
2. ProjectDetectionError - Project detection errors
3. ProjectValidationError - Project validation errors
4. TemplateError - Template processing errors
5. VSCodeConfigError - VSCode configuration errors
6. ProjectManagerError - Base exception for project manager
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////

# ///////////////////////////////////////////////////////////////
# UTILITY EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class ProjectUtilityError(Exception):
    """Base exception for all project utility errors.

    This is the main exception class for all project utility operations.
    Used for general errors like invalid arguments, unexpected failures, etc.
    """

    def __init__(self, message: str, details: str | None = None) -> None:
        """Initialize the exception with a message and optional details.

        Args:
            message: Human-readable error message
            details: Optional technical details for debugging
        """
        self.message = message
        self.details = details
        super().__init__(self.message)


# ///////////////////////////////////////////////////////////////
# PROJECT DETECTION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class ProjectDetectionError(ProjectUtilityError):
    """Project detection errors for project management operations.

    This exception is raised when project detection operations fail,
    such as identifying project types or analyzing project structure.
    """

    def __init__(
        self,
        operation: str,
        project_path: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize project detection error with specific context.

        Args:
            operation: The operation being performed (e.g., "type_detection", "structure_analysis")
            project_path: The project path being analyzed
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.project_path = project_path
        self.reason = reason
        message = f"Project detection {operation} failed for '{project_path}': {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# PROJECT VALIDATION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class ProjectValidationError(ProjectUtilityError):
    """Project validation errors for project management operations.

    This exception is raised when project validation operations fail,
    such as validating project names, paths, or configurations.
    """

    def __init__(
        self,
        validation_type: str,
        value: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize project validation error with specific context.

        Args:
            validation_type: Type of validation being performed (e.g., "name", "path", "config")
            value: The value being validated
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.validation_type = validation_type
        self.value = value
        self.reason = reason
        message = (
            f"Project validation '{validation_type}' failed for '{value}': {reason}"
        )
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# TEMPLATE EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class TemplateError(ProjectUtilityError):
    """Template processing errors for project management operations.

    This exception is raised when template operations fail,
    such as generating templates or processing template placeholders.
    """

    def __init__(
        self,
        operation: str,
        template_path: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize template error with specific context.

        Args:
            operation: The operation being performed (e.g., "generation", "placeholder_replacement")
            template_path: The template file being processed
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.template_path = template_path
        self.reason = reason
        message = f"Template {operation} failed for '{template_path}': {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# VSCODE CONFIG EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class VSCodeConfigError(ProjectUtilityError):
    """VSCode configuration errors for project management operations.

    This exception is raised when VSCode configuration operations fail,
    such as generating settings or configuring extensions.
    """

    def __init__(
        self,
        operation: str,
        config_path: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize VSCode config error with specific context.

        Args:
            operation: The operation being performed (e.g., "settings_generation", "extension_config")
            config_path: The configuration file being processed
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.config_path = config_path
        self.reason = reason
        message = f"VSCode config {operation} failed for '{config_path}': {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# MANAGER EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class ProjectManagerError(Exception):
    """Base exception for ProjectManager errors.

    This exception is raised when ProjectManager operations fail,
    such as process orchestration, progress tracking, or state management.
    """

    def __init__(self, message: str, details: str | None = None) -> None:
        """Initialize the manager error with a message and optional details.

        Args:
            message: Human-readable error message
            details: Optional technical details for debugging
        """
        self.message = message
        self.details = details
        super().__init__(self.message)
