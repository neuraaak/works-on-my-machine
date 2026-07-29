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
import inspect
from pathlib import Path
from types import ModuleType

# Third-party imports
import pytest
from click.testing import CliRunner

# Local imports
import womm.interfaces.project.create_interface as create_interface_module
import womm.interfaces.project.setup_interface as setup_interface_module
from womm.commands.project.create import create_group
from womm.commands.project.setup import setup_group
from womm.exceptions.project import ProjectServiceError
from womm.interfaces.project.create_interface import ProjectCreateInterface
from womm.interfaces.project.detection_interface import ProjectDetectionInterface
from womm.interfaces.project.manager_interface import ProjectManagerInterface
from womm.interfaces.project.setup_interface import ProjectSetupInterface
from womm.interfaces.project.template_interface import TemplateInterface
from womm.shared.paths import WOMM_HOME_ENV, user_templates_dir
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


class _FakeProjectManager:
    """Command-boundary fake that records project creation options."""

    instances: list[_FakeProjectManager] = []

    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
        self.instances.append(self)

    def create_project(self, **kwargs: object) -> ProjectCreationResult:
        self.calls.append(kwargs)
        project_name = str(kwargs["project_name"])
        target = Path(str(kwargs.get("target", ".")))
        return ProjectCreationResult(
            success=True,
            project_path=target / project_name,
            project_name=project_name,
            project_type=str(kwargs["project_type"]),
        )

    def setup_project(self, **kwargs: object) -> ProjectSetupResult:
        self.calls.append(kwargs)
        project_path = Path(str(kwargs["project_path"]))
        return ProjectSetupResult(
            success=True,
            project_path=project_path,
            project_name=project_path.name,
            project_type=str(kwargs["project_type"]),
        )


def _inject_detection_service(
    interface: ProjectDetectionInterface | ProjectSetupInterface,
    service: _FakeDetectionService,
) -> None:
    """Install a test double without weakening production attribute types."""
    object.__setattr__(interface, "_detection_service", service)


# ///////////////////////////////////////////////////////////////
# ZERO-UI CONTRACT
# ///////////////////////////////////////////////////////////////


@pytest.mark.parametrize(
    "interface_module",
    [create_interface_module, setup_interface_module],
)
def test_create_and_setup_interfaces_never_import_ui(interface_module: ModuleType):
    """Terminal rendering belongs to commands, not project interfaces."""
    source = inspect.getsource(interface_module)

    assert "ui.project" not in source
    assert "ui.common" not in source
    assert "ezprinter" not in source
    assert "ezconsole" not in source


# ///////////////////////////////////////////////////////////////
# PROJECT DETECTION INTERFACE
# ///////////////////////////////////////////////////////////////


def test_detect_project_type_success(tmp_path: Path):
    interface = ProjectDetectionInterface()
    _inject_detection_service(
        interface,
        _FakeDetectionService(
            type_result=ProjectDetectionResult(success=True, project_type="python"),
            config_result=ProjectDetectionResult(
                success=True, detected_files=["pyproject.toml"]
            ),
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
    _inject_detection_service(
        interface,
        _FakeDetectionService(
            type_result=ProjectDetectionResult(success=True, project_type="python"),
            config_result=ProjectDetectionResult(success=True),
        ),
    )

    interface.detect_project_type(tmp_path)

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_detect_project_type_unknown_has_zero_confidence(tmp_path: Path):
    interface = ProjectDetectionInterface()
    _inject_detection_service(
        interface,
        _FakeDetectionService(
            type_result=ProjectDetectionResult(success=True, project_type="unknown")
        ),
    )

    result = interface.detect_project_type(tmp_path)

    assert result.success
    assert result.project_type == "unknown"
    assert result.confidence == 0.0


def test_detect_project_type_service_error_returns_failed_result_never_raises(
    tmp_path: Path,
):
    interface = ProjectDetectionInterface()
    _inject_detection_service(
        interface,
        _FakeDetectionService(
            type_error=ProjectServiceError(
                operation="detect_project_type", reason="disk unreadable"
            )
        ),
    )

    result = interface.detect_project_type(tmp_path)

    assert not result.success
    assert "disk unreadable" in result.error


def test_detect_project_config_service_error_returns_failed_result(tmp_path: Path):
    interface = ProjectDetectionInterface()
    _inject_detection_service(
        interface,
        _FakeDetectionService(
            config_error=ProjectServiceError(
                operation="detect_project_config", reason="permission denied"
            )
        ),
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


def test_create_project_does_not_write_to_the_terminal(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    interface = ProjectCreateInterface()

    interface.create_project(
        project_type="python",
        project_name="demo",
        project_path=tmp_path / "demo",
        dry_run=True,
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_create_project_invalid_name_never_raises(tmp_path: Path):
    interface = ProjectCreateInterface()

    result = interface.create_project(
        project_type="python",
        project_name="",
        project_path=tmp_path / "demo",
    )

    assert not result.success
    assert result.error


@pytest.mark.parametrize("command", ["python", "javascript"])
def test_create_minimal_command_forwards_minimal_mode(
    command: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    _FakeProjectManager.instances.clear()
    monkeypatch.setattr(
        "womm.commands.project.create.ProjectManagerInterface", _FakeProjectManager
    )

    result = CliRunner().invoke(
        create_group,
        [command, "demo", "--minimal", "--target", str(tmp_path)],
    )

    assert result.exit_code == 0, result.output
    assert _FakeProjectManager.instances[0].calls[0]["minimal"] is True


# ///////////////////////////////////////////////////////////////
# PROJECT SETUP INTERFACE
# ///////////////////////////////////////////////////////////////


def test_setup_project_undetectable_type_returns_failed_result(tmp_path: Path):
    interface = ProjectSetupInterface()
    _inject_detection_service(
        interface,
        _FakeDetectionService(
            type_result=ProjectDetectionResult(success=True, project_type="unknown")
        ),
    )

    result = interface.setup_project(project_path=tmp_path)

    assert isinstance(result, ProjectSetupResult)
    assert not result.success
    assert "Could not detect project type" in result.error


def test_setup_project_does_not_write_to_the_terminal(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
):
    interface = ProjectSetupInterface()
    monkeypatch.setattr(interface, "_copy_vscode_config", lambda *_args: None)

    result = interface.setup_project(project_path=tmp_path, project_type="python")

    assert result.success
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_setup_python_command_renders_a_successful_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    _FakeProjectManager.instances.clear()
    monkeypatch.setattr(
        "womm.commands.project.setup.ProjectManagerInterface", _FakeProjectManager
    )

    result = CliRunner().invoke(setup_group, ["python", "--path", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert _FakeProjectManager.instances[0].calls[0]["project_type"] == "python"


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
    monkeypatch.setenv(WOMM_HOME_ENV, str(tmp_path))
    return TemplateInterface()


def test_templates_live_in_the_data_directory(
    template_interface: TemplateInterface, tmp_path: Path
):
    """User templates are data: they follow ``~/.womm``, not the code."""
    assert template_interface._templates_dir == tmp_path / "templates"
    assert template_interface._templates_dir == user_templates_dir()


def test_templates_dir_exists_after_construction(
    template_interface: TemplateInterface,
):
    assert template_interface._templates_dir.is_dir()


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
