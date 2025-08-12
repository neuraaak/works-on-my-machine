#!/usr/bin/env python3
"""
New project commands for WOMM CLI.
Handles creation of new Python and JavaScript projects.
"""

# IMPORTS
########################################################
# External modules and dependencies

import sys
from pathlib import Path

import click

from ..core.dependencies.runtime_manager import runtime_manager
from ..core.ui.console import console

# IMPORTS
########################################################
# Internal modules and dependencies
from ..core.utils.results import SecurityResult, ValidationResult

# IMPORTS
########################################################
# Local utility imports
from ..utils.path_resolver import resolve_script_path
from ..utils.security import run_secure_command, security_validator, validate_user_input

# MAIN FUNCTIONS
########################################################
# Core CLI functionality and command groups


@click.group()
def new_group():
    """🆕 Create new projects."""


# UTILITY FUNCTIONS
########################################################
# Helper functions and utilities


def print_new_project_progress(step: str, message: str):
    """Display project creation progress"""
    console.print(f"🔄 {step}: {message}", style="blue")


def print_new_project_complete(project_type: str, project_name: str, project_path: str):
    """Display project creation completion"""
    console.print(
        f"✅ {project_type} project '{project_name}' created successfully!",
        style="green",
    )
    console.print(f"📁 Location: {project_path}", style="cyan")


def print_new_project_error(project_type: str, project_name: str, error: str):
    """Display project creation error"""
    console.print(
        f"❌ Failed to create {project_type} project '{project_name}': {error}",
        style="red",
    )


def print_dependency_check_result(result):
    """Display dependency check result"""
    if result.all_available:
        console.print("✅ All dependencies are available", style="green")
    else:
        console.print(
            f"⚠️ Missing dependencies: {', '.join(result.missing)}", style="yellow"
        )


def print_installation_result(result):
    """Display installation result"""
    if result.success:
        console.print("✅ Dependencies installed successfully", style="green")
    else:
        console.print(f"❌ Installation failed: {result.error}", style="red")


def print_security_result(result):
    """Display security validation result"""
    if result.success:
        console.print("✅ Security validation passed", style="green")
    else:
        console.print(f"❌ Security validation failed: {result.error}", style="red")


def print_validation_result(result):
    """Display input validation result"""
    if result.success:
        console.print("✅ Input validation passed", style="green")
    else:
        console.print(f"❌ Input validation failed: {result.error}", style="red")


def print_prompt(message: str, required: bool = False) -> str:
    """Display a prompt and get user input"""
    prompt_text = f"{message}: "
    if required:
        prompt_text += "(required) "
    return input(prompt_text)


# COMMAND FUNCTIONS
########################################################
# Command implementations


@new_group.command("python")
@click.argument("project_name", required=False)
@click.option(
    "--current-dir",
    is_flag=True,
    help="Configure current directory instead of creating new one",
)
def new_python(project_name, current_dir):
    """🐍 Create a new Python project with full development environment."""

    # 0. Prompt for project name if not provided and not current-dir
    if not project_name and not current_dir:
        project_name = print_prompt("Nom du projet Python", required=True)
        if not project_name:
            print_new_project_error("python", "unknown", "Nom de projet requis")
            sys.exit(1)

    # 1. Security validation for project name
    if project_name:
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
    python_result = runtime_manager.check_runtime("python")
    print_dependency_check_result(python_result)

    # 3. Install dependencies if needed
    if not python_result.success:
        print_new_project_progress(
            "Dependency installation", "Installing missing dependencies"
        )
        install_result = runtime_manager.install_runtime("python")
        print_installation_result(install_result)

        if not install_result.success:
            print_new_project_error(
                "python", project_name or "unknown", "Dependency installation failed"
            )
            sys.exit(1)

    # 4. Security validation for script execution
    script_path = resolve_script_path("languages/python/scripts/setup_project.py")

    print_new_project_progress("Script validation", "Validating setup script")
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
    result = run_secure_command(cmd, "Setting up Python project")

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
    """🟨 Create a new JavaScript/Node.js project with development tools."""

    # 0. Prompt for project name if not provided and not current-dir
    if not project_name and not current_dir:
        project_name = print_prompt("Nom du projet JavaScript", required=True)
        if not project_name:
            print_new_project_error("javascript", "unknown", "Nom de projet requis")
            sys.exit(1)

    # 1. Security validation for project name
    if project_name:
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
    node_result = runtime_manager.check_runtime("node")
    print_dependency_check_result(node_result)

    # 3. Install dependencies if needed
    if not node_result.success:
        print_new_project_progress(
            "Dependency installation", "Installing missing dependencies"
        )
        install_result = runtime_manager.install_runtime("node")
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

    print_new_project_progress("Script validation", "Validating setup script")
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
    result = run_secure_command(cmd, f"Setting up {project_type} project")

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
    """🔍 Auto-detect project type and create appropriate setup."""

    print_new_project_progress("Project detection", "Detecting project type")

    # Utiliser le détecteur interne au lieu d'un script externe inexistant
    from ..core.project.project_detector import (
        ProjectDetector,
        launch_project_setup,
    )

    detector = ProjectDetector(Path.cwd())
    detected_type, confidence = detector.detect_project_type()

    if detected_type == "generic" or confidence == 0:
        print_new_project_error(
            "auto-detected",
            project_name or "unknown",
            "No suitable project type detected",
        )
        sys.exit(1)

    # Lancer la configuration directement
    rc = launch_project_setup(
        project_type=detected_type,
        project_name=project_name,
        current_dir=current_dir,
    )

    if rc == 0:
        project_path = Path.cwd() / (project_name or Path.cwd().name)
        print_new_project_complete(
            detected_type.title(), project_name or "current", str(project_path)
        )
    else:
        print_new_project_error(
            detected_type, project_name or "unknown", "Detection/setup failed"
        )
        sys.exit(1)
