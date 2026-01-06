#!/usr/bin/env python3
"""
System Manager for Works On My Machine.
Handles system detection and prerequisites installation with integrated UI.
"""

# =============================================================================
# IMPORTS
# =============================================================================
# Standard library imports
import logging
from typing import Dict, List

# Third-party imports
from rich.table import Table

from ...exceptions.system import (
    DevelopmentEnvironmentDetectionError,
    PackageManagerDetectionError,
    SystemDetectionError,
    SystemInfoError,
)
from ...ui.common.console import (
    console,
    print_error,
    print_header,
    print_success,
    print_system,
)
from ...ui.common.progress import create_spinner_with_status
from ...utils.system.system_detector import SystemDetector

# Local imports - moved to methods to avoid slow startup
# from ..dependencies.runtime_manager import runtime_manager

# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)

# =============================================================================
# MAIN CLASS
# =============================================================================


class SystemManager:
    """Manages system detection and prerequisites installation with integrated UI."""

    def __init__(self):
        """Initialize the SystemManager."""
        # Lazy initialization to avoid slow startup
        self._detector = None

    @property
    def detector(self):
        """Lazy load SystemDetector when needed."""
        if self._detector is None:
            try:
                self._detector = SystemDetector()
            except (
                SystemDetectionError,
                PackageManagerDetectionError,
                DevelopmentEnvironmentDetectionError,
            ) as e:
                # Re-raise our custom exceptions
                logger.error(f"Failed to initialize SystemDetector: {e}")
                raise
            except Exception as e:
                # Wrap unexpected external exceptions
                logger.error(f"Unexpected error initializing SystemDetector: {e}")
                raise SystemDetectionError(
                    message=f"Failed to initialize system detector: {e}",
                    details=f"Exception type: {type(e).__name__}",
                ) from e
        return self._detector

    def detect_system(self, dry_run: bool = False) -> None:
        """
        Detect system information and available tools with UI.

        Args:
            dry_run: Show what would be done without making changes

        Raises:
            SystemDetectionError: If system detection fails
            SystemInfoError: If system information retrieval fails
        """
        try:
            if dry_run:
                from ...ui.common.console import (
                    print_dry_run_message,
                    print_dry_run_success,
                    print_dry_run_warning,
                )

                print_dry_run_warning()
                print_header("WOMM System Detection (DRY RUN)")

                # Simulate system detection process
                print_dry_run_message(
                    "scan system", "detect operating system and platform"
                )
                print_dry_run_message(
                    "check package managers", "identify available package managers"
                )
                print_dry_run_message(
                    "detect development tools",
                    "find installed development environments",
                )
                print_dry_run_message(
                    "analyze results", "generate system information report"
                )
                print_dry_run_success()
                return

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

                # Update status during detection
                progress.update(task, status="Scanning system...")
                try:
                    data = self.detector.get_system_data()
                except (
                    SystemInfoError,
                    PackageManagerDetectionError,
                    DevelopmentEnvironmentDetectionError,
                ) as e:
                    # Re-raise our custom exceptions
                    logger.error(f"System detection failed: {e}")
                    raise
                except Exception as e:
                    # Wrap unexpected external exceptions
                    logger.error(f"Unexpected error during system detection: {e}")
                    raise SystemInfoError(
                        message=f"Failed to retrieve system information: {e}",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

                # Final status update
                progress.update(task, status="Detection complete!")

            if data:
                self._display_system_data(data)
            else:
                console.print("❌ Failed to detect system information")
                raise SystemDetectionError(
                    message="System detection returned no data",
                    details="SystemDetector.get_system_data() returned None or empty data",
                )

        except (
            SystemDetectionError,
            SystemInfoError,
            PackageManagerDetectionError,
            DevelopmentEnvironmentDetectionError,
        ):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in detect_system: {e}")
            raise SystemDetectionError(
                message=f"System detection failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def check_prerequisites(self, tools: List[str]) -> None:
        """
        Check system prerequisites with UI.

        Args:
            tools: List of tools to check

        Raises:
            SystemDetectionError: If prerequisites checking fails
        """
        try:
            # Input validation
            if tools is not None and not isinstance(tools, list):
                raise SystemDetectionError(
                    message="Tools parameter must be a list",
                    details=f"Received type: {type(tools).__name__}",
                )

            print_header("WOMM System Prerequisites :: Checking")

            from ...ui.common.console import print_system

            # Lazy import to avoid slow startup
            from ..dependencies.runtime_manager import runtime_manager

            print_system("Checking system prerequisites...")

            # Determine which tools to process
            tools_to_process = (
                ["python", "node", "git"]
                if not tools or "all" in tools
                else list(tools)
            )

            # Check prerequisites
            results = {}
            for _i, step in enumerate(tools_to_process):
                try:
                    result = runtime_manager.check_runtime(step)
                    results[step] = result
                except Exception as e:
                    logger.warning(f"Failed to check runtime {step}: {e}")
                    # Continue with other tools

            # Display results in a table
            self._display_prerequisites_table(results, "Prerequisites Status")
            console.print("")

            # Check if any tools are missing
            missing_tools = [
                tool for tool, result in results.items() if not result.success
            ]
            if missing_tools:
                print_error(f"Missing tools: {', '.join(missing_tools)}")
                print_system("💡 Run without --check flag to install them.")

        except SystemDetectionError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in check_prerequisites: {e}")
            raise SystemDetectionError(
                message=f"Prerequisites checking failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def install_prerequisites(
        self,
        tools: List[str],
        pm_args: List[str] | None = None,
        ask_path: bool = False,
        dry_run: bool = False,
    ) -> None:
        """
        Install system prerequisites with interactive UI.

        Args:
            tools: List of tools to install
            pm_args: Package manager arguments
            ask_path: Whether to ask for installation path
            dry_run: Show what would be done without making changes

        Raises:
            SystemDetectionError: If prerequisites installation fails
        """
        try:
            # Input validation
            if tools is not None and not isinstance(tools, list):
                raise SystemDetectionError(
                    message="Tools parameter must be a list",
                    details=f"Received type: {type(tools).__name__}",
                )
            if pm_args is not None and not isinstance(pm_args, list):
                raise SystemDetectionError(
                    message="Package manager arguments must be a list",
                    details=f"Received type: {type(pm_args).__name__}",
                )

            if dry_run:
                from ...ui.common.console import (
                    print_dry_run_message,
                    print_dry_run_success,
                    print_dry_run_warning,
                )

                print_dry_run_warning()
                print_header("WOMM System Prerequisites :: Installing (DRY RUN)")

                # Simulate system detection and installation process
                print_dry_run_message(
                    "detect system", "check available package managers"
                )
                print_dry_run_message(
                    "check current status", "analyze installed runtimes"
                )

                if tools:
                    print_dry_run_message(
                        "install runtimes", f"tools: {', '.join(tools)}"
                    )
                else:
                    print_dry_run_message(
                        "install runtimes", "interactive selection mode"
                    )

                if ask_path:
                    print_dry_run_message(
                        "prompt for paths", "ask user for installation directories"
                    )

                if pm_args:
                    print_dry_run_message(
                        "use package manager args", f"args: {', '.join(pm_args)}"
                    )

                print_dry_run_success()
                return

            print_header("WOMM System Prerequisites :: Installing")

            # Step 1: Ensure a package manager is available (no auto-install)
            from ..dependencies.package_manager import package_manager

            # Lazy import to avoid slow startup
            from ..dependencies.runtime_manager import (
                RUNTIMES,
                RuntimeResult,
                runtime_manager,
            )

            print_system("Checking system prerequisites...")

            # Ensure package manager first to avoid repeated failures later
            preferred = None  # Let runtime-specific handle preferences, but early feedback helps
            try:
                pm_result = package_manager.ensure_manager(preferred)
            except Exception as e:
                logger.error(f"Failed to ensure package manager: {e}")
                raise SystemDetectionError(
                    message=f"Package manager setup failed: {e}",
                    details=f"Exception type: {type(e).__name__}",
                ) from e

            if not pm_result.success:
                if getattr(pm_result, "panel", None) is not None:
                    console.print(pm_result.panel)
                print_error("Aucun gestionnaire de paquets disponible. Abandon.")
                return

            selected_pm_name = pm_result.package_manager_name
            selected_pm_platform = pm_result.platform

            all_runtimes = list(RUNTIMES.keys())
            try:
                current_status = runtime_manager.get_installation_status(all_runtimes)
            except Exception as e:
                logger.error(f"Failed to get installation status: {e}")
                raise SystemDetectionError(
                    message=f"Failed to check current installation status: {e}",
                    details=f"Exception type: {type(e).__name__}",
                ) from e

            # Display current status
            current_results = {}
            for runtime in all_runtimes:
                status = current_status[runtime]
                current_results[runtime] = RuntimeResult(
                    success=status["installed"],
                    runtime_name=runtime,
                    version=status["version"],
                    path=status["path"],
                    message=f"Runtime {runtime} {'available' if status['installed'] else 'not found'}",
                    error=(
                        None
                        if status["installed"]
                        else f"Runtime {runtime} not installed"
                    ),
                )

            self._display_prerequisites_table(current_results, "Current Status")

            # Step 2: Interactive selection if not "all" specified
            if not tools or "all" in tools:
                # Use interactive selection
                try:
                    selected_runtimes = self._interactive_runtime_selection(
                        current_status
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to perform interactive runtime selection: {e}"
                    )
                    raise SystemDetectionError(
                        message=f"Interactive runtime selection failed: {e}",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e
                # No need to show "no selection" message as it's handled in _interactive_runtime_selection
                if not selected_runtimes:
                    return
            else:
                # Use specified tools
                selected_runtimes = tools

            # Step 3: Install selected runtimes
            if not selected_runtimes:
                console.print("✅ Tous les runtimes sont déjà installés !")
                return

            print_system("🚀 Installation des runtimes sélectionnés...")

            installation_results = {}
            for runtime in selected_runtimes:
                print_system(f"📦 Installation de {runtime}...")

                with create_spinner_with_status(f"Installing {runtime}...") as (
                    progress,
                    task,
                ):
                    # Build extra args for PM if requested
                    extra_pm_args = list(pm_args) if pm_args else None

                    # Best-effort ask-path (Windows/winget,choco) via generic args
                    if ask_path:
                        from ...ui.common.console import print_warn
                        from ...ui.common.prompts import prompt_path

                        try:
                            install_dir = prompt_path(
                                f"Chemin d'installation pour {runtime} (laisser vide pour défaut):",
                                default=None,
                            )
                            if install_dir:
                                extra_pm_args = extra_pm_args or []
                                # Best-effort mapping by selected package manager
                                if (
                                    selected_pm_platform == "windows"
                                    and selected_pm_name == "winget"
                                ):
                                    extra_pm_args.append(f"--location={install_dir}")
                                elif (
                                    selected_pm_platform == "windows"
                                    and selected_pm_name == "chocolatey"
                                ):
                                    extra_pm_args.append(
                                        f'--install-arguments=INSTALLDIR="{install_dir}"'
                                    )
                                else:
                                    print_warn(
                                        "Le gestionnaire de paquets sélectionné ne supporte probablement pas un chemin d'installation personnalisé. L'argument sera ignoré."
                                    )
                        except Exception as e:
                            logger.warning(
                                f"Failed to prompt for installation path: {e}"
                            )
                            # Continue without custom path

                    # Use runtime_manager for installation
                    try:
                        result = runtime_manager.install_runtime(
                            runtime, extra_pm_args=extra_pm_args
                        )
                        installation_results[runtime] = result
                    except Exception as e:
                        logger.error(f"Failed to install runtime {runtime}: {e}")
                        # Create a failed result
                        installation_results[runtime] = RuntimeResult(
                            success=False,
                            runtime_name=runtime,
                            version=None,
                            path=None,
                            message=f"Installation failed: {e}",
                            error=str(e),
                        )

                    if result.success:
                        progress.update(
                            task, status=f"{runtime} installed successfully!"
                        )
                    else:
                        progress.update(task, status=f"{runtime} installation failed!")

            # Step 4: Display final results
            print_system("Installation Summary:")
            self._display_installation_table(installation_results)
            console.print("")

            # Step 5: Final verification
            failed_installations = [
                runtime
                for runtime, result in installation_results.items()
                if not result.success
            ]

            if failed_installations:
                print_error(f"Failed to install: {', '.join(failed_installations)}")
                raise SystemDetectionError(
                    message="Prerequisites installation failed",
                    details=f"Failed installations: {', '.join(failed_installations)}",
                )
            else:
                print_success("All prerequisites installed successfully!")

        except SystemDetectionError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in install_prerequisites: {e}")
            raise SystemDetectionError(
                message=f"Prerequisites installation failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _interactive_runtime_selection(self, current_status: Dict) -> List[str]:
        """
        Interactive runtime selection using the new select_multiple_from_list method.

        Args:
            current_status: Current installation status

        Returns:
            List[str]: Selected runtime names

        Raises:
            SystemDetectionError: If interactive selection fails
        """
        try:
            from ...ui.interactive import InteractiveMenu

            # Lazy import to avoid slow startup
            from ..dependencies.runtime_manager import RUNTIMES

            # Prepare items for selection
            items = []
            checked_items = []
            disabled_items = []

            # Sort runtimes by priority
            sorted_runtimes = sorted(RUNTIMES.items(), key=lambda x: x[1]["priority"])

            for runtime_name, runtime_config in sorted_runtimes:
                runtime_status = current_status.get(runtime_name, {})
                is_installed = runtime_status.get("installed", False)
                version = runtime_status.get("version", "Non installé")

                # Create item dict
                item = {
                    "key": runtime_name,
                    "name": runtime_name.title(),
                    "version": version,
                    "priority": runtime_config["priority"],
                    "installed": is_installed,
                }
                items.append(item)

                # Mark as checked and disabled if installed
                if is_installed:
                    checked_items.append(runtime_name)
                    disabled_items.append(runtime_name)

            # Display function
            def format_runtime_item(item):
                status_icon = "✅" if item["installed"] else "❌"
                priority_text = (
                    f"[{item['priority']}] " if not item["installed"] else ""
                )
                return (
                    f"{status_icon} {priority_text}{item['name']} ({item['version']})"
                )

            # Create interactive menu
            menu = InteractiveMenu("Quels runtimes voulez-vous installer ?")

            # Check if all runtimes are already installed
            all_installed = all(item["installed"] for item in items)
            if all_installed:
                console.print("✅ Tous les runtimes sont déjà installés !")
                return []

            # Show selection
            selected = menu.select_multiple_from_list(
                items=items,
                display_func=format_runtime_item,
                checked_items=checked_items,
                disabled_items=disabled_items,
            )

            if selected:
                # Extract runtime names from selected items
                return [item["key"] for item in selected]

            return []

        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in interactive runtime selection: {e}")
            raise SystemDetectionError(
                message=f"Interactive runtime selection failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _display_system_data(self, data: Dict) -> None:
        """
        Display system data in a Rich panel.

        Args:
            data: System data to display

        Raises:
            SystemDetectionError: If data display fails
        """
        try:
            from ...ui.common.panels import create_panel

            # Validate data structure
            if not isinstance(data, dict):
                raise SystemDetectionError(
                    message="Invalid data format: expected dictionary",
                    details=f"Received type: {type(data).__name__}",
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
            content.append(
                f"Architecture: {system_info.get('architecture', 'unknown')}"
            )
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

        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error displaying system data: {e}")
            raise SystemDetectionError(
                message=f"Failed to display system data: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _display_prerequisites_table(self, results: Dict, title: str) -> None:
        """
        Display prerequisites results in a table.

        Args:
            results: Prerequisites results
            title: Table title

        Raises:
            SystemDetectionError: If table display fails
        """
        try:
            table = Table(title=title)
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

        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error displaying prerequisites table: {e}")
            raise SystemDetectionError(
                message=f"Failed to display prerequisites table: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _display_installation_table(self, results: Dict) -> None:
        """
        Display installation results in a table.

        Args:
            results: Installation results

        Raises:
            SystemDetectionError: If table display fails
        """
        try:
            table = Table(title="Installation Results")
            table.add_column("Tool", style="cyan", no_wrap=True)
            table.add_column("Status", style="bold")
            table.add_column("Version", style="dim")
            table.add_column("Message", style="dim")

            for tool, result in results.items():
                if result.success:
                    status = "✅ Success"
                    version = result.version or "N/A"
                else:
                    status = "❌ Failed"
                    version = "N/A"

                message = result.message or result.error or "N/A"
                table.add_row(tool.capitalize(), status, version, message)

            console.print(table)

        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error displaying installation table: {e}")
            raise SystemDetectionError(
                message=f"Failed to display installation table: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

system_manager = SystemManager()
