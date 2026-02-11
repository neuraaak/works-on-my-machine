#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# FILE SCANNER SERVICE - File Scanning Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
File Scanner Service - Singleton service for finding and filtering Python files.

Handles file discovery, security pattern filtering, and directory scanning.
Provides comprehensive file scanning capabilities with security validation
and pattern-based filtering for development tools.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import time
from pathlib import Path
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.common import (
    FileAccessError,
    FileScanError,
    FileValidationError,
    SecurityFilterError,
)
from ...shared.configs.security import FileScannerConfig
from ...shared.result_models import FileScanResult
from ...shared.results import FileSearchResult
from ...utils.common import (
    contains_security_sensitive_pattern,
    is_python_file,
    should_exclude_path,
)
from .security_validator_service import SecurityValidatorService

# ///////////////////////////////////////////////////////////////
# FILE SCANNER SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class FileScannerService:
    """Singleton service for file discovery and filtering operations."""

    _instance: ClassVar[FileScannerService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> FileScannerService:
        """Create or return the singleton instance.

        Returns:
            FileScannerService: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize file scanner service (only once)."""
        if FileScannerService._initialized:
            return

        self.logger = logging.getLogger(__name__)
        self.security_validator = SecurityValidatorService()
        FileScannerService._initialized = True

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def find_python_files(
        self, target_path: Path, recursive: bool = True
    ) -> FileSearchResult:
        """Find Python files in the given path.

        Args:
            target_path: Path to search (file or directory)
            recursive: Whether to search recursively in subdirectories

        Returns:
            FileSearchResult: Result with list of Python file paths

        Raises:
            FileValidationError: If input validation fails
            FileScanError: If target path does not exist
            FileAccessError: If directory access fails
            SecurityFilterError: If security filtering fails
        """
        start_time = time.time()
        try:
            # Input validation
            self._validate_target_path(target_path)

            python_files = []

            if target_path.is_file():
                if is_python_file(target_path):
                    python_files.append(target_path)
            elif target_path.is_dir():
                python_files.extend(self._scan_directory(target_path, recursive))
            else:
                raise FileScanError(
                    message="Path is neither a file nor a directory",
                    operation="find_python_files",
                    target_path=str(target_path),
                    details=(
                        f"Path type: {target_path.stat().st_mode if target_path.exists() else 'unknown'}"
                    ),
                )

            # Filter out files that match security patterns
            filtered_files = self._filter_secure_files(python_files)

            search_time = time.time() - start_time
            self.logger.debug(
                f"Found {len(filtered_files)} Python files in {target_path}"
            )
            return FileSearchResult(
                success=True,
                message=f"Found {len(filtered_files)} Python files",
                target_path=target_path,
                files_found=filtered_files,
                recursive=recursive,
                search_time=search_time,
            )

        except (
            FileValidationError,
            FileScanError,
            FileAccessError,
            SecurityFilterError,
        ) as e:
            search_time = time.time() - start_time
            # Re-raise specialized exceptions as-is but return result
            return FileSearchResult(
                success=False,
                error=str(e),
                target_path=target_path,
                files_found=[],
                recursive=recursive,
                search_time=search_time,
            )
        except Exception as e:
            search_time = time.time() - start_time
            # Wrap unexpected external exceptions
            return FileSearchResult(
                success=False,
                error=f"Unexpected error during file scanning: {e}",
                target_path=target_path,
                files_found=[],
                recursive=recursive,
                search_time=search_time,
            )

    def get_project_python_files(self, project_root: Path) -> FileSearchResult:
        """Get all Python files in a project, excluding common non-source directories.

        Args:
            project_root: Root directory of the project

        Returns:
            FileSearchResult: Result with list of Python source files

        Raises:
            FileValidationError: If input validation fails
            FileScanError: If project root is invalid
            FileAccessError: If directory access fails
            SecurityFilterError: If security filtering fails
        """
        start_time = time.time()
        try:
            # Input validation
            self._validate_project_root(project_root)

            python_files = []

            # Walk through all subdirectories
            try:
                for item in project_root.rglob("*"):
                    if should_exclude_path(item):
                        continue

                    if item.is_file() and is_python_file(item):
                        python_files.append(item)

            except (PermissionError, OSError) as e:
                search_time = time.time() - start_time
                return FileSearchResult(
                    success=False,
                    error=f"Permission or OS error: {e}",
                    target_path=project_root,
                    files_found=[],
                    recursive=True,
                    search_time=search_time,
                )

            # Filter security patterns
            filtered_files = self._filter_secure_files(python_files)

            search_time = time.time() - start_time
            self.logger.debug(
                f"Found {len(filtered_files)} Python files in project {project_root.name}"
            )
            return FileSearchResult(
                success=True,
                message=f"Found {len(filtered_files)} Python files in project",
                target_path=project_root,
                files_found=filtered_files,
                recursive=True,
                search_time=search_time,
            )

        except (
            FileValidationError,
            FileScanError,
            FileAccessError,
            SecurityFilterError,
        ) as e:
            search_time = time.time() - start_time
            return FileSearchResult(
                success=False,
                error=str(e),
                target_path=project_root,
                files_found=[],
                recursive=True,
                search_time=search_time,
            )
        except Exception as e:
            search_time = time.time() - start_time
            return FileSearchResult(
                success=False,
                error=f"Unexpected error during project file scanning: {e}",
                target_path=project_root,
                files_found=[],
                recursive=True,
                search_time=search_time,
            )

    def get_scan_summary(
        self, target_path: Path | list[Path] | None = None
    ) -> FileScanResult:
        """Get a summary of the scanning operation.

        Args:
            target_path: Path that was scanned, or list of already-scanned files.
                        If None, returns a generic summary.

        Returns:
            FileScanResult: Summary information with scan results

        Raises:
            FileServiceError: If scanning fails
        """
        start_time = time.time()
        try:
            if isinstance(target_path, list):
                # Already have files, just create summary
                python_files = target_path
                actual_path = python_files[0].parent if python_files else None
            elif target_path is not None:
                # Need to scan
                search_result = self.find_python_files(target_path)
                if search_result.success and isinstance(
                    search_result.files_found, list
                ):
                    python_files = search_result.files_found
                else:
                    python_files = []
                actual_path = target_path
            else:
                # No path provided, return empty summary
                python_files = []
                actual_path = None

            scan_time = time.time() - start_time

            return FileScanResult(
                success=True,
                message=f"Successfully scanned {len(python_files)} Python files",
                target_path=actual_path,
                total_files=len(python_files),
                files_found=python_files,
                excluded_dirs=list(FileScannerConfig.EXCLUDED_DIRS),
                file_extensions=list(FileScannerConfig.PYTHON_EXTENSIONS),
                scan_time=scan_time,
            )
        except Exception as e:
            scan_time = time.time() - start_time
            return FileScanResult(
                success=False,
                error=f"Scan failed: {e}",
                target_path=target_path if isinstance(target_path, Path) else None,
                total_files=0,
                files_found=[],
                excluded_dirs=list(FileScannerConfig.EXCLUDED_DIRS),
                file_extensions=list(FileScannerConfig.PYTHON_EXTENSIONS),
                scan_time=scan_time,
            )

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

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
                    message="Directory does not exist",
                    operation="scan_directory",
                    target_path=str(directory),
                    details=f"Directory {directory} was not found",
                )

            python_files = []

            if recursive:
                # Recursive scan
                try:
                    for item in directory.rglob("*"):
                        if should_exclude_path(item):
                            continue

                        if item.is_file() and is_python_file(item):
                            python_files.append(item)
                except (PermissionError, OSError) as e:
                    raise FileAccessError(
                        message=f"Permission or OS error during recursive scan: {e}",
                        operation="recursive_scan",
                        file_path=str(directory),
                        reason=f"Permission or OS error during recursive scan: {e}",
                        details=f"Failed to recursively scan directory {directory}",
                    ) from e
            else:
                # Non-recursive scan
                try:
                    for item in directory.iterdir():
                        if should_exclude_path(item):
                            continue

                        if item.is_file() and is_python_file(item):
                            python_files.append(item)
                except (PermissionError, OSError) as e:
                    raise FileAccessError(
                        message=f"Permission or OS error during directory scan: {e}",
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
                message=f"Unexpected error during directory scanning: {e}",
                operation="scan_directory",
                target_path=str(directory),
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _validate_target_path(self, target_path: Path) -> None:
        """Validate target path for file scanning.

        Args:
            target_path: Path to validate

        Raises:
            FileValidationError: If target path is invalid
            FileScanError: If target path does not exist
        """
        if not target_path:
            raise FileValidationError(
                message="Target path cannot be None",
                operation="validate_target_path",
                target_path="",
                details="Input validation failed for file scanning operation",
            )

        if not target_path.exists():
            raise FileScanError(
                message="Path does not exist",
                operation="validate_target_path",
                target_path=str(target_path),
                details=f"Target path {target_path} was not found",
            )

    def _validate_project_root(self, project_root: Path) -> None:
        """Validate project root for file scanning.

        Args:
            project_root: Project root to validate

        Raises:
            FileValidationError: If project root is invalid
            FileScanError: If project root does not exist or is not a directory
        """
        if not project_root:
            raise FileValidationError(
                message="Project root cannot be None",
                operation="validate_project_root",
                target_path="",
                details="Input validation failed for project file scanning",
            )

        if not project_root.exists() or not project_root.is_dir():
            raise FileScanError(
                message="Invalid project root",
                operation="validate_project_root",
                target_path=str(project_root),
                details=(
                    f"Project root {project_root} does not exist or is not a directory"
                ),
            )

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
                    if contains_security_sensitive_pattern(file_path):
                        self.logger.debug(
                            f"Skipping security-sensitive file: {file_path}"
                        )
                        continue

                    # Additional security validation using SecurityValidator
                    try:
                        validation_result = self.security_validator.validate_file_path(
                            str(file_path)
                        )
                        if validation_result.is_valid:
                            filtered_files.append(file_path)
                        else:
                            # If security validation fails, log and skip the file
                            self.logger.warning(
                                f"Security validation failed for {file_path}: {validation_result.validation_reason}"
                            )
                    except Exception as e:
                        # If security validation fails, log and include the file
                        self.logger.warning(
                            f"Security validation failed for {file_path}: {e}"
                        )
                        filtered_files.append(file_path)

                except Exception as e:
                    # Log individual file processing errors but continue
                    self.logger.warning(f"Error processing file {file_path}: {e}")
                    filtered_files.append(file_path)  # Include on error for safety

            return filtered_files

        except Exception as e:
            raise SecurityFilterError(
                message=f"Security filtering failed: {e}",
                operation="filter_files",
                target_path="multiple",
                details=f"Failed to filter {len(files)} files",
            ) from e
