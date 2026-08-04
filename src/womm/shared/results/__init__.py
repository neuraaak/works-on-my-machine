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
from .context_results import (
    BackupCleanupResult,
    BackupDataResult,
    BackupFileInfo,
    BackupFileListResult,
    BackupFileResult,
    ContextBackupResult,
    ContextCherryPickResult,
    ContextEntriesResult,
    ContextRegistryResult,
    ContextRestoreResult,
    ContextSetupResult,
    ContextValidationResult,
    ScriptInfoResult,
    ScriptRegistrationResult,
    ScriptUnregistrationResult,
    ScriptValidationResult,
)
from .dependency_results import (
    DependencyCheckResult,
    DependencyInventoryEntry,
    DependencyInventoryResult,
    DependencyProbe,
    DependencyStatusResult,
)
from .doctor_results import DoctorResult
from .file_results import FileOperationResult, FileScanResult, FileSearchResult
from .project_results import (
    ConfigurationResult,
    ProjectCreationResult,
    ProjectDetectionResult,
    ProjectSetupResult,
    SetupResult,
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
    PathBackupContentResult,
    PathBackupInfo,
    PathBackupListResult,
    PathBackupResult,
    PathOperationResult,
    PrerequisitesCheckResult,
    PrerequisitesInstallResult,
    SystemDetectionResult,
    SystemInfoResult,
)
from .template_results import (
    TemplateListResult,
    TemplateStoreResult,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "BackupCleanupResult",
    "BackupDataResult",
    "BackupFileInfo",
    "BackupFileListResult",
    "BackupFileResult",
    "BaseResult",
    "CommandAvailabilityResult",
    "CommandResult",
    "CommandValidationResult",
    "CommandVersionResult",
    "ConfigurationResult",
    "ContextBackupResult",
    "ContextCherryPickResult",
    "ContextEntriesResult",
    "ContextRegistryResult",
    "ContextRestoreResult",
    "ContextSetupResult",
    "ContextValidationResult",
    "DependencyCheckResult",
    "DependencyInventoryEntry",
    "DependencyInventoryResult",
    "DependencyProbe",
    "DependencyStatusResult",
    "DoctorResult",
    "EnvironmentRefreshResult",
    "EnvironmentVerificationResult",
    "FileOperationResult",
    "FileScanResult",
    "FileSearchResult",
    "PathBackupContentResult",
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
    "ScriptInfoResult",
    "ScriptRegistrationResult",
    "ScriptUnregistrationResult",
    "ScriptValidationResult",
    "SecurityReportResult",
    "SecurityResult",
    "SetupResult",
    "SystemDetectionResult",
    "SystemInfoResult",
    "TemplateListResult",
    "TemplateStoreResult",
    "ValidationResult",
]
