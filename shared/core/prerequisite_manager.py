#!/usr/bin/env python3
"""
Prerequisite Manager for Works On My Machine.
Handles installation and checking of system prerequisites.
Unified module combining simple API with advanced features.
"""

import logging
import platform
import shutil
import tempfile
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .cli_manager import check_tool_available, run_command, run_silent


class PrerequisiteManager:
    """Unified system prerequisites manager with advanced features."""

    def __init__(self):
        """Initialize the prerequisite manager."""
        self.logger = self._setup_logging()
        self.system = platform.system()
        self.architecture = platform.machine()
        self.available_managers = self.detect_package_managers()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for prerequisite operations."""
        logger = logging.getLogger("prerequisite_manager")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def detect_package_managers(self) -> Dict[str, bool]:
        """Detect available package managers."""
        managers = {}

        if self.system == "Windows":
            managers["chocolatey"] = shutil.which("choco") is not None
            managers["winget"] = shutil.which("winget") is not None
            managers["scoop"] = shutil.which("scoop") is not None
        elif self.system == "Darwin":  # macOS
            managers["homebrew"] = shutil.which("brew") is not None
            managers["macports"] = shutil.which("port") is not None
        elif self.system == "Linux":
            managers["apt"] = shutil.which("apt") is not None
            managers["yum"] = shutil.which("yum") is not None
            managers["dnf"] = shutil.which("dnf") is not None
            managers["pacman"] = shutil.which("pacman") is not None
            managers["snap"] = shutil.which("snap") is not None

        return managers

    def check_tool(self, tool_name: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a tool is available.

        Args:
            tool_name: Name of the tool to check

        Returns:
            Tuple of (is_available, version_or_error)
        """
        if tool_name == "python":
            return self._check_python()
        elif tool_name == "node":
            return self._check_node()
        elif tool_name == "git":
            return self._check_git()
        elif tool_name == "npm":
            return self._check_npm()
        else:
            if check_tool_available(tool_name):
                version = self._get_tool_version(tool_name)
                return True, version
            return False, None

    def _check_python(self) -> Tuple[bool, Optional[str]]:
        """Check Python installation with version validation."""
        python_cmds = ["python3", "python", "py"]

        for cmd in python_cmds:
            if shutil.which(cmd):
                try:
                    result = run_silent([cmd, "--version"])
                    if result.success and result.stdout.strip():
                        version = result.stdout.strip().split()[1]
                        version_parts = [int(x) for x in version.split(".")]
                        if version_parts >= [3, 8]:
                            return True, version
                except Exception as e:
                    self.logger.debug(f"Failed to check Python version with {cmd}: {e}")
                    continue

        return False, None

    def _check_node(self) -> Tuple[bool, Optional[str]]:
        """Check Node.js installation with version validation."""
        if check_tool_available("node"):
            try:
                result = run_silent(["node", "--version"])
                if result.success and result.stdout.strip():
                    version = result.stdout.strip().replace("v", "")
                    version_parts = [int(x) for x in version.split(".")]
                    if version_parts >= [18, 0]:
                        return True, version
            except Exception as e:
                self.logger.debug(f"Failed to check Node.js version: {e}")

        return False, None

    def _check_git(self) -> Tuple[bool, Optional[str]]:
        """Check Git installation."""
        if check_tool_available("git"):
            try:
                result = run_silent(["git", "--version"])
                if result.success and result.stdout.strip():
                    version = result.stdout.strip().split()[2]
                    return True, version
            except Exception as e:
                self.logger.debug(f"Failed to check Git version: {e}")

        return False, None

    def _check_npm(self) -> Tuple[bool, Optional[str]]:
        """Check npm installation."""
        if check_tool_available("npm"):
            try:
                result = run_silent(["npm", "--version"])
                if result.success and result.stdout.strip():
                    version = result.stdout.strip()
                    return True, version
            except Exception as e:
                self.logger.debug(f"Failed to check npm version: {e}")

        return False, None

    def _get_tool_version(self, tool_name: str) -> Optional[str]:
        """Get version of a tool."""
        version_flags = {
            "python": "--version",
            "node": "--version",
            "npm": "--version",
            "git": "--version",
        }

        flag = version_flags.get(tool_name, "--version")
        result = run_silent([tool_name, flag])

        if result.success and result.stdout.strip():
            return result.stdout.strip().split("\n")[0]
        return None

    def check_prerequisites(self, tools: List[str]) -> Dict[str, Dict]:
        """
        Check multiple prerequisites.

        Args:
            tools: List of tool names to check

        Returns:
            Dictionary with tool status information
        """
        results = {}

        for tool in tools:
            is_available, version = self.check_tool(tool)
            results[tool] = {
                "available": is_available,
                "version": version,
                "status": "installed" if is_available else "missing"
            }

        return results

    def get_best_package_manager(self) -> Optional[str]:
        """Return the best available package manager."""
        if self.system == "Windows":
            if self.available_managers.get("chocolatey"):
                return "chocolatey"
            elif self.available_managers.get("winget"):
                return "winget"
            elif self.available_managers.get("scoop"):
                return "scoop"
        elif self.system == "Darwin":
            if self.available_managers.get("homebrew"):
                return "homebrew"
        elif self.system == "Linux":
            if self.available_managers.get("apt"):
                return "apt"
            elif self.available_managers.get("dnf"):
                return "dnf"
            elif self.available_managers.get("yum"):
                return "yum"
            elif self.available_managers.get("pacman"):
                return "pacman"

        return None

    def install_package_manager(self, manager: str) -> bool:
        """Install a package manager if possible."""
        self.logger.info(f"Installing {manager}...")

        if manager == "chocolatey" and self.system == "Windows":
            return self._install_chocolatey()
        elif manager == "homebrew" and self.system == "Darwin":
            return self._install_homebrew()

        return False

    def _install_chocolatey(self) -> bool:
        """Install Chocolatey on Windows."""
        try:
            install_script = """
            Set-ExecutionPolicy Bypass -Scope Process -Force
            [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
            iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
            """

            run_command(
                ["powershell", "-Command", install_script],
                "Installation Chocolatey"
            )

            # Reload available package managers
            self.available_managers = self.detect_package_managers()

            if self.available_managers.get("chocolatey"):
                self.logger.info("Chocolatey installed successfully")
                return True
            else:
                self.logger.error("Failed to install Chocolatey")
                return False

        except Exception as e:
            self.logger.error(f"Error installing Chocolatey: {e}")
            return False

    def _install_homebrew(self) -> bool:
        """Install Homebrew on macOS."""
        try:
            install_cmd = [
                "/bin/bash",
                "-c",
                "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)",
            ]

            result = run_command(install_cmd, "Installation Homebrew")
            if not result.success:
                raise Exception("Homebrew installation failed")

            # Reload available package managers
            self.available_managers = self.detect_package_managers()

            if self.available_managers.get("homebrew"):
                self.logger.info("Homebrew installed successfully")
                return True
            else:
                self.logger.error("Failed to install Homebrew")
                return False

        except Exception as e:
            self.logger.error(f"Error installing Homebrew: {e}")
            return False

    def install_tool(self, tool_name: str, custom_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Install a specific tool.

        Args:
            tool_name: Name of the tool to install
            interactive: Whether to run in interactive mode
            custom_path: Custom installation path

        Returns:
            Tuple of (success, message)
        """
        self.logger.info(f"Installing {tool_name}...")

        # Get installation method for the tool
        install_method = self._get_install_method(tool_name)
        if not install_method:
            # Try manual installation
            return self._install_manually(tool_name, custom_path)

        # Execute installation
        try:
            result = run_silent(install_method["command"], install_method.get("description", f"Installing {tool_name}"))

            if result.success:
                self.logger.info(f"Successfully installed {tool_name}")
                return True, f"{tool_name} installed successfully"
            else:
                error_msg = result.stderr or "Unknown error"
                self.logger.error(f"Failed to install {tool_name}: {error_msg}")
                # Fallback to manual installation
                return self._install_manually(tool_name, custom_path)

        except Exception as e:
            error_msg = f"Exception during {tool_name} installation: {e}"
            self.logger.error(error_msg)
            # Fallback to manual installation
            return self._install_manually(tool_name, custom_path)

    def _get_install_method(self, tool_name: str) -> Optional[Dict]:
        """Get installation method for a tool based on platform."""
        manager = self.get_best_package_manager()
        if not manager:
            return None

        # Platform-specific installation methods
        install_methods = {
            "chocolatey": {
                "python": {
                    "command": ["choco", "install", "python", "-y"],
                    "description": "Installing Python via Chocolatey"
                },
                "node": {
                    "command": ["choco", "install", "nodejs", "-y"],
                    "description": "Installing Node.js via Chocolatey"
                },
                "git": {
                    "command": ["choco", "install", "git", "-y"],
                    "description": "Installing Git via Chocolatey"
                }
            },
            "winget": {
                "python": {
                    "command": ["winget", "install", "Python.Python.3.12"],
                    "description": "Installing Python via winget"
                },
                "node": {
                    "command": ["winget", "install", "OpenJS.NodeJS"],
                    "description": "Installing Node.js via winget"
                },
                "git": {
                    "command": ["winget", "install", "Git.Git"],
                    "description": "Installing Git via winget"
                }
            },
            "homebrew": {
                "python": {
                    "command": ["brew", "install", "python@3.12"],
                    "description": "Installing Python via Homebrew"
                },
                "node": {
                    "command": ["brew", "install", "node"],
                    "description": "Installing Node.js via Homebrew"
                },
                "git": {
                    "command": ["brew", "install", "git"],
                    "description": "Installing Git via Homebrew"
                }
            },
            "apt": {
                "python": {
                    "command": ["sudo", "apt", "update", "&&", "sudo", "apt", "install", "-y", "python3", "python3-pip"],
                    "description": "Installing Python via apt"
                },
                "node": {
                    "command": ["sudo", "apt", "update", "&&", "sudo", "apt", "install", "-y", "nodejs", "npm"],
                    "description": "Installing Node.js via apt"
                },
                "git": {
                    "command": ["sudo", "apt", "update", "&&", "sudo", "apt", "install", "-y", "git"],
                    "description": "Installing Git via apt"
                }
            }
        }

        if manager in install_methods and tool_name in install_methods[manager]:
            return install_methods[manager][tool_name]

        return None

    def _install_manually(self, tool_name: str, custom_path: Optional[str] = None) -> Tuple[bool, str]:
        """Manual installation via direct download."""
        self.logger.info(f"Manual installation of {tool_name}...")

        if tool_name == "python":
            return self._install_python_manually(custom_path)
        elif tool_name == "node":
            return self._install_node_manually(custom_path)
        elif tool_name == "git":
            return self._install_git_manually(custom_path)

        return False, f"No manual installation method available for {tool_name}"

    def _install_python_manually(self, custom_path: Optional[str] = None) -> Tuple[bool, str]:
        """Manual installation of Python."""
        if self.system == "Windows":
            python_url = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
            installer_path = Path(tempfile.gettempdir()) / "python_installer.exe"

            try:
                self.logger.info("Downloading Python...")
                urllib.request.urlretrieve(python_url, installer_path)  # noqa: S310

                install_cmd = [
                    str(installer_path),
                    "/quiet",
                    "InstallAllUsers=1",
                    "PrependPath=1",
                    "Include_test=0",
                ]

                if custom_path:
                    install_cmd.append(f"TargetDir={custom_path}")

                result = run_command(install_cmd, "Manual Python installation")
                if result.success:
                    return True, "Python installed successfully"
                else:
                    return False, "Python installation failed"

            except Exception as e:
                return False, f"Error during manual installation: {e}"
            finally:
                if installer_path.exists():
                    installer_path.unlink()

        return False, "Manual Python installation not supported on this platform"

    def _install_node_manually(self, _custom_path: Optional[str] = None) -> Tuple[bool, str]:
        """Manual installation of Node.js."""
        if self.system == "Windows":
            node_url = "https://nodejs.org/dist/v20.9.0/node-v20.9.0-x64.msi"
            installer_path = Path(tempfile.gettempdir()) / "node_installer.msi"

            try:
                self.logger.info("Downloading Node.js...")
                urllib.request.urlretrieve(node_url, installer_path)  # noqa: S310

                install_cmd = ["msiexec", "/i", str(installer_path), "/quiet"]
                result = run_command(install_cmd, "Manual Node.js installation")

                if result.success:
                    return True, "Node.js installed successfully"
                else:
                    return False, "Node.js installation failed"

            except Exception as e:
                return False, f"Error during manual installation: {e}"
            finally:
                if installer_path.exists():
                    installer_path.unlink()

        return False, "Manual Node.js installation not supported on this platform"

    def _install_git_manually(self, _custom_path: Optional[str] = None) -> Tuple[bool, str]:
        """Manual installation of Git."""
        if self.system == "Windows":
            git_url = "https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe"
            installer_path = Path(tempfile.gettempdir()) / "git_installer.exe"

            try:
                self.logger.info("Downloading Git...")
                urllib.request.urlretrieve(git_url, installer_path)  # noqa: S310

                install_cmd = [str(installer_path), "/SILENT"]
                result = run_command(install_cmd, "Manual Git installation")

                if result.success:
                    return True, "Git installed successfully"
                else:
                    return False, "Git installation failed"

            except Exception as e:
                return False, f"Error during manual installation: {e}"
            finally:
                if installer_path.exists():
                    installer_path.unlink()

        return False, "Manual Git installation not supported on this platform"

    def install_prerequisites(self, tools: List[str], interactive: bool = False, custom_path: Optional[str] = None) -> Dict[str, Dict]:
        """
        Install multiple prerequisites.

        Args:
            tools: List of tool names to install
            interactive: Whether to run in interactive mode
            custom_path: Custom installation path

        Returns:
            Dictionary with installation results
        """
        results = {}

        for tool in tools:
            success, message = self.install_tool(tool, interactive, custom_path)
            results[tool] = {
                "success": success,
                "message": message,
                "status": "installed" if success else "failed"
            }

        return results

    def get_installation_status(self, tools: List[str]) -> Dict[str, Dict]:
        """
        Get comprehensive status of tools (check + install if needed).

        Args:
            tools: List of tool names to check/install

        Returns:
            Dictionary with comprehensive status information
        """
        # First check what's already available
        check_results = self.check_prerequisites(tools)

        # Identify missing tools
        missing_tools = [tool for tool, info in check_results.items() if not info["available"]]

        # Install missing tools
        if missing_tools:
            install_results = self.install_prerequisites(missing_tools)

            # Update check results with installation results
            for tool, install_info in install_results.items():
                if install_info["success"]:
                    # Re-check the tool after installation
                    is_available, version = self.check_tool(tool)
                    check_results[tool] = {
                        "available": is_available,
                        "version": version,
                        "status": "installed" if is_available else "failed",
                        "installed": True
                    }
                else:
                    check_results[tool]["installed"] = False
                    check_results[tool]["error"] = install_info["message"]

        return check_results

    def setup_npm_path(self) -> bool:
        """Set up npm global PATH for CSpell and other npm tools."""
        self.logger.info("Setting up npm global PATH...")

        try:
            # Get npm prefix (where global packages are installed)
            result = run_silent(["npm", "config", "get", "prefix"])
            if not result.success:
                self.logger.warning("Could not get npm prefix")
                return False

            npm_prefix = result.stdout.strip()
            npm_bin_path = Path(npm_prefix)

            # Check if npm bin path is already in PATH
            result = run_silent(["reg", "query", "HKCU\\Environment", "/v", "PATH"])
            if result.returncode == 0:
                output = result.stdout.decode("utf-8", errors="ignore")
                for line in output.split("\n"):
                    if "PATH" in line and "REG_EXPAND_SZ" in line:
                        current_path = line.split("REG_EXPAND_SZ")[1].strip()
                        break
                else:
                    current_path = ""
            else:
                current_path = ""

            # Check if npm path is already in PATH
            if str(npm_bin_path) not in current_path:
                # Add npm path to PATH
                new_path = f"{npm_bin_path};{current_path}" if current_path else str(npm_bin_path)

                try:
                    result = run_command(
                        [
                            "reg",
                            "add",
                            "HKCU\\Environment",
                            "/v",
                            "PATH",
                            "/t",
                            "REG_EXPAND_SZ",
                            "/d",
                            new_path,
                            "/f",
                        ],
                        "Setting npm PATH",
                        capture_output=True,
                        text=True,
                    )

                    if result.success:
                        self.logger.info("npm global PATH updated successfully")
                        return True
                    else:
                        self.logger.warning("Failed to update npm PATH automatically")
                        return False
                except Exception as e:
                    self.logger.error(f"Error updating npm PATH: {e}")
                    return False
            else:
                self.logger.info("npm global PATH already configured")
                return True

        except Exception as e:
            self.logger.error(f"Error setting up npm PATH: {e}")
            return False


# Global instance for simple usage
prerequisite_manager = PrerequisiteManager()


def check_prerequisites(tools: List[str]) -> Dict[str, Dict]:
    """Check prerequisites using global instance."""
    return prerequisite_manager.check_prerequisites(tools)


def install_prerequisites(tools: List[str], interactive: bool = False, custom_path: Optional[str] = None) -> Dict[str, Dict]:
    """Install prerequisites using global instance."""
    return prerequisite_manager.install_prerequisites(tools, interactive, custom_path)


def get_installation_status(tools: List[str]) -> Dict[str, Dict]:
    """Get comprehensive installation status using global instance."""
    return prerequisite_manager.get_installation_status(tools)


def install_package_manager(manager: str) -> bool:
    """Install a package manager using global instance."""
    return prerequisite_manager.install_package_manager(manager)


def setup_npm_path() -> bool:
    """Setup npm PATH using global instance."""
    return prerequisite_manager.setup_npm_path()
