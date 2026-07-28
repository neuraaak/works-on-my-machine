#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST PROJECT DETECTION SERVICE - Direct project service coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Direct tests for project type, configuration, and structure detection."""

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
from womm.services.project.detection_service import ProjectDetectionService

# ///////////////////////////////////////////////////////////////
# PROJECT TYPE DETECTION
# ///////////////////////////////////////////////////////////////


@pytest.mark.parametrize(
    ("marker", "project_type"),
    [
        ("pyproject.toml", "python"),
        ("package.json", "javascript"),
        ("pom.xml", "java"),
        ("go.mod", "go"),
        ("Cargo.toml", "rust"),
        ("demo.csproj", "csharp"),
    ],
)
def test_detect_project_type_from_marker_file(
    tmp_path: Path, marker: str, project_type: str
) -> None:
    (tmp_path / marker).touch()

    result = ProjectDetectionService().detect_project_type(tmp_path)

    assert result.success
    assert result.project_type == project_type
    assert result.confidence == 100.0
    assert result.detected_files is not None
    assert marker in result.detected_files


def test_detect_project_type_from_source_extension(tmp_path: Path) -> None:
    (tmp_path / "main.go").touch()

    result = ProjectDetectionService().detect_project_type(tmp_path)

    assert result.project_type == "go"
    assert result.detected_files == [".go"]


def test_detect_project_type_from_indicator_directory(tmp_path: Path) -> None:
    (tmp_path / "node_modules").mkdir()

    result = ProjectDetectionService().detect_project_type(tmp_path)

    assert result.project_type == "javascript"
    assert result.detected_files == ["node_modules"]


def test_detect_project_type_uses_declared_precedence_for_mixed_project(
    tmp_path: Path,
) -> None:
    (tmp_path / "pyproject.toml").touch()
    (tmp_path / "package.json").touch()

    result = ProjectDetectionService().detect_project_type(tmp_path)

    assert result.project_type == "python"
    assert result.detected_files == ["pyproject.toml"]


def test_detect_project_type_returns_unknown_for_empty_directory(
    tmp_path: Path,
) -> None:
    result = ProjectDetectionService().detect_project_type(tmp_path)

    assert result.success
    assert result.project_type == "unknown"
    assert result.confidence == 0.0
    assert result.detected_files == []


def test_detect_project_type_rejects_missing_path(tmp_path: Path) -> None:
    with pytest.raises(ProjectServiceError) as excinfo:
        ProjectDetectionService().detect_project_type(tmp_path / "missing")

    assert excinfo.value.reason == "Project path does not exist"


def test_detect_project_type_rejects_regular_file(tmp_path: Path) -> None:
    source = tmp_path / "main.py"
    source.touch()

    with pytest.raises(ProjectServiceError) as excinfo:
        ProjectDetectionService().detect_project_type(source)

    assert excinfo.value.reason == "Project path is not a directory"


def test_detect_project_type_wraps_directory_access_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def deny_access(_path: Path):
        raise PermissionError("access denied")

    monkeypatch.setattr(Path, "iterdir", deny_access)

    with pytest.raises(ProjectServiceError) as excinfo:
        ProjectDetectionService().detect_project_type(tmp_path)

    assert excinfo.value.reason == "access denied"
    assert isinstance(excinfo.value.__cause__, PermissionError)


# ///////////////////////////////////////////////////////////////
# CONFIGURATION DETECTION
# ///////////////////////////////////////////////////////////////


def test_detect_python_config_returns_markers_and_details(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").touch()
    virtual_env = tmp_path / ".venv"
    virtual_env.mkdir()

    result = ProjectDetectionService().detect_project_config(tmp_path)

    assert result.success
    assert result.project_type == "python"
    assert result.confidence == 100.0
    assert result.configuration_files == {
        "pyproject_toml": "found",
        "venv": str(virtual_env),
    }


def test_detect_csharp_config_supports_solution_glob(tmp_path: Path) -> None:
    (tmp_path / "demo.sln").touch()

    result = ProjectDetectionService().detect_project_config(tmp_path)

    assert result.project_type == "csharp"
    assert result.configuration_files == {"sln": "found"}


def test_detect_unknown_config_has_zero_confidence(tmp_path: Path) -> None:
    result = ProjectDetectionService().detect_project_config(tmp_path)

    assert result.success
    assert result.project_type == "unknown"
    assert result.confidence == 0.0
    assert result.configuration_files == {}


def test_detect_config_keeps_partial_result_when_analyzer_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "pyproject.toml").touch()

    def fail_analysis(_path: Path):
        raise ValueError("invalid configuration")

    monkeypatch.setattr(
        "womm.services.project.detection_service.analyze_python_config",
        fail_analysis,
    )

    result = ProjectDetectionService().detect_project_config(tmp_path)

    assert result.success
    assert result.project_type == "python"
    assert result.configuration_files == {}


# ///////////////////////////////////////////////////////////////
# STRUCTURE DETECTION
# ///////////////////////////////////////////////////////////////


def test_detect_project_structure_categorizes_directories_and_counts(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "src"
    test_dir = tmp_path / "tests"
    config_dir = tmp_path / "config"
    build_dir = tmp_path / "dist"
    docs_dir = tmp_path / "docs"
    for directory in (source_dir, test_dir, config_dir, build_dir, docs_dir):
        directory.mkdir()
    (source_dir / "main.py").touch()
    (test_dir / "test_main.py").touch()

    result = ProjectDetectionService().detect_project_structure(tmp_path)

    assert result.success
    assert result.configuration_files is not None
    structure = result.configuration_files
    assert structure["source_dirs"] == str(source_dir)
    assert structure["test_dirs"] == str(test_dir)
    assert structure["config_dirs"] == str(config_dir)
    assert structure["build_dirs"] == str(build_dir)
    assert structure["documentation_dirs"] == str(docs_dir)
    assert structure["total_files"] == "2"
    assert structure["total_dirs"] == "5"


def test_detect_project_structure_returns_partial_result_on_access_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def deny_access(_path: Path, _pattern: str):
        raise PermissionError("structure unavailable")

    monkeypatch.setattr(Path, "rglob", deny_access)

    result = ProjectDetectionService().detect_project_structure(tmp_path)

    assert result.success
    assert result.configuration_files is not None
    assert result.configuration_files["total_files"] == "0"
    assert result.configuration_files["total_dirs"] == "0"
