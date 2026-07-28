#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST CONTEXT DISPLAY - Renderer branch coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Tests for the context-menu Result renderers.

No interactive input here, so branches are cheap to verify by asserting on
the ``ezprinter``/``ezconsole`` calls each success/failure path makes.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from unittest.mock import MagicMock

# Local imports
from womm.shared.results import (
    ContextBackupResult,
    ContextCherryPickResult,
    ContextEntriesResult,
    ContextRestoreResult,
    ContextSetupResult,
    ContextStatusResult,
    ScriptRegistrationResult,
    ScriptUnregistrationResult,
)
from womm.ui.context import display as display_module

# ///////////////////////////////////////////////////////////////
# FIXTURES
# ///////////////////////////////////////////////////////////////


def _patch_ui(monkeypatch):
    ezprinter = MagicMock()
    ezconsole = MagicMock()
    monkeypatch.setattr(display_module, "ezprinter", ezprinter)
    monkeypatch.setattr(display_module, "ezconsole", ezconsole)
    return ezprinter, ezconsole


# ///////////////////////////////////////////////////////////////
# SCRIPT REGISTRATION
# ///////////////////////////////////////////////////////////////


def test_render_script_registration_result_failure(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    result = ScriptRegistrationResult(success=False, error="registry locked")

    display_module.render_script_registration_result(result)

    ezprinter.error.assert_called_once_with("Registration failed: registry locked")


def test_render_script_registration_result_dry_run(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    result = ScriptRegistrationResult(success=True, dry_run=True, label="My Tool")

    display_module.render_script_registration_result(result)

    ezprinter.info.assert_any_call("Would register: My Tool")
    ezprinter.success.assert_not_called()


def test_render_script_registration_result_success(monkeypatch):
    ezprinter, ezconsole = _patch_ui(monkeypatch)
    result = ScriptRegistrationResult(success=True, dry_run=False, label="My Tool")

    display_module.render_script_registration_result(result)

    ezprinter.success.assert_called_once_with(
        "Tool 'My Tool' registered successfully in context menu"
    )
    ezconsole.print.assert_called()


# ///////////////////////////////////////////////////////////////
# SCRIPT UNREGISTRATION
# ///////////////////////////////////////////////////////////////


def test_render_script_unregistration_result_failure_with_permission_errors(
    monkeypatch,
):
    ezprinter, _ = _patch_ui(monkeypatch)
    result = ScriptUnregistrationResult(
        success=False, error="not found", permission_errors=["denied on HKCU"]
    )

    display_module.render_script_unregistration_result(result)

    ezprinter.error.assert_any_call("Unregistration failed: not found")
    ezprinter.error.assert_any_call("  Permission error: denied on HKCU")


def test_render_script_unregistration_result_success_with_permission_warnings(
    monkeypatch,
):
    ezprinter, ezconsole = _patch_ui(monkeypatch)
    result = ScriptUnregistrationResult(
        success=True, key_name="MyTool", permission_errors=["denied on HKCU"]
    )

    display_module.render_script_unregistration_result(result)

    ezprinter.success.assert_called_once_with(
        "Entry 'MyTool' removed successfully from context menu"
    )
    ezprinter.warning.assert_called_once_with("Permission error: denied on HKCU")
    ezconsole.print.assert_called()


# ///////////////////////////////////////////////////////////////
# BACKUP / RESTORE
# ///////////////////////////////////////////////////////////////


def test_render_context_backup_result_failure(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    result = ContextBackupResult(success=False, error="disk full")

    display_module.render_context_backup_result(result)

    ezprinter.error.assert_called_once_with("Backup failed: disk full")


def test_render_context_backup_result_success(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    result = ContextBackupResult(success=True, backup_file="backup.json", entry_count=5)

    display_module.render_context_backup_result(result)

    ezprinter.info.assert_any_call("Backup saved to: backup.json")
    ezprinter.info.assert_any_call("5 entries backed up")


def test_render_context_restore_result_failure(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    result = ContextRestoreResult(success=False, error="corrupt backup")

    display_module.render_context_restore_result(result)

    ezprinter.error.assert_called_once_with("Restore failed: corrupt backup")


def test_render_context_restore_result_success(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    result = ContextRestoreResult(success=True, backup_file="backup.json")

    display_module.render_context_restore_result(result)

    ezprinter.info.assert_any_call("Restored from: backup.json")


# ///////////////////////////////////////////////////////////////
# ENTRIES
# ///////////////////////////////////////////////////////////////


def test_render_context_entries_result_failure(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    result = ContextEntriesResult(success=False, error="registry unavailable")

    display_module.render_context_entries_result(result)

    ezprinter.error.assert_called_once_with(
        "Failed to retrieve context menu entries: registry unavailable"
    )


def test_render_context_entries_result_success_with_entries(monkeypatch):
    ezprinter, ezconsole = _patch_ui(monkeypatch)
    result = ContextEntriesResult(
        success=True,
        entries={
            "directory": [
                {
                    "key_name": "womm_tool",
                    "display_name": "WOMM Tool",
                    "command": "womm run",
                    "icon": "icon.ico",
                }
            ],
            "background": [],
        },
    )

    display_module.render_context_entries_result(result)

    ezprinter.print_header.assert_called_once_with("Context Menu Entries")
    ezconsole.print.assert_any_call("  Key: womm_tool")


def test_render_context_entries_result_success_no_entries(monkeypatch):
    ezprinter, ezconsole = _patch_ui(monkeypatch)
    result = ContextEntriesResult(success=True, entries={})

    display_module.render_context_entries_result(result)

    ezconsole.print.assert_any_call("  No entries found")


# ///////////////////////////////////////////////////////////////
# STATUS
# ///////////////////////////////////////////////////////////////


def test_render_context_status_result_success(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    result = ContextStatusResult(success=True, total_entries=7)

    display_module.render_context_status_result(result)

    ezprinter.success.assert_called_once_with("Found 7 context menu entries")


def test_render_context_status_result_failure_with_error(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    result = ContextStatusResult(success=False, error="access denied")

    display_module.render_context_status_result(result)

    ezprinter.error.assert_called_once_with("Failed to retrieve context menu status")
    ezprinter.info.assert_any_call("Error: access denied")


# ///////////////////////////////////////////////////////////////
# SETUP
# ///////////////////////////////////////////////////////////////


def test_render_context_setup_result_success(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    result = ContextSetupResult(success=True, total_tools=3)

    display_module.render_context_setup_result(result)

    ezprinter.success.assert_called_once_with(
        "All 3 WOMM tools registered successfully!"
    )


def test_render_context_setup_result_partial_failure(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    result = ContextSetupResult(
        success=False, success_count=1, total_tools=3, error="one tool failed"
    )

    display_module.render_context_setup_result(result)

    ezprinter.info.assert_any_call("Registered 1/3 tools successfully")
    ezprinter.error.assert_called_once_with("Setup error: one tool failed")


# ///////////////////////////////////////////////////////////////
# CHERRY-PICK
# ///////////////////////////////////////////////////////////////


def test_render_context_cherry_pick_result_success(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    result = ContextCherryPickResult(success=True, success_count=2)

    display_module.render_context_cherry_pick_result(result)

    ezprinter.success.assert_called_once_with(
        "Cherry-pick completed! 2 entries installed"
    )


def test_render_context_cherry_pick_result_failure(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    result = ContextCherryPickResult(success=False, error="entry not found")

    display_module.render_context_cherry_pick_result(result)

    ezprinter.error.assert_called_once_with("Cherry-pick failed: entry not found")


# ///////////////////////////////////////////////////////////////
# HELPERS
# ///////////////////////////////////////////////////////////////


def test_show_list_commands_prints_panel(monkeypatch):
    _, ezconsole = _patch_ui(monkeypatch)

    display_module.show_list_commands()

    ezconsole.print.assert_called()


def test_show_tip_panel_uses_given_title(monkeypatch):
    _, ezconsole = _patch_ui(monkeypatch)

    display_module.show_tip_panel("some content", title="Custom Title")

    ezconsole.print.assert_called()
