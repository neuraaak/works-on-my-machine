#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT CORE UTILS - Core Project Functionality
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Core project utilities - consolidated project detection and discovery utilities.

Merged from:
- project_detection_utils.py
- project_structure_utils.py
- project_config_utils.py

Provides core functionality for:
- Detecting project types and configurations
- Creating project structures
- Creating configuration files
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
import logging
from pathlib import Path

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# PROJECT DETECTION & ANALYSIS
# ///////////////////////////////////////////////////////////////


def matches_project_type(config_files: dict[str, list[str]], project_type: str) -> bool:
    """
    Check if configuration files match a project type.

    Args:
        config_files: Dict mapping project types to their marker files
        project_type: Type to check for

    Returns:
        True if project type markers found, False otherwise
    """
    return bool(config_files.get(project_type, []))


def categorize_directory(path: Path) -> str:
    """
    Categorize a directory based on its contents.

    Args:
        path: Directory path to categorize

    Returns:
        Directory category string
    """
    if not path.is_dir():
        return "unknown"

    # Check for specific indicators
    if (path / "package.json").exists():
        return "javascript"
    if (path / "pyproject.toml").exists() or (path / "setup.py").exists():
        return "python"
    if (path / "pom.xml").exists():
        return "java"
    if (path / ".git").exists():
        return "git_repo"

    return "generic"


def analyze_python_config(project_path: Path) -> dict[str, dict[str, str]]:
    """
    Analyze Python project configuration.

    Args:
        project_path: Path to Python project

    Returns:
        Dictionary with Python configuration details
    """
    config = {"markers": {}, "details": {}}

    # Check for configuration files
    if (project_path / "pyproject.toml").exists():
        config["markers"]["pyproject_toml"] = "found"

    if (project_path / "setup.py").exists():
        config["markers"]["setup_py"] = "found"

    if (project_path / "requirements.txt").exists():
        config["markers"]["requirements_txt"] = "found"

    if (project_path / ".venv").exists():
        config["details"]["venv"] = str(project_path / ".venv")

    return config


def analyze_javascript_config(
    project_path: Path,
) -> dict[str, dict[str, str]]:
    """
    Analyze JavaScript project configuration.

    Args:
        project_path: Path to JavaScript project

    Returns:
        Dictionary with JavaScript configuration details
    """
    config = {"markers": {}, "details": {}}

    if (project_path / "package.json").exists():
        config["markers"]["package_json"] = "found"

    if (project_path / "package-lock.json").exists():
        config["markers"]["package_lock"] = "found"

    if (project_path / "yarn.lock").exists():
        config["markers"]["yarn_lock"] = "found"

    if (project_path / "node_modules").exists():
        config["details"]["node_modules"] = "present"

    return config


def analyze_java_config(project_path: Path) -> dict[str, dict[str, str]]:
    """
    Analyze Java project configuration.

    Args:
        project_path: Path to Java project

    Returns:
        Dictionary with Java configuration details
    """
    config = {"markers": {}, "details": {}}

    if (project_path / "pom.xml").exists():
        config["markers"]["pom_xml"] = "found"

    if (project_path / "build.gradle").exists():
        config["markers"]["gradle"] = "found"

    if (project_path / "build.sbt").exists():
        config["markers"]["sbt"] = "found"

    return config


def analyze_go_config(project_path: Path) -> dict[str, dict[str, str]]:
    """
    Analyze Go project configuration.

    Args:
        project_path: Path to Go project

    Returns:
        Dictionary with Go configuration details
    """
    config = {"markers": {}, "details": {}}

    if (project_path / "go.mod").exists():
        config["markers"]["go_mod"] = "found"

    if (project_path / "go.sum").exists():
        config["markers"]["go_sum"] = "found"

    return config


def analyze_rust_config(project_path: Path) -> dict[str, dict[str, str]]:
    """
    Analyze Rust project configuration.

    Args:
        project_path: Path to Rust project

    Returns:
        Dictionary with Rust configuration details
    """
    config = {"markers": {}, "details": {}}

    if (project_path / "Cargo.toml").exists():
        config["markers"]["cargo_toml"] = "found"

    if (project_path / "Cargo.lock").exists():
        config["markers"]["cargo_lock"] = "found"

    return config


def analyze_csharp_config(project_path: Path) -> dict[str, dict[str, str]]:
    """
    Analyze C# project configuration.

    Args:
        project_path: Path to C# project

    Returns:
        Dictionary with C# configuration details
    """
    config = {"markers": {}, "details": {}}

    # Check for .csproj files
    csproj_files = list(project_path.glob("*.csproj"))
    if csproj_files:
        config["markers"]["csproj"] = "found"

    # Check for .sln files
    sln_files = list(project_path.glob("*.sln"))
    if sln_files:
        config["markers"]["sln"] = "found"

    return config


# ///////////////////////////////////////////////////////////////
# PROJECT STRUCTURE CREATION
# ///////////////////////////////////////////////////////////////


def create_common_structure(project_path: Path, _project_name: str) -> list[str]:
    """
    Create common project structure.

    Args:
        project_path: Path where project will be created
        project_name: Name of the project

    Returns:
        List of created directories
    """
    created = []

    common_dirs = [
        project_path / "src",
        project_path / "tests",
        project_path / "docs",
        project_path / ".github",
    ]

    for dir_path in common_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        created.append(str(dir_path))
        logger.debug(f"Created directory: {dir_path}")

    return created


def create_python_structure(project_path: Path, project_name: str) -> list[str]:
    """
    Create Python-specific project structure.

    Args:
        project_path: Path where project will be created
        project_name: Name of the project

    Returns:
        List of created directories
    """
    created = list(create_common_structure(project_path, project_name))

    python_dirs = [
        project_path / project_name,
        project_path / "tests",
        project_path / "src",
    ]

    for dir_path in python_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        if dir_path not in [Path(p) for p in created]:
            created.append(str(dir_path))
            logger.debug(f"Created Python directory: {dir_path}")

    return created


def create_javascript_structure(project_path: Path, project_name: str) -> list[str]:
    """
    Create JavaScript-specific project structure.

    Args:
        project_path: Path where project will be created
        project_name: Name of the project

    Returns:
        List of created directories
    """
    created = list(create_common_structure(project_path, project_name))

    js_dirs = [
        project_path / "src",
        project_path / "src" / "components",
        project_path / "src" / "utils",
        project_path / "tests",
        project_path / "public",
    ]

    for dir_path in js_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        if dir_path not in [Path(p) for p in created]:
            created.append(str(dir_path))
            logger.debug(f"Created JavaScript directory: {dir_path}")

    return created


# ///////////////////////////////////////////////////////////////
# PROJECT CONFIGURATION FILE CREATION
# ///////////////////////////////////////////////////////////////


def create_python_requirements_files(project_path: Path) -> list[str]:
    """
    Create Python requirements files.

    Args:
        project_path: Path to Python project

    Returns:
        List of created files
    """
    created = []

    requirements_txt = project_path / "requirements.txt"
    requirements_txt.touch()
    created.append(str(requirements_txt))

    requirements_dev_txt = project_path / "requirements-dev.txt"
    requirements_dev_txt.touch()
    created.append(str(requirements_dev_txt))

    return created


def create_python_dev_config_files(project_path: Path) -> list[str]:
    """
    Create Python development configuration files.

    Args:
        project_path: Path to Python project

    Returns:
        List of created files
    """
    created = []

    pyproject_toml = project_path / "pyproject.toml"
    if not pyproject_toml.exists():
        pyproject_toml.touch()
        created.append(str(pyproject_toml))

    return created


def create_javascript_config_files(project_path: Path) -> list[str]:
    """
    Create JavaScript configuration files.

    Args:
        project_path: Path to JavaScript project

    Returns:
        List of created files
    """
    created = []

    package_json = project_path / "package.json"
    if not package_json.exists():
        package_json.write_text(json.dumps({"name": "", "version": "1.0.0"}, indent=2))
        created.append(str(package_json))

    gitignore = project_path / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("node_modules/\n.env\n")
        created.append(str(gitignore))

    return created
