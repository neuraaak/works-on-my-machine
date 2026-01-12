#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM MANAGER INTERFACE - System Detection and Prerequisites Management Interface
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
System Manager Interface for Works On My Machine.

Handles system detection and prerequisites installation with integrated UI.
Provides comprehensive system information, package manager detection,
and runtime installation capabilities.

This interface orchestrates system services and converts service exceptions
to interface exceptions following the MEF pattern.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from ...exceptions.system import (
    DetectorInterfaceError,
    DevEnvDetectionServiceError,
    InfoServiceError,
    SystemDetectionServiceError,
)
from ...services import SystemDetectorService
from ...shared.results.system_results import (
    SystemDetectionResult,
)
from ...ui.common.ezpl_bridge import (
    ezlogger,
    ezpl_bridge,
    ezprinter,
)

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class SystemDetectorInterface:
    """Manages system detection and prerequisites installation with integrated UI.

    This interface orchestrates SystemDetectorService and converts service
    exceptions to interface exceptions following the MEF pattern.
    """

    def __init__(self) -> None:
        """Initialize the SystemManagerInterface."""
        # Lazy initialization to avoid slow startup
        self._detector: SystemDetectorService | None = None

    @property
    def detector(self) -> SystemDetectorService:
        """Lazy load SystemDetectorService when needed."""
        if self._detector is None:
            self._detector = SystemDetectorService()
        return self._detector

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def detect_system(self) -> SystemDetectionResult:
        """
        Detect system information and available tools with UI.

        Returns:
            SystemDetectionResult: Result of the detection operation

        Raises:
            SystemDetectorInterfaceError: If system detection fails
        """
        try:
            ezprinter.print_header("WOMM System Detection")

            with ezprinter.create_spinner_with_status(
                "Detecting system information..."
            ) as (
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
                    InfoServiceError,
                    DetectorInterfaceError,
                    DevEnvDetectionServiceError,
                    SystemDetectionServiceError,
                ) as e:
                    # Convert service exceptions to interface exceptions
                    ezlogger.error(f"System detection failed: {e}")
                    raise DetectorInterfaceError(
                        message=f"System detection failed: {e.message if hasattr(e, 'message') else str(e)}",
                        operation="detect_system",
                        details=f"Service exception: {type(e).__name__} - {e.details if hasattr(e, 'details') else ''}",
                    ) from e
                except Exception as e:
                    # Wrap unexpected external exceptions
                    ezlogger.error(f"Unexpected error during system detection: {e}")
                    raise DetectorInterfaceError(
                        message=f"Failed to retrieve system information: {e}",
                        operation="detect_system",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

                # Final status update
                progress.update(task, status="Detection complete!")

            if data:
                self._display_system_data(data)
                return SystemDetectionResult(
                    success=True,
                    message="System detection completed successfully",
                    system_data=data,
                    detection_time=0.0,
                )
            else:
                ezpl_bridge.console.print("❌ Failed to detect system information")
                raise DetectorInterfaceError(
                    message="System detection returned no data",
                    operation="detect_system",
                    details="SystemDetector.get_system_data() returned None or empty data",
                )

        except DetectorInterfaceError:
            # Re-raise interface exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            ezlogger.error(f"Unexpected error in detect_system: {e}")
            raise DetectorInterfaceError(
                message=f"System detection failed: {e}",
                operation="detect_system",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _display_system_data(self, data: dict) -> None:
        """
        Display system data in a Rich panel.

        Args:
            data: System data to display

        Raises:
            SystemDetectorInterfaceError: If data display fails
        """
        try:
            # Validate data structure
            if not isinstance(data, dict):
                raise DetectorInterfaceError(
                    message="Invalid data format: expected dictionary",
                    operation="display_system_data",
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
            ezpl_bridge.console.print()
            panel = ezprinter.create_panel(
                "\n".join(content),
                title="System Detection Results",
                border_style="dim white",
            )
            ezpl_bridge.console.print(panel)

        except DetectorInterfaceError:
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            ezlogger.error(f"Unexpected error displaying system data: {e}")
            raise DetectorInterfaceError(
                message=f"Failed to display system data: {e}",
                operation="display_system_data",
                details=f"Exception type: {type(e).__name__}",
            ) from e
