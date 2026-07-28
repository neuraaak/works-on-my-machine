#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST PROJECT MANAGER INTERFACE - Orchestration facade coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Direct tests for ProjectManagerInterface, the project orchestration facade."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path
from typing import Any

# Third-party imports
import pytest

# Local imports
from womm.interfaces.project.manager_interface import ProjectManagerInterface
from womm.shared.results import (
    ProjectCreationResult,
    ProjectDetectionResult,
    ProjectSetupResult,
)
from womm.utils.dependencies.probe import ProbeResult

# ///////////////////////////////////////////////////////////////
# FIXTURES
# ///////////////////////////////////////////////////////////////


@pytest.fixture(autouse=True)
def _available_runtimes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the dependency probe deterministic regardless of the host machine."""
    monkeypatch.setattr(
        "womm.interfaces.project.manager_interface.probe",
        lambda name: ProbeResult(name=name, available=True),
    )


# ///////////////////////////////////////////////////////////////
# CREATE PROJECT — PATH RESOLUTION
# ///////////////////////////////////////////////////////////////


def test_create_project_uses_current_directory_when_requested(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    manager = ProjectManagerInterface()
    captured: dict[str, Any] = {}
    monkeypatch.setattr(
        manager._create_interface,
        "create_project",
        lambda **kwargs: captured.update(kwargs) or ProjectCreationResult(success=True),
    )

    manager.create_project(project_type="python", current_dir=True)

    assert captured["project_path"] == tmp_path
    assert captured["project_name"] == tmp_path.name


def test_create_project_uses_target_and_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = ProjectManagerInterface()
    captured: dict[str, Any] = {}
    monkeypatch.setattr(
        manager._create_interface,
        "create_project",
        lambda **kwargs: captured.update(kwargs) or ProjectCreationResult(success=True),
    )

    manager.create_project(
        project_type="python", project_name="demo", target=str(tmp_path)
    )

    assert captured["project_path"] == tmp_path / "demo"
    assert captured["project_name"] == "demo"


def test_create_project_target_without_name_is_rejected(tmp_path: Path) -> None:
    manager = ProjectManagerInterface()

    result = manager.create_project(project_type="python", target=str(tmp_path))

    assert not result.success
    assert "Project name is required when using target directory" in result.error


def test_create_project_uses_cwd_and_name_by_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    manager = ProjectManagerInterface()
    captured: dict[str, Any] = {}
    monkeypatch.setattr(
        manager._create_interface,
        "create_project",
        lambda **kwargs: captured.update(kwargs) or ProjectCreationResult(success=True),
    )

    manager.create_project(project_type="python", project_name="demo")

    assert captured["project_path"] == tmp_path / "demo"


# ///////////////////////////////////////////////////////////////
# CREATE PROJECT — DRY RUN
# ///////////////////////////////////////////////////////////////


def test_create_project_dry_run_does_not_delegate_to_create_interface(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager = ProjectManagerInterface()

    def fail(**_kwargs: Any) -> ProjectCreationResult:
        raise AssertionError("create_interface must not run in dry-run mode")

    monkeypatch.setattr(manager._create_interface, "create_project", fail)

    result = manager.create_project(
        project_type="python", project_name="demo", dry_run=True
    )

    assert result.success
    assert "Dry-run mode: no actual changes were made" in result.warnings


# ///////////////////////////////////////////////////////////////
# CREATE PROJECT — JAVASCRIPT TYPE MAPPING
# ///////////////////////////////////////////////////////////////


@pytest.mark.parametrize(
    ("js_type_option", "expected_project_type"),
    [
        ("js", "node"),
        ("ts", "node"),
        ("react", "react"),
        ("vue", "vue"),
        ("react-ts", "react"),
        ("vue-ts", "vue"),
        ("node", "node"),
        ("unknown", "node"),
    ],
)
def test_create_project_maps_javascript_type_option(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    js_type_option: str,
    expected_project_type: str,
) -> None:
    manager = ProjectManagerInterface()
    captured: dict[str, Any] = {}
    monkeypatch.setattr(
        manager._create_interface,
        "create_project",
        lambda **kwargs: captured.update(kwargs) or ProjectCreationResult(success=True),
    )

    manager.create_project(
        project_type="javascript",
        project_name="demo",
        target=str(tmp_path),
        type=js_type_option,
    )

    assert captured["project_type"] == expected_project_type


# ///////////////////////////////////////////////////////////////
# CREATE PROJECT — DEPENDENCY CHECK
# ///////////////////////////////////////////////////////////////


def test_create_project_reports_missing_python_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = ProjectManagerInterface()
    monkeypatch.setattr(
        "womm.interfaces.project.manager_interface.probe",
        lambda _name: ProbeResult(name="python", available=False),
    )

    def fail(**_kwargs: Any) -> ProjectCreationResult:
        raise AssertionError("create_interface must not run when deps are missing")

    monkeypatch.setattr(manager._create_interface, "create_project", fail)

    result = manager.create_project(
        project_type="python", project_name="demo", target=str(tmp_path)
    )

    assert not result.success
    assert "Python runtime not found" in result.error


def test_create_project_reports_missing_node_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = ProjectManagerInterface()
    monkeypatch.setattr(
        "womm.interfaces.project.manager_interface.probe",
        lambda _name: ProbeResult(name="node", available=False),
    )

    result = manager.create_project(
        project_type="javascript", project_name="demo", target=str(tmp_path)
    )

    assert not result.success
    assert "Node.js runtime not found" in result.error


# ///////////////////////////////////////////////////////////////
# DELEGATION TO SUB-INTERFACES
# ///////////////////////////////////////////////////////////////


def test_detect_project_type_delegates_to_detection_interface(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = ProjectManagerInterface()
    expected = ProjectDetectionResult(success=True, project_type="python")
    captured: dict[str, Any] = {}
    monkeypatch.setattr(
        manager._detection_interface,
        "detect_project_type",
        lambda project_path=None: (
            captured.update(project_path=project_path) or expected
        ),
    )

    result = manager.detect_project_type(tmp_path)

    assert result is expected
    assert captured["project_path"] == tmp_path


def test_setup_development_environment_delegates_to_setup_interface(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = ProjectManagerInterface()
    expected = ProjectSetupResult(success=True)
    captured: dict[str, Any] = {}
    monkeypatch.setattr(
        manager._setup_interface,
        "setup_development_environment",
        lambda project_path, project_type: (
            captured.update(project_path=project_path, project_type=project_type)
            or expected
        ),
    )

    result = manager.setup_development_environment(tmp_path, "python")

    assert result is expected
    assert captured == {"project_path": tmp_path, "project_type": "python"}


def test_setup_project_delegates_to_setup_interface(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = ProjectManagerInterface()
    expected = ProjectSetupResult(success=True)
    captured: dict[str, Any] = {}
    monkeypatch.setattr(
        manager._setup_interface,
        "setup_project",
        lambda **kwargs: captured.update(kwargs) or expected,
    )

    result = manager.setup_project(
        project_type="python",
        project_path=tmp_path,
        virtual_env=True,
        install_deps=True,
    )

    assert result is expected
    assert captured["project_type"] == "python"
    assert captured["project_path"] == tmp_path
    assert captured["virtual_env"] is True
    assert captured["install_deps"] is True


# ///////////////////////////////////////////////////////////////
# PROJECT TYPES AND TEMPLATES
# ///////////////////////////////////////////////////////////////


def test_get_available_project_types_returns_configured_types() -> None:
    manager = ProjectManagerInterface()

    types = manager.get_available_project_types()

    assert ("python", "Python") in types or any(t[0] == "python" for t in types)
    assert all(isinstance(entry, tuple) and len(entry) == 2 for entry in types)


def test_get_project_templates_filters_by_project_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager = ProjectManagerInterface()
    monkeypatch.setattr(
        manager.template_manager,
        "list_templates",
        lambda: {"python": ["basic", "fastapi"], "javascript": ["react"]},
    )

    assert manager.get_project_templates("python") == ["basic", "fastapi"]
    assert manager.get_project_templates("rust") == []
