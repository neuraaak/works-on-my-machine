#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT DETECTION INTERFACE - Project Detection Interface
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Project detection interface for WOMM CLI.

Handles project type detection operations following the MEF pattern.
Provides unified interface for detecting project types and configurations.

This interface orchestrates ProjectDetectionService and converts service exceptions
to interface exceptions.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path

# Local imports
from ...exceptions.project import (
    ProjectDetectionInterfaceError,
    ProjectDetectionServiceError,
    ProjectServiceError,
)
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
        """Initialize the project detection interface.

        Raises:
            ProjectDetectionInterfaceError: If interface initialization fails
        """
        try:
            self._detection_service = ProjectDetectionService()
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            logger.error(
                f"Failed to initialize ProjectDetectionInterface: {e}", exc_info=True
            )
            raise ProjectDetectionInterfaceError(
                message=f"Failed to initialize project detection interface: {e}",
                operation="initialization",
                details=f"Exception type: {type(e).__name__}",
            ) from e

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

        Raises:
            ProjectDetectionInterfaceError: If project detection fails
        """
        try:
            # Use current directory if no path provided
            if project_path is None:
                project_path = Path.cwd()

            # Normalize path
            project_path = project_path.resolve()

            ezprinter.info(f"Detecting project type at: {project_path}")

            # Call service to detect project type
            detected_type = self._detection_service.detect_project_type(project_path)

            # Get additional configuration information
            config_info = {}
            detected_files = []
            confidence = 0.0

            if detected_type:
                try:
                    config_info = self._detection_service.detect_project_config(
                        project_path
                    )
                    # Extract detected files from config
                    if isinstance(config_info, dict):
                        config_files = config_info.get("config_files", {})
                        if isinstance(config_files, dict):
                            detected_files = list(config_files.keys())
                    confidence = 100.0  # High confidence when type is detected
                except (ProjectServiceError, ProjectDetectionServiceError):
                    # If config detection fails, we still have the type
                    logger.warning(
                        f"Could not detect full configuration for {detected_type} project"
                    )
                    confidence = 75.0  # Lower confidence without full config
            else:
                confidence = 0.0
                ezprinter.warning("Could not detect project type")

            # Build result
            result = ProjectDetectionResult(
                success=True,
                project_type=detected_type or "unknown",
                confidence=confidence,
                detected_files=detected_files,
                configuration_files=(
                    config_info.get("config_files", {})
                    if isinstance(config_info, dict)
                    else {}
                ),
            )

            if detected_type:
                ezprinter.success(
                    f"Detected project type: {detected_type} (confidence: {confidence:.0f}%)"
                )
            else:
                ezprinter.warning("Project type could not be determined")

            return result

        except (ProjectServiceError, ProjectDetectionServiceError) as e:
            # Convert service exceptions to interface exceptions
            raise ProjectDetectionInterfaceError(
                message=f"Failed to detect project type: {e.message if hasattr(e, 'message') else str(e)}",
                operation="detect_project_type",
                project_path=str(project_path) if project_path else "",
                details=(
                    e.details
                    if hasattr(e, "details")
                    else f"Exception type: {type(e).__name__}"
                ),
            ) from e
        except Exception as e:
            # Wrap unexpected exceptions
            logger.error(
                f"Unexpected error during project detection: {e}", exc_info=True
            )
            raise ProjectDetectionInterfaceError(
                message=f"Unexpected error during project detection: {e}",
                operation="detect_project_type",
                project_path=str(project_path) if project_path else "",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def detect_project_config(
        self, project_path: Path | None = None
    ) -> ProjectDetectionResult:
        """Detect project configuration files and settings.

        Args:
            project_path: Path to the project directory (defaults to current directory)

        Returns:
            ProjectDetectionResult: Result containing project configuration information

        Raises:
            ProjectDetectionInterfaceError: If project configuration detection fails
        """
        try:
            # Use current directory if no path provided
            if project_path is None:
                project_path = Path.cwd()

            # Normalize path
            project_path = project_path.resolve()

            ezprinter.info(f"Detecting project configuration at: {project_path}")

            # Call service to detect project configuration
            config_info = self._detection_service.detect_project_config(project_path)

            # Extract information from config
            detected_type = config_info.get("project_type") if config_info else None
            config_files = (
                config_info.get("config_files", {})
                if isinstance(config_info, dict)
                else {}
            )
            detected_files = list(config_files.keys()) if config_files else []

            # Build result
            result = ProjectDetectionResult(
                success=True,
                project_type=str(detected_type) if detected_type else "unknown",
                confidence=100.0 if detected_type else 0.0,
                detected_files=detected_files,
                configuration_files=(
                    config_files if isinstance(config_files, dict) else {}
                ),
            )

            if detected_type:
                ezprinter.success(
                    f"Detected {detected_type} project with {len(detected_files)} configuration files"
                )
            else:
                ezprinter.warning("Project configuration could not be determined")

            return result

        except (ProjectServiceError, ProjectDetectionServiceError) as e:
            # Convert service exceptions to interface exceptions
            raise ProjectDetectionInterfaceError(
                message=f"Failed to detect project configuration: {e.message if hasattr(e, 'message') else str(e)}",
                operation="detect_project_config",
                project_path=str(project_path) if project_path else "",
                details=(
                    e.details
                    if hasattr(e, "details")
                    else f"Exception type: {type(e).__name__}"
                ),
            ) from e
        except Exception as e:
            # Wrap unexpected exceptions
            logger.error(
                f"Unexpected error during project configuration detection: {e}",
                exc_info=True,
            )
            raise ProjectDetectionInterfaceError(
                message=f"Unexpected error during project configuration detection: {e}",
                operation="detect_project_config",
                project_path=str(project_path) if project_path else "",
                details=f"Exception type: {type(e).__name__}",
            ) from e
