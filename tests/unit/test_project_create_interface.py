#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST PROJECT CREATE INTERFACE - Direct orchestration coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Direct tests for project creation orchestration."""

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
from womm.interfaces.project.create_interface import ProjectCreateInterface
from womm.shared.results import ProjectCreationResult

# ///////////////////////////////////////////////////////////////
# PUBLIC CREATION WORKFLOW
# ///////////////////////////////////////////////////////////////


def test_create_project_classifies_invalid_name_as_validation_failure(
    tmp_path: Path,
) -> None:
    result = ProjectCreateInterface().create_project(
        project_type="python",
        project_name="",
        project_path=tmp_path / "demo",
    )

    assert not result.success
    assert result.error.startswith("Project validation failed:")
    assert "Project name cannot be empty" in result.error


@pytest.mark.parametrize(
    ("project_type", "type_option", "expected_type"),
    [
        ("javascript", "js", "node"),
        ("javascript", "react-ts", "react"),
        ("javascript", "vue", "vue"),
        ("react", None, "react"),
    ],
)
def test_create_project_maps_javascript_variants(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    project_type: str,
    type_option: str | None,
    expected_type: str,
) -> None:
    interface = ProjectCreateInterface()
    captured: dict[str, object] = {}

    def capture(
        project_name: str,
        project_path: Path,
        javascript_type: str,
        force: bool,
        **kwargs: object,
    ) -> ProjectCreationResult:
        captured.update(
            name=project_name,
            path=project_path,
            type=javascript_type,
            force=force,
            kwargs=kwargs,
        )
        return ProjectCreationResult(success=True)

    monkeypatch.setattr(interface, "_create_javascript_project", capture)
    kwargs = {"type": type_option} if type_option is not None else {}

    result = interface.create_project(
        project_type,
        "demo",
        tmp_path / "demo",
        force=True,
        **kwargs,
    )

    assert result.success
    assert captured["type"] == expected_type
    assert captured["force"] is True


def test_create_project_translates_service_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    interface = ProjectCreateInterface()

    def fail(*_args: object, **_kwargs: object) -> ProjectCreationResult:
        raise ProjectServiceError(operation="create_project", reason="template missing")

    monkeypatch.setattr(interface, "_create_python_project", fail)

    result = interface.create_project("python", "demo", tmp_path / "demo")

    assert not result.success
    assert result.error == "Project creation failed: template missing"


# ///////////////////////////////////////////////////////////////
# PYTHON ORCHESTRATION
# ///////////////////////////////////////////////////////////////


def test_create_python_installs_dependencies_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    interface = ProjectCreateInterface()
    install_calls = 0

    def success(*_args: object, **_kwargs: object) -> ProjectCreationResult:
        return ProjectCreationResult(success=True)

    def create_files(*_args: object, **_kwargs: object) -> ProjectCreationResult:
        return ProjectCreationResult(
            success=True,
            files_created=["pyproject.toml", "src/demo.py"],
        )

    def install_dependencies(_path: Path) -> ProjectCreationResult:
        nonlocal install_calls
        install_calls += 1
        return ProjectCreationResult(success=True)

    monkeypatch.setattr(interface._python_service, "create_project_structure", success)
    monkeypatch.setattr(interface._python_service, "create_project_files", create_files)
    monkeypatch.setattr(interface._python_service, "setup_virtual_environment", success)
    monkeypatch.setattr(
        interface._python_service,
        "install_dev_dependencies",
        install_dependencies,
    )
    monkeypatch.setattr(interface._python_service, "setup_git_repository", success)
    monkeypatch.setattr(interface, "_get_configured_tools", lambda *_args: ["Git"])
    monkeypatch.setattr(
        "womm.services.project.python_project_creation_service.create_python_dev_config_files",
        lambda _path: [],
    )

    result = interface._create_python_project(
        "demo",
        tmp_path / "demo",
        force=False,
    )

    assert result.success
    assert result.files_created == ["pyproject.toml", "src/demo.py"]
    assert result.tools_configured == ["Git"]
    assert install_calls == 1


def test_create_python_minimal_skips_environment_setup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    interface = ProjectCreateInterface()
    environment_calls: list[str] = []

    monkeypatch.setattr(
        interface._python_service,
        "create_project_structure",
        lambda *_args: ProjectCreationResult(success=True),
    )
    monkeypatch.setattr(
        interface._python_service,
        "create_project_files",
        lambda *_args, **_kwargs: ProjectCreationResult(
            success=True,
            files_created=["pyproject.toml"],
        ),
    )
    monkeypatch.setattr(
        interface._python_service,
        "setup_virtual_environment",
        lambda *_args: environment_calls.append("venv"),
    )
    monkeypatch.setattr(
        interface._python_service,
        "setup_dev_tools",
        lambda *_args: environment_calls.append("tools"),
    )
    monkeypatch.setattr(
        interface._python_service,
        "setup_git_repository",
        lambda *_args: environment_calls.append("git"),
    )

    result = interface._create_python_project(
        "demo",
        tmp_path / "demo",
        force=False,
        minimal=True,
    )

    assert result.success
    assert result.files_created == ["pyproject.toml"]
    assert result.tools_configured == []
    assert environment_calls == []


def test_create_python_reports_git_setup_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    interface = ProjectCreateInterface()

    monkeypatch.setattr(
        interface._python_service,
        "create_project_structure",
        lambda *_args: ProjectCreationResult(success=True),
    )
    monkeypatch.setattr(
        interface._python_service,
        "create_project_files",
        lambda *_args, **_kwargs: ProjectCreationResult(success=True),
    )
    monkeypatch.setattr(
        interface._python_service,
        "setup_virtual_environment",
        lambda *_args: ProjectCreationResult(success=True),
    )
    monkeypatch.setattr(
        interface._python_service,
        "setup_dev_tools",
        lambda *_args: ProjectCreationResult(success=True),
    )
    monkeypatch.setattr(
        interface._python_service,
        "setup_git_repository",
        lambda *_args: ProjectCreationResult(success=False),
    )

    result = interface._create_python_project(
        "demo",
        tmp_path / "demo",
        force=False,
    )

    assert not result.success
    assert result.error == "Failed to setup Git repository"


# ///////////////////////////////////////////////////////////////
# JAVASCRIPT ORCHESTRATION
# ///////////////////////////////////////////////////////////////


def test_create_javascript_runs_full_workflow_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    interface = ProjectCreateInterface()
    calls: list[tuple[object, ...]] = []

    def succeed(name: str):
        def operation(*args: object, **_kwargs: object) -> ProjectCreationResult:
            calls.append((name, *args))
            files = ["package.json", "src/index.jsx"] if name == "files" else None
            return ProjectCreationResult(success=True, files_created=files)

        return operation

    monkeypatch.setattr(
        interface._javascript_service,
        "create_project_structure",
        succeed("structure"),
    )
    monkeypatch.setattr(
        interface._javascript_service,
        "create_project_files",
        succeed("files"),
    )
    monkeypatch.setattr(
        interface._javascript_service,
        "initialize_npm_project",
        succeed("npm"),
    )
    monkeypatch.setattr(
        interface._javascript_service,
        "install_dependencies",
        succeed("dependencies"),
    )
    monkeypatch.setattr(
        interface._javascript_service,
        "setup_dev_tools",
        succeed("tools"),
    )
    monkeypatch.setattr(
        interface._javascript_service,
        "setup_git_repository",
        succeed("git"),
    )
    monkeypatch.setattr(
        interface,
        "_get_configured_tools",
        lambda *_args: ["package.json", "Git"],
    )
    project_path = tmp_path / "demo"

    result = interface._create_javascript_project(
        "demo",
        project_path,
        "react",
        force=False,
    )

    assert result.success
    assert result.files_created == ["package.json", "src/index.jsx"]
    assert result.tools_configured == ["package.json", "Git"]
    assert calls == [
        ("structure", project_path, "demo", "react"),
        ("files", project_path, "demo", "react"),
        ("npm", project_path, "demo"),
        ("dependencies", project_path, "react"),
        ("tools", project_path, "react"),
        ("git", project_path),
    ]


def test_create_javascript_minimal_skips_environment_setup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    interface = ProjectCreateInterface()
    environment_calls: list[str] = []

    monkeypatch.setattr(
        interface._javascript_service,
        "create_project_structure",
        lambda *_args: ProjectCreationResult(success=True),
    )
    monkeypatch.setattr(
        interface._javascript_service,
        "create_project_files",
        lambda *_args, **_kwargs: ProjectCreationResult(
            success=True,
            files_created=["package.json"],
        ),
    )
    monkeypatch.setattr(
        interface._javascript_service,
        "initialize_npm_project",
        lambda *_args, **_kwargs: environment_calls.append("npm"),
    )
    monkeypatch.setattr(
        interface._javascript_service,
        "install_dependencies",
        lambda *_args: environment_calls.append("dependencies"),
    )
    monkeypatch.setattr(
        interface._javascript_service,
        "setup_dev_tools",
        lambda *_args: environment_calls.append("tools"),
    )
    monkeypatch.setattr(
        interface._javascript_service,
        "setup_git_repository",
        lambda *_args: environment_calls.append("git"),
    )

    result = interface._create_javascript_project(
        "demo",
        tmp_path / "demo",
        "vue",
        force=False,
        minimal=True,
    )

    assert result.success
    assert result.files_created == ["package.json"]
    assert result.tools_configured == []
    assert environment_calls == []


def test_create_javascript_reports_git_setup_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    interface = ProjectCreateInterface()

    def success(*_args: object, **_kwargs: object) -> ProjectCreationResult:
        return ProjectCreationResult(success=True)

    monkeypatch.setattr(
        interface._javascript_service, "create_project_structure", success
    )
    monkeypatch.setattr(interface._javascript_service, "create_project_files", success)
    monkeypatch.setattr(
        interface._javascript_service, "initialize_npm_project", success
    )
    monkeypatch.setattr(interface._javascript_service, "install_dependencies", success)
    monkeypatch.setattr(interface._javascript_service, "setup_dev_tools", success)
    monkeypatch.setattr(
        interface._javascript_service,
        "setup_git_repository",
        lambda *_args: ProjectCreationResult(success=False),
    )

    result = interface._create_javascript_project(
        "demo",
        tmp_path / "demo",
        "node",
        force=False,
    )

    assert not result.success
    assert result.error == "Failed to setup Git repository"


# ///////////////////////////////////////////////////////////////
# SUPPORT HELPERS
# ///////////////////////////////////////////////////////////////


def test_get_configured_tools_detects_created_artifacts(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").touch()
    (tmp_path / "package.json").touch()
    (tmp_path / ".vscode").mkdir()
    (tmp_path / ".git").mkdir()
    (tmp_path / ".venv").mkdir()

    tools = ProjectCreateInterface()._get_configured_tools(tmp_path, "python")

    assert tools == [
        "pyproject.toml",
        "package.json",
        "VSCode",
        "Git",
        "Virtual Environment",
    ]
