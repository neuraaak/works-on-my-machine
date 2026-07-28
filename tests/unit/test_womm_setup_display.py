#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST WOMM SETUP DISPLAY - Renderer branch coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Tests for the install/uninstall Result renderers.

These renderers hold real product logic (which panel title/content is shown
for which failure reason) even though they are UI-layer code; they contain
no interactive input, so they're cheap to verify by asserting on the
``ezprinter``/``ezconsole`` calls each branch makes.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from unittest.mock import MagicMock

# Local imports
from womm.shared.results import (
    InstallationResult,
    InstallPlanResult,
    UninstallationResult,
    UninstallPlanResult,
)
from womm.ui.womm_setup import display as display_module

# ///////////////////////////////////////////////////////////////
# FIXTURES
# ///////////////////////////////////////////////////////////////


def _patch_ui(monkeypatch):
    ezprinter = MagicMock()
    ezconsole = MagicMock()
    ezprinter.create_warning_panel.return_value = "warning-panel"
    ezprinter.create_success_panel.return_value = "success-panel"
    monkeypatch.setattr(display_module, "ezprinter", ezprinter)
    monkeypatch.setattr(display_module, "ezconsole", ezconsole)
    return ezprinter, ezconsole


# ///////////////////////////////////////////////////////////////
# INSTALL PLAN FAILURE
# ///////////////////////////////////////////////////////////////


def test_render_install_plan_failure_already_exists_uses_dedicated_title(monkeypatch):
    ezprinter, ezconsole = _patch_ui(monkeypatch)
    plan = InstallPlanResult(
        success=False,
        error="Installation directory already exists",
        message="womm is already installed at C:/womm",
    )

    display_module.render_install_plan_failure(plan)

    ezprinter.create_warning_panel.assert_called_once_with(
        title="Installation Directory Already Exists",
        content="womm is already installed at C:/womm",
    )
    ezconsole.print.assert_any_call("warning-panel")


def test_render_install_plan_failure_other_error_uses_generic_title(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    plan = InstallPlanResult(success=False, error="disk full", message="")

    display_module.render_install_plan_failure(plan)

    ezprinter.create_warning_panel.assert_called_once_with(
        title="Pre-check Failed", content="disk full"
    )


# ///////////////////////////////////////////////////////////////
# INSTALLATION RESULT
# ///////////////////////////////////////////////////////////////


def test_render_installation_result_failure_reports_error(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    result = InstallationResult(success=False, error="permission denied")

    display_module.render_installation_result(result)

    ezprinter.error.assert_called_once_with("Installation failed: permission denied")
    ezprinter.success.assert_not_called()


def test_render_installation_result_success_shows_target_path(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    result = InstallationResult(success=True, target_path="C:/womm")

    display_module.render_installation_result(result)

    ezprinter.system.assert_called_once_with("📁 Installed to: C:/womm")
    ezprinter.create_success_panel.assert_called_once()


# ///////////////////////////////////////////////////////////////
# WINDOWS TIPS
# ///////////////////////////////////////////////////////////////


def test_render_windows_install_tips_emits_two_tips(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)

    display_module.render_windows_install_tips()

    assert ezprinter.tip.call_count == 2


# ///////////////////////////////////////////////////////////////
# UNINSTALL PLAN FAILURE
# ///////////////////////////////////////////////////////////////


def test_render_uninstall_plan_failure_not_found_uses_dedicated_title(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    plan = UninstallPlanResult(
        success=False, error="WOMM installation not found", message="nothing here"
    )

    display_module.render_uninstall_plan_failure(plan)

    ezprinter.create_warning_panel.assert_called_once_with(
        title="WOMM Not Found", content="nothing here"
    )


def test_render_uninstall_plan_failure_other_error_uses_generic_title(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    plan = UninstallPlanResult(success=False, error="locked file", message="")

    display_module.render_uninstall_plan_failure(plan)

    ezprinter.create_warning_panel.assert_called_once_with(
        title="Pre-check Failed", content="locked file"
    )


def test_render_uninstall_cancelled_prints_red_message(monkeypatch):
    _, ezconsole = _patch_ui(monkeypatch)

    display_module.render_uninstall_cancelled()

    ezconsole.print.assert_called_once_with("❌ Uninstallation cancelled", style="red")


# ///////////////////////////////////////////////////////////////
# UNINSTALLATION RESULT
# ///////////////////////////////////////////////////////////////


def test_render_uninstallation_result_failure_reports_error(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    result = UninstallationResult(success=False, error="in use")

    display_module.render_uninstallation_result(result)

    ezprinter.error.assert_called_once_with("Uninstallation failed: in use")
    ezprinter.success.assert_not_called()


def test_render_uninstallation_result_success_shows_removed_path(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    result = UninstallationResult(success=True, removed_path="C:/womm")

    display_module.render_uninstallation_result(result)

    ezprinter.system.assert_called_once_with("📁 Removed from: C:/womm")
    ezprinter.create_success_panel.assert_called_once()
