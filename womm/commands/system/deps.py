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

# Third-party imports
import click
from ezpl.types import LogLevel

# Local imports
from ...interfaces import (
    DevToolsInterface,
    RuntimeInterface,
    SystemPackageManagerInterface,
)
from ...shared.configs.dependencies import (
    DependenciesHierarchy,
    DevToolsConfig,
    RuntimeConfig,
)
from ...ui.common import ezconsole, ezpl_bridge, ezprinter
from ...ui.dependencies import (
    display_runtime_check_specific,
    display_runtime_install_result,
    display_runtimes_list,
)
from ...ui.system import (
    display_best_manager,
    display_deps_check_results,
    display_deps_status_table,
    display_deps_validation_results,
    display_system_managers_list,
)

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
            # Check specific manager
            result = interface.check_package_manager(manager)
            if result.success:
                msg = f"{manager} is available"
                if result.version:
                    msg += f" (version {result.version})"
                ezprinter.success(msg)

                if verbose:
                    ezprinter.info(f"Platform: {result.platform}")
                    ezprinter.info(f"Priority: {result.priority}")
            else:
                ezprinter.error(f"{manager} is not available")
                if verbose:
                    ezprinter.info(f"Error: {result.error}")
        else:
            # Check all managers - interface handles spinner + UI
            interface.check_all_managers()

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
        # TODO: Migrate to interface method that handles data retrieval + UI display
        interface = SystemPackageManagerInterface()
        status = interface.get_installation_status()
        display_system_managers_list(status, verbose)

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
        # TODO: Migrate to interface method that handles data retrieval + UI display
        interface = SystemPackageManagerInterface()
        best = interface.get_best_available_manager()
        display_best_manager(best, interface, verbose)

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
            # TODO: Migrate to interface method that handles check + UI display
            result = interface.check_runtime(runtime)
            display_runtime_check_specific(result, runtime, verbose)
        else:
            # Check all runtimes - interface handles spinner + UI
            interface.check_all_runtimes()

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
def runtime_install(runtime: str, manager: str | None, verbose: bool) -> None:
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

        # TODO: Migrate verbose output to interface
        if verbose:
            ezprinter.info(f"Installing {runtime}...")
            if manager:
                ezprinter.info(f"Using specified manager: {manager}")
            else:
                ezprinter.info("Auto-selecting best system package manager...")

        # TODO: Migrate to interface method that handles install + UI display
        result = interface.install_runtime(runtime)
        display_runtime_install_result(result, runtime, verbose)

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
        display_runtimes_list(verbose)

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
            # TODO: Migrate specific tool check to interface method with UI display
            tool_info = _find_tool_info(tool)
            if not tool_info:
                ezprinter.error(f"Unknown tool: {tool}")
                raise click.Abort()

            language, tool_type = tool_info
            result = interface.check_dev_tool(language, tool_type, tool)

            # TODO: Migrate result display to UI module (display_tool_check_specific)
            if result.success:
                msg = f"{tool} is available"
                if result.path:
                    msg += f" ({result.path})"
                ezprinter.success(msg)

                if verbose:
                    try:
                        chain = DependenciesHierarchy.get_devtool_chain(tool)
                        ezprinter.info(
                            f"Dependencies: {chain['runtime_package_manager']} → {chain['runtime']}"
                        )
                    except Exception as e:
                        logger.debug(
                            f"Could not resolve dependency chain for {tool}: {e}"
                        )
            else:
                ezprinter.warning(f"{tool} is not available")

                if verbose:
                    ezprinter.info("Use 'womm deps tool install' to install it")
        else:
            # Check all tools - interface handles spinner + UI
            interface.check_all_tools()

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

        # TODO: Migrate verbose output and dependency chain display to interface/UI
        if verbose:
            ezprinter.info(f"Installing {tool}...")

            try:
                chain = DependenciesHierarchy.get_devtool_chain(tool)
                ezprinter.info(
                    f"Dependency chain: {tool} → {chain['runtime_package_manager']} → {chain['runtime']}"
                )
            except Exception as e:
                logger.debug(f"Could not resolve dependency chain: {e}")

        # TODO: Migrate installation logic and result display to interface/UI
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
        result = interface.install_dev_tool(language, tool_type, tool)

        # TODO: Migrate result display to UI module (display_tool_install_result)
        if result.success:
            msg = f"{tool} installed successfully"
            if result.path:
                msg += f" → {result.path}"
            ezprinter.success(msg)
        else:
            ezprinter.error(f"Failed to install {tool}")
            if result.error:
                ezprinter.error(f"Error: {result.error}")

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
        # TODO: Migrate entire tool list display to UI module (display_devtools_list)
        from rich.table import Table

        tools_config = DevToolsConfig.DEVTOOLS_DEPENDENCIES

        if category and category in tools_config:
            # Show specific category
            table = Table(
                title=f"{category.capitalize()} Development Tools", show_header=True
            )
            table.add_column("Category", style="cyan")
            table.add_column("Tools", style="white")

            if verbose:
                table.add_column("Package Manager", style="yellow")

            for subcat, tools in tools_config[category].items():
                row = [subcat, ", ".join(tools)]

                if verbose:
                    pm = DevToolsConfig.DEFAULT_RUNTIME_PACKAGE_MANAGER.get(
                        category, "N/A"
                    )
                    row.append(pm)

                table.add_row(*row)
        else:
            # Show all categories
            table = Table(title="All Development Tools", show_header=True)
            table.add_column("Language", style="cyan", no_wrap=True)
            table.add_column("Category", style="yellow", no_wrap=True)
            table.add_column("Tools", style="white")

            if verbose:
                table.add_column("Package Manager", style="magenta")

            for lang, categories in tools_config.items():
                for subcat, tools in categories.items():
                    row = [lang, subcat, ", ".join(tools)]

                    if verbose:
                        pm = DevToolsConfig.DEFAULT_RUNTIME_PACKAGE_MANAGER.get(
                            lang, "N/A"
                        )
                        row.append(pm)

                    table.add_row(*row)

        ezconsole.print(table)

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
        system_interface = SystemPackageManagerInterface()
        runtime_interface = RuntimeInterface()
        tool_interface = DevToolsInterface()

        # Collect all results
        system_results = system_interface.detect_available_managers()
        runtime_results = {
            rt: runtime_interface.check_runtime(rt) for rt in RuntimeConfig.RUNTIMES
        }

        # Tool results
        tool_results = {}
        for category, tools in DevToolsConfig.DEVTOOLS_DEPENDENCIES.items():
            for subcategory, tool_list in tools.items():
                for tool in tool_list:
                    result = tool_interface.check_dev_tool(category, subcategory, tool)
                    tool_results[tool] = result

        # Display via UI function (to be created)
        display_deps_check_results(
            system_results, runtime_results, tool_results, verbose
        )

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
        system_interface = SystemPackageManagerInterface()
        runtime_interface = RuntimeInterface()
        tool_interface = DevToolsInterface()

        # Collect data
        system_status = system_interface.get_installation_status()
        runtime_results = {
            rt: runtime_interface.check_runtime(rt) for rt in RuntimeConfig.RUNTIMES
        }

        sample_tools = ["cspell", "ruff", "pytest", "eslint"]
        tool_results = {}
        for tool in sample_tools:
            try:
                tool_info = _find_tool_info(tool)
                if tool_info:
                    language, tool_type = tool_info
                    result = tool_interface.check_dev_tool(language, tool_type, tool)
                    tool_results[tool] = result
            except Exception as e:
                logger.debug(f"Could not check tool {tool}: {e}")

        # Display via UI function (to be created)
        display_deps_status_table(system_status, runtime_results, tool_results, verbose)

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
        # Collect validation results
        issues = []
        valid_count = 0

        # Check each devtool's chain
        for _category, tools in DevToolsConfig.DEVTOOLS_DEPENDENCIES.items():
            for _subcategory, tool_list in tools.items():
                for tool in tool_list:
                    try:
                        chain = DependenciesHierarchy.get_devtool_chain(tool)

                        if not chain.get("runtime_package_manager"):
                            issues.append(f"❌ {tool}: Missing runtime_package_manager")
                        elif not chain.get("runtime"):
                            issues.append(f"❌ {tool}: Missing runtime")
                        else:
                            valid_count += 1
                    except Exception as e:
                        issues.append(f"❌ {tool}: Invalid chain ({e})")

        # Display via UI function (to be created)
        display_deps_validation_results(issues, valid_count, verbose)

    except Exception as e:
        logger.error(f"Failed to validate dependencies: {e}")
        ezprinter.error(f"Validation failed: {e}")
        raise click.Abort() from e


# ///////////////////////////////////////////////////////////////
# EXPORT
# ///////////////////////////////////////////////////////////////

__all__ = ["deps_group"]
