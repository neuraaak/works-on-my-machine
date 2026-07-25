#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# WOMM SETUP UI - Installation/Uninstallation UI Package
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""UI components for WOMM installation/uninstallation commands."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .display import (
    render_install_plan_failure,
    render_installation_result,
    render_uninstall_cancelled,
    render_uninstall_plan_failure,
    render_uninstallation_result,
    render_windows_install_tips,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "render_install_plan_failure",
    "render_installation_result",
    "render_uninstall_cancelled",
    "render_uninstall_plan_failure",
    "render_uninstallation_result",
    "render_windows_install_tips",
]
