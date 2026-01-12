#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM DISPLAY - System UI Display Functions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
System display functions for Works On My Machine.

Provides display functions for system detection results and information.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Third-party imports
from rich.table import Table

# Local imports
from ..common import ezconsole, ezpl_bridge, ezprinter

# ///////////////////////////////////////////////////////////////
# DISPLAY FUNCTIONS
# ///////////////////////////////////////////////////////////////


def display_system_managers_list(status: dict, verbose: bool = False) -> None:
    """
    Display all system package managers and their status in a table.

    Args:
        status: Dictionary of manager status information from get_installation_status()
        verbose: Whether to show additional details (priority column)
    """
    table = Table(title="System Package Managers", show_header=True)
    table.add_column("Manager", style="cyan", no_wrap=True)
    table.add_column("Available", style="green", justify="center")
    table.add_column("Version", style="yellow")
    table.add_column("Platform", style="blue")

    if verbose:
        table.add_column("Priority", style="magenta", justify="center")

    for name, info in status.items():
        if info["supported_on_current_platform"]:
            row = [
                name,
                "✓" if info["available"] else "✗",
                info["version"] or "N/A",
                info["platform"],
            ]

            if verbose:
                row.append(str(info.get("priority", "N/A")))

            table.add_row(*row)

    ezconsole.print(table)


def display_available_managers(results: dict, verbose: bool = False) -> None:
    """
    Display available package managers from detection results.

    Args:
        results: Dictionary of package manager results from detect_available_managers()
        verbose: Whether to show detailed information about each manager
    """
    available = [name for name, res in results.items() if res.success]

    if available:
        ezprinter.tip(f"Available managers: {', '.join(available)}")

        if verbose:
            ezprinter.info("\nDetails:")
            for name in available:
                res = results[name]
                ezprinter.info(f"  • {name}: v{res.version} (priority: {res.priority})")
    else:
        ezprinter.warning("No system package managers detected")


def display_best_manager(
    best: object,
    interface: object,
    verbose: bool = False,
) -> None:
    """
    Display the best available package manager.

    Args:
        best: BestManagerInfo object or None from get_best_available_manager()
        interface: SystemPackageManagerInterface instance for config access
        verbose: Whether to show additional information about selection criteria
    """
    if best:
        msg = f"✨ Best manager: {best.manager_name}"
        if best.version:
            msg += f" (version {best.version})"
        ezprinter.tip(msg)

        if verbose:
            config = interface.package_manager_service.get_manager_config(
                best.manager_name
            )
            if config:
                ezprinter.info(f"Platform: {config.get('platform', 'N/A')}")
                ezprinter.info(f"Priority: {config.get('priority', 'N/A')}")
            ezprinter.info(
                "\nThis manager was selected based on:"
                "\n  • Platform compatibility"
                "\n  • Availability on system"
                "\n  • Priority ranking"
            )
    else:
        ezprinter.error("No system package manager available")

        if verbose:
            ezprinter.info(
                "\nTip: Install a package manager for your platform:"
                "\n  • Windows: winget, chocolatey, scoop"
                "\n  • macOS: homebrew"
                "\n  • Linux: apt, dnf, pacman (usually pre-installed)"
            )


def display_system_detection_results(data: dict) -> None:
    """
    Display system detection results in a Rich panel.

    Args:
        data: System data to display with the following structure:
            - system_info: Dict with platform, architecture, python_version, shell
            - package_managers: Dict of available package managers
            - dev_environments: Dict of detected development environments
            - recommendations: Dict of recommendations by category

    Raises:
        ValueError: If data format is invalid
    """
    # Validate data structure
    if not isinstance(data, dict):
        raise TypeError(
            f"Invalid data format: expected dictionary, got {type(data).__name__}"
        )

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
    panel = ezprinter.create_panel(
        "\n".join(content),
        title="System Detection Results",
        border_style="dim white",
    )
    ezpl_bridge.console.print(panel)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "display_available_managers",
    "display_best_manager",
    "display_system_detection_results",
    "display_system_managers_list",
]
