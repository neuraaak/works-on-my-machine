#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEPS COMMAND - Dependencies Management
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Dependencies command for Works On My Machine.

Manages the 3-strata dependency hierarchy:
- Strata 1: System Package Managers (winget, choco, homebrew)
- Strata 2: Runtimes (python, node, git)
- Strata 3: DevTools (cspell, ruff, eslint)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import sys

# Third-party imports
import click
from ezpl.types import LogLevel

# Local imports
from ...interfaces import (
    DevToolsInterface,
    RuntimeInterface,
    SystemPackageManagerInterface,
)
from ...shared.configs.dependencies import DevToolsConfig
from ...ui.common import ezpl_bridge, ezprinter

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)


# ///////////////////////////////////////////////////////////////
# HELPER FUNCTIONS
# ///////////////////////////////////////////////////////////////


def _find_tool_info(tool_name: str) -> tuple[str, str] | None:
    """
    Find the language (category) and tool_type (subcategory) for a given tool.

    Args:
        tool_name: The name of the tool to find

    Returns:
        Tuple of (language, tool_type) if found, None otherwise
    """
    for category, tools in DevToolsConfig.DEVTOOLS_DEPENDENCIES.items():
        for subcategory, tool_list in tools.items():
            if tool_name in tool_list:
                return (category, subcategory)
    return None


# ///////////////////////////////////////////////////////////////
# MAIN DEPS GROUP
# ///////////////////////////////////////////////////////////////


@click.group(invoke_without_command=True)
@click.pass_context
def deps_group(ctx: click.Context) -> None:
    """
    Manage dependencies across all strata (system, runtime, tools).

    The dependency system is organized in 3 hierarchical strata:

    \b
    Strata 1: System Package Managers (winget, chocolatey, homebrew, apt)
    Strata 2: Runtimes (python, node, git)
    Strata 3: Development Tools (cspell, ruff, eslint, pytest)

    Each strata depends on the lower ones. Use subcommands to manage each level.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ///////////////////////////////////////////////////////////////
# STRATA 1: SYSTEM PACKAGE MANAGERS
# ///////////////////////////////////////////////////////////////


@deps_group.group(name="system", invoke_without_command=True)
@click.pass_context
def system_group(ctx: click.Context) -> None:
    """
    Manage system package managers (Strata 1).

    System package managers are the foundation of the dependency hierarchy.
    They are used to install runtimes and other system-level dependencies.

    \b
    Examples:
        womm deps system check           # Check all managers
        womm deps system check winget    # Check specific manager
        womm deps system list            # List all managers
        womm deps system best            # Show best available manager
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@system_group.command(name="check")
@click.help_option("-h", "--help")
@click.argument("manager", required=False)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show detailed information about the manager.",
)
def system_check(manager: str | None, verbose: bool) -> None:
    """
    Check system package manager availability.

    If MANAGER is provided, checks only that specific manager.
    Otherwise, checks all available managers for the current platform.

    \b
    Examples:
        womm deps system check           # Check all managers
        womm deps system check winget    # Check winget only
        womm deps system check -v        # Verbose output
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Print header
    ezprinter.print_header("System Package Manager Check")

    try:
        interface = SystemPackageManagerInterface()

        if manager:
            # Check specific manager - interface handles display
            result = interface.check_package_manager(
                manager, show_ui=True, verbose=verbose
            )
            # Exit with appropriate code
            sys.exit(0 if result.success else 1)
        else:
            # Check all managers - interface handles spinner + UI
            summary = interface.check_all_managers()
            # Exit with appropriate code
            all_success = all(result.success for result in summary.values())
            sys.exit(0 if all_success else 1)

    except Exception as e:
        logger.error(f"Failed to check system package managers: {e}")
        ezprinter.error(f"Check failed: {e}")
        raise click.Abort() from e


@system_group.command(name="list")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show detailed information for each manager.",
)
def system_list(verbose: bool) -> None:
    """
    List all system package managers and their status.

    Shows a table with all package managers, their availability,
    version, and platform support for the current system.

    \b
    Example:
        womm deps system list
        womm deps system list -v
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Print header
    ezprinter.print_header("System Package Manager List")

    try:
        interface = SystemPackageManagerInterface()
        result = interface.list_managers(verbose)
        # Exit with appropriate code
        any_available = any(
            manager_info.get("installed", False)
            for manager_info in result.values()
            if isinstance(manager_info, dict)
        )
        sys.exit(0 if any_available else 1)

    except Exception as e:
        logger.error(f"Failed to list system package managers: {e}")
        ezprinter.error(f"List failed: {e}")
        raise click.Abort() from e


@system_group.command(name="best")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show why this manager was selected as best.",
)
def system_best(verbose: bool) -> None:
    """
    Show the best available system package manager.

    Uses the priority system to determine the best manager
    for the current platform.

    \b
    Example:
        womm deps system best
        womm deps system best -v
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Print header
    ezprinter.print_header("Best System Package Manager")

    try:
        interface = SystemPackageManagerInterface()
        result = interface.show_best_manager(verbose)
        # Exit with appropriate code
        sys.exit(0 if result else 1)

    except Exception as e:
        logger.error(f"Failed to get best system package manager: {e}")
        ezprinter.error(f"Best failed: {e}")
        raise click.Abort() from e


# ///////////////////////////////////////////////////////////////
# STRATA 2: RUNTIMES
# ///////////////////////////////////////////////////////////////


@deps_group.group(name="runtime", invoke_without_command=True)
@click.pass_context
def runtime_group(ctx: click.Context) -> None:
    """
    Manage language runtimes (Strata 2).

    Runtimes are programming language environments (Python, Node.js, Git)
    that are required to run development tools.

    \b
    Examples:
        womm deps runtime check          # Check all runtimes
        womm deps runtime check python   # Check specific runtime
        womm deps runtime install python # Install with best manager
        womm deps runtime list           # List available runtimes
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@runtime_group.command(name="check")
@click.help_option("-h", "--help")
@click.argument("runtime", required=False)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show detailed information about the runtime.",
)
def runtime_check(runtime: str | None, verbose: bool) -> None:
    """
    Check runtime installation status.

    If RUNTIME is provided, checks only that specific runtime.
    Otherwise, checks all configured runtimes.

    \b
    Examples:
        womm deps runtime check          # Check all runtimes
        womm deps runtime check python   # Check Python only
        womm deps runtime check -v       # Verbose output
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Print header
    ezprinter.print_header("Runtime Check")

    try:
        interface = RuntimeInterface()

        if runtime:
            result = interface.show_runtime_check(runtime, verbose)
            # Exit with appropriate code
            sys.exit(0 if result.success else 1)
        else:
            # Check all runtimes - interface handles spinner + UI
            results = interface.check_all_runtimes()
            # Exit with appropriate code (success if all are successful)
            all_success = all(r.success for r in results.values())
            sys.exit(0 if all_success else 1)

    except Exception as e:
        logger.error(f"Failed to check runtime: {e}")
        ezprinter.error(f"Check failed: {e}")
        raise click.Abort() from e


@runtime_group.command(name="install")
@click.help_option("-h", "--help")
@click.argument("runtime")
@click.option(
    "--via",
    "manager",
    help="Specific system package manager to use (e.g., winget, chocolatey).",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show detailed installation progress.",
)
def runtime_install(runtime: str, _manager: str | None, verbose: bool) -> None:
    """
    Install a runtime.

    Automatically selects the best system package manager unless --via is specified.
    The installation process will:
    1. Check if already installed
    2. Find best system package manager (or use specified one)
    3. Install the runtime via the package manager

    \b
    Examples:
        womm deps runtime install python          # Auto-select best manager
        womm deps runtime install python --via winget
        womm deps runtime install node -v         # Verbose mode
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Print header
    ezprinter.print_header("Runtime Installation")

    try:
        interface = RuntimeInterface()

        result = interface.show_runtime_install(runtime, verbose)
        # Exit with appropriate code
        sys.exit(0 if result.success else 1)

    except Exception as e:
        logger.error(f"Failed to install runtime {runtime}: {e}")
        ezprinter.error(f"Installation failed: {e}")
        raise click.Abort() from e


@runtime_group.command(name="list")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show detailed information for each runtime.",
)
def runtime_list(verbose: bool) -> None:
    """
    List all available runtimes.

    Shows configured runtimes with their minimum version requirements
    and supported package managers.

    \b
    Example:
        womm deps runtime list
        womm deps runtime list -v
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Print header
    ezprinter.print_header("Runtime List")

    try:
        interface = RuntimeInterface()
        interface.show_runtimes_list(verbose)
        # Exit with success (list is informational)
        sys.exit(0)

    except Exception as e:
        logger.error(f"Failed to list runtimes: {e}")
        ezprinter.error(f"List failed: {e}")
        raise click.Abort() from e


# ///////////////////////////////////////////////////////////////
# STRATA 3: DEVTOOLS
# ///////////////////////////////////////////////////////////////


@deps_group.group(name="tool", invoke_without_command=True)
@click.pass_context
def tool_group(ctx: click.Context) -> None:
    """
    Manage development tools (Strata 3).

    Development tools are language-specific utilities (cspell, ruff, eslint)
    that help with code quality, formatting, and linting.

    \b
    Examples:
        womm deps tool check          # Check all tools
        womm deps tool check cspell   # Check specific tool
        womm deps tool install cspell # Install with dependency resolution
        womm deps tool list           # List available tools
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@tool_group.command(name="check")
@click.help_option("-h", "--help")
@click.argument("tool", required=False)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show detailed information about the tool.",
)
def tool_check(tool: str | None, verbose: bool) -> None:
    """
    Check development tool availability.

    If TOOL is provided, checks only that specific tool.
    Otherwise, checks all configured development tools.

    \b
    Examples:
        womm deps tool check          # Check all tools
        womm deps tool check cspell   # Check cspell only
        womm deps tool check -v       # Verbose output
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Print header
    ezprinter.print_header("Dev Tools Check")

    try:
        interface = DevToolsInterface()

        if tool:
            tool_info = _find_tool_info(tool)
            if tool_info is None:
                ezprinter.error(f"Unknown tool: {tool}")
                sys.exit(1)

            assert tool_info is not None
            language, tool_type = tool_info
            result = interface.show_tool_check(language, tool_type, tool, verbose)
            # Exit with appropriate code
            sys.exit(0 if result.success else 1)
        else:
            # Check all tools - interface handles spinner + UI
            results = interface.check_all_tools()
            if results is None:
                results = {}
            assert results is not None
            # Exit with appropriate code (success if all are successful)
            all_success = all(r.success for r in results.values())
            sys.exit(0 if all_success else 1)

    except Exception as e:
        logger.error(f"Failed to check tool: {e}")
        ezprinter.error(f"Check failed: {e}")
        raise click.Abort() from e


@tool_group.command(name="install")
@click.help_option("-h", "--help")
@click.argument("tool")
@click.option(
    "--force",
    is_flag=True,
    help="Force reinstall even if already installed.",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show detailed installation progress.",
)
def tool_install(tool: str, force: bool, verbose: bool) -> None:
    """
    Install a development tool (auto-resolves dependencies).

    The installation process will:
    1. Check if already installed (skip if force=False)
    2. Resolve dependency chain via DependenciesHierarchy
    3. Ensure runtime is installed (install if missing)
    4. Ensure runtime package manager is available
    5. Install the tool via the package manager

    \b
    Examples:
        womm deps tool install cspell
        womm deps tool install ruff --force
        womm deps tool install eslint -v
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Print header
    ezprinter.print_header("Dev Tool Installation")

    try:
        interface = DevToolsInterface()

        # Check if already installed (unless force)
        if not force:
            tool_info = _find_tool_info(tool)
            if not tool_info:
                ezprinter.error(f"Unknown tool: {tool}")
                raise click.Abort()

            language, tool_type = tool_info
            check_result = interface.check_dev_tool(language, tool_type, tool)
            if check_result.success:
                ezprinter.success(f"{tool} is already installed")
                if not click.confirm("Reinstall anyway?", default=False):
                    return

        tool_info = _find_tool_info(tool)
        if not tool_info:
            ezprinter.error(f"Unknown tool: {tool}")
            raise click.Abort()

        language, tool_type = tool_info
        result = interface.show_tool_install(language, tool_type, tool, verbose)
        # Exit with appropriate code
        sys.exit(0 if result.success else 1)

    except Exception as e:
        logger.error(f"Failed to install tool {tool}: {e}")
        ezprinter.error(f"Installation failed: {e}")
        raise click.Abort() from e


@tool_group.command(name="list")
@click.help_option("-h", "--help")
@click.argument("category", required=False)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show dependency chains for each tool.",
)
def tool_list(category: str | None, verbose: bool) -> None:
    """
    List available development tools.

    If CATEGORY is provided, shows only tools for that category.
    Otherwise, shows all tools grouped by language and category.

    \b
    Examples:
        womm deps tool list          # List all tools
        womm deps tool list python   # List Python tools only
        womm deps tool list -v       # Show dependency chains
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Print header
    ezprinter.print_header("Dev Tool List")

    try:
        interface = DevToolsInterface()
        interface.show_tools_list(category, verbose)
        # Exit with success (list is informational)
        sys.exit(0)

    except Exception as e:
        logger.error(f"Failed to list tools: {e}")
        ezprinter.error(f"List failed: {e}")
        raise click.Abort() from e


# ///////////////////////////////////////////////////////////////
# GLOBAL COMMANDS
# ///////////////////////////////////////////////////////////////


@deps_group.command(name="check")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show detailed information for each component.",
)
def deps_check(verbose: bool) -> None:
    """
    Check all dependencies across all strata.

    Performs a comprehensive check of:
    - System package managers (Strata 1)
    - Runtimes (Strata 2)
    - Development tools (Strata 3)

    \b
    Example:
        womm deps check
        womm deps check -v
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Print header
    ezprinter.print_header("Dependencies Check")

    try:
        from ...interfaces import DepsInterface

        interface = DepsInterface()
        results = interface.check_all(verbose)
        # Exit with appropriate code (success if all strata have successful results)
        system_ok = any(
            r.get("available", False) for r in results.get("system", {}).values()
        )
        runtime_ok = all(r.success for r in results.get("runtime", {}).values())
        tools_ok = all(r.success for r in results.get("tools", {}).values())
        all_ok = system_ok and runtime_ok and tools_ok
        sys.exit(0 if all_ok else 1)

    except Exception as e:
        logger.error(f"Failed to check dependencies: {e}")
        ezprinter.error(f"Check failed: {e}")
        raise click.Abort() from e


@deps_group.command(name="status")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show additional details in the status report.",
)
def deps_status(verbose: bool) -> None:
    """
    Show comprehensive dependency status report.

    Generates a detailed table showing the status of all components
    across all three strata, including versions and availability.

    \b
    Example:
        womm deps status
        womm deps status -v
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Print header
    ezprinter.print_header("Dependency Status")

    try:
        from ...interfaces import DepsInterface

        interface = DepsInterface()
        interface.show_status(verbose)
        # Exit with success (status is informational)
        sys.exit(0)

    except Exception as e:
        logger.error(f"Failed to generate status report: {e}")
        ezprinter.error(f"Status failed: {e}")
        raise click.Abort() from e


@deps_group.command(name="validate")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show detailed validation information.",
)
def deps_validate(verbose: bool) -> None:
    """
    Validate all dependency chains.

    Checks that all development tools have valid dependency chains
    defined in DependenciesHierarchy, ensuring proper runtime and
    package manager mappings.

    \b
    Example:
        womm deps validate
        womm deps validate -v
    """
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Print header
    ezprinter.print_header("Dependency Validation")

    try:
        from ...interfaces import DepsInterface

        interface = DepsInterface()
        result = interface.validate_chains(verbose)
        # Exit with appropriate code (success if no issues)
        sys.exit(0 if len(result.get("issues", [])) == 0 else 1)

    except Exception as e:
        logger.error(f"Failed to validate dependencies: {e}")
        ezprinter.error(f"Validation failed: {e}")
        raise click.Abort() from e


# ///////////////////////////////////////////////////////////////
# EXPORT
# ///////////////////////////////////////////////////////////////

__all__ = ["deps_group"]
