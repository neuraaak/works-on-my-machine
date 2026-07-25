#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# INSTALLATION UTILS - Installation Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Installation utilities for Works On My Machine.

This module provides pure utility functions for WOMM installation operations.
All functions here are stateless and can be used independently.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
import logging
import platform
from datetime import datetime
from pathlib import Path

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

# Fallback exclusion patterns used when pyproject.toml is unreadable or absent.
DEFAULT_EXCLUDE_PATTERNS = (
    ".git",
    ".gitignore",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".coverage",
    "htmlcov",
    "coverage.xml",
    ".venv",
    "venv",
    "node_modules",
    "build",
    "dist",
    "*.egg-info",
    "tests",
    "test_*",
    "*_test.py",
    "docs",
    "pyproject.toml",
    "setup.py",  # Only exclude root setup.py, not subdirectory setup.py files
    "*.log",
    ".DS_Store",
    "Thumbs.db",
    ".vscode",
    ".idea",
    ".cursor",
    "ignore-install.txt",
    "womm.bat",
)

# ///////////////////////////////////////////////////////////////
# FILE MANAGEMENT UTILITIES
# ///////////////////////////////////////////////////////////////


def should_exclude_file(file_path: Path, source_path: Path) -> bool:
    """
    Check if a file should be excluded from installation.

    Args:
        file_path: Path to the file relative to source
        source_path: Source directory path (womm package directory)

    Returns:
        bool: True if file should be excluded, False otherwise

    Raises:
        ValueError: If either path is empty.
    """
    if not file_path or not source_path:
        raise ValueError("File path and source path cannot be empty")

    # Check if we're in dev mode (pyproject.toml exists in parent)
    pyproject_file = source_path.parent / "pyproject.toml"

    if pyproject_file.exists():
        # DEV MODE: Read pyproject.toml for patterns
        return check_pyproject_patterns(file_path, source_path, pyproject_file)

    # PACKAGE MODE: No filtering needed (already done during build)
    return False


def check_pyproject_patterns(
    file_path: Path, source_path: Path, pyproject_file: Path
) -> bool:
    """
    Check exclusion patterns from pyproject.toml.

    Args:
        file_path: Path to the file relative to source
        source_path: Source directory path (womm package directory)
        pyproject_file: Path to pyproject.toml

    Returns:
        bool: True if file should be excluded, False otherwise

    Raises:
        ValueError: If `file_path` is not relative to `source_path`.
    """
    if not pyproject_file.exists():
        logger.warning(f"pyproject.toml not found at {pyproject_file}")
        return check_default_patterns(file_path, source_path)

    import tomllib

    try:
        with open(pyproject_file, "rb") as f:
            config = tomllib.load(f)
    except OSError as e:
        logger.warning(f"Failed to read pyproject.toml: {e}")
        return check_default_patterns(file_path, source_path)
    except tomllib.TOMLDecodeError as e:
        logger.warning(f"Failed to parse pyproject.toml: {e}")
        return check_default_patterns(file_path, source_path)

    # Get exclude patterns from setuptools
    setuptools_config = config.get("tool", {}).get("setuptools", {})
    packages_find = setuptools_config.get("packages", {}).get("find", {})
    exclude_patterns = list(packages_find.get("exclude", []))

    # Add womm-specific exclusions
    womm_config = config.get("tool", {}).get("womm", {}).get("installation", {})
    exclude_patterns.extend(womm_config.get("additional-exclude", []))

    # Apply patterns
    relative_path = str(file_path.relative_to(source_path))

    for pattern in exclude_patterns:
        if pattern.endswith("*"):
            # Handle wildcard patterns
            if relative_path.startswith(pattern[:-1]):
                return True
        elif pattern in relative_path:
            return True

    return False


def check_default_patterns(file_path: Path, source_path: Path) -> bool:
    """
    Fallback to default exclusion patterns.

    Args:
        file_path: Path to the file relative to source
        source_path: Source directory path (womm package directory)

    Returns:
        bool: True if file should be excluded, False otherwise

    Raises:
        ValueError: If `file_path` is not relative to `source_path`.
    """
    file_name = file_path.name
    relative_path = str(file_path.relative_to(source_path))

    for pattern in DEFAULT_EXCLUDE_PATTERNS:
        if pattern.startswith("*"):
            if file_name.endswith(pattern[1:]):
                return True
        elif pattern == "setup.py":
            # Only exclude root setup.py, not subdirectory setup.py files
            if relative_path == "setup.py":
                return True
        elif pattern in relative_path:
            return True

    return False


def get_files_to_copy(source_path: Path) -> list[str]:
    """
    Get list of files to copy during installation.

    Args:
        source_path: Source directory path

    Returns:
        List[str]: List of file paths relative to source

    Raises:
        FileNotFoundError: If `source_path` does not exist.
    """
    if not source_path or not source_path.exists():
        raise FileNotFoundError(f"Source path does not exist: {source_path}")

    files_to_copy = []

    for file_path in source_path.rglob("*"):
        try:
            if file_path.is_file() and not should_exclude_file(file_path, source_path):
                files_to_copy.append(str(file_path.relative_to(source_path)))
        except (OSError, ValueError) as e:
            logger.warning(f"Failed to process file {file_path}: {e}")
            continue

    return files_to_copy


# ///////////////////////////////////////////////////////////////
# EXECUTABLE CREATION UTILITIES
# ///////////////////////////////////////////////////////////////


def create_womm_executable(target_path: Path) -> dict[str, str | bool]:
    """
    Verify womm executable files exist.

    The womm.py and womm.bat files are copied during the file copy phase,
    this function verifies they exist and are readable.

    Args:
        target_path: Path where WOMM is installed

    Returns:
        Dict: Dictionary with success status and details

    Raises:
        ValueError: If `target_path` is empty.
        FileNotFoundError: If womm.py or the platform launcher is missing.
        OSError: If womm.py exists but cannot be read.
    """
    if not target_path:
        raise ValueError("Target path cannot be empty")

    # Verify womm.py exists and is a readable regular file
    womm_py_path = target_path / "womm.py"
    if not womm_py_path.is_file():
        raise FileNotFoundError(
            f"womm.py not found in target directory: {womm_py_path}"
        )

    with open(womm_py_path, encoding="utf-8") as f:
        f.read(1)  # Try reading first byte

    # Windows ships a .bat launcher; Unix runs womm.py through python3
    executable_name = "womm.bat" if platform.system() == "Windows" else "womm"
    executable_path = target_path / executable_name

    if not executable_path.is_file():
        raise FileNotFoundError(
            f"{executable_name} not found in target directory: {executable_path}"
        )

    return {
        "success": True,
        "executable_path": str(executable_path),
        "womm_py_path": str(womm_py_path),
        "platform": platform.system(),
    }


# ///////////////////////////////////////////////////////////////
# VERIFICATION UTILITIES
# ///////////////////////////////////////////////////////////////


def verify_files_copied(
    source_path: Path, target_path: Path, files_list: list[str] | None = None
) -> dict[str, str | bool | int | list[str]]:
    """
    Verify that all required files were copied correctly.

    Args:
        source_path: Original source directory (womm package directory)
        target_path: Target installation directory (will contain womm/ subdirectory)
        files_list: Optional list of relative file paths to verify. If None, uses get_files_to_copy()

    Returns:
        Dict: Dictionary with verification results

    Raises:
        FileNotFoundError: If a path does not exist, or files are missing at the target.
        OSError: If copied files differ in size from their source.
    """
    if not source_path or not source_path.exists():
        raise FileNotFoundError(f"Source path does not exist: {source_path}")

    if not target_path or not target_path.exists():
        raise FileNotFoundError(f"Target path does not exist: {target_path}")

    files_to_check = files_list if files_list else get_files_to_copy(source_path)
    missing_files: list[str] = []
    size_mismatches: list[str] = []

    # Layout is flat: womm/* keeps its prefix, womm.py and womm.bat sit at the root,
    # so the relative path applies unchanged to the target in both cases.
    for relative_file in files_to_check:
        source_file = source_path / relative_file
        target_file = target_path / relative_file
        try:
            if not target_file.exists():
                missing_files.append(relative_file)
            elif source_file.stat().st_size != target_file.stat().st_size:
                size_mismatches.append(relative_file)
        except OSError as e:
            logger.warning(f"Failed to verify file {relative_file}: {e}")
            missing_files.append(relative_file)

    if missing_files:
        raise FileNotFoundError(
            f"Missing {len(missing_files)} files at {target_path}: "
            f"{missing_files[:5]}{'...' if len(missing_files) > 5 else ''}"
        )

    if size_mismatches:
        raise OSError(
            f"Size mismatch in {len(size_mismatches)} files at {target_path}: "
            f"{size_mismatches[:5]}{'...' if len(size_mismatches) > 5 else ''}"
        )

    # All files verified successfully
    return {
        "success": True,
        "total_files": len(files_to_check),
        "missing_files": [],
        "size_mismatches": [],
    }


# ///////////////////////////////////////////////////////////////
# PROOF OF INSTALLATION
# ///////////////////////////////////////////////////////////////


def create_installation_proof(target_path: Path) -> dict[str, str | bool]:
    """
    Create a .proof file to mark successful installation.

    The .proof file is created in the womm/ subdirectory to identify
    the installation type (dev/package/exe) and validate installation integrity.

    Args:
        target_path: Target installation directory (e.g., ~/.womm/)

    Returns:
        Dict: Dictionary with success status and proof file path

    Raises:
        NotADirectoryError: If the target has no womm/ directory to mark.
        OSError: If the proof file cannot be written.
    """
    womm_dir = target_path / "womm"
    proof_file = womm_dir / ".proof"

    if not womm_dir.is_dir():
        raise NotADirectoryError(
            f"womm directory not found in target installation: {womm_dir}"
        )

    # Create proof file with installation metadata
    proof_data = {
        "installation_type": "womm",
        "installation_date": datetime.now().isoformat(),
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "target_path": str(target_path),
    }

    with open(proof_file, "w", encoding="utf-8") as f:
        json.dump(proof_data, f, indent=2)

    return {
        "success": True,
        "proof_file": str(proof_file),
        "installation_type": "womm",
    }
