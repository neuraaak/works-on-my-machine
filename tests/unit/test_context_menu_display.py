#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST CONTEXT MENU DISPLAY - Backup selection UI
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Tests for ``ContextMenuUI``.

This module is pure presentation: it receives resolved ``BackupFileInfo``
records and never touches the filesystem. The tests build those records in
memory and patch only the interactive prompts and the terminal.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from datetime import datetime
from unittest.mock import MagicMock

# Local imports
from womm.shared.results import BackupFileInfo
from womm.ui.context import menu_display as menu_display_module

# ///////////////////////////////////////////////////////////////
# FIXTURES
# ///////////////////////////////////////////////////////////////


def _patch_ui(monkeypatch):
    ezprinter = MagicMock()
    ezconsole = MagicMock()
    monkeypatch.setattr(menu_display_module, "ezprinter", ezprinter)
    monkeypatch.setattr(menu_display_module, "ezconsole", ezconsole)
    return ezprinter, ezconsole


def _backup(name="context_menu_backup_1.json", entries=2):
    return BackupFileInfo(
        filename=name,
        filepath=f"/backups/{name}",
        size_bytes=2048,
        modified_time=datetime(2026, 1, 1, 10, 0, 0),
        entry_count=entries,
        backup_timestamp="2026-01-01T10:00:00",
    )


# ///////////////////////////////////////////////////////////////
# SHOW BACKUP SELECTION MENU
# ///////////////////////////////////////////////////////////////


def test_selection_menu_reports_an_empty_list(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)

    result = menu_display_module.ContextMenuUI.show_backup_selection_menu([])

    assert result is None
    ezprinter.error.assert_called_once_with("No context menu backups found")


def test_selection_menu_returns_the_chosen_backup(monkeypatch):
    _patch_ui(monkeypatch)
    first, second = _backup("a.json"), _backup("b.json")
    captured = {}

    def fake_prompt_choice(_question, choices):
        captured["choices"] = choices
        return choices[1]

    monkeypatch.setattr(menu_display_module, "prompt_choice", fake_prompt_choice)

    result = menu_display_module.ContextMenuUI.show_backup_selection_menu(
        [first, second]
    )

    assert result is second
    assert len(captured["choices"]) == 2
    assert "a.json" in captured["choices"][0]
    assert "2 entries" in captured["choices"][0]


def test_selection_menu_returns_none_when_cancelled(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)

    def fake_prompt_choice(_question, _choices):
        raise KeyboardInterrupt

    monkeypatch.setattr(menu_display_module, "prompt_choice", fake_prompt_choice)

    result = menu_display_module.ContextMenuUI.show_backup_selection_menu([_backup()])

    assert result is None
    ezprinter.info.assert_called_with("Restore cancelled")


def test_selection_menu_handles_an_unknown_modified_time(monkeypatch):
    _patch_ui(monkeypatch)
    backup = _backup()
    backup.modified_time = None
    captured = {}

    def fake_prompt_choice(_question, choices):
        captured["choices"] = choices
        return choices[0]

    monkeypatch.setattr(menu_display_module, "prompt_choice", fake_prompt_choice)

    result = menu_display_module.ContextMenuUI.show_backup_selection_menu([backup])

    assert result is backup
    assert "unknown" in captured["choices"][0]


# ///////////////////////////////////////////////////////////////
# CONFIRM RESTORE OPERATION
# ///////////////////////////////////////////////////////////////


def test_confirm_restore_shows_details_and_returns_the_answer(monkeypatch):
    _patch_ui(monkeypatch)
    monkeypatch.setattr(menu_display_module, "confirm", lambda _question, **_k: True)

    assert (
        menu_display_module.ContextMenuUI.confirm_restore_operation(_backup()) is True
    )


def test_confirm_restore_propagates_a_refusal(monkeypatch):
    _patch_ui(monkeypatch)
    monkeypatch.setattr(menu_display_module, "confirm", lambda _question, **_k: False)

    assert (
        menu_display_module.ContextMenuUI.confirm_restore_operation(_backup()) is False
    )


# ///////////////////////////////////////////////////////////////
# FORMAT ENTRY DISPLAY
# ///////////////////////////////////////////////////////////////


def test_format_entry_display_uses_muiverb_and_exe():
    entry = {
        "key_name": "womm_tool",
        "properties": {
            "MUIVerb": "Open with WOMM",
            "Command": '"C:\\bin\\womm.exe" %1',
        },
    }

    label = menu_display_module.format_entry_display(entry)

    assert label == "Open with WOMM (womm.exe) [key: womm_tool]"


def test_format_entry_display_falls_back_to_the_key_name():
    assert (
        menu_display_module.format_entry_display({"key_name": "bare"})
        == "bare [key: bare]"
    )
