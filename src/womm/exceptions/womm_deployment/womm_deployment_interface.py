#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# INSTALLATION INTERFACE EXCEPTIONS - Installation Interface Exception Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Exception classes for installation interface operations.

This module contains custom exceptions used specifically by the installation
interfaces, such as:
- InstallationManagerInterface (womm/interfaces/installation/installation_manager.py)
- UninstallationManagerInterface (womm/interfaces/installation/uninstallation_manager.py)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION
# ///////////////////////////////////////////////////////////////


class WommDeploymentInterfaceError(Exception):
    """Base exception for all installation interface errors.

    This is the main exception class for all installation interface operations.
    Used for general errors like unexpected failures during interface operations.
    """

    def __init__(
        self,
        message: str = "Installation interface error",
        operation: str = "",
        reason: str = "",
        details: str = "",
    ) -> None:
        """Initialize the exception.

        Args:
            message: User-facing error message
            operation: The operation that failed (e.g., 'install', 'uninstall')
            reason: The reason for the failure
            details: Technical details for debugging
        """
        self.message = message
        self.operation = operation
        self.reason = reason
        self.details = details
        super().__init__(self.message)


# ///////////////////////////////////////////////////////////////
# INSTALLATION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class InstallerInterfaceError(WommDeploymentInterfaceError):
    """Exception raised when installation operations fail at the interface level."""


class UninstallerInterfaceError(WommDeploymentInterfaceError):
    """Exception raised when uninstallation operations fail at the interface level."""


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "InstallerInterfaceError",
    "UninstallerInterfaceError",
    "WommDeploymentInterfaceError",
]
