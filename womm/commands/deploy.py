#!/usr/bin/env python3
"""
Deployment commands for WOMM CLI.
Handles deployment and distribution tools.
"""

import sys

import click

from ..utils.path_manager import resolve_script_path


@click.group()
def deploy_group():
    """📦 Deployment and distribution tools."""


@deploy_group.command("tools")
@click.option(
    "--target",
    type=click.Path(),
    default="~/.womm",
    help="Target directory for deployment",
)
@click.option("--global", "create_global", is_flag=True, help="Create global commands")
def deploy_tools(target, create_global):
    """Deploy development tools to global directory."""
    script_path = resolve_script_path("shared/installation/deploy-devtools.py")

    cmd = [sys.executable, str(script_path), "--target", target]
    if create_global:
        cmd.append("--install-global")

    from shared.core.cli_manager import run_command

    result = run_command(cmd, f"Deploying tools to {target}")
    sys.exit(0 if result.success else 1)
