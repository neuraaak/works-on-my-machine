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
from ...shared.results import (
    DependencyCheckResult,
    DependencyInventoryResult,
    DependencyStatusResult,
    EnvironmentRefreshResult,
    SystemDetectionResult,
)
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
    manager_name: str | None,
    version: str | None = None,
    platform: str | None = None,
    priority: int | None = None,
    verbose: bool = False,
) -> None:
    """
    Display the best available package manager.

    Args:
        manager_name: Name of the best manager or None if not available
        version: Manager version if available
        platform: Platform the manager runs on
        priority: Priority ranking of the manager
        verbose: Whether to show additional information about selection criteria
    """
    if manager_name:
        msg = f"✨ Best manager: {manager_name}"
        if version:
            msg += f" (version {version})"
        ezprinter.tip(msg)

        if verbose:
            if platform:
                ezprinter.info(f"Platform: {platform}")
            if priority is not None:
                ezprinter.info(f"Priority: {priority}")
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


def render_system_detection_result(result: SystemDetectionResult) -> None:
    """
    Render a system detection Result: the detail panel on success, an error
    message on failure.

    Args:
        result: Outcome returned by ``SystemDetectorInterface.detect_system()``.
    """
    if result.success:
        print()
        display_system_detection_results(result.system_data or {})
        return

    ezprinter.error(result.message or "System detection failed")
    if result.error:
        ezprinter.info(result.error)


def render_environment_refresh_result(
    result: EnvironmentRefreshResult, accessible: bool
) -> None:
    """
    Render an environment refresh Result together with the accessibility check.

    Args:
        result: Outcome returned by ``SystemEnvironmentInterface.refresh_environment()``.
        accessible: Whether the target command is reachable after the refresh
            (from ``verify_environment_refresh()``).
    """
    if result.success:
        if accessible:
            print()
            ezprinter.tip(
                "Recent PATH additions should now be accessible in this terminal session"
            )
        else:
            ezprinter.warning(
                "Environment refreshed but changes may not be accessible in current session"
            )
            ezprinter.tip(
                "Solution: Restart your terminal or open a new command prompt"
            )
        return

    ezprinter.error(result.message or "Environment refresh failed")
    if result.error:
        ezprinter.info(result.error)
    ezprinter.info("This means WOMM may not be accessible in the current session")
    ezprinter.info("Solution: Restart your terminal or run 'refreshenv' manually")


def display_deps_check_results(
    result: DependencyCheckResult,
    verbose: bool = False,
) -> None:
    """
    Display dependency check results (all strata).

    Args:
        result: Probe results collected by ``DepsInterface.check_all()``
        verbose: Whether to show additional details
    """
    ezprinter.info("Checking all dependencies...\n")

    # Strata 1
    ezprinter.info("\n=== System Package Managers (Strata 1) ===")
    available = [entry for entry in result.system if entry.available]
    if available:
        ezprinter.success(f"Available: {', '.join(e.name for e in available)}")
        if verbose:
            for entry in available:
                ezprinter.info(f"  • {entry.name}: v{entry.version}")
    else:
        ezprinter.warning("No system package managers available")
    ezconsole.print("")

    # Strata 2
    ezprinter.info("\n=== Runtimes (Strata 2) ===")
    for entry in result.runtime:
        status = "✓" if entry.available else "✗"
        version = f"v{entry.version}" if entry.version else "N/A"
        msg = f"{status} {entry.name}: {version}"
        if entry.available:
            ezprinter.success(msg)
        else:
            ezprinter.warning(msg)
    ezconsole.print("")

    # Strata 3
    ezprinter.info("\n=== Development Tools (Strata 3) ===")
    for entry in result.tools:
        status = "✓" if entry.available else "✗"
        prefix = "  " if verbose else ""
        msg = f"{prefix}{status} {entry.name}"
        if entry.available:
            ezprinter.success(msg)
        else:
            ezprinter.warning(msg)


def display_deps_status_table(
    result: DependencyStatusResult,
    verbose: bool = False,
) -> None:
    """
    Display comprehensive dependency status in a table.

    Args:
        result: Status data collected by ``DepsInterface.show_status()``
        verbose: Whether to show additional details column
    """
    table = Table(title="WOMM Dependency Status", show_header=True)
    table.add_column("Strata", style="cyan", width=20)
    table.add_column("Component", style="yellow", width=30)
    table.add_column("Status", style="green", width=10, justify="center")
    table.add_column("Version", style="white", width=15)

    if verbose:
        table.add_column("Details", style="blue", width=30)

    # Strata 1
    for manager in result.system:
        if manager.supported_on_current_platform:
            row = [
                "System PKG MGR",
                manager.name,
                "✓" if manager.available else "✗",
                manager.version or "N/A",
            ]
            if verbose:
                row.append(f"Priority: {manager.priority}")
            table.add_row(*row)

    # Strata 2
    for entry in result.runtime:
        row = [
            "Runtime",
            entry.name,
            "✓" if entry.available else "✗",
            entry.version or "N/A",
        ]
        if verbose:
            row.append("Min: Any")
        table.add_row(*row)

    # Strata 3
    for entry in result.tools:
        row = ["DevTool", entry.name, "✓" if entry.available else "✗", "N/A"]
        if verbose:
            row.append("N/A")
        table.add_row(*row)

    ezconsole.print(table)


def display_deps_inventory(result: DependencyInventoryResult) -> None:
    """
    Display the static dependency inventory (no probing).

    Args:
        result: Inventory collected by ``DepsInterface.list_all()``
    """
    ezprinter.info("=== System Package Managers (Strata 1) ===")
    for entry in result.system:
        ezprinter.info(f"  • {entry.name} ({entry.detail})")

    ezprinter.info("\n=== Runtimes (Strata 2) ===")
    for entry in result.runtime:
        ezprinter.info(f"  • {entry.name} ({entry.detail})")

    ezprinter.info("\n=== Development Tools (Strata 3) ===")
    for entry in result.tools:
        ezprinter.info(f"  • {entry.name}: {entry.detail}")


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "display_available_managers",
    "display_best_manager",
    "display_deps_check_results",
    "display_deps_inventory",
    "display_deps_status_table",
    "display_system_detection_results",
    "display_system_managers_list",
    "render_environment_refresh_result",
    "render_system_detection_result",
]
