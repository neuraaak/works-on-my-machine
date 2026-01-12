#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT DETECTION SERVICE - Project Detection Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Project Detection Service - Singleton service for project detection.

Handles project type detection, configuration file analysis, and project structure validation.
Provides comprehensive project analysis capabilities for various development environments.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.project import ProjectDetectionServiceError, ProjectServiceError
from ...shared.configs.project import ProjectConfig
from ...shared.results import ProjectDetectionResult
from ...utils.project import (
    analyze_csharp_config,
    analyze_go_config,
    analyze_java_config,
    analyze_javascript_config,
    analyze_python_config,
    analyze_rust_config,
    categorize_directory,
    matches_project_type,
)

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# PROJECT DETECTION SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class ProjectDetectionService:
    """Singleton service for detecting project types and configurations."""

    _instance: ClassVar[ProjectDetectionService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> ProjectDetectionService:
        """Create or return the singleton instance.

        Returns:
            ProjectDetectionService: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize project detection service (only once)."""
        if ProjectDetectionService._initialized:
            return

        self.logger = logging.getLogger(__name__)
        ProjectDetectionService._initialized = True

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def detect_project_type(self, project_path: Path) -> ProjectDetectionResult:
        """Detect the type of project at the given path.

        Args:
            project_path: Path to the project directory

        Returns:
            ProjectDetectionResult: Result with detected project type and metadata

        Raises:
            ProjectServiceError: If input validation fails
            ProjectDetectionError: If project detection fails
        """
        try:
            # Input validation
            if not project_path:
                raise ProjectServiceError(
                    message="Project path cannot be None",
                    operation="detect_project_type",
                    details="Empty project path provided for project type detection",
                )

            if not project_path.exists():
                raise ProjectDetectionServiceError(
                    message="Project path does not exist",
                    operation="detect_project_type",
                    project_path=str(project_path),
                    reason="Project path does not exist",
                    details=f"Path {project_path} was not found",
                )

            if not project_path.is_dir():
                raise ProjectDetectionServiceError(
                    message="Project path is not a directory",
                    operation="detect_project_type",
                    project_path=str(project_path),
                    reason="Project path is not a directory",
                    details=f"Path {project_path} is not a directory",
                )

            # Analyze project structure
            project_files = list(project_path.iterdir())
            project_dirs = [item for item in project_files if item.is_dir()]
            project_files = [item for item in project_files if item.is_file()]

            # Check each project type
            detected_type = None
            for project_type, indicators in ProjectConfig.PROJECT_INDICATORS.items():
                if matches_project_type(project_files, project_dirs, indicators):
                    detected_type = project_type
                    break

            # Build result
            return ProjectDetectionResult(
                success=True,
                message="Project type detection completed",
                project_type=detected_type or "unknown",
                confidence=100.0 if detected_type else 0.0,
                detected_files=[f.name for f in project_files],
                configuration_files={},
            )

        except (ProjectServiceError, ProjectDetectionServiceError):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in detect_project_type: {e}")
            raise ProjectServiceError(
                message=f"Unexpected error during project type detection: {e}",
                operation="detect_project_type",
                details=f"Exception type: {type(e).__name__}, Project: {project_path}",
            ) from e

    def detect_project_config(self, project_path: Path) -> ProjectDetectionResult:
        """Detect project configuration files and settings.

        Args:
            project_path: Path to the project directory

        Returns:
            ProjectDetectionResult: Result with project configuration information

        Raises:
            ProjectServiceError: If input validation fails
            ProjectDetectionError: If project configuration detection fails
        """
        try:
            # Input validation
            if not project_path:
                raise ProjectServiceError(
                    message="Project path cannot be None",
                    operation="detect_project_config",
                    details="Empty project path provided for project configuration detection",
                )

            if not project_path.exists():
                raise ProjectDetectionServiceError(
                    message="Project path does not exist",
                    operation="detect_project_config",
                    project_path=str(project_path),
                    reason="Project path does not exist",
                    details=f"Path {project_path} was not found",
                )

            if not project_path.is_dir():
                raise ProjectDetectionServiceError(
                    message="Project path is not a directory",
                    operation="detect_project_config",
                    project_path=str(project_path),
                    reason="Project path is not a directory",
                    details=f"Path {project_path} is not a directory",
                )

            config_files: dict[str, str] = {}

            # Detect project type first
            type_result = self.detect_project_type(project_path)
            if not type_result.success:
                raise ProjectDetectionServiceError(
                    message="Failed to detect project type",
                    operation="detect_project_config",
                    project_path=str(project_path),
                    reason="Unable to determine project type",
                    details="Project type detection failed",
                )

            project_type = type_result.project_type

            # Analyze configuration files based on project type
            try:
                if project_type == "python":
                    config = analyze_python_config(project_path)
                    if config and isinstance(config, dict):
                        config_files.update(config.get("config_files", {}))
                elif project_type == "javascript":
                    config = analyze_javascript_config(project_path)
                    if config and isinstance(config, dict):
                        config_files.update(config.get("config_files", {}))
                elif project_type == "java":
                    config = analyze_java_config(project_path)
                    if config and isinstance(config, dict):
                        config_files.update(config.get("config_files", {}))
                elif project_type == "go":
                    config = analyze_go_config(project_path)
                    if config and isinstance(config, dict):
                        config_files.update(config.get("config_files", {}))
                elif project_type == "rust":
                    config = analyze_rust_config(project_path)
                    if config and isinstance(config, dict):
                        config_files.update(config.get("config_files", {}))
                elif project_type == "csharp":
                    config = analyze_csharp_config(project_path)
                    if config and isinstance(config, dict):
                        config_files.update(config.get("config_files", {}))
            except Exception as e:
                logger.warning(
                    f"Failed to analyze configuration for {project_type}: {e}"
                )
                # Continue with partial results

            return ProjectDetectionResult(
                success=True,
                message="Project configuration detection completed",
                project_type=project_type,
                confidence=100.0,
                detected_files=[],
                configuration_files=config_files,
            )

        except (ProjectServiceError, ProjectDetectionServiceError):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in detect_project_config: {e}")
            raise ProjectServiceError(
                message=f"Unexpected error during project configuration detection: {e}",
                operation="detect_project_config",
                details=f"Exception type: {type(e).__name__}, Project: {project_path}",
            ) from e

    def detect_project_structure(self, project_path: Path) -> ProjectDetectionResult:
        """Detect project structure and organization.

        Args:
            project_path: Path to the project directory

        Returns:
            ProjectDetectionResult: Result with project structure information

        Raises:
            ProjectServiceError: If input validation fails
            ProjectDetectionError: If project structure detection fails
        """
        try:
            # Input validation
            if not project_path:
                raise ProjectServiceError(
                    message="Project path cannot be None",
                    operation="detect_project_structure",
                    details="Empty project path provided for project structure detection",
                )

            if not project_path.exists():
                raise ProjectDetectionServiceError(
                    message="Project path does not exist",
                    operation="detect_project_structure",
                    project_path=str(project_path),
                    reason="Project path does not exist",
                    details=f"Path {project_path} was not found",
                )

            if not project_path.is_dir():
                raise ProjectDetectionServiceError(
                    message="Project path is not a directory",
                    operation="detect_project_structure",
                    project_path=str(project_path),
                    reason="Project path is not a directory",
                    details=f"Path {project_path} is not a directory",
                )

            structure: dict[str, str | bool | int | list[str]] = {
                "source_dirs": [],
                "test_dirs": [],
                "config_dirs": [],
                "build_dirs": [],
                "documentation_dirs": [],
                "total_files": 0,
                "total_dirs": 0,
            }

            try:
                # Walk through project structure
                for item in project_path.rglob("*"):
                    if item.is_file():
                        structure["total_files"] = int(structure["total_files"]) + 1
                    elif item.is_dir():
                        structure["total_dirs"] = int(structure["total_dirs"]) + 1
                        categorize_directory(item, structure, project_path)

            except (PermissionError, OSError) as e:
                logger.warning(f"Permission or OS error during structure analysis: {e}")
                # Continue with partial results

            return ProjectDetectionResult(
                success=True,
                message="Project structure detection completed",
                project_type="",
                confidence=100.0,
                detected_files=[],
                configuration_files=structure,
            )

        except (ProjectServiceError, ProjectDetectionServiceError):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in detect_project_structure: {e}")
            raise ProjectServiceError(
                message=f"Unexpected error during project structure detection: {e}",
                operation="detect_project_structure",
                details=f"Exception type: {type(e).__name__}, Project: {project_path}",
            ) from e
