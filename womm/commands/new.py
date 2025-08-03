#!/usr/bin/env python3
"""
New project commands for WOMM CLI.
Handles creation of new Python and JavaScript projects.
"""

import sys

import click

from ..utils.path_manager import resolve_script_path
from ..utils.security import SECURITY_AVAILABLE, run_secure_command, validate_user_input


@click.group()
def new_group():
    """🆕 Create new projects."""


@new_group.command("python")
@click.argument("project_name", required=False)
@click.option(
    "--current-dir",
    is_flag=True,
    help="Configure current directory instead of creating new one",
)
def new_python(project_name, current_dir):
    """Create a new Python project with full development environment."""
    # Security validation for project name
    if project_name and SECURITY_AVAILABLE:
        is_valid, error = validate_user_input(project_name, "project_name")
        if not is_valid:
            click.echo(f"❌ Invalid project name: {error}", err=True)
            sys.exit(1)

    # Check and install Python if needed
    from shared.dependency_manager import check_and_install_dependencies
    if not check_and_install_dependencies(["python"]):
        click.echo("❌ Python installation required but not completed")
        sys.exit(1)

    script_path = resolve_script_path("languages/python/scripts/setup_project.py")

    # Security validation for script execution
    if SECURITY_AVAILABLE:
        from ..utils.security import security_validator
        is_valid, error = security_validator.validate_script_execution(script_path)
        if not is_valid:
            click.echo(f"❌ Script validation failed: {error}", err=True)
            sys.exit(1)

    cmd = [sys.executable, str(script_path)]
    if current_dir:
        cmd.append("--current-dir")
    elif project_name:
        cmd.append(project_name)

    # Use secure command execution if available
    if SECURITY_AVAILABLE:
        result = run_secure_command(cmd, "Setting up Python project")
    else:
        from shared.core.cli_manager import run_command
        result = run_command(cmd, "Setting up Python project")

    sys.exit(0 if result.success else 1)


@new_group.command("javascript")
@click.argument("project_name", required=False)
@click.option(
    "--current-dir",
    is_flag=True,
    help="Configure current directory instead of creating new one",
)
@click.option(
    "--type",
    "project_type",
    type=click.Choice(["node", "react", "vue", "express"]),
    default="node",
    help="JavaScript project type",
)
def new_javascript(project_name, current_dir, project_type):
    """Create a new JavaScript/Node.js project with development tools."""
    # Security validation for project name
    if project_name and SECURITY_AVAILABLE:
        is_valid, error = validate_user_input(project_name, "project_name")
        if not is_valid:
            click.echo(f"❌ Invalid project name: {error}", err=True)
            sys.exit(1)

    script_path = resolve_script_path("languages/javascript/scripts/setup_project.py")

    # Security validation for script execution
    if SECURITY_AVAILABLE:
        from ..utils.security import security_validator
        is_valid, error = security_validator.validate_script_execution(script_path)
        if not is_valid:
            click.echo(f"❌ Script validation failed: {error}", err=True)
            sys.exit(1)

    cmd = [sys.executable, str(script_path)]
    if current_dir:
        cmd.append("--current-dir")
    elif project_name:
        cmd.append(project_name)

    cmd.extend(["--type", project_type])

    # Use secure command execution if available
    if SECURITY_AVAILABLE:
        result = run_secure_command(cmd, f"Setting up {project_type} project")
    else:
        from shared.core.cli_manager import run_command
        result = run_command(cmd, f"Setting up {project_type} project")

    sys.exit(0 if result.success else 1)


@new_group.command("detect")
@click.argument("project_name", required=False)
@click.option("--current-dir", is_flag=True, help="Configure current directory")
def new_detect(project_name, current_dir):
    """Auto-detect project type and create appropriate setup."""
    script_path = resolve_script_path("shared/project/project_detector.py")

    cmd = [sys.executable, str(script_path)]
    if current_dir:
        cmd.append("--current-dir")
    elif project_name:
        cmd.append(project_name)

    from shared.core.cli_manager import run_command
    result = run_command(cmd, "Auto-detecting and setting up project")
    sys.exit(0 if result.success else 1)
