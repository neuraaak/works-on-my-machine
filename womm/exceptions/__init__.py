#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS - Custom Exceptions by Domain
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Custom exceptions for Works On My Machine.

This package contains all custom exceptions organized by domain.
Import exceptions from the appropriate domain:

    from exceptions.common import CommandServiceError, FileServiceError
    from exceptions.context import ContextServiceError
    from exceptions.cspell import CSpellError, SpellServiceError
    from exceptions.dependencies import DevToolsError, PackageManagerError
    from exceptions.lint import LintServiceError, ToolExecutionError
    from exceptions.project import ProjectServiceError, TemplateError
    from exceptions.system import SystemServiceError, FileSystemError
    from exceptions.womm_deployment import WommDeploymentServiceError

Available domains:
- common: Command, file, and security service exceptions
- context: Context menu service exceptions
- cspell: Spell checking service exceptions
- dependencies: Dependency management exceptions
- lint: Linting service exceptions
- project: Project management exceptions
- system: System management exceptions
- womm_deployment: WOMM installation/deployment exceptions
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS BY DOMAIN
# ///////////////////////////////////////////////////////////////
# Local imports - Common exceptions
from .common import (
    CommandExecutionError,
    CommandServiceError,
    CommandUtilityError,
    CommandValidationError,
    DirectoryAccessError,
    FileAccessError,
    FileScanError,
    FileServiceError,
    FileValidationError,
    PathValidationError,
    SecurityFilterError,
    SecurityServiceError,
    TimeoutError,
    ValidationServiceError,
)

# Local imports - Context exceptions
from .context import (
    ContextServiceError,
    ContextUtilityError,
    MenuServiceError,
    ScriptDetectorServiceError,
)

# Local imports - CSpell exceptions
from .cspell import (
    CheckServiceError,
    CSpellDictionaryInterfaceError,
    CSpellInterfaceError,
    CSpellServiceError,
    DictionaryServiceError,
)

# Local imports - Dependencies exceptions
from .dependencies import (
    DependenciesInterfaceError,
    DependenciesServiceError,
    DevToolsInterfaceError,
    DevToolsServiceError,
    PackageManagerInterfaceError,
    PackageManagerServiceError,
    RuntimeManagerInterfaceError,
    RuntimeManagerServiceError,
)

# Local imports - Lint exceptions
from .lint import (
    LintInterfaceError,
    LintServiceError,
    PythonLintInterfaceError,
    ToolAvailabilityServiceError,
    ToolExecutionServiceError,
)

# Local imports - Project exceptions
from .project import (
    CreateInterfaceError,
    ProjectDetectionInterfaceError,
    ProjectDetectionServiceError,
    ProjectInterfaceError,
    ProjectServiceError,
    SetupInterfaceError,
    TemplateInterfaceError,
    TemplateServiceError,
)

# Local imports - System exceptions
from .system import (
    DetectorInterfaceError,
    DevEnvDetectionServiceError,
    EnvironmentInterfaceError,
    EnvironmentServiceError,
    FileSystemServiceError,
    InfoServiceError,
    PkgManagerDetectionServiceError,
    RegistryServiceError,
    ReportGenerationServiceError,
    SystemDetectionServiceError,
    SystemInterfaceError,
    SystemServiceError,
    UserPathInterfaceError,
    UserPathServiceError,
)

# Local imports - WOMM Deployment exceptions
from .womm_deployment import (
    DependencyServiceError,
    DeploymentFileServiceError,
    DeploymentUtilityError,
    ExeVerificationServiceError,
    FileVerificationServiceError,
    InstallerInterfaceError,
    PathServiceError,
    PathUtilityError,
    UninstallerInterfaceError,
    VerificationServiceError,
    WommDeploymentInterfaceError,
    WommDeploymentServiceError,
    WommInstallerError,
    WommUninstallerError,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API - All Exceptions
# ///////////////////////////////////////////////////////////////

__all__ = [  # noqa: RUF022
    # Common exceptions
    "CommandExecutionError",
    "CommandServiceError",
    "CommandUtilityError",
    "CommandValidationError",
    "DirectoryAccessError",
    "FileAccessError",
    "FileScanError",
    "FileServiceError",
    "FileValidationError",
    "PathValidationError",
    "SecurityFilterError",
    "SecurityServiceError",
    "TimeoutError",
    "ValidationServiceError",
    # Context exceptions
    "MenuServiceError",
    "ContextServiceError",
    "ContextUtilityError",
    "ScriptDetectorServiceError",
    # CSpell exceptions
    "CheckServiceError",
    "CSpellInterfaceError",
    "DictionaryServiceError",
    "CSpellDictionaryInterfaceError",
    "CSpellInterfaceError",
    "CSpellServiceError",
    # Dependencies exceptions
    "DependenciesInterfaceError",
    "DependenciesServiceError",
    "DevToolsServiceError",
    "DevToolsInterfaceError",
    "PackageManagerServiceError",
    "PackageManagerInterfaceError",
    "RuntimeManagerServiceError",
    "RuntimeManagerInterfaceError",
    # Lint exceptions
    "PythonLintInterfaceError",
    "PythonLintInterfaceError",
    "LintInterfaceError",
    "LintServiceError",
    "PythonLintInterfaceError",
    "PythonLintInterfaceError",
    "ToolAvailabilityServiceError",
    "ToolExecutionServiceError",
    # Project exceptions
    "CreateInterfaceError",
    "ProjectDetectionInterfaceError",
    "ProjectDetectionServiceError",
    "ProjectInterfaceError",
    "ProjectServiceError",
    "SetupInterfaceError",
    "TemplateServiceError",
    "TemplateInterfaceError",
    # System exceptions
    "DevEnvDetectionServiceError",
    "EnvironmentInterfaceError",
    "EnvironmentServiceError",
    "EnvironmentInterfaceError",
    "FileSystemServiceError",
    "PkgManagerDetectionServiceError",
    "UserPathInterfaceError",
    "RegistryServiceError",
    "ReportGenerationServiceError",
    "SystemDetectionServiceError",
    "DetectorInterfaceError",
    "InfoServiceError",
    "SystemInterfaceError",
    "SystemServiceError",
    "UserPathServiceError",
    # WOMM Deployment exceptions
    "DeploymentUtilityError",
    "DependencyServiceError",
    "ExeVerificationServiceError",
    "FileVerificationServiceError",
    "PathUtilityError",
    "WommDeploymentInterfaceError",
    "WommDeploymentServiceError",
    "WommInstallerError",
    "DeploymentFileServiceError",
    "InstallerInterfaceError",
    "PathServiceError",
    "VerificationServiceError",
    "InstallerInterfaceError",
    "WommUninstallerError",
    "UninstallerInterfaceError",
    "VerificationServiceError",
]
