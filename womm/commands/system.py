#!/usr/bin/env python3
"""
System commands for WOMM CLI.
Handles system detection and prerequisites installation.
"""

import sys
from typing import Dict

import click


@click.group()
def system_group():
    """🔧 System detection and prerequisites."""


def display_system_data(data: Dict) -> None:
    """Display system data in a Rich panel."""
    try:
        from shared.ui import console, create_panel

        # Validate data structure
        if not isinstance(data, dict):
            raise ValueError("Invalid data format: expected dictionary")

        system_info = data.get('system_info', {})
        package_managers = data.get('package_managers', {})
        dev_environments = data.get('dev_environments', {})
        recommendations = data.get('recommendations', {})

        # Format the data nicely
        content = []
        content.append("[bold blue]System Information[/bold blue]")
        content.append(f"OS: {system_info.get('platform', 'unknown')} {system_info.get('platform_release', '')}")
        content.append(f"Architecture: {system_info.get('architecture', 'unknown')}")
        content.append(f"Python: {system_info.get('python_version', 'unknown')}")
        content.append(f"Shell: {system_info.get('shell', 'unknown')}")

        content.append(f"\n[bold green]Package Managers[/bold green] ({len(package_managers)} available)")
        for name, info in package_managers.items():
            if info.get('available'):
                content.append(f"✓ {name}: {info.get('version', 'unknown')} - {info.get('description', '')}")

        content.append(f"\n[bold yellow]Development Environments[/bold yellow] ({len(dev_environments)} detected)")
        for _, info in dev_environments.items():
            if info.get('available'):
                content.append(f"✓ {info.get('name', 'unknown')}: {info.get('version', 'unknown')}")

        content.append("\n[bold magenta]Recommendations[/bold magenta]")
        for category, recommendation in recommendations.items():
            content.append(f"• {category}: {recommendation}")

        # Add a blank line before the panel for better spacing
        console.print()
        panel = create_panel("\n".join(content), title="System Detection Results", style="blue")
        console.print(panel)

    except ImportError:
        # Fallback to basic output
        print("\n=== System Detection Results ===")
        print(f"OS: {data['system_info']['platform']} {data['system_info']['platform_release']}")
        print(f"Architecture: {data['system_info']['architecture']}")
        print(f"Python: {data['system_info']['python_version']}")
        print(f"Shell: {data['system_info']['shell']}")

        # Display package managers
        if data.get('package_managers'):
            print(f"\nPackage Managers ({len(data['package_managers'])} available):")
            for name, info in data['package_managers'].items():
                if info.get('available'):
                    print(f"✓ {name}: {info.get('version', 'unknown')} - {info.get('description', '')}")

        # Display development environments
        if data.get('dev_environments'):
            print(f"\nDevelopment Environments ({len(data['dev_environments'])} detected):")
            for _, info in data['dev_environments'].items():
                if info.get('available'):
                    print(f"✓ {info.get('name', 'unknown')}: {info.get('version', 'unknown')}")

        # Display recommendations
        if data.get('recommendations'):
            print("\nRecommendations:")
            for category, recommendation in data['recommendations'].items():
                print(f"• {category}: {recommendation}")


def display_prerequisites_data(results: Dict) -> None:
    """Display prerequisites data in a Rich panel."""
    try:
        from shared.ui import console, create_panel

        # Validate data structure
        if not isinstance(results, dict):
            raise ValueError("Invalid data format: expected dictionary")

        # Format the data nicely
        content = []
        content.append("[bold blue]Prerequisites[/bold blue]")

        for tool, info in results.items():
            status_icon = "✅" if info.get("available", False) else "❌"
            status_text = info.get("status", "unknown")
            version = info.get("version", "unknown")

            if info.get("available", False):
                content.append(f"{status_icon} {tool}: {status_text} (v{version})")
            else:
                error = info.get("error", "Not installed")
                content.append(f"{status_icon} {tool}: {status_text} - {error}")

        # Add summary
        content.append("\n[bold green]Summary[/bold green]")
        available_count = sum(1 for info in results.values() if info.get("available", False))
        total_count = len(results)

        if available_count == total_count:
            content.append("• All prerequisites are available")
            content.append("• No installation required")
        else:
            missing_count = total_count - available_count
            content.append(f"• {available_count}/{total_count} prerequisites available")
            content.append(f"• {missing_count} prerequisites need installation")

        # Add a blank line before the panel for better spacing
        console.print()
        panel = create_panel("\n".join(content), title="Prerequisites Status", style="green")
        console.print(panel)

    except ImportError:
        # Fallback to basic output
        print("\n=== Prerequisites Status ===")
        for tool, info in results.items():
            status_icon = "✅" if info.get("available", False) else "❌"
            status_text = info.get("status", "unknown")
            version = info.get("version", "unknown")

            if info.get("available", False):
                print(f"{status_icon} {tool}: {status_text} (v{version})")
            else:
                error = info.get("error", "Not installed")
                print(f"{status_icon} {tool}: {status_text} - {error}")


@system_group.command("detect")
def system_detect():
    """Detect system information and available tools."""
    try:
        from shared.core.system_detector import SystemDetector
        from shared.ui import create_progress, print_header

        print_header("System Detection")

        with create_progress("Analyzing system...") as (progress, task):
            try:
                # Use SystemDetector directly instead of executing external script
                detector = SystemDetector()
                data = detector.get_system_data()

                progress.update(task, description="System detection completed")

                # Display the results
                display_system_data(data)

            except Exception as e:
                progress.update(task, description="System detection failed")
                print(f"❌ Error during system detection: {e}")
                sys.exit(1)

        sys.exit(0)

    except ImportError as e:
        print(f"❌ Error: SystemDetector module not available: {e}")
        print("💡 This is a development version. Please ensure all modules are properly installed.")
        sys.exit(1)


@system_group.command("install")
@click.option("--check", is_flag=True, help="Only check prerequisites")
@click.option("--interactive", is_flag=True, help="Interactive installation mode")
@click.argument(
    "tools", nargs=-1, type=click.Choice(["python", "node", "git", "npm", "all"])
)
def system_install(check, interactive, tools):
    """Install system prerequisites."""
    try:
        from shared.core.prerequisite_manager import PrerequisiteManager
        from shared.ui import create_progress, print_header

        print_header("System Prerequisites Installation")

        # Determine tools to process
        if "all" in tools:
            tools_to_process = ["python", "node", "git", "npm"]
        else:
            tools_to_process = list(tools) if tools else ["python", "node", "git"]

        # Set progress message based on mode
        progress_message = "Checking prerequisites..." if check else "Processing prerequisites..."

        with create_progress(progress_message) as (progress, task):
            # Use PrerequisiteManager directly
            manager = PrerequisiteManager()

            if check:
                # Only check, don't install
                results = manager.check_prerequisites(tools_to_process)
                progress.update(task, description="Prerequisites check completed")
            else:
                # Install missing tools
                results = manager.get_installation_status(tools_to_process)
                progress.update(task, description="Prerequisites installation completed")

            # Display the results
            display_prerequisites_data(results)

        # Determine exit code
        all_available = all(info.get("available", False) for info in results.values())
        sys.exit(0 if all_available else 1)

    except ImportError as e:
        print(f"❌ Error: PrerequisiteManager module not available: {e}")
        print("💡 This is a development version. Please ensure all modules are properly installed.")
        sys.exit(1)
