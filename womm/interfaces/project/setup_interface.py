#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT SETUP INTERFACE - Project Setup Interface
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Project setup interface for WOMM CLI.

Handles project setup operations following the MEF pattern.
Provides unified interface for setting up existing projects with development tools.

This interface orchestrates project creation services and converts service exceptions
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
from ...exceptions.common import ValidationServiceError
from ...exceptions.project import ProjectServiceError, SetupInterfaceError
from ...services import (
    JavaScriptProjectCreationService,
    ProjectDetectionService,
    PythonProjectCreationService,
)
from ...shared.results import ProjectSetupResult
from ...ui.common import ezprinter
from ...utils.project import (
    copy_asset_type,
    validate_project_path,
    validate_project_type,
)
from ..dependencies.runtime_interface import RuntimeInterface

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
    handling UI interactions and orchestrating project setup services.
    """

    def __init__(self):
        """Initialize the project setup interface.

        Raises:
            ProjectSetupInterfaceError: If interface initialization fails
        """
        try:
            self._detection_service = ProjectDetectionService()
            self._python_service = PythonProjectCreationService()
            self._javascript_service = JavaScriptProjectCreationService()
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            logger.error(
                f"Failed to initialize ProjectSetupInterface: {e}", exc_info=True
            )
            raise SetupInterfaceError(
                message=f"Failed to initialize project setup interface: {e}",
                operation="initialization",
                details=f"Exception type: {type(e).__name__}",
            ) from e

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

        Raises:
            ProjectSetupInterfaceError: If project setup fails
        """
        try:
            # Validate project path
            validate_project_path(project_path)
            project_path = project_path.resolve()

            # Auto-detect project type if not provided
            if project_type is None:
                with ezprinter.create_spinner_with_status(
                    "Detecting project type..."
                ) as spinner:
                    detected_type = self._detection_service.detect_project_type(
                        project_path
                    )
                    if detected_type:
                        project_type = detected_type
                        spinner.update_status(f"Detected: {project_type}")
                    else:
                        raise SetupInterfaceError(
                            message="Could not detect project type",
                            operation="setup_project",
                            project_path=str(project_path),
                            details="Project type detection failed. Please specify project type manually.",
                        )

            # Validate project type
            validate_project_type(project_type)

            # Check dependencies
            self._check_dependencies(project_type)

            ezprinter.print_header(f"Setting up {project_type} project")

            files_modified = []
            tools_configured = []
            warnings = []

            # Copy VSCode configuration
            with ezprinter.create_spinner_with_status(
                "Configuring VSCode settings..."
            ) as spinner:
                try:
                    self._copy_vscode_config(project_path, project_type)
                    tools_configured.append("vscode")
                    spinner.update_status("VSCode configured")
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
                raise SetupInterfaceError(
                    message=f"Unsupported project type for setup: {project_type}",
                    operation="setup_project",
                    project_path=str(project_path),
                    project_type=project_type,
                    details="Only python, javascript, react, and vue are supported",
                )

            ezprinter.success(
                f"Project setup completed ({len(tools_configured)} tools configured)"
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

        except (ProjectServiceError, ValidationServiceError) as e:
            # Convert service exceptions to interface exceptions
            raise SetupInterfaceError(
                message=f"Failed to setup project: {e.message if hasattr(e, 'message') else str(e)}",
                operation="setup_project",
                project_path=str(project_path) if project_path else "",
                project_type=project_type or "",
                details=(
                    e.details
                    if hasattr(e, "details")
                    else f"Exception type: {type(e).__name__}"
                ),
            ) from e
        except SetupInterfaceError:
            raise
        except Exception as e:
            # Wrap unexpected exceptions
            logger.error(f"Unexpected error during project setup: {e}", exc_info=True)
            raise SetupInterfaceError(
                message=f"Unexpected error during project setup: {e}",
                operation="setup_project",
                project_path=str(project_path) if project_path else "",
                project_type=project_type or "",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def setup_development_environment(
        self, project_path: Path, project_type: str | None = None
    ) -> ProjectSetupResult:
        """Set up development environment for an existing project.

        Args:
            project_path: Path to the project
            project_type: Type of project (auto-detected if None)

        Returns:
            ProjectSetupResult: Result containing setup information

        Raises:
            ProjectSetupInterfaceError: If environment setup fails
        """
        try:
            # Auto-detect project type if not provided
            if project_type is None:
                detected_type = self._detection_service.detect_project_type(
                    project_path
                )
                if detected_type:
                    project_type = detected_type
                else:
                    raise SetupInterfaceError(
                        message="Could not detect project type",
                        operation="setup_development_environment",
                        project_path=str(project_path),
                        details="Project type detection failed. Please specify project type manually.",
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

        except SetupInterfaceError:
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error during environment setup: {e}", exc_info=True
            )
            raise SetupInterfaceError(
                message=f"Unexpected error during environment setup: {e}",
                operation="setup_development_environment",
                project_path=str(project_path) if project_path else "",
                project_type=project_type or "",
                details=f"Exception type: {type(e).__name__}",
            ) from e

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
            with ezprinter.create_spinner_with_status(
                "Setting up virtual environment..."
            ) as spinner:
                try:
                    venv_result = self._python_service.setup_virtual_environment(
                        project_path
                    )
                    if venv_result.get("success"):
                        tools_configured.append("venv")
                        spinner.update_status("Virtual environment ready")
                    else:
                        warnings.append("Virtual environment setup failed")
                except Exception as e:
                    logger.warning(f"Failed to setup venv: {e}")
                    warnings.append(f"Virtual environment setup skipped: {e}")

        # Install dependencies
        if install_deps:
            with ezprinter.create_spinner_with_status(
                "Installing dependencies..."
            ) as spinner:
                try:
                    deps_result = self._python_service.install_dev_dependencies(
                        project_path
                    )
                    if deps_result.get("success"):
                        tools_configured.append("dependencies")
                        spinner.update_status("Dependencies installed")
                    else:
                        warnings.append("Dependency installation failed")
                except Exception as e:
                    logger.warning(f"Failed to install dependencies: {e}")
                    warnings.append(f"Dependency installation skipped: {e}")

        # Setup dev tools
        if setup_dev_tools:
            with ezprinter.create_spinner_with_status(
                "Setting up development tools..."
            ) as spinner:
                try:
                    dev_tools_result = self._python_service.setup_dev_tools(
                        project_path
                    )
                    if dev_tools_result.get("success"):
                        tools_configured.append("dev_tools")
                        spinner.update_status("Development tools configured")
                    else:
                        warnings.append("Dev tools setup failed")
                except Exception as e:
                    logger.warning(f"Failed to setup dev tools: {e}")
                    warnings.append(f"Dev tools setup skipped: {e}")

        # Setup Git repository and hooks (if needed)
        if setup_git_hooks:
            with ezprinter.create_spinner_with_status(
                "Setting up Git repository..."
            ) as spinner:
                try:
                    git_result = self._python_service.setup_git_repository(project_path)
                    if git_result.get("success"):
                        tools_configured.append("git")
                        spinner.update_status("Git repository initialized")
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
            with ezprinter.create_spinner_with_status(
                "Installing dependencies..."
            ) as spinner:
                try:
                    deps_result = self._javascript_service.install_dependencies(
                        project_path, project_type
                    )
                    if deps_result.get("success"):
                        tools_configured.append("dependencies")
                        spinner.update_status("Dependencies installed")
                    else:
                        warnings.append("Dependency installation failed")
                except Exception as e:
                    logger.warning(f"Failed to install dependencies: {e}")
                    warnings.append(f"Dependency installation skipped: {e}")

        # Setup dev tools
        if setup_dev_tools:
            with ezprinter.create_spinner_with_status(
                "Setting up development tools..."
            ) as spinner:
                try:
                    dev_tools_result = self._javascript_service.setup_dev_tools(
                        project_path, project_type
                    )
                    if dev_tools_result.get("success"):
                        tools_configured.append("dev_tools")
                        spinner.update_status("Development tools configured")
                    else:
                        warnings.append("Dev tools setup failed")
                except Exception as e:
                    logger.warning(f"Failed to setup dev tools: {e}")
                    warnings.append(f"Dev tools setup skipped: {e}")

        # Setup Git repository and hooks
        if setup_git_hooks:
            with ezprinter.create_spinner_with_status(
                "Setting up Git repository..."
            ) as spinner:
                try:
                    git_result = self._javascript_service.setup_git_repository(
                        project_path
                    )
                    if git_result.get("success"):
                        tools_configured.append("git")
                        spinner.update_status("Git repository initialized")
                    else:
                        warnings.append("Git repository setup failed")
                except Exception as e:
                    logger.warning(f"Failed to setup git repository: {e}")
                    warnings.append(f"Git repository setup skipped: {e}")

            with ezprinter.create_spinner_with_status(
                "Setting up Git hooks..."
            ) as spinner:
                try:
                    hooks_result = self._javascript_service.setup_git_hooks(
                        project_path
                    )
                    if hooks_result.get("success"):
                        tools_configured.append("git_hooks")
                        spinner.update_status("Git hooks configured")
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

    def _check_dependencies(self, project_type: str) -> None:
        """Check if required dependencies are available.

        Args:
            project_type: Type of project

        Raises:
            ProjectSetupInterfaceError: If required dependencies are not available
        """
        try:
            if project_type == "python":
                runtime_manager = RuntimeInterface()
                result = runtime_manager.check_runtime("python")
                if not result.success:
                    raise SetupInterfaceError(
                        message="Python runtime not found",
                        operation="check_dependencies",
                        project_type=project_type,
                        details="Python runtime is required for Python projects",
                    )

            elif project_type in ["javascript", "react", "vue"]:
                runtime_manager = RuntimeInterface()
                result = runtime_manager.check_runtime("node")
                if not result.success:
                    raise SetupInterfaceError(
                        message="Node.js runtime not found",
                        operation="check_dependencies",
                        project_type=project_type,
                        details="Node.js runtime is required for JavaScript projects",
                    )

        except SetupInterfaceError:
            raise
        except Exception as e:
            raise SetupInterfaceError(
                message=f"Error checking dependencies: {e}",
                operation="check_dependencies",
                project_type=project_type,
                details=f"Exception type: {type(e).__name__}",
            ) from e
