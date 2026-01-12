#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# RUNTIME DISPLAY - Runtime UI Display Functions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Runtime display functions for Works On My Machine.

Provides display functions for runtime checks, installations, and listings.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Third-party imports
from rich.table import Table

# Local imports
from ...shared.configs.dependencies import RuntimeConfig
from ..common import ezconsole, ezprinter

# ///////////////////////////////////////////////////////////////
# DISPLAY FUNCTIONS
# ///////////////////////////////////////////////////////////////


def display_runtime_check_specific(
    result: object, runtime: str, verbose: bool = False
) -> None:
    """
    Display the result of checking a specific runtime.

    Args:
        result: Result object from check_runtime() with success, version, path, error
        runtime: Name of the runtime that was checked
        verbose: Whether to show additional details
    """
    if result.success:
        msg = f"{runtime} is installed"
        if result.version:
            msg += f" (version {result.version})"
        ezprinter.success(msg)

        if verbose:
            ezprinter.info(f"Path: {result.path}")
    else:
        ezprinter.warning(f"{runtime} is not installed")

        if verbose:
            config = RuntimeConfig.RUNTIMES.get(runtime, {})
            min_version = config.get("version", "N/A")
            ezprinter.info(f"Required version: {min_version}")


def display_runtime_check_all(interface: object, verbose: bool = False) -> None:
    """
    Display the result of checking all runtimes in a table.

    Args:
        interface: RuntimeInterface instance
        verbose: Whether to show additional details (path column)
    """
    with ezprinter.create_spinner("Checking runtimes..."):
        results = {}
        for runtime_name in RuntimeConfig.RUNTIMES:
            result = interface.check_runtime(runtime_name)
            results[runtime_name] = result

    # Create table with results
    table = Table(title="Runtimes", show_header=True)
    table.add_column("Runtime", style="cyan", no_wrap=True)
    table.add_column("Status", style="green", justify="center")
    table.add_column("Version", style="yellow")

    if verbose:
        table.add_column("Path", style="blue")

    for runtime_name, result in results.items():
        status = "✓" if result.success else "✗"
        version = f"v{result.version}" if result.version else "N/A"

        row = [runtime_name, status, version]

        if verbose:
            row.append(result.path or "N/A")

        table.add_row(*row)

    print()
    ezconsole.print(table)


def display_runtime_install_result(
    result: object,
    runtime: str,
    verbose: bool = False,
) -> None:
    """
    Display the result of a runtime installation.

    Args:
        result: Result object from install_runtime() with success, version, path, error
        runtime: Name of the runtime that was installed
        verbose: Whether to show additional details
    """
    if result.success:
        msg = f"{runtime} installed successfully"
        if result.version:
            msg += f" (version {result.version})"
        ezprinter.success(msg)

        if verbose:
            ezprinter.info(f"Path: {result.path}")
    else:
        ezprinter.error(f"Failed to install {runtime}")
        if result.error:
            ezprinter.error(f"Error: {result.error}")


def display_runtimes_list(verbose: bool = False) -> None:
    """
    Display all available runtimes in a table.

    Args:
        verbose: Whether to show additional details (package managers column)
    """
    table = Table(title="Available Runtimes", show_header=True)
    table.add_column("Runtime", style="cyan", no_wrap=True)
    table.add_column("Min Version", style="yellow")
    table.add_column("Priority", style="magenta", justify="center")

    if verbose:
        table.add_column("Package Managers", style="blue")

    for name, config in RuntimeConfig.RUNTIMES.items():
        row = [
            name,
            config.get("version", "Any"),
            str(config.get("priority", "N/A")),
        ]

        if verbose:
            managers = config.get("package_managers", [])
            row.append(", ".join(managers[:3]) + ("..." if len(managers) > 3 else ""))

        table.add_row(*row)

    ezconsole.print(table)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "display_runtime_check_all",
    "display_runtime_check_specific",
    "display_runtime_install_result",
    "display_runtimes_list",
]
