#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST JAVASCRIPT PROJECT CREATION SERVICE - Direct service coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Direct tests for JavaScript project creation and setup operations."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
from pathlib import Path
from types import SimpleNamespace

# Third-party imports
import pytest

# Local imports
from womm.exceptions.project import ProjectServiceError
from womm.services.project.javascript_project_creation_service import (
    JavaScriptProjectCreationService,
)

# ///////////////////////////////////////////////////////////////
# FIXTURES AND HELPERS
# ///////////////////////////////////////////////////////////////


@pytest.fixture
def service() -> JavaScriptProjectCreationService:
    """Return the shared JavaScript project creation service."""
    return JavaScriptProjectCreationService()


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
    tmp_path: Path, service: JavaScriptProjectCreationService
) -> None:
    project_path = tmp_path / "demo"

    result = service.create_project_structure(project_path, "demo", "node")

    assert result.success
    assert result.project_type == "node"
    assert result.directories_created is not None
    relative_directories = {
        Path(item).relative_to(project_path).as_posix()
        for item in result.directories_created
    }
    assert relative_directories == {
        "src",
        "src/components",
        "src/utils",
        "tests",
        "docs",
        ".github",
        "public",
    }


@pytest.mark.parametrize(
    ("project_name", "project_type"),
    [("bad/name", "node"), ("demo", "python")],
)
def test_create_project_structure_rejects_invalid_input(
    tmp_path: Path,
    service: JavaScriptProjectCreationService,
    project_name: str,
    project_type: str,
) -> None:
    with pytest.raises(ProjectServiceError) as excinfo:
        service.create_project_structure(tmp_path / "demo", project_name, project_type)

    assert excinfo.value.operation == "create_project_structure"
    assert not (tmp_path / "demo").exists()


@pytest.mark.parametrize(
    ("project_type", "expected_files", "expected_main", "expected_dependency"),
    [
        (
            "node",
            {"src/main.js", "src/index.js"},
            "src/main.js",
            None,
        ),
        (
            "react",
            {
                "src/App.jsx",
                "src/App.css",
                "src/index.jsx",
                "src/index.css",
                "public/index.html",
            },
            "src/index.jsx",
            "react",
        ),
        (
            "vue",
            {"src/App.vue", "src/main.js", "public/index.html"},
            "src/main.js",
            "vue",
        ),
    ],
)
def test_create_minimal_project_files_for_each_variant(
    tmp_path: Path,
    service: JavaScriptProjectCreationService,
    project_type: str,
    expected_files: set[str],
    expected_main: str,
    expected_dependency: str | None,
) -> None:
    project_path = tmp_path / project_type
    service.create_project_structure(project_path, project_type, project_type)

    result = service.create_project_files(
        project_path, project_type, project_type, minimal=True
    )

    assert result.success
    assert result.files_created is not None
    assert relative_created_paths(project_path, result.files_created) == {
        "package.json",
        *expected_files,
    }
    package = json.loads((project_path / "package.json").read_text(encoding="utf-8"))
    assert package["name"] == project_type
    assert package["main"] == expected_main
    if expected_dependency is None:
        assert package["dependencies"] == {}
    else:
        assert expected_dependency in package["dependencies"]
    assert not (project_path / ".gitignore").exists()


def test_create_full_project_files_adds_gitignore(
    tmp_path: Path, service: JavaScriptProjectCreationService
) -> None:
    project_path = tmp_path / "demo"
    service.create_project_structure(project_path, "demo", "node")

    result = service.create_project_files(project_path, "demo", "node")

    assert result.files_created is not None
    assert ".gitignore" in relative_created_paths(project_path, result.files_created)
    assert (project_path / ".gitignore").read_text() == "node_modules/\n.env\n"


def test_create_project_files_requires_existing_directory(
    tmp_path: Path, service: JavaScriptProjectCreationService
) -> None:
    with pytest.raises(ProjectServiceError) as excinfo:
        service.create_project_files(tmp_path / "missing", "demo", "node", minimal=True)

    assert excinfo.value.operation == "create_project_files"
    assert excinfo.value.reason.startswith("Project directory does not exist:")


# ///////////////////////////////////////////////////////////////
# NPM AND DEVELOPMENT TOOLS
# ///////////////////////////////////////////////////////////////


def test_initialize_npm_project_accepts_existing_package(
    tmp_path: Path,
    service: JavaScriptProjectCreationService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "package.json").touch()
    monkeypatch.setattr(
        "womm.services.project.javascript_project_creation_service.check_npm_available",
        lambda: True,
    )

    result = service.initialize_npm_project(tmp_path, "demo")

    assert result.success
    assert result.project_name == "demo"


def test_initialize_npm_project_rejects_missing_npm(
    tmp_path: Path,
    service: JavaScriptProjectCreationService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "womm.services.project.javascript_project_creation_service.check_npm_available",
        lambda: False,
    )

    with pytest.raises(ProjectServiceError) as excinfo:
        service.initialize_npm_project(tmp_path, "demo")

    assert excinfo.value.operation == "initialize_npm_project"
    assert excinfo.value.reason == "npm is not installed or not in PATH"


@pytest.mark.parametrize("project_type", ["node", "javascript", "react", "vue"])
def test_install_dependencies_accepts_javascript_variants(
    tmp_path: Path,
    service: JavaScriptProjectCreationService,
    monkeypatch: pytest.MonkeyPatch,
    project_type: str,
) -> None:
    monkeypatch.setattr(
        "womm.services.project.javascript_project_creation_service.install_npm_dependencies",
        lambda _path: True,
    )

    result = service.install_dependencies(tmp_path, project_type)

    assert result.success
    assert result.project_type == project_type


def test_install_dependencies_rejects_failed_install(
    tmp_path: Path,
    service: JavaScriptProjectCreationService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "womm.services.project.javascript_project_creation_service.install_npm_dependencies",
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
    service: JavaScriptProjectCreationService,
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
        "womm.services.project.javascript_project_creation_service.install_npm_dev_dependencies",
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
    service: JavaScriptProjectCreationService,
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
    service: JavaScriptProjectCreationService,
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
    service: JavaScriptProjectCreationService,
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
    service: JavaScriptProjectCreationService,
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
    service: JavaScriptProjectCreationService,
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
    service: JavaScriptProjectCreationService,
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
