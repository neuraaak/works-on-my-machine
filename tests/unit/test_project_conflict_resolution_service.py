#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST PROJECT CONFLICT RESOLUTION SERVICE - Direct service coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Direct tests for the project destination guard used by ``womm create``.

Since 2026-08-02 the service exposes a single policy: refuse a non-empty
destination unless ``--force`` allows generated files to be merged into it.
"""

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
    ConflictResolutionService,
)

# ///////////////////////////////////////////////////////////////
# DESTINATION VALIDATION
# ///////////////////////////////////////////////////////////////


def test_missing_destination_is_accepted(tmp_path: Path) -> None:
    ConflictResolutionService().validate_project_destination(tmp_path / "new")


def test_empty_destination_is_accepted(tmp_path: Path) -> None:
    target = tmp_path / "empty"
    target.mkdir()

    ConflictResolutionService().validate_project_destination(target)


def test_non_empty_destination_is_refused_without_force(tmp_path: Path) -> None:
    target = tmp_path / "existing"
    target.mkdir()
    (target / "keep.txt").write_text("user content", encoding="utf-8")

    with pytest.raises(ProjectServiceError, match="already exists and is not empty"):
        ConflictResolutionService().validate_project_destination(target)


def test_non_empty_destination_is_accepted_with_force(tmp_path: Path) -> None:
    target = tmp_path / "existing"
    target.mkdir()
    keep = target / "keep.txt"
    keep.write_text("user content", encoding="utf-8")

    ConflictResolutionService().validate_project_destination(target, force=True)

    # --force merges, it never deletes what the user already had there.
    assert keep.read_text(encoding="utf-8") == "user content"


def test_destination_that_is_a_file_is_refused(tmp_path: Path) -> None:
    target = tmp_path / "a-file"
    target.write_text("x", encoding="utf-8")

    with pytest.raises(ProjectServiceError, match="is not a directory"):
        ConflictResolutionService().validate_project_destination(target)


def test_destination_that_is_a_file_is_refused_even_with_force(tmp_path: Path) -> None:
    # `force` relaxes the non-empty rule only; it must not turn a file into a
    # valid project root.
    target = tmp_path / "a-file"
    target.write_text("x", encoding="utf-8")

    with pytest.raises(ProjectServiceError, match="is not a directory"):
        ConflictResolutionService().validate_project_destination(target, force=True)


def test_unreadable_destination_is_wrapped_as_a_service_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "existing"
    target.mkdir()

    def _boom(_self: Path) -> object:
        raise OSError("permission denied")

    monkeypatch.setattr(Path, "iterdir", _boom)

    with pytest.raises(ProjectServiceError, match="permission denied"):
        ConflictResolutionService().validate_project_destination(target)
