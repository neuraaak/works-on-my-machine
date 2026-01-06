#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# NEW - New Project Commands
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
New project commands for WOMM CLI.

This module handles creation of new Python and JavaScript projects using the modular architecture.
Provides interactive and direct modes for project creation with comprehensive setup.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys

# Third-party imports
import click

# Local imports
from ..core.managers.project import ProjectManager
from ..core.ui.common.console import (
    print_dry_run_message,
    print_dry_run_success,
    print_dry_run_warning,
    print_error,
    print_header,
)
from ..core.ui.project import ProjectWizard

# ///////////////////////////////////////////////////////////////
# COMMAND GROUPS
# ///////////////////////////////////////////////////////////////


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help")
@click.pass_context
def new_group(ctx: click.Context) -> None:
    """🆕 Create new projects with modern development setup."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ///////////////////////////////////////////////////////////////
# PYTHON PROJECT COMMANDS
# ///////////////////////////////////////////////////////////////


@new_group.command("python")
@click.help_option("-h", "--help")
@click.argument("project_name", required=False)
@click.option(
    "-c",
    "--current-dir",
    is_flag=True,
    help="Use current directory instead of creating a new one",
)
@click.option(
    "-t",
    "--target",
    help="Target directory where to create the project (default: current directory)",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    help="Run in interactive mode with guided setup",
)
@click.option(
    "--author-name",
    help="Author name for the project",
)
@click.option(
    "--author-email",
    help="Author email for the project",
)
@click.option(
    "--project-url",
    help="Project URL",
)
@click.option(
    "--project-repository",
    help="Project repository URL",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
def new_python(
    project_name: str | None,
    current_dir: bool,
    target: str | None,
    interactive: bool,
    author_name: str | None,
    author_email: str | None,
    project_url: str | None,
    project_repository: str | None,
    dry_run: bool,
) -> None:
    """🐍 Create a new Python project with full development environment."""

    # Initialize project manager
    project_manager = ProjectManager()

    try:
        # Interactive mode
        if interactive:
            if dry_run:
                print_header("🐍 Interactive Python Project Setup (DRY RUN)")
                print_dry_run_warning()
                print_dry_run_message(
                    "run interactive mode", "prompt user for project details"
                )
                print_dry_run_message("validate inputs", "check project configuration")
                print_dry_run_message(
                    "create project", "generate project structure and files"
                )
                print_dry_run_success()
                return 0
            else:
                return _run_interactive_python_setup(project_manager)

        # Non-interactive mode
        return _run_direct_python_setup(
            project_manager,
            project_name,
            current_dir,
            target,
            author_name,
            author_email,
            project_url,
            project_repository,
            dry_run,
        )

    except Exception as e:
        print_error(f"Error creating Python project: {e}")
        sys.exit(1)


# ///////////////////////////////////////////////////////////////
# JAVASCRIPT PROJECT COMMANDS
# ///////////////////////////////////////////////////////////////


@new_group.command("javascript")
@click.help_option("-h", "--help")
@click.argument("project_name", required=False)
@click.option(
    "-c",
    "--current-dir",
    is_flag=True,
    help="Use current directory instead of creating a new one",
)
@click.option(
    "-t",
    "--target",
    help="Target directory where to create the project (default: current directory)",
)
@click.option(
    "--type",
    "project_type",
    type=click.Choice(["node", "react", "vue"]),
    default="node",
    help="JavaScript project type",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    help="Run in interactive mode with guided setup",
)
@click.option(
    "--author-name",
    help="Author name for the project",
)
@click.option(
    "--author-email",
    help="Author email for the project",
)
@click.option(
    "--project-url",
    help="Project URL",
)
@click.option(
    "--project-repository",
    help="Project repository URL",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
def new_javascript(
    project_name: str | None,
    current_dir: bool,
    target: str | None,
    project_type: str,
    interactive: bool,
    author_name: str | None,
    author_email: str | None,
    project_url: str | None,
    project_repository: str | None,
    dry_run: bool,
) -> None:
    """🟨 Create a new JavaScript/Node.js project with development tools."""

    # Initialize project manager
    project_manager = ProjectManager()

    try:
        # Interactive mode
        if interactive:
            if dry_run:
                print_header("🟨 Interactive JavaScript Project Setup (DRY RUN)")
                print_dry_run_warning()
                print_dry_run_message(
                    "run interactive mode", "prompt user for project details"
                )
                print_dry_run_message("validate inputs", "check project configuration")
                print_dry_run_message(
                    "create project", "generate project structure and files"
                )
                print_dry_run_success()
                return 0
            else:
                return _run_interactive_javascript_setup(project_manager)

        # Non-interactive mode
        return _run_direct_javascript_setup(
            project_manager,
            project_name,
            current_dir,
            target,
            project_type,
            author_name,
            author_email,
            project_url,
            project_repository,
            dry_run,
        )

    except Exception as e:
        print_error(f"Error creating JavaScript project: {e}")
        sys.exit(1)


# ///////////////////////////////////////////////////////////////
# HELPER FUNCTIONS - INTERACTIVE MODES
# ///////////////////////////////////////////////////////////////


def _run_interactive_python_setup(project_manager: ProjectManager) -> int:
    """Run interactive Python project setup."""
    print_header("🐍 Interactive Python Project Setup")

    # Get project configuration
    config = ProjectWizard.run_interactive_setup()
    if not config:
        print_error("Project setup cancelled")
        return 1

    # Create project
    success = project_manager.create_project(
        project_type="python",
        project_name=config.get("project_name"),
        target=str(config.get("project_path").parent),
        **config.get("options", {}),
    )

    if success:
        return 0
    else:
        return 1


def _run_interactive_javascript_setup(project_manager: ProjectManager) -> int:
    """Run interactive JavaScript project setup."""
    print_header("🟨 Interactive JavaScript Project Setup")

    # Get project configuration
    config = ProjectWizard.run_interactive_setup()
    if not config:
        print_error("Project setup cancelled")
        return 1

    # Determine the project type based on configuration
    js_project_type = config.get("project_type", "node")

    # Map the project type to the correct ProjectManager type
    if js_project_type in ["react", "vue"]:
        pm_project_type = js_project_type  # Use directly: "react" or "vue"
    else:
        pm_project_type = "javascript"  # Use "javascript" for node, library, cli

    # Prepare options
    options = config.get("options", {})

    # Add project_type to options only when using "javascript" as main type
    # and it's not already in options
    if pm_project_type == "javascript" and "project_type" not in options:
        options["project_type"] = js_project_type

    # Remove project_type from options to avoid conflict with create_project parameter
    options.pop("project_type", None)

    # Create project
    success = project_manager.create_project(
        project_type=pm_project_type,
        project_name=config.get("project_name"),
        target=str(config.get("project_path").parent),
        **options,
    )

    if success:
        return 0
    else:
        return 1


# ///////////////////////////////////////////////////////////////
# HELPER FUNCTIONS - DIRECT MODES
# ///////////////////////////////////////////////////////////////


def _run_direct_python_setup(
    project_manager: ProjectManager,
    project_name: str | None,
    current_dir: bool,
    target: str | None,
    author_name: str | None,
    author_email: str | None,
    project_url: str | None,
    project_repository: str | None,
    dry_run: bool = False,
) -> int:
    """Run direct Python project setup."""

    # Validate project name if provided
    if project_name and not current_dir and not project_name.strip():
        print_error("Project name cannot be empty")
        return 1

    # Prepare options
    options = {}
    if author_name:
        options["author_name"] = author_name
    if author_email:
        options["author_email"] = author_email
    if project_url:
        options["project_url"] = project_url
    if project_repository:
        options["project_repository"] = project_repository
    if target:
        options["target"] = target

    # Create project
    success = project_manager.create_project(
        project_type="python",
        project_name=project_name,
        current_dir=current_dir,
        dry_run=dry_run,
        **options,
    )

    if success:
        return 0
    else:
        return 1


def _run_direct_javascript_setup(
    project_manager: ProjectManager,
    project_name: str | None,
    current_dir: bool,
    target: str | None,
    project_type: str,
    author_name: str | None,
    author_email: str | None,
    project_url: str | None,
    project_repository: str | None,
    dry_run: bool = False,
) -> int:
    """Run direct JavaScript project setup."""

    # Validate project name if provided
    if project_name and not current_dir and not project_name.strip():
        print_error("Project name cannot be empty")
        return 1

    # Prepare options
    options = {}
    if author_name:
        options["author_name"] = author_name
    if author_email:
        options["author_email"] = author_email
    if project_url:
        options["project_url"] = project_url
    if project_repository:
        options["project_repository"] = project_repository
    if target:
        options["target"] = target

    # Create project
    # Map CLI types to ProjectManager types
    pm_project_type = "javascript" if project_type == "node" else project_type

    success = project_manager.create_project(
        project_type=pm_project_type,
        project_name=project_name,
        current_dir=current_dir,
        dry_run=dry_run,
        **options,
    )

    if success:
        return 0
    else:
        return 1
