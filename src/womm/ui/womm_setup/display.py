#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# WOMM SETUP UI - Installation/Uninstallation UI Components
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Installation/uninstallation UI components for Works On My Machine.

Renders the Result objects returned by ``WommInstallerInterface`` and
``WommUninstallerInterface``. The interfaces carry no UI; all presentation —
including planning-phase failures (already-installed, not-found) — lives
here, driven off the command layer.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from ...shared.results import (
    InstallationResult,
    InstallPlanResult,
    UninstallationResult,
    UninstallPlanResult,
)
from ..common.ezpl_bridge import ezconsole, ezprinter

# ///////////////////////////////////////////////////////////////
# INSTALLATION RENDERERS
# ///////////////////////////////////////////////////////////////


def render_install_plan_failure(plan: InstallPlanResult) -> None:
    """Render a failed installation plan (already installed, precheck failure).

    Args:
        plan: Result of ``WommInstallerInterface.precheck_install()``
    """
    title = (
        "Installation Directory Already Exists"
        if plan.error == "Installation directory already exists"
        else "Pre-check Failed"
    )
    content = plan.message or plan.error
    panel = ezprinter.create_warning_panel(title=title, content=content)
    ezconsole.print("")
    ezconsole.print(panel)


def render_installation_result(result: InstallationResult) -> None:
    """Render the final result of an installation run.

    Args:
        result: Result of ``WommInstallerInterface.execute_install()``
    """
    if not result.success:
        ezprinter.error(f"Installation failed: {result.error}")
        return

    ezconsole.print("")
    ezprinter.success("✅ W.O.M.M installation completed successfully!")
    ezprinter.system(f"📁 Installed to: {result.target_path}")

    completion_content = (
        "WOMM has been successfully installed on your system.\n\n"
        "Getting started:\n"
        "• Run 'womm --help' to see all available commands\n"
        "• Try 'womm init' to set up a new project\n"
        "• Use 'womm deploy' to manage your development tools\n\n"
        "• Restart your terminal for PATH changes to take effect\n\n"
        "Welcome to Works On My Machine!"
    )
    panel = ezprinter.create_success_panel(
        title="Installation Complete", content=completion_content
    )
    ezconsole.print("")
    ezconsole.print(panel)


def render_windows_install_tips() -> None:
    """Render the Windows-specific PATH refresh tips after a successful install."""
    ezprinter.tip(
        "On Windows, the 'womm' command will be available in new terminal sessions."
    )
    ezprinter.tip("To use it immediately in this terminal, run: womm refresh-env")


# ///////////////////////////////////////////////////////////////
# UNINSTALLATION RENDERERS
# ///////////////////////////////////////////////////////////////


def render_uninstall_plan_failure(plan: UninstallPlanResult) -> None:
    """Render a failed uninstallation plan (not installed, scan failure).

    Args:
        plan: Result of ``WommUninstallerInterface.plan_uninstall()``
    """
    title = (
        "WOMM Not Found"
        if plan.error == "WOMM installation not found"
        else "Pre-check Failed"
    )
    panel = ezprinter.create_warning_panel(
        title=title, content=plan.message or plan.error
    )
    ezconsole.print("")
    ezconsole.print(panel)


def render_uninstall_cancelled() -> None:
    """Render the user-cancelled uninstallation message."""
    ezconsole.print("❌ Uninstallation cancelled", style="red")


def render_uninstallation_result(result: UninstallationResult) -> None:
    """Render the final result of an uninstallation run.

    Args:
        result: Result of ``WommUninstallerInterface.execute_uninstall()``
    """
    if not result.success:
        ezprinter.error(f"Uninstallation failed: {result.error}")
        return

    ezconsole.print("")
    ezprinter.success("✅ W.O.M.M uninstallation completed successfully!")
    ezprinter.system(f"📁 Removed from: {result.removed_path}")

    completion_content = (
        "WOMM has been successfully removed from your system.\n\n"
        "To complete the cleanup:\n"
        "• Restart your terminal for PATH changes to take effect\n"
        "• Remove any remaining WOMM references from your shell config files\n\n"
        "Thank you for using Works On My Machine!"
    )
    panel = ezprinter.create_success_panel(
        title="Uninstallation Complete", content=completion_content
    )
    ezconsole.print("")
    ezconsole.print(panel)


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
