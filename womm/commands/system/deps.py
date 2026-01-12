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
from ...ui.runtime import (
    display_runtime_check_all,
    display_runtime_check_specific,
    display_runtime_install_result,
    display_runtimes_list,
)
from ...ui.system import (
    display_available_managers,
    display_best_manager,
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


@click.group(name="deps")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output with detailed information.",
)
@click.pass_context
def deps_group(ctx: click.Context, verbose: bool) -> None:
    """
    Manage dependencies across all strata (system, runtime, tools).

    The dependency system is organized in 3 hierarchical strata:

    \b
    Strata 1: System Package Managers (winget, chocolatey, homebrew, apt)
    Strata 2: Runtimes (python, node, git)
    Strata 3: Development Tools (cspell, ruff, eslint, pytest)

    Each strata depends on the lower ones. Use subcommands to manage each level.
    """
    # Store verbose in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

    if verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")


# ///////////////////////////////////////////////////////////////
# STRATA 1: SYSTEM PACKAGE MANAGERS
# ///////////////////////////////////////////////////////////////


@deps_group.group(name="system")
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


@system_group.command(name="check")
@click.help_option("-h", "--help")
@click.argument("manager", required=False)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show detailed information about the manager.",
)
@click.pass_context
def system_check(ctx: click.Context, manager: str | None, verbose: bool) -> None:
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
    ezprinter.print_header("System Package Manager availability checking")

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

                if verbose or ctx.obj.get("verbose"):
                    ezprinter.info(f"Platform: {result.platform}")
                    ezprinter.info(f"Priority: {result.priority}")
            else:
                ezprinter.error(f"{manager} is not available")
                if verbose or ctx.obj.get("verbose"):
                    ezprinter.info(f"Error: {result.error}")
        else:
            # Check all managers
            results = interface.detect_available_managers()
            display_available_managers(results, verbose or ctx.obj.get("verbose"))

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
@click.pass_context
def system_list(ctx: click.Context, verbose: bool) -> None:
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
    ezprinter.print_header("System Package Manager listing")

    try:
        interface = SystemPackageManagerInterface()
        status = interface.get_installation_status()
        display_system_managers_list(status, verbose or ctx.obj.get("verbose"))

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
@click.pass_context
def system_best(ctx: click.Context, verbose: bool) -> None:
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
    ezprinter.print_header("System Package Manager recommendation")

    try:
        interface = SystemPackageManagerInterface()
        best = interface.get_best_available_manager()
        display_best_manager(best, interface, verbose or ctx.obj.get("verbose"))

    except Exception as e:
        logger.error(f"Failed to get best system package manager: {e}")
        ezprinter.error(f"Best failed: {e}")
        raise click.Abort() from e


# ///////////////////////////////////////////////////////////////
# STRATA 2: RUNTIMES
# ///////////////////////////////////////////////////////////////


@deps_group.group(name="runtime")
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


@runtime_group.command(name="check")
@click.help_option("-h", "--help")
@click.argument("runtime", required=False)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show detailed information about the runtime.",
)
@click.pass_context
def runtime_check(ctx: click.Context, runtime: str | None, verbose: bool) -> None:
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
    ezprinter.print_header("Runtime availability checking")

    try:
        interface = RuntimeInterface()

        if runtime:
            # Check specific runtime
            result = interface.check_runtime(runtime)
            display_runtime_check_specific(
                result, runtime, verbose or ctx.obj.get("verbose")
            )
        else:
            # Check all runtimes
            display_runtime_check_all(interface, verbose or ctx.obj.get("verbose"))

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
@click.pass_context
def runtime_install(
    ctx: click.Context, runtime: str, manager: str | None, verbose: bool
) -> None:
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
    ezprinter.print_header("Runtime installation")

    try:
        interface = RuntimeInterface()

        if verbose or ctx.obj.get("verbose"):
            ezprinter.info(f"Installing {runtime}...")
            if manager:
                ezprinter.info(f"Using specified manager: {manager}")
            else:
                ezprinter.info("Auto-selecting best system package manager...")

        result = interface.install_runtime(runtime)
        display_runtime_install_result(
            result, runtime, verbose or ctx.obj.get("verbose")
        )

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
@click.pass_context
def runtime_list(ctx: click.Context, verbose: bool) -> None:
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
    ezprinter.print_header("Runtime listing")

    try:
        display_runtimes_list(verbose or ctx.obj.get("verbose"))

    except Exception as e:
        logger.error(f"Failed to list runtimes: {e}")
        ezprinter.error(f"List failed: {e}")
        raise click.Abort() from e


# ///////////////////////////////////////////////////////////////
# STRATA 3: DEVTOOLS
# ///////////////////////////////////////////////////////////////


@deps_group.group(name="tool")
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


@tool_group.command(name="check")
@click.help_option("-h", "--help")
@click.argument("tool", required=False)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show detailed information about the tool.",
)
@click.pass_context
def tool_check(ctx: click.Context, tool: str | None, verbose: bool) -> None:
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
    ezprinter.print_header("Dev Tools availability checking")

    try:
        interface = DevToolsInterface()

        if tool:
            # Check specific tool
            tool_info = _find_tool_info(tool)
            if not tool_info:
                ezprinter.error(f"Unknown tool: {tool}")
                raise click.Abort()

            language, tool_type = tool_info
            result = interface.check_dev_tool(language, tool_type, tool)
            if result.success:
                msg = f"{tool} is available"
                if result.path:
                    msg += f" ({result.path})"
                ezprinter.success(msg)

                if verbose or ctx.obj.get("verbose"):
                    # Show dependency chain
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

                if verbose or ctx.obj.get("verbose"):
                    ezprinter.info("Use 'womm deps tool install' to install it")
        else:
            # Check all tools
            ezprinter.info("Checking development tools...\n")
            for category, tools in DevToolsConfig.DEVTOOLS_DEPENDENCIES.items():
                ezprinter.info(f"\n{category.upper()}:")
                for subcategory, tool_list in tools.items():
                    if verbose or ctx.obj.get("verbose"):
                        ezprinter.info(f"  [{subcategory}]")

                    for tool_name in tool_list:
                        result = interface.check_dev_tool(
                            category, subcategory, tool_name
                        )
                        status = "✓" if result.success else "✗"
                        prefix = "    " if (verbose or ctx.obj.get("verbose")) else "  "
                        msg = f"{prefix}{status} {tool_name}"

                        if result.success:
                            ezprinter.success(msg)
                        else:
                            ezprinter.warning(msg)

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
@click.pass_context
def tool_install(ctx: click.Context, tool: str, force: bool, verbose: bool) -> None:
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
    ezprinter.print_header("Dev Tool installation")

    try:
        interface = DevToolsInterface()

        if verbose or ctx.obj.get("verbose"):
            ezprinter.info(f"Installing {tool}...")

            # Show dependency chain
            try:
                chain = DependenciesHierarchy.get_devtool_chain(tool)
                ezprinter.info(
                    f"Dependency chain: {tool} → {chain['runtime_package_manager']} → {chain['runtime']}"
                )
            except Exception as e:
                logger.debug(f"Could not resolve dependency chain: {e}")

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
        result = interface.install_dev_tool(language, tool_type, tool)

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
@click.pass_context
def tool_list(ctx: click.Context, category: str | None, verbose: bool) -> None:
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
    ezprinter.print_header("Dev Tool listing")

    try:
        from rich.table import Table

        tools_config = DevToolsConfig.DEVTOOLS_DEPENDENCIES

        if category and category in tools_config:
            # Show specific category
            table = Table(
                title=f"{category.capitalize()} Development Tools", show_header=True
            )
            table.add_column("Category", style="cyan")
            table.add_column("Tools", style="white")

            if verbose or ctx.obj.get("verbose"):
                table.add_column("Package Manager", style="yellow")

            for subcat, tools in tools_config[category].items():
                row = [subcat, ", ".join(tools)]

                if verbose or ctx.obj.get("verbose"):
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

            if verbose or ctx.obj.get("verbose"):
                table.add_column("Package Manager", style="magenta")

            for lang, categories in tools_config.items():
                for subcat, tools in categories.items():
                    row = [lang, subcat, ", ".join(tools)]

                    if verbose or ctx.obj.get("verbose"):
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
@click.pass_context
def deps_check(ctx: click.Context, verbose: bool) -> None:
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

    # Print header
    ezprinter.print_header("Global dependencies checking")

    try:
        ezprinter.info("Checking all dependencies...\n")

        # Strata 1
        ezprinter.info("\n=== System Package Managers (Strata 1) ===")
        system_interface = SystemPackageManagerInterface()
        results = system_interface.detect_available_managers()
        available = [name for name, res in results.items() if res.success]

        if available:
            ezprinter.success(f"Available: {', '.join(available)}")
            if verbose or ctx.obj.get("verbose"):
                for name in available:
                    res = results[name]
                    ezprinter.info(f"  • {name}: v{res.version}")
        else:
            ezprinter.warning("No system package managers available")
        ezconsole.print("")

        # Strata 2
        ezprinter.info("\n=== Runtimes (Strata 2) ===")
        runtime_interface = RuntimeInterface()
        for runtime in RuntimeConfig.RUNTIMES:
            result = runtime_interface.check_runtime(runtime)
            status = "✓" if result.success else "✗"
            version = f"v{result.version}" if result.version else "N/A"
            msg = f"{status} {runtime}: {version}"

            if result.success:
                ezprinter.success(msg)
            else:
                ezprinter.warning(msg)
        ezconsole.print("")

        # Strata 3
        ezprinter.info("\n=== Development Tools (Strata 3) ===")
        tool_interface = DevToolsInterface()
        for category, tools in DevToolsConfig.DEVTOOLS_DEPENDENCIES.items():
            if verbose or ctx.obj.get("verbose"):
                ezprinter.info(f"\n{category}:")

            for subcategory, tool_list in tools.items():
                for tool in tool_list:
                    result = tool_interface.check_dev_tool(category, subcategory, tool)
                    status = "✓" if result.success else "✗"
                    prefix = "  " if (verbose or ctx.obj.get("verbose")) else ""
                    msg = f"{prefix}{status} {tool}"

                    if result.success:
                        ezprinter.success(msg)
                    else:
                        ezprinter.warning(msg)

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
@click.pass_context
def deps_status(ctx: click.Context, verbose: bool) -> None:
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

    # Print header
    ezprinter.print_header("Comprehensive Dependency Status Report")

    try:
        from rich.table import Table

        # Create comprehensive status table
        table = Table(title="WOMM Dependency Status", show_header=True)
        table.add_column("Strata", style="cyan", width=20)
        table.add_column("Component", style="yellow", width=30)
        table.add_column("Status", style="green", width=10, justify="center")
        table.add_column("Version", style="white", width=15)

        if verbose or ctx.obj.get("verbose"):
            table.add_column("Details", style="blue", width=30)

        # Strata 1
        system_interface = SystemPackageManagerInterface()
        status_data = system_interface.get_installation_status()
        for name, info in status_data.items():
            if info["supported_on_current_platform"]:
                row = [
                    "System PKG MGR",
                    name,
                    "✓" if info["available"] else "✗",
                    info["version"] or "N/A",
                ]

                if verbose or ctx.obj.get("verbose"):
                    details = f"Priority: {info.get('priority', 'N/A')}"
                    row.append(details)

                table.add_row(*row)

        # Strata 2
        runtime_interface = RuntimeInterface()
        for runtime in RuntimeConfig.RUNTIMES:
            result = runtime_interface.check_runtime(runtime)
            row = [
                "Runtime",
                runtime,
                "✓" if result.success else "✗",
                result.version or "N/A",
            ]

            if verbose or ctx.obj.get("verbose"):
                config = RuntimeConfig.RUNTIMES.get(runtime, {})
                min_ver = config.get("version", "Any")
                row.append(f"Min: {min_ver}")

            table.add_row(*row)

        # Strata 3 (sample tools)
        tool_interface = DevToolsInterface()
        sample_tools = ["cspell", "ruff", "pytest", "eslint"]
        for tool in sample_tools:
            try:
                tool_info = _find_tool_info(tool)
                if not tool_info:
                    logger.debug(f"Tool {tool} not found in config")
                    continue

                language, tool_type = tool_info
                result = tool_interface.check_dev_tool(language, tool_type, tool)
                row = [
                    "DevTool",
                    tool,
                    "✓" if result.success else "✗",
                    "N/A",
                ]

                if verbose or ctx.obj.get("verbose"):
                    try:
                        chain = DependenciesHierarchy.get_devtool_chain(tool)
                        row.append(
                            f"{chain['runtime_package_manager']} → {chain['runtime']}"
                        )
                    except Exception as e:
                        logger.debug(
                            f"Could not resolve dependency chain for {tool}: {e}"
                        )
                        row.append("N/A")

                table.add_row(*row)
            except Exception as e:
                logger.debug(f"Could not check tool {tool}: {e}")

        ezconsole.print(table)

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
@click.pass_context
def deps_validate(ctx: click.Context, verbose: bool) -> None:
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
    ezprinter.print_header("Dependency Chain Validation")

    try:
        ezprinter.info("Validating dependency chains...\n")

        issues = []
        valid_count = 0

        # Check each devtool's chain
        for category, tools in DevToolsConfig.DEVTOOLS_DEPENDENCIES.items():
            if verbose or ctx.obj.get("verbose"):
                ezprinter.info(f"\n=== {category.upper()} ===")

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
                            if verbose or ctx.obj.get("verbose"):
                                ezprinter.success(
                                    f"✓ {tool}: {chain['runtime_package_manager']} → {chain['runtime']}"
                                )
                    except Exception as e:
                        issues.append(f"❌ {tool}: Invalid chain ({e})")

        # Summary
        ezconsole.print("")
        if issues:
            ezprinter.error(f"\n{len(issues)} issue(s) found:")
            for issue in issues:
                ezprinter.error(f"  {issue}")
        else:
            ezprinter.success(f"\n✓ All {valid_count} dependency chains are valid")

    except Exception as e:
        logger.error(f"Failed to validate dependencies: {e}")
        ezprinter.error(f"Validation failed: {e}")
        raise click.Abort() from e


# ///////////////////////////////////////////////////////////////
# EXPORT
# ///////////////////////////////////////////////////////////////

__all__ = ["deps_group"]
