#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM DETECTOR - System Detection Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Advanced system detector for dev-tools.
Detects OS, architecture, package managers, and development environments
"""

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
from ...exceptions.system import (
    DevelopmentEnvironmentDetectionError,
    PackageManagerDetectionError,
    ReportGenerationError,
    SystemDetectionError,
    SystemInfoError,
)
from ..cli_utils import CLIUtils, run_silent

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)


# ///////////////////////////////////////////////////////////////
# SYSTEM DETECTOR CLASS
# ///////////////////////////////////////////////////////////////


class SystemDetector:
    """Complete system detector."""

    def __init__(self) -> None:
        """Initialize the system detector."""
        try:
            self.system_info = self.get_system_info()
            self.package_managers = self.detect_package_managers()
            self.dev_environments = self.detect_development_environments()
        except (
            SystemDetectionError,
            SystemInfoError,
            PackageManagerDetectionError,
            DevelopmentEnvironmentDetectionError,
        ):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise SystemDetectionError(
                message=f"Failed to initialize system detector: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def get_system_info(self) -> dict[str, str | bool | int]:
        """
        Returns basic system information.

        Returns:
            Dict: System information dictionary

        Raises:
            SystemInfoError: If system information gathering fails
        """
        try:
            return {
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "python_implementation": platform.python_implementation(),
                "node": platform.node(),
                "user": os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
                "home": str(Path.home()),
                "shell": os.environ.get("SHELL", "unknown"),
                "terminal": os.environ.get("TERM", "unknown"),
                "path_separator": os.pathsep,
                "line_separator": os.linesep,
            }
        except Exception as e:
            # Wrap unexpected external exceptions
            raise SystemInfoError(
                operation="platform_info",
                reason=f"Failed to gather system information: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def detect_package_managers(self) -> dict[str, dict[str, str | bool]]:
        """
        Detects all available package managers.

        Returns:
            Dict[str, Dict]: Dictionary of detected package managers

        Raises:
            PackageManagerDetectionError: If package manager detection fails
        """
        try:
            managers = {}

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

        except (PackageManagerDetectionError, SystemInfoError):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise PackageManagerDetectionError(
                package_manager="all",
                operation="detection",
                reason=f"Failed to detect package managers: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _detect_windows_managers(self) -> dict[str, dict[str, str | bool]]:
        """
        Detects Windows package managers.

        Returns:
            Dict[str, Dict]: Dictionary of Windows package managers

        Raises:
            PackageManagerDetectionError: If Windows package manager detection fails
        """
        try:
            managers = {}

            # Chocolatey
            if CLIUtils().check_command_available("choco"):
                try:
                    result = run_silent(["choco", "--version"])
                    managers["chocolatey"] = {
                        "available": True,
                        "version": result.stdout.strip() if result.success else None,
                        "command": "choco",
                        "description": "Community package manager",
                        "install_cmd": "choco install",
                        "priority": 1,
                    }
                except Exception as e:
                    logger.warning(f"Failed to get Chocolatey version: {e}")
                    managers["chocolatey"] = {
                        "available": True,
                        "version": "unknown",
                        "command": "choco",
                        "description": "Community package manager",
                        "install_cmd": "choco install",
                        "priority": 1,
                    }

            # Winget
            if CLIUtils().check_command_available("winget"):
                try:
                    result = run_silent(["winget", "--version"])
                    managers["winget"] = {
                        "available": True,
                        "version": result.stdout.strip() if result.success else None,
                        "command": "winget",
                        "description": "Official Microsoft package manager",
                        "install_cmd": "winget install",
                        "priority": 2,
                    }
                except Exception as e:
                    logger.warning(f"Failed to get Winget version: {e}")
                    managers["winget"] = {
                        "available": True,
                        "version": "unknown",
                        "command": "winget",
                        "description": "Official Microsoft package manager",
                        "install_cmd": "winget install",
                        "priority": 2,
                    }

            # Scoop
            if CLIUtils().check_command_available("scoop"):
                try:
                    result = run_silent(["scoop", "--version"])
                    managers["scoop"] = {
                        "available": True,
                        "version": result.stdout.strip() if result.success else None,
                        "command": "scoop",
                        "description": "Package manager for developers",
                        "install_cmd": "scoop install",
                        "priority": 3,
                    }
                except Exception as e:
                    logger.warning(f"Failed to get Scoop version: {e}")
                    managers["scoop"] = {
                        "available": True,
                        "version": "unknown",
                        "command": "scoop",
                        "description": "Package manager for developers",
                        "install_cmd": "scoop install",
                        "priority": 3,
                    }

            return managers

        except Exception as e:
            # Wrap unexpected external exceptions
            raise PackageManagerDetectionError(
                package_manager="windows_managers",
                operation="detection",
                reason=f"Failed to detect Windows package managers: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _detect_macos_managers(self) -> dict[str, dict[str, str | bool]]:
        """
        Detects macOS package managers.

        Returns:
            Dict[str, Dict]: Dictionary of macOS package managers

        Raises:
            PackageManagerDetectionError: If macOS package manager detection fails
        """
        try:
            managers = {}

            # Homebrew
            if CLIUtils().check_command_available("brew"):
                try:
                    result = run_silent(["brew", "--version"])
                    version = result.stdout.split("\n")[0]
                    managers["homebrew"] = {
                        "available": True,
                        "version": version,
                        "command": "brew",
                        "description": "Main package manager for macOS",
                        "install_cmd": "brew install",
                        "priority": 1,
                    }
                except Exception as e:
                    logger.warning(f"Failed to get Homebrew version: {e}")
                    managers["homebrew"] = {
                        "available": True,
                        "version": "unknown",
                        "command": "brew",
                        "description": "Main package manager for macOS",
                        "install_cmd": "brew install",
                        "priority": 1,
                    }

            # MacPorts
            if shutil.which("port"):
                try:
                    result = run_silent(["port", "version"])
                    managers["macports"] = {
                        "available": True,
                        "version": result.stdout.strip() if result.success else None,
                        "command": "port",
                        "description": "Alternative package manager",
                        "install_cmd": "sudo port install",
                        "priority": 2,
                    }
                except Exception as e:
                    logger.warning(f"Failed to get MacPorts version: {e}")
                    managers["macports"] = {
                        "available": True,
                        "version": "unknown",
                        "command": "port",
                        "description": "Alternative package manager",
                        "install_cmd": "sudo port install",
                        "priority": 2,
                    }

            return managers

        except Exception as e:
            # Wrap unexpected external exceptions
            raise PackageManagerDetectionError(
                package_manager="macos_managers",
                operation="detection",
                reason=f"Failed to detect macOS package managers: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _detect_linux_managers(self) -> dict[str, dict[str, str | bool]]:
        """
        Detects Linux package managers.

        Returns:
            Dict[str, Dict]: Dictionary of Linux package managers

        Raises:
            PackageManagerDetectionError: If Linux package manager detection fails
        """
        try:
            managers = {}

            # APT (Debian/Ubuntu)
            if CLIUtils().check_command_available("apt"):
                try:
                    result = run_silent(["apt", "--version"])
                    managers["apt"] = {
                        "available": True,
                        "version": result.stdout.split("\n")[0],
                        "command": "apt",
                        "description": "Debian/Ubuntu package manager",
                        "install_cmd": "sudo apt install",
                        "priority": 1,
                    }
                except Exception as e:
                    logger.warning(f"Failed to get APT version: {e}")
                    managers["apt"] = {
                        "available": True,
                        "version": "unknown",
                        "command": "apt",
                        "description": "Debian/Ubuntu package manager",
                        "install_cmd": "sudo apt install",
                        "priority": 1,
                    }

            # DNF (Fedora)
            if shutil.which("dnf"):
                try:
                    result = run_silent(["dnf", "--version"])
                    managers["dnf"] = {
                        "available": True,
                        "version": result.stdout.split("\n")[0],
                        "command": "dnf",
                        "description": "Fedora/RHEL package manager",
                        "install_cmd": "sudo dnf install",
                        "priority": 1,
                    }
                except Exception as e:
                    logger.warning(f"Failed to get DNF version: {e}")
                    managers["dnf"] = {
                        "available": True,
                        "version": "unknown",
                        "command": "dnf",
                        "description": "Fedora/RHEL package manager",
                        "install_cmd": "sudo dnf install",
                        "priority": 1,
                    }

            # YUM (CentOS/RHEL)
            if shutil.which("yum"):
                try:
                    result = run_silent(["yum", "--version"])
                    managers["yum"] = {
                        "available": True,
                        "version": result.stdout.split("\n")[0],
                        "command": "yum",
                        "description": "CentOS/RHEL package manager",
                        "install_cmd": "sudo yum install",
                        "priority": 2,
                    }
                except Exception as e:
                    logger.warning(f"Failed to get YUM version: {e}")
                    managers["yum"] = {
                        "available": True,
                        "version": "unknown",
                        "command": "yum",
                        "description": "CentOS/RHEL package manager",
                        "install_cmd": "sudo yum install",
                        "priority": 2,
                    }

            # Pacman (Arch)
            if shutil.which("pacman"):
                try:
                    result = run_silent(["pacman", "--version"])
                    managers["pacman"] = {
                        "available": True,
                        "version": result.stdout.split("\n")[0],
                        "command": "pacman",
                        "description": "Arch Linux package manager",
                        "install_cmd": "sudo pacman -S",
                        "priority": 1,
                    }
                except Exception as e:
                    logger.warning(f"Failed to get Pacman version: {e}")
                    managers["pacman"] = {
                        "available": True,
                        "version": "unknown",
                        "command": "pacman",
                        "description": "Arch Linux package manager",
                        "install_cmd": "sudo pacman -S",
                        "priority": 1,
                    }

            # Snap
            if shutil.which("snap"):
                try:
                    result = run_silent(["snap", "--version"])
                    managers["snap"] = {
                        "available": True,
                        "version": result.stdout.split("\n")[0],
                        "command": "snap",
                        "description": "Universal Ubuntu package manager",
                        "install_cmd": "sudo snap install",
                        "priority": 3,
                    }
                except Exception as e:
                    logger.warning(f"Failed to get Snap version: {e}")
                    managers["snap"] = {
                        "available": True,
                        "version": "unknown",
                        "command": "snap",
                        "description": "Universal Ubuntu package manager",
                        "install_cmd": "sudo snap install",
                        "priority": 3,
                    }

            return managers

        except Exception as e:
            # Wrap unexpected external exceptions
            raise PackageManagerDetectionError(
                package_manager="linux_managers",
                operation="detection",
                reason=f"Failed to detect Linux package managers: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def detect_development_environments(self) -> dict[str, dict[str, str | bool]]:
        """
        Detects development environments.

        Returns:
            Dict[str, Dict]: Dictionary of detected development environments

        Raises:
            DevelopmentEnvironmentDetectionError: If development environment detection fails
        """
        try:
            envs = {}

            # Editors/IDEs
            editors = {
                "code": "Visual Studio Code",
                "code-insiders": "VS Code Insiders",
                "subl": "Sublime Text",
                "atom": "Atom",
                "vim": "Vim",
                "nvim": "Neovim",
                "emacs": "Emacs",
                "nano": "Nano",
            }

            for cmd, name in editors.items():
                if shutil.which(cmd):
                    try:
                        result = run_silent([cmd, "--version"])
                        envs[cmd] = {
                            "available": True,
                            "name": name,
                            "version": (
                                result.stdout.split("\n")[0]
                                if result.stdout
                                else "unknown"
                            ),
                            "command": cmd,
                        }
                    except Exception as e:
                        logger.warning(f"Failed to get {cmd} version: {e}")
                        envs[cmd] = {
                            "available": True,
                            "name": name,
                            "version": "unknown",
                            "command": cmd,
                        }

            # Shells
            shells = {
                "bash": "Bash",
                "zsh": "Zsh",
                "fish": "Fish",
                "powershell": "PowerShell",
                "pwsh": "PowerShell Core",
            }

            for cmd, name in shells.items():
                if shutil.which(cmd):
                    envs[f"shell_{cmd}"] = {
                        "available": True,
                        "name": name,
                        "command": cmd,
                        "type": "shell",
                    }

            return envs

        except Exception as e:
            # Wrap unexpected external exceptions
            raise DevelopmentEnvironmentDetectionError(
                environment="all",
                operation="detection",
                reason=f"Failed to detect development environments: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def get_best_package_manager(self) -> str | None:
        """
        Returns the best available package manager.

        Returns:
            Optional[str]: Name of the best package manager or None

        Raises:
            SystemDetectionError: If package manager selection fails
        """
        try:
            available = {
                name: info
                for name, info in self.package_managers.items()
                if info["available"]
            }

            if not available:
                return None

            # Sort by priority
            sorted_managers = sorted(available.items(), key=lambda x: x[1]["priority"])
            return sorted_managers[0][0]

        except Exception as e:
            # Wrap unexpected external exceptions
            raise SystemDetectionError(
                message=f"Failed to select best package manager: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

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
            raise SystemDetectionError(
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
                raise ReportGenerationError(
                    operation="validation",
                    file_path=str(output_path),
                    reason="Output path must be a Path object",
                    details="Invalid output_path type provided",
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
                raise ReportGenerationError(
                    operation="write",
                    file_path=str(output_path),
                    reason="Cannot write report file",
                    details=f"Error: {e}",
                ) from e
            except (TypeError, ValueError) as e:
                raise ReportGenerationError(
                    operation="serialization",
                    file_path=str(output_path),
                    reason="Cannot serialize report data",
                    details=f"Error: {e}",
                ) from e

            return output_path

        except (ReportGenerationError, SystemDetectionError):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise ReportGenerationError(
                operation="generation",
                file_path=str(output_path) if output_path else "unknown",
                reason=f"Failed to generate system report: {e}",
                details=f"Exception type: {type(e).__name__}",
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
            recommendations = {}

            # Package manager
            best_manager = self.get_best_package_manager()
            if best_manager:
                recommendations["package_manager"] = (
                    f"Use {best_manager} for installations"
                )
            else:
                installable = self.can_install_package_manager()
                if installable:
                    recommendations["package_manager"] = (
                        f"Install {installable} to facilitate installations"
                    )
                else:
                    recommendations["package_manager"] = (
                        "No package manager detected - manual installation required"
                    )

            # Recommended editor
            if "code" in self.dev_environments:
                recommendations["editor"] = (
                    "VS Code detected - excellent choice for dev-tools"
                )
            elif any("vim" in env or "nvim" in env for env in self.dev_environments):
                recommendations["editor"] = (
                    "Command line editor detected - dev-tools compatible"
                )
            else:
                recommendations["editor"] = (
                    "Install VS Code recommended for better integration"
                )

            return recommendations

        except Exception as e:
            # Wrap unexpected external exceptions
            raise SystemDetectionError(
                message=f"Failed to generate recommendations: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def get_system_data(self) -> dict[str, str | bool | int | dict[str, str | bool]]:
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
            raise SystemDetectionError(
                message=f"Failed to retrieve system data: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e
