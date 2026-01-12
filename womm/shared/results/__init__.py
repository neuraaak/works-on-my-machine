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
from .context_results import (
    ContextRegistryResult,
    ContextValidationResult,
)
from .cspell_results import (
    AddWordsResult,
    CSpellConfigResult,
    CSpellInstallResult,
    DictionaryResult,
    DictionarySetupResult,
    SpellCheckResult,
    SpellResult,
    SpellSummary,
)
from .dependencies_results import (
    DependencyCheckResult,
    DevToolResult,
    PackageManagerResult,
    RuntimeResult,
)
from .file_results import (
    FileOperationResult,
    FileScanResult,
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
    "CSpellConfigResult",
    "CSpellInstallResult",
    "CommandResult",
    "ConfigurationResult",
    "ContextRegistryResult",
    "ContextValidationResult",
    "DependencyCheckResult",
    "DevToolResult",
    "DictionaryResult",
    "DictionarySetupResult",
    "EnvironmentRefreshResult",
    "EnvironmentVerificationResult",
    "FileOperationResult",
    "FileScanResult",
    "InstallationResult",
    "LintSummaryResult",
    "PackageManagerResult",
    "PathOperationResult",
    "PrerequisitesCheckResult",
    "PrerequisitesInstallResult",
    "ProjectCreationResult",
    "ProjectDetectionResult",
    "ProjectSetupResult",
    "RuntimeResult",
    "SecurityResult",
    "SetupResult",
    "SpellCheckResult",
    "SpellResult",
    "SpellSummary",
    "SystemDetectionResult",
    "SystemInfoResult",
    "TemplateResult",
    "ToolResult",
    "ToolStatusResult",
    "UninstallationResult",
    "ValidationResult",
    "WOMMInstallerVerificationResult",
]
