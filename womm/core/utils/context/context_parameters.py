#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT PARAMETERS - Context Menu Parameters Management
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Context parameters management for intelligent context menu registration.

This module provides functionality to handle intelligent context parameters
like --root, --file, --files, --background and automatically generate
appropriate command parameters and registry paths.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from enum import Enum

# Local imports
from ...exceptions.context.context_exceptions import (
    ContextUtilityError,
    ValidationError,
)


class ContextType(Enum):
    """Types of context menu entries."""

    DIRECTORY = "directory"
    BACKGROUND = "background"
    FILE = "file"
    FILES = "files"
    ROOT = "root"


class ContextParameters:
    """Manages intelligent context parameters for context menu registration."""

    # Registry paths for different context types
    REGISTRY_PATHS = {
        ContextType.DIRECTORY: "Software\\Classes\\Directory\\shell",
        ContextType.BACKGROUND: "Software\\Classes\\Directory\\background\\shell",
        ContextType.FILE: "Software\\Classes\\*\\shell",
        ContextType.FILES: "Software\\Classes\\*\\shell",
        ContextType.ROOT: "Software\\Classes\\Drive\\shell",
    }

    # Command parameters for different context types
    COMMAND_PARAMETERS = {
        ContextType.DIRECTORY: "%V",  # Selected folder
        ContextType.BACKGROUND: "%V",  # Background context
        ContextType.FILE: "%1",  # Single selected file
        ContextType.FILES: "%V",  # Multiple selected files
        ContextType.ROOT: "%V",  # Root directory (drive)
    }

    # File type extensions for different contexts
    FILE_TYPE_EXTENSIONS = {
        "image": {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".tiff",
            ".webp",
            ".svg",
            ".ico",
        },
        "text": {
            ".txt",
            ".md",
            ".py",
            ".js",
            ".html",
            ".css",
            ".json",
            ".xml",
            ".csv",
            ".log",
        },
        "archive": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".cab"},
        "document": {
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".odt",
            ".ods",
            ".odp",
        },
        "media": {
            ".mp3",
            ".mp4",
            ".avi",
            ".mkv",
            ".wav",
            ".flac",
            ".mov",
            ".wmv",
            ".flv",
        },
        "code": {
            ".py",
            ".js",
            ".ts",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".cs",
            ".php",
            ".rb",
            ".go",
            ".rs",
        },
    }

    def __init__(self):
        """Initialize the context parameters manager."""
        self.context_types: set[ContextType] = set()
        self.file_types: set[str] = set()
        self.custom_extensions: set[str] = set()

    def add_context_type(self, context_type: ContextType) -> None:
        """
        Add a context type to the parameters.

        Args:
            context_type: The context type to add

        Raises:
            ValidationError: If context_type is invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not context_type:
                raise ValidationError(
                    "context_type", "context_type", "Context type cannot be None"
                )

            if not isinstance(context_type, ContextType):
                raise ValidationError(
                    "context_type",
                    "context_type",
                    f"Context type must be a ContextType enum, got {type(context_type).__name__}",
                )

            self.context_types.add(context_type)

        except ValidationError:
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error adding context type: {e}",
                details=f"Context type: {context_type}",
            ) from e

    def add_file_type(self, file_type: str) -> None:
        """
        Add a file type to the parameters.

        Args:
            file_type: The file type to add (e.g., 'image', 'text', 'archive')

        Raises:
            ValidationError: If file_type is invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not file_type:
                raise ValidationError(
                    "file_type", "file_type", "File type cannot be None or empty"
                )

            if not isinstance(file_type, str):
                raise ValidationError(
                    "file_type",
                    "file_type",
                    f"File type must be a string, got {type(file_type).__name__}",
                )

            file_type = file_type.strip()
            if not file_type:
                raise ValidationError(
                    "file_type",
                    "file_type",
                    "File type cannot be empty after stripping",
                )

            if file_type in self.FILE_TYPE_EXTENSIONS:
                self.file_types.add(file_type)
            else:
                # Treat as custom extension
                if file_type.startswith("."):
                    self.custom_extensions.add(file_type.lower())
                else:
                    self.custom_extensions.add(f".{file_type.lower()}")

        except ValidationError:
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error adding file type: {e}",
                details=f"File type: {file_type}",
            ) from e

    def get_registry_paths(self) -> list[str]:
        """
        Get registry paths for all configured context types.

        Returns:
            List of registry paths

        Raises:
            ContextUtilityError: For unexpected errors
        """
        try:
            paths = []
            for context_type in self.context_types:
                if context_type in self.REGISTRY_PATHS:
                    paths.append(self.REGISTRY_PATHS[context_type])
            return paths

        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error getting registry paths: {e}",
                details=f"Context types: {[ct.value for ct in self.context_types]}",
            ) from e

    def get_command_parameter(self, context_type: ContextType) -> str:
        """
        Get the appropriate command parameter for a context type.

        Args:
            context_type: The context type

        Returns:
            Command parameter string

        Raises:
            ValidationError: If context_type is invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not context_type:
                raise ValidationError(
                    "command_parameter", "context_type", "Context type cannot be None"
                )

            if not isinstance(context_type, ContextType):
                raise ValidationError(
                    "command_parameter",
                    "context_type",
                    f"Context type must be a ContextType enum, got {type(context_type).__name__}",
                )

            return self.COMMAND_PARAMETERS.get(context_type, "%V")

        except ValidationError:
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error getting command parameter: {e}",
                details=f"Context type: {context_type}",
            ) from e

    def get_file_extensions(self) -> set[str]:
        """
        Get all file extensions for configured file types.

        Returns:
            Set of file extensions

        Raises:
            ContextUtilityError: For unexpected errors
        """
        try:
            extensions = set()

            # Add extensions from file types
            for file_type in self.file_types:
                if file_type in self.FILE_TYPE_EXTENSIONS:
                    extensions.update(self.FILE_TYPE_EXTENSIONS[file_type])

            # Add custom extensions
            extensions.update(self.custom_extensions)

            return extensions

        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error getting file extensions: {e}",
                details=f"File types: {list(self.file_types)}, Custom extensions: {list(self.custom_extensions)}",
            ) from e

    def build_command(self, base_command: str, context_type: ContextType) -> str:
        """
        Build the final command with appropriate parameters.

        Args:
            base_command: Base command without parameters
            context_type: Context type for parameter selection

        Returns:
            Complete command with parameters

        Raises:
            ValidationError: If parameters are invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not base_command:
                raise ValidationError(
                    "command_building",
                    "base_command",
                    "Base command cannot be None or empty",
                )

            if not isinstance(base_command, str):
                raise ValidationError(
                    "command_building",
                    "base_command",
                    f"Base command must be a string, got {type(base_command).__name__}",
                )

            if not context_type:
                raise ValidationError(
                    "command_building", "context_type", "Context type cannot be None"
                )

            if not isinstance(context_type, ContextType):
                raise ValidationError(
                    "command_building",
                    "context_type",
                    f"Context type must be a ContextType enum, got {type(context_type).__name__}",
                )

            parameter = self.get_command_parameter(context_type)

            # Check if command already has a parameter at the end (various formats)
            if base_command.endswith('"%V"'):
                # Replace "%V" with new parameter
                return base_command[:-4] + f'"{parameter}"'
            elif base_command.endswith('%V"'):
                # Replace %V" with new parameter
                return base_command[:-3] + f'{parameter}"'
            elif base_command.endswith("%V"):
                # Replace %V with new parameter
                return base_command[:-2] + parameter
            elif base_command.endswith('"'):
                # Command already has quotes, add parameter outside
                return f"{base_command} {parameter}"
            else:
                # Add quotes and parameter
                return f'"{base_command}" {parameter}'

        except (ValidationError, ContextUtilityError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error building command: {e}",
                details=f"Base command: {base_command}, Context type: {context_type}",
            ) from e

    def validate_parameters(self) -> dict[str, str | bool | list]:
        """
        Validate the current parameter configuration.

        Returns:
            Validation result dictionary

        Raises:
            ContextUtilityError: For unexpected errors
        """
        try:
            errors = []
            warnings = []

            # Check if context types are specified
            if not self.context_types:
                errors.append("No context types specified")

            # Check for conflicting context types
            if (
                ContextType.FILE in self.context_types
                and ContextType.FILES in self.context_types
            ):
                warnings.append(
                    "Both --file and --files specified, --files will take precedence"
                )

            # Check file types
            if self.file_types:
                invalid_types = self.file_types - set(self.FILE_TYPE_EXTENSIONS.keys())
                if invalid_types:
                    warnings.append(f"Unknown file types: {', '.join(invalid_types)}")

            # Check custom extensions
            for ext in self.custom_extensions:
                if not ext.startswith("."):
                    errors.append(f"Custom extension must start with '.': {ext}")

            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "context_types": [ct.value for ct in self.context_types],
                "file_types": list(self.file_types),
                "custom_extensions": list(self.custom_extensions),
            }

        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error validating parameters: {e}",
                details="Failed to validate context parameters",
            ) from e

    def get_description(self) -> str:
        """
        Get a human-readable description of the current configuration.

        Returns:
            Description string

        Raises:
            ContextUtilityError: For unexpected errors
        """
        try:
            parts = []

            # Context types
            if self.context_types:
                context_names = [ct.value for ct in self.context_types]
                parts.append(f"Context: {', '.join(context_names)}")

            # File types
            if self.file_types:
                parts.append(f"File types: {', '.join(self.file_types)}")

            # Custom extensions
            if self.custom_extensions:
                parts.append(f"Extensions: {', '.join(sorted(self.custom_extensions))}")

            return (
                " | ".join(parts)
                if parts
                else "Default context (directory + background)"
            )

        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error getting description: {e}",
                details="Failed to generate context description",
            ) from e

    @classmethod
    def from_flags(
        cls,
        root: bool = False,
        file: bool = False,
        files: bool = False,
        background: bool = False,
        file_types: list[str] | None = None,
        extensions: list[str] | None = None,
    ) -> "ContextParameters":
        """
        Create ContextParameters from command line flags.

        Args:
            root: --root flag
            file: --file flag
            files: --files flag
            background: --background flag
            file_types: List of file types
            extensions: List of custom extensions

        Returns:
            Configured ContextParameters instance

        Raises:
            ValidationError: If parameters are invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if file_types is not None and not isinstance(file_types, list):
                raise ValidationError(
                    "from_flags",
                    "file_types",
                    f"File types must be a list, got {type(file_types).__name__}",
                )

            if extensions is not None and not isinstance(extensions, list):
                raise ValidationError(
                    "from_flags",
                    "extensions",
                    f"Extensions must be a list, got {type(extensions).__name__}",
                )

            params = cls()

            # Add context types based on flags
            if root:
                params.add_context_type(ContextType.ROOT)
            if file:
                params.add_context_type(ContextType.FILE)
            if files:
                params.add_context_type(ContextType.FILES)
            if background:
                params.add_context_type(ContextType.BACKGROUND)

            # If no specific context types specified, use defaults
            if not any([root, file, files, background]):
                params.add_context_type(ContextType.DIRECTORY)
                params.add_context_type(ContextType.BACKGROUND)

            # Add file types
            if file_types:
                for file_type in file_types:
                    params.add_file_type(file_type)

            # Add custom extensions
            if extensions:
                for ext in extensions:
                    params.add_file_type(ext)

            return params

        except (ValidationError, ContextUtilityError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error creating ContextParameters from flags: {e}",
                details=f"Root: {root}, File: {file}, Files: {files}, Background: {background}",
            ) from e

    @classmethod
    def get_available_file_types(cls) -> dict[str, set[str]]:
        """
        Get all available file types and their extensions.

        Returns:
            Dictionary of file types and their extensions

        Raises:
            ContextUtilityError: For unexpected errors
        """
        try:
            return cls.FILE_TYPE_EXTENSIONS.copy()
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error getting available file types: {e}",
                details="Failed to copy file type extensions",
            ) from e

    @classmethod
    def get_context_type_help(cls) -> str:
        """
        Get help text for context types.

        Returns:
            Help text string

        Raises:
            ContextUtilityError: For unexpected errors
        """
        try:
            help_text = "Available context types:\n"
            help_text += "• --root: Root directories (drives)\n"
            help_text += "• --file: Single file selection\n"
            help_text += "• --files: Multiple file selection\n"
            help_text += "• --background: Background context (empty space)\n"
            help_text += "• Default: Both directory and background contexts\n"
            return help_text
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error getting context type help: {e}",
                details="Failed to generate help text",
            ) from e

    @classmethod
    def get_file_type_help(cls) -> str:
        """
        Get help text for file types.

        Returns:
            Help text string

        Raises:
            ContextUtilityError: For unexpected errors
        """
        try:
            help_text = "Available file types:\n"
            for file_type, extensions in cls.FILE_TYPE_EXTENSIONS.items():
                ext_list = ", ".join(sorted(extensions))
                help_text += f"• {file_type}: {ext_list}\n"
            help_text += "• Custom extensions: Use --extensions .ext1 .ext2\n"
            return help_text
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error getting file type help: {e}",
                details="Failed to generate help text",
            ) from e
