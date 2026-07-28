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
from ...exceptions.project import ProjectServiceError
from ...shared.configs.project import ProjectConfig
from ...shared.results import ProjectDetectionResult
from ...utils.project import (
    analyze_csharp_config,
    analyze_go_config,
    analyze_java_config,
    analyze_javascript_config,
    analyze_python_config,
    analyze_rust_config,
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
            ProjectServiceError: If validation fails or project detection fails
        """
        try:
            # Input validation
            if not project_path:
                raise ProjectServiceError(
                    operation="detect_project_type",
                    reason="Project path cannot be None",
                )

            if not project_path.exists():
                raise ProjectServiceError(
                    operation="detect_project_type",
                    reason="Project path does not exist",
                    details=f"Path {project_path} was not found",
                )

            if not project_path.is_dir():
                raise ProjectServiceError(
                    operation="detect_project_type",
                    reason="Project path is not a directory",
                    details=f"Path {project_path} is not a directory",
                )

            # Analyze project structure
            project_files = list(project_path.iterdir())
            project_dirs = [item for item in project_files if item.is_dir()]
            project_files = [item for item in project_files if item.is_file()]

            # Check each project type
            detected_type = None
            detected_files_by_type: dict[str, list[str]] = {}
            dir_names = [item.name for item in project_dirs]

            for project_type, indicators in ProjectConfig.PROJECT_INDICATORS.items():
                matches: list[str] = []

                for marker in indicators.get("files", []):
                    matches.extend(
                        item.name for item in project_files if item.match(marker)
                    )

                for marker in indicators.get("dirs", []):
                    if marker in dir_names:
                        matches.append(marker)

                for ext in indicators.get("extensions", []):
                    if any(f.suffix == ext for f in project_files):
                        matches.append(ext)

                if matches:
                    detected_files_by_type[project_type] = matches
                    if detected_type is None:
                        detected_type = project_type

            # Build result
            return ProjectDetectionResult(
                success=True,
                message="Project type detection completed",
                project_type=detected_type or "unknown",
                confidence=100.0 if detected_type else 0.0,
                detected_files=detected_files_by_type.get(detected_type or "", []),
                configuration_files={},
            )

        except ProjectServiceError:
            # Re-raise as-is
            raise
        except (OSError, TypeError, ValueError) as e:
            # Wrap unexpected external exceptions
            logger.exception("Unexpected error in detect_project_type")
            raise ProjectServiceError(
                operation="detect_project_type",
                reason=str(e),
                details=f"Exception type: {type(e).__name__}, Project: {project_path}",
            ) from e

    def detect_project_config(self, project_path: Path) -> ProjectDetectionResult:
        """Detect project configuration files and settings.

        Args:
            project_path: Path to the project directory

        Returns:
            ProjectDetectionResult: Result with project configuration information

        Raises:
            ProjectServiceError: If validation fails or project configuration detection fails
        """
        try:
            # Input validation
            if not project_path:
                raise ProjectServiceError(
                    operation="detect_project_config",
                    reason="Project path cannot be None",
                )

            if not project_path.exists():
                raise ProjectServiceError(
                    operation="detect_project_config",
                    reason="Project path does not exist",
                    details=f"Path {project_path} was not found",
                )

            if not project_path.is_dir():
                raise ProjectServiceError(
                    operation="detect_project_config",
                    reason="Project path is not a directory",
                    details=f"Path {project_path} is not a directory",
                )

            config_files: dict[str, str] = {}

            # Detect project type first
            type_result = self.detect_project_type(project_path)
            if not type_result.success:
                raise ProjectServiceError(
                    operation="detect_project_config",
                    reason="Unable to determine project type",
                    details="Project type detection failed",
                )

            project_type = type_result.project_type

            # Analyze configuration files based on project type
            try:
                config: dict[str, dict[str, str]] = {}
                if project_type == "python":
                    config = analyze_python_config(project_path)
                elif project_type == "javascript":
                    config = analyze_javascript_config(project_path)
                elif project_type == "java":
                    config = analyze_java_config(project_path)
                elif project_type == "go":
                    config = analyze_go_config(project_path)
                elif project_type == "rust":
                    config = analyze_rust_config(project_path)
                elif project_type == "csharp":
                    config = analyze_csharp_config(project_path)

                for section in ("markers", "details"):
                    values = config.get(section, {})
                    if isinstance(values, dict):
                        config_files.update(values)
            except (OSError, TypeError, ValueError) as e:
                logger.warning(
                    f"Failed to analyze configuration for {project_type}: {e}"
                )
                # Continue with partial results

            return ProjectDetectionResult(
                success=True,
                message="Project configuration detection completed",
                project_type=project_type,
                confidence=100.0 if project_type != "unknown" else 0.0,
                detected_files=[],
                configuration_files=config_files,
            )

        except ProjectServiceError:
            # Re-raise as-is
            raise
        except (OSError, TypeError, ValueError) as e:
            # Wrap unexpected external exceptions
            logger.exception("Unexpected error in detect_project_config")
            raise ProjectServiceError(
                operation="detect_project_config",
                reason=str(e),
                details=f"Exception type: {type(e).__name__}, Project: {project_path}",
            ) from e

    def detect_project_structure(self, project_path: Path) -> ProjectDetectionResult:
        """Detect project structure and organization.

        Args:
            project_path: Path to the project directory

        Returns:
            ProjectDetectionResult: Result with project structure information

        Raises:
            ProjectServiceError: If validation fails or project structure detection fails
        """
        try:
            # Input validation
            if not project_path:
                raise ProjectServiceError(
                    operation="detect_project_structure",
                    reason="Project path cannot be None",
                )

            if not project_path.exists():
                raise ProjectServiceError(
                    operation="detect_project_structure",
                    reason="Project path does not exist",
                    details=f"Path {project_path} was not found",
                )

            if not project_path.is_dir():
                raise ProjectServiceError(
                    operation="detect_project_structure",
                    reason="Project path is not a directory",
                    details=f"Path {project_path} is not a directory",
                )

            source_dirs: list[str] = []
            test_dirs: list[str] = []
            config_dirs: list[str] = []
            build_dirs: list[str] = []
            documentation_dirs: list[str] = []
            total_files = 0
            total_dirs = 0

            try:
                # Walk through project structure
                for item in project_path.rglob("*"):
                    if item.is_file():
                        total_files += 1
                    elif item.is_dir():
                        total_dirs += 1
                        name = item.name.lower()
                        if name in {"src", "lib", "app", "source"}:
                            source_dirs.append(str(item))
                        elif name in {"tests", "test", "__tests__"}:
                            test_dirs.append(str(item))
                        elif name in {"config", ".config", "configs"}:
                            config_dirs.append(str(item))
                        elif name in {"build", "dist", "target", "out"}:
                            build_dirs.append(str(item))
                        elif name in {"docs", "doc", "documentation"}:
                            documentation_dirs.append(str(item))

            except (PermissionError, OSError) as e:
                logger.warning(f"Permission or OS error during structure analysis: {e}")
                # Continue with partial results

            structure = {
                "source_dirs": ", ".join(source_dirs),
                "test_dirs": ", ".join(test_dirs),
                "config_dirs": ", ".join(config_dirs),
                "build_dirs": ", ".join(build_dirs),
                "documentation_dirs": ", ".join(documentation_dirs),
                "total_files": str(total_files),
                "total_dirs": str(total_dirs),
            }

            return ProjectDetectionResult(
                success=True,
                message="Project structure detection completed",
                project_type="",
                confidence=100.0,
                detected_files=[],
                configuration_files=structure,
            )

        except ProjectServiceError:
            # Re-raise as-is
            raise
        except (OSError, TypeError, ValueError) as e:
            # Wrap unexpected external exceptions
            logger.exception("Unexpected error in detect_project_structure")
            raise ProjectServiceError(
                operation="detect_project_structure",
                reason=str(e),
                details=f"Exception type: {type(e).__name__}, Project: {project_path}",
            ) from e
