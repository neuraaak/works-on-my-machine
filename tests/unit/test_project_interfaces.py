#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST PROJECT INTERFACES - Boundary tests for the exception->Result contract
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Boundary tests for the ``interfaces/project`` package.

These verify the exception-rework contract: every public method of
``ProjectDetectionInterface``, ``ProjectCreateInterface``, ``ProjectSetupInterface``
and ``ProjectManagerInterface`` translates its collaborators' outcomes (service
exceptions, Result objects) into a typed Result and never raises. Fake services
are injected directly (post-construction, mirroring the pattern used for
``ContextMenuInterface``) so the tests exercise only the interface's
translation logic.
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
from womm.commands.project.setup import setup_group
from womm.exceptions.project import ProjectServiceError
from womm.interfaces.project.detection_interface import ProjectDetectionInterface
from womm.interfaces.project.setup_interface import ProjectSetupInterface
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
# PROJECT MANAGER INTERFACE
# ///////////////////////////////////////////////////////////////
#
# ``ProjectManagerInterface.create_project`` was removed (see
# test_project_manager_interface.py for the rationale): it was dead code,
# unreachable from any live CLI entry point, and its JavaScript type-mapping
# logic violated the "no language/framework mapping in Python code" rule
# enforced by the Copier migration.
