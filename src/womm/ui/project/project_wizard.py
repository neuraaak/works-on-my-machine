#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT WIZARD - Interactive Project Setup Wizard
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Interactive wizard for configuring existing projects.

This module provides an interactive step-by-step wizard for the ``womm
setup`` command, letting users pick which development tools to configure
in an already-existing project directory.

Project *creation* (language/variant/file-structure selection) is handled
entirely by Copier templates (see ``womm create``/``womm template``); this
wizard no longer has a scaffolding role.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path

try:
    from InquirerPy import inquirer

    INQUIRERPY_AVAILABLE = True
except ImportError:
    INQUIRERPY_AVAILABLE = False

# Local imports
from ..common.ezpl_bridge import ezprinter

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class ProjectWizard:
    """Interactive wizard for configuring existing projects."""

    @staticmethod
    def run_interactive_setup_for_existing_project(
        project_type: str, project_path: Path
    ) -> dict[str, str | bool | int | dict[str, str | bool]] | None:
        """
        Run interactive setup wizard for an existing project.

        Args:
            project_type: Type of the existing project
            project_path: Path to the existing project

        Returns:
            Setup configuration dictionary or None if cancelled
        """
        ezprinter.info(f"🔧 Interactive Setup for {project_type.title()} Project")
        ezprinter.info("=" * 40)
        ezprinter.info(f"Project path: {project_path.absolute()}")

        # Configure setup options
        setup_options = ProjectWizard._configure_setup_options(project_type)

        # Confirm setup
        if not ProjectWizard._confirm_setup(project_type, project_path, setup_options):
            return None

        # Return setup configuration
        return {
            "project_type": project_type,
            "project_path": str(project_path),
            "options": setup_options,
        }

    @staticmethod
    def _configure_setup_options(
        _project_type: str,
    ) -> dict[str, str | bool]:
        """Configure setup-specific options for an existing project."""
        options = {}

        if INQUIRERPY_AVAILABLE:
            # Common setup options
            options["virtual_env"] = inquirer.confirm(
                message="Create virtual environment?",
                default=False,
            ).execute()

            options["install_deps"] = inquirer.confirm(
                message="Install dependencies?",
                default=True,
            ).execute()

            options["setup_dev_tools"] = inquirer.confirm(
                message="Setup development tools (linting, formatting, etc.)?",
                default=True,
            ).execute()

            options["setup_git_hooks"] = inquirer.confirm(
                message="Setup Git hooks?",
                default=True,
            ).execute()

        else:
            # Fallback to simple input
            virtual_env = input("Create virtual environment? (y/N): ").strip().lower()
            options["virtual_env"] = virtual_env in ["y", "yes"]

            install_deps = input("Install dependencies? (Y/n): ").strip().lower()
            options["install_deps"] = install_deps in ["", "y", "yes"]

            setup_dev_tools = input("Setup development tools? (Y/n): ").strip().lower()
            options["setup_dev_tools"] = setup_dev_tools in ["", "y", "yes"]

            setup_git_hooks = input("Setup Git hooks? (Y/n): ").strip().lower()
            options["setup_git_hooks"] = setup_git_hooks in ["", "y", "yes"]

        return options

    @staticmethod
    def _confirm_setup(
        project_type: str, project_path: Path, options: dict[str, str | bool]
    ) -> bool:
        """Confirm setup configuration with a Rich panel."""
        from rich.console import Console
        from rich.table import Table

        console = Console()

        # Create a table for the setup configuration summary
        table = Table(
            title="🔧 Setup Configuration Summary",
            show_header=True,
            header_style="bold blue",
        )
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")

        table.add_row("Project type", project_type.title())
        table.add_row("Project path", str(project_path.absolute()))
        table.add_row(
            "Virtual environment", "Yes" if options.get("virtual_env") else "No"
        )
        table.add_row(
            "Install dependencies", "Yes" if options.get("install_deps") else "No"
        )
        table.add_row(
            "Setup dev tools", "Yes" if options.get("setup_dev_tools") else "No"
        )
        table.add_row(
            "Setup Git hooks", "Yes" if options.get("setup_git_hooks") else "No"
        )

        console.print("")
        console.print(table)
        console.print("")

        if INQUIRERPY_AVAILABLE:
            return inquirer.confirm(
                message="Proceed with setup?",
                default=True,
            ).execute()
        else:
            confirm = input("Proceed with setup? (Y/n): ").strip().lower()
            return confirm in ["", "y", "yes"]


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["ProjectWizard"]
