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
from types import SimpleNamespace
from typing import cast

# Third-party imports
import pytest

# Local imports
from womm.exceptions.project import ProjectServiceError
from womm.services.project.python_project_creation_service import (
    PythonProjectCreationService,
)
from womm.shared.results import ProjectCreationResult

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


# ///////////////////////////////////////////////////////////////
# ENVIRONMENT AND DEVELOPMENT TOOLS
# ///////////////////////////////////////////////////////////////


def test_setup_virtual_environment_accepts_success_result(
    tmp_path: Path,
    service: PythonProjectCreationService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "pyproject.toml").touch()

    def create_venv(path: Path, *, with_pip: bool) -> None:
        assert with_pip
        path.mkdir()

    monkeypatch.setattr(
        "womm.services.project.env_utils.venv.create",
        create_venv,
    )
    monkeypatch.setattr(
        "womm.services.project.env_utils._upgrade_pip",
        lambda _project_path, _venv_path: None,
    )

    result = service.setup_virtual_environment(tmp_path)

    assert result.success
    assert result.project_type == "python"
    assert (tmp_path / "venv").is_dir()


@pytest.mark.parametrize("result", [{"success": False}, None])
def test_setup_virtual_environment_rejects_unsuccessful_result(
    tmp_path: Path,
    service: PythonProjectCreationService,
    monkeypatch: pytest.MonkeyPatch,
    result: object,
) -> None:
    monkeypatch.setattr(
        "womm.services.project.python_project_creation_service.create_virtual_environment",
        lambda _path: result,
    )

    with pytest.raises(ProjectServiceError) as excinfo:
        service.setup_virtual_environment(tmp_path)

    assert excinfo.value.operation == "setup_virtual_environment"
    assert excinfo.value.reason == "Virtual environment creation returned failure"


@pytest.mark.parametrize("success", [True, False])
def test_install_dev_dependencies_reports_utility_result(
    tmp_path: Path,
    service: PythonProjectCreationService,
    monkeypatch: pytest.MonkeyPatch,
    success: bool,
) -> None:
    monkeypatch.setattr(
        "womm.services.project.python_project_creation_service.install_python_dependencies",
        lambda _path, _requirements: success,
    )

    result = service.install_dev_dependencies(tmp_path)

    assert result.success is success
    assert ("installed successfully" in result.message) is success


def test_install_dev_dependencies_wraps_utility_error(
    tmp_path: Path,
    service: PythonProjectCreationService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_install(_path: Path, _requirements: str) -> bool:
        raise FileNotFoundError("Virtual environment not found")

    monkeypatch.setattr(
        "womm.services.project.python_project_creation_service.install_python_dependencies",
        fail_install,
    )

    with pytest.raises(ProjectServiceError) as excinfo:
        service.install_dev_dependencies(tmp_path)

    assert excinfo.value.operation == "install_dev_dependencies"
    assert excinfo.value.reason == "Virtual environment not found"
    assert isinstance(excinfo.value.__cause__, FileNotFoundError)


def test_setup_dev_tools_creates_config_then_installs_dependencies(
    tmp_path: Path,
    service: PythonProjectCreationService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def create_config(_path: Path) -> list[str]:
        calls.append("config")
        return []

    def install_dependencies(_path: Path) -> ProjectCreationResult:
        calls.append("dependencies")
        return ProjectCreationResult(success=True)

    monkeypatch.setattr(
        "womm.services.project.python_project_creation_service.create_python_dev_config_files",
        create_config,
    )
    monkeypatch.setattr(service, "install_dev_dependencies", install_dependencies)

    result = service.setup_dev_tools(tmp_path)

    assert result.success
    assert calls == ["config", "dependencies"]


# ///////////////////////////////////////////////////////////////
# GIT SETUP
# ///////////////////////////////////////////////////////////////


def test_setup_git_repository_skips_when_git_is_unavailable(
    tmp_path: Path,
    service: PythonProjectCreationService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("shutil.which", lambda _command: None)

    result = service.setup_git_repository(tmp_path)

    assert result.success
    assert result.warnings == ["Git not found in system PATH"]


@pytest.mark.parametrize(
    ("returncode", "expected_success"),
    [(0, True), (1, False)],
)
def test_setup_git_repository_reports_command_result(
    tmp_path: Path,
    service: PythonProjectCreationService,
    monkeypatch: pytest.MonkeyPatch,
    returncode: int,
    expected_success: bool,
) -> None:
    (tmp_path / "pyproject.toml").touch()
    monkeypatch.setattr("shutil.which", lambda _command: "git")
    monkeypatch.setattr(
        service._command_runner,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=returncode, stderr="git failed"
        ),
    )

    result = service.setup_git_repository(tmp_path)

    assert result.success is expected_success
    assert result.error == ("" if expected_success else "git failed")
