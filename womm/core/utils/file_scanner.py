#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# FILE SCANNER - File Scanning Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
File Scanner - Utilities for finding and filtering Python files.

Handles file discovery, security pattern filtering, and directory scanning.
Provides comprehensive file scanning capabilities with security validation
and pattern-based filtering for development tools.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path

# Local imports
# Import specialized exceptions
from ..exceptions.file import (
    FileAccessError,
    FileScanError,
    FileUtilityError,
    SecurityFilterError,
)
from .security.security_validator import SecurityValidator

# ///////////////////////////////////////////////////////////////
# FILE SCANNER CLASS
# ///////////////////////////////////////////////////////////////


class FileScanner:
    """Handles file discovery and filtering for linting operations."""

    # Python file extensions
    PYTHON_EXTENSIONS = {".py", ".pyi"}

    # Directories to exclude from scanning
    EXCLUDED_DIRS = {
        "__pycache__",
        ".git",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "node_modules",
        ".venv",
        "venv",
        "env",
        ".env",
        "build",
        "dist",
        "*.egg-info",
    }

    def __init__(self) -> None:
        """Initialize file scanner."""
        self.security_validator = SecurityValidator()

    def find_python_files(
        self, target_path: Path, recursive: bool = True
    ) -> list[Path]:
        """Find Python files in the given path.

        Args:
            target_path: Path to search (file or directory)
            recursive: Whether to search recursively in subdirectories

        Returns:
            List[Path]: List of Python file paths

        Raises:
            FileUtilityError: If input validation fails
            FileScanError: If target path does not exist
            FileAccessError: If directory access fails
            SecurityFilterError: If security filtering fails
        """
        try:
            # Input validation
            self._validate_target_path(target_path)

            python_files = []

            if target_path.is_file():
                if self._is_python_file(target_path):
                    python_files.append(target_path)
            elif target_path.is_dir():
                python_files.extend(self._scan_directory(target_path, recursive))
            else:
                raise FileScanError(
                    operation="find_python_files",
                    target_path=str(target_path),
                    reason="Path is neither a file nor a directory",
                    details=f"Path type: {target_path.stat().st_mode if target_path.exists() else 'unknown'}",
                )

            # Filter out files that match security patterns
            filtered_files = self._filter_secure_files(python_files)

            logging.debug(f"Found {len(filtered_files)} Python files in {target_path}")
            return filtered_files

        except (FileUtilityError, FileScanError, FileAccessError, SecurityFilterError):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise FileUtilityError(
                message=f"Unexpected error during file scanning: {e}",
                details=f"Exception type: {type(e).__name__}, Target: {target_path}",
            ) from e

    def get_project_python_files(self, project_root: Path) -> list[Path]:
        """Get all Python files in a project, excluding common non-source directories.

        Args:
            project_root: Root directory of the project

        Returns:
            List[Path]: List of Python source files

        Raises:
            FileUtilityError: If input validation fails
            FileScanError: If project root is invalid
            FileAccessError: If directory access fails
            SecurityFilterError: If security filtering fails
        """
        try:
            # Input validation
            self._validate_project_root(project_root)

            python_files = []

            # Walk through all subdirectories
            try:
                for item in project_root.rglob("*"):
                    if self._should_exclude_path(item):
                        continue

                    if item.is_file() and self._is_python_file(item):
                        python_files.append(item)

            except (PermissionError, OSError) as e:
                raise FileAccessError(
                    operation="scan_directory",
                    file_path=str(project_root),
                    reason=f"Permission or OS error: {e}",
                    details=f"Failed to scan directory {project_root}",
                ) from e

            # Filter security patterns
            filtered_files = self._filter_secure_files(python_files)

            logging.debug(
                f"Found {len(filtered_files)} Python files in project {project_root.name}"
            )
            return filtered_files

        except (FileUtilityError, FileScanError, FileAccessError, SecurityFilterError):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise FileUtilityError(
                message=f"Unexpected error during project file scanning: {e}",
                details=f"Exception type: {type(e).__name__}, Project: {project_root}",
            ) from e

    def _scan_directory(self, directory: Path, recursive: bool) -> list[Path]:
        """Scan a directory for Python files.

        Args:
            directory: Directory to scan
            recursive: Whether to scan recursively

        Returns:
            List[Path]: List of Python files found

        Raises:
            FileScanError: If directory does not exist
            FileAccessError: If directory access fails
        """
        try:
            if not directory.exists():
                raise FileScanError(
                    operation="scan_directory",
                    target_path=str(directory),
                    reason="Directory does not exist",
                    details=f"Directory {directory} was not found",
                )

            python_files = []

            if recursive:
                # Recursive scan
                try:
                    for item in directory.rglob("*"):
                        if self._should_exclude_path(item):
                            continue

                        if item.is_file() and self._is_python_file(item):
                            python_files.append(item)
                except (PermissionError, OSError) as e:
                    raise FileAccessError(
                        operation="recursive_scan",
                        file_path=str(directory),
                        reason=f"Permission or OS error during recursive scan: {e}",
                        details=f"Failed to recursively scan directory {directory}",
                    ) from e
            else:
                # Non-recursive scan
                try:
                    for item in directory.iterdir():
                        if self._should_exclude_path(item):
                            continue

                        if item.is_file() and self._is_python_file(item):
                            python_files.append(item)
                except (PermissionError, OSError) as e:
                    raise FileAccessError(
                        operation="directory_scan",
                        file_path=str(directory),
                        reason=f"Permission or OS error during directory scan: {e}",
                        details=f"Failed to scan directory {directory}",
                    ) from e

            return python_files

        except (FileScanError, FileAccessError):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise FileScanError(
                operation="scan_directory",
                target_path=str(directory),
                reason=f"Unexpected error during directory scanning: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _validate_target_path(self, target_path: Path) -> None:
        """Validate target path for file scanning.

        Args:
            target_path: Path to validate

        Raises:
            FileUtilityError: If target path is invalid
            FileScanError: If target path does not exist
        """
        if not target_path:
            raise FileUtilityError(
                message="Target path cannot be None",
                details="Input validation failed for file scanning operation",
            )

        if not target_path.exists():
            raise FileScanError(
                operation="validate_target_path",
                target_path=str(target_path),
                reason="Path does not exist",
                details=f"Target path {target_path} was not found",
            )

    def _validate_project_root(self, project_root: Path) -> None:
        """Validate project root for file scanning.

        Args:
            project_root: Project root to validate

        Raises:
            FileUtilityError: If project root is invalid
            FileScanError: If project root does not exist or is not a directory
        """
        if not project_root:
            raise FileUtilityError(
                message="Project root cannot be None",
                details="Input validation failed for project file scanning",
            )

        if not project_root.exists() or not project_root.is_dir():
            raise FileScanError(
                operation="validate_project_root",
                target_path=str(project_root),
                reason="Invalid project root",
                details=f"Project root {project_root} does not exist or is not a directory",
            )

    def _is_python_file(self, file_path: Path) -> bool:
        """Check if a file is a Python file.

        Args:
            file_path: File path to check

        Returns:
            bool: True if file is a Python file
        """
        try:
            if not file_path.exists():
                return False

            if not file_path.is_file():
                return False

            return file_path.suffix.lower() in self.PYTHON_EXTENSIONS

        except Exception as e:
            # Log but don't raise - this is a helper method
            logging.warning(
                f"Error checking if file is Python: {file_path}, Error: {e}"
            )
            return False

    def _should_exclude_path(self, path: Path) -> bool:
        """Check if a path should be excluded from scanning.

        Args:
            path: Path to check

        Returns:
            bool: True if path should be excluded
        """
        try:
            # Check if any part of the path matches excluded patterns
            return any(part in self.EXCLUDED_DIRS for part in path.parts)
        except Exception as e:
            # Log but don't raise - this is a helper method
            logging.warning(f"Error checking path exclusion: {path}, Error: {e}")
            return True  # Exclude on error for safety

    def _filter_secure_files(self, files: list[Path]) -> list[Path]:
        """Filter files based on security patterns.

        Args:
            files: List of files to filter

        Returns:
            List[Path]: Filtered list of files

        Raises:
            SecurityFilterError: If security filtering fails
        """
        try:
            filtered_files = []

            for file_path in files:
                try:
                    # Check if file path contains security-sensitive patterns
                    file_str = str(file_path)
                    if any(
                        pattern in file_str.lower()
                        for pattern in [
                            "password",
                            "secret",
                            "key",
                            "credential",
                            "token",
                        ]
                    ):
                        logging.debug(f"Skipping security-sensitive file: {file_path}")
                        continue

                    # Additional security validation using SecurityValidator
                    try:
                        self.security_validator.validate_file_path(file_str)
                        filtered_files.append(file_path)
                    except Exception as e:
                        # If security validation fails, log and include the file
                        logging.warning(
                            f"Security validation failed for {file_path}: {e}"
                        )
                        filtered_files.append(file_path)

                except Exception as e:
                    # Log individual file processing errors but continue
                    logging.warning(f"Error processing file {file_path}: {e}")
                    filtered_files.append(file_path)  # Include on error for safety

            return filtered_files

        except Exception as e:
            raise SecurityFilterError(
                operation="filter_files",
                file_path="multiple",
                reason=f"Security filtering failed: {e}",
                details=f"Failed to filter {len(files)} files",
            ) from e

    def get_scan_summary(
        self, target_path: Path
    ) -> dict[str, str | int | bool | list[str]]:
        """Get a summary of the scanning operation.

        Args:
            target_path: Path that was scanned

        Returns:
            dict: Summary information
        """
        try:
            python_files = self.find_python_files(target_path)

            return {
                "target_path": str(target_path),
                "total_files": len(python_files),
                "file_extensions": list(self.PYTHON_EXTENSIONS),
                "excluded_dirs": list(self.EXCLUDED_DIRS),
                "scan_successful": True,
            }
        except Exception as e:
            return {
                "target_path": str(target_path),
                "total_files": 0,
                "file_extensions": list(self.PYTHON_EXTENSIONS),
                "excluded_dirs": list(self.EXCLUDED_DIRS),
                "scan_successful": False,
                "error": str(e),
            }
