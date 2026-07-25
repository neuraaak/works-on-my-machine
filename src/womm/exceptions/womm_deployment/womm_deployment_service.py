#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# WOMM DEPLOYMENT SERVICE EXCEPTIONS - Deployment Service Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
WOMM deployment service exceptions for Works On My Machine.

This module contains the single exception raised by the deployment services:
- WommInstallerService (womm/services/womm_setup/installer_service.py)
- WommUninstallerService (womm/services/womm_setup/uninstaller_service.py)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION
# ///////////////////////////////////////////////////////////////


class WommDeploymentServiceError(Exception):
    """Single exception for the WOMM deployment services.

    Covers every deployment failure (PATH verification, command accessibility,
    executable verification, removal verification, …). The failing step is
    carried by the ``operation`` field rather than by per-step subclasses, since
    no caller branches on the specific failure kind.
    """

    def __init__(
        self,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            operation: The deployment step that failed (e.g. 'path_verification')
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.reason = reason
        self.details = details
        self.message = f"{operation}: {reason}"
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of error."""
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["WommDeploymentServiceError"]
