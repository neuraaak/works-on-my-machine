#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# RESULTS - Result Classes Package
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Result classes for Works On My Machine.

This package provides structured data objects for service and interface operations.
Results are organized by domain for better maintainability.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .base import BaseResult, CommandResult
from .command_results import (
    CommandAvailabilityResult,
    CommandVersionResult,
)
from .context_results import (
    ContextRegistryResult,
    ContextValidationResult,
)
from .cspell_results import (
    AddWordsResult,
    CSpellCheckResult,
    CSpellConfigResult,
    CSpellInstallResult,
    CSpellResult,
    CSpellSummary,
    DictionaryResult,
    DictionarySetupResult,
)
from .dependencies_results import (
    DependencyCheckResult,
    DevToolAvailabilityResult,
    DevToolResult,
    PackageManagerAvailabilityResult,
    PackageManagerPlatformResult,
    PackageManagerResult,
    RuntimeInstallationResult,
    RuntimeResult,
)
from .file_results import (
    FileOperationResult,
    FileScanResult,
    FileSearchResult,
)
from .installation_results import (
    InstallationResult,
    UninstallationResult,
    WOMMInstallerVerificationResult,
)
from .lint_results import (
    LintSummaryResult,
    ToolResult,
    ToolStatusResult,
)
from .project_results import (
    ConfigurationResult,
    ProjectCreationResult,
    ProjectDetectionResult,
    ProjectSetupResult,
    SetupResult,
    TemplateResult,
)
from .security_results import (
    CommandValidationResult,
    PathValidationResult,
    SecurityReportResult,
    SecurityResult,
    ValidationResult,
)
from .system_results import (
    EnvironmentRefreshResult,
    EnvironmentVerificationResult,
    PathOperationResult,
    PrerequisitesCheckResult,
    PrerequisitesInstallResult,
    SystemDetectionResult,
    SystemInfoResult,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "AddWordsResult",
    "BaseResult",
    "CSpellCheckResult",
    "CSpellConfigResult",
    "CSpellInstallResult",
    "CSpellResult",
    "CSpellSummary",
    "CommandAvailabilityResult",
    "CommandResult",
    "CommandValidationResult",
    "CommandVersionResult",
    "ConfigurationResult",
    "ContextRegistryResult",
    "ContextValidationResult",
    "DependencyCheckResult",
    "DevToolAvailabilityResult",
    "DevToolResult",
    "DictionaryResult",
    "DictionarySetupResult",
    "EnvironmentRefreshResult",
    "EnvironmentVerificationResult",
    "FileOperationResult",
    "FileScanResult",
    "FileSearchResult",
    "InstallationResult",
    "LintSummaryResult",
    "PackageManagerAvailabilityResult",
    "PackageManagerPlatformResult",
    "PackageManagerResult",
    "PathOperationResult",
    "PathValidationResult",
    "PrerequisitesCheckResult",
    "PrerequisitesInstallResult",
    "ProjectCreationResult",
    "ProjectDetectionResult",
    "ProjectSetupResult",
    "RuntimeInstallationResult",
    "RuntimeResult",
    "SecurityReportResult",
    "SecurityResult",
    "SetupResult",
    "SystemDetectionResult",
    "SystemInfoResult",
    "TemplateResult",
    "ToolResult",
    "ToolStatusResult",
    "UninstallationResult",
    "ValidationResult",
    "WOMMInstallerVerificationResult",
]
