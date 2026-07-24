#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM DETECTOR INTERFACE - System Detection Interface
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
System Detector Interface for Works On My Machine.

Orchestrates SystemDetectorService and translates its exception into a Result.
This interface carries no UI: it does not print, log, or drive spinners — the
command layer owns presentation (spinner + renderer). It never re-raises; the
single service exception is converted into a ``SystemDetectionResult``.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from ...exceptions.system import DetectorServiceError
from ...services import SystemDetectorService
from ...shared.results import SystemDetectionResult

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class SystemDetectorInterface:
    """Orchestrates SystemDetectorService and returns a Result.

    Pure orchestration: no UI, no re-raise. The service's ``DetectorServiceError``
    is translated into a ``SystemDetectionResult`` (the single exception→Result
    conversion point). Unexpected errors are not swallowed — they propagate.
    """

    def __init__(self) -> None:
        """Initialize the interface (service is created lazily)."""
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
        Detect system information and available tools.

        Returns:
            SystemDetectionResult: success with ``system_data`` populated, or
            failure carrying the error message when detection fails.
        """
        try:
            data = self.detector.get_system_data()
        except DetectorServiceError as e:
            return SystemDetectionResult(
                success=False,
                message="System detection failed",
                error=str(e),
                system_data={},
            )

        return SystemDetectionResult(
            success=True,
            message="System detection completed successfully",
            system_data=data,
        )


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["SystemDetectorInterface"]
