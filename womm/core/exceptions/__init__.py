#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS - Custom Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Custom exceptions for Works On My Machine.

This package contains all custom exceptions used throughout the WOMM project.
Provides specialized exception classes for different error scenarios.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .cli import (
    CLIUtilityError,
    CommandExecutionError,
    CommandValidationError,
    TimeoutError,
)
from .common_exceptions import (
    CommonUtilityError,
    ImportUtilityError,
    PathResolutionError,
    SecurityError,
)
from .context import BackupError, ContextMenuError, ContextUtilityError, IconError
from .context import RegistryError as ContextRegistryError
from .context import ScriptError
from .context import ValidationError as ContextValidationError
from .dependencies import (
    DependenciesUtilityError,
    DevToolsError,
    InstallationError,
    PackageManagerError,
    RuntimeManagerError,
)
from .dependencies import ValidationError as DependenciesValidationError
from .file import FileAccessError, FileScanError, FileUtilityError, SecurityFilterError
from .installation import (
    DirectoryAccessError,
    ExecutableVerificationError,
    FileVerificationError,
    InstallationFileError,
    InstallationManagerError,
    InstallationPathError,
    InstallationSystemError,
    InstallationUtilityError,
    InstallationVerificationError,
    PathUtilityError,
    UninstallationFileError,
    UninstallationManagerError,
    UninstallationManagerVerificationError,
    UninstallationPathError,
    UninstallationUtilityError,
    UninstallationVerificationError,
)
from .lint import (
    LintManagerError,
    LintUtilityError,
    LintValidationError,
    ToolAvailabilityError,
    ToolExecutionError,
)
from .project import (
    ProjectDetectionError,
    ProjectManagerError,
    ProjectUtilityError,
    ProjectValidationError,
    TemplateError,
    VSCodeConfigError,
)
from .security import (
    FileValidationError,
    PathValidationError,
    SecurityUtilityError,
    ValidationError,
)
from .spell import (
    CSpellError,
    DictionaryError,
    SpellManagerError,
    SpellUtilityError,
    SpellValidationError,
)
from .system import FileSystemError, RegistryError, UserPathError

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "BackupError",
    # CLI exceptions
    "CLIUtilityError",
    "CSpellError",
    "CommandExecutionError",
    "CommandValidationError",
    # Common utility exceptions
    "CommonUtilityError",
    "ContextMenuError",
    "ContextRegistryError",
    # Context menu exceptions
    "ContextUtilityError",
    "ContextValidationError",
    # Dependencies management exceptions
    "DependenciesUtilityError",
    "DependenciesValidationError",
    "DevToolsError",
    "DictionaryError",
    "DirectoryAccessError",
    "ExecutableVerificationError",
    "FileAccessError",
    "FileScanError",
    "FileSystemError",
    # File scanning exceptions
    "FileUtilityError",
    "FileValidationError",
    "FileVerificationError",
    "IconError",
    "ImportUtilityError",
    "InstallationError",
    "InstallationFileError",
    # Installation Manager exceptions
    "InstallationManagerError",
    "InstallationPathError",
    "InstallationSystemError",
    # Installation Utility exceptions
    "InstallationUtilityError",
    "InstallationVerificationError",
    "LintManagerError",
    # Linting exceptions
    "LintUtilityError",
    "LintValidationError",
    "PackageManagerError",
    "PathResolutionError",
    "PathUtilityError",
    "PathValidationError",
    "ProjectDetectionError",
    "ProjectManagerError",
    # Project management exceptions
    "ProjectUtilityError",
    "ProjectValidationError",
    "RegistryError",
    "RuntimeManagerError",
    "ScriptError",
    "SecurityError",
    "SecurityFilterError",
    # Security exceptions
    "SecurityUtilityError",
    "SpellManagerError",
    # Spell checking exceptions
    "SpellUtilityError",
    "SpellValidationError",
    "TemplateError",
    "TimeoutError",
    "ToolAvailabilityError",
    "ToolExecutionError",
    "UninstallationFileError",
    # Uninstallation Manager exceptions
    "UninstallationManagerError",
    "UninstallationManagerVerificationError",
    "UninstallationPathError",
    # Uninstallation Utility exceptions
    "UninstallationUtilityError",
    "UninstallationVerificationError",
    # System exceptions
    "UserPathError",
    "VSCodeConfigError",
    "ValidationError",
]
