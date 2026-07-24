#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEPENDENCIES DISPLAY - Dependencies UI Display Functions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Dependencies display functions for Works On My Machine.

Provides display functions for development tools status and dependency information.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging

# Local imports
from ...exceptions.dependencies import DevToolsInterfaceError
from ...ui.common import ezconsole, ezprinter

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# DISPLAY FUNCTIONS
# ///////////////////////////////////////////////////////////////


def display_devtools_status_table(status: dict[str, dict]) -> None:
    """
    Display development tools status in a formatted table.

    Args:
        status: Status information with structure:
            {
                language: {
                    tool_type: {
                        tool: {
                            "installed": bool,
                            "path": str
                        }
                    }
                }
            }

    Raises:
        TypeError: If table display fails due to invalid data
    """
    try:
        # Build rows data
        rows = []
        for language, lang_tools in status.items():
            for tool_type, tools in lang_tools.items():
                for tool, info in tools.items():
                    status_icon = "✅" if info["installed"] else "❌"
                    status_text = "Installed" if info["installed"] else "Missing"
                    path_text = info.get("path", "Not found") or "Not found"
                    rows.append(
                        [
                            language,
                            tool_type,
                            tool,
                            f"{status_icon} {status_text}",
                            path_text,
                        ]
                    )

        # Create table using ezprinter
        table = ezprinter.create_table(
            title="Development Tools Status",
            columns=[
                ("Language", "cyan", False),
                ("Tool Type", "blue", False),
                ("Tool", "white", False),
                ("Status", "green", False),
                ("Path", "dim", False),
            ],
            rows=rows,
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


def display_runtime_table(results: dict) -> None:
    """
    Display runtime check results in a table.

    Args:
        results: Dictionary mapping runtime names to RuntimeResult objects
    """
    # Build rows data
    rows = []
    for runtime, result in results.items():
        if result and result.success:
            status = "✓"
            version = f"v{result.version}" if result.version else "N/A"
        else:
            status = "✗"
            version = "Not available"
        rows.append([runtime, status, version])

    # Create table using ezprinter
    table = ezprinter.create_table(
        title="Runtimes",
        columns=[
            ("Runtime", "cyan", False),
            ("Status", "green", False),
            ("Version", "yellow", False),
        ],
        rows=rows,
    )

    ezconsole.print(table)


def display_system_table(results: dict) -> None:
    """
    Display system package manager results in a table.

    Args:
        results: Dictionary mapping manager names to result objects
    """
    # Build rows data
    rows = []
    for name, result in results.items():
        if result and result.success:
            status = "✓"
            version = f"v{result.version}" if result.version else "N/A"
        else:
            status = "✗"
            version = "Not available"
        rows.append([name, status, version])

    # Create table using ezprinter
    table = ezprinter.create_table(
        title="System Package Managers",
        columns=[
            ("Manager", "cyan", False),
            ("Status", "green", False),
            ("Version", "yellow", False),
        ],
        rows=rows,
    )

    ezconsole.print(table)


def display_system_check_all(_interface, _verbose: bool = False) -> None:
    """DEPRECATED: Use interface.check_all_managers() instead."""
    logger.warning("display_system_check_all is deprecated")


def display_tool_table(results: dict) -> None:
    """
    Display development tool results in a table.

    Args:
        results: Dictionary mapping tool names to result objects
    """
    # Build rows data
    rows = []
    for tool, result in results.items():
        if result and result.success:
            status = "✓"
            available = "Yes"
        else:
            status = "✗"
            available = "No"
        rows.append([tool, status, available])

    # Create table using ezprinter
    table = ezprinter.create_table(
        title="Development Tools",
        columns=[
            ("Tool", "cyan", False),
            ("Status", "green", False),
            ("Available", "yellow", False),
        ],
        rows=rows,
    )

    ezconsole.print(table)


def display_tool_check_all(_interface, _verbose: bool = False) -> None:
    """DEPRECATED: Use interface.check_all_tools() instead."""
    logger.warning("display_tool_check_all is deprecated")


def display_runtime_check_specific(
    result, runtime: str, _verbose: bool = False
) -> None:
    """
    Display result of checking a specific runtime.

    Args:
        result: RuntimeResult from interface.check_runtime()
        runtime: Runtime name
        verbose: Whether to show detailed information
    """
    if result.success:
        ezprinter.success(f"✓ {runtime} is available")
        if result.version:
            ezprinter.info(f"  Version: {result.version}")
        if result.path:
            ezprinter.info(f"  Path: {result.path}")
    else:
        ezprinter.error(f"✗ {runtime} is not available")
        if result.error:
            ezprinter.info(f"  Details: {result.error}")


def display_runtime_install_result(
    result, runtime: str, _verbose: bool = False
) -> None:
    """
    Display result of runtime installation.

    Args:
        result: Result from runtime installation
        runtime: Runtime name
        _verbose: Whether to show detailed information
    """
    if result.success:
        ezprinter.success(f"✓ {runtime} installed successfully")
    else:
        ezprinter.error(f"✗ Failed to install {runtime}")


def display_runtimes_list(_verbose: bool = False) -> None:
    """
    Display list of available runtimes.

    Args:
        _verbose: Whether to show detailed information
    """
    from ...shared.configs.dependencies import RuntimeConfig

    runtimes = list(RuntimeConfig.RUNTIMES.keys())
    ezprinter.info(f"Available runtimes: {', '.join(runtimes)}")


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "display_devtools_status_table",
    "display_runtime_check_specific",
    "display_runtime_install_result",
    "display_runtime_table",
    "display_runtimes_list",
    "display_system_check_all",
    "display_system_table",
    "display_tool_check_all",
    "display_tool_table",
]
