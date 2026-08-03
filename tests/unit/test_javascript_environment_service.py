#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST JAVASCRIPT ENVIRONMENT SERVICE - Direct service coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Direct tests for JavaScript environment setup operations."""

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
from womm.services.project.javascript_environment_service import (
    JavaScriptEnvironmentService,
)

# ///////////////////////////////////////////////////////////////
# FIXTURES AND HELPERS
# ///////////////////////////////////////////////////////////////


@pytest.fixture
def service() -> JavaScriptEnvironmentService:
    """Return the shared JavaScript environment service."""
    return JavaScriptEnvironmentService()


# ///////////////////////////////////////////////////////////////
# NPM AND DEVELOPMENT TOOLS
# ///////////////////////////////////////////////////////////////


@pytest.mark.parametrize("project_type", ["node", "javascript", "react", "vue"])
def test_install_dependencies_accepts_javascript_variants(
    tmp_path: Path,
    service: JavaScriptEnvironmentService,
    monkeypatch: pytest.MonkeyPatch,
    project_type: str,
) -> None:
    monkeypatch.setattr(
        "womm.services.project.javascript_environment_service.install_npm_dependencies",
        lambda _path: True,
    )

    result = service.install_dependencies(tmp_path, project_type)

    assert result.success
    assert result.project_type == project_type


def test_install_dependencies_rejects_failed_install(
    tmp_path: Path,
    service: JavaScriptEnvironmentService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "womm.services.project.javascript_environment_service.install_npm_dependencies",
        lambda _path: False,
    )

    with pytest.raises(ProjectServiceError) as excinfo:
        service.install_dependencies(tmp_path, "node")

    assert excinfo.value.operation == "install_dependencies"
    assert excinfo.value.reason == "npm install command failed"


@pytest.mark.parametrize(
    ("project_type", "specific_dependencies"),
    [
        ("node", set()),
        (
            "react",
            {
                "@types/react",
                "@types/react-dom",
                "@testing-library/react",
                "@testing-library/jest-dom",
            },
        ),
        ("vue", {"@vue/cli-service", "@vue/compiler-sfc"}),
    ],
)
def test_setup_dev_tools_installs_variant_dependencies(
    tmp_path: Path,
    service: JavaScriptEnvironmentService,
    monkeypatch: pytest.MonkeyPatch,
    project_type: str,
    specific_dependencies: set[str],
) -> None:
    captured: list[str] = []
    monkeypatch.setattr("shutil.which", lambda _command: "npm")

    def install(_path: Path, dependencies: list[str]) -> bool:
        captured.extend(dependencies)
        return True

    monkeypatch.setattr(
        "womm.services.project.javascript_environment_service.install_npm_dev_dependencies",
        install,
    )

    result = service.setup_dev_tools(tmp_path, project_type)

    assert result.success
    assert {"eslint", "prettier", "husky", "lint-staged", "@types/node"} <= set(
        captured
    )
    assert specific_dependencies <= set(captured)


def test_setup_dev_tools_validates_project_path_before_npm(
    tmp_path: Path,
    service: JavaScriptEnvironmentService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("shutil.which", lambda _command: None)

    with pytest.raises(ProjectServiceError) as excinfo:
        service.setup_dev_tools(tmp_path / "missing", "node")

    assert excinfo.value.operation == "setup_dev_tools"
    assert excinfo.value.reason.startswith("Project directory does not exist:")


# ///////////////////////////////////////////////////////////////
# GIT AND HUSKY
# ///////////////////////////////////////////////////////////////


def test_setup_git_repository_skips_when_git_is_unavailable(
    tmp_path: Path,
    service: JavaScriptEnvironmentService,
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
    service: JavaScriptEnvironmentService,
    monkeypatch: pytest.MonkeyPatch,
    returncode: int,
    expected_success: bool,
) -> None:
    (tmp_path / "package.json").touch()
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


def test_setup_git_hooks_skips_when_npx_is_unavailable(
    tmp_path: Path,
    service: JavaScriptEnvironmentService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("shutil.which", lambda _command: None)

    result = service.setup_git_hooks(tmp_path)

    assert result.success
    assert result.warnings == ["npx not found in system PATH"]


@pytest.mark.parametrize(
    ("returncodes", "expected_error"),
    [
        ([1], "husky init failed"),
        ([0, 1], "husky hook creation failed"),
    ],
)
def test_setup_git_hooks_reports_command_failure(
    tmp_path: Path,
    service: JavaScriptEnvironmentService,
    monkeypatch: pytest.MonkeyPatch,
    returncodes: list[int],
    expected_error: str,
) -> None:
    (tmp_path / "package.json").touch()
    results = iter(
        SimpleNamespace(returncode=code, stderr=expected_error) for code in returncodes
    )
    monkeypatch.setattr("shutil.which", lambda _command: "npx")
    monkeypatch.setattr(
        service._command_runner,
        "run",
        lambda *_args, **_kwargs: next(results),
    )

    result = service.setup_git_hooks(tmp_path)

    assert not result.success
    assert result.error == expected_error


def test_setup_git_hooks_runs_init_then_add(
    tmp_path: Path,
    service: JavaScriptEnvironmentService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    commands: list[list[str]] = []
    (tmp_path / "package.json").touch()
    monkeypatch.setattr("shutil.which", lambda _command: "npx")

    def run(command: list[str], **_kwargs: object) -> SimpleNamespace:
        commands.append(command)
        return SimpleNamespace(returncode=0, stderr="")

    monkeypatch.setattr(service._command_runner, "run", run)

    result = service.setup_git_hooks(tmp_path)

    assert result.success
    assert commands == [
        ["npx", "husky", "install"],
        ["npx", "husky", "add", ".husky/pre-commit", "npm run lint-staged"],
    ]
