#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT WIZARD - Interactive Project Creation Wizard
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Interactive wizard for project creation.

This module provides an interactive step-by-step wizard for creating
new projects, making it easy for users to set up their projects
without needing to know all the technical details.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path

try:
    from InquirerPy import inquirer
    from InquirerPy.base.control import Choice
    from InquirerPy.validator import PathValidator

    INQUIRERPY_AVAILABLE = True
except ImportError:
    INQUIRERPY_AVAILABLE = False


from ...shared.configs.project import ProjectVariantConfig
from ...utils.project import check_project_name, suggest_project_name
from ..common.ezpl_bridge import ezconsole, ezprinter
from ..common.interactive_menu import InteractiveMenu


class ProjectWizard:
    """Interactive wizard for project creation."""

    @staticmethod
    def run_interactive_setup() -> dict[str, str | bool | int] | None:
        """
        Run the complete interactive project creation wizard.

        Returns:
            Project configuration dictionary or None if cancelled
        """
        ezprinter.info("🎯 Interactive Project Creation Wizard")
        ezprinter.info("=" * 50)

        # Step 1: Select project type
        ezconsole.print("", style="dim")
        ezconsole.print("📁 Step 1: Select project type", style="bold blue")
        project_type = ProjectWizard._select_project_type()
        if not project_type:
            return None

        # Step 2: Enter project name
        ezconsole.print("\n" + (":" * 80) + "\n", style="dim")
        ezconsole.print("🏷️  Step 2: Enter project name", style="bold blue")
        project_name = ProjectWizard._get_project_name()
        if not project_name:
            return None

        # Step 3: Select project location
        ezconsole.print("\n" + (":" * 80) + "\n", style="dim")
        ezconsole.print("📂 Step 3: Select project location", style="bold blue")
        project_path = ProjectWizard._select_project_location(project_name)
        if not project_path:
            return None

        # Step 4: Configure project options
        ezconsole.print("\n" + (":" * 80) + "\n", style="dim")
        ezconsole.print("⚙️  Step 4: Configure project options", style="bold blue")
        project_options = ProjectWizard._configure_project_options(project_type)

        # Step 5: Confirm and create
        ezconsole.print("\n" + (":" * 80) + "\n", style="dim")
        ezconsole.print("✅ Step 5: Confirm project creation", style="bold blue")
        if not ProjectWizard._confirm_project_creation(
            project_name, project_path, project_type, project_options
        ):
            return None

        # Return complete configuration
        return {
            "project_type": project_type,
            "project_name": project_name,
            "project_path": project_path,
            "current_dir": False,
            **project_options,
        }

    @staticmethod
    def run_interactive_setup_for_existing_project(
        project_type: str, project_path: Path
    ) -> dict[str, str | bool | int] | None:
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
            "project_path": project_path,
            "options": setup_options,
        }

    @staticmethod
    def _select_project_type() -> str | None:
        """Interactive project type selection."""
        # Get project types directly from config (no need for interface)
        project_types = ProjectVariantConfig.get_project_types_for_ui()

        if INQUIRERPY_AVAILABLE:
            choices = [Choice(value=ptype, name=desc) for ptype, desc in project_types]
            selected = inquirer.select(
                message="Select project type:",
                choices=choices,
                pointer="→",
            ).execute()
            return selected
        else:
            # Fallback to simple menu
            menu = InteractiveMenu("Select project type:")
            items = [
                {"type": ptype, "description": desc} for ptype, desc in project_types
            ]
            selected = menu.select_from_list(
                items, display_func=lambda x: x["description"]
            )
            return selected["type"] if selected else None

    @staticmethod
    def _get_project_name() -> str | None:
        """Get project name with validation."""
        if INQUIRERPY_AVAILABLE:
            while True:
                name = inquirer.text(
                    message="Enter project name:",
                    validate=lambda x: ProjectWizard._validate_project_name(x),
                ).execute()

                if name:
                    # Suggest valid name if needed
                    suggested = suggest_project_name(name)
                    if suggested != name:
                        use_suggested = inquirer.confirm(
                            message=f"Use suggested name '{suggested}' instead?",
                            default=True,
                        ).execute()
                        if use_suggested:
                            return suggested
                    return name
                return None
        else:
            # Fallback to simple input
            while True:
                name = input("Enter project name: ").strip()
                if not name:
                    return None

                is_valid, error = check_project_name(name)
                if is_valid:
                    return name
                else:
                    ezprinter.error(f"Invalid project name: {error}")
                    suggested = suggest_project_name(name)
                    ezprinter.info(f"Suggested name: {suggested}")

    @staticmethod
    def _validate_project_name(name: str) -> bool:
        """Validate project name for InquirerPy."""
        is_valid, _ = check_project_name(name)
        return is_valid

    @staticmethod
    def _select_project_location(project_name: str) -> Path | None:
        """Select project location."""
        current_dir = Path.cwd()

        # Options for project location
        location_options = [
            ("current", f"📁 Current directory ({current_dir})"),
            ("subdir", f"📂 Create subdirectory '{project_name}' in current directory"),
            ("custom", "🔍 Choose custom location"),
        ]

        if INQUIRERPY_AVAILABLE:
            choices = [Choice(value=opt, name=desc) for opt, desc in location_options]
            location_type = inquirer.select(
                message="Select project location:",
                choices=choices,
                pointer="→",
            ).execute()

            if location_type == "current":
                return current_dir
            elif location_type == "subdir":
                return current_dir / project_name
            elif location_type == "custom":
                return ProjectWizard._select_custom_location(project_name)
        else:
            # Fallback to simple menu
            menu = InteractiveMenu("Select project location:")
            items = [
                {"type": opt, "description": desc} for opt, desc in location_options
            ]
            selected = menu.select_from_list(
                items, display_func=lambda x: x["description"]
            )

            if selected:
                if selected["type"] == "current":
                    return current_dir
                elif selected["type"] == "subdir":
                    return current_dir / project_name
                elif selected["type"] == "custom":
                    return ProjectWizard._select_custom_location(project_name)

        return None

    @staticmethod
    def _select_custom_location(project_name: str) -> Path | None:
        """Select custom project location."""
        if INQUIRERPY_AVAILABLE:
            # Use InquirerPy file browser for directory selection
            class DirectoryValidator(PathValidator):
                def validate(self, document):
                    result = super().validate(document)
                    if result:
                        path = Path(document.text)
                        if not path.exists():
                            return True  # Allow non-existent directories
                        return path.is_dir()
                    return False

            custom_path = inquirer.filepath(
                message="Select project directory:",
                validate=DirectoryValidator(),
            ).execute()

            if custom_path:
                return Path(custom_path) / project_name
        else:
            # Fallback to simple input
            while True:
                custom_path = input("Enter project directory path: ").strip()
                if not custom_path:
                    return None

                try:
                    path = Path(custom_path)
                    if not path.exists():
                        # Create directory
                        path.mkdir(parents=True, exist_ok=True)
                    elif not path.is_dir():
                        ezprinter.error("Path exists but is not a directory")
                        continue

                    return path / project_name
                except Exception as e:
                    ezprinter.error(f"Invalid path: {e}")

        return None

    @staticmethod
    def _configure_project_options(project_type: str) -> dict[str, str | bool]:
        """Configure project-specific options."""
        options = {}

        # Common options
        if INQUIRERPY_AVAILABLE:
            options["author_name"] = (
                inquirer.text(
                    message="Author name:",
                    default="Your Name",
                ).execute()
                or "Your Name"
            )

            options["author_email"] = (
                inquirer.text(
                    message="Author email:",
                    default="your.email@example.com",
                ).execute()
                or "your.email@example.com"
            )

            options["project_description"] = (
                inquirer.text(
                    message="Project description:",
                    default=f"A {project_type} project created with WOMM CLI",
                ).execute()
                or f"A {project_type} project created with WOMM CLI"
            )

            # Project-specific options
            if project_type in ["react", "vue"]:
                options["project_type"] = project_type
                options["use_typescript"] = inquirer.confirm(
                    message="Use TypeScript?",
                    default=True,
                ).execute()

            if project_type == "javascript":
                # Get JavaScript project type choices from ProjectVariantConfig
                js_type_choices = (
                    ProjectVariantConfig.get_javascript_project_type_choices_for_ui()
                )
                choices = [
                    Choice(value=ptype, name=desc) for ptype, desc in js_type_choices
                ]
                options["project_type"] = inquirer.select(
                    message="JavaScript project type:",
                    choices=choices,
                    pointer="→",
                ).execute()

        else:
            # Fallback to simple input
            options["author_name"] = (
                input("Author name [Your Name]: ").strip() or "Your Name"
            )
            options["author_email"] = (
                input("Author email [your.email@example.com]: ").strip()
                or "your.email@example.com"
            )
            options["project_description"] = (
                input("Project description: ").strip()
                or f"A {project_type} project created with WOMM CLI"
            )

            if project_type in ["react", "vue"]:
                options["project_type"] = project_type
                use_ts = input("Use TypeScript? (y/N): ").strip().lower()
                options["use_typescript"] = use_ts in ["y", "yes"]

            if project_type == "javascript":
                # Get JavaScript project type choices from ProjectVariantConfig
                js_type_choices = (
                    ProjectVariantConfig.get_javascript_project_type_choices_for_ui()
                )
                ezprinter.info("JavaScript project types:")
                for idx, (_ptype, desc) in enumerate(js_type_choices, start=1):
                    ezprinter.info(f"{idx}. {desc}")
                choice = (
                    input(f"Select type (1-{len(js_type_choices)}) [1]: ").strip()
                    or "1"
                )
                if choice.isdigit() and 1 <= int(choice) <= len(js_type_choices):
                    options["project_type"] = js_type_choices[int(choice) - 1][0]
                else:
                    options["project_type"] = js_type_choices[0][0]  # Default to first

        return options

    @staticmethod
    def _confirm_project_creation(
        project_name: str,
        project_path: Path,
        project_type: str,
        options: dict[str, str | bool],
    ) -> bool:
        """Confirm project creation with a Rich panel."""
        from rich.console import Console
        from rich.table import Table

        console = Console()

        # Create a table for the configuration summary
        table = Table(
            title="📋 Project Configuration Summary",
            show_header=True,
            header_style="bold blue",
        )
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")

        table.add_row("Project name", project_name)
        table.add_row("Project type", project_type)
        table.add_row("Location", str(project_path))
        table.add_row("Author", options.get("author_name", "Your Name"))
        table.add_row(
            "Description", options.get("project_description", "No description")
        )

        console.print("")
        console.print(table)
        console.print("")

        if INQUIRERPY_AVAILABLE:
            return inquirer.confirm(
                message="Create project with these settings?",
                default=True,
            ).execute()
        else:
            confirm = input("Create project? (Y/n): ").strip().lower()
            return confirm in ["", "y", "yes"]

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
