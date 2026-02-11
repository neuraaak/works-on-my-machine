#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM DETECTOR SERVICE - System Detection Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
SystemDetectorService - Service for advanced system detection.

Detects OS, architecture, package managers, and development
environments. Provides comprehensive system information for WOMM.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
import logging
import os
import platform
import shutil
from pathlib import Path

# Local imports
from ...exceptions.common import ValidationServiceError
from ...exceptions.system import (
    DevEnvDetectionServiceError,
    InfoServiceError,
    PkgManagerDetectionServiceError,
    ReportGenerationServiceError,
    SystemDetectionServiceError,
)
from ...shared.configs.system import SystemDetectorConfig
from ...shared.results import SystemInfoResult
from ...utils.system import (
    create_editor_entry,
    create_package_manager_entry,
    create_shell_entry,
    extract_version_first_line,
    extract_version_from_stdout,
    generate_recommendations,
    get_best_package_manager,
)
from ..common.command_runner_service import CommandRunnerService

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)
_command_runner = CommandRunnerService()


# ///////////////////////////////////////////////////////////////
# SYSTEM DETECTOR SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class SystemDetectorService:
    """System detector service for real-time system detection.

    Detects system information on instantiation for accurate, up-to-date results.
    """

    def __init__(self) -> None:
        """Initialize the system detector service with fresh detection."""
        try:
            # Initialization is critical - raise exceptions on failure
            system_info_result = self.get_system_info()
            if not system_info_result.success:
                raise InfoServiceError(
                    operation="initialization",
                    reason=system_info_result.message or "Failed to get system info",
                    details=system_info_result.error or "",
                )
            self.system_info = {
                "platform": system_info_result.platform,
                "platform_release": system_info_result.platform_release,
                "platform_version": system_info_result.platform_version,
                "architecture": system_info_result.architecture,
                "processor": system_info_result.processor,
                "python_version": system_info_result.python_version,
                "python_implementation": system_info_result.python_implementation,
                "node": system_info_result.node,
                "user": system_info_result.user,
                "home": system_info_result.home,
                "shell": system_info_result.shell,
                "terminal": system_info_result.terminal,
                "path_separator": system_info_result.path_separator,
                "line_separator": system_info_result.line_separator,
            }
            self.package_managers = self.detect_package_managers()
            self.dev_environments = self.detect_development_environments()
        except (
            SystemDetectionServiceError,
            InfoServiceError,
            PkgManagerDetectionServiceError,
            DevEnvDetectionServiceError,
            ValidationServiceError,
        ):
            # Re-raise programming errors and critical errors
            raise
        except Exception as e:
            # Wrap unexpected external exceptions - critical init error
            raise SystemDetectionServiceError(
                message=f"Failed to initialize system detector: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def get_system_info(self) -> SystemInfoResult:
        """
        Returns basic system information.

        Returns:
            SystemInfoResult: System information result

        Raises:
            SystemInfoError: If system information gathering fails critically
        """
        try:
            return SystemInfoResult(
                success=True,
                message="System information retrieved successfully",
                platform=platform.system(),
                platform_release=platform.release(),
                platform_version=platform.version(),
                architecture=platform.machine(),
                processor=platform.processor(),
                python_version=platform.python_version(),
                python_implementation=platform.python_implementation(),
                node=platform.node(),
                user=os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
                home=str(Path.home()),
                shell=os.environ.get("SHELL", "unknown"),
                terminal=os.environ.get("TERM", "unknown"),
                path_separator=os.pathsep,
                line_separator=os.linesep,
            )
        except (OSError, PermissionError) as e:
            # Critical system errors - raise exception
            raise InfoServiceError(
                operation="platform_info",
                reason=f"Failed to gather system information: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e
        except Exception as e:
            # Wrap unexpected external exceptions - critical error
            raise InfoServiceError(
                operation="platform_info",
                reason=f"Failed to gather system information: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def detect_package_managers(
        self,
    ) -> dict[str, dict[str, str | bool | int | None]]:
        """
        Detects all available package managers.

        Returns:
            Dict[str, Dict]: Dictionary of detected package managers

        Raises:
            PackageManagerDetectionError: If package manager detection fails
        """
        try:
            managers: dict[str, dict[str, str | bool | int | None]] = {}

            # Windows
            if self.system_info["platform"] == "Windows":
                managers.update(self._detect_windows_managers())

            # macOS
            elif self.system_info["platform"] == "Darwin":
                managers.update(self._detect_macos_managers())

            # Linux
            elif self.system_info["platform"] == "Linux":
                managers.update(self._detect_linux_managers())

            return managers

        except (PkgManagerDetectionServiceError, InfoServiceError):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise PkgManagerDetectionServiceError(
                package_manager="all",
                operation="detection",
                reason=f"Failed to detect package managers: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _detect_windows_managers(
        self,
    ) -> dict[str, dict[str, str | bool | int | None]]:
        """
        Detects Windows package managers.

        Returns:
            Dict[str, Dict]: Dictionary of Windows package managers

        Raises:
            PackageManagerDetectionError: If Windows package manager detection fails
        """
        try:
            managers: dict[str, dict[str, str | bool | int | None]] = {}

            for (
                manager_name,
                metadata,
            ) in SystemDetectorConfig.get_windows_package_managers().items():
                command = metadata.get("command")
                if not isinstance(command, str):
                    logger.warning(
                        f"Invalid command value for {manager_name}: {command}"
                    )
                    continue

                availability_result = _command_runner.check_command_available(command)
                if availability_result.is_available:
                    try:
                        result = _command_runner.run_silent([command, "--version"])
                        version = extract_version_from_stdout(
                            result.stdout if bool(result) else None
                        )
                    except Exception as e:
                        logger.warning(f"Failed to get {manager_name} version: {e}")
                        version = "unknown"

                    managers[manager_name] = create_package_manager_entry(
                        manager_name, version, metadata
                    )

            return managers

        except Exception as e:
            # Wrap unexpected external exceptions
            raise PkgManagerDetectionServiceError(
                package_manager="windows_managers",
                operation="detection",
                reason=f"Failed to detect Windows package managers: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _detect_macos_managers(
        self,
    ) -> dict[str, dict[str, str | bool | int | None]]:
        """
        Detects macOS package managers.

        Returns:
            Dict[str, Dict]: Dictionary of macOS package managers

        Raises:
            PackageManagerDetectionError: If macOS package manager detection fails
        """
        try:
            managers: dict[str, dict[str, str | bool | int | None]] = {}

            for (
                manager_name,
                metadata,
            ) in SystemDetectorConfig.get_macos_package_managers().items():
                command = metadata.get("command")
                if not isinstance(command, str):
                    logger.warning(
                        f"Invalid command value for {manager_name}: {command}"
                    )
                    continue
                # Homebrew uses check_command_available, MacPorts uses shutil.which
                availability_result = (
                    _command_runner.check_command_available(command)
                    if command == "brew"
                    else None
                )
                is_available = (
                    availability_result.is_available
                    if availability_result
                    else bool(shutil.which(command))
                )

                if is_available:
                    try:
                        version_args = (
                            ["--version"] if command == "brew" else ["version"]
                        )
                        result = _command_runner.run_silent([command, *version_args])
                        version = (
                            extract_version_first_line(
                                result.stdout if bool(result) else None
                            )
                            if command == "brew"
                            else extract_version_from_stdout(
                                result.stdout if bool(result) else None
                            )
                        )
                    except Exception as e:
                        logger.warning(f"Failed to get {manager_name} version: {e}")
                        version = "unknown"

                    managers[manager_name] = create_package_manager_entry(
                        manager_name, version, metadata
                    )

            return managers

        except Exception as e:
            # Wrap unexpected external exceptions
            raise PkgManagerDetectionServiceError(
                package_manager="macos_managers",
                operation="detection",
                reason=f"Failed to detect macOS package managers: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _detect_linux_managers(
        self,
    ) -> dict[str, dict[str, str | bool | int | None]]:
        """
        Detects Linux package managers.

        Returns:
            Dict[str, Dict]: Dictionary of Linux package managers

        Raises:
            PackageManagerDetectionError: If Linux package manager detection fails
        """
        try:
            managers: dict[str, dict[str, str | bool | int | None]] = {}

            for (
                manager_name,
                metadata,
            ) in SystemDetectorConfig.get_linux_package_managers().items():
                command = metadata.get("command")
                if not isinstance(command, str):
                    logger.warning(
                        f"Invalid command value for {manager_name}: {command}"
                    )
                    continue
                # APT uses check_command_available, others use shutil.which
                availability_result = (
                    _command_runner.check_command_available(command)
                    if command == "apt"
                    else None
                )
                is_available = (
                    availability_result.is_available
                    if availability_result
                    else bool(shutil.which(command))
                )

                if is_available:
                    try:
                        result = _command_runner.run_silent([command, "--version"])
                        version = extract_version_first_line(
                            result.stdout if bool(result) else None
                        )
                    except Exception as e:
                        logger.warning(f"Failed to get {manager_name} version: {e}")
                        version = "unknown"

                    managers[manager_name] = create_package_manager_entry(
                        manager_name, version, metadata
                    )

            return managers

        except Exception as e:
            # Wrap unexpected external exceptions
            raise PkgManagerDetectionServiceError(
                package_manager="linux_managers",
                operation="detection",
                reason=f"Failed to detect Linux package managers: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def detect_development_environments(
        self,
    ) -> dict[str, dict[str, str | bool]]:
        """
        Detects development environments.

        Returns:
            Dict[str, Dict]: Dictionary of detected development environments

        Raises:
            DevelopmentEnvironmentDetectionError: If development environment detection fails
        """
        try:
            envs: dict[str, dict[str, str | bool]] = {}
            platform_name = self.system_info["platform"]

            # Editors/IDEs - filter by platform for relevance
            editor_configs = self._get_platform_editors(platform_name)
            for cmd, name in editor_configs.items():
                cmd_path = shutil.which(cmd)
                if cmd_path:
                    version = "unknown"
                    try:
                        # Use full path returned by shutil.which to handle .CMD/.BAT on Windows
                        result = _command_runner.run_silent([cmd_path, "--version"])
                        if result.returncode == 0 and result.stdout:
                            version = extract_version_first_line(result.stdout)
                        else:
                            # Log when version extraction fails
                            logger.debug(
                                f"Could not extract version for {cmd}: "
                                f"returncode={result.returncode}, stdout={bool(result.stdout)}"
                            )
                    except Exception as e:
                        logger.debug(f"Failed to get version for {cmd}: {e}")

                    envs[cmd] = create_editor_entry(cmd, name, version)

            # Shells - filter by platform for relevance
            shell_configs = self._get_platform_shells(platform_name)
            for cmd, name in shell_configs.items():
                if shutil.which(cmd):
                    version = self._get_shell_version(cmd)
                    envs[f"shell_{cmd}"] = create_shell_entry(cmd, name)
                    # Add version to shell entry if available
                    if version and version != "unknown":
                        envs[f"shell_{cmd}"]["version"] = version

            return envs

        except Exception as e:
            # Wrap unexpected external exceptions
            raise DevEnvDetectionServiceError(
                environment="all",
                operation="detection",
                reason=f"Failed to detect development environments: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _get_platform_editors(self, platform_name: str) -> dict[str, str]:
        """
        Get relevant editors for the current platform.

        Args:
            platform_name: Name of the platform (Windows, Darwin, Linux)

        Returns:
            Dict[str, str]: Platform-specific editor configurations
        """
        if platform_name == "Windows":
            # Windows: show native editors only
            return {
                "code": SystemDetectorConfig.EDITORS.get("code", "Visual Studio Code"),
            }
        elif platform_name == "Darwin":
            # macOS: show common editors
            return {
                k: v
                for k, v in SystemDetectorConfig.EDITORS.items()
                if k in ["code", "vim", "nvim", "emacs", "subl"]
            }
        else:  # Linux and others
            # Linux: show all editors
            return {
                k: v
                for k, v in SystemDetectorConfig.EDITORS.items()
                if k not in ["atom"]  # Atom is deprecated
            }

    def _get_platform_shells(self, platform_name: str) -> dict[str, str]:
        """
        Get relevant shells for the current platform.

        Args:
            platform_name: Name of the platform (Windows, Darwin, Linux)

        Returns:
            Dict[str, str]: Platform-specific shell configurations
        """
        if platform_name == "Windows":
            # Windows: show native shells only (PowerShell, not bash/zsh from Git)
            return {
                "powershell": SystemDetectorConfig.SHELLS.get(
                    "powershell", "PowerShell"
                ),
            }
        elif platform_name == "Darwin":
            # macOS: show common shells
            return {
                k: v
                for k, v in SystemDetectorConfig.SHELLS.items()
                if k in ["bash", "zsh", "fish", "powershell"]
            }
        else:  # Linux
            # Linux: show all shells
            return SystemDetectorConfig.SHELLS

    def get_best_package_manager(self) -> str | None:
        """
        Returns the best available package manager.

        Returns:
            Optional[str]: Name of the best package manager or None

        Raises:
            SystemDetectionError: If package manager selection fails
        """
        try:
            return get_best_package_manager(self.package_managers)
        except Exception as e:
            # Wrap unexpected external exceptions
            raise SystemDetectionServiceError(
                message=f"Failed to select best package manager: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _get_shell_version(self, shell: str) -> str:
        """
        Get shell version.

        Args:
            shell: Shell command name (bash, zsh, powershell, etc.)

        Returns:
            str: Version string or "unknown"
        """
        try:
            if shell == "powershell":
                # PowerShell requires special handling - use -Command with $PSVersionTable
                result = _command_runner.run_silent(
                    ["powershell", "-Command", "$PSVersionTable.PSVersion"]
                )
                if result.returncode == 0 and result.stdout:
                    # PowerShell returns table format:
                    # Major  Minor  Build  Revision
                    # -----  -----  -----  --------
                    # 5      1      26100  7462
                    lines = [
                        line.strip()
                        for line in result.stdout.strip().split("\n")
                        if line.strip()
                    ]
                    # Skip header and separator lines, get the data line
                    if len(lines) >= 3:
                        version_parts = lines[2].split()
                        if len(version_parts) >= 2:
                            # Format as "Major.Minor"
                            return f"{version_parts[0]}.{version_parts[1]}"
            else:
                # Other shells: try --version
                result = _command_runner.run_silent([shell, "--version"])
                if result.returncode == 0 and result.stdout:
                    version = extract_version_first_line(result.stdout)
                    if version and version != "unknown":
                        return version

            return "unknown"

        except Exception as e:
            logger.debug(f"Failed to get version for shell {shell}: {e}")
            return "unknown"

    def can_install_package_manager(self) -> str | None:
        """
        Checks if a package manager can be installed.

        Returns:
            Optional[str]: Name of installable package manager or None

        Raises:
            SystemDetectionError: If package manager installation check fails
        """
        try:
            if self.system_info["platform"] == "Windows" and (
                shutil.which("powershell") or shutil.which("pwsh")
            ):
                # Can install Chocolatey via PowerShell
                return "chocolatey"
            elif self.system_info["platform"] == "Darwin" and shutil.which("curl"):
                # Can install Homebrew via curl
                return "homebrew"

            return None

        except Exception as e:
            # Wrap unexpected external exceptions
            raise SystemDetectionServiceError(
                message=f"Failed to check package manager installation capability: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def export_report(self, output_path: Path | None = None) -> Path:
        """
        Generates and exports a detailed system report.

        Args:
            output_path: Optional path for the output file

        Returns:
            Path: Path to the generated report file

        Raises:
            ReportGenerationError: If report generation or export fails
        """
        try:
            # Input validation
            if output_path is not None and not isinstance(output_path, Path):
                raise ReportGenerationServiceError(
                    operation="validation",
                    reason="Output path must be a Path object",
                    details=f"Invalid output_path type: {type(output_path)}",
                )

            report = {
                "system_info": self.system_info,
                "package_managers": self.package_managers,
                "development_environments": self.dev_environments,
                "recommendations": self.get_recommendations(),
            }

            if output_path is None:
                output_path = Path.cwd() / "system_report.json"

            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
            except (PermissionError, OSError) as e:
                raise ReportGenerationServiceError(
                    operation="write",
                    reason="Cannot write report file",
                    details=f"File: {output_path} | Error: {e}",
                ) from e
            except (TypeError, ValueError) as e:
                raise ReportGenerationServiceError(
                    operation="serialization",
                    reason="Cannot serialize report data",
                    details=f"File: {output_path} | Error: {e}",
                ) from e

            return output_path

        except (ReportGenerationServiceError, SystemDetectionServiceError):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise ReportGenerationServiceError(
                operation="generation",
                reason=f"Failed to generate system report: {e}",
                details=(
                    f"File: {output_path if output_path else 'unknown'} | "
                    f"Exception type: {type(e).__name__}"
                ),
            ) from e

    def get_recommendations(self) -> dict[str, str]:
        """
        Generates recommendations based on detection.

        Returns:
            Dict[str, str]: Dictionary of recommendations

        Raises:
            SystemDetectionError: If recommendation generation fails
        """
        try:
            best_manager = self.get_best_package_manager()
            installable_manager = self.can_install_package_manager()

            return generate_recommendations(
                self.package_managers,
                self.dev_environments,
                best_manager,
                installable_manager,
            )

        except Exception as e:
            # Wrap unexpected external exceptions
            raise SystemDetectionServiceError(
                message=f"Failed to generate recommendations: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def get_system_data(self) -> dict[str, object]:
        """
        Returns complete system data without any display logic.

        Returns:
            Dict: Complete system data dictionary

        Raises:
            SystemDetectionError: If system data retrieval fails
        """
        try:
            return {
                "system_info": self.system_info,
                "package_managers": self.package_managers,
                "dev_environments": self.dev_environments,
                "recommendations": self.get_recommendations(),
            }
        except Exception as e:
            # Wrap unexpected external exceptions
            raise SystemDetectionServiceError(
                message=f"Failed to retrieve system data: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e
