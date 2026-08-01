#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST SYSTEM PATH DISPLAY - PATH renderer branch coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Tests for the PATH-vertical UI display functions.

No interactive input here, so branches are cheap to verify by asserting on
the ``ezprinter``/``ezconsole``/``ezpl_bridge`` calls each path makes, and
on the rich ``Panel`` objects pushed to the console.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from unittest.mock import MagicMock

# Third-party imports
from rich.panel import Panel

# Local imports
from womm.shared.results import (
    PathBackupContentResult,
    PathBackupListResult,
    PathBackupResult,
    PathOperationResult,
)
from womm.shared.results.system_results import PathBackupInfo
from womm.ui.system import path_display as display_module

# ///////////////////////////////////////////////////////////////
# HELPERS
# ///////////////////////////////////////////////////////////////


def _patch_ui(monkeypatch):
    ezprinter = MagicMock()
    ezconsole = MagicMock()
    ezpl_bridge = MagicMock()
    ezprinter.create_backup_table.return_value = "backup-table"
    monkeypatch.setattr(display_module, "ezprinter", ezprinter)
    # raising=False: the module only imports ezconsole once panels land.
    monkeypatch.setattr(display_module, "ezconsole", ezconsole, raising=False)
    monkeypatch.setattr(display_module, "ezpl_bridge", ezpl_bridge)
    return ezprinter, ezconsole, ezpl_bridge


def _panels(ezconsole) -> list[Panel]:
    """Return every Panel pushed to the patched console, in order."""
    return [
        call.args[0]
        for call in ezconsole.print.call_args_list
        if call.args and isinstance(call.args[0], Panel)
    ]


# ///////////////////////////////////////////////////////////////
# PATH OPERATIONS
# ///////////////////////////////////////////////////////////////


def test_render_path_operation_result_modified(monkeypatch):
    ezprinter, _, _ = _patch_ui(monkeypatch)
    result = PathOperationResult(
        success=True, path_modified=True, message="PATH updated"
    )

    display_module.render_path_operation_result(result)

    ezprinter.success.assert_called_once_with("PATH updated")


def test_render_path_operation_result_not_modified(monkeypatch):
    ezprinter, _, _ = _patch_ui(monkeypatch)
    result = PathOperationResult(
        success=True, path_modified=False, message="already present"
    )

    display_module.render_path_operation_result(result)

    ezprinter.info.assert_called_once_with("already present")


def test_render_path_operation_result_failure(monkeypatch):
    ezprinter, _, _ = _patch_ui(monkeypatch)
    result = PathOperationResult(success=False, error="permission denied")

    display_module.render_path_operation_result(result)

    ezprinter.error.assert_called_once_with("PATH operation failed")
    ezprinter.info.assert_any_call("permission denied")


def test_render_path_operation_result_default_context_shows_no_panel(monkeypatch):
    _, ezconsole, _ = _patch_ui(monkeypatch)
    result = PathOperationResult(
        success=True, path_modified=True, message="PATH updated"
    )

    display_module.render_path_operation_result(result)

    assert _panels(ezconsole) == []


def test_render_path_operation_result_failure_default_context_shows_no_panel(
    monkeypatch,
):
    _, ezconsole, _ = _patch_ui(monkeypatch)
    result = PathOperationResult(success=False, error="permission denied")

    display_module.render_path_operation_result(result)

    assert _panels(ezconsole) == []


def test_render_path_operation_result_restore_success_shows_complete_panel(monkeypatch):
    _, ezconsole, _ = _patch_ui(monkeypatch)
    result = PathOperationResult(
        success=True, path_modified=True, message="PATH restored"
    )

    display_module.render_path_operation_result(result, context="restore")

    panels = _panels(ezconsole)
    assert len(panels) == 1
    assert panels[0].title == "Restore Complete"
    assert panels[0].border_style == "green"
    assert "restart" in panels[0].renderable.lower()
    assert "womm path backup list" in panels[0].renderable


def test_render_path_operation_result_restore_failure_shows_troubleshooting_panel(
    monkeypatch,
):
    _, ezconsole, _ = _patch_ui(monkeypatch)
    result = PathOperationResult(success=False, error="permission denied")

    display_module.render_path_operation_result(result, context="restore")

    panels = _panels(ezconsole)
    assert len(panels) == 1
    assert panels[0].title == "Troubleshooting"
    assert panels[0].border_style == "yellow"
    assert "womm path backup list" in panels[0].renderable


# ///////////////////////////////////////////////////////////////
# BACKUP CREATION
# ///////////////////////////////////////////////////////////////


def test_render_path_backup_result_success(monkeypatch):
    ezprinter, _, _ = _patch_ui(monkeypatch)
    result = PathBackupResult(
        success=True, backup_location="C:/backups", backup_file="C:/backups/a.json"
    )

    display_module.render_path_backup_result(result)

    ezprinter.system.assert_any_call("Backup location: C:/backups")
    ezprinter.system.assert_any_call("Backup file: a.json")


def test_render_path_backup_result_failure(monkeypatch):
    ezprinter, _, _ = _patch_ui(monkeypatch)
    result = PathBackupResult(success=False, error="disk full")

    display_module.render_path_backup_result(result)

    ezprinter.error.assert_called_once_with("PATH backup failed")


def test_render_path_backup_result_success_shows_information_panel(monkeypatch):
    _, ezconsole, _ = _patch_ui(monkeypatch)
    result = PathBackupResult(
        success=True, backup_location="C:/backups", backup_file="C:/backups/a.json"
    )

    display_module.render_path_backup_result(result)

    panels = _panels(ezconsole)
    assert len(panels) == 1
    assert panels[0].title == "Backup Information"
    assert panels[0].border_style == "yellow"
    assert panels[0].width == 80
    assert "a.json" in panels[0].renderable
    assert "womm path backup restore" in panels[0].renderable


def test_render_path_backup_result_failure_shows_troubleshooting_panel(monkeypatch):
    _, ezconsole, _ = _patch_ui(monkeypatch)
    result = PathBackupResult(success=False, error="disk full")

    display_module.render_path_backup_result(result)

    panels = _panels(ezconsole)
    assert len(panels) == 1
    assert panels[0].title == "Troubleshooting"
    assert panels[0].border_style == "yellow"
    assert "womm path backup list" in panels[0].renderable


# ///////////////////////////////////////////////////////////////
# BACKUP LISTING
# ///////////////////////////////////////////////////////////////


def test_render_path_backup_list_result_failure(monkeypatch):
    ezprinter, _, _ = _patch_ui(monkeypatch)
    result = PathBackupListResult(success=False, error="not found")

    display_module.render_path_backup_list_result(result)

    ezprinter.error.assert_called_once_with("Failed to retrieve PATH backups")


def test_render_path_backup_list_result_empty(monkeypatch):
    ezprinter, _, _ = _patch_ui(monkeypatch)
    result = PathBackupListResult(success=True, backups=[])

    display_module.render_path_backup_list_result(result)

    ezprinter.system.assert_any_call("No backup files found")


def test_render_path_backup_list_result_with_backups(monkeypatch):
    ezprinter, _, ezpl_bridge = _patch_ui(monkeypatch)
    result = PathBackupListResult(
        success=True,
        backups=[
            PathBackupInfo(
                name="a.json",
                path="C:/a.json",
                size=100,
                modified="2026-01-01",
                path_entries=3,
            )
        ],
    )

    display_module.render_path_backup_list_result(result)

    ezprinter.create_backup_table.assert_called_once()
    ezpl_bridge.console.print.assert_any_call("backup-table")


def test_render_path_backup_list_result_with_backups_shows_commands_panel(monkeypatch):
    _, ezconsole, _ = _patch_ui(monkeypatch)
    result = PathBackupListResult(
        success=True,
        backups=[
            PathBackupInfo(
                name="a.json",
                path="C:/a.json",
                size=100,
                modified="2026-01-01",
                path_entries=3,
            )
        ],
    )

    display_module.render_path_backup_list_result(result)

    panels = _panels(ezconsole)
    assert len(panels) == 1
    assert panels[0].title == "PATH Commands"
    assert panels[0].border_style == "blue"
    assert "womm path backup create" in panels[0].renderable
    assert "womm path backup restore" in panels[0].renderable
    assert "womm path backup list" in panels[0].renderable


def test_render_path_backup_list_result_empty_shows_getting_started_panel(monkeypatch):
    _, ezconsole, _ = _patch_ui(monkeypatch)
    result = PathBackupListResult(success=True, backups=[])

    display_module.render_path_backup_list_result(result)

    panels = _panels(ezconsole)
    assert len(panels) == 1
    assert panels[0].title == "Getting Started"
    assert panels[0].border_style == "blue"
    assert "womm path backup create" in panels[0].renderable


def test_render_path_backup_list_result_failure_shows_troubleshooting_panel(
    monkeypatch,
):
    _, ezconsole, _ = _patch_ui(monkeypatch)
    result = PathBackupListResult(success=False, error="not found")

    display_module.render_path_backup_list_result(result)

    panels = _panels(ezconsole)
    assert len(panels) == 1
    assert panels[0].title == "Troubleshooting"
    assert panels[0].border_style == "yellow"


# ///////////////////////////////////////////////////////////////
# PATH ENTRIES
# ///////////////////////////////////////////////////////////////


def test_render_path_entries_result_shows_table_and_commands_panel(monkeypatch):
    ezprinter, ezconsole, ezpl_bridge = _patch_ui(monkeypatch)
    # Must stay a MagicMock: the renderer calls .add_row() on it.
    table = MagicMock()
    ezprinter.create_table.return_value = table
    result = PathOperationResult(
        success=True, message="ok", path_entries=["C:/a", "C:/b"]
    )

    display_module.render_path_entries_result(result)

    ezprinter.create_table.assert_called_once()
    assert table.add_row.call_count == 2
    ezpl_bridge.console.print.assert_any_call(table)
    panels = _panels(ezconsole)
    assert len(panels) == 1
    assert panels[0].title == "PATH Commands"
    assert panels[0].border_style == "blue"


def test_render_path_entries_result_empty_path(monkeypatch):
    ezprinter, ezconsole, _ = _patch_ui(monkeypatch)
    result = PathOperationResult(success=True, message="ok", path_entries=[])

    display_module.render_path_entries_result(result)

    ezprinter.create_table.assert_not_called()
    ezprinter.system.assert_any_call("PATH is empty")
    assert len(_panels(ezconsole)) == 1


def test_render_path_entries_result_failure(monkeypatch):
    ezprinter, ezconsole, _ = _patch_ui(monkeypatch)
    result = PathOperationResult(success=False, error="registry unavailable")

    display_module.render_path_entries_result(result)

    ezprinter.error.assert_called_once_with("Failed to read the current PATH")
    panels = _panels(ezconsole)
    assert len(panels) == 1
    assert panels[0].title == "Troubleshooting"
    assert panels[0].border_style == "yellow"


# ///////////////////////////////////////////////////////////////
# BACKUP CONTENT
# ///////////////////////////////////////////////////////////////


def test_render_path_backup_content_result_success(monkeypatch):
    ezprinter, ezconsole, ezpl_bridge = _patch_ui(monkeypatch)
    # Must stay a MagicMock: the renderer calls .add_row() on it.
    table = MagicMock()
    ezprinter.create_table.return_value = table
    result = PathBackupContentResult(
        success=True,
        name=".path_20260801_120000.json",
        backup_file="C:/backups/.path_20260801_120000.json",
        timestamp="20260801_120000",
        platform="Windows",
        separator=";",
        length=9,
        entries=["C:/a", "C:/b"],
    )

    display_module.render_path_backup_content_result(result)

    ezprinter.create_table.assert_called_once()
    assert table.add_row.call_count == 2
    ezpl_bridge.console.print.assert_any_call(table)
    panels = _panels(ezconsole)
    assert len(panels) == 1
    assert panels[0].title == "Backup Content"
    assert panels[0].border_style == "blue"
    assert "womm path backup restore" in panels[0].renderable


def test_render_path_backup_content_result_failure(monkeypatch):
    ezprinter, ezconsole, _ = _patch_ui(monkeypatch)
    result = PathBackupContentResult(
        success=False, message="No readable backup named 'nope.json'"
    )

    display_module.render_path_backup_content_result(result)

    ezprinter.error.assert_called_once_with("No readable backup named 'nope.json'")
    panels = _panels(ezconsole)
    assert len(panels) == 1
    assert panels[0].title == "Troubleshooting"
    assert "womm path backup list" in panels[0].renderable
