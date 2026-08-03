"""Tests for the destination pre-flight guard."""

from pathlib import Path

import pytest

from womm.exceptions.project import ProjectServiceError
from womm.services.project.destination_guard import (
    check_destination,
    describe_occupants,
)


def test_missing_destination_is_accepted(tmp_path: Path):
    check_destination(tmp_path / "new-project", force=False)


def test_empty_destination_is_accepted(tmp_path: Path):
    destination = tmp_path / "empty"
    destination.mkdir()
    check_destination(destination, force=False)


def test_git_only_destination_is_accepted(tmp_path: Path):
    destination = tmp_path / "cloned"
    (destination / ".git").mkdir(parents=True)
    check_destination(destination, force=False)


def test_non_empty_destination_is_refused(tmp_path: Path):
    destination = tmp_path / "busy"
    destination.mkdir()
    (destination / "README.md").write_text("x", encoding="utf-8")

    with pytest.raises(ProjectServiceError) as excinfo:
        check_destination(destination, force=False)

    assert excinfo.value.operation == "check_destination"
    assert "--force" in str(excinfo.value)


def test_non_empty_destination_is_accepted_with_force(tmp_path: Path):
    destination = tmp_path / "busy"
    destination.mkdir()
    (destination / "README.md").write_text("x", encoding="utf-8")

    check_destination(destination, force=True)


def test_file_destination_is_refused_even_with_force(tmp_path: Path):
    destination = tmp_path / "a-file.txt"
    destination.write_text("x", encoding="utf-8")

    with pytest.raises(ProjectServiceError):
        check_destination(destination, force=True)


def test_describe_occupants_is_capped(tmp_path: Path):
    for index in range(10):
        (tmp_path / f"file-{index}.txt").write_text("x", encoding="utf-8")

    occupants = describe_occupants(tmp_path, limit=4)

    assert len(occupants) == 4


def test_describe_occupants_ignores_git(tmp_path: Path):
    (tmp_path / ".git").mkdir()
    (tmp_path / "README.md").write_text("x", encoding="utf-8")

    assert describe_occupants(tmp_path) == ["README.md"]
