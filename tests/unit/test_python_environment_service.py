#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST PYTHON ENVIRONMENT SERVICE - Direct service coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Direct tests for Python environment setup operations."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path
from types import SimpleNamespace

# Third-party imports
import pytest

# Local imports
from womm.exceptions.project import ProjectServiceError
from womm.services.project.python_environment_service import (
    PythonEnvironmentService,
)
from womm.shared.results import ProjectCreationResult

# ///////////////////////////////////////////////////////////////
# FIXTURES
# ///////////////////////////////////////////////////////////////


@pytest.fixture
def service() -> PythonEnvironmentService:
    """Return the shared Python environment service."""
    return PythonEnvironmentService()


# ///////////////////////////////////////////////////////////////
# ENVIRONMENT AND DEVELOPMENT TOOLS
# ///////////////////////////////////////////////////////////////


def test_setup_virtual_environment_accepts_success_result(
    tmp_path: Path,
    service: PythonEnvironmentService,
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
    service: PythonEnvironmentService,
    monkeypatch: pytest.MonkeyPatch,
    result: object,
) -> None:
    monkeypatch.setattr(
        "womm.services.project.python_environment_service.create_virtual_environment",
        lambda _path: result,
    )

    with pytest.raises(ProjectServiceError) as excinfo:
        service.setup_virtual_environment(tmp_path)

    assert excinfo.value.operation == "setup_virtual_environment"
    assert excinfo.value.reason == "Virtual environment creation returned failure"


@pytest.mark.parametrize("success", [True, False])
def test_install_dev_dependencies_reports_utility_result(
    tmp_path: Path,
    service: PythonEnvironmentService,
    monkeypatch: pytest.MonkeyPatch,
    success: bool,
) -> None:
    monkeypatch.setattr(
        "womm.services.project.python_environment_service.install_python_dependencies",
        lambda _path, _requirements: success,
    )

    result = service.install_dev_dependencies(tmp_path)

    assert result.success is success
    assert ("installed successfully" in result.message) is success


def test_install_dev_dependencies_wraps_utility_error(
    tmp_path: Path,
    service: PythonEnvironmentService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_install(_path: Path, _requirements: str) -> bool:
        raise FileNotFoundError("Virtual environment not found")

    monkeypatch.setattr(
        "womm.services.project.python_environment_service.install_python_dependencies",
        fail_install,
    )

    with pytest.raises(ProjectServiceError) as excinfo:
        service.install_dev_dependencies(tmp_path)

    assert excinfo.value.operation == "install_dev_dependencies"
    assert excinfo.value.reason == "Virtual environment not found"
    assert isinstance(excinfo.value.__cause__, FileNotFoundError)


def test_setup_dev_tools_creates_config_then_installs_dependencies(
    tmp_path: Path,
    service: PythonEnvironmentService,
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
        "womm.services.project.python_environment_service.create_python_dev_config_files",
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
    service: PythonEnvironmentService,
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
    service: PythonEnvironmentService,
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
