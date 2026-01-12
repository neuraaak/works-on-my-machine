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
from ...ui.common import ezconsole

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
    from rich.table import Table

    try:
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


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "display_devtools_status_table",
]
