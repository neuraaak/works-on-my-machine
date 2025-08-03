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
    context,
    deploy,
    install,
    lint,
    new,
    spell,
    system,
)

# Add shared modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))


@click.group()
@click.version_option(version="1.0.0")
def womm():
    """🛠️ Works On My Machine - Universal development tools.

    Automatic installation, cross-platform configuration, global commands
    for Python and JavaScript projects.

    🔒 Enhanced with comprehensive security validation.
    """


# Register command groups
womm.add_command(install.install_group)
womm.add_command(new.new_group)
womm.add_command(lint.lint_group)
womm.add_command(spell.spell_group)
womm.add_command(system.system_group)
womm.add_command(deploy.deploy_group)
womm.add_command(context.context_group)


if __name__ == "__main__":
    womm()
