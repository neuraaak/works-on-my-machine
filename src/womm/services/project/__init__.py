#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SERVICES PROJECT - Project Services
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Project services for Works On My Machine.

This package contains services for project management operations including
detection, validation, and configuration.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .conflict_resolution_service import ConflictResolutionService
from .detection_service import ProjectDetectionService
from .env_utils import (
    check_npm_available,
    create_virtual_environment,
    find_pip_executable,
    install_npm_dependencies,
    install_npm_dev_dependencies,
    install_python_dependencies,
)
from .javascript_environment_service import JavaScriptEnvironmentService
from .javascript_project_creation_service import JavaScriptProjectCreationService
from .python_environment_service import PythonEnvironmentService
from .template_service import TemplateService
from .validation_service import ProjectValidationService

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ConflictResolutionService",
    "JavaScriptEnvironmentService",
    "JavaScriptProjectCreationService",
    "ProjectDetectionService",
    "ProjectValidationService",
    "PythonEnvironmentService",
    "TemplateService",
    "check_npm_available",
    "create_virtual_environment",
    "find_pip_executable",
    "install_npm_dependencies",
    "install_npm_dev_dependencies",
    "install_python_dependencies",
]
