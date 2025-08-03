#!/usr/bin/env python3
"""
Works On My Machine (WOMM) - Main CLI Entry Point.
Modular CLI interface for universal development tools.
"""

import sys
from pathlib import Path

import click

# Import and register all command modules
from .commands import (
    backup_path,
    context,
    deploy,
    install,
    lint,
    new,
    restore_path,
    spell,
    system,
    uninstall,
)

# Add shared modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))


@click.group(invoke_without_command=True)
@click.version_option(version="1.0.0")
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
            from shared.ui import console, print_header
            from shared.ui.panels import create_info_panel

            print_header("Works On My Machine")

            info_content = """
            Universal development tools for Python and JavaScript projects.

            Features:
            • Automatic project setup and configuration
            • Cross-platform compatibility
            • Security validation and safe execution
            • Beautiful terminal interface with Rich
            • Global command access
            """

            panel = create_info_panel("Welcome", info_content.strip())
            console.print(panel)

        except ImportError:
            # Fallback to basic output
            pass


# Register command groups
womm.add_command(install)
womm.add_command(uninstall)
womm.add_command(backup_path)
womm.add_command(restore_path)

womm.add_command(new.new_group)
womm.add_command(lint.lint_group)
womm.add_command(spell.spell_group)
womm.add_command(system.system_group)
womm.add_command(deploy.deploy_group)
womm.add_command(context.context_group)


if __name__ == "__main__":
    womm()
