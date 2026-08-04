#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST PROJECT SETUP INTERFACE - Direct orchestration coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Direct tests for project setup orchestration."""

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
from womm.interfaces.project.setup_interface import ProjectSetupInterface
from womm.shared.results import ProjectCreationResult, ProjectDetectionResult

# ///////////////////////////////////////////////////////////////
# PUBLIC SETUP WORKFLOWS
# ///////////////////////////////////////////////////////////////


def test_setup_project_reports_missing_directory_as_validation_failure(
    tmp_path: Path,
) -> None:
    result = ProjectSetupInterface().setup_project(
        tmp_path / "missing", project_type="python"
    )

    assert not result.success
    assert result.error.startswith("Failed to setup project:")
    assert "Project directory does not exist" in result.error


def test_setup_project_auto_detects_and_aggregates_results(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    interface = ProjectSetupInterface()
    monkeypatch.setattr(
        interface._detection_service,
        "detect_project_type",
        lambda _path: ProjectDetectionResult(success=True, project_type="python"),
    )
    monkeypatch.setattr(interface, "_check_dependencies", lambda _type: "")
    monkeypatch.setattr(interface, "_copy_vscode_config", lambda *_args: None)
    monkeypatch.setattr(
        interface,
        "_setup_python_project",
        lambda *_args, **_kwargs: {
            "files_modified": ["pyproject.toml"],
            "tools_configured": ["venv"],
            "warnings": ["partial warning"],
        },
    )

    result = interface.setup_project(tmp_path)

    assert result.success
    assert result.project_type == "python"
    assert result.project_name == tmp_path.name
    assert result.files_modified == ["pyproject.toml"]
    assert result.tools_configured == ["vscode", "venv"]
    assert result.warnings == ["partial warning"]


def test_setup_project_returns_dependency_probe_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    interface = ProjectSetupInterface()
    monkeypatch.setattr(
        interface,
        "_check_dependencies",
        lambda _type: "Node.js runtime not found",
    )

    result = interface.setup_project(tmp_path, project_type="javascript")

    assert not result.success
    assert result.error == "Node.js runtime not found"


def test_setup_project_keeps_vscode_copy_failure_as_warning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    interface = ProjectSetupInterface()
    monkeypatch.setattr(interface, "_check_dependencies", lambda _type: "")

    def fail_copy(_path: Path, _type: str) -> None:
        raise OSError("assets unavailable")

    monkeypatch.setattr(interface, "_copy_vscode_config", fail_copy)

    result = interface.setup_project(tmp_path, project_type="python")

    assert result.success
    assert result.tools_configured is not None
    assert "vscode" not in result.tools_configured
    assert result.warnings == ["VSCode configuration skipped: assets unavailable"]


def test_setup_development_environment_forwards_complete_defaults(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    interface = ProjectSetupInterface()
    captured: dict[str, object] = {}

    def capture_setup(project_path: Path, **kwargs: object) -> ProjectCreationResult:
        captured["project_path"] = project_path
        captured.update(kwargs)
        return ProjectCreationResult(success=True, project_path=project_path)

    monkeypatch.setattr(interface, "setup_project", capture_setup)

    result = interface.setup_development_environment(tmp_path, "python")

    assert result.success
    assert captured == {
        "project_path": tmp_path,
        "project_type": "python",
        "virtual_env": True,
        "install_deps": True,
        "setup_dev_tools": True,
        "setup_git_hooks": False,
    }


# ///////////////////////////////////////////////////////////////
# PYTHON ORCHESTRATION
# ///////////////////////////////////////////////////////////////


def test_setup_python_installs_dependencies_once_when_dev_tools_are_enabled(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    interface = ProjectSetupInterface()
    install_calls = 0

    def install_dependencies(_path: Path) -> ProjectCreationResult:
        nonlocal install_calls
        install_calls += 1
        return ProjectCreationResult(success=True)

    monkeypatch.setattr(
        interface._python_service,
        "install_dev_dependencies",
        install_dependencies,
    )
    monkeypatch.setattr(
        "womm.services.project.python_environment_service.create_python_dev_config_files",
        lambda _path: [],
    )

    result = interface._setup_python_project(
        tmp_path,
        install_deps=True,
        setup_dev_tools=True,
    )

    assert install_calls == 1
    assert result["tools_configured"] == ["dependencies", "dev_tools"]


def test_setup_python_collects_failures_and_continues(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    interface = ProjectSetupInterface()

    def fail_venv(_path: Path) -> ProjectCreationResult:
        raise OSError("venv unavailable")

    monkeypatch.setattr(
        interface._python_service, "setup_virtual_environment", fail_venv
    )
    monkeypatch.setattr(
        interface._python_service,
        "setup_dev_tools",
        lambda _path: ProjectCreationResult(success=False),
    )
    monkeypatch.setattr(
        interface._python_service,
        "setup_git_repository",
        lambda _path: ProjectCreationResult(success=False),
    )

    result = interface._setup_python_project(
        tmp_path,
        virtual_env=True,
        setup_dev_tools=True,
        setup_git_hooks=True,
    )

    assert result["tools_configured"] == []
    assert result["warnings"] == [
        "Virtual environment setup skipped: venv unavailable",
        "Dev tools setup failed",
        "Git repository setup failed",
    ]


# ///////////////////////////////////////////////////////////////
# JAVASCRIPT ORCHESTRATION
# ///////////////////////////////////////////////////////////////


def test_setup_javascript_runs_each_requested_operation_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    interface = ProjectSetupInterface()
    calls: list[str] = []

    def succeed(name: str):
        def operation(*_args: object) -> ProjectCreationResult:
            calls.append(name)
            return ProjectCreationResult(success=True)

        return operation

    monkeypatch.setattr(
        interface._javascript_service,
        "install_dependencies",
        succeed("dependencies"),
    )
    monkeypatch.setattr(
        interface._javascript_service,
        "setup_dev_tools",
        succeed("dev_tools"),
    )
    monkeypatch.setattr(
        interface._javascript_service,
        "setup_git_repository",
        succeed("git"),
    )
    monkeypatch.setattr(
        interface._javascript_service,
        "setup_git_hooks",
        succeed("git_hooks"),
    )

    result = interface._setup_javascript_project(
        tmp_path,
        "react",
        install_deps=True,
        setup_dev_tools=True,
        setup_git_hooks=True,
    )

    assert calls == ["dependencies", "dev_tools", "git", "git_hooks"]
    assert result["tools_configured"] == calls
    assert result["warnings"] == []


def test_setup_javascript_collects_unsuccessful_results(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    interface = ProjectSetupInterface()

    def failure(*_args: object) -> ProjectCreationResult:
        return ProjectCreationResult(success=False)

    monkeypatch.setattr(interface._javascript_service, "install_dependencies", failure)
    monkeypatch.setattr(interface._javascript_service, "setup_dev_tools", failure)
    monkeypatch.setattr(interface._javascript_service, "setup_git_repository", failure)
    monkeypatch.setattr(interface._javascript_service, "setup_git_hooks", failure)

    result = interface._setup_javascript_project(
        tmp_path,
        "vue",
        install_deps=True,
        setup_dev_tools=True,
        setup_git_hooks=True,
    )

    assert result["tools_configured"] == []
    assert result["warnings"] == [
        "Dependency installation failed",
        "Dev tools setup failed",
        "Git repository setup failed",
        "Git hooks setup failed",
    ]


# ///////////////////////////////////////////////////////////////
# SUPPORT HELPERS
# ///////////////////////////////////////////////////////////////


@pytest.mark.parametrize(
    ("project_type", "language", "variant"),
    [
        ("python", "python", "py"),
        ("javascript", "javascript", "js"),
        ("react", "javascript", "react"),
        ("vue", "javascript", "vue"),
    ],
)
def test_copy_vscode_config_maps_project_variant(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    project_type: str,
    language: str,
    variant: str,
) -> None:
    captured: list[tuple[object, ...]] = []
    monkeypatch.setattr(
        "womm.interfaces.project.setup_interface.copy_asset_type",
        lambda *args, **_kwargs: captured.append(args),
    )

    ProjectSetupInterface()._copy_vscode_config(tmp_path, project_type)

    assert captured == [(language, variant, "vscode", tmp_path / ".vscode")]


@pytest.mark.parametrize(
    ("project_type", "runtime"),
    [
        ("python", "python"),
        ("javascript", "node"),
        ("react", "node"),
        ("vue", "node"),
    ],
)
def test_check_dependencies_probes_expected_runtime(
    monkeypatch: pytest.MonkeyPatch,
    project_type: str,
    runtime: str,
) -> None:
    captured: list[str] = []

    def successful_probe(name: str) -> SimpleNamespace:
        captured.append(name)
        return SimpleNamespace(success=True)

    monkeypatch.setattr(
        "womm.interfaces.project.setup_interface.probe", successful_probe
    )

    error = ProjectSetupInterface()._check_dependencies(project_type)

    assert error == ""
    assert captured == [runtime]


def test_check_dependencies_translates_probe_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_probe(_name: str) -> SimpleNamespace:
        raise OSError("probe unavailable")

    monkeypatch.setattr("womm.interfaces.project.setup_interface.probe", fail_probe)

    error = ProjectSetupInterface()._check_dependencies("python")

    assert error == "Error checking dependencies: probe unavailable"
