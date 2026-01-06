#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS PROJECT - Project Management Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Project management exceptions for Works On My Machine.

This package contains custom exceptions used specifically by project management modules:
- ProjectManager (womm/core/managers/project/project_manager.py)
- Project utilities (womm/core/utils/project/*.py)

Following a pragmatic approach with focused exception types:
1. ProjectUtilityError - Base exception for project utilities
2. ProjectDetectionError - Project detection errors
3. ProjectValidationError - Project validation errors
4. TemplateError - Template processing errors
5. VSCodeConfigError - VSCode configuration errors
6. ProjectManagerError - Base exception for project manager
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .project_exceptions import (
    ProjectDetectionError,
    ProjectManagerError,
    ProjectUtilityError,
    ProjectValidationError,
    TemplateError,
    VSCodeConfigError,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Base exception
    "ProjectUtilityError",
    # Project detection exceptions
    "ProjectDetectionError",
    # Project validation exceptions
    "ProjectValidationError",
    # Template exceptions
    "TemplateError",
    # VSCode configuration exceptions
    "VSCodeConfigError",
    # Manager exceptions
    "ProjectManagerError",
]
