#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SERVICES - Service Modules (Implementations)
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Service modules (Implementations) for Works On My Machine.

This package contains service modules that implement business logic
and provide concrete functionality for the WOMM system.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports - Common services
from .common import (
    BaseValidationService,
    CommandRunnerService,
    FileScannerService,
    SecurityValidatorService,
)

# Local imports - Context services
from .context import (
    ContextParameters,
    ContextRegistryService,
    ContextType,
    ContextValidationService,
)

# Local imports - Project services
from .project import (
    ConflictResolutionService,
    JavaScriptEnvironmentService,
    JavaScriptProjectCreationService,
    ProjectDetectionService,
    ProjectValidationService,
    PythonEnvironmentService,
    TemplateService,
)

# Local imports - System services
from .system import SystemDetectorService, SystemEnvironmentService, SystemPathService

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [  # noqa: RUF022
    # Common services
    "BaseValidationService",
    "CommandRunnerService",
    "FileScannerService",
    "SecurityValidatorService",
    # Context services
    "ContextParameters",
    "ContextRegistryService",
    "ContextType",
    "ContextValidationService",
    # Project services
    "ConflictResolutionService",
    "JavaScriptEnvironmentService",
    "JavaScriptProjectCreationService",
    "ProjectDetectionService",
    "ProjectValidationService",
    "PythonEnvironmentService",
    "TemplateService",
    # System services
    "SystemDetectorService",
    "SystemEnvironmentService",
    "SystemPathService",
]
