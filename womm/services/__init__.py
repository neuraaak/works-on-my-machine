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
    ContextParametersService,
    ContextRegistryService,
    ContextType,
    ContextValidationService,
)

# Local imports - Cspell services
from .cspell import (
    CSpellCheckerService,
    CSpellDictionaryService,
)

# Local imports - Dependencies services
from .dependencies import (
    DevToolsService,
    RuntimeService,
    SystemPackageManagerService,
)

# Local imports - Lint services
from .lint import (
    LintService,
    PythonLintService,
)

# Local imports - Project services
from .project import (
    ConflictResolutionService,
    JavaScriptProjectCreationService,
    ProjectDetectionService,
    ProjectValidationService,
    PythonProjectCreationService,
    TemplateService,
)

# Local imports - System services
from .system import (
    SystemDetectorService,
    SystemEnvironmentService,
    SystemPathService,
)

# Local imports - Womm deployment services
from .womm_setup import (
    WommInstallerService,
    WommUninstallerService,
)

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
    "ContextParametersService",
    "ContextRegistryService",
    "ContextType",
    "ContextValidationService",
    # Cspell services
    "CSpellCheckerService",
    "CSpellDictionaryService",
    # Dependencies services
    "DevToolsService",
    "SystemPackageManagerService",
    "RuntimeService",
    # Lint services
    "LintService",
    "PythonLintService",
    # Project services
    "ConflictResolutionService",
    "JavaScriptProjectCreationService",
    "ProjectDetectionService",
    "ProjectValidationService",
    "PythonProjectCreationService",
    "TemplateService",
    # System services
    "SystemDetectorService",
    "SystemEnvironmentService",
    "SystemPathService",
    # Womm deployment services
    "WommInstallerService",
    "WommUninstallerService",
]
