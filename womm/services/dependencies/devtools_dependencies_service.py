#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEV TOOLS SERVICE - Development Tools Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Dev Tools Service - Singleton service for development tools operations.

Handles development tools detection, availability checking, and installation
coordination for language-specific tools.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import shutil
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.common import ValidationServiceError
from ...exceptions.dependencies import DevToolsServiceError
from ...shared.configs.dependencies import DevToolsConfig
from ...shared.configs.dependencies.dependencies_hierarchy import DependenciesHierarchy
from ...shared.results import DevToolAvailabilityResult
from ..common.command_runner_service import CommandRunnerService

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# DEV TOOLS SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class DevToolsService:
    """Singleton service for development tools operations."""

    _instance: ClassVar[DevToolsService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> DevToolsService:
        """Create or return the singleton instance."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize dev tools service (only once)."""
        if DevToolsService._initialized:
            return

        try:
            self.cache: dict[str, bool] = {}
            self._command_runner = CommandRunnerService()
            DevToolsService._initialized = True

        except Exception as e:
            logger.error(f"Failed to initialize DevToolsService: {e}")
            raise DevToolsServiceError(
                tool_name="dev_tools_service",
                operation="initialization",
                reason=f"Failed to initialize dev tools service: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def check_tool_availability(self, tool: str) -> DevToolAvailabilityResult:
        """
        Check if a development tool is available.

        Args:
            tool: Name of the tool to check

        Returns:
            DevToolAvailabilityResult: Result with availability status

        Raises:
            DevToolsError: If tool check fails
            ValidationError: If validation fails
        """
        try:
            # Input validation
            if not tool:
                raise ValidationServiceError(
                    operation="check_tool_availability",
                    field="tool",
                    reason="Tool name must not be empty",
                    details="Tool name parameter must be a non-empty string",
                )

            # Check cache first
            cache_key = f"tool:{tool}"
            if cache_key in self.cache:
                is_available = self.cache[cache_key]
                language = self._find_language_for_tool(tool)
                return DevToolAvailabilityResult(
                    success=True,
                    message=f"Tool '{tool}' availability: {is_available}",
                    tool_name=tool,
                    is_available=is_available,
                    language=language,
                )

            # Check if tool is available
            available = shutil.which(tool) is not None

            # For special tools, check via alternative methods
            if not available and tool in DevToolsConfig.TOOL_CONFIGS:
                config = DevToolsConfig.TOOL_CONFIGS[tool]
                check_method = config.get("check_method", "standard")
                if check_method == "npx":
                    # Check via npx
                    try:
                        result = self._command_runner.run_silent(
                            ["npx", tool, "--version"]
                        )
                        available = bool(result)
                    except Exception as e:
                        logger.debug(f"Failed to check tool {tool} via npx: {e}")
                        available = False

            self.cache[cache_key] = available

            # Find language
            language = self._find_language_for_tool(tool)

            return DevToolAvailabilityResult(
                success=True,
                message=f"Tool '{tool}' is {'available' if available else 'not available'}",
                tool_name=tool,
                is_available=available,
                language=language,
            )

        except ValidationServiceError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in check_tool_availability: {e}")
            return DevToolAvailabilityResult(
                success=False,
                error=str(e),
                tool_name=tool,
                is_available=False,
                language="",
            )

    def get_tools_for_language(self, language: str) -> dict[str, list[str]]:
        """
        Get development tools for a language.

        Args:
            language: Programming language (python, javascript, universal)

        Returns:
            dict: Dictionary of tool types to tool names
        """
        if not language:
            return {}
        return DevToolsConfig.DEVTOOLS_DEPENDENCIES.get(language, {})

    def get_installation_method(self, language: str) -> str:
        """
        Get installation method for a language.

        Args:
            language: Programming language

        Returns:
            str: Installation method (pip, npm, auto)
        """
        if not language:
            return "auto"
        return DevToolsConfig.DEFAULT_RUNTIME_PACKAGE_MANAGER.get(language, "auto")

    def get_tool_config(
        cls, tool: str
    ) -> dict[str, str | list[str | list[str]]] | None:
        """
        Get special configuration for a tool.

        Args:
            tool: Name of the tool

        Returns:
            dict | None: Tool configuration or None if not found
        """
        if not tool:
            return None
        return DevToolsConfig.TOOL_CONFIGS.get(tool)

    def install_devtool(self, tool: str) -> DevToolAvailabilityResult:
        """
        Install a development tool by following its dependency chain.

        Uses DependenciesHierarchy to identify required runtime and runtime_package_manager,
        then installs the tool using the appropriate package manager.

        Args:
            tool: Name of the tool to install (cspell, ruff, eslint, etc.)

        Returns:
            DevToolAvailabilityResult: Result with installation status

        Raises:
            DevToolsServiceError: If installation fails
            ValidationServiceError: If validation fails
        """
        try:
            # Input validation
            if not tool:
                raise ValidationServiceError(
                    operation="install_devtool",
                    field="tool",
                    reason="Tool name must not be empty",
                    details="Tool name parameter must be a non-empty string",
                )

            # Check if already installed
            check_result = self.check_tool_availability(tool)
            if check_result.is_available:
                logger.info(f"Tool {tool} is already installed")
                return check_result

            # Get dependency chain from hierarchy
            try:
                chain = DependenciesHierarchy.get_devtool_chain(tool)
            except ValueError as e:
                raise ValidationServiceError(
                    operation="install_devtool",
                    field="tool",
                    reason=f"Unknown development tool: {tool}",
                    details=str(e),
                ) from e

            runtime_package_manager = chain.get("runtime_package_manager")
            runtime = chain.get("runtime")

            if not runtime_package_manager or not runtime:
                raise DevToolsServiceError(
                    tool_name=tool,
                    operation="install",
                    reason="Invalid dependency chain",
                    details=f"Chain: {chain}",
                )

            logger.info(
                f"Installing {tool} (requires {runtime_package_manager} from {runtime})..."
            )

            # Lazy import to avoid circular dependency
            from .runtime_service import RuntimeService

            runtime_service = RuntimeService()

            # Ensure runtime is installed
            runtime_check = runtime_service.check_runtime_installation(runtime)
            if not runtime_check.is_installed:
                logger.info(f"Runtime {runtime} not found, installing...")
                runtime_install_result = runtime_service.install_runtime(runtime)
                if not runtime_install_result.is_installed:
                    raise DevToolsServiceError(
                        tool_name=tool,
                        operation="install",
                        reason=f"Failed to install required runtime: {runtime}",
                        details=f"Runtime installation result: {runtime_install_result.message}",
                    )

            # Ensure runtime package manager is available
            if not runtime_service.ensure_runtime_package_manager(
                runtime_package_manager
            ):
                raise DevToolsServiceError(
                    tool_name=tool,
                    operation="install",
                    reason=f"Runtime package manager {runtime_package_manager} not available",
                    details=f"Required runtime: {runtime}",
                )

            # Install the tool using the runtime package manager
            install_cmd = self._get_install_command(runtime_package_manager, tool)
            if not install_cmd:
                raise DevToolsServiceError(
                    tool_name=tool,
                    operation="install",
                    reason=f"No install command for {runtime_package_manager}",
                    details=f"Tool: {tool}",
                )

            logger.info(f"Installing {tool}: {' '.join(install_cmd)}")
            result = self._command_runner.run(install_cmd)

            if result.returncode != 0:
                raise DevToolsServiceError(
                    tool_name=tool,
                    operation="install",
                    reason="Installation command failed",
                    details=f"Command: {' '.join(install_cmd)}\nError: {result.stderr or result.stdout}",
                )

            logger.info(f"Successfully installed {tool}")

            # Invalidate cache
            if tool in self.cache:
                del self.cache[tool]

            # Check again after installation
            return self.check_tool_availability(tool)

        except ValidationServiceError:
            raise
        except DevToolsServiceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in install_devtool: {e}")
            raise DevToolsServiceError(
                tool_name=tool,
                operation="install",
                reason=f"Failed to install tool: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _get_install_command(self, rpm: str, tool: str) -> list[str] | None:
        """
        Get installation command for a tool using the specified runtime package manager.

        Args:
            rpm: Runtime package manager (pip, npm, etc.)
            tool: Tool name

        Returns:
            list[str] | None: Command list or None if not supported
        """
        # Map runtime package managers to their install commands
        install_patterns = {
            "pip": ["pip", "install"],
            "uv": ["uv", "pip", "install"],
            "npm": ["npm", "install", "-g"],
            "yarn": ["yarn", "global", "add"],
        }

        pattern = install_patterns.get(rpm)
        if not pattern:
            return None

        return [*pattern, tool]

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _find_language_for_tool(self, tool: str) -> str:
        """
        Find the language associated with a tool.

        Args:
            tool: Name of the tool

        Returns:
            str: Language name or empty string if not found
        """
        try:
            for lang, tools_dict in DevToolsConfig.DEVTOOLS_DEPENDENCIES.items():
                for tool_list in tools_dict.values():
                    if tool in tool_list:
                        return lang
            return ""
        except Exception as e:
            logger.debug(f"Failed to find language for tool {tool}: {e}")
            return ""
