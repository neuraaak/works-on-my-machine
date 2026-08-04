#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST PROJECT MANAGER INTERFACE - Orchestration facade coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Direct tests for ProjectManagerInterface, the project orchestration facade.

``create_project`` was removed from this facade: it predated the Copier
migration (Task 6/7) and its JavaScript type-mapping logic (``js`` -> ``node``,
``react-ts`` -> ``react``, ...) was exactly the kind of language/framework
mapping that must not live in Python code. Project creation now goes through
``ProjectCreateInterface`` directly (see ``commands/project/create.py``), which
this facade never wrapped correctly after Task 6 changed its signature.
"""

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
    ProjectDetectionResult,
    ProjectSetupResult,
)

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
