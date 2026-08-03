#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST PYTHON PROJECT CREATION SERVICE - Direct service coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Direct tests for Python project creation and setup operations."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path
from typing import cast

# Third-party imports
import pytest

# Local imports
from womm.exceptions.project import ProjectServiceError
from womm.services.project.python_project_creation_service import (
    PythonProjectCreationService,
)

# ///////////////////////////////////////////////////////////////
# FIXTURES
# ///////////////////////////////////////////////////////////////


@pytest.fixture
def service() -> PythonProjectCreationService:
    """Return the shared Python project creation service."""
    return PythonProjectCreationService()


def relative_created_paths(project_path: Path, paths: list[str]) -> set[str]:
    """Normalize reported file paths relative to the project."""
    relative_paths = set()
    for item in paths:
        path = Path(item)
        if path.is_absolute():
            path = path.relative_to(project_path)
        relative_paths.add(path.as_posix())
    return relative_paths


# ///////////////////////////////////////////////////////////////
# STRUCTURE AND FILE CREATION
# ///////////////////////////////////////////////////////////////


def test_create_project_structure_creates_expected_directories(
    tmp_path: Path, service: PythonProjectCreationService
) -> None:
    project_path = tmp_path / "demo"

    result = service.create_project_structure(project_path, "demo")

    assert result.success
    assert result.project_name == "demo"
    assert result.project_type == "python"
    assert result.directories_created is not None
    relative_directories = {
        Path(item).relative_to(project_path).as_posix()
        for item in result.directories_created
    }
    assert relative_directories == {
        "src",
        "tests",
        "docs",
        ".github",
        "demo",
    }


def test_create_project_structure_rejects_invalid_name(
    tmp_path: Path, service: PythonProjectCreationService
) -> None:
    with pytest.raises(ProjectServiceError) as excinfo:
        service.create_project_structure(tmp_path / "demo", "bad/name")

    assert excinfo.value.operation == "create_project_structure"
    assert "invalid characters" in excinfo.value.reason
    assert not (tmp_path / "demo").exists()


def test_create_minimal_project_files_after_structure_creation(
    tmp_path: Path, service: PythonProjectCreationService
) -> None:
    project_path = tmp_path / "demo"
    service.create_project_structure(project_path, "demo")

    result = service.create_project_files(project_path, "demo", minimal=True)

    assert result.success
    assert result.files_created is not None
    assert relative_created_paths(project_path, result.files_created) == {
        "pyproject.toml",
        "src/demo/__init__.py",
        "src/demo/main.py",
    }
    assert (project_path / "pyproject.toml").is_file()
    assert not (project_path / "tests" / "test_demo.py").exists()
    assert not (project_path / "requirements-dev.txt").exists()


def test_create_full_project_files_after_structure_creation(
    tmp_path: Path, service: PythonProjectCreationService
) -> None:
    project_path = tmp_path / "demo"
    service.create_project_structure(project_path, "demo")

    result = service.create_project_files(project_path, "demo")

    assert result.success
    assert result.files_created is not None
    assert relative_created_paths(project_path, result.files_created) == {
        "pyproject.toml",
        "src/demo/__init__.py",
        "src/demo/main.py",
        "tests/test_demo.py",
        "requirements.txt",
        "requirements-dev.txt",
    }


def test_create_project_files_requires_existing_directory(
    tmp_path: Path, service: PythonProjectCreationService
) -> None:
    with pytest.raises(ProjectServiceError) as excinfo:
        service.create_project_files(tmp_path / "missing", "demo", minimal=True)

    assert excinfo.value.operation == "create_project_files"
    assert excinfo.value.reason.startswith("Project directory does not exist:")


def test_create_pyproject_passes_custom_template_values(
    tmp_path: Path,
    service: PythonProjectCreationService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def capture_template(
        template_path: Path,
        output_path: Path,
        template_vars: dict[str, str],
    ) -> None:
        captured.update(
            template_path=template_path,
            output_path=output_path,
            template_vars=template_vars,
        )

    monkeypatch.setattr(
        service._template_service, "generate_template", capture_template
    )

    result = service._create_pyproject_toml(
        tmp_path,
        "demo",
        author_name="Ada",
        author_email="ada@example.com",
    )

    assert result.success
    assert captured["output_path"] == tmp_path / "pyproject.toml"
    template_vars = cast("dict[str, str]", captured["template_vars"])
    assert template_vars["AUTHOR_NAME"] == "Ada"
    assert template_vars["AUTHOR_EMAIL"] == "ada@example.com"
