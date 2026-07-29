#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# WOMM CLI - Main CLI Entry Point
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""Click entry point for Works On My Machine."""

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
from . import __version__
from .commands.core import path_cmd
from .commands.project import create_group, setup_group, template_group
from .commands.system import context_group, deps_group, system_group
from .commands.tools import lint_group
from .shared import startup as _startup  # noqa: F401
from .ui.common import ezpl_bridge, ezprinter

# Force UTF-8 encoding on Windows.
if sys.platform == "win32":
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
@click.version_option(version=__version__)
@click.pass_context
def womm(
    ctx: click.Context,
    log_level: str | None,
    log_file: str | None,
    log_json: bool,
) -> None:
    """🛠️ Works On My Machine - Universal development tools."""
    if log_level or log_file or log_json:
        ezprinter.warning(
            "Log configuration options are not yet fully supported via ezpl"
        )

    if ctx.invoked_subcommand is None:
        ezpl_bridge.console.print(r"""
================================================================================
                    __      _____  __  __ __  __
                    \ \    / / _ \|  \/  |  \/  |
                     \ \/\/ / (_) | |\/| | |\/| |
                      \_/\_/ \___/|_|  |_|_|  |_|
================================================================================


""")
        panel = ezprinter.create_info_panel(
            "Welcome",
            "\n".join(
                [
                    "Universal development tools for Python and JavaScript projects.",
                    "",
                    "Features:",
                    "• Cross-platform project setup and configuration",
                    "• Security validation and safe execution",
                    "• Beautiful terminal interface with Rich",
                    "• Global command access",
                ]
            ),
        )
        ezpl_bridge.console.print(panel)


# ///////////////////////////////////////////////////////////////
# COMMAND REGISTRATION
# ///////////////////////////////////////////////////////////////


for command in (
    path_cmd,
    create_group,
    lint_group,
    system_group,
    context_group,
    setup_group,
    template_group,
    deps_group,
):
    womm.add_command(command)


def main() -> None:
    """Run the WOMM command-line interface."""
    womm()


if __name__ == "__main__":
    main()
