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
# Third-party imports
from rich.progress import TaskID

# Local imports
from ...exceptions.system import (
    DetectorInterfaceError,
    DevEnvDetectionServiceError,
    InfoServiceError,
    SystemDetectionServiceError,
)
from ...services import SystemDetectorService
from ...shared.results import SystemDetectionResult
from ...ui.common import ezlogger, ezpl_bridge, ezprinter
from ...ui.system import display_system_detection_results

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
            with ezprinter.create_spinner_with_status(
                "Detecting system information..."
            ) as (
                progress,
                task,
            ):
                task_id = TaskID(task)
                # Update description and status
                progress.update(
                    task_id,
                    description="🔍 Detecting system information...",
                    status="Initializing...",
                )

                # Update status during detection
                progress.update(task_id, status="Scanning system...")
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
                progress.update(task_id, status="Detection complete!")

            if data:
                print()
                display_system_detection_results(data)
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
