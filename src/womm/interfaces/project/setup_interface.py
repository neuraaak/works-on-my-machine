#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT SETUP INTERFACE - Project Setup Interface
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Project setup interface for WOMM CLI.

Handles project setup operations following the MEF pattern.
Provides unified interface for setting up existing projects with development tools.

This interface orchestrates project creation services and converts service
exceptions into a typed ``ProjectSetupResult`` — it never raises.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path

# Local imports
from ...exceptions.common import ValidationServiceError
from ...exceptions.project import ProjectServiceError
from ...services import (
    JavaScriptProjectCreationService,
    ProjectDetectionService,
    PythonProjectCreationService,
)
from ...shared.results import ProjectSetupResult
from ...utils.dependencies import probe
from ...utils.project import (
    copy_asset_type,
    validate_project_path,
    validate_project_type,
)

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class ProjectSetupInterface:
    """
    Interface for project setup operations.

    This class provides a high-level interface for setting up existing projects,
    orchestrating project setup services without rendering terminal output.
    """

    def __init__(self):
        """Initialize the project setup interface."""
        self._detection_service = ProjectDetectionService()
        self._python_service = PythonProjectCreationService()
        self._javascript_service = JavaScriptProjectCreationService()
        self.logger = logging.getLogger(__name__)

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def setup_project(
        self,
        project_path: Path,
        project_type: str | None = None,
        virtual_env: bool = False,
        install_deps: bool = False,
        setup_dev_tools: bool = False,
        setup_git_hooks: bool = False,
        **kwargs,  # noqa: ARG002
    ) -> ProjectSetupResult:
        """Set up an existing project with development tools and configuration.

        Args:
            project_path: Path to the existing project
            project_type: Type of project (python, javascript, react, vue). Auto-detected if None.
            virtual_env: Whether to create virtual environment (Python only)
            install_deps: Whether to install dependencies
            setup_dev_tools: Whether to set up development tools
            setup_git_hooks: Whether to set up Git hooks
            **kwargs: Additional project-specific options

        Returns:
            ProjectSetupResult: Result containing setup information
        """
        try:
            # Validate project path
            validate_project_path(project_path, must_exist=True, require_empty=False)
            project_path = project_path.resolve()

            # Auto-detect project type if not provided
            if project_type is None:
                detection_result = self._detection_service.detect_project_type(
                    project_path
                )
                detected_type = detection_result.project_type
                if detected_type and detected_type != "unknown":
                    project_type = detected_type
                else:
                    return ProjectSetupResult(
                        success=False,
                        project_path=project_path,
                        error=(
                            "Could not detect project type. Project type "
                            "detection failed. Please specify project type "
                            "manually."
                        ),
                    )

            if not project_type:
                return ProjectSetupResult(
                    success=False,
                    project_path=project_path,
                    error="Project type is required",
                )

            # Validate project type
            validate_project_type(project_type)

            # Check dependencies
            deps_error = self._check_dependencies(project_type)
            if deps_error:
                return ProjectSetupResult(
                    success=False,
                    project_path=project_path,
                    project_type=project_type,
                    error=deps_error,
                )

            files_modified = []
            tools_configured = []
            warnings = []

            # Copy VSCode configuration
            try:
                self._copy_vscode_config(project_path, project_type)
                tools_configured.append("vscode")
            except Exception as e:
                logger.warning(f"Failed to copy VSCode config: {e}")
                warnings.append(f"VSCode configuration skipped: {e}")

            # Set up project based on type
            if project_type == "python":
                result = self._setup_python_project(
                    project_path,
                    virtual_env=virtual_env,
                    install_deps=install_deps,
                    setup_dev_tools=setup_dev_tools,
                    setup_git_hooks=setup_git_hooks,
                )
                files_modified.extend(result.get("files_modified", []))
                tools_configured.extend(result.get("tools_configured", []))
                warnings.extend(result.get("warnings", []))
            elif project_type in ["javascript", "react", "vue"]:
                result = self._setup_javascript_project(
                    project_path,
                    project_type,
                    install_deps=install_deps,
                    setup_dev_tools=setup_dev_tools,
                    setup_git_hooks=setup_git_hooks,
                )
                files_modified.extend(result.get("files_modified", []))
                tools_configured.extend(result.get("tools_configured", []))
                warnings.extend(result.get("warnings", []))
            else:
                return ProjectSetupResult(
                    success=False,
                    project_path=project_path,
                    project_type=project_type,
                    error=(
                        f"Unsupported project type for setup: {project_type}. "
                        "Only python, javascript, react, and vue are supported"
                    ),
                )

            return ProjectSetupResult(
                success=True,
                project_path=project_path,
                project_name=project_path.name,
                project_type=project_type,
                files_modified=files_modified,
                tools_configured=tools_configured,
                warnings=warnings if warnings else None,
            )

        except (
            ProjectServiceError,
            ValidationServiceError,
            ValueError,
            OSError,
        ) as e:
            reason = getattr(e, "reason", str(e))
            return ProjectSetupResult(
                success=False,
                project_path=project_path if project_path else None,
                project_type=project_type or "",
                error=f"Failed to setup project: {reason}",
            )
        except Exception as e:
            logger.error(f"Unexpected error during project setup: {e}", exc_info=True)
            return ProjectSetupResult(
                success=False,
                project_path=project_path if project_path else None,
                project_type=project_type or "",
                error=f"Unexpected error during project setup: {e}",
            )

    def setup_development_environment(
        self, project_path: Path, project_type: str | None = None
    ) -> ProjectSetupResult:
        """Set up development environment for an existing project.

        Args:
            project_path: Path to the project
            project_type: Type of project (auto-detected if None)

        Returns:
            ProjectSetupResult: Result containing setup information
        """
        try:
            # Auto-detect project type if not provided
            if project_type is None:
                detection_result = self._detection_service.detect_project_type(
                    project_path
                )
                detected_type = detection_result.project_type
                if detected_type and detected_type != "unknown":
                    project_type = detected_type
                else:
                    return ProjectSetupResult(
                        success=False,
                        project_path=project_path,
                        error=(
                            "Could not detect project type. Project type "
                            "detection failed. Please specify project type "
                            "manually."
                        ),
                    )

            if not project_type:
                return ProjectSetupResult(
                    success=False,
                    project_path=project_path,
                    error="Project type is required",
                )

            # Use setup_project with minimal options
            return self.setup_project(
                project_path,
                project_type=project_type,
                virtual_env=(project_type == "python"),
                install_deps=True,
                setup_dev_tools=True,
                setup_git_hooks=False,
            )

        except Exception as e:
            logger.error(
                f"Unexpected error during environment setup: {e}", exc_info=True
            )
            return ProjectSetupResult(
                success=False,
                project_path=project_path if project_path else None,
                project_type=project_type or "",
                error=f"Unexpected error during environment setup: {e}",
            )

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _setup_python_project(
        self,
        project_path: Path,
        virtual_env: bool = False,
        install_deps: bool = False,
        setup_dev_tools: bool = False,
        setup_git_hooks: bool = False,
    ) -> dict[str, list[str]]:
        """Set up Python project.

        Args:
            project_path: Path to the project
            virtual_env: Whether to create virtual environment
            install_deps: Whether to install dependencies
            setup_dev_tools: Whether to set up development tools
            setup_git_hooks: Whether to set up Git hooks

        Returns:
            dict: Metadata about setup with 'files_modified', 'tools_configured', 'warnings'
        """
        files_modified = []
        tools_configured = []
        warnings = []

        # Setup virtual environment
        if virtual_env:
            try:
                venv_result = self._python_service.setup_virtual_environment(
                    project_path
                )
                if venv_result.success:
                    tools_configured.append("venv")
                else:
                    warnings.append("Virtual environment setup failed")
            except Exception as e:
                logger.warning(f"Failed to setup venv: {e}")
                warnings.append(f"Virtual environment setup skipped: {e}")

        # setup_dev_tools installs the Python development dependencies itself.
        if install_deps and not setup_dev_tools:
            try:
                deps_result = self._python_service.install_dev_dependencies(
                    project_path
                )
                if deps_result.success:
                    tools_configured.append("dependencies")
                else:
                    warnings.append("Dependency installation failed")
            except Exception as e:
                logger.warning(f"Failed to install dependencies: {e}")
                warnings.append(f"Dependency installation skipped: {e}")

        # Setup dev tools
        if setup_dev_tools:
            try:
                dev_tools_result = self._python_service.setup_dev_tools(project_path)
                if dev_tools_result.success:
                    if install_deps:
                        tools_configured.append("dependencies")
                    tools_configured.append("dev_tools")
                else:
                    warnings.append("Dev tools setup failed")
            except Exception as e:
                logger.warning(f"Failed to setup dev tools: {e}")
                warnings.append(f"Dev tools setup skipped: {e}")

        # Setup Git repository and hooks (if needed)
        if setup_git_hooks:
            try:
                git_result = self._python_service.setup_git_repository(project_path)
                if git_result.success:
                    tools_configured.append("git")
                else:
                    warnings.append("Git repository setup failed")
            except Exception as e:
                logger.warning(f"Failed to setup git repository: {e}")
                warnings.append(f"Git repository setup skipped: {e}")

        return {
            "files_modified": files_modified,
            "tools_configured": tools_configured,
            "warnings": warnings,
        }

    def _setup_javascript_project(
        self,
        project_path: Path,
        project_type: str,
        install_deps: bool = False,
        setup_dev_tools: bool = False,
        setup_git_hooks: bool = False,
    ) -> dict[str, list[str]]:
        """Set up JavaScript project.

        Args:
            project_path: Path to the project
            project_type: Type of JavaScript project (node, react, vue)
            install_deps: Whether to install dependencies
            setup_dev_tools: Whether to set up development tools
            setup_git_hooks: Whether to set up Git hooks

        Returns:
            dict: Metadata about setup with 'files_modified', 'tools_configured', 'warnings'
        """
        files_modified = []
        tools_configured = []
        warnings = []

        # Install dependencies
        if install_deps:
            try:
                deps_result = self._javascript_service.install_dependencies(
                    project_path, project_type
                )
                if deps_result.success:
                    tools_configured.append("dependencies")
                else:
                    warnings.append("Dependency installation failed")
            except Exception as e:
                logger.warning(f"Failed to install dependencies: {e}")
                warnings.append(f"Dependency installation skipped: {e}")

        # Setup dev tools
        if setup_dev_tools:
            try:
                dev_tools_result = self._javascript_service.setup_dev_tools(
                    project_path, project_type
                )
                if dev_tools_result.success:
                    tools_configured.append("dev_tools")
                else:
                    warnings.append("Dev tools setup failed")
            except Exception as e:
                logger.warning(f"Failed to setup dev tools: {e}")
                warnings.append(f"Dev tools setup skipped: {e}")

        # Setup Git repository and hooks
        if setup_git_hooks:
            try:
                git_result = self._javascript_service.setup_git_repository(project_path)
                if git_result.success:
                    tools_configured.append("git")
                else:
                    warnings.append("Git repository setup failed")
            except Exception as e:
                logger.warning(f"Failed to setup git repository: {e}")
                warnings.append(f"Git repository setup skipped: {e}")

            try:
                hooks_result = self._javascript_service.setup_git_hooks(project_path)
                if hooks_result.success:
                    tools_configured.append("git_hooks")
                else:
                    warnings.append("Git hooks setup failed")
            except Exception as e:
                logger.warning(f"Failed to setup git hooks: {e}")
                warnings.append(f"Git hooks setup skipped: {e}")

        return {
            "files_modified": files_modified,
            "tools_configured": tools_configured,
            "warnings": warnings,
        }

    def _copy_vscode_config(self, project_path: Path, project_type: str) -> None:
        """Copy VSCode configuration from assets to project.

        Args:
            project_path: Path to the project
            project_type: Type of project (python, javascript, react, vue)
        """
        # Map project_type to language and variant
        language_map = {
            "python": "python",
            "javascript": "javascript",
            "react": "javascript",
            "vue": "javascript",
        }
        variant_map = {
            "python": "py",
            "javascript": "js",
            "react": "react",
            "vue": "vue",
        }

        language = language_map.get(project_type)
        variant = variant_map.get(project_type)

        if language and variant:
            vscode_dir = project_path / ".vscode"
            copy_asset_type(language, variant, "vscode", vscode_dir, overwrite=False)
        else:
            logger.warning(
                f"No specific VSCode assets found for project type: {project_type}"
            )

    def _check_dependencies(self, project_type: str) -> str:
        """Check if required dependencies are available.

        Args:
            project_type: Type of project

        Returns:
            Empty string if dependencies are satisfied, otherwise an error message.
        """
        try:
            if project_type == "python":
                result = probe("python")
                if not result.success:
                    return "Python runtime not found. Python runtime is required for Python projects"

            elif project_type in ["javascript", "react", "vue"]:
                result = probe("node")
                if not result.success:
                    return "Node.js runtime not found. Node.js runtime is required for JavaScript projects"

            return ""

        except Exception as e:
            return f"Error checking dependencies: {e}"
