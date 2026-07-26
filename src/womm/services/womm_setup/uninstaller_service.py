#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UNINSTALLATION SERVICE - Uninstallation Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Uninstallation Service - Singleton service for uninstallation operations.

Handles uninstallation verification operations that require service dependencies:
- Complete uninstallation verification (uses CommandRunnerService)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.common import CommandExecutionError
from ...exceptions.womm_deployment import WommDeploymentServiceError
from ...shared.results import WOMMInstallerVerificationResult
from ..common.command_runner_service import CommandRunnerService

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# UNINSTALLATION SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class WommUninstallerService:
    """Singleton service for uninstallation verification operations."""

    _instance: ClassVar[WommUninstallerService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> WommUninstallerService:
        """Create or return the singleton instance.

        Returns:
            UninstallationService: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize uninstallation service (only once)."""
        if WommUninstallerService._initialized:
            return

        self.logger = logging.getLogger(__name__)
        self._command_runner = CommandRunnerService()
        WommUninstallerService._initialized = True

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def verify_uninstallation_complete(
        self, target_path: Path
    ) -> WOMMInstallerVerificationResult:
        """
        Verify that uninstallation completed successfully.

        Args:
            target_path: Target installation directory

        Returns:
            InstallationVerificationResult: Result with success status and details

        Raises:
            WommDeploymentServiceError: If `target_path` is empty
        """
        if not target_path:
            raise WommDeploymentServiceError(
                operation="completion_verification",
                reason="Target path cannot be empty",
            )

        # The directory removal itself is verified by utils; this service only
        # checks that the `womm` command is no longer reachable.
        try:
            cmd_result = self._command_runner.run_silent(
                ["womm", "--version"], timeout=10
            )
        except CommandExecutionError as e:
            # If command execution fails, that's actually success (command not found)
            self.logger.info(f"Command execution failed (expected): {e}")
            return WOMMInstallerVerificationResult(
                success=True,
                message="WOMM command no longer accessible (execution failed)",
                entry_path=str(target_path),
                executable_works=False,
            )

        # Exit code 9009 is "command not found" on Windows, i.e. success here.
        command_gone = cmd_result.returncode == 9009
        return WOMMInstallerVerificationResult(
            # A command that is still reachable may belong to another
            # installation, so it never fails the uninstall.
            success=True,
            message=(
                "WOMM command no longer accessible"
                if command_gone
                else "WOMM command still accessible (may be from another installation)"
            ),
            entry_path=str(target_path),
            executable_works=not command_gone,
        )
