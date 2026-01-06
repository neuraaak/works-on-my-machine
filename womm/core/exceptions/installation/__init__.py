#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS INSTALLATION - Installation Exceptions Package
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Installation exceptions package for Works On My Machine.

This package contains all exceptions used by installation and uninstallation modules.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .installation_exceptions import (
    ExecutableVerificationError,
    FileVerificationError,
    InstallationFileError,
    InstallationManagerError,
    InstallationPathError,
    InstallationSystemError,
    InstallationUtilityError,
    InstallationVerificationError,
    PathUtilityError,
)
from .uninstallation_exceptions import (
    DirectoryAccessError,
    FileScanError,
    UninstallationFileError,
    UninstallationManagerError,
    UninstallationManagerVerificationError,
    UninstallationPathError,
    UninstallationUtilityError,
    UninstallationVerificationError,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Installation Utility exceptions
    "InstallationUtilityError",
    "FileVerificationError",
    "PathUtilityError",
    "ExecutableVerificationError",
    # Installation Manager exceptions
    "InstallationManagerError",
    "InstallationFileError",
    "InstallationPathError",
    "InstallationVerificationError",
    "InstallationSystemError",
    # Uninstallation Utility exceptions
    "UninstallationUtilityError",
    "FileScanError",
    "DirectoryAccessError",
    "UninstallationVerificationError",
    # Uninstallation Manager exceptions
    "UninstallationManagerError",
    "UninstallationFileError",
    "UninstallationPathError",
    "UninstallationManagerVerificationError",
]
