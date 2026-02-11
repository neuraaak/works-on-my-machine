#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS WOMM_DEPLOYMENT - WOMM Deployment Service Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
WOMM deployment service exceptions for Works On My Machine.

This package exports all exceptions for WOMM deployment operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .womm_deployment_interface import (
    InstallerInterfaceError,
    UninstallerInterfaceError,
    WommDeploymentInterfaceError,
)
from .womm_deployment_service import (
    DependencyServiceError,
    DeploymentFileServiceError,
    DeploymentUtilityError,
    ExeVerificationServiceError,
    FileVerificationServiceError,
    PathServiceError,
    PathUtilityError,
    VerificationServiceError,
    WommDeploymentServiceError,
    WommInstallerError,
    WommUninstallerError,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [  # noqa: RUF022
    # womm_deployment_interface
    "WommDeploymentInterfaceError",
    "InstallerInterfaceError",
    "InstallerInterfaceError",
    "UninstallerInterfaceError",
    # womm_deployment_service
    "DeploymentUtilityError",
    "DependencyServiceError",
    "ExeVerificationServiceError",
    "FileVerificationServiceError",
    "PathUtilityError",
    "WommDeploymentServiceError",
    "WommInstallerError",
    "PathServiceError",
    "VerificationServiceError",
    "WommUninstallerError",
    "DeploymentFileServiceError",
    "VerificationServiceError",
]
