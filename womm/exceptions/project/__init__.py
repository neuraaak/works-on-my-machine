#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS PROJECT - Project Service Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Project service exceptions for Works On My Machine.

This package exports all exceptions for project operations.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .project_interface import (
    CreateInterfaceError,
    ProjectDetectionInterfaceError,
    ProjectInterfaceError,
    SetupInterfaceError,
    TemplateInterfaceError,
)
from .project_service import (
    ProjectDetectionServiceError,
    ProjectServiceError,
    TemplateServiceError,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [  # noqa: RUF022
    # project_interface
    "CreateInterfaceError",
    "ProjectDetectionInterfaceError",
    "ProjectInterfaceError",
    "SetupInterfaceError",
    "TemplateInterfaceError",
    # project_service
    "ProjectDetectionServiceError",
    "ProjectServiceError",
    "TemplateServiceError",
]
