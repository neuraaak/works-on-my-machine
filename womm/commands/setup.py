#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SETUP - Setup Commands
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Setup commands for WOMM CLI.

This module handles configuration of existing projects using the modular architecture.
Provides commands for setting up development environments in existing projects.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys
from pathlib import Path
from typing import Any

# Third-party imports
import click

# Local imports
from ..core.managers.project import ProjectManager
from ..core.ui.common.console import print_error, print_info, print_success
from ..core.ui.project import ProjectWizard
from ..core.utils.project.project_detector import ProjectDetector

# ///////////////////////////////////////////////////////////////
# COMMAND GROUPS
# ///////////////////////////////////////////////////////////////


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help")
@click.pass_context
def setup_group(ctx: click.Context) -> None:
    """🔧 Configure existing projects with development tools."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ///////////////////////////////////////////////////////////////
# AUTO-DETECTION COMMANDS
# ///////////////////////////////////////////////////////////////


@setup_group.command("detect")
@click.help_option("-h", "--help")
@click.option(
    "-p",
    "--path",
    "project_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=".",
    help="Path to the project directory",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    help="Run in interactive mode with guided setup",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
def setup_detect(
    project_path: Path,
    interactive: bool,
    dry_run: bool,
) -> None:
    """🔍 Auto-detect project type and configure development environment."""

    # Initialize project manager
    project_manager = ProjectManager()

    try:
        # Detect project type
        detector = ProjectDetector()
        detected_type = detector.detect_project_type(project_path)

        if detected_type == "unknown" or not detected_type:
            print_error("No suitable project type detected in the specified directory")
            print_info("Supported project types: python, javascript, react, vue")
            sys.exit(1)

        print_success(f"Detected project type: {detected_type}")

        # Interactive mode
        if interactive:
            return _run_interactive_setup(project_manager, detected_type, project_path)

        # Non-interactive mode
        options = {"dry_run": dry_run}
        return _run_direct_setup(project_manager, detected_type, project_path, options)

    except Exception as e:
        print_error(f"Error detecting project type: {e}")
        sys.exit(1)


# ///////////////////////////////////////////////////////////////
# PYTHON PROJECT COMMANDS
# ///////////////////////////////////////////////////////////////


@setup_group.command("python")
@click.help_option("-h", "--help")
@click.option(
    "-p",
    "--path",
    "project_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=".",
    help="Path to the Python project directory",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    help="Run in interactive mode with guided setup",
)
@click.option(
    "--virtual-env",
    is_flag=True,
    help="Create virtual environment",
)
@click.option(
    "--install-deps",
    is_flag=True,
    help="Install dependencies",
)
@click.option(
    "--setup-dev-tools",
    is_flag=True,
    help="Setup development tools (linting, formatting, etc.)",
)
@click.option(
    "--setup-git-hooks",
    is_flag=True,
    help="Setup Git hooks",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
def setup_python(
    project_path: Path,
    interactive: bool,
    virtual_env: bool,
    install_deps: bool,
    setup_dev_tools: bool,
    setup_git_hooks: bool,
    dry_run: bool,
) -> None:
    """🐍 Configure existing Python project with development environment."""

    # Initialize project manager
    project_manager = ProjectManager()

    try:
        # Interactive mode
        if interactive:
            return _run_interactive_setup(project_manager, "python", project_path)

        # Non-interactive mode
        options = {
            "virtual_env": virtual_env,
            "install_deps": install_deps,
            "setup_dev_tools": setup_dev_tools,
            "setup_git_hooks": setup_git_hooks,
            "dry_run": dry_run,
        }
        return _run_direct_setup(project_manager, "python", project_path, options)

    except Exception as e:
        print_error(f"Error configuring Python project: {e}")
        sys.exit(1)


# ///////////////////////////////////////////////////////////////
# JAVASCRIPT PROJECT COMMANDS
# ///////////////////////////////////////////////////////////////


@setup_group.command("javascript")
@click.help_option("-h", "--help")
@click.option(
    "-p",
    "--path",
    "project_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=".",
    help="Path to the JavaScript project directory",
)
@click.option(
    "-t",
    "--type",
    "project_type",
    type=click.Choice(["javascript", "react", "vue"]),
    help="JavaScript project type (auto-detected if not specified)",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    help="Run in interactive mode with guided setup",
)
@click.option(
    "--install-deps",
    is_flag=True,
    help="Install dependencies",
)
@click.option(
    "--setup-dev-tools",
    is_flag=True,
    help="Setup development tools (linting, formatting, etc.)",
)
@click.option(
    "--setup-git-hooks",
    is_flag=True,
    help="Setup Git hooks",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
def setup_javascript(
    project_path: Path,
    project_type: str | None,
    interactive: bool,
    install_deps: bool,
    setup_dev_tools: bool,
    setup_git_hooks: bool,
    dry_run: bool,
) -> None:
    """🟨 Configure existing JavaScript project with development environment."""

    # Initialize project manager
    project_manager = ProjectManager()

    try:
        # Auto-detect type if not specified
        if not project_type:
            detector = ProjectDetector()
            detected_type = detector.detect_project_type(project_path)
            if detected_type in ["javascript", "react", "vue"]:
                project_type = detected_type
            else:
                print_error("Could not auto-detect JavaScript project type")
                print_info("Please specify --type (javascript, react, vue)")
                sys.exit(1)

        # Interactive mode
        if interactive:
            return _run_interactive_setup(project_manager, project_type, project_path)

        # Non-interactive mode
        options = {
            "install_deps": install_deps,
            "setup_dev_tools": setup_dev_tools,
            "setup_git_hooks": setup_git_hooks,
            "dry_run": dry_run,
        }
        return _run_direct_setup(project_manager, project_type, project_path, options)

    except Exception as e:
        print_error(f"Error configuring JavaScript project: {e}")
        sys.exit(1)


# ///////////////////////////////////////////////////////////////
# HELPER FUNCTIONS - INTERACTIVE MODES
# ///////////////////////////////////////////////////////////////


def _run_interactive_setup(
    project_manager: ProjectManager, project_type: str, project_path: Path
) -> int:
    """Run interactive project setup."""
    # Get setup configuration
    config = ProjectWizard.run_interactive_setup_for_existing_project(
        project_type, project_path
    )
    if not config:
        print_error("Project setup cancelled")
        return 1

    # Configure project
    success = project_manager.setup_project(
        project_type=project_type,
        project_path=project_path,
        **config.get("options", {}),
    )

    if success:
        return 0
    else:
        print_error(f"Failed to configure {project_type} project")
        return 1


# ///////////////////////////////////////////////////////////////
# HELPER FUNCTIONS - DIRECT MODES
# ///////////////////////////////////////////////////////////////


def _run_direct_setup(
    project_manager: ProjectManager,
    project_type: str,
    project_path: Path,
    options: dict[str, Any] | None = None,
) -> int:
    """Run direct project setup."""

    if options is None:
        options = {}

    # Configure project
    success = project_manager.setup_project(
        project_type=project_type,
        project_path=project_path,
        **options,
    )

    if success:
        return 0
    else:
        print_error(f"Failed to configure {project_type} project")
        return 1
