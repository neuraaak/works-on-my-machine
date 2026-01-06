#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# WOMM CLI - Main CLI Entry Point
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Works On My Machine (WOMM) - Main CLI Entry Point.

Modular CLI interface for universal development tools.
Provides the main Click-based command-line interface for WOMM.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import os
import sys

# Third-party imports
import click

# Local imports
# Import version and core commands only to avoid circular imports
from . import __version__
from .commands import install, path_cmd, uninstall

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////
# Platform-specific configuration

# Force UTF-8 encoding on Windows
if sys.platform == "win32":
    # Set environment variables for UTF-8
    os.environ["PYTHONIOENCODING"] = "utf-8"

# ///////////////////////////////////////////////////////////////
# MAIN CLI FUNCTION
# ///////////////////////////////////////////////////////////////


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help")
@click.option(
    "--log-level",
    type=click.Choice(
        ["debug", "info", "warn", "error", "critical"], case_sensitive=False
    ),
    default=None,
    help="Configure console log level",
)
@click.option(
    "--log-file",
    type=click.Path(dir_okay=False, path_type=str),
    default=None,
    help="Enable file logging to the given path",
)
@click.option(
    "--log-json/--no-log-json",
    default=False,
    help="Use JSON lines format for file logs",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes (global mode)",
)
@click.version_option(version=__version__)
@click.pass_context
def womm(
    ctx: click.Context,
    log_level: str | None,
    log_file: str | None,
    log_json: bool,
    dry_run: bool,
) -> None:
    """🛠️ Works On My Machine - Universal development tools.

    Automatic installation, cross-platform configuration, global commands
    for Python and JavaScript projects.

    🔒 Enhanced with comprehensive security validation.
    """

    # Configure logging early
    from .core.ui.common.console import (
        configure_logging,
        get_log_level,
        print_warn,
        to_loglevel,
    )

    try:
        if log_level or log_file or log_json:
            level_to_set = to_loglevel(log_level) if log_level else get_log_level()
            configure_logging(level=level_to_set, file=log_file, json_format=log_json)
    except Exception as e:  # noqa: BLE001
        print_warn(f"Failed to configure logging: {e}")

    # Set global dry-run mode if specified
    if dry_run:
        os.environ["WOMM_DRY_RUN"] = "1"
        from .core.ui.common.console import print_system

        print_system("🔍 GLOBAL DRY-RUN MODE ENABLED - No changes will be made")

    # Show welcome message only when no subcommand is provided
    if ctx.invoked_subcommand is None:
        try:
            from .core.ui.common.console import console
            from .core.ui.common.panels import create_info_panel

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
• Explore all available commands with --help or -h
• Use --dry-run to preview changes without making them
"""

            from .core.ui.common.panels import create_panel

            panel = create_panel(
                info_content.strip(),
                title="💡 Tips",
                border_style="yellow",
                padding=(1, 1),
                width=80,
            )
            console.print(panel)

        except Exception:
            # In normal operation, UI should be available; if not, re-raise
            raise


# ///////////////////////////////////////////////////////////////
# COMMAND REGISTRATION
# ///////////////////////////////////////////////////////////////
# Register all command groups and subcommands

# Register core command groups
womm.add_command(install)
womm.add_command(uninstall)
womm.add_command(path_cmd)

# Dynamic imports to avoid circular dependencies
try:
    from .commands import new

    womm.add_command(new.new_group)
except ImportError:
    pass

try:
    from .commands import lint

    womm.add_command(lint.lint_group)
except ImportError:
    pass

try:
    from .commands import spell

    womm.add_command(spell.spell_group)
except ImportError:
    pass

try:
    from .commands import system

    womm.add_command(system.system_group)
except ImportError:
    pass

try:
    from .commands import context

    womm.add_command(context.context_group)
except ImportError:
    pass

try:
    from .commands import setup

    womm.add_command(setup.setup_group)
except ImportError:
    pass

try:
    from .commands import template

    womm.add_command(template.template_group)
except ImportError:
    pass

# ///////////////////////////////////////////////////////////////
# UTILITY FUNCTIONS
# ///////////////////////////////////////////////////////////////
# Entry point and execution helpers


def main() -> None:
    """Main entry point for PyPI installation."""
    womm()


# ///////////////////////////////////////////////////////////////
# EXECUTION ENTRY POINT
# ///////////////////////////////////////////////////////////////

if __name__ == "__main__":
    womm()
