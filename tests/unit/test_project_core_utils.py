#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST PROJECT CORE UTILS - Detection, structure, and config coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Direct tests for project detection, structure, and config file utilities."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
from pathlib import Path

# Local imports
from womm.utils.project import core_utils

# ///////////////////////////////////////////////////////////////
# MATCHES PROJECT TYPE
# ///////////////////////////////////////////////////////////////


def test_matches_project_type_true_when_markers_present() -> None:
    assert core_utils.matches_project_type({"python": ["pyproject.toml"]}, "python")


def test_matches_project_type_false_when_markers_absent() -> None:
    assert not core_utils.matches_project_type({"python": []}, "python")
    assert not core_utils.matches_project_type({}, "rust")


# ///////////////////////////////////////////////////////////////
# CATEGORIZE DIRECTORY
# ///////////////////////////////////////////////////////////////


def test_categorize_directory_returns_unknown_for_non_directory(
    tmp_path: Path,
) -> None:
    assert core_utils.categorize_directory(tmp_path / "missing") == "unknown"


def test_categorize_directory_detects_javascript(tmp_path: Path) -> None:
    (tmp_path / "package.json").touch()
    assert core_utils.categorize_directory(tmp_path) == "javascript"


def test_categorize_directory_detects_java(tmp_path: Path) -> None:
    (tmp_path / "pom.xml").touch()
    assert core_utils.categorize_directory(tmp_path) == "java"


def test_categorize_directory_detects_git_repo(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    assert core_utils.categorize_directory(tmp_path) == "git_repo"


def test_categorize_directory_falls_back_to_generic(tmp_path: Path) -> None:
    assert core_utils.categorize_directory(tmp_path) == "generic"


# ///////////////////////////////////////////////////////////////
# ANALYZE PYTHON CONFIG
# ///////////////////////////////////////////////////////////////


def test_analyze_python_config_detects_markers_and_venv(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").touch()
    (tmp_path / "requirements.txt").touch()
    (tmp_path / ".venv").mkdir()

    config = core_utils.analyze_python_config(tmp_path)

    assert config["markers"] == {
        "pyproject_toml": "found",
        "requirements_txt": "found",
    }
    assert config["details"] == {"venv": str(tmp_path / ".venv")}


def test_analyze_python_config_empty_when_nothing_present(tmp_path: Path) -> None:
    config = core_utils.analyze_python_config(tmp_path)

    assert config == {"markers": {}, "details": {}}


# ///////////////////////////////////////////////////////////////
# ANALYZE JAVASCRIPT CONFIG
# ///////////////////////////////////////////////////////////////


def test_analyze_javascript_config_detects_markers(tmp_path: Path) -> None:
    (tmp_path / "package.json").touch()
    (tmp_path / "yarn.lock").touch()
    (tmp_path / "node_modules").mkdir()

    config = core_utils.analyze_javascript_config(tmp_path)

    assert config["markers"] == {"package_json": "found", "yarn_lock": "found"}
    assert config["details"] == {"node_modules": "present"}


# ///////////////////////////////////////////////////////////////
# ANALYZE JAVA / GO / RUST / CSHARP CONFIG
# ///////////////////////////////////////////////////////////////


def test_analyze_java_config_detects_all_markers(tmp_path: Path) -> None:
    (tmp_path / "pom.xml").touch()
    (tmp_path / "build.gradle").touch()
    (tmp_path / "build.sbt").touch()

    config = core_utils.analyze_java_config(tmp_path)

    assert config["markers"] == {
        "pom_xml": "found",
        "gradle": "found",
        "sbt": "found",
    }


def test_analyze_go_config_detects_markers(tmp_path: Path) -> None:
    (tmp_path / "go.mod").touch()
    (tmp_path / "go.sum").touch()

    assert core_utils.analyze_go_config(tmp_path)["markers"] == {
        "go_mod": "found",
        "go_sum": "found",
    }


def test_analyze_rust_config_detects_markers(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").touch()

    assert core_utils.analyze_rust_config(tmp_path)["markers"] == {
        "cargo_toml": "found"
    }


def test_analyze_csharp_config_detects_csproj_and_sln(tmp_path: Path) -> None:
    (tmp_path / "demo.csproj").touch()
    (tmp_path / "demo.sln").touch()

    assert core_utils.analyze_csharp_config(tmp_path)["markers"] == {
        "csproj": "found",
        "sln": "found",
    }


def test_analyze_csharp_config_empty_without_project_files(tmp_path: Path) -> None:
    assert core_utils.analyze_csharp_config(tmp_path) == {
        "markers": {},
        "details": {},
    }


# ///////////////////////////////////////////////////////////////
# STRUCTURE CREATION
# ///////////////////////////////////////////////////////////////


def test_create_common_structure_creates_expected_directories(
    tmp_path: Path,
) -> None:
    created = core_utils.create_common_structure(tmp_path, "demo")

    assert set(created) == {
        str(tmp_path / "src"),
        str(tmp_path / "tests"),
        str(tmp_path / "docs"),
        str(tmp_path / ".github"),
    }
    for directory in created:
        assert Path(directory).is_dir()


def test_create_python_structure_adds_package_dir_without_duplicates(
    tmp_path: Path,
) -> None:
    created = core_utils.create_python_structure(tmp_path, "demo")

    assert (tmp_path / "demo").is_dir()
    assert (tmp_path / "tests").is_dir()
    assert (tmp_path / "src").is_dir()
    assert len(created) == len(set(created))
    assert str(tmp_path / "src") in created
    assert str(tmp_path / "demo") in created


def test_create_javascript_structure_adds_js_dirs_without_duplicates(
    tmp_path: Path,
) -> None:
    created = core_utils.create_javascript_structure(tmp_path, "demo")

    assert (tmp_path / "src" / "components").is_dir()
    assert (tmp_path / "src" / "utils").is_dir()
    assert (tmp_path / "public").is_dir()
    assert len(created) == len(set(created))


# ///////////////////////////////////////////////////////////////
# CONFIG FILE CREATION
# ///////////////////////////////////////////////////////////////


def test_create_python_requirements_files_creates_both_files(
    tmp_path: Path,
) -> None:
    created = core_utils.create_python_requirements_files(tmp_path)

    assert (tmp_path / "requirements.txt").is_file()
    assert (tmp_path / "requirements-dev.txt").is_file()
    assert created == [
        str(tmp_path / "requirements.txt"),
        str(tmp_path / "requirements-dev.txt"),
    ]


def test_create_python_dev_config_files_creates_pyproject_when_missing(
    tmp_path: Path,
) -> None:
    created = core_utils.create_python_dev_config_files(tmp_path)

    assert (tmp_path / "pyproject.toml").is_file()
    assert created == [str(tmp_path / "pyproject.toml")]


def test_create_python_dev_config_files_skips_existing_pyproject(
    tmp_path: Path,
) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\n")

    created = core_utils.create_python_dev_config_files(tmp_path)

    assert created == []
    assert (tmp_path / "pyproject.toml").read_text() == "[project]\n"


def test_create_javascript_config_files_creates_package_json_and_gitignore(
    tmp_path: Path,
) -> None:
    created = core_utils.create_javascript_config_files(tmp_path)

    package_json = json.loads((tmp_path / "package.json").read_text())
    assert package_json == {"name": "", "version": "1.0.0"}
    assert "node_modules/" in (tmp_path / ".gitignore").read_text()
    assert len(created) == 2


def test_create_javascript_config_files_skips_existing_files(
    tmp_path: Path,
) -> None:
    (tmp_path / "package.json").write_text("{}")
    (tmp_path / ".gitignore").write_text("custom\n")

    created = core_utils.create_javascript_config_files(tmp_path)

    assert created == []
    assert (tmp_path / "package.json").read_text() == "{}"
    assert (tmp_path / ".gitignore").read_text() == "custom\n"
