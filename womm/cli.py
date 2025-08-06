#!/usr/bin/env python3
"""
Works On My Machine (WOMM) - Main CLI Entry Point.
Modular CLI interface for universal development tools.
"""

# IMPORTS
########################################################
# External modules and dependencies

import os
import sys
from pathlib import Path

import click

# CONSTANTS
########################################################
# Platform-specific configuration

# Force UTF-8 encoding on Windows
if sys.platform == "win32":
    # Set environment variables for UTF-8
    os.environ["PYTHONIOENCODING"] = "utf-8"

# IMPORTS
########################################################
# Internal modules and command imports

# Import and register all command modules
# Add shared modules to path - works both for development and PyPI installation
import importlib.util

from . import __version__
from .commands import (
    backup_path,
    context,
    install,
    lint,
    new,
    restore_path,
    spell,
    system,
    uninstall,
)

# CONFIGURATION
########################################################
# Path configuration and module setup

# Check if shared module is available (PyPI installation)
if importlib.util.find_spec("shared") is None:
    # Fallback to path insertion (development)
    sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

# MAIN FUNCTIONS
########################################################
# Core CLI functionality and command groups


@click.group(invoke_without_command=True)
@click.version_option(version=__version__)
@click.pass_context
def womm(ctx):
    """🛠️ Works On My Machine - Universal development tools.

    Automatic installation, cross-platform configuration, global commands
    for Python and JavaScript projects.

    🔒 Enhanced with comprehensive security validation.
    """

    # Show welcome message only when no subcommand is provided
    if ctx.invoked_subcommand is None:
        try:
            from shared.ui import console
            from shared.ui.panels import create_info_panel

            print(
                r"""
================================================================================
                    __      _____  __  __ __  __
                    \ \    / / _ \|  \/  |  \/  |
                     \ \/\/ / (_) | |\/| | |\/| |
                      \_/\_/ \___/|_|  |_|_|  |_|

================================================================================


"""
            )

            # Welcome message
            info_content = """
Universal development tools for Python and JavaScript projects.

Features:
• Automatic project setup and configuration
• Cross-platform compatibility
• Security validation and safe execution
• Beautiful terminal interface with Rich
• Global command access
"""

            panel = create_info_panel("Welcome", info_content.strip(), padding=(1, 1))
            console.print(panel)

            # Tips
            info_content = """
💡 Tips:
• Use WOMM commands in any directory
• Install globally for easy access
• Run security checks before using tools
• Explore all available commands with --help
"""

            from shared.ui.panels import create_panel

            panel = create_panel(
                info_content.strip(),
                title="💡 Tips",
                border_style="yellow",
                padding=(1, 1),
                width=80,
            )
            console.print(panel)

        except ImportError:
            # Fallback to basic output
            pass


# COMMAND REGISTRATION
########################################################
# Register all command groups and subcommands

# Register command groups
womm.add_command(install)
womm.add_command(uninstall)
womm.add_command(backup_path)
womm.add_command(restore_path)

womm.add_command(new.new_group)
womm.add_command(lint.lint_group)
womm.add_command(spell.spell_group)
womm.add_command(system.system_group)
womm.add_command(context.context_group)

# UTILITY FUNCTIONS
########################################################
# Entry point and execution helpers


def main():
    """Main entry point for PyPI installation."""
    womm()


if __name__ == "__main__":
    womm()
