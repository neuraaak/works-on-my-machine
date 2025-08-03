#!/usr/bin/env python3
"""
Dependency Manager for WOMM CLI.
Handles recursive dependency checking and installation.
"""

import platform
import sys
from pathlib import Path
from typing import Dict, List, Optional

import click

from .core.cli_manager import check_tool_available, run_command, run_silent
from .core.results import (
    DependencyCheckResult,
    InstallationResult,
    create_dependency_check_error,
    create_dependency_check_success,
)


class DependencyManager:
    """Manages dependencies with recursive installation capability."""

    def __init__(self):
        """Initialize dependency manager."""
        self._cache = {}  # Cache for dependency checks
        self.system = platform.system()
        self._package_managers = self._detect_package_managers()

    def _detect_package_managers(self) -> Dict[str, bool]:
        """Detect available package managers."""
        managers = {
            "chocolatey": False,
            "winget": False,
            "scoop": False,
            "apt": False,
            "yum": False,
            "brew": False,
        }

        # Check Windows package managers
        if self.system == "Windows":
            managers["chocolatey"] = self._check_command("choco")
            managers["winget"] = self._check_command("winget")
            managers["scoop"] = self._check_command("scoop")
        # Check Linux package managers
        elif self.system == "Linux":
            managers["apt"] = self._check_command("apt")
            managers["yum"] = self._check_command("yum")
        # Check macOS package managers
        elif self.system == "Darwin":
            managers["brew"] = self._check_command("brew")

        return managers

    def _check_command(self, command: str) -> bool:
        """Check if a command is available."""
        # Use CLI manager command checking
        if not check_tool_available(command):
            return False

        # Use silent execution to check version
        result = run_silent([command, "--version"])
        return result.success

    def check_with_cache(self, dependency: str) -> bool:
        """Check dependency with caching."""
        if dependency not in self._cache:
            self._cache[dependency] = self._check_dependency(dependency)
        return self._cache[dependency]

    def _check_dependency(self, dependency: str) -> bool:
        """Check if a specific dependency is installed."""
        check_methods = {
            "python": self._check_python,
            "node": self._check_node,
            "npm": self._check_npm,
            "git": self._check_git,
            "cspell": self._check_cspell,
            "package_manager": self._check_package_manager,
        }

        if dependency in check_methods:
            return check_methods[dependency]()
        else:
            return self._check_command(dependency)

    def _check_python(self) -> bool:
        """Check if Python is installed."""
        # Use silent execution with sys.executable (full path)
        result = run_silent([sys.executable, "--version"])
        return result.success

    def _check_node(self) -> bool:
        """Check if Node.js is installed."""
        return self._check_command("node")

    def _check_npm(self) -> bool:
        """Check if npm is installed."""
        # npm usually comes with Node.js, so check both
        if self._check_command("npm"):
            return True

        # If npm not found but node is available, try to get npm version
        if self._check_command("node"):
            # Use silent execution to check npm via node
            result = run_silent(
                [
                    "node",
                    "-e",
                    "console.log(require('child_process').execSync('npm --version', {encoding: 'utf8'}))",
                ]
            )
            return result.success

        return False

    def _check_git(self) -> bool:
        """Check if Git is installed."""
        return self._check_command("git")

    def _check_cspell(self) -> bool:
        """Check if CSpell is installed (global or local)."""
        # Check global installation
        if self._check_command("cspell"):
            return True

        # Check local installation in current project
        result = run_silent(["npx", "cspell", "--version"])
        return result.success

    def _check_package_manager(self) -> bool:
        """Check if any package manager is available."""
        return any(self._package_managers.values())

    def get_available_package_manager(self) -> Optional[str]:
        """Get the best available package manager."""
        if self.system == "Windows":
            # Prefer winget (official Microsoft), then chocolatey, then scoop
            if self._package_managers["winget"]:
                return "winget"
            elif self._package_managers["chocolatey"]:
                return "chocolatey"
            elif self._package_managers["scoop"]:
                return "scoop"
        elif self.system == "Linux":
            if self._package_managers["apt"]:
                return "apt"
            elif self._package_managers["yum"]:
                return "yum"
        elif self.system == "Darwin" and self._package_managers["brew"]:
            return "brew"
        return None

    def check_and_install_recursive(self, dependencies: List[str]) -> bool:
        """Check and install dependencies recursively."""
        click.echo(f"🔍 Checking dependencies: {', '.join(dependencies)}")

        for dependency in dependencies:
            if not self._install_dependency_recursive(dependency):
                return False

        return True

    def check_dependencies(self, dependencies: List[str]) -> DependencyCheckResult:
        """Check if dependencies are available and return structured result."""
        available = []
        missing = []

        for dependency in dependencies:
            if self.check_with_cache(dependency):
                available.append(dependency)
            else:
                missing.append(dependency)

        if not missing:
            return create_dependency_check_success(available)
        else:
            return create_dependency_check_error(
                f"Missing dependencies: {', '.join(missing)}",
                available=available,
                missing=missing,
            )

    def install_dependencies(self, dependencies: List[str]) -> InstallationResult:
        """Install dependencies and return structured result."""
        installed = []
        failed = []
        skipped = []

        for dependency in dependencies:
            if self.check_with_cache(dependency):
                skipped.append(dependency)
                continue

            if self._install_dependency_recursive(dependency):
                installed.append(dependency)
            else:
                failed.append(dependency)

        if not failed:
            return InstallationResult(
                success=True,
                message=f"Successfully installed {len(installed)} dependencies",
                installed=installed,
                skipped=skipped,
                failed=failed,
            )
        else:
            return InstallationResult(
                success=False,
                error=f"Failed to install: {', '.join(failed)}",
                installed=installed,
                skipped=skipped,
                failed=failed,
            )

    def _install_dependency_recursive(self, dependency: str) -> bool:
        """Install a dependency and its prerequisites recursively."""
        if self.check_with_cache(dependency):
            click.echo(f"✅ {dependency} is already installed")
            return True

        click.echo(f"❌ {dependency} is not installed")

        # Get installation method for this dependency
        install_method = self._get_installation_method(dependency)
        if not install_method:
            click.echo(f"❌ No installation method available for {dependency}")
            return False

        # Check prerequisites for this installation method
        prerequisites = self._get_prerequisites(install_method)
        for prereq in prerequisites:
            if not self._install_dependency_recursive(prereq):
                return False

        # Install the dependency
        return self._install_dependency(dependency, install_method)

    def _get_installation_method(self, dependency: str) -> Optional[str]:
        """Get the installation method for a dependency."""
        methods = {
            "python": "package_manager",
            "node": "package_manager",
            "npm": "node",  # npm comes with node
            "git": "package_manager",
            "cspell": "npm",
            "package_manager": "manual",  # Package manager needs manual installation
        }

        return methods.get(dependency, "package_manager")

    def _get_prerequisites(self, method: str) -> List[str]:
        """Get prerequisites for an installation method."""
        prereqs = {
            "package_manager": ["package_manager"],
            "npm": ["node"],
            "node": ["package_manager"],
            "manual": [],
        }
        return prereqs.get(method, [])

    def _install_dependency(self, dependency: str, method: str) -> bool:
        """Install a dependency using the specified method."""
        click.echo(f"📦 Installing {dependency} using {method}...")

        if method == "package_manager":
            return self._install_via_package_manager(dependency)
        elif method == "npm":
            return self._install_via_npm(dependency)
        elif method == "manual":
            return self._install_package_manager_manual()
        else:
            click.echo(f"❌ Unknown installation method: {method}")
            return False

    def _install_via_package_manager(self, dependency: str) -> bool:
        """Install dependency via package manager."""
        package_manager = self.get_available_package_manager()
        if not package_manager:
            click.echo("❌ No package manager available")
            return False

        # Get package name for the dependency
        package_name = self._get_package_name(dependency, package_manager)
        if not package_name:
            click.echo(f"❌ No package found for {dependency} in {package_manager}")
            return False

        # Build installation command
        if package_manager == "winget":
            cmd = ["winget", "install", package_name, "--accept-source-agreements"]
        elif package_manager == "chocolatey":
            cmd = ["choco", "install", package_name, "-y"]
        elif package_manager == "scoop":
            cmd = ["scoop", "install", package_name]
        elif package_manager == "apt":
            cmd = [
                "sudo",
                "apt",
                "update",
                "&&",
                "sudo",
                "apt",
                "install",
                "-y",
                package_name,
            ]
        elif package_manager == "yum":
            cmd = ["sudo", "yum", "install", "-y", package_name]
        elif package_manager == "brew":
            cmd = ["brew", "install", package_name]
        else:
            click.echo(f"❌ Unsupported package manager: {package_manager}")
            return False

        # Execute installation
        try:
            click.echo(f"🔄 Installing {dependency} via {package_manager}...")
            result = run_command(cmd, f"Installing {dependency}")

            if result.success:
                click.echo(f"✅ {dependency} installed successfully")

                # Add dependency to PATH if needed
                self._add_dependency_to_path(dependency, package_manager)

                # Clear cache for this dependency
                self._cache.pop(dependency, None)
                return True
            else:
                click.echo(f"❌ Failed to install {dependency}: {result.stderr}")
                return False
        except Exception as e:
            click.echo(f"❌ Error installing {dependency}: {e}")
            return False

    def _install_via_npm(self, dependency: str) -> bool:
        """Install dependency via npm."""
        try:
            click.echo(f"🔄 Installing {dependency} via npm...")
            cmd = ["npm", "install", "-g", dependency]
            result = run_command(cmd, f"Installing {dependency} globally")

            if result.success:
                click.echo(f"✅ {dependency} installed successfully")

                # Add npm global bin to PATH if needed
                self._add_npm_to_path()

                self._cache.pop(dependency, None)
                return True
            else:
                click.echo(f"❌ Failed to install {dependency}: {result.stderr}")
                return False
        except Exception as e:
            click.echo(f"❌ Error installing {dependency}: {e}")
            return False

    def _install_package_manager_manual(self) -> bool:
        """Guide user to install a package manager manually."""
        if self.system == "Windows":
            click.echo(
                "📦 No package manager found. Please install one of the following:"
            )
            click.echo(
                "  1. Winget (recommended): https://docs.microsoft.com/en-us/windows/package-manager/winget/"
            )
            click.echo("  2. Chocolatey: https://chocolatey.org/install")
            click.echo("  3. Scoop: https://scoop.sh/")
        elif self.system == "Linux":
            click.echo("📦 Package manager should be available by default.")
        elif self.system == "Darwin":
            click.echo("📦 Please install Homebrew: https://brew.sh/")

        response = input(
            "Press Enter after installing a package manager, or 'q' to quit: "
        )
        if response.lower() == "q":
            return False

        # Refresh package manager detection
        self._package_managers = self._detect_package_managers()
        return self._check_package_manager()

    def _get_package_name(self, dependency: str, package_manager: str) -> Optional[str]:
        """Get the package name for a dependency in a specific package manager."""
        packages = {
            "python": {
                "winget": "Python.Python.3.11",
                "chocolatey": "python",
                "scoop": "python",
                "apt": "python3",
                "yum": "python3",
                "brew": "python@3.11",
            },
            "node": {
                "winget": "OpenJS.NodeJS",
                "chocolatey": "nodejs",
                "scoop": "nodejs",
                "apt": "nodejs",
                "yum": "nodejs",
                "brew": "node",
            },
            "git": {
                "winget": "Git.Git",
                "chocolatey": "git",
                "scoop": "git",
                "apt": "git",
                "yum": "git",
                "brew": "git",
            },
        }

        return packages.get(dependency, {}).get(package_manager)

    def _add_dependency_to_path(self, dependency: str, package_manager: str) -> None:
        """Add dependency to PATH if needed."""
        # Most package managers handle PATH automatically
        # Only special cases need manual PATH addition
        if dependency == "node" and package_manager in ["winget", "chocolatey"]:
            # Node.js might need PATH addition on Windows
            click.echo("🔄 Node.js installed - PATH should be updated automatically")
        elif dependency == "python" and package_manager in ["winget", "chocolatey"]:
            # Python might need PATH addition on Windows
            click.echo("🔄 Python installed - PATH should be updated automatically")

    def _add_npm_to_path(self) -> None:
        """Add npm global bin directory to PATH."""
        if self.system != "Windows":
            return  # Unix systems usually handle this automatically

        # Get npm prefix (where global packages are installed)
        result = run_silent(["npm", "config", "get", "prefix"])

        if result.success:
            npm_prefix = result.stdout.strip()
            npm_bin_path = Path(npm_prefix)

            # Check if npm bin path is already in USER PATH
            current_path = self._get_current_user_path()

            if str(npm_bin_path) not in current_path:
                # Add npm path to USER PATH
                new_path = (
                    f"{current_path};{npm_bin_path}"
                    if current_path
                    else str(npm_bin_path)
                )

                path_result = run_command(
                    ["setx", "PATH", new_path],
                    "Adding npm global bin to USER PATH",
                    capture_output=True,
                    text=True,
                )

                if path_result.success:
                    click.echo("✅ npm global bin added to USER PATH")
                    click.echo("🔄 Restart your terminal to use npm global tools")
                else:
                    click.echo("⚠️  Failed to add npm to PATH automatically")
                    click.echo(
                        f'💡 You can add it manually: setx PATH "%PATH%;{npm_bin_path}"'
                    )
            else:
                click.echo("✅ npm global bin already in PATH")
        else:
            click.echo("⚠️  Could not get npm prefix")

    def _get_current_user_path(self) -> str:
        """Get current USER PATH from Windows registry."""
        result = run_silent(["reg", "query", "HKCU\\Environment", "/v", "PATH"])

        if result.success:
            for line in result.stdout.split("\n"):
                if "PATH" in line and "REG_EXPAND_SZ" in line:
                    return line.split("REG_EXPAND_SZ")[1].strip()
        else:
            click.echo("⚠️  Warning: Could not read Windows PATH")

        return ""


# Global instance for easy access
dependency_manager = DependencyManager()


def check_and_install_dependencies(dependencies: List[str]) -> bool:
    """Convenience function to check and install dependencies."""
    return dependency_manager.check_and_install_recursive(dependencies)
