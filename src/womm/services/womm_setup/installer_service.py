#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# INSTALLATION SERVICE - Installation Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Installation Service - Singleton service for installation operations.

Handles installation verification operations that require service dependencies:
- PATH configuration verification (uses SystemPathService)
- Command accessibility verification (uses CommandRunnerService)
- Executable verification (uses CommandRunnerService)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import platform
from pathlib import Path
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.common import CommandExecutionError, ValidationServiceError
from ...exceptions.system import RegistryServiceError
from ...exceptions.womm_deployment import WommDeploymentServiceError
from ...shared.results import WOMMInstallerVerificationResult
from ..common.command_runner_service import CommandRunnerService
from ..system.path_service import SystemPathService

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# INSTALLATION SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class WommInstallerService:
    """Singleton service for installation verification operations."""

    _instance: ClassVar[WommInstallerService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> WommInstallerService:
        """Create or return the singleton instance.

        Returns:
            InstallationService: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize installation service (only once)."""
        if WommInstallerService._initialized:
            return

        self.logger = logging.getLogger(__name__)
        self._command_runner = CommandRunnerService()
        self._path_service = SystemPathService()
        WommInstallerService._initialized = True

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def verify_path_configuration(
        self, entry_path: str
    ) -> WOMMInstallerVerificationResult:
        """
        Verify that WOMM is correctly configured in PATH.

        Args:
            entry_path: Path to WOMM installation directory

        Returns:
            InstallationVerificationResult: Verification result

        Raises:
            WommDeploymentServiceError: If PATH configuration verification fails
        """
        if not entry_path:
            raise WommDeploymentServiceError(
                operation="path_verification",
                reason="Entry path cannot be empty",
            )

        is_windows = platform.system() == "Windows"

        if is_windows:
            # Query Windows registry for PATH using SystemPathService
            try:
                path_result = self._path_service.get_current_system_path()
            except (RegistryServiceError, ValidationServiceError) as e:
                raise WommDeploymentServiceError(
                    operation="path_verification",
                    reason="Failed to query Windows registry",
                    details=f"Path: {entry_path}, Error: {e}",
                ) from e

            if not path_result.success:
                # Business logic error - return result
                return WOMMInstallerVerificationResult(
                    success=False,
                    message=path_result.message or "Failed to get current PATH",
                    error=path_result.error or "",
                    entry_path=entry_path,
                    path_configured=False,
                    path_entries=[],
                )
            path_entries = path_result.path_entries or []
            found_in_path = self._resolve(entry_path) in {
                self._resolve(p) for p in path_entries if p
            }
        else:
            # Check Unix shell configuration files
            path_entries = self._shell_configs_mentioning(entry_path)
            found_in_path = bool(path_entries)

        if not found_in_path:
            raise WommDeploymentServiceError(
                operation="path_verification",
                reason="WOMM path not found in system PATH",
                details=(
                    f"Platform: {platform.system()}, "
                    f"Checked locations: {'Registry' if is_windows else path_entries}"
                ),
            )

        return WOMMInstallerVerificationResult(
            success=True,
            message=f"PATH configuration verified successfully for: {entry_path}",
            entry_path=entry_path,
            path_configured=True,
            path_entries=path_entries if is_windows else [],
        )

    def verify_commands_accessible(
        self, entry_path: str
    ) -> WOMMInstallerVerificationResult:
        """
        Verify that WOMM commands are accessible from PATH.

        Args:
            entry_path: Path to WOMM installation directory

        Returns:
            InstallationVerificationResult: Verification result

        Raises:
            WommDeploymentServiceError: If the executable is missing or not accessible
        """
        if not entry_path:
            raise WommDeploymentServiceError(
                operation="command_verification",
                reason="Entry path cannot be empty",
            )

        executable_name = "womm.bat" if platform.system() == "Windows" else "womm"
        local_executable = Path(entry_path) / executable_name

        # Test 1: Local executable exists and works
        if not local_executable.exists():
            raise WommDeploymentServiceError(
                operation="command_verification",
                reason=f"WOMM executable not found at {local_executable}",
                details=f"Platform: {platform.system()}",
            )

        local_stderr = self._version_check([str(local_executable), "--version"])
        local_works = local_stderr is None

        # Test 2: Global accessibility via PATH
        global_stderr = self._version_check([executable_name, "--version"])
        global_works = global_stderr is None

        if local_works:
            # A working local executable is enough: on Windows the global command
            # is routinely not yet visible in the session that ran the install.
            message = (
                "WOMM commands are accessible both locally and globally"
                if global_works
                else (
                    "WOMM executable works locally. Global command not yet accessible "
                    "in current session (normal after fresh installation)"
                )
            )
            return WOMMInstallerVerificationResult(
                success=True,
                message=message,
                entry_path=entry_path,
                commands_accessible=True,
                accessible_commands=["womm"],
            )

        # Both local and global failed - this is a real problem
        raise WommDeploymentServiceError(
            operation="command_verification",
            reason="WOMM command not accessible - both local and global tests failed",
            details=f"Local: {local_stderr}, Global: {global_stderr}",
        )

    def verify_executable_works(
        self, target_path: Path
    ) -> WOMMInstallerVerificationResult:
        """
        Verify that the WOMM executable works correctly.

        Args:
            target_path: Target installation directory

        Returns:
            InstallationVerificationResult: Verification result

        Raises:
            WommDeploymentServiceError: If executable is missing or fails to work
        """
        if not target_path or not target_path.exists():
            raise WommDeploymentServiceError(
                operation="executable_verification",
                reason="Target path does not exist",
                details=f"Target path: {target_path}",
            )

        executable_name = "womm.bat" if platform.system() == "Windows" else "womm"
        executable_path = target_path / executable_name

        if not executable_path.exists():
            raise WommDeploymentServiceError(
                operation="executable_verification",
                reason=f"Executable not found at {executable_path}",
                details=f"Platform: {platform.system()}",
            )

        failure = self._version_check([str(executable_path), "--version"])
        if failure is not None:
            raise WommDeploymentServiceError(
                operation="executable_verification",
                reason=f"Executable test failed at {executable_path}",
                details=failure,
            )

        return WOMMInstallerVerificationResult(
            success=True,
            message=f"WOMM executable verified successfully at {executable_path}",
            entry_path=str(target_path),
            executable_works=True,
        )

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _resolve(self, path: str) -> str:
        """Resolve a path for comparison, falling back to the raw string.

        Args:
            path: Path to normalize

        Returns:
            str: Resolved path, or the input unchanged if resolution fails
        """
        try:
            return str(Path(path).resolve())
        except OSError as e:
            self.logger.warning(f"Failed to resolve path {path}: {e}")
            return path

    def _shell_configs_mentioning(self, entry_path: str) -> list[str]:
        """List the user's shell rc files that reference `entry_path`.

        Args:
            entry_path: Path to look for in the shell configuration files

        Returns:
            List[str]: Paths of the rc files mentioning `entry_path`
        """
        shell_rc_files = [
            Path.home() / ".bashrc",
            Path.home() / ".zshrc",
            Path.home() / ".profile",
        ]

        matches = []
        for rc_file in shell_rc_files:
            try:
                if rc_file.exists() and entry_path in rc_file.read_text(
                    encoding="utf-8"
                ):
                    matches.append(str(rc_file))
            except (OSError, UnicodeDecodeError) as e:
                self.logger.warning(f"Failed to check shell config {rc_file}: {e}")
                continue

        return matches

    def _version_check(self, command: list[str]) -> str | None:
        """Run `command` and report whether it succeeded.

        Args:
            command: Command to run

        Returns:
            None if the command exited 0, otherwise an ASCII-safe failure
            description (stderr, or the reason the command could not run).
        """
        try:
            result = self._command_runner.run_silent(command, capture_output=True)
        except CommandExecutionError as e:
            self.logger.warning(f"Failed to run {command}: {e}")
            return self._ascii(str(e))

        if result.returncode == 0:
            return None

        stderr = result.stderr
        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors="replace")
        return self._ascii(stderr) if stderr else f"exit code {result.returncode}"

    @staticmethod
    def _ascii(text: str) -> str:
        """Strip characters the console encoding cannot represent.

        Args:
            text: Text to sanitize

        Returns:
            str: ASCII-safe text
        """
        return text.encode("ascii", "replace").decode("ascii")
