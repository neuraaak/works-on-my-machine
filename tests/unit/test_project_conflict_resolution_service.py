#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST PROJECT CONFLICT RESOLUTION SERVICE - Direct service coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Direct tests for file/directory conflict resolution during project creation."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path

# Third-party imports
import pytest

# Local imports
from womm.exceptions.project import ProjectServiceError
from womm.services.project.conflict_resolution_service import (
    ConflictAction,
    ConflictResolutionService,
)

# ///////////////////////////////////////////////////////////////
# FILE CONFLICT RESOLUTION
# ///////////////////////////////////////////////////////////////


def test_resolve_file_conflict_overwrites_when_target_is_missing(
    tmp_path: Path,
) -> None:
    action = ConflictResolutionService().resolve_file_conflict(
        tmp_path / "source.txt", tmp_path / "missing.txt"
    )

    assert action == ConflictAction.OVERWRITE


def test_resolve_file_conflict_overwrites_when_forced(tmp_path: Path) -> None:
    target = tmp_path / "existing.txt"
    target.touch()

    action = ConflictResolutionService().resolve_file_conflict(
        tmp_path / "source.txt", target, force=True
    )

    assert action == ConflictAction.OVERWRITE


def test_resolve_file_conflict_prompts_when_target_exists_and_not_forced(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "existing.txt"
    target.touch()
    service = ConflictResolutionService()
    monkeypatch.setattr(
        service, "_prompt_file_resolution", lambda *_args: ConflictAction.SKIP
    )

    action = service.resolve_file_conflict(tmp_path / "source.txt", target)

    assert action == ConflictAction.SKIP


# ///////////////////////////////////////////////////////////////
# DIRECTORY CONFLICT RESOLUTION
# ///////////////////////////////////////////////////////////////


def test_resolve_directory_conflict_overwrites_when_target_is_missing(
    tmp_path: Path,
) -> None:
    action = ConflictResolutionService().resolve_directory_conflict(
        tmp_path / "source", tmp_path / "missing"
    )

    assert action == ConflictAction.OVERWRITE


def test_resolve_directory_conflict_merges_when_forced(tmp_path: Path) -> None:
    target = tmp_path / "existing"
    target.mkdir()

    action = ConflictResolutionService().resolve_directory_conflict(
        tmp_path / "source", target, force=True
    )

    assert action == ConflictAction.MERGE


def test_resolve_directory_conflict_prompts_when_target_exists_and_not_forced(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "existing"
    target.mkdir()
    service = ConflictResolutionService()
    monkeypatch.setattr(
        service,
        "_prompt_directory_resolution",
        lambda *_args: ConflictAction.CANCEL,
    )

    action = service.resolve_directory_conflict(tmp_path / "source", target)

    assert action == ConflictAction.CANCEL


# ///////////////////////////////////////////////////////////////
# FILE COPY WITH RESOLUTION
# ///////////////////////////////////////////////////////////////


def test_copy_file_with_resolution_copies_when_no_conflict(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("content")
    target = tmp_path / "out" / "target.txt"

    copied = ConflictResolutionService().copy_file_with_resolution(source, target)

    assert copied is True
    assert target.read_text() == "content"


def test_copy_file_with_resolution_overwrites_when_forced(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("new")
    target = tmp_path / "target.txt"
    target.write_text("old")

    copied = ConflictResolutionService().copy_file_with_resolution(
        source, target, force=True
    )

    assert copied is True
    assert target.read_text() == "new"


def test_copy_file_with_resolution_skips_and_leaves_target_untouched(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source.txt"
    source.write_text("new")
    target = tmp_path / "target.txt"
    target.write_text("old")
    service = ConflictResolutionService()
    monkeypatch.setattr(
        service, "_prompt_file_resolution", lambda *_args: ConflictAction.SKIP
    )

    copied = service.copy_file_with_resolution(source, target)

    assert copied is False
    assert target.read_text() == "old"


def test_copy_file_with_resolution_returns_false_when_cancelled(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source.txt"
    source.write_text("new")
    target = tmp_path / "target.txt"
    target.write_text("old")
    service = ConflictResolutionService()
    monkeypatch.setattr(
        service, "_prompt_file_resolution", lambda *_args: ConflictAction.CANCEL
    )

    copied = service.copy_file_with_resolution(source, target)

    assert copied is False


def test_copy_file_with_resolution_wraps_unexpected_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = ConflictResolutionService()
    monkeypatch.setattr(
        service,
        "resolve_file_conflict",
        lambda *_args, **_kwargs: ConflictAction.OVERWRITE,
    )

    with pytest.raises(ProjectServiceError, match="copy_file_with_resolution"):
        service.copy_file_with_resolution(
            tmp_path / "missing-source.txt", tmp_path / "target.txt"
        )


# ///////////////////////////////////////////////////////////////
# DIRECTORY COPY WITH RESOLUTION
# ///////////////////////////////////////////////////////////////


def test_copy_directory_with_resolution_copies_when_no_conflict(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "file.txt").write_text("content")
    target = tmp_path / "target"

    copied = ConflictResolutionService().copy_directory_with_resolution(source, target)

    assert copied is True
    assert (target / "file.txt").read_text() == "content"


def test_copy_directory_with_resolution_overwrite_replaces_existing_contents(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "new.txt").write_text("new")
    target = tmp_path / "target"
    target.mkdir()
    (target / "stale.txt").write_text("stale")
    service = ConflictResolutionService()
    monkeypatch.setattr(
        service,
        "_prompt_directory_resolution",
        lambda *_args: ConflictAction.OVERWRITE,
    )

    copied = service.copy_directory_with_resolution(source, target)

    assert copied is True
    assert (target / "new.txt").read_text() == "new"
    assert not (target / "stale.txt").exists()


def test_copy_directory_with_resolution_merge_keeps_existing_files(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "new.txt").write_text("new")
    target = tmp_path / "target"
    target.mkdir()
    (target / "kept.txt").write_text("kept")

    copied = ConflictResolutionService().copy_directory_with_resolution(
        source, target, force=True
    )

    assert copied is True
    assert (target / "new.txt").read_text() == "new"
    assert (target / "kept.txt").read_text() == "kept"


def test_copy_directory_with_resolution_skips_and_leaves_target_untouched(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "new.txt").write_text("new")
    target = tmp_path / "target"
    target.mkdir()
    service = ConflictResolutionService()
    monkeypatch.setattr(
        service,
        "_prompt_directory_resolution",
        lambda *_args: ConflictAction.SKIP,
    )

    copied = service.copy_directory_with_resolution(source, target)

    assert copied is False
    assert not (target / "new.txt").exists()


def test_copy_directory_with_resolution_wraps_unexpected_errors(
    tmp_path: Path,
) -> None:
    with pytest.raises(ProjectServiceError, match="copy_directory_with_resolution"):
        ConflictResolutionService().copy_directory_with_resolution(
            tmp_path / "missing-source", tmp_path / "target"
        )
