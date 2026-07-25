#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS WOMM_DEPLOYMENT - WOMM Deployment Service Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
WOMM deployment service exceptions for Works On My Machine.

This package exports the single exception raised by the WOMM deployment
services. The interfaces (``WommInstallerInterface``/``WommUninstallerInterface``)
never raise: they translate this exception into a Result.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .womm_deployment_service import WommDeploymentServiceError

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "WommDeploymentServiceError",
]
