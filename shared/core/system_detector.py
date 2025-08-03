#!/usr/bin/env python3
"""
Advanced system detector for dev-tools.
Detects OS, architecture, package managers, and development environments
"""

import json
import logging
import os
import platform
import shutil
from pathlib import Path
from typing import Dict, Optional

# Import CLI manager with proper error handling
try:
    from .cli_manager import check_tool_available, run_silent
except ImportError:
    # Fallback for direct execution
    import subprocess
    import sys
    from pathlib import Path

    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))

    try:
        from shared.core.cli_manager import check_tool_available, run_silent
    except ImportError:
        # Ultimate fallback - define basic functions
        def check_tool_available(tool_name: str) -> bool:
            """Basic tool availability check."""
            return shutil.which(tool_name) is not None

        def run_silent(command):
            """Basic command execution."""
            try:
                result = subprocess.run(  # noqa: S603
                    command, capture_output=True, text=True, timeout=30
                )
                return type(
                    "Result",
                    (),
                    {
                        "success": result.returncode == 0,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "returncode": result.returncode,
                    },
                )()
            except Exception as e:
                return type(
                    "Result",
                    (),
                    {
                        "success": False,
                        "stdout": "",
                        "stderr": str(e),
                        "returncode": -1,
                    },
                )()


class SystemDetector:
    """Complete system detector."""

    def __init__(self):
        """Initialize the system detector."""
        self.system_info = self.get_system_info()
        self.package_managers = self.detect_package_managers()
        self.dev_environments = self.detect_development_environments()

    def get_system_info(self) -> Dict:
        """Returns basic system information."""
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

    def detect_package_managers(self) -> Dict[str, Dict]:
        """Detects all available package managers."""
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

    def _detect_windows_managers(self) -> Dict[str, Dict]:
        """Detects Windows package managers."""
        managers = {}

        # Chocolatey
        if check_tool_available("choco"):
            try:
                from shared.core.cli_manager import run_silent

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
                logging.debug(f"Failed to detect Chocolatey version: {e}")

        # Winget
        if check_tool_available("winget"):
            try:
                from shared.core.cli_manager import run_silent

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
                logging.debug(f"Failed to detect Winget version: {e}")

        # Scoop
        if check_tool_available("scoop"):
            try:
                from shared.core.cli_manager import run_silent

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
                logging.debug(f"Failed to detect Scoop version: {e}")

        return managers

    def _detect_macos_managers(self) -> Dict[str, Dict]:
        """Detects macOS package managers."""
        managers = {}

        # Homebrew
        if check_tool_available("brew"):
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
                logging.debug(f"Failed to detect Homebrew version: {e}")

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
                logging.debug(f"Failed to detect MacPorts version: {e}")

        return managers

    def _detect_linux_managers(self) -> Dict[str, Dict]:
        """Detects Linux package managers."""
        managers = {}

        # APT (Debian/Ubuntu)
        if check_tool_available("apt"):
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
                logging.debug(f"Failed to detect APT version: {e}")

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
                logging.debug(f"Failed to detect DNF version: {e}")

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
                logging.debug(f"Failed to detect YUM version: {e}")

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
                logging.debug(f"Failed to detect Pacman version: {e}")

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
                logging.debug(f"Failed to detect Snap version: {e}")

        return managers

    def detect_development_environments(self) -> Dict[str, Dict]:
        """Detects development environments."""
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
                            result.stdout.split("\n")[0] if result.stdout else "unknown"
                        ),
                        "command": cmd,
                    }
                except Exception:
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

    def get_best_package_manager(self) -> Optional[str]:
        """Returns the best available package manager."""
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

    def can_install_package_manager(self) -> Optional[str]:
        """Checks if a package manager can be installed."""
        if self.system_info["platform"] == "Windows" and (
            shutil.which("powershell") or shutil.which("pwsh")
        ):
            # Can install Chocolatey via PowerShell
            return "chocolatey"
        elif self.system_info["platform"] == "Darwin" and shutil.which("curl"):
            # Can install Homebrew via curl
            return "homebrew"

        return None

    def export_report(self, output_path: Optional[Path] = None) -> Path:
        """Generates and exports a detailed system report."""
        report = {
            "system_info": self.system_info,
            "package_managers": self.package_managers,
            "development_environments": self.dev_environments,
            "recommendations": self.get_recommendations(),
        }

        if output_path is None:
            output_path = Path.cwd() / "system_report.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return output_path

    def get_recommendations(self) -> Dict[str, str]:
        """Generates recommendations based on detection."""
        recommendations = {}

        # Package manager
        best_manager = self.get_best_package_manager()
        if best_manager:
            recommendations["package_manager"] = f"Use {best_manager} for installations"
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

    def get_system_data(self) -> Dict:
        """Returns complete system data without any display logic."""
        return {
            "system_info": self.system_info,
            "package_managers": self.package_managers,
            "dev_environments": self.dev_environments,
            "recommendations": self.get_recommendations(),
        }


def main():
    """Main entry point."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="System detector for dev-tools")
    parser.add_argument("--export", help="Export report to JSON file")
    parser.add_argument("--summary", action="store_true", help="Display summary")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    detector = SystemDetector()

    if args.json:
        # Return structured data as JSON - ONLY this print, nothing else
        data = detector.get_system_data()
        print(json.dumps(data, indent=2))
    elif args.export:
        try:
            from shared.ui import print_success

            output_path = detector.export_report(Path(args.export))
            print_success(f"Report exported to: {output_path}")
        except ImportError:
            output_path = detector.export_report(Path(args.export))
            print(f"REPORT  Report exported to: {output_path}")
    elif args.summary:
        # For backward compatibility, but this should be handled by the calling command
        data = detector.get_system_data()
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
