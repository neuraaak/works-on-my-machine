#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST PROJECT CONFLICT PROMPTS - Interactive resolver coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Tests for the interactive half of conflict resolution."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path

# Third-party imports
import pytest

# Local imports
from womm.shared.conflicts import ConflictAction
from womm.ui.project.create import conflict_prompts
from womm.ui.project.create.conflict_prompts import InteractiveConflictResolver

# ///////////////////////////////////////////////////////////////
# HELPERS
# ///////////////////////////////////////////////////////////////


def _answer_confirms(monkeypatch: pytest.MonkeyPatch, *answers: bool) -> list[str]:
    """Feed successive answers to `confirm` and record the questions asked."""
    asked: list[str] = []
    remaining = list(answers)

    def fake_confirm(prompt_text: str, **_kwargs: object) -> bool:
        asked.append(prompt_text)
        return remaining.pop(0)

    monkeypatch.setattr(conflict_prompts, "confirm", fake_confirm)
    return asked


def _answer_choices(monkeypatch: pytest.MonkeyPatch, *choices: str) -> None:
    """Feed successive answers to the directory menu."""
    remaining = list(choices)
    monkeypatch.setattr(
        conflict_prompts.Prompt,
        "ask",
        staticmethod(lambda *_args, **_kwargs: remaining.pop(0)),
    )


# ///////////////////////////////////////////////////////////////
# FILE RESOLUTION
# ///////////////////////////////////////////////////////////////


def test_resolve_file_overwrites_when_confirmed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _answer_confirms(monkeypatch, True)

    action = InteractiveConflictResolver().resolve_file(tmp_path / "a.txt", "file")

    assert action == ConflictAction.OVERWRITE


def test_resolve_file_skips_when_overwrite_declined(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _answer_confirms(monkeypatch, False, True)

    action = InteractiveConflictResolver().resolve_file(tmp_path / "a.txt", "file")

    assert action == ConflictAction.SKIP


def test_resolve_file_cancels_when_skip_declined(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _answer_confirms(monkeypatch, False, False)

    action = InteractiveConflictResolver().resolve_file(tmp_path / "a.txt", "file")

    assert action == ConflictAction.CANCEL


def test_resolve_file_cancels_on_keyboard_interrupt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def interrupt(*_args: object, **_kwargs: object) -> bool:
        raise KeyboardInterrupt

    monkeypatch.setattr(conflict_prompts, "confirm", interrupt)

    action = InteractiveConflictResolver().resolve_file(tmp_path / "a.txt", "file")

    assert action == ConflictAction.CANCEL


def test_resolve_file_skips_when_prompting_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def boom(*_args: object, **_kwargs: object) -> bool:
        raise RuntimeError("no tty")

    monkeypatch.setattr(conflict_prompts, "confirm", boom)

    action = InteractiveConflictResolver().resolve_file(tmp_path / "a.txt", "file")

    assert action == ConflictAction.SKIP


# ///////////////////////////////////////////////////////////////
# DIRECTORY RESOLUTION
# ///////////////////////////////////////////////////////////////


@pytest.mark.parametrize(
    ("choice", "expected"),
    [
        ("1", ConflictAction.MERGE),
        ("3", ConflictAction.SKIP),
        ("4", ConflictAction.CANCEL),
    ],
)
def test_resolve_directory_maps_menu_choices(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    choice: str,
    expected: ConflictAction,
) -> None:
    _answer_choices(monkeypatch, choice)

    action = InteractiveConflictResolver().resolve_directory(tmp_path / "d", "dir")

    assert action == expected


def test_resolve_directory_overwrites_only_after_a_second_confirmation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _answer_choices(monkeypatch, "2")
    _answer_confirms(monkeypatch, True)

    action = InteractiveConflictResolver().resolve_directory(tmp_path / "d", "dir")

    assert action == ConflictAction.OVERWRITE


def test_resolve_directory_re_asks_when_overwrite_is_declined(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _answer_choices(monkeypatch, "2", "1")
    _answer_confirms(monkeypatch, False)

    action = InteractiveConflictResolver().resolve_directory(tmp_path / "d", "dir")

    assert action == ConflictAction.MERGE


def test_resolve_directory_merges_when_prompting_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def boom(*_args: object, **_kwargs: object) -> str:
        raise RuntimeError("no tty")

    monkeypatch.setattr(conflict_prompts.Prompt, "ask", staticmethod(boom))

    action = InteractiveConflictResolver().resolve_directory(tmp_path / "d", "dir")

    assert action == ConflictAction.MERGE
