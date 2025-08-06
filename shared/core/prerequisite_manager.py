#!/usr/bin/env python3
"""
Prerequisite Manager for Works On My Machine.
Simplified version using the new DependencyManager.
"""

from typing import Dict, List, Optional

from .dependencies.runtime_manager import check_runtime, check_and_install_runtimes
from .dependencies.dependency_manager import get_installation_status


def check_prerequisites(tools: List[str], display_results: bool = True) -> Dict[str, Dict]:
    """Check if prerequisites are installed."""
    results = {}
    
    if "all" in tools:
        tools = ["python", "node", "git"]

    for tool in tools:
        result = check_runtime(tool)
        results[tool] = {
            "success": result.success,
            "message": result.message,
            "error": result.error,
            "version": result.version,
        }

    if display_results:
        _display_results(results)

    return results


def install_prerequisites(tools: List[str], custom_path: Optional[str] = None, display_results: bool = True) -> Dict[str, Dict]:
    """Install prerequisites."""
    if "all" in tools:
        tools = ["python", "node", "git"]

    # Use the new dependency manager
    install_result = check_and_install_runtimes(tools)
    
    results = {}
    for tool in tools:
        if tool in install_result.installed:
            results[tool] = {
                "success": True,
                "message": "Installed successfully",
                "error": None,
            }
        elif tool in install_result.skipped:
            results[tool] = {
                "success": True,
                "message": "Already installed",
                "error": None,
            }
        elif tool in install_result.failed:
            results[tool] = {
                "success": False,
                "message": "Installation failed",
                "error": "Installation failed",
            }

    if display_results:
        _display_results(results)

    return results


def get_installation_status(tools: List[str]) -> Dict[str, Dict]:
    """Get detailed installation status for tools."""
    if "all" in tools:
        tools = ["python", "node", "git"]
    
    status = get_installation_status(runtimes=tools)
    return status["runtimes"]


def _display_results(results: Dict[str, Dict]):
    """Display results using Rich UI."""
    try:
        from shared.ui.console import console, print_header
        from shared.ui.panels import create_panel
    except ImportError:
        # Fallback to basic output
        print("\n=== Prerequisites Results ===")
        for tool, result in results.items():
            if result.get("success"):
                print(f"✅ {tool}: {result.get('message', 'Available')}")
            else:
                print(f"❌ {tool}: {result.get('error', 'Not available')}")
        return

    try:
        print_header("W.O.M.M Prerequisites Check")

        content = []
        content.append("[bold blue]Prerequisites Results[/bold blue]")
        content.append("")

        for tool, result in results.items():
            if result.get("success"):
                content.append(f"✅ {tool}: {result.get('message', 'Available')}")
            else:
                content.append(f"❌ {tool}: {result.get('error', 'Not available')}")

        console.print()
        panel = create_panel(
            "\n".join(content),
            title="Prerequisites Check",
            style="white",
            border_style="dim white",
            padding=(1, 1),
        )
        console.print(panel)

    except Exception:
        # Fallback to basic output
        print("\n=== Prerequisites Results ===")
        for tool, result in results.items():
            if result.get("success"):
                print(f"✅ {tool}: {result.get('message', 'Available')}")
            else:
                print(f"❌ {tool}: {result.get('error', 'Not available')}")


# Legacy functions - simplified implementations
def install_package_manager(manager: str) -> bool:
    """Install a package manager - simplified implementation."""
    # This functionality is now handled by the new DependencyManager
    # For simplicity, return False as it's not commonly used
    return False


def setup_npm_path() -> bool:
    """Setup npm global packages path - simplified implementation."""
    # This functionality is now handled by the new DependencyManager
    # For simplicity, return True as npm path is usually handled automatically
    return True
