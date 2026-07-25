#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# INTERFACES INSTALLATION - Installation Interfaces
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Installation interfaces for Works On My Machine.

This package contains installation interface modules that orchestrate services
for installation and uninstallation operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .installer_interface import WommInstallerInterface
from .progress import DeploymentProgressReporter, NullProgressReporter
from .uninstaller_interface import WommUninstallerInterface

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "DeploymentProgressReporter",
    "NullProgressReporter",
    "WommInstallerInterface",
    "WommUninstallerInterface",
]
