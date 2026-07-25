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
from .command_results import CommandAvailabilityResult, CommandVersionResult
from .context_results import ContextRegistryResult, ContextValidationResult
from .file_results import FileOperationResult, FileScanResult, FileSearchResult
from .installation_results import (
    InstallationResult,
    InstallPlanResult,
    UninstallationResult,
    UninstallPlanResult,
    WOMMInstallerVerificationResult,
)
from .lint_results import LintSummaryResult, ToolResult, ToolStatusResult
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
    PathBackupInfo,
    PathBackupListResult,
    PathBackupResult,
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
    "BaseResult",
    "CommandAvailabilityResult",
    "CommandResult",
    "CommandValidationResult",
    "CommandVersionResult",
    "ConfigurationResult",
    "ContextRegistryResult",
    "ContextValidationResult",
    "EnvironmentRefreshResult",
    "EnvironmentVerificationResult",
    "FileOperationResult",
    "FileScanResult",
    "FileSearchResult",
    "InstallPlanResult",
    "InstallationResult",
    "LintSummaryResult",
    "PathBackupInfo",
    "PathBackupListResult",
    "PathBackupResult",
    "PathOperationResult",
    "PathValidationResult",
    "PrerequisitesCheckResult",
    "PrerequisitesInstallResult",
    "ProjectCreationResult",
    "ProjectDetectionResult",
    "ProjectSetupResult",
    "SecurityReportResult",
    "SecurityResult",
    "SetupResult",
    "SystemDetectionResult",
    "SystemInfoResult",
    "TemplateResult",
    "ToolResult",
    "ToolStatusResult",
    "UninstallPlanResult",
    "UninstallationResult",
    "ValidationResult",
    "WOMMInstallerVerificationResult",
]
