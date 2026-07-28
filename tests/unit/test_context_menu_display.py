#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST CONTEXT MENU DISPLAY - Backup selection UI logic
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Tests for ``ContextMenuUI``.

Real backup discovery/parsing/sorting logic runs against real JSON files
under ``tmp_path``; only the interactive prompts (``prompt_choice``,
``confirm``) and the terminal (``ezprinter``/``ezconsole``) are patched.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
import os
import time
from unittest.mock import MagicMock

# Local imports
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


def _write_backup(path, entries=2, timestamp="2026-01-01T10:00:00"):
    path.write_text(
        json.dumps(
            {
                "timestamp": timestamp,
                "entries": [{"key_name": f"entry{i}"} for i in range(entries)],
            }
        ),
        encoding="utf-8",
    )


# ///////////////////////////////////////////////////////////////
# SHOW BACKUP SELECTION MENU
# ///////////////////////////////////////////////////////////////


def test_show_backup_selection_menu_no_backups_found(tmp_path, monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)

    result = menu_display_module.ContextMenuUI.show_backup_selection_menu(tmp_path)

    assert result is None
    ezprinter.error.assert_called_once_with("No context menu backups found")


def test_show_backup_selection_menu_returns_selected_file(tmp_path, monkeypatch):
    _patch_ui(monkeypatch)
    backup = tmp_path / "context_menu_backup_1.json"
    _write_backup(backup)

    monkeypatch.setattr(
        menu_display_module,
        "prompt_choice",
        lambda _message, choices: choices[0],
    )

    result = menu_display_module.ContextMenuUI.show_backup_selection_menu(tmp_path)

    assert result == backup


def test_show_backup_selection_menu_cancelled_returns_none(tmp_path, monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    _write_backup(tmp_path / "context_menu_backup_1.json")

    def _raise_keyboard_interrupt(*_args, **_kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr(menu_display_module, "prompt_choice", _raise_keyboard_interrupt)

    result = menu_display_module.ContextMenuUI.show_backup_selection_menu(tmp_path)

    assert result is None
    ezprinter.info.assert_any_call("📤 Restore cancelled")


def test_show_backup_selection_menu_skips_unreadable_backup(tmp_path, monkeypatch):
    _patch_ui(monkeypatch)
    good = tmp_path / "context_menu_backup_good.json"
    _write_backup(good)
    bad = tmp_path / "context_menu_backup_bad.json"
    bad.write_text("not json", encoding="utf-8")

    monkeypatch.setattr(
        menu_display_module,
        "prompt_choice",
        lambda _message, choices: choices[0],
    )

    result = menu_display_module.ContextMenuUI.show_backup_selection_menu(tmp_path)

    assert result in {good, bad}


def test_show_backup_selection_menu_sorts_newest_first(tmp_path, monkeypatch):
    _patch_ui(monkeypatch)
    older = tmp_path / "context_menu_backup_older.json"
    newer = tmp_path / "context_menu_backup_newer.json"
    _write_backup(older)
    _write_backup(newer)

    now = time.time()
    os.utime(older, (now - 100, now - 100))
    os.utime(newer, (now, now))

    captured_choices = {}

    def _capture_and_select(_message, choices):
        captured_choices["choices"] = choices
        return choices[0]

    monkeypatch.setattr(menu_display_module, "prompt_choice", _capture_and_select)

    result = menu_display_module.ContextMenuUI.show_backup_selection_menu(tmp_path)

    assert result == newer
    assert captured_choices["choices"][0].startswith("context_menu_backup_newer")


# ///////////////////////////////////////////////////////////////
# CONFIRM RESTORE OPERATION
# ///////////////////////////////////////////////////////////////


def test_confirm_restore_operation_shows_details_and_asks(tmp_path, monkeypatch):
    _, ezconsole = _patch_ui(monkeypatch)
    backup = tmp_path / "backup.json"
    _write_backup(backup, entries=3)

    monkeypatch.setattr(menu_display_module, "confirm", lambda *_a, **_k: True)

    result = menu_display_module.ContextMenuUI.confirm_restore_operation(backup)

    assert result is True
    ezconsole.print.assert_called()


def test_confirm_restore_operation_handles_invalid_timestamp(tmp_path, monkeypatch):
    _patch_ui(monkeypatch)
    backup = tmp_path / "backup.json"
    _write_backup(backup, timestamp="not-a-timestamp")

    monkeypatch.setattr(menu_display_module, "confirm", lambda *_a, **_k: False)

    result = menu_display_module.ContextMenuUI.confirm_restore_operation(backup)

    assert result is False


def test_confirm_restore_operation_handles_unreadable_file(tmp_path, monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    backup = tmp_path / "backup.json"
    backup.write_text("not json", encoding="utf-8")

    monkeypatch.setattr(menu_display_module, "confirm", lambda *_a, **_k: True)

    result = menu_display_module.ContextMenuUI.confirm_restore_operation(backup)

    assert result is True
    assert ezprinter.debug.called


# ///////////////////////////////////////////////////////////////
# SHOW CHERRY PICK MENU
# ///////////////////////////////////////////////////////////////


def test_show_cherry_pick_menu_returns_selected_entries(monkeypatch):
    _patch_ui(monkeypatch)
    entries = [{"key_name": "a"}, {"key_name": "b"}]

    fake_menu = MagicMock()
    fake_menu.select_multiple_from_list.return_value = [entries[0]]
    monkeypatch.setattr("womm.ui.common.InteractiveMenu", lambda **_kwargs: fake_menu)

    result = menu_display_module.ContextMenuUI.show_cherry_pick_menu(entries)

    assert result == [entries[0]]


def test_show_cherry_pick_menu_empty_selection_returns_empty_list(monkeypatch):
    _patch_ui(monkeypatch)

    fake_menu = MagicMock()
    fake_menu.select_multiple_from_list.return_value = None
    monkeypatch.setattr("womm.ui.common.InteractiveMenu", lambda **_kwargs: fake_menu)

    result = menu_display_module.ContextMenuUI.show_cherry_pick_menu([])

    assert result == []
