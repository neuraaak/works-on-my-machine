#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST PROJECT VALIDATION SERVICE - Direct project service coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Direct tests for project name, path, type, and config validation."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path

# Third-party imports
import pytest

# Local imports
from womm.exceptions.common import ValidationServiceError
from womm.services.project.validation_service import ProjectValidationService

# ///////////////////////////////////////////////////////////////
# PROJECT NAME VALIDATION
# ///////////////////////////////////////////////////////////////


def test_validate_project_name_accepts_a_valid_name() -> None:
    ProjectValidationService().validate_project_name("my-project_1.0")


def test_validate_project_name_rejects_empty_name() -> None:
    with pytest.raises(ValidationServiceError, match="cannot be empty"):
        ProjectValidationService().validate_project_name("")


def test_validate_project_name_rejects_name_too_long() -> None:
    too_long = "a" * 51

    with pytest.raises(ValidationServiceError, match="too long"):
        ProjectValidationService().validate_project_name(too_long)


@pytest.mark.parametrize("name", [".hidden", "trailing."])
def test_validate_project_name_rejects_leading_or_trailing_dot(name: str) -> None:
    with pytest.raises(ValidationServiceError, match="dot"):
        ProjectValidationService().validate_project_name(name)


def test_validate_project_name_rejects_invalid_characters() -> None:
    with pytest.raises(ValidationServiceError, match="invalid characters"):
        ProjectValidationService().validate_project_name("bad:name")


def test_validate_project_name_rejects_windows_reserved_name() -> None:
    with pytest.raises(ValidationServiceError, match="reserved"):
        ProjectValidationService().validate_project_name("CON")


def test_validate_project_name_rejects_disallowed_pattern() -> None:
    with pytest.raises(ValidationServiceError, match="letters, numbers"):
        ProjectValidationService().validate_project_name("bad name")


# ///////////////////////////////////////////////////////////////
# PROJECT PATH VALIDATION
# ///////////////////////////////////////////////////////////////


def test_validate_project_path_accepts_a_writable_new_directory(
    tmp_path: Path,
) -> None:
    ProjectValidationService().validate_project_path(tmp_path / "new-project")


def test_validate_project_path_rejects_none() -> None:
    with pytest.raises(ValidationServiceError, match="cannot be None"):
        ProjectValidationService().validate_project_path(None)


def test_validate_project_path_rejects_missing_parent(tmp_path: Path) -> None:
    missing_parent = tmp_path / "missing" / "project"

    with pytest.raises(ValidationServiceError, match="does not exist"):
        ProjectValidationService().validate_project_path(missing_parent)


def test_validate_project_path_rejects_parent_that_is_a_file(
    tmp_path: Path,
) -> None:
    parent_file = tmp_path / "not-a-dir"
    parent_file.touch()

    with pytest.raises(ValidationServiceError, match="not a directory"):
        ProjectValidationService().validate_project_path(parent_file / "project")


def test_validate_project_path_rejects_existing_path_that_is_a_file(
    tmp_path: Path,
) -> None:
    existing_file = tmp_path / "project"
    existing_file.touch()

    with pytest.raises(ValidationServiceError, match="not a directory"):
        ProjectValidationService().validate_project_path(existing_file)


def test_validate_project_path_rejects_non_empty_existing_directory(
    tmp_path: Path,
) -> None:
    existing_dir = tmp_path / "project"
    existing_dir.mkdir()
    (existing_dir / "file.txt").touch()

    with pytest.raises(ValidationServiceError, match="not empty"):
        ProjectValidationService().validate_project_path(existing_dir)


def test_validate_project_path_accepts_empty_existing_directory(
    tmp_path: Path,
) -> None:
    existing_dir = tmp_path / "project"
    existing_dir.mkdir()

    ProjectValidationService().validate_project_path(existing_dir)


# ///////////////////////////////////////////////////////////////
# PROJECT TYPE VALIDATION
# ///////////////////////////////////////////////////////////////


def test_validate_project_type_accepts_a_supported_type() -> None:
    ProjectValidationService().validate_project_type("python")


def test_validate_project_type_rejects_empty_type() -> None:
    with pytest.raises(ValidationServiceError, match="cannot be empty"):
        ProjectValidationService().validate_project_type("")


def test_validate_project_type_rejects_unsupported_type() -> None:
    with pytest.raises(ValidationServiceError, match="Unsupported project type"):
        ProjectValidationService().validate_project_type("cobol")


# ///////////////////////////////////////////////////////////////
# PROJECT CONFIG VALIDATION
# ///////////////////////////////////////////////////////////////


def test_validate_project_config_accepts_a_valid_config() -> None:
    ProjectValidationService().validate_project_config(
        {"project_name": "my-project", "project_type": "python"}
    )


def test_validate_project_config_rejects_empty_config() -> None:
    with pytest.raises(ValidationServiceError, match="cannot be None"):
        ProjectValidationService().validate_project_config({})


def test_validate_project_config_rejects_missing_required_field() -> None:
    with pytest.raises(ValidationServiceError, match="Missing required field"):
        ProjectValidationService().validate_project_config({"project_name": "ok"})


def test_validate_project_config_propagates_invalid_project_name() -> None:
    with pytest.raises(ValidationServiceError, match="cannot be empty"):
        ProjectValidationService().validate_project_config(
            {"project_name": "", "project_type": "python"}
        )


def test_validate_project_config_propagates_invalid_project_type() -> None:
    with pytest.raises(ValidationServiceError, match="Unsupported project type"):
        ProjectValidationService().validate_project_config(
            {"project_name": "my-project", "project_type": "cobol"}
        )


# ///////////////////////////////////////////////////////////////
# NAME SUGGESTION
# ///////////////////////////////////////////////////////////////


def test_suggest_project_name_sanitizes_invalid_input() -> None:
    result = ProjectValidationService().suggest_project_name("My Bad:Name!!")

    ProjectValidationService().validate_project_name(result)


def test_suggest_project_name_falls_back_for_empty_input() -> None:
    assert ProjectValidationService().suggest_project_name("") == "my-project"


# ///////////////////////////////////////////////////////////////
# NON-RAISING NAME CHECK
# ///////////////////////////////////////////////////////////////


def test_check_project_name_returns_true_for_valid_name() -> None:
    is_valid, error = ProjectValidationService().check_project_name("my-project")

    assert is_valid is True
    assert error is None


def test_check_project_name_returns_false_with_message_for_invalid_name() -> None:
    is_valid, error = ProjectValidationService().check_project_name("")

    assert is_valid is False
    assert error is not None
    assert "cannot be empty" in error


# ///////////////////////////////////////////////////////////////
# VALIDATION SUMMARY
# ///////////////////////////////////////////////////////////////


def test_get_validation_summary_reports_all_valid(tmp_path: Path) -> None:
    summary = ProjectValidationService().get_validation_summary(
        project_name="my-project",
        project_path=tmp_path / "new-project",
        project_type="python",
    )

    assert summary == {
        "project_name": True,
        "project_path": True,
        "project_type": True,
    }


def test_get_validation_summary_reports_each_invalid_component(
    tmp_path: Path,
) -> None:
    non_empty_dir = tmp_path / "existing"
    non_empty_dir.mkdir()
    (non_empty_dir / "file.txt").touch()

    summary = ProjectValidationService().get_validation_summary(
        project_name="",
        project_path=non_empty_dir,
        project_type="cobol",
    )

    assert summary == {
        "project_name": False,
        "project_path": False,
        "project_type": False,
    }
