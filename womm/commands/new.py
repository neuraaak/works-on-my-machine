#!/usr/bin/env python3
"""
New project commands for WOMM CLI.
Handles creation of new Python and JavaScript projects.
"""

import sys
from pathlib import Path

import click

from shared.core.results import SecurityResult, ValidationResult
from shared.dependency_manager import dependency_manager

# Import UI and Result classes
from shared.ui import (
    print_dependency_check_result,
    print_installation_result,
    print_new_project_complete,
    print_new_project_error,
    print_new_project_progress,
    print_security_result,
    print_validation_result,
)

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

    # 0. Prompt for project name if not provided and not current-dir
    if not project_name and not current_dir:
        from shared.ui import print_prompt

        project_name = print_prompt("Nom du projet Python", required=True)
        if not project_name:
            print_new_project_error("python", "unknown", "Nom de projet requis")
            sys.exit(1)

    # 1. Security validation for project name
    if project_name and SECURITY_AVAILABLE:
        print_new_project_progress("Security validation", "Validating project name")
        is_valid, error = validate_user_input(project_name, "project_name")
        validation_result = ValidationResult(
            success=is_valid,
            input_type="project_name",
            input_value=project_name,
            error=error,
        )
        print_validation_result(validation_result)

        if not is_valid:
            print_new_project_error("python", project_name, error)
            sys.exit(1)

    # 2. Check dependencies
    print_new_project_progress("Dependency check", "Checking Python availability")
    dep_check_result = dependency_manager.check_dependencies(["python"])
    print_dependency_check_result(dep_check_result)

    # 3. Install dependencies if needed
    if not dep_check_result.all_available:
        print_new_project_progress(
            "Dependency installation", "Installing missing dependencies"
        )
        install_result = dependency_manager.install_dependencies(["python"])
        print_installation_result(install_result)

        if not install_result.success:
            print_new_project_error(
                "python", project_name or "unknown", "Dependency installation failed"
            )
            sys.exit(1)

    # 4. Security validation for script execution
    script_path = resolve_script_path("languages/python/scripts/setup_project.py")

    if SECURITY_AVAILABLE:
        print_new_project_progress("Script validation", "Validating setup script")
        from ..utils.security import security_validator

        is_valid, error = security_validator.validate_script_execution(script_path)
        security_result = SecurityResult(
            success=is_valid, error=error, security_level="high"
        )
        print_security_result(security_result)

        if not is_valid:
            print_new_project_error(
                "python",
                project_name or "unknown",
                f"Script validation failed: {error}",
            )
            sys.exit(1)

    # 5. Build and execute command
    print_new_project_progress("Project setup", "Executing setup script")
    cmd = [sys.executable, str(script_path)]
    if current_dir:
        cmd.append("--current-dir")
    elif project_name:
        cmd.append(project_name)

    # 6. Execute setup script
    if SECURITY_AVAILABLE:
        result = run_secure_command(cmd, "Setting up Python project")
    else:
        from shared.core.cli_manager import run_command

        result = run_command(cmd, "Setting up Python project")

    # 7. Handle result
    if result.success:
        project_path = Path.cwd() / (project_name or Path.cwd().name)
        print_new_project_complete(
            "Python", project_name or "current", str(project_path)
        )
    else:
        print_new_project_error(
            "python", project_name or "unknown", result.stderr or "Setup failed"
        )
        sys.exit(1)


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

    # 0. Prompt for project name if not provided and not current-dir
    if not project_name and not current_dir:
        from shared.ui import print_prompt

        project_name = print_prompt("Nom du projet JavaScript", required=True)
        if not project_name:
            print_new_project_error("javascript", "unknown", "Nom de projet requis")
            sys.exit(1)

    # 1. Security validation for project name
    if project_name and SECURITY_AVAILABLE:
        print_new_project_progress("Security validation", "Validating project name")
        is_valid, error = validate_user_input(project_name, "project_name")
        validation_result = ValidationResult(
            success=is_valid,
            input_type="project_name",
            input_value=project_name,
            error=error,
        )
        print_validation_result(validation_result)

        if not is_valid:
            print_new_project_error("javascript", project_name, error)
            sys.exit(1)

    # 2. Check dependencies
    print_new_project_progress("Dependency check", "Checking Node.js availability")
    dep_check_result = dependency_manager.check_dependencies(["node", "npm"])
    print_dependency_check_result(dep_check_result)

    # 3. Install dependencies if needed
    if not dep_check_result.all_available:
        print_new_project_progress(
            "Dependency installation", "Installing missing dependencies"
        )
        install_result = dependency_manager.install_dependencies(["node", "npm"])
        print_installation_result(install_result)

        if not install_result.success:
            print_new_project_error(
                "javascript",
                project_name or "unknown",
                "Dependency installation failed",
            )
            sys.exit(1)

    # 4. Security validation for script execution
    script_path = resolve_script_path("languages/javascript/scripts/setup_project.py")

    if SECURITY_AVAILABLE:
        print_new_project_progress("Script validation", "Validating setup script")
        from ..utils.security import security_validator

        is_valid, error = security_validator.validate_script_execution(script_path)
        security_result = SecurityResult(
            success=is_valid, error=error, security_level="high"
        )
        print_security_result(security_result)

        if not is_valid:
            print_new_project_error(
                "javascript",
                project_name or "unknown",
                f"Script validation failed: {error}",
            )
            sys.exit(1)

    # 5. Build and execute command
    print_new_project_progress(
        "Project setup", f"Executing {project_type} setup script"
    )
    cmd = [sys.executable, str(script_path)]
    if current_dir:
        cmd.append("--current-dir")
    elif project_name:
        cmd.append(project_name)

    cmd.extend(["--type", project_type])

    # 6. Execute setup script
    if SECURITY_AVAILABLE:
        result = run_secure_command(cmd, f"Setting up {project_type} project")
    else:
        from shared.core.cli_manager import run_command

        result = run_command(cmd, f"Setting up {project_type} project")

    # 7. Handle result
    if result.success:
        project_path = Path.cwd() / (project_name or Path.cwd().name)
        print_new_project_complete(
            "JavaScript", project_name or "current", str(project_path)
        )
    else:
        print_new_project_error(
            "javascript", project_name or "unknown", result.stderr or "Setup failed"
        )
        sys.exit(1)


@new_group.command("detect")
@click.argument("project_name", required=False)
@click.option("--current-dir", is_flag=True, help="Configure current directory")
def new_detect(project_name, current_dir):
    """Auto-detect project type and create appropriate setup."""

    print_new_project_progress("Project detection", "Detecting project type")
    script_path = resolve_script_path("shared/project/project_detector.py")

    cmd = [sys.executable, str(script_path)]
    if current_dir:
        cmd.append("--current-dir")
    elif project_name:
        cmd.append(project_name)

    from shared.core.cli_manager import run_command

    result = run_command(cmd, "Auto-detecting and setting up project")

    if result.success:
        project_path = Path.cwd() / (project_name or Path.cwd().name)
        print_new_project_complete(
            "Auto-detected", project_name or "current", str(project_path)
        )
    else:
        print_new_project_error(
            "auto-detected",
            project_name or "unknown",
            result.stderr or "Detection failed",
        )
        sys.exit(1)
