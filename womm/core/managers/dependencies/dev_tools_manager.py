#!/usr/bin/env python3
"""
Development Tools Manager for Works On My Machine.
Manages language-specific development tools (black, isort, eslint, etc.).
"""

import logging
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ....common.results import BaseResult
from ...exceptions.dependencies import DevToolsError, InstallationError, ValidationError
from ...ui.common.console import print_deps, print_error, print_success
from ...utils.cli_utils import CLIUtils, run_command, run_silent

# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)

# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class DevToolResult(BaseResult):
    """Result of a development tool operation."""

    tool_name: str = ""
    language: str = ""
    tool_type: str = ""
    path: Optional[str] = None


# =============================================================================
# DEVELOPMENT TOOLS DEFINITIONS
# =============================================================================

DEV_TOOLS = {
    "python": {
        "formatting": ["black", "isort"],
        "linting": ["ruff", "flake8"],
        "security": ["bandit"],
        "testing": ["pytest"],
        "type_checking": ["mypy"],
    },
    "javascript": {
        "formatting": ["prettier"],
        "linting": ["eslint"],
        "testing": ["jest"],
        "bundling": ["webpack", "vite"],
    },
    "universal": {
        "spell_checking": ["cspell"],
        "git_hooks": ["pre-commit"],
    },
}

# Installation methods for each language
INSTALLATION_METHODS = {
    "python": "pip",
    "javascript": "npm",
    "universal": "auto",  # Auto-detect based on tool
}

# Special tool configurations
TOOL_CONFIGS = {
    "cspell": {
        "check_method": "npx",  # Can be checked via npx
        "install_method": "npm",
    },
    "pre-commit": {"check_method": "standard", "install_method": "pip"},
}


# =============================================================================
# MAIN CLASS
# =============================================================================


class DevToolsManager:
    """Manages development tools for different languages."""

    def __init__(self):
        """
        Initialize the development tools manager.

        Raises:
            DevToolsError: If development tools manager initialization fails
        """
        try:
            self.cache = {}

        except Exception as e:
            logger.error(f"Failed to initialize DevToolsManager: {e}")
            raise DevToolsError(
                tool_name="dev_tools_manager",
                operation="initialization",
                reason=f"Failed to initialize development tools manager: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

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
                raise ValidationError(
                    component="dev_tool_check",
                    validation_type="input_validation",
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
                available = self._check_tool_availability(tool)
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

        except (DevToolsError, ValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in check_dev_tool: {e}")
            raise DevToolsError(
                tool_name=tool,
                operation="check",
                reason=f"Failed to check development tool: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def install_dev_tool(
        self, language: str, tool_type: str, tool: str
    ) -> DevToolResult:
        """
        Install a development tool with integrated UI feedback.

        Args:
            language: Programming language (python, javascript, etc.)
            tool_type: Type of tool (formatting, linting, etc.)
            tool: Name of the tool

        Returns:
            DevToolResult: Result of the installation operation

        Raises:
            DevToolsError: If tool installation fails
            InstallationError: If installation process fails
            ValidationError: If validation fails
        """
        try:
            # Input validation
            if not language or not tool_type or not tool:
                raise ValidationError(
                    component="dev_tool_installation",
                    validation_type="input_validation",
                    reason="Language, tool_type, and tool must not be empty",
                    details="All parameters must be non-empty strings",
                )

            from ...ui.common.progress import create_spinner_with_status

            # Check if already installed
            try:
                check_result = self.check_dev_tool(language, tool_type, tool)
                if check_result.success:
                    print_success(f"Dev tool {tool} already installed")
                    return DevToolResult(
                        success=True,
                        tool_name=tool,
                        language=language,
                        tool_type=tool_type,
                        path=shutil.which(tool),
                        message=f"Dev tool {tool} already installed",
                    )
            except (DevToolsError, ValidationError):
                # Re-raise our custom exceptions
                raise
            except Exception as e:
                logger.warning(
                    f"Failed to check if tool {tool} is already installed: {e}"
                )

            with create_spinner_with_status(
                f"Installing [bold cyan]{tool}[/bold cyan]..."
            ) as (
                progress,
                task,
            ):
                # Determine installation method
                progress.update(task, status="Determining installation method...")
                try:
                    install_method = self._get_installation_method(language, tool)
                except Exception as e:
                    logger.warning(
                        f"Failed to determine installation method for {tool}: {e}"
                    )
                    install_method = "auto"

                # Ensure required runtime is available (and attempt install if missing)
                progress.update(task, status="Checking runtime requirements...")
                try:
                    runtime_ok, runtime_error = self._ensure_required_runtime(
                        install_method, tool
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to check runtime requirements for {tool}: {e}"
                    )
                    runtime_ok, runtime_error = False, f"Runtime check failed: {e}"

                if not runtime_ok:
                    progress.update(task, status="Runtime requirements not met")
                    print_error(
                        f"Runtime requirements not available for {tool}: {runtime_error}"
                    )
                    return DevToolResult(
                        success=False,
                        tool_name=tool,
                        language=language,
                        tool_type=tool_type,
                        message="Required runtime not available",
                        error=runtime_error or "Required runtime not available",
                    )

                # Install the tool
                progress.update(task, status=f"Installing via {install_method}...")
                success = False
                try:
                    if install_method == "pip":
                        success = self._install_python_tool(tool)
                    elif install_method == "npm":
                        success = self._install_javascript_tool(tool)
                    else:
                        progress.update(task, status="No installation method found")
                        print_error(f"No installation method found for {tool}")
                        return DevToolResult(
                            success=False,
                            tool_name=tool,
                            language=language,
                            tool_type=tool_type,
                            message=f"No installation method found for {tool}",
                            error="No installation method found",
                        )
                except Exception as e:
                    logger.error(f"Failed to install tool {tool}: {e}")
                    success = False

                if success:
                    # Clear cache for this tool
                    try:
                        self._clear_tool_cache(language, tool_type, tool)
                    except Exception as e:
                        logger.warning(f"Failed to clear cache for {tool}: {e}")

                    progress.update(task, status="Installation completed successfully!")
                    print_success(f"Dev tool {tool} installed successfully")

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
                    print_error(f"Failed to install dev tool {tool}")
                    return DevToolResult(
                        success=False,
                        tool_name=tool,
                        language=language,
                        tool_type=tool_type,
                        message=f"Failed to install dev tool {tool}",
                        error="Installation failed",
                    )

        except (DevToolsError, InstallationError, ValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in install_dev_tool: {e}")
            raise DevToolsError(
                tool_name=tool,
                operation="installation",
                reason=f"Failed to install development tool: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def check_and_install_dev_tools(self, language: str) -> Dict[str, DevToolResult]:
        """
        Check and install all dev tools for a language with integrated UI.

        Args:
            language: Programming language to check and install tools for

        Returns:
            Dict[str, DevToolResult]: Results for each tool

        Raises:
            DevToolsError: If dev tools check/installation fails
            ValidationError: If validation fails
        """
        try:
            # Input validation
            if not language:
                raise ValidationError(
                    component="dev_tools_check_and_install",
                    validation_type="input_validation",
                    reason="Language must not be empty",
                    details="Language parameter must be a non-empty string",
                )

            from ...ui.common.progress import create_spinner_with_status

            if language not in DEV_TOOLS:
                print_error(f"Language {language} not supported")
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

            print_deps(f"Checking and installing {language} development tools...")

            results = {}
            total_tools = sum(len(tools) for tools in DEV_TOOLS[language].values())
            processed = 0

            with create_spinner_with_status(
                f"Processing [bold cyan]{language}[/bold cyan] dev tools..."
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
                                print_success(f"Dev tool {tool} already available")
                        except (DevToolsError, ValidationError):
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
            print_deps(
                f"Development tools summary: {successful}/{len(results)} tools available"
            )

            return results

        except (DevToolsError, ValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in check_and_install_dev_tools: {e}")
            raise DevToolsError(
                tool_name="dev_tools_manager",
                operation="check_and_install",
                reason=f"Failed to check and install development tools: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def get_required_tools(self, language: str) -> List[str]:
        """
        Get list of required tools for a language.

        Args:
            language: Programming language

        Returns:
            List[str]: List of required tools

        Raises:
            ValidationError: If validation fails
        """
        try:
            # Input validation
            if not language:
                raise ValidationError(
                    component="get_required_tools",
                    validation_type="input_validation",
                    reason="Language must not be empty",
                    details="Language parameter must be a non-empty string",
                )

            if language not in DEV_TOOLS:
                return []

            tools = []
            for _, tool_list in DEV_TOOLS[language].items():
                tools.extend(tool_list)

            return tools

        except ValidationError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in get_required_tools: {e}")
            raise ValidationError(
                component="get_required_tools",
                validation_type="unexpected_error",
                reason=f"Failed to get required tools: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def get_tool_status(self, language: str = None) -> Dict[str, Dict]:
        """
        Get comprehensive status of development tools with UI output.

        Args:
            language: Specific language to check (optional)

        Returns:
            Dict[str, Dict]: Status information for each tool

        Raises:
            DevToolsError: If tool status check fails
            ValidationError: If validation fails
        """
        try:
            from ...ui.common.progress import create_spinner

            status = {}
            languages_to_check = [language] if language else DEV_TOOLS.keys()

            with create_spinner("Checking dev tools status...") as (progress, task):
                for lang in languages_to_check:
                    if lang not in DEV_TOOLS:
                        continue

                    progress.update(
                        task,
                        description=f"Checking [bold cyan]{lang}[/bold cyan] tools...",
                    )

                    status[lang] = {}
                    for tool_type, tools in DEV_TOOLS[lang].items():
                        status[lang][tool_type] = {}
                        for tool in tools:
                            try:
                                available = self._check_tool_availability(tool)
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

        except (DevToolsError, ValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in get_tool_status: {e}")
            raise DevToolsError(
                tool_name="dev_tools_manager",
                operation="get_status",
                reason=f"Failed to get tool status: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _display_status_table(self, status: Dict[str, Dict]) -> None:
        """
        Display development tools status in a formatted table.

        Args:
            status: Status information to display

        Raises:
            DevToolsError: If table display fails
        """
        try:
            from rich.table import Table

            from ...ui.common.console import console

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

            console.print("\n")
            console.print(table)
            console.print("\n")

        except Exception as e:
            logger.error(f"Failed to display status table: {e}")
            raise DevToolsError(
                tool_name="dev_tools_manager",
                operation="display_status_table",
                reason=f"Failed to display status table: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _check_tool_availability(self, tool: str) -> bool:
        """
        Check if a tool is available.

        Args:
            tool: Name of the tool to check

        Returns:
            bool: True if tool is available, False otherwise

        Raises:
            DevToolsError: If tool availability check fails
        """
        try:
            # Input validation
            if not tool:
                raise ValidationError(
                    component="tool_availability_check",
                    validation_type="input_validation",
                    reason="Tool name must not be empty",
                    details="Tool parameter must be a non-empty string",
                )

            # Standard check via PATH
            try:
                if CLIUtils().check_command_available(tool):
                    return True
            except Exception as e:
                logger.warning(
                    f"Failed to check tool availability via PATH for {tool}: {e}"
                )

            # Special checks for certain tools
            if tool == "cspell":
                # Check if cspell is available via npx
                try:
                    result = run_silent(["npx", "cspell", "--version"])
                    return result.success
                except Exception as e:
                    logger.warning(f"Failed to check cspell via npx: {e}")

            return False

        except ValidationError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _check_tool_availability: {e}")
            raise DevToolsError(
                tool_name=tool,
                operation="availability_check",
                reason=f"Failed to check tool availability: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _get_installation_method(self, language: str, tool: str) -> str:
        """
        Get the installation method for a tool.

        Args:
            language: Programming language
            tool: Name of the tool

        Returns:
            str: Installation method (pip, npm, auto)

        Raises:
            ValidationError: If validation fails
        """
        try:
            # Input validation
            if not language or not tool:
                raise ValidationError(
                    component="get_installation_method",
                    validation_type="input_validation",
                    reason="Language and tool must not be empty",
                    details="Both parameters must be non-empty strings",
                )

            # Check if tool has specific configuration
            if tool in TOOL_CONFIGS:
                return TOOL_CONFIGS[tool]["install_method"]

            # Use language default
            return INSTALLATION_METHODS.get(language, "auto")

        except ValidationError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _get_installation_method: {e}")
            raise ValidationError(
                component="get_installation_method",
                validation_type="unexpected_error",
                reason=f"Failed to get installation method: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

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
                raise ValidationError(
                    component="python_tool_installation",
                    validation_type="input_validation",
                    reason="Tool name must not be empty",
                    details="Tool parameter must be a non-empty string",
                )

            cmd = [sys.executable, "-m", "pip", "install", tool]
            try:
                result = run_command(cmd)
                return result.success
            except Exception as e:
                logger.error(f"Failed to install Python tool {tool}: {e}")
                raise InstallationError(
                    component=tool,
                    operation="python_installation",
                    reason=f"Failed to install Python tool: {e}",
                    details=f"Command: {' '.join(cmd)}",
                ) from e

        except (InstallationError, ValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _install_python_tool: {e}")
            raise InstallationError(
                component=tool,
                operation="python_installation",
                reason=f"Failed to install Python tool: {e}",
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
                raise ValidationError(
                    component="javascript_tool_installation",
                    validation_type="input_validation",
                    reason="Tool name must not be empty",
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
                raise InstallationError(
                    component=tool,
                    operation="javascript_installation",
                    reason="npm not found in PATH or known locations",
                    details=(
                        "Ensure Node.js is installed and npm is accessible. "
                        "Tried PATH and common Windows locations."
                    ),
                )

            cmd = [npm_executable, "install", "-g", tool]
            try:
                result = run_command(cmd)
                return result.success
            except Exception as e:
                logger.error(f"Failed to install JavaScript tool {tool}: {e}")
                raise InstallationError(
                    component=tool,
                    operation="javascript_installation",
                    reason=f"Failed to install JavaScript tool: {e}",
                    details=f"Command: {' '.join(cmd)}",
                ) from e

        except (InstallationError, ValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _install_javascript_tool: {e}")
            raise InstallationError(
                component=tool,
                operation="javascript_installation",
                reason=f"Failed to install JavaScript tool: {e}",
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
                raise ValidationError(
                    component="clear_tool_cache",
                    validation_type="input_validation",
                    reason="Language, tool_type, and tool must not be empty",
                    details="All parameters must be non-empty strings",
                )

            cache_key = f"{language}:{tool_type}:{tool}"
            if cache_key in self.cache:
                del self.cache[cache_key]

        except ValidationError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _clear_tool_cache: {e}")
            raise DevToolsError(
                tool_name=tool,
                operation="clear_cache",
                reason=f"Failed to clear tool cache: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _ensure_required_runtime(
        self, install_method: str, tool: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Ensure the required runtime (python/node) is available before installing a tool.

        Args:
            install_method: Installation method (pip, npm, etc.)
            tool: Name of the tool

        Returns:
            Tuple[bool, Optional[str]]: (True, None) if runtime is available or successfully installed; otherwise (False, error_message)

        Raises:
            DevToolsError: If runtime check fails
        """
        try:
            # Input validation
            if not install_method or not tool:
                raise ValidationError(
                    component="ensure_required_runtime",
                    validation_type="input_validation",
                    reason="Install_method and tool must not be empty",
                    details="Both parameters must be non-empty strings",
                )

            # Lazy import to avoid circular dependencies at module import time
            try:
                from .runtime_manager import runtime_manager
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

        except ValidationError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _ensure_required_runtime: {e}")
            raise DevToolsError(
                tool_name=tool,
                operation="ensure_runtime",
                reason=f"Failed to ensure required runtime: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e


# GLOBAL INSTANCE
########################################################

dev_tools_manager = DevToolsManager()
