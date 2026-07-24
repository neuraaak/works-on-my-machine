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
from .javascript_project_creation_service import JavaScriptProjectCreationService
from .python_project_creation_service import PythonProjectCreationService
from .template_service import TemplateService
from .validation_service import ProjectValidationService

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ConflictResolutionService",
    "JavaScriptProjectCreationService",
    "ProjectDetectionService",
    "ProjectValidationService",
    "PythonProjectCreationService",
    "TemplateService",
]
