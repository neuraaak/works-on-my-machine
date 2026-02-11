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

# Local imports
from ...exceptions.womm_deployment import (
    DeploymentUtilityError,
    FileVerificationServiceError,
)

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

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
        InstallationUtilityError: If file exclusion check fails
    """
    try:
        # Input validation
        if not file_path or not source_path:
            raise DeploymentUtilityError(
                message="File path and source path cannot be empty",
                operation="should_exclude_file",
                details="Invalid parameters provided for file exclusion check",
            )

        # Check if we're in dev mode (pyproject.toml exists in parent)
        project_root = source_path.parent
        pyproject_file = project_root / "pyproject.toml"

        if pyproject_file.exists():
            # DEV MODE: Read pyproject.toml for patterns
            return check_pyproject_patterns(file_path, source_path, pyproject_file)
        else:
            # PACKAGE MODE: No filtering needed (already done during build)
            return False  # Include everything

    except DeploymentUtilityError:
        # Re-raise specialized exceptions as-is
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise DeploymentUtilityError(
            message=f"Failed to check file exclusion: {e}",
            operation="should_exclude_file",
            details=f"Exception type: {type(e).__name__}, File: {file_path}, Source: {source_path}",
        ) from e


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
        InstallationUtilityError: If pyproject.toml parsing fails
    """
    try:
        # Input validation
        if not pyproject_file.exists():
            logger.warning(f"pyproject.toml not found at {pyproject_file}")
            return check_default_patterns(file_path, source_path)

        try:
            import tomllib  # type: ignore[reportMissingImports]  # Python 3.11+
        except ImportError:
            import tomli as tomllib  # type: ignore[reportMissingImports]  # Python < 3.11

        try:
            with open(pyproject_file, "rb") as f:
                config = tomllib.load(f)

            # Get exclude patterns from setuptools
            setuptools_config = config.get("tool", {}).get("setuptools", {})
            packages_find = setuptools_config.get("packages", {}).get("find", {})
            exclude_patterns = packages_find.get("exclude", [])

            # Add womm-specific exclusions
            womm_config = config.get("tool", {}).get("womm", {}).get("installation", {})
            additional_exclude = womm_config.get("additional-exclude", [])
            exclude_patterns.extend(additional_exclude)

            # Apply patterns
            relative_path = file_path.relative_to(source_path)

            for pattern in exclude_patterns:
                if pattern.endswith("*"):
                    # Handle wildcard patterns
                    base_pattern = pattern[:-1]
                    if str(relative_path).startswith(base_pattern):
                        return True
                elif pattern in str(relative_path):
                    return True

            return False

        except (PermissionError, OSError) as e:
            logger.warning(f"Failed to read pyproject.toml: {e}")
            return check_default_patterns(file_path, source_path)
        except (ValueError, KeyError) as e:
            logger.warning(f"Failed to parse pyproject.toml: {e}")
            return check_default_patterns(file_path, source_path)

    except Exception as e:
        # Wrap unexpected external exceptions
        raise DeploymentUtilityError(
            message=f"Failed to check pyproject patterns: {e}",
            details=f"Exception type: {type(e).__name__}, File: {file_path}, Pyproject: {pyproject_file}",
        ) from e


def check_default_patterns(file_path: Path, source_path: Path) -> bool:
    """
    Fallback to default exclusion patterns.

    Args:
        file_path: Path to the file relative to source
        source_path: Source directory path (womm package directory)

    Returns:
        bool: True if file should be excluded, False otherwise

    Raises:
        InstallationUtilityError: If default pattern check fails
    """
    try:
        default_patterns = [
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
        ]

        file_name = file_path.name
        relative_path = file_path.relative_to(source_path)

        for pattern in default_patterns:
            if pattern.startswith("*"):
                if file_name.endswith(pattern[1:]):
                    return True
            elif pattern == "setup.py":
                # Only exclude root setup.py, not subdirectory setup.py files
                if str(relative_path) == "setup.py":
                    return True
            elif pattern in str(relative_path):
                return True

        return False

    except Exception as e:
        # Wrap unexpected external exceptions
        raise DeploymentUtilityError(
            message=f"Failed to check default patterns: {e}",
            details=f"Exception type: {type(e).__name__}, File: {file_path}",
        ) from e


def get_files_to_copy(source_path: Path) -> list[str]:
    """
    Get list of files to copy during installation.

    Args:
        source_path: Source directory path

    Returns:
        List[str]: List of file paths relative to source

    Raises:
        InstallationUtilityError: If file enumeration fails
    """
    try:
        # Input validation
        if not source_path or not source_path.exists():
            raise DeploymentUtilityError(
                message="Source path does not exist",
                details=f"Source path: {source_path}",
            )

        files_to_copy = []

        for file_path in source_path.rglob("*"):
            try:
                if file_path.is_file() and not should_exclude_file(
                    file_path, source_path
                ):
                    relative_path = file_path.relative_to(source_path)
                    files_to_copy.append(str(relative_path))
            except Exception as e:
                logger.warning(f"Failed to process file {file_path}: {e}")
                continue

        return files_to_copy

    except DeploymentUtilityError:
        # Re-raise specialized exceptions as-is
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise DeploymentUtilityError(
            message=f"Failed to enumerate files to copy: {e}",
            details=f"Exception type: {type(e).__name__}, Source: {source_path}",
        ) from e


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
        DeploymentUtilityError: If executable files are missing or not readable
    """
    try:
        # Input validation
        if not target_path:
            raise DeploymentUtilityError(
                message="Target path cannot be empty",
                details="Invalid target path provided for executable verification",
            )

        # Verify womm.py exists
        womm_py_path = target_path / "womm.py"
        if not womm_py_path.exists():
            raise DeploymentUtilityError(
                message="womm.py not found in target directory",
                details=f"Expected file: {womm_py_path}",
            )

        # Verify womm.py is readable
        if not womm_py_path.is_file():
            raise DeploymentUtilityError(
                message="womm.py is not a regular file",
                details=f"Invalid file type at: {womm_py_path}",
            )

        try:
            with open(womm_py_path, encoding="utf-8") as f:
                f.read(1)  # Try reading first byte
        except (PermissionError, OSError) as e:
            raise DeploymentUtilityError(
                message=f"womm.py is not readable: {e}",
                details=f"File: {womm_py_path}",
            ) from e

        # Verify womm.bat exists (Windows)
        if platform.system() == "Windows":
            executable_path = target_path / "womm.bat"
            executable_name = "womm.bat"
        else:
            # Unix systems use womm.py directly via python3
            executable_path = target_path / "womm"
            executable_name = "womm"

        if not executable_path.exists():
            raise DeploymentUtilityError(
                message=f"{executable_name} not found in target directory",
                details=f"Expected file: {executable_path}",
            )

        if not executable_path.is_file():
            raise DeploymentUtilityError(
                message=f"{executable_name} is not a regular file",
                details=f"Invalid file type at: {executable_path}",
            )

        return {
            "success": True,
            "executable_path": str(executable_path),
            "womm_py_path": str(womm_py_path),
            "platform": platform.system(),
        }

    except DeploymentUtilityError:
        # Re-raise specialized exceptions as-is
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise DeploymentUtilityError(
            message=f"Unexpected error during executable verification: {e}",
            details=f"Exception type: {type(e).__name__}, Target path: {target_path}",
        ) from e


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
        FileVerificationError: If files are missing or corrupted
    """
    try:
        # Input validation
        if not source_path or not source_path.exists():
            raise FileVerificationServiceError(
                verification_type="copy_verification",
                file_path=str(source_path),
                message="Source path does not exist",
                details="Invalid source path provided for verification",
            )

        if not target_path or not target_path.exists():
            raise FileVerificationServiceError(
                verification_type="copy_verification",
                file_path=str(target_path),
                message="Target path does not exist",
                details="Invalid target path provided for verification",
            )

        files_to_check = files_list if files_list else get_files_to_copy(source_path)
        missing_files = []
        size_mismatches = []

        # Files are copied based on their type:
        # - womm/* files go to target_path/womm/*
        # - womm.py and womm.bat go to target_path/

        for relative_file in files_to_check:
            try:
                source_file = source_path / relative_file

                # Determine target path based on file type
                if relative_file.startswith("womm/"):
                    target_file = target_path / relative_file
                else:
                    # womm.py, womm.bat go directly to target root
                    target_file = target_path / relative_file
                if not target_file.exists():
                    missing_files.append(str(relative_file))
                elif source_file.stat().st_size != target_file.stat().st_size:
                    size_mismatches.append(str(relative_file))
            except Exception as e:
                logger.warning(f"Failed to verify file {relative_file}: {e}")
                missing_files.append(str(relative_file))

        # If there are issues, raise appropriate exceptions
        if missing_files:
            raise FileVerificationServiceError(
                verification_type="copy_verification",
                file_path=str(missing_files[0]),  # First missing file
                message=f"Missing {len(missing_files)} files",
                details=f"Missing files: {missing_files[:5]}{'...' if len(missing_files) > 5 else ''}",
            )

        if size_mismatches:
            raise FileVerificationServiceError(
                verification_type="copy_verification",
                file_path=str(size_mismatches[0]),  # First mismatched file
                message=f"Size mismatch in {len(size_mismatches)} files",
                details=f"Size mismatches: {size_mismatches[:5]}{'...' if len(size_mismatches) > 5 else ''}",
            )

        # All files verified successfully
        return {
            "success": True,
            "total_files": len(files_to_check),
            "missing_files": [],
            "size_mismatches": [],
        }

    except (FileVerificationServiceError, DeploymentUtilityError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise FileVerificationServiceError(
            verification_type="copy_verification",
            file_path=str(target_path),
            message=f"Unexpected error during file verification: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e


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
        DeploymentUtilityError: If proof file creation fails
    """
    try:
        womm_dir = target_path / "womm"
        proof_file = womm_dir / ".proof"

        # Ensure womm directory exists
        if not womm_dir.exists():
            raise DeploymentUtilityError(
                message="womm directory not found in target installation",
                details=f"Expected directory: {womm_dir}",
            )

        if not womm_dir.is_dir():
            raise DeploymentUtilityError(
                message="womm path is not a directory",
                details=f"Invalid path: {womm_dir}",
            )

        # Create proof file with installation metadata
        proof_data = {
            "installation_type": "womm",
            "installation_date": datetime.now().isoformat(),
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "target_path": str(target_path),
        }

        try:
            with open(proof_file, "w", encoding="utf-8") as f:
                json.dump(proof_data, f, indent=2)
        except (PermissionError, OSError) as e:
            raise DeploymentUtilityError(
                message=f"Failed to create proof file: {e}",
                details=f"Target file: {proof_file}",
            ) from e

        return {
            "success": True,
            "proof_file": str(proof_file),
            "installation_type": "womm",
        }

    except DeploymentUtilityError:
        # Re-raise specialized exceptions as-is
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise DeploymentUtilityError(
            message=f"Unexpected error during proof creation: {e}",
            details=f"Exception type: {type(e).__name__}, Target path: {target_path}",
        ) from e
