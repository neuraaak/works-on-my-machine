#!/usr/bin/env python3
"""
System commands for WOMM CLI.
Handles system detection and prerequisites installation.
"""

# IMPORTS
########################################################
# Standard library imports
import sys
from typing import Dict

# Third-party imports
import click

# Local imports
# (None for this file)


# MAIN FUNCTIONS
########################################################
# Core CLI functionality and command groups


@click.group()
def system_group():
    """🔧 System detection and prerequisites."""


# UTILITY FUNCTIONS
########################################################
# Helper functions and utilities


def display_system_data(data: Dict) -> None:
    """Display system data in a Rich panel."""
    try:
        from shared.ui.console import console
        from shared.ui.panels import create_panel

        # Validate data structure
        if not isinstance(data, dict):
            raise ValueError("Invalid data format: expected dictionary")

        system_info = data.get("system_info", {})
        package_managers = data.get("package_managers", {})
        dev_environments = data.get("dev_environments", {})
        recommendations = data.get("recommendations", {})

        # Format the data nicely
        content = []
        content.append("[bold blue]System Information[/bold blue]")
        content.append(
            f"OS: {system_info.get('platform', 'unknown')} {system_info.get('platform_release', '')}"
        )
        content.append(f"Architecture: {system_info.get('architecture', 'unknown')}")
        content.append(f"Python: {system_info.get('python_version', 'unknown')}")
        content.append(f"Shell: {system_info.get('shell', 'unknown')}")

        content.append(
            f"\n[bold green]Package Managers[/bold green] ({len(package_managers)} available)"
        )
        for name, info in package_managers.items():
            if info.get("available"):
                content.append(
                    f"✓ {name}: {info.get('version', 'unknown')} - {info.get('description', '')}"
                )

        content.append(
            f"\n[bold yellow]Development Environments[/bold yellow] ({len(dev_environments)} detected)"
        )
        for _, info in dev_environments.items():
            if info.get("available"):
                content.append(
                    f"✓ {info.get('name', 'unknown')}: {info.get('version', 'unknown')}"
                )

        content.append("\n[bold magenta]Recommendations[/bold magenta]")
        for category, recommendation in recommendations.items():
            content.append(f"- {category}: {recommendation}")

        # Add a blank line before the panel for better spacing
        console.print()
        panel = create_panel(
            "\n".join(content),
            title="System Detection Results",
            style="white",
            border_style="dim white",
        )
        console.print(panel)

    except ImportError:
        # Fallback to basic output
        print("\n=== System Detection Results ===")
        print(
            f"OS: {data['system_info']['platform']} {data['system_info']['platform_release']}"
        )
        print(f"Architecture: {data['system_info']['architecture']}")
        print(f"Python: {data['system_info']['python_version']}")
        print(f"Shell: {data['system_info']['shell']}")


# COMMAND FUNCTIONS
########################################################
# Command implementations


@system_group.command("detect")
def system_detect():
    """🔍 Detect system information and available tools."""
    try:
        from shared.core.system_detector import SystemDetector
        from shared.ui.console import print_header
        from shared.ui.progress import create_spinner_with_status

        print_header("WOMM System Detection")

        with create_spinner_with_status("Detecting system information...") as (
            progress,
            task,
        ):
            # Update description and status
            progress.update(
                task,
                description="🔍 Detecting system information...",
                status="Initializing...",
            )

            detector = SystemDetector()

            # Update status during detection
            progress.update(task, status="Scanning system...")
            data = detector.get_system_data()

            # Final status update
            progress.update(task, status="Detection complete!")

        if data:
            display_system_data(data)
        else:
            print("❌ Failed to detect system information")
            sys.exit(1)

    except ImportError:
        print("❌ System detection module not available")
        sys.exit(1)


@system_group.command("install")
@click.option("--check", is_flag=True, help="Only check prerequisites")
@click.argument("tools", nargs=-1, type=click.Choice(["python", "node", "git", "all"]))
def system_install(check, tools):
    """📦 Install system prerequisites."""
    try:
        from rich.table import Table

        from shared.core.dependencies.runtime_manager import runtime_manager
        from shared.ui.console import console, print_header
        from shared.ui.progress import (
            create_step_progress,
        )

        print_header("WOMM System Prerequisites")

        # Determine which tools to process
        tools_to_process = (
            ["python", "node", "git"] if not tools or "all" in tools else list(tools)
        )

        if check:
            # Check target directory existence
            with create_step_progress(
                tools_to_process, "Checking system prerequisites..."
            ) as (
                progress,
                task,
                steps,
            ):
                # Only check prerequisites
                results = {}
                for i, step in enumerate(tools_to_process):
                    progress.update(
                        task,
                        description=f"[bold blue]{step}",
                        current_step=step,
                        step=i + 1,
                    )
                    result = runtime_manager.check_runtime(step)
                    results[step] = result

                    # Advance progress bar
                    progress.advance(task)

            # Display results in a table
            table = Table(title="Prerequisites Status")
            table.add_column("Tool", style="cyan", no_wrap=True)
            table.add_column("Status", style="bold")
            table.add_column("Version", style="dim")
            table.add_column("Path", style="dim")

            for tool, result in results.items():
                status = "✅ Installed" if result.success else "❌ Missing"
                version = result.version or "N/A"
                path = result.path or "N/A"
                table.add_row(tool.capitalize(), status, version, path)

            console.print("")
            console.print(table)

            # Check if any tools are missing
            missing_tools = [
                tool for tool, result in results.items() if not result.success
            ]
            if missing_tools:
                console.print(f"\n⚠️  Missing tools: {', '.join(missing_tools)}")
                console.print("💡 Run without --check flag to install them.")
                sys.exit(1)
            else:
                console.print("\n✅ All prerequisites are installed!")

        else:
            # Install prerequisites
            console.print("📦 Installing system prerequisites...\n")
            results = runtime_manager.check_and_install_runtimes(tools_to_process)

            # Display results
            table = Table(title="Installation Results")
            table.add_column("Tool", style="cyan", no_wrap=True)
            table.add_column("Status", style="bold")
            table.add_column("Version", style="dim")
            table.add_column("Message", style="dim")

            failed_installations = []
            for tool, result in results.items():
                if result.success:
                    status = "✅ Success"
                    version = result.version or "N/A"
                else:
                    status = "❌ Failed"
                    version = "N/A"
                    failed_installations.append(tool)

                message = result.message or result.error or "N/A"
                table.add_row(tool.capitalize(), status, version, message)

            console.print(table)

            if failed_installations:
                console.print(
                    f"\n❌ Failed to install: {', '.join(failed_installations)}"
                )
                sys.exit(1)
            else:
                console.print("\n🎉 All prerequisites installed successfully!")

    except ImportError as e:
        print(f"❌ Dependency manager not available: {e}")
        sys.exit(1)
