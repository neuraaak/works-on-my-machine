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


def display_deps_check_results(
    system_results: dict,
    runtime_results: dict,
    tool_results: dict,
    verbose: bool = False,
) -> None:
    """
    Display dependency check results (all strata).

    Args:
        system_results: System package manager results
        runtime_results: Runtime check results
        tool_results: Development tool check results
        verbose: Whether to show additional details
    """
    ezprinter.info("Checking all dependencies...\n")

    # Strata 1
    ezprinter.info("\n=== System Package Managers (Strata 1) ===")
    available = [name for name, res in system_results.items() if res.success]
    if available:
        ezprinter.success(f"Available: {', '.join(available)}")
        if verbose:
            for name in available:
                res = system_results[name]
                ezprinter.info(f"  • {name}: v{res.version}")
    else:
        ezprinter.warning("No system package managers available")
    ezconsole.print("")

    # Strata 2
    ezprinter.info("\n=== Runtimes (Strata 2) ===")
    for runtime, result in runtime_results.items():
        status = "✓" if result.success else "✗"
        version = f"v{result.version}" if result.version else "N/A"
        msg = f"{status} {runtime}: {version}"
        if result.success:
            ezprinter.success(msg)
        else:
            ezprinter.warning(msg)
    ezconsole.print("")

    # Strata 3
    ezprinter.info("\n=== Development Tools (Strata 3) ===")
    for tool, result in tool_results.items():
        status = "✓" if result.success else "✗"
        prefix = "  " if verbose else ""
        msg = f"{prefix}{status} {tool}"
        if result.success:
            ezprinter.success(msg)
        else:
            ezprinter.warning(msg)


def display_deps_status_table(
    system_status: dict,
    runtime_results: dict,
    tool_results: dict,
    verbose: bool = False,
) -> None:
    """
    Display comprehensive dependency status in a table.

    Args:
        system_status: System manager status data
        runtime_results: Runtime check results
        tool_results: Development tool check results (tool name -> result)
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
    for name, info in system_status.items():
        if info.get("supported_on_current_platform"):
            row = [
                "System PKG MGR",
                name,
                "✓" if info.get("available") else "✗",
                info.get("version") or "N/A",
            ]
            if verbose:
                row.append(f"Priority: {info.get('priority', 'N/A')}")
            table.add_row(*row)

    # Strata 2
    for runtime, result in runtime_results.items():
        row = [
            "Runtime",
            runtime,
            "✓" if result.success else "✗",
            result.version or "N/A",
        ]
        if verbose:
            row.append("Min: Any")
        table.add_row(*row)

    # Strata 3
    for tool, result in tool_results.items():
        row = ["DevTool", tool, "✓" if result.success else "✗", "N/A"]
        if verbose:
            row.append("N/A")
        table.add_row(*row)

    ezconsole.print(table)


def display_deps_validation_results(
    issues: list[str], valid_count: int, _verbose: bool = False
) -> None:
    """
    Display dependency validation results.

    Args:
        issues: List of validation issues found
        valid_count: Number of valid dependency chains
        verbose: Whether to show detailed results
    """
    ezprinter.info("Validating dependency chains...\n")

    if issues:
        ezprinter.error(f"\n{len(issues)} issue(s) found:")
        for issue in issues:
            ezprinter.error(f"  {issue}")
    else:
        ezprinter.success(f"\n✓ All {valid_count} dependency chains are valid")


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "display_available_managers",
    "display_best_manager",
    "display_deps_check_results",
    "display_deps_status_table",
    "display_deps_validation_results",
    "display_system_detection_results",
    "display_system_managers_list",
]
