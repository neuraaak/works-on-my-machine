#!/usr/bin/env python3
"""
Prerequisites installation manager for dev-tools.
Supports Windows (Chocolatey, Winget, Scoop), Linux (apt, yum), macOS (Homebrew).
"""

import json
import os
import platform
import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Importer le gestionnaire CLI
from shared.cli_manager import check_tool_available, run_command, run_silent


class PrerequisiteInstaller:
    """Prerequisites installation manager."""

    def __init__(self):
        """Initialize the installation manager."""
        self.system = platform.system()
        self.architecture = platform.machine()
        self.available_managers = self.detect_package_managers()

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

    def check_prerequisites(self) -> Dict[str, Dict]:
        """Check prerequisites status."""
        prerequisites = {
            "python": {
                "installed": self.check_python(),
                "required_version": "3.8+",
                "description": "Python for dev-tools scripts",
            },
            "node": {
                "installed": self.check_node(),
                "required_version": "18+",
                "description": "Node.js for CSpell and JavaScript projects",
            },
            "git": {
                "installed": self.check_git(),
                "required_version": "2.0+",
                "description": "Git for version control",
            },
        }

        return prerequisites

    def check_python(self) -> Dict:
        """Check Python installation."""
        python_cmds = ["python3", "python", "py"]

        for cmd in python_cmds:
            if shutil.which(cmd):
                try:
                    result = run_silent([cmd, "--version"])
                    version = (
                        result.stdout.strip().split()[1] if result.success else None
                    )
                    if version:
                        version_parts = [int(x) for x in version.split(".")]
                        if version_parts >= [3, 8]:
                            return {
                                "status": True,
                                "version": version,
                                "command": cmd,
                                "path": shutil.which(cmd),
                            }
                except Exception:
                    continue

        return {"status": False, "version": None, "command": None, "path": None}

    def check_node(self) -> Dict:
        """Check Node.js installation."""
        if check_tool_available("node"):
            try:
                result = run_silent(["node", "--version"])
                version = (
                    result.stdout.strip().replace("v", "")
                    if result.success and result.stdout.strip()
                    else None
                )
                version_parts = [int(x) for x in version.split(".")]

                npm_version = None
                if check_tool_available("npm"):
                    npm_result = run_silent(["npm", "--version"])
                    npm_version = (
                        npm_result.stdout.strip() if npm_result.success else None
                    )

                return {
                    "status": version_parts >= [18, 0],
                    "version": version,
                    "npm_version": npm_version,
                    "path": shutil.which("node"),
                }
            except Exception:
                pass

        return {"status": False, "version": None, "npm_version": None, "path": None}

    def check_git(self) -> Dict:
        """Check Git installation."""
        if check_tool_available("git"):
            try:
                result = run_silent(["git", "--version"])
                version = (
                    result.stdout.strip().split()[2]
                    if result.success and len(result.stdout.strip().split()) > 2
                    else None
                )
                return {"status": True, "version": version, "path": shutil.which("git")}
            except Exception:
                pass

        return {"status": False, "version": None, "path": None}

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
        print(f"🔧 Installing {manager}...")

        if manager == "chocolatey" and self.system == "Windows":
            return self.install_chocolatey()
        elif manager == "homebrew" and self.system == "Darwin":
            return self.install_homebrew()

        return False

    def install_chocolatey(self) -> bool:
        """Install Chocolatey on Windows."""
        try:
            # Official Chocolatey installation script
            install_script = """
            Set-ExecutionPolicy Bypass -Scope Process -Force
            [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
            iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
            """

            # Execute via PowerShell
            result = run_command(
                ["powershell", "-Command", install_script], "Installation Chocolatey"
            )

            # Reload available package managers
            self.available_managers = self.detect_package_managers()

            if self.available_managers.get("chocolatey"):
                print("✅ Chocolatey installed successfully")
                return True
            else:
                print("❌ Error installing Chocolatey")
                return False

        except Exception as e:
            print(f"❌ Error installing Chocolatey: {e}")
            return False

    def install_homebrew(self) -> bool:
        """Install Homebrew on macOS."""
        try:
            # Official Homebrew installation script
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
                print("✅ Homebrew installed successfully")
                return True
            else:
                print("❌ Error installing Homebrew")
                return False

        except Exception as e:
            print(f"❌ Error during installation: {e}")
            return False

    def install_prerequisite(
        self, prereq: str, custom_path: Optional[str] = None
    ) -> bool:
        """Install a specific prerequisite."""
        manager = self.get_best_package_manager()

        if not manager:
            print(f"❌ No package manager available to install {prereq}")
            return self.install_manually(prereq, custom_path)

        print(f"📦 Installing {prereq} via {manager}...")

        # Installation commands by package manager
        install_commands = {
            "chocolatey": {
                "python": ["choco", "install", "python", "-y"],
                "node": ["choco", "install", "nodejs", "-y"],
                "npm": ["choco", "install", "nodejs", "-y"],  # npm comes with nodejs
                "git": ["choco", "install", "git", "-y"],
            },
            "winget": {
                "python": ["winget", "install", "Python.Python.3.12"],
                "node": ["winget", "install", "OpenJS.NodeJS"],
                "npm": ["winget", "install", "OpenJS.NodeJS"],  # npm comes with nodejs
                "git": ["winget", "install", "Git.Git"],
            },
            "scoop": {
                "python": ["scoop", "install", "python"],
                "node": ["scoop", "install", "nodejs"],
                "npm": ["scoop", "install", "nodejs"],  # npm comes with nodejs
                "git": ["scoop", "install", "git"],
            },
            "homebrew": {
                "python": ["brew", "install", "python@3.12"],
                "node": ["brew", "install", "node"],
                "npm": ["brew", "install", "node"],  # npm comes with nodejs
                "git": ["brew", "install", "git"],
            },
            "apt": {
                "python": [
                    "sudo",
                    "apt",
                    "update",
                    "&&",
                    "sudo",
                    "apt",
                    "install",
                    "-y",
                    "python3",
                    "python3-pip",
                ],
                "node": [
                    "sudo",
                    "apt",
                    "update",
                    "&&",
                    "sudo",
                    "apt",
                    "install",
                    "-y",
                    "nodejs",
                    "npm",
                ],
                "npm": [
                    "sudo",
                    "apt",
                    "update",
                    "&&",
                    "sudo",
                    "apt",
                    "install",
                    "-y",
                    "npm",
                ],
                "git": [
                    "sudo",
                    "apt",
                    "update",
                    "&&",
                    "sudo",
                    "apt",
                    "install",
                    "-y",
                    "git",
                ],
            },
        }

        if manager in install_commands and prereq in install_commands[manager]:
            try:
                cmd = install_commands[manager][prereq]
                result = run_command(cmd, f"Installation {prereq} via {manager}")
                if not result.success:
                    raise Exception(f"Failed to install {prereq}")
                print(f"✅ {prereq} installed successfully")
                return True
            except Exception as e:
                print(f"❌ Error installing {prereq}: {e}")
                return False
        else:
            return self.install_manually(prereq, custom_path)

    def install_manually(self, prereq: str, custom_path: Optional[str] = None) -> bool:
        """Manual installation via direct download."""
        print(f"🔽 Manual installation of {prereq}...")

        if prereq == "python":
            return self.install_python_manually(custom_path)
        elif prereq == "node":
            return self.install_node_manually(custom_path)
        elif prereq == "npm":
            return self.install_node_manually(custom_path)  # npm comes with nodejs
        elif prereq == "git":
            return self.install_git_manually(custom_path)

        return False

    def install_python_manually(self, custom_path: Optional[str] = None) -> bool:
        """Manual installation of Python."""
        if self.system == "Windows":
            # Python URL for Windows
            python_url = (
                "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
            )
            installer_path = Path(tempfile.gettempdir()) / "python_installer.exe"

            try:
                print("📥 Downloading Python...")
                urllib.request.urlretrieve(python_url, installer_path)

                # Silent installation
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
                if not result.success:
                    raise Exception("Python installation failed")
                print("✅ Python installed successfully")
                return True

            except Exception as e:
                print(f"❌ Error during manual installation: {e}")
                return False
            finally:
                if installer_path.exists():
                    installer_path.unlink()

        return False

    def install_node_manually(self, custom_path: Optional[str] = None) -> bool:
        """Manual installation of Node.js."""
        if self.system == "Windows":
            # Node.js URL for Windows
            node_url = "https://nodejs.org/dist/v20.9.0/node-v20.9.0-x64.msi"
            installer_path = Path(tempfile.gettempdir()) / "node_installer.msi"

            try:
                print("📥 Downloading Node.js...")
                urllib.request.urlretrieve(node_url, installer_path)

                # Silent installation
                install_cmd = ["msiexec", "/i", str(installer_path), "/quiet"]

                result = run_command(install_cmd, "Manual Node.js installation")
                if not result.success:
                    raise Exception("Node.js installation failed")
                print("✅ Node.js installed successfully")
                return True

            except Exception as e:
                print(f"❌ Error during manual installation: {e}")
                return False
            finally:
                if installer_path.exists():
                    installer_path.unlink()

        return False

    def install_git_manually(self, custom_path: Optional[str] = None) -> bool:
        """Manual installation of Git."""
        if self.system == "Windows":
            # Git URL for Windows
            git_url = "https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe"
            installer_path = Path(tempfile.gettempdir()) / "git_installer.exe"

            try:
                print("📥 Downloading Git...")
                urllib.request.urlretrieve(git_url, installer_path)

                # Silent installation
                install_cmd = [str(installer_path), "/SILENT"]

                result = run_command(install_cmd, "Manual Git installation")
                if not result.success:
                    raise Exception("Git installation failed")
                print("✅ Git installed successfully")
                return True

            except Exception as e:
                print(f"❌ Error during manual installation: {e}")
                return False
            finally:
                if installer_path.exists():
                    installer_path.unlink()

        return False

    def prompt_installation(self) -> Tuple[bool, List[str], Optional[str]]:
        """Prompt user for installation."""
        prerequisites = self.check_prerequisites()
        missing = [
            name
            for name, info in prerequisites.items()
            if not info["installed"]["status"]
        ]

        if not missing:
            print("✅ All prerequisites are installed!")
            return True, [], None

        print("\n🔍 Checking prerequisites...")
        print("=" * 50)

        for name, info in prerequisites.items():
            status = info["installed"]
            if status["status"]:
                print(f"✅ {name.upper()}: {status['version']} - {status['path']}")
            else:
                print(f"❌ {name.upper()}: Not installed - {info['description']}")

        print(f"\n⚠️  Missing prerequisites: {', '.join(missing)}")

        # Main prompt
        response = input(
            "\n🤔 Do you want to install missing prerequisites? (y/N): "
        ).lower()
        if response not in ["o", "oui", "y", "yes"]:
            return False, missing, None

        # Package manager choice if multiple available
        available = [
            name for name, available in self.available_managers.items() if available
        ]
        if len(available) > 1:
            print(f"\n📦 Available package managers: {', '.join(available)}")
            manager_choice = input(
                "Choose a package manager (or Enter for automatic): "
            ).lower()
            if manager_choice in available:
                # TODO: Use chosen package manager
                pass

        # Custom installation path
        custom_path = None
        if self.system == "Windows":
            path_response = input(
                "\n📁 Custom installation path? (Enter for default): "
            ).strip()
            if path_response:
                custom_path = path_response

        return True, missing, custom_path

    def install_missing_prerequisites(
        self, missing: List[str], custom_path: Optional[str] = None
    ) -> bool:
        """Install missing prerequisites."""
        success_count = 0

        # Offer to install a package manager if none available
        if not self.get_best_package_manager():
            if self.system == "Windows":
                install_choco = input(
                    "\n🍫 Install Chocolatey to make installations easier? (y/N): "
                ).lower()
                if install_choco in ["o", "oui", "y", "yes"]:
                    if self.install_package_manager("chocolatey"):
                        print(
                            "✅ Chocolatey installed - future installations will be faster"
                        )
            elif self.system == "Darwin":
                install_brew = input(
                    "\n🍺 Install Homebrew to make installations easier? (y/N): "
                ).lower()
                if install_brew in ["o", "oui", "y", "yes"]:
                    if self.install_package_manager("homebrew"):
                        print(
                            "✅ Homebrew installed - future installations will be faster"
                        )

        for prereq in missing:
            print(f"\n📦 Installing {prereq}...")
            if self.install_prerequisite(prereq, custom_path):
                success_count += 1
            else:
                print(f"❌ Failed to install {prereq}")

        if success_count == len(missing):
            print("\n🎉 All prerequisites have been installed successfully!")
            print("🔄 Restart your terminal to use the new tools")
            return True
        else:
            print(f"\n⚠️  {success_count}/{len(missing)} prerequisites installed")
            return False


def main():
    """Run the main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Dev-tools prerequisites installation manager"
    )
    parser.add_argument("--check", action="store_true", help="Only check prerequisites")
    parser.add_argument(
        "--install",
        nargs="*",
        choices=["python", "node", "git", "npm", "all"],
        help="Install specific prerequisites",
    )
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--path", help="Custom installation path")

    args = parser.parse_args()

    installer = PrerequisiteInstaller()

    if args.check:
        prerequisites = installer.check_prerequisites()
        for name, info in prerequisites.items():
            status = info["installed"]
            if status["status"]:
                print(f"✅ {name}: {status['version']}")
            else:
                print(f"❌ {name}: Not installed")
        return

    if args.install:
        to_install = (
            args.install if "all" not in args.install else ["python", "node", "git", "npm"]
        )
        for prereq in to_install:
            installer.install_prerequisite(prereq, args.path)
        return

    # Mode par défaut ou interactif
    should_install, missing, custom_path = installer.prompt_installation()

    if should_install and missing:
        installer.install_missing_prerequisites(missing, custom_path or args.path)
    elif not missing:
        print("✅ All prerequisites are already installed!")
    else:
        print("⏭️  Installation cancelled by user")


if __name__ == "__main__":
    main()
