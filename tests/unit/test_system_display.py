#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST SYSTEM DISPLAY - Renderer branch coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Tests for the system-vertical UI display functions.

No interactive input here, so branches are cheap to verify by asserting on
the ``ezprinter``/``ezconsole``/``ezpl_bridge`` calls each path makes. The
one real validation (``display_system_detection_results`` raises on a
non-dict payload) is asserted directly.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from unittest.mock import MagicMock

# Third-party imports
import pytest

# Local imports
from womm.shared.results import (
    DependencyCheckResult,
    DependencyInventoryResult,
    DependencyStatusResult,
    DoctorResult,
    EnvironmentRefreshResult,
    SystemDetectionResult,
)
from womm.shared.results.dependency_results import (
    DependencyInventoryEntry,
    DependencyManagerStatus,
    DependencyProbe,
)
from womm.ui.system import display as display_module

# ///////////////////////////////////////////////////////////////
# FIXTURES
# ///////////////////////////////////////////////////////////////


def _patch_ui(monkeypatch):
    ezprinter = MagicMock()
    ezconsole = MagicMock()
    ezpl_bridge = MagicMock()
    ezprinter.create_panel.return_value = "panel"
    monkeypatch.setattr(display_module, "ezprinter", ezprinter)
    monkeypatch.setattr(display_module, "ezconsole", ezconsole)
    monkeypatch.setattr(display_module, "ezpl_bridge", ezpl_bridge)
    return ezprinter, ezconsole, ezpl_bridge


# ///////////////////////////////////////////////////////////////
# MANAGERS LIST / AVAILABLE / BEST
# ///////////////////////////////////////////////////////////////


def test_display_system_managers_list_skips_unsupported_platform(monkeypatch):
    _, ezconsole, _ = _patch_ui(monkeypatch)
    status = {
        "winget": {
            "supported_on_current_platform": True,
            "available": True,
            "version": "1.0",
            "platform": "windows",
        },
        "brew": {
            "supported_on_current_platform": False,
            "available": False,
            "version": None,
            "platform": "macos",
        },
    }

    display_module.display_system_managers_list(status)

    ezconsole.print.assert_called_once()


def test_display_system_managers_list_verbose_adds_priority_column(monkeypatch):
    _, ezconsole, _ = _patch_ui(monkeypatch)
    status = {
        "winget": {
            "supported_on_current_platform": True,
            "available": True,
            "version": "1.0",
            "platform": "windows",
            "priority": 1,
        }
    }

    display_module.display_system_managers_list(status, verbose=True)

    ezconsole.print.assert_called_once()


def test_display_available_managers_none_available_warns(monkeypatch):
    ezprinter, _, _ = _patch_ui(monkeypatch)

    display_module.display_available_managers({"winget": MagicMock(success=False)})

    ezprinter.warning.assert_called_once_with("No system package managers detected")


def test_display_available_managers_lists_available(monkeypatch):
    ezprinter, _, _ = _patch_ui(monkeypatch)
    result = MagicMock(success=True, version="1.0", priority=1)

    display_module.display_available_managers({"winget": result}, verbose=True)

    ezprinter.tip.assert_called_once_with("Available managers: winget")
    ezprinter.info.assert_any_call("\nDetails:")


def test_display_best_manager_none_available(monkeypatch):
    ezprinter, _, _ = _patch_ui(monkeypatch)

    display_module.display_best_manager(None)

    ezprinter.error.assert_called_once_with("No system package manager available")


def test_display_best_manager_none_available_verbose_shows_platform_tips(
    monkeypatch,
):
    ezprinter, _, _ = _patch_ui(monkeypatch)

    display_module.display_best_manager(None, verbose=True)

    assert ezprinter.info.called


def test_display_best_manager_available(monkeypatch):
    ezprinter, _, _ = _patch_ui(monkeypatch)

    display_module.display_best_manager("winget", version="1.0")

    ezprinter.tip.assert_called_once_with("✨ Best manager: winget (version 1.0)")


def test_display_best_manager_available_verbose_shows_selection_criteria(
    monkeypatch,
):
    ezprinter, _, _ = _patch_ui(monkeypatch)

    display_module.display_best_manager(
        "winget", version="1.0", platform="windows", priority=1, verbose=True
    )

    ezprinter.info.assert_any_call("Platform: windows")
    ezprinter.info.assert_any_call("Priority: 1")


# ///////////////////////////////////////////////////////////////
# SYSTEM DETECTION RESULTS
# ///////////////////////////////////////////////////////////////


def test_display_system_detection_results_rejects_non_dict():
    with pytest.raises(TypeError, match="Invalid data format"):
        display_module.display_system_detection_results("not a dict")


def test_display_system_detection_results_builds_panel(monkeypatch):
    ezprinter, _, ezpl_bridge = _patch_ui(monkeypatch)
    data = {
        "system_info": {"platform": "Windows", "python_version": "3.13"},
        "package_managers": {"winget": {"available": True, "version": "1.0"}},
        "dev_environments": {"vscode": {"available": True, "name": "VSCode"}},
        "recommendations": {"editor": "Use VSCode"},
    }

    display_module.display_system_detection_results(data)

    ezprinter.create_panel.assert_called_once()
    ezpl_bridge.console.print.assert_called_once_with("panel")


def test_render_system_detection_result_success(monkeypatch):
    _, _, ezpl_bridge = _patch_ui(monkeypatch)
    result = SystemDetectionResult(success=True, system_data={})

    display_module.render_system_detection_result(result)

    ezpl_bridge.console.print.assert_called_once()


def test_render_system_detection_result_failure(monkeypatch):
    ezprinter, _, _ = _patch_ui(monkeypatch)
    result = SystemDetectionResult(success=False, message="detection failed")

    display_module.render_system_detection_result(result)

    ezprinter.error.assert_called_once_with("detection failed")


# ///////////////////////////////////////////////////////////////
# DOCTOR
# ///////////////////////////////////////////////////////////////


def test_render_doctor_result_reports_all_fields(monkeypatch):
    ezprinter, ezconsole, _ = _patch_ui(monkeypatch)
    result = DoctorResult(
        success=True,
        channel="package",
        version="1.0.0",
        executable="/usr/bin/womm",
        data_dir="/home/user/.womm",
        data_dir_writable=True,
        path_command="/usr/bin/womm",
        context_menu_status="0 entries",
    )

    display_module.render_doctor_result(result, verbose=True)

    ezprinter.system.assert_any_call("Runtime channel: package")
    ezprinter.success.assert_any_call("Data directory: /home/user/.womm (writable)")
    ezprinter.info.assert_any_call("Executable: /usr/bin/womm")
    ezconsole.print.assert_called()


def test_render_doctor_result_warns_when_data_dir_not_writable(monkeypatch):
    ezprinter, _, _ = _patch_ui(monkeypatch)
    result = DoctorResult(
        success=True,
        data_dir="/root/.womm",
        data_dir_writable=False,
    )

    display_module.render_doctor_result(result)

    ezprinter.warning.assert_any_call("Data directory: /root/.womm (not writable)")


def test_render_doctor_result_failure(monkeypatch):
    ezprinter, _, _ = _patch_ui(monkeypatch)
    result = DoctorResult(success=False, message="boom", error="detail")

    display_module.render_doctor_result(result)

    ezprinter.error.assert_called_once_with("boom")
    ezprinter.info.assert_any_call("detail")


# ///////////////////////////////////////////////////////////////
# ENVIRONMENT REFRESH
# ///////////////////////////////////////////////////////////////


def test_render_environment_refresh_result_success_and_accessible(monkeypatch):
    ezprinter, _, _ = _patch_ui(monkeypatch)
    result = EnvironmentRefreshResult(success=True)

    display_module.render_environment_refresh_result(result, accessible=True)

    ezprinter.tip.assert_called_once()


def test_render_environment_refresh_result_success_but_inaccessible(monkeypatch):
    ezprinter, _, _ = _patch_ui(monkeypatch)
    result = EnvironmentRefreshResult(success=True)

    display_module.render_environment_refresh_result(result, accessible=False)

    ezprinter.warning.assert_called_once()
    ezprinter.tip.assert_called_once()


def test_render_environment_refresh_result_failure(monkeypatch):
    ezprinter, _, _ = _patch_ui(monkeypatch)
    result = EnvironmentRefreshResult(success=False, error="registry error")

    display_module.render_environment_refresh_result(result, accessible=False)

    ezprinter.error.assert_called_once_with("Environment refresh failed")
    ezprinter.info.assert_any_call("registry error")


# ///////////////////////////////////////////////////////////////
# DEPENDENCY CHECK / STATUS / INVENTORY
# ///////////////////////////////////////////////////////////////


def test_render_deps_check_result_reports_all_strata(monkeypatch):
    ezprinter, ezconsole, _ = _patch_ui(monkeypatch)
    result = DependencyCheckResult(
        success=True,
        system=[DependencyProbe(name="winget", available=True, version="1.0")],
        runtime=[DependencyProbe(name="python", available=False)],
        tools=[DependencyProbe(name="ruff", available=True)],
    )

    display_module.render_deps_check_result(result, verbose=True)

    ezprinter.success.assert_any_call("Available: winget")
    ezprinter.warning.assert_any_call("✗ python: N/A")
    ezprinter.success.assert_any_call("  ✓ ruff")
    ezconsole.print.assert_any_call("")


def test_render_deps_check_result_no_system_managers(monkeypatch):
    ezprinter, _, _ = _patch_ui(monkeypatch)
    result = DependencyCheckResult(success=True, system=[], runtime=[], tools=[])

    display_module.render_deps_check_result(result)

    ezprinter.warning.assert_any_call("No system package managers available")


def test_render_deps_check_result_failure_shows_troubleshooting(monkeypatch):
    ezprinter, ezconsole, _ = _patch_ui(monkeypatch)
    result = DependencyCheckResult(success=False, message="boom", error="detail")

    display_module.render_deps_check_result(result)

    ezprinter.error.assert_called_once_with("boom")
    ezprinter.info.assert_any_call("detail")
    ezconsole.print.assert_called()


def test_render_deps_status_result_verbose(monkeypatch):
    _, ezconsole, _ = _patch_ui(monkeypatch)
    result = DependencyStatusResult(
        success=True,
        system=[
            DependencyManagerStatus(
                name="winget",
                supported_on_current_platform=True,
                available=True,
                version="1.0",
                priority="1",
            )
        ],
        runtime=[DependencyProbe(name="python", available=True, version="3.13")],
        tools=[DependencyProbe(name="ruff", available=False)],
    )

    display_module.render_deps_status_result(result, verbose=True)

    ezconsole.print.assert_called()


def test_render_deps_status_result_failure_shows_troubleshooting(monkeypatch):
    ezprinter, ezconsole, _ = _patch_ui(monkeypatch)
    result = DependencyStatusResult(success=False, message="boom", error="detail")

    display_module.render_deps_status_result(result)

    ezprinter.error.assert_called_once_with("boom")
    ezprinter.info.assert_any_call("detail")
    ezconsole.print.assert_called()


def test_render_deps_inventory_result_lists_all_strata(monkeypatch):
    ezprinter, _, _ = _patch_ui(monkeypatch)
    result = DependencyInventoryResult(
        success=True,
        system=[DependencyInventoryEntry(name="winget", detail="Windows")],
        runtime=[DependencyInventoryEntry(name="python", detail="3.13")],
        tools=[DependencyInventoryEntry(name="ruff", detail="linter")],
    )

    display_module.render_deps_inventory_result(result)

    ezprinter.info.assert_any_call("  • winget (Windows)")


def test_render_deps_inventory_result_failure_shows_troubleshooting(monkeypatch):
    ezprinter, ezconsole, _ = _patch_ui(monkeypatch)
    result = DependencyInventoryResult(success=False, message="boom", error="detail")

    display_module.render_deps_inventory_result(result)

    ezprinter.error.assert_called_once_with("boom")
    ezprinter.info.assert_any_call("detail")
    ezconsole.print.assert_called()
