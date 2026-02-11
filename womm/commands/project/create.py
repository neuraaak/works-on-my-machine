#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CREATE - Create Project Commands
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Create project commands for WOMM CLI.

This module handles creation of new Python and JavaScript projects using the modular architecture.
Provides interactive and direct modes for project creation with comprehensive setup.
Supports minimal mode for creating only basic structure and files.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys
from pathlib import Path
from typing import Any

# Third-party imports
import click
from ezpl.types import LogLevel

# Local imports
from ...interfaces import ProjectManagerInterface
from ...ui.common import ezpl_bridge, ezprinter
from ...ui.project import ProjectWizard

# ///////////////////////////////////////////////////////////////
# COMMAND GROUPS
# ///////////////////////////////////////////////////////////////


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
@click.pass_context
def create_group(ctx: click.Context, verbose: bool) -> None:
    """🆕 Create new projects with modern development setup."""
    # Configure verbose mode if requested
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    if ctx.invoked_subcommand is None:
        # Auto-detect project type if no subcommand specified
        try:
            project_manager = ProjectManagerInterface()
            detection_result = project_manager.detect_project_type(Path.cwd())
            detected_type = detection_result.project_type
            confidence = detection_result.confidence
            if detected_type and detected_type != "unknown":
                ezprinter.success(
                    f"Detected project type: {detected_type} (confidence: {confidence}%)"
                )
                ezprinter.info(
                    f"Use 'womm create {detected_type} <project_name>' to create a project"
                )
            else:
                click.echo(ctx.get_help())
        except Exception:
            click.echo(ctx.get_help())


# ///////////////////////////////////////////////////////////////
# PYTHON PROJECT COMMANDS
# ///////////////////////////////////////////////////////////////


@create_group.command("python")
@click.help_option("-h", "--help")
@click.argument("project_name", required=False)
@click.option(
    "-c",
    "--current-dir",
    is_flag=True,
    help="Use current directory instead of creating a new one",
)
@click.option(
    "--target",
    help="Target directory where to create the project (default: current directory)",
)
@click.option(
    "-I",
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
    "--type",
    "project_type",
    type=click.Choice(["py", "django"]),
    help="Python project type (py, django). Auto-detected if not specified.",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force overwrite existing files without prompting",
)
@click.option(
    "--minimal",
    is_flag=True,
    help="Create only basic structure and files (no dependencies, no dev tools, no configs)",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def create_python(
    project_name: str | None,
    current_dir: bool,
    target: str | None,
    interactive: bool,
    author_name: str | None,
    author_email: str | None,
    project_url: str | None,
    project_repository: str | None,
    project_type: str | None,
    force: bool,
    minimal: bool,
    verbose: bool,
) -> None:
    """🐍 Create a new Python project with full development environment."""
    # Configure verbose mode if requested
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    # Initialize project manager (lazy loading)
    project_manager = ProjectManagerInterface()

    try:
        # Interactive mode
        if interactive:
            success = _run_interactive_python_setup(project_manager, minimal)
            if not success:
                sys.exit(1)
            return

        # Non-interactive mode
        success = _run_direct_python_setup(
            project_manager,
            project_name,
            current_dir,
            target,
            author_name,
            author_email,
            project_url,
            project_repository,
            project_type,
            force,
            minimal,
        )
        if not success:
            sys.exit(1)
        return

    except Exception as e:
        # Extract error message from exception
        error_msg = str(e)
        if hasattr(e, "message") and e.message:
            error_msg = e.message
        elif hasattr(e, "reason") and e.reason:
            error_msg = e.reason
        elif hasattr(e, "details") and e.details:
            error_msg = e.details

        ezprinter.error(f"Error creating Python project: {error_msg}")
        if hasattr(e, "details") and e.details and e.details != error_msg:
            ezprinter.info(f"Details: {e.details}")
        sys.exit(1)


# ///////////////////////////////////////////////////////////////
# JAVASCRIPT PROJECT COMMANDS
# ///////////////////////////////////////////////////////////////


@create_group.command("javascript")
@click.help_option("-h", "--help")
@click.argument("project_name", required=False)
@click.option(
    "-c",
    "--current-dir",
    is_flag=True,
    help="Use current directory instead of creating a new one",
)
@click.option(
    "--target",
    help="Target directory where to create the project (default: current directory)",
)
@click.option(
    "--type",
    "project_type",
    type=click.Choice(["js", "ts", "react", "vue", "react-ts", "vue-ts", "node"]),
    help="JavaScript project type. Auto-detected if not specified.",
)
@click.option(
    "-I",
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
    "--force",
    is_flag=True,
    help="Force overwrite existing files without prompting",
)
@click.option(
    "--minimal",
    is_flag=True,
    help="Create only basic structure and files (no dependencies, no dev tools, no configs)",
)
def create_javascript(
    project_name: str | None,
    current_dir: bool,
    target: str | None,
    project_type: str | None,
    interactive: bool,
    author_name: str | None,
    author_email: str | None,
    project_url: str | None,
    project_repository: str | None,
    force: bool,
    minimal: bool,
) -> None:
    """🟨 Create a new JavaScript/Node.js project with development tools."""

    # Initialize project manager
    project_manager = ProjectManagerInterface()

    try:
        # Interactive mode
        if interactive:
            success = _run_interactive_javascript_setup(project_manager, minimal)
            if not success:
                sys.exit(1)
            return

        # Non-interactive mode
        # Map "node" to "js" for backward compatibility
        if project_type == "node":
            project_type = "js"

        success = _run_direct_javascript_setup(
            project_manager,
            project_name,
            current_dir,
            target,
            project_type,
            author_name,
            author_email,
            project_url,
            project_repository,
            force,
            minimal,
        )
        if not success:
            sys.exit(1)
        return

    except Exception as e:
        ezprinter.error(f"Error creating JavaScript project: {e}")
        sys.exit(1)


# ///////////////////////////////////////////////////////////////
# HELPER FUNCTIONS - INTERACTIVE MODES
# ///////////////////////////////////////////////////////////////


def _run_interactive_python_setup(
    project_manager: ProjectManagerInterface, minimal: bool
) -> bool:
    """Run interactive Python project setup."""
    ezprinter.print_header("🐍 Interactive Python Project Setup")

    # Get project configuration
    config = ProjectWizard.run_interactive_setup()
    if not config:
        ezprinter.error("Project setup cancelled")
        return False

    project_path = config.get("project_path")
    if not isinstance(project_path, Path):
        ezprinter.error("Invalid project path returned by wizard")
        return False

    project_name = config.get("project_name")
    if project_name is not None and not isinstance(project_name, str):
        ezprinter.error("Invalid project name returned by wizard")
        return False

    # Create project
    options: dict[str, Any] = {
        key: value
        for key, value in config.items()
        if key not in {"project_type", "project_name", "project_path", "current_dir"}
    }
    options["minimal"] = minimal
    success = project_manager.create_project(
        project_type="python",
        project_name=project_name,
        target=str(project_path.parent),
        **options,
    )

    return bool(success)


def _run_interactive_javascript_setup(
    project_manager: ProjectManagerInterface, minimal: bool
) -> bool:
    """Run interactive JavaScript project setup."""
    ezprinter.print_header("🟨 Interactive JavaScript Project Setup")

    # Get project configuration
    config = ProjectWizard.run_interactive_setup()
    if not config:
        ezprinter.error("Project setup cancelled")
        return False

    project_path = config.get("project_path")
    if not isinstance(project_path, Path):
        ezprinter.error("Invalid project path returned by wizard")
        return False

    project_name = config.get("project_name")
    if project_name is not None and not isinstance(project_name, str):
        ezprinter.error("Invalid project name returned by wizard")
        return False

    # Determine the project type based on configuration
    js_project_type = config.get("project_type", "node")
    if not isinstance(js_project_type, str):
        js_project_type = "node"

    # Map the project type to the correct project type
    if js_project_type in ["react", "vue"]:
        pm_project_type = js_project_type  # Use directly: "react" or "vue"
    else:
        pm_project_type = "javascript"  # Use "javascript" for node, library, cli

    # Prepare options
    options: dict[str, Any] = {
        key: value
        for key, value in config.items()
        if key not in {"project_type", "project_name", "project_path", "current_dir"}
    }

    # Map js_project_type to type for JavaScript projects
    if pm_project_type == "javascript":
        # Map project type to type
        type_map = {
            "node": "js",
            "library": "js",
            "cli": "js",
            "react": "react",
            "vue": "vue",
        }
        project_type = type_map.get(js_project_type, "js")
        options["type"] = project_type

    # Remove project_type from options to avoid conflict with create_project parameter
    options["minimal"] = minimal

    # Create project
    success = project_manager.create_project(
        project_type=pm_project_type,
        project_name=project_name,
        target=str(project_path.parent),
        **options,
    )

    return bool(success)


# ///////////////////////////////////////////////////////////////
# HELPER FUNCTIONS - DIRECT MODES
# ///////////////////////////////////////////////////////////////


def _run_direct_python_setup(
    project_manager: ProjectManagerInterface,
    project_name: str | None,
    current_dir: bool,
    target: str | None,
    author_name: str | None,
    author_email: str | None,
    project_url: str | None,
    project_repository: str | None,
    project_type: str | None,
    force: bool,
    dry_run: bool = False,
    minimal: bool = False,
) -> bool:
    """Run direct Python project setup."""

    # Validate project name if provided
    if project_name and not current_dir and not project_name.strip():
        ezprinter.error("Project name cannot be empty")
        return False

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
    if project_type:
        options["type"] = project_type
    options["force"] = force
    options["minimal"] = minimal

    # Create project
    success = project_manager.create_project(
        project_type="python",
        project_name=project_name,
        current_dir=current_dir,
        dry_run=dry_run,
        **options,
    )

    return bool(success)


def _run_direct_javascript_setup(
    project_manager: ProjectManagerInterface,
    project_name: str | None,
    current_dir: bool,
    target: str | None,
    project_type: str | None,
    author_name: str | None,
    author_email: str | None,
    project_url: str | None,
    project_repository: str | None,
    force: bool,
    dry_run: bool = False,
    minimal: bool = False,
) -> bool:
    """Run direct JavaScript project setup."""

    # Validate project name if provided
    if project_name and not current_dir and not project_name.strip():
        ezprinter.error("Project name cannot be empty")
        return False

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
    if project_type:
        options["type"] = project_type
    options["force"] = force
    options["minimal"] = minimal

    # Create project
    # Use "javascript" as the base type, type will be handled by the manager
    success = project_manager.create_project(
        project_type="javascript",
        project_name=project_name,
        current_dir=current_dir,
        dry_run=dry_run,
        **options,
    )

    return bool(success)
