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

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import os
import sys

# Third-party imports
import click

# Local imports
from . import (
    HAS_PROOF_FILE,
    __version__,
)
from .ui.common import ezlogger  # noqa: F401
from .ui.common import (
    ezpl_bridge,
    ezprinter,
)
from .utils.common import is_pip_installation
from .utils.womm_setup import is_valid_womm_installation

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////
# Platform-specific configuration

# Force UTF-8 encoding on Windows
if sys.platform == "win32":
    # Set environment variables for UTF-8
    os.environ["PYTHONIOENCODING"] = "utf-8"

HAS_PROOF_FILE = True  # noqa: F811

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
@click.version_option(version=__version__)
@click.pass_context
def womm(
    ctx: click.Context,
    log_level: str | None,
    log_file: str | None,
    log_json: bool,
) -> None:
    """🛠️ Works On My Machine - Universal development tools.

    Automatic installation, cross-platform configuration, global commands
    for Python and JavaScript projects.

    🔒 Enhanced with comprehensive security validation.
    """

    # ///////////////////////////////////////////////////////////////
    # INSTALLATION GUARD - Enforce installation workflow
    # ///////////////////////////////////////////////////////////////

    # Check if WOMM is properly installed and initialized
    if is_pip_installation():
        # In pip installations, verify installation validity before allowing commands
        invoked_cmd = ctx.invoked_subcommand

        # Commands allowed even without installation
        unguarded_commands = {
            "install",  # Installation command
            "system",  # System detection (diagnostic only)
            "help",  # Help command (implicit)
            None,  # No subcommand (show help)
        }

        # If invoking a guarded command, check installation validity
        if (
            invoked_cmd
            and invoked_cmd not in unguarded_commands
            and not is_valid_womm_installation()
        ):
            ezprinter.error(
                "WOMM Installation Required\n\n"
                "This WOMM installation has not been initialized yet.\n"
                "Please run the installation command first:\n\n"
                "  womm install\n\n"
                "After installation, you'll have full access to all WOMM commands."
            )
            sys.exit(1)

    # Configure logging early (if needed)
    # TODO: Configure logging via ezpl when available
    if log_level or log_file or log_json:
        ezprinter.warning(
            "Log configuration options are not yet fully supported via ezpl"
        )

    # Show welcome message only when no subcommand is provided
    if ctx.invoked_subcommand is None:
        ezpl_bridge.console.print(
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

        panel = ezprinter.create_info_panel("Welcome", info_content.strip())
        ezpl_bridge.console.print(panel)

        # Tips
        info_content = """
💡 Tips:
• Use WOMM commands in any directory
• Install globally for easy access
• Run security checks before using tools
• Explore all available commands with --help or -h
• Use --dry-run to preview changes without making them
"""

        panel = ezprinter.create_panel(
            info_content.strip(),
            title="💡 Tips",
            border_style="yellow",
        )
        ezpl_bridge.console.print(panel)


# ///////////////////////////////////////////////////////////////
# COMMAND REGISTRATION
# ///////////////////////////////////////////////////////////////
# Register all command groups and subcommands
# Commands are filtered based on HAS_PROOF_FILE:
# - Without proof file: Only install and system (setup phase)
# - With proof file: All commands except install (operational phase)

# Register core command groups (lazy imports to avoid loading all modules)
try:
    from .commands.core import install, path_cmd, uninstall

    # Only register path_cmd and uninstall if proof file exists
    if not HAS_PROOF_FILE:
        womm.add_command(install)

    # Only register path_cmd and uninstall if proof file exists
    if HAS_PROOF_FILE:
        womm.add_command(uninstall)
        womm.add_command(path_cmd)
except ImportError:
    pass

# Dynamic imports to avoid circular dependencies
# Only register project commands if proof file exists
if HAS_PROOF_FILE:
    try:
        from .commands.project import create_group

        womm.add_command(create_group)
    except ImportError:
        pass

    try:
        from .commands.tools import lint_group

        womm.add_command(lint_group)
    except ImportError:
        pass

    try:
        from .commands.tools import cspell_group

        womm.add_command(cspell_group)
    except ImportError:
        pass

# System commands are always available
try:
    from .commands.system import system_group

    womm.add_command(system_group)
except ImportError:
    pass

# Only register context commands if proof file exists
if HAS_PROOF_FILE:
    try:
        from .commands.system import context_group

        womm.add_command(context_group)
    except ImportError:
        pass

    try:
        from .commands.project import setup_group

        womm.add_command(setup_group)
    except ImportError:
        pass

    try:
        from .commands.project import template_group

        womm.add_command(template_group)
    except ImportError:
        pass

    try:
        from .commands.system import deps_group

        womm.add_command(deps_group)
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
