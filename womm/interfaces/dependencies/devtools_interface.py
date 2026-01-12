#!/usr/bin/env python3
"""
Development Tools Manager for Works On My Machine.
Manages language-specific development tools (black, isort, eslint, etc.).
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import shutil
import sys
from pathlib import Path

# Local imports
from ...exceptions.common import ValidationServiceError
from ...exceptions.dependencies import DevToolsInterfaceError
from ...exceptions.womm_deployment import (
    DependencyServiceError,
)
from ...services import CommandRunnerService, DevToolsService
from ...shared.configs.dependencies.devtools_config import DevToolsConfig
from ...shared.results.dependencies_results import DevToolResult
from ...ui.common.ezpl_bridge import (
    ezconsole,
    ezprinter,
)

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)


# ///////////////////////////////////////////////////////////////
# DEVELOPMENT TOOLS DEFINITIONS
# ///////////////////////////////////////////////////////////////

# DEVTOOLS_DEPENDENCIES, DEFAULT_RUNTIME_PACKAGE_MANAGER, and TOOL_CONFIGS from DevToolsConfig
# Import from config instead of defining here
DEVTOOLS_DEPENDENCIES = DevToolsConfig.DEVTOOLS_DEPENDENCIES
DEFAULT_RUNTIME_PACKAGE_MANAGER = DevToolsConfig.DEFAULT_RUNTIME_PACKAGE_MANAGER
TOOL_CONFIGS = DevToolsConfig.TOOL_CONFIGS

# Backward compatibility aliases
DEV_TOOLS = DEVTOOLS_DEPENDENCIES
INSTALLATION_METHODS = DEFAULT_RUNTIME_PACKAGE_MANAGER


# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class DevToolsInterface:
    """Manages development tools for different languages."""

    def __init__(self):
        """
        Initialize the development tools manager.

        Raises:
            DevToolsError: If development tools manager initialization fails
        """
        try:
            self.cache = {}
            self._command_runner: CommandRunnerService | None = None
            self._dev_tools_service: DevToolsService | None = None

        except Exception as e:
            logger.error(f"Failed to initialize DevToolsManager: {e}")
            raise DevToolsInterfaceError(
                tool_name="dev_tools_manager",
                operation="initialization",
                message=f"Failed to initialize development tools manager: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # SERVICE PROPERTIES (LAZY INITIALIZATION)
    # ///////////////////////////////////////////////////////////////

    @property
    def command_runner(self) -> CommandRunnerService:
        """Lazy load CommandRunnerService when needed."""
        if self._command_runner is None:
            self._command_runner = CommandRunnerService()
        return self._command_runner

    @property
    def dev_tools_service(self) -> DevToolsService:
        """Lazy load DevToolsService when needed."""
        if self._dev_tools_service is None:
            self._dev_tools_service = DevToolsService()
        return self._dev_tools_service

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def check_dev_tool(self, language: str, tool_type: str, tool: str) -> DevToolResult:
        """
        Check if a development tool is installed.

        Args:
            language: Programming language (python, javascript, etc.)
            tool_type: Type of tool (formatting, linting, etc.)
            tool: Name of the tool

        Returns:
            DevToolResult: Result of the check operation

        Raises:
            DevToolsError: If tool check fails
            ValidationError: If validation fails
        """
        try:
            # Input validation
            if not language or not tool_type or not tool:
                raise ValidationServiceError(
                    operation="dev_tool_check",
                    field="parameters",
                    reason="Language, tool_type, and tool must not be empty",
                    details="All parameters must be non-empty strings",
                )

            cache_key = f"{language}:{tool_type}:{tool}"

            if cache_key in self.cache:
                available = self.cache[cache_key]
                return DevToolResult(
                    success=available,
                    tool_name=tool,
                    language=language,
                    tool_type=tool_type,
                    path=shutil.which(tool) if available else None,
                    message=f"Dev tool {tool} {'available' if available else 'not found'}",
                    error=None if available else f"Dev tool {tool} not installed",
                )

            # Check if tool is available
            try:
                available = self.dev_tools_service.check_tool_availability(tool)
            except Exception as e:
                logger.warning(f"Failed to check tool availability for {tool}: {e}")
                available = False

            self.cache[cache_key] = available

            return DevToolResult(
                success=available,
                tool_name=tool,
                language=language,
                tool_type=tool_type,
                path=shutil.which(tool) if available else None,
                message=f"Dev tool {tool} {'available' if available else 'not found'}",
                error=None if available else f"Dev tool {tool} not installed",
            )

        except (DevToolsInterfaceError, ValidationServiceError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in check_dev_tool: {e}")
            raise DevToolsInterfaceError(
                tool_name=tool,
                operation="check",
                message=f"Failed to check development tool: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def install_dev_tool(
        self, language: str, tool_type: str, tool: str
    ) -> DevToolResult:
        """
        Install a development tool with integrated UI feedback.

        Delegates to DevToolsService which handles full dependency chain resolution
        via DependencyHierarchy (devtool → runtime_package_manager → runtime).

        Args:
            language: Programming language (python, javascript, etc.)
            tool_type: Type of tool (formatting, linting, etc.)
            tool: Name of the tool

        Returns:
            DevToolResult: Result of the installation operation

        Raises:
            DevToolsError: If tool installation fails
            ValidationError: If validation fails
        """
        try:
            # Input validation
            if not language or not tool_type or not tool:
                raise ValidationServiceError(
                    component="dev_tool_installation",
                    validation_type="input_validation",
                    message="Language, tool_type, and tool must not be empty",
                    details="All parameters must be non-empty strings",
                )

            with ezprinter.create_spinner_with_status(f"Installing {tool}...") as (
                progress,
                task,
            ):
                # Check if already installed
                progress.update(task, status="Checking current installation...")
                try:
                    check_result = self.check_dev_tool(language, tool_type, tool)
                    if check_result.success:
                        progress.update(task, status="Already installed")
                        ezprinter.success(f"Dev tool {tool} already installed")
                        return DevToolResult(
                            success=True,
                            tool_name=tool,
                            language=language,
                            tool_type=tool_type,
                            path=shutil.which(tool),
                            message=f"Dev tool {tool} already installed",
                        )
                except Exception as e:
                    logger.warning(
                        f"Failed to check if tool {tool} is already installed: {e}"
                    )

                # Delegate to service - it handles full dependency chain
                progress.update(
                    task, status="Resolving dependencies via DependencyHierarchy..."
                )
                try:
                    result = self.dev_tools_service.install_devtool(tool)
                except ValidationServiceError as e:
                    progress.update(task, status="Validation failed")
                    ezprinter.error(f"Invalid tool: {e.reason}")
                    return DevToolResult(
                        success=False,
                        tool_name=tool,
                        language=language,
                        tool_type=tool_type,
                        message=f"Invalid tool: {e.reason}",
                        error=str(e),
                    )
                except Exception as e:
                    progress.update(task, status="Installation failed")
                    logger.error(f"Failed to install tool {tool}: {e}")
                    ezprinter.error(f"Failed to install dev tool {tool}: {e}")
                    return DevToolResult(
                        success=False,
                        tool_name=tool,
                        language=language,
                        tool_type=tool_type,
                        message=f"Failed to install dev tool {tool}",
                        error=str(e),
                    )

                # Clear cache for this tool
                try:
                    self._clear_tool_cache(language, tool_type, tool)
                except Exception as e:
                    logger.warning(f"Failed to clear cache for {tool}: {e}")

                if result.success and result.is_available:
                    progress.update(task, status="Installation completed successfully!")
                    ezprinter.success(f"Dev tool {tool} installed successfully")
                    return DevToolResult(
                        success=True,
                        tool_name=tool,
                        language=language,
                        tool_type=tool_type,
                        path=shutil.which(tool),
                        message=f"Dev tool {tool} installed successfully",
                    )
                else:
                    progress.update(task, status="Installation failed")
                    ezprinter.error(f"Failed to install dev tool {tool}")
                    return DevToolResult(
                        success=False,
                        tool_name=tool,
                        language=language,
                        tool_type=tool_type,
                        message=f"Failed to install dev tool {tool}",
                        error="Installation failed",
                    )

        except (
            DevToolsInterfaceError,
            DependencyServiceError,
            ValidationServiceError,
        ):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in install_dev_tool: {e}")
            raise DevToolsInterfaceError(
                tool_name=tool,
                operation="installation",
                message=f"Failed to install development tool: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def check_and_install_dev_tools(self, language: str) -> dict[str, DevToolResult]:
        """
        Check and install all dev tools for a language with integrated UI.

        Args:
            language: Programming language to check and install tools for

        Returns:
            dict[str, DevToolResult]: Results for each tool

        Raises:
            DevToolsError: If dev tools check/installation fails
            ValidationError: If validation fails
        """
        try:
            # Input validation
            if not language:
                raise ValidationServiceError(
                    component="dev_tools_check_and_install",
                    validation_type="input_validation",
                    message="Language must not be empty",
                    details="Language parameter must be a non-empty string",
                )

            if language not in DEV_TOOLS:
                ezprinter.error(f"Language {language} not supported")
                return {
                    "error": DevToolResult(
                        success=False,
                        tool_name="",
                        language=language,
                        tool_type="",
                        message=f"Language {language} not supported",
                        error=f"Language {language} not supported",
                    )
                }

            ezprinter.deps(f"Checking and installing {language} development tools...")

            results = {}
            total_tools = sum(len(tools) for tools in DEV_TOOLS[language].values())
            processed = 0

            with ezprinter.create_spinner_with_status(
                f"Processing {language} dev tools..."
            ) as (
                progress,
                task,
            ):
                for tool_type, tools in DEV_TOOLS[language].items():
                    for tool in tools:
                        processed += 1
                        progress.update(
                            task,
                            status=f"Processing {tool} ({processed}/{total_tools})...",
                        )

                        try:
                            result = self.check_dev_tool(language, tool_type, tool)
                            if not result.success:
                                # Try to install the tool
                                progress.update(task, status=f"Installing {tool}...")
                                result = self.install_dev_tool(
                                    language, tool_type, tool
                                )
                            else:
                                ezprinter.success(f"Dev tool {tool} already available")
                        except (
                            DevToolsInterfaceError,
                            ValidationServiceError,
                        ):
                            # Re-raise our custom exceptions
                            raise
                        except Exception as e:
                            logger.warning(f"Failed to process tool {tool}: {e}")
                            result = DevToolResult(
                                success=False,
                                tool_name=tool,
                                language=language,
                                tool_type=tool_type,
                                message=f"Failed to process tool {tool}",
                                error=str(e),
                            )

                        results[tool] = result

                progress.update(task, status="All tools processed!")

            # Summary
            successful = sum(1 for result in results.values() if result.success)
            ezprinter.deps(
                f"Development tools summary: {successful}/{len(results)} tools available"
            )

            return results

        except (DevToolsInterfaceError, ValidationServiceError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in check_and_install_dev_tools: {e}")
            raise DevToolsInterfaceError(
                tool_name="dev_tools_manager",
                operation="check_and_install",
                message=f"Failed to check and install development tools: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def get_required_tools(self, language: str) -> list[str]:
        """
        Get list of required tools for a language.

        Args:
            language: Programming language

        Returns:
            list[str]: List of required tools

        Raises:
            ValidationError: If validation fails
        """
        try:
            # Input validation
            if not language:
                raise ValidationServiceError(
                    component="get_required_tools",
                    validation_type="input_validation",
                    message="Language must not be empty",
                    details="Language parameter must be a non-empty string",
                )

            if language not in DEV_TOOLS:
                return []

            tools = []
            for _, tool_list in DEV_TOOLS[language].items():
                tools.extend(tool_list)

            return tools

        except ValidationServiceError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in get_required_tools: {e}")
            raise ValidationServiceError(
                component="get_required_tools",
                validation_type="unexpected_error",
                message=f"Failed to get required tools: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def get_tool_status(self, language: str | None = None) -> dict[str, dict]:
        """
        Get comprehensive status of development tools with UI output.

        Args:
            language: Specific language to check (optional)

        Returns:
            dict[str, dict]: Status information for each tool

        Raises:
            DevToolsError: If tool status check fails
            ValidationError: If validation fails
        """
        try:
            status = {}
            languages_to_check = [language] if language else DEV_TOOLS.keys()

            with ezprinter.create_spinner("Checking dev tools status...") as (
                progress,
                task,
            ):
                for lang in languages_to_check:
                    if lang not in DEV_TOOLS:
                        continue

                    progress.update(
                        task,
                        description=f"Checking {lang} tools...",
                    )

                    status[lang] = {}
                    for tool_type, tools in DEV_TOOLS[lang].items():
                        status[lang][tool_type] = {}
                        for tool in tools:
                            try:
                                available = (
                                    self.dev_tools_service.check_tool_availability(tool)
                                )
                                status[lang][tool_type][tool] = {
                                    "installed": available,
                                    "path": shutil.which(tool) if available else None,
                                    "supported": True,
                                }
                            except Exception as e:
                                logger.warning(
                                    f"Failed to check status for {tool}: {e}"
                                )
                                status[lang][tool_type][tool] = {
                                    "installed": False,
                                    "path": None,
                                    "supported": True,
                                }

            # Display results in a table
            if status:
                try:
                    self._display_status_table(status)
                except Exception as e:
                    logger.warning(f"Failed to display status table: {e}")

            return status

        except (DevToolsInterfaceError, ValidationServiceError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in get_tool_status: {e}")
            raise DevToolsInterfaceError(
                tool_name="dev_tools_manager",
                operation="get_status",
                message=f"Failed to get tool status: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _display_status_table(self, status: dict[str, dict]) -> None:
        """
        Display development tools status in a formatted table.

        Args:
            status: Status information to display

        Raises:
            DevToolsError: If table display fails
        """
        try:
            from rich.table import Table

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Language", style="cyan")
            table.add_column("Tool Type", style="blue")
            table.add_column("Tool", style="white")
            table.add_column("Status", justify="center")
            table.add_column("Path", style="dim")

            for language, lang_tools in status.items():
                for tool_type, tools in lang_tools.items():
                    for tool, info in tools.items():
                        status_icon = "✅" if info["installed"] else "❌"
                        status_text = "Installed" if info["installed"] else "Missing"
                        path_text = info.get("path", "Not found") or "Not found"

                        table.add_row(
                            language,
                            tool_type,
                            tool,
                            f"{status_icon} {status_text}",
                            path_text,
                        )

            ezconsole.print("\n")
            ezconsole.print(table)
            ezconsole.print("\n")

        except Exception as e:
            logger.error(f"Failed to display status table: {e}")
            raise DevToolsInterfaceError(
                tool_name="dev_tools_manager",
                operation="display_status_table",
                message=f"Failed to display status table: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # Methods _check_tool_availability and _get_installation_method
    # have been moved to DevToolsService

    def _install_python_tool(self, tool: str) -> bool:
        """
        Install a Python development tool.

        Args:
            tool: Name of the tool to install

        Returns:
            bool: True if installation successful, False otherwise

        Raises:
            InstallationError: If installation fails
        """
        try:
            # Input validation
            if not tool:
                raise ValidationServiceError(
                    component="python_tool_installation",
                    validation_type="input_validation",
                    message="Tool name must not be empty",
                    details="Tool parameter must be a non-empty string",
                )

            cmd = [sys.executable, "-m", "pip", "install", tool]
            try:
                result = self.command_runner.run(cmd)
                return result.success
            except Exception as e:
                logger.error(f"Failed to install Python tool {tool}: {e}")
                raise DependencyServiceError(
                    component=tool,
                    operation="python_installation",
                    message=f"Failed to install Python tool: {e}",
                    details=f"Command: {' '.join(cmd)}",
                ) from e

        except (DependencyServiceError, ValidationServiceError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _install_python_tool: {e}")
            raise DependencyServiceError(
                component=tool,
                operation="python_installation",
                message=f"Failed to install Python tool: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _install_javascript_tool(self, tool: str) -> bool:
        """
        Install a JavaScript development tool.

        Args:
            tool: Name of the tool to install

        Returns:
            bool: True if installation successful, False otherwise

        Raises:
            InstallationError: If installation fails
        """
        try:
            # Input validation
            if not tool:
                raise ValidationServiceError(
                    component="javascript_tool_installation",
                    validation_type="input_validation",
                    message="Tool name must not be empty",
                    details="Tool parameter must be a non-empty string",
                )
            # Resolve npm executable robustly (handles .venv PATH issues on Windows)
            npm_executable = shutil.which("npm")
            if not npm_executable:
                # Fallback to common Windows install locations
                fallback_paths = [
                    r"C:\\Program Files\\nodejs\\npm.cmd",
                    r"C:\\Program Files\\nodejs\\npm",
                    str(Path.home() / "AppData/Roaming/npm/npm.cmd"),
                    str(Path.home() / "AppData/Roaming/npm/npm"),
                ]
                for candidate in fallback_paths:
                    if Path(candidate).exists():
                        npm_executable = candidate
                        break

            if not npm_executable:
                raise DependencyServiceError(
                    component=tool,
                    operation="javascript_installation",
                    message="npm not found in PATH or known locations",
                    details=(
                        "Ensure Node.js is installed and npm is accessible. "
                        "Tried PATH and common Windows locations."
                    ),
                )

            cmd = [npm_executable, "install", "-g", tool]
            try:
                result = self.command_runner.run(cmd)
                return result.success
            except Exception as e:
                logger.error(f"Failed to install JavaScript tool {tool}: {e}")
                raise DependencyServiceError(
                    component=tool,
                    operation="javascript_installation",
                    message=f"Failed to install JavaScript tool: {e}",
                    details=f"Command: {' '.join(cmd)}",
                ) from e

        except (DependencyServiceError, ValidationServiceError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _install_javascript_tool: {e}")
            raise DependencyServiceError(
                component=tool,
                operation="javascript_installation",
                message=f"Failed to install JavaScript tool: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _clear_tool_cache(self, language: str, tool_type: str, tool: str):
        """
        Clear cache for a specific tool.

        Args:
            language: Programming language
            tool_type: Type of tool
            tool: Name of the tool

        Raises:
            DevToolsError: If cache clearing fails
        """
        try:
            # Input validation
            if not language or not tool_type or not tool:
                raise ValidationServiceError(
                    component="clear_tool_cache",
                    validation_type="input_validation",
                    message="Language, tool_type, and tool must not be empty",
                    details="All parameters must be non-empty strings",
                )

            cache_key = f"{language}:{tool_type}:{tool}"
            if cache_key in self.cache:
                del self.cache[cache_key]

        except ValidationServiceError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _clear_tool_cache: {e}")
            raise DevToolsInterfaceError(
                tool_name=tool,
                operation="clear_cache",
                message=f"Failed to clear tool cache: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _ensure_required_runtime(
        self, install_method: str, tool: str
    ) -> tuple[bool, str | None]:
        """
        Ensure the required runtime (python/node) is available before installing a tool.

        Args:
            install_method: Installation method (pip, npm, etc.)
            tool: Name of the tool

        Returns:
            tuple[bool, str | None]: (True, None) if runtime is available or successfully installed; otherwise (False, error_message)

        Raises:
            DevToolsError: If runtime check fails
        """
        try:
            # Input validation
            if not install_method or not tool:
                raise ValidationServiceError(
                    component="ensure_required_runtime",
                    validation_type="input_validation",
                    message="Install_method and tool must not be empty",
                    details="Both parameters must be non-empty strings",
                )

            # Lazy import to avoid circular dependencies at module import time
            try:
                from .runtime_interface import RuntimeInterface

                runtime_manager = RuntimeInterface()
            except Exception as e:
                logger.error(f"Failed to import runtime manager: {e}")
                return False, f"Failed to import runtime manager: {e}"

            # Determine required runtime based on installation method or tool specifics
            required_runtime = None
            if install_method == "pip":
                required_runtime = "python"
            elif install_method == "npm" or tool in ("cspell",):
                required_runtime = "node"

            if not required_runtime:
                return False, "Unknown installation method for runtime requirement"

            # Check runtime availability
            try:
                runtime_check = runtime_manager.check_runtime(required_runtime)
                if runtime_check.success:
                    return True, None
            except Exception as e:
                logger.warning(f"Failed to check runtime {required_runtime}: {e}")

            # Attempt to install the missing runtime automatically
            try:
                runtime_install = runtime_manager.install_runtime(required_runtime)
                if runtime_install.success:
                    return True, None
            except Exception as e:
                logger.warning(f"Failed to install runtime {required_runtime}: {e}")

            return (
                False,
                f"Failed to ensure runtime {required_runtime}",
            )

        except ValidationServiceError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _ensure_required_runtime: {e}")
            raise DevToolsInterfaceError(
                tool_name=tool,
                operation="ensure_runtime",
                message=f"Failed to ensure required runtime: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e
