#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM - System Commands
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
System commands for WOMM CLI.

This module handles system detection and prerequisites installation.
Provides commands for detecting system information and installing required tools.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys

# Third-party imports
import click

# Local imports
from ..core.ui.common.console import print_error
from ..core.utils.security.security_validator import security_validator

# ///////////////////////////////////////////////////////////////
# COMMAND GROUPS
# ///////////////////////////////////////////////////////////////


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help")
@click.pass_context
def system_group(ctx: click.Context) -> None:
    """🔧 System detection and prerequisites."""
    # If no subcommand is provided, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ///////////////////////////////////////////////////////////////
# SYSTEM DETECTION COMMANDS
# ///////////////////////////////////////////////////////////////


@system_group.command("detect")
@click.help_option("-h", "--help")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
def system_detect(dry_run: bool) -> None:
    """🔍 Detect system information and available tools."""
    # Lazy import to avoid slow startup
    from ..core.managers.system import SystemManager

    # Use SystemManager for system detection with integrated UI
    system_manager = SystemManager()
    system_manager.detect_system(dry_run=dry_run)


# ///////////////////////////////////////////////////////////////
# ENVIRONMENT MANAGEMENT COMMANDS
# ///////////////////////////////////////////////////////////////


@system_group.command("refresh-env")
@click.help_option("-h", "--help")
@click.option(
    "-t",
    "--target",
    type=click.Path(),
    help="Custom target directory (default: ~/.womm)",
)
def system_refresh_env(target: str | None) -> None:
    """🔄 Refresh environment variables (Windows only)."""
    # Security validation for target path
    if target:
        is_valid = security_validator.validate_directory_path(target)
        if not is_valid:
            print_error(f"Invalid target path: {target}")
            sys.exit(1)

    try:
        # Use EnvironmentManager for environment refresh
        from ..core.managers.system.environment_manager import EnvironmentManager

        environment_manager = EnvironmentManager()

        if environment_manager.platform != "windows":
            click.echo(
                "[INFO] Environment refresh is only available on Windows", err=True
            )
            sys.exit(0)

        success = environment_manager.refresh_environment_with_ui()

        if not success:
            sys.exit(1)

    except Exception as e:
        print_error(f"Unexpected environment refresh error: {e}")
        sys.exit(1)


# ///////////////////////////////////////////////////////////////
# PREREQUISITES INSTALLATION COMMANDS
# ///////////////////////////////////////////////////////////////


@system_group.command("install")
@click.help_option("-h", "--help")
@click.option(
    "-c",
    "--check",
    is_flag=True,
    help="Only check prerequisites",
)
@click.option(
    "-p",
    "--pm-args",
    help="Extra arguments passed to the package manager (quoted string)",
    multiple=True,
)
@click.option(
    "-a",
    "--ask-path",
    is_flag=True,
    help="Interactively ask for an installation path (best-effort, Windows only)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
@click.argument("tools", nargs=-1, type=click.Choice(["python", "node", "git", "all"]))
def system_install(
    check: bool,
    pm_args: tuple[str, ...],
    ask_path: bool,
    dry_run: bool,
    tools: tuple[str, ...],
) -> None:
    """📦 Install system prerequisites."""
    # Lazy import to avoid slow startup
    from ..core.managers.system import SystemManager

    # Use SystemManager for prerequisites management with integrated UI
    system_manager = SystemManager()
    if check:
        system_manager.check_prerequisites(list(tools))
    else:
        # Flatten pm_args (Click multiple=True yields a tuple of strings)
        extra_args = [a for a in pm_args if a]
        system_manager.install_prerequisites(
            list(tools), pm_args=extra_args, ask_path=ask_path, dry_run=dry_run
        )
