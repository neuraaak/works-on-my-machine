#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST PROJECT INTERFACES - Boundary tests for the exception->Result contract
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Boundary tests for the ``interfaces/project`` package.

These verify the exception-rework contract: every public method of
``ProjectDetectionInterface``, ``ProjectCreateInterface``, ``ProjectSetupInterface``,
``TemplateInterface`` and ``ProjectManagerInterface`` translates its
collaborators' outcomes (service exceptions, Result objects) into a typed
Result and never raises. Fake services are injected directly (post-construction,
mirroring the pattern used for ``ContextMenuInterface``) so the tests exercise
only the interface's translation logic.
"""

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
from womm.interfaces.project.detection_interface import ProjectDetectionInterface
from womm.interfaces.project.manager_interface import ProjectManagerInterface
from womm.interfaces.project.setup_interface import ProjectSetupInterface
from womm.interfaces.project.template_interface import TemplateInterface
from womm.shared.results.project_results import (
    ProjectCreationResult,
    ProjectDetectionResult,
    ProjectSetupResult,
)

# ///////////////////////////////////////////////////////////////
# FAKE SERVICES
# ///////////////////////////////////////////////////////////////


class _FakeDetectionService:
    """Stand-in for ProjectDetectionService with scriptable outcomes."""

    def __init__(
        self,
        type_result: ProjectDetectionResult | None = None,
        type_error: Exception | None = None,
        config_result: ProjectDetectionResult | None = None,
        config_error: Exception | None = None,
    ):
        self._type_result = type_result
        self._type_error = type_error
        self._config_result = config_result
        self._config_error = config_error

    def detect_project_type(self, _project_path: Path) -> ProjectDetectionResult:
        if self._type_error:
            raise self._type_error
        return self._type_result or ProjectDetectionResult(
            success=True, project_type="unknown"
        )

    def detect_project_config(self, _project_path: Path) -> ProjectDetectionResult:
        if self._config_error:
            raise self._config_error
        return self._config_result or ProjectDetectionResult(success=True)


# ///////////////////////////////////////////////////////////////
# PROJECT DETECTION INTERFACE
# ///////////////////////////////////////////////////////////////


def test_detect_project_type_success(tmp_path: Path):
    interface = ProjectDetectionInterface()
    interface._detection_service = _FakeDetectionService(
        type_result=ProjectDetectionResult(success=True, project_type="python"),
        config_result=ProjectDetectionResult(
            success=True, detected_files=["pyproject.toml"]
        ),
    )

    result = interface.detect_project_type(tmp_path)

    assert result.success
    assert result.project_type == "python"
    assert result.confidence == 100.0


def test_detect_project_type_does_not_write_to_the_terminal(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    interface = ProjectDetectionInterface()
    interface._detection_service = _FakeDetectionService(
        type_result=ProjectDetectionResult(success=True, project_type="python"),
        config_result=ProjectDetectionResult(success=True),
    )

    interface.detect_project_type(tmp_path)

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_detect_project_type_unknown_has_zero_confidence(tmp_path: Path):
    interface = ProjectDetectionInterface()
    interface._detection_service = _FakeDetectionService(
        type_result=ProjectDetectionResult(success=True, project_type="unknown")
    )

    result = interface.detect_project_type(tmp_path)

    assert result.success
    assert result.project_type == "unknown"
    assert result.confidence == 0.0


def test_detect_project_type_service_error_returns_failed_result_never_raises(
    tmp_path: Path,
):
    interface = ProjectDetectionInterface()
    interface._detection_service = _FakeDetectionService(
        type_error=ProjectServiceError(
            operation="detect_project_type", reason="disk unreadable"
        )
    )

    result = interface.detect_project_type(tmp_path)

    assert not result.success
    assert "disk unreadable" in result.error


def test_detect_project_config_service_error_returns_failed_result(tmp_path: Path):
    interface = ProjectDetectionInterface()
    interface._detection_service = _FakeDetectionService(
        config_error=ProjectServiceError(
            operation="detect_project_config", reason="permission denied"
        )
    )

    result = interface.detect_project_config(tmp_path)

    assert not result.success
    assert "permission denied" in result.error


# ///////////////////////////////////////////////////////////////
# PROJECT CREATE INTERFACE
# ///////////////////////////////////////////////////////////////


def test_create_project_unsupported_type_returns_failed_result(tmp_path: Path):
    interface = ProjectCreateInterface()

    result = interface.create_project(
        project_type="rust",
        project_name="demo",
        project_path=tmp_path / "demo",
    )

    assert isinstance(result, ProjectCreationResult)
    assert not result.success
    assert "Unsupported project type" in result.error


def test_create_project_dry_run_reports_success(tmp_path: Path):
    interface = ProjectCreateInterface()

    result = interface.create_project(
        project_type="python",
        project_name="demo",
        project_path=tmp_path / "demo",
        dry_run=True,
    )

    assert result.success
    assert result.warnings and "Dry-run" in result.warnings[0]


def test_create_project_invalid_name_never_raises(tmp_path: Path):
    interface = ProjectCreateInterface()

    result = interface.create_project(
        project_type="python",
        project_name="",
        project_path=tmp_path / "demo",
    )

    assert not result.success
    assert result.error


# ///////////////////////////////////////////////////////////////
# PROJECT SETUP INTERFACE
# ///////////////////////////////////////////////////////////////


def test_setup_project_undetectable_type_returns_failed_result(tmp_path: Path):
    interface = ProjectSetupInterface()
    interface._detection_service = _FakeDetectionService(
        type_result=ProjectDetectionResult(success=True, project_type="unknown")
    )

    result = interface.setup_project(project_path=tmp_path)

    assert isinstance(result, ProjectSetupResult)
    assert not result.success
    assert "Could not detect project type" in result.error


def test_setup_project_unsupported_type_returns_failed_result(tmp_path: Path):
    interface = ProjectSetupInterface()

    result = interface.setup_project(project_path=tmp_path, project_type="rust")

    assert not result.success
    assert "Unsupported project type" in result.error


# ///////////////////////////////////////////////////////////////
# TEMPLATE INTERFACE
# ///////////////////////////////////////////////////////////////


@pytest.fixture
def template_interface(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "womm.interfaces.project.template_interface.get_womm_installation_path",
        lambda: tmp_path,
    )
    return TemplateInterface()


def test_list_templates_empty_by_default(template_interface: TemplateInterface):
    assert template_interface.list_templates() == {}


def test_get_template_info_missing_returns_none(
    template_interface: TemplateInterface,
):
    assert template_interface.get_template_info("does-not-exist") is None


def test_delete_template_missing_returns_failed_result(
    template_interface: TemplateInterface,
):
    result = template_interface.delete_template("does-not-exist")

    assert not result.success
    assert "not found" in result.error


def test_create_template_from_project_missing_source_returns_failed_result(
    template_interface: TemplateInterface, tmp_path: Path
):
    result = template_interface.create_template_from_project(
        source_project_path=tmp_path / "missing-source",
        template_name="demo-template",
    )

    assert not result.success
    assert "does not exist" in result.error


def test_create_template_from_project_dry_run_reports_success(
    template_interface: TemplateInterface, tmp_path: Path
):
    source = tmp_path / "source-project"
    source.mkdir()

    result = template_interface.create_template_from_project(
        source_project_path=source,
        template_name="demo-template",
        dry_run=True,
    )

    assert result.success


def test_create_template_from_project_duplicate_name_returns_failed_result(
    template_interface: TemplateInterface, tmp_path: Path
):
    source = tmp_path / "source-project"
    source.mkdir()
    (source / "main.py").write_text("print('hi')", encoding="utf-8")

    first = template_interface.create_template_from_project(
        source_project_path=source, template_name="demo-template"
    )
    assert first.success

    second = template_interface.create_template_from_project(
        source_project_path=source, template_name="demo-template"
    )

    assert not second.success
    assert "already exists" in second.error


def test_generate_from_template_missing_template_returns_failed_result(
    template_interface: TemplateInterface, tmp_path: Path
):
    result = template_interface.generate_from_template(
        template_name="does-not-exist", target_path=tmp_path / "out"
    )

    assert not result.success
    assert "not found" in result.error


# ///////////////////////////////////////////////////////////////
# PROJECT MANAGER INTERFACE
# ///////////////////////////////////////////////////////////////


def test_manager_create_project_requires_type():
    manager = ProjectManagerInterface()

    result = manager.create_project(project_type="")

    assert not result.success
    assert "Project type is required" in result.error


def test_manager_create_project_requires_name_without_current_dir():
    manager = ProjectManagerInterface()

    result = manager.create_project(project_type="python")

    assert not result.success
    assert "Project name is required" in result.error


def test_manager_create_project_unsupported_type():
    manager = ProjectManagerInterface()

    result = manager.create_project(project_type="rust", project_name="demo")

    assert not result.success
    assert "Unsupported project type" in result.error
