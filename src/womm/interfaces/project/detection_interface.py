#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT DETECTION INTERFACE - Project Detection Interface
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Project detection interface for WOMM CLI.

Handles project type detection operations following the MEF pattern.
Provides unified interface for detecting project types and configurations.

This interface orchestrates ProjectDetectionService and converts service
exceptions into a typed ``ProjectDetectionResult`` — it never raises.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path

# Local imports
from ...exceptions.project import ProjectServiceError
from ...services import ProjectDetectionService
from ...shared.results import ProjectDetectionResult
from ...ui.common import ezprinter

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class ProjectDetectionInterface:
    """
    Interface for project type detection operations.

    This class provides a high-level interface for project detection operations,
    handling UI interactions and orchestrating project detection services.
    """

    def __init__(self):
        """Initialize the project detection interface."""
        self._detection_service = ProjectDetectionService()
        self.logger = logging.getLogger(__name__)

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def detect_project_type(
        self, project_path: Path | None = None
    ) -> ProjectDetectionResult:
        """Detect the type of project at the given path.

        Args:
            project_path: Path to the project directory (defaults to current directory)

        Returns:
            ProjectDetectionResult: Result containing detected project type and metadata
        """
        try:
            # Use current directory if no path provided
            resolved_path = (project_path or Path.cwd()).resolve()

            ezprinter.info(f"Detecting project type at: {resolved_path}")

            # Call service to detect project type
            type_result = self._detection_service.detect_project_type(resolved_path)
            detected_type = (
                type_result.project_type
                if isinstance(type_result, ProjectDetectionResult)
                else ""
            )

            # Get additional configuration information
            config_files: dict[str, str] = {}
            detected_files: list[str] = []
            confidence = 0.0

            if detected_type and detected_type != "unknown":
                try:
                    config_result = self._detection_service.detect_project_config(
                        resolved_path
                    )
                    if isinstance(config_result, ProjectDetectionResult):
                        config_files = config_result.configuration_files or {}
                        detected_files = config_result.detected_files or []
                    confidence = 100.0  # High confidence when type is detected
                except ProjectServiceError:
                    # If config detection fails, we still have the type
                    logger.warning(
                        f"Could not detect full configuration for {detected_type} project"
                    )
                    confidence = 75.0  # Lower confidence without full config
            else:
                confidence = 0.0
                ezprinter.warning("Could not detect project type")

            if detected_type:
                ezprinter.success(
                    f"Detected project type: {detected_type} (confidence: {confidence:.0f}%)"
                )
            else:
                ezprinter.warning("Project type could not be determined")

            return ProjectDetectionResult(
                success=True,
                project_type=detected_type or "unknown",
                confidence=confidence,
                detected_files=detected_files,
                configuration_files=config_files,
            )

        except ProjectServiceError as e:
            return ProjectDetectionResult(
                success=False,
                error=f"Failed to detect project type: {e.reason}",
            )
        except Exception as e:
            logger.error(
                f"Unexpected error during project detection: {e}", exc_info=True
            )
            return ProjectDetectionResult(
                success=False,
                error=f"Unexpected error during project detection: {e}",
            )

    def detect_project_config(
        self, project_path: Path | None = None
    ) -> ProjectDetectionResult:
        """Detect project configuration files and settings.

        Args:
            project_path: Path to the project directory (defaults to current directory)

        Returns:
            ProjectDetectionResult: Result containing project configuration information
        """
        try:
            # Use current directory if no path provided
            resolved_path = (project_path or Path.cwd()).resolve()

            ezprinter.info(f"Detecting project configuration at: {resolved_path}")

            # Call service to detect project configuration
            config_result = self._detection_service.detect_project_config(resolved_path)
            detected_type = (
                config_result.project_type
                if isinstance(config_result, ProjectDetectionResult)
                else ""
            )
            config_files = (
                config_result.configuration_files
                if isinstance(config_result, ProjectDetectionResult)
                else {}
            )
            detected_files = (
                list(config_result.detected_files or [])
                if isinstance(config_result, ProjectDetectionResult)
                else []
            )

            if detected_type:
                ezprinter.success(
                    f"Detected {detected_type} project with {len(detected_files)} configuration files"
                )
            else:
                ezprinter.warning("Project configuration could not be determined")

            return ProjectDetectionResult(
                success=True,
                project_type=str(detected_type) if detected_type else "unknown",
                confidence=100.0 if detected_type else 0.0,
                detected_files=detected_files,
                configuration_files=config_files,
            )

        except ProjectServiceError as e:
            return ProjectDetectionResult(
                success=False,
                error=f"Failed to detect project configuration: {e.reason}",
            )
        except Exception as e:
            logger.error(
                f"Unexpected error during project configuration detection: {e}",
                exc_info=True,
            )
            return ProjectDetectionResult(
                success=False,
                error=f"Unexpected error during project configuration detection: {e}",
            )
