#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEPENDENCY HIERARCHY - Dependency Chain Configuration
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Dependency hierarchy and relationships for WOMM.

Defines the 3-strata dependency model with 4 distinct concepts:

Strata 1: system_package_manager
    Platform-level package managers (winget, chocolatey, homebrew, apt)

Strata 2: runtime + runtime_package_manager
    - runtime: Language interpreters (python, node, git)
    - runtime_package_manager: Bundled or standalone pkg managers (pip, uv, npm, yarn)

Strata 3: devtools_dependencies
    Development utilities (cspell, ruff, eslint, pytest)
"""

from __future__ import annotations

from typing import ClassVar

# ///////////////////////////////////////////////////////////////
# DEPENDENCY HIERARCHY
# ///////////////////////////////////////////////////////////////


class DependenciesHierarchy:
    """
    WOMM 3-Strata Dependency Model with 4 Concepts

    Strata 1: system_package_manager
        OS-level installers that can install runtimes
        Examples: winget, chocolatey, homebrew, apt

    Strata 2a: runtime
        Language interpreters and core executables
        Come with bundled runtime_package_managers
        Examples: python, node, git

    Strata 2b: runtime_package_manager
        Language-specific package managers (pip, uv, npm, yarn)
        May be bundled with runtime or installed separately

    Strata 3: devtools_dependencies
        Development tools that require runtime_package_managers
        Examples: cspell, ruff, eslint, pytest

    Installation Order:
    ===================

        system_package_manager (Strata 1)
            ↓
        runtime (Strata 2a)
            ↓ (bundled with)
        runtime_package_manager (Strata 2b)
            ↓
        devtools_dependencies (Strata 3)

    Example Chain:
    ==============

        To install cspell:
        cspell → npm → node → winget

        To install ruff:
        ruff → pip → python → winget
    """

    # ///////////////////////////////////////////////////////////
    # STRATA DEFINITIONS
    # ///////////////////////////////////////////////////////////

    STRATA: ClassVar[dict[int, dict[str, str | list[str]]]] = {
        1: {
            "name": "system_package_manager",
            "description": "Platform-level package managers",
            "examples": ["winget", "chocolatey", "homebrew", "apt", "dnf"],
        },
        2: {
            "name": "runtime",
            "description": "Language interpreters with bundled package managers",
            "examples": ["python", "node", "git"],
            "note": "Each runtime includes a default runtime_package_manager",
        },
        3: {
            "name": "devtools_dependencies",
            "description": "Development and project utilities",
            "examples": ["cspell", "ruff", "eslint", "pytest"],
        },
    }

    STRATA_NAMES: ClassVar[dict[str, int]] = {
        "system_package_manager": 1,
        "runtime": 2,
        "runtime_package_manager": 2,  # Part of Strata 2
        "devtools_dependencies": 3,
    }

    # ///////////////////////////////////////////////////////////
    # RUNTIME PACKAGE MANAGERS (Strata 2b)
    # ///////////////////////////////////////////////////////////

    RUNTIME_PACKAGE_MANAGERS: ClassVar[dict[str, dict[str, str | bool | list[str]]]] = {
        "pip": {
            "runtime": "python",
            "bundled": True,
            "alternatives": ["uv", "poetry", "pipenv"],
        },
        "uv": {
            "runtime": "python",
            "bundled": False,
            "install_method": "pip",
        },
        "npm": {
            "runtime": "node",
            "bundled": True,
            "alternatives": ["yarn", "pnpm"],
        },
        "yarn": {
            "runtime": "node",
            "bundled": False,
            "install_method": "npm",
        },
        "pnpm": {
            "runtime": "node",
            "bundled": False,
            "install_method": "npm",
        },
    }

    # ///////////////////////////////////////////////////////////
    # DEVTOOLS DEPENDENCIES (Strata 3 → Strata 2b → Strata 2a)
    # ///////////////////////////////////////////////////////////

    DEVTOOLS_DEPENDENCIES: ClassVar[dict[str, dict[str, str]]] = {
        # -------------------------------------------------------
        # Python DevTools (require pip + python)
        # -------------------------------------------------------
        "black": {
            "runtime_package_manager": "pip",
            "runtime": "python",
        },
        "isort": {
            "runtime_package_manager": "pip",
            "runtime": "python",
        },
        "ruff": {
            "runtime_package_manager": "pip",
            "runtime": "python",
        },
        "flake8": {
            "runtime_package_manager": "pip",
            "runtime": "python",
        },
        "bandit": {
            "runtime_package_manager": "pip",
            "runtime": "python",
        },
        "pytest": {
            "runtime_package_manager": "pip",
            "runtime": "python",
        },
        "mypy": {
            "runtime_package_manager": "pip",
            "runtime": "python",
        },
        "pre-commit": {
            "runtime_package_manager": "pip",
            "runtime": "python",
        },
        # -------------------------------------------------------
        # JavaScript DevTools (require npm + node)
        # -------------------------------------------------------
        "prettier": {
            "runtime_package_manager": "npm",
            "runtime": "node",
        },
        "eslint": {
            "runtime_package_manager": "npm",
            "runtime": "node",
        },
        "jest": {
            "runtime_package_manager": "npm",
            "runtime": "node",
        },
        "webpack": {
            "runtime_package_manager": "npm",
            "runtime": "node",
        },
        "vite": {
            "runtime_package_manager": "npm",
            "runtime": "node",
        },
        "cspell": {
            "runtime_package_manager": "npm",
            "runtime": "node",
            "check_method": "npx",  # Can be checked via npx without global install
        },
    }

    # ///////////////////////////////////////////////////////////
    # RUNTIME INSTALLATION (Strata 2a → Strata 1)
    # ///////////////////////////////////////////////////////////

    RUNTIME_INSTALLERS: ClassVar[dict[str, list[str]]] = {
        "python": ["winget", "chocolatey", "scoop", "homebrew", "apt", "dnf", "pacman"],
        "node": ["winget", "chocolatey", "scoop", "homebrew", "apt", "dnf", "pacman"],
        "git": ["winget", "chocolatey", "scoop", "homebrew", "apt", "dnf", "pacman"],
    }

    # ///////////////////////////////////////////////////////////
    # SYSTEM PACKAGE MANAGER AVAILABILITY (Strata 1 → Platform)
    # ///////////////////////////////////////////////////////////

    SYSTEM_PACKAGE_MANAGER_PLATFORMS: ClassVar[dict[str, list[str]]] = {
        "winget": ["windows"],
        "chocolatey": ["windows"],
        "scoop": ["windows"],
        "homebrew": ["darwin"],
        "apt": ["linux"],
        "dnf": ["linux"],
        "pacman": ["linux"],
        "zypper": ["linux"],
    }

    # ///////////////////////////////////////////////////////////
    # HELPER METHODS
    # ///////////////////////////////////////////////////////////

    @classmethod
    def get_devtool_chain(cls, devtool: str) -> dict[str, str | None]:
        """
        Get the complete dependency chain for a devtool.

        Args:
            devtool: Name of the development tool

        Returns:
            Dictionary with runtime, runtime_package_manager, and optional check_method

        Example:
            >>> get_devtool_chain("cspell")
            {
                "devtool": "cspell",
                "runtime_package_manager": "npm",
                "runtime": "node",
                "check_method": "npx"
            }
        """
        if devtool not in cls.DEVTOOLS_DEPENDENCIES:
            return {
                "devtool": devtool,
                "runtime_package_manager": None,
                "runtime": None,
            }

        chain_data = cls.DEVTOOLS_DEPENDENCIES[devtool]
        chain: dict[str, str | None] = {
            "devtool": devtool,
            "runtime_package_manager": chain_data.get("runtime_package_manager"),
            "runtime": chain_data.get("runtime"),
        }
        if "check_method" in chain_data:
            chain["check_method"] = chain_data["check_method"]
        return chain

    @classmethod
    def get_runtime_from_package_manager(
        cls, runtime_package_manager: str
    ) -> str | None:
        """
        Get the runtime required by a runtime_package_manager.

        Args:
            runtime_package_manager: Name of the runtime package manager

        Returns:
            Runtime name or None

        Example:
            >>> get_runtime_from_package_manager("npm")
            "node"
        """
        pkg_info = cls.RUNTIME_PACKAGE_MANAGERS.get(runtime_package_manager)
        if pkg_info:
            runtime = pkg_info.get("runtime")
            if isinstance(runtime, str):
                return runtime
        return None

    @classmethod
    def is_bundled_package_manager(cls, runtime_package_manager: str) -> bool:
        """
        Check if a runtime_package_manager is bundled with its runtime.

        Args:
            runtime_package_manager: Name of the package manager

        Returns:
            True if bundled (pip, npm), False if separate (uv, yarn)
        """
        pkg_info = cls.RUNTIME_PACKAGE_MANAGERS.get(runtime_package_manager, {})
        bundled = pkg_info.get("bundled", False)
        return isinstance(bundled, bool) and bundled

    @classmethod
    def get_package_manager_alternatives(
        cls, runtime_package_manager: str
    ) -> list[str]:
        """
        Get alternative runtime_package_managers for the same runtime.

        Args:
            runtime_package_manager: Name of the package manager

        Returns:
            List of alternative package managers

        Example:
            >>> get_package_manager_alternatives("pip")
            ["uv", "poetry", "pipenv"]
        """
        pkg_info = cls.RUNTIME_PACKAGE_MANAGERS.get(runtime_package_manager, {})
        alternatives = pkg_info.get("alternatives", [])
        if isinstance(alternatives, list):
            return alternatives
        return []

    @classmethod
    def get_runtime_installers(cls, runtime: str) -> list[str]:
        """
        Get system_package_managers that can install a runtime.

        Args:
            runtime: Name of the runtime (python, node, git)

        Returns:
            List of system_package_manager names
        """
        return cls.RUNTIME_INSTALLERS.get(runtime, [])

    @classmethod
    def get_available_system_package_managers(cls, platform: str) -> list[str]:
        """
        Get system_package_managers available on a platform.

        Args:
            platform: Platform name (windows, darwin, linux)

        Returns:
            List of system_package_manager names available on this platform
        """
        available = []
        for manager, platforms in cls.SYSTEM_PACKAGE_MANAGER_PLATFORMS.items():
            if platform in platforms:
                available.append(manager)
        return available

    @classmethod
    def get_full_chain(cls, devtool: str) -> list[tuple[int, str]]:
        """
        Get the complete installation chain as a sorted list of strata.

        Returns a list of (strata, name) tuples in installation order.

        Args:
            devtool: Name of the development tool

        Returns:
            List of (strata_number, component_name) tuples, sorted by strata

        Example:
            >>> get_full_chain("cspell")
            [(2, "node"), (2, "npm"), (3, "cspell")]

            >>> get_full_chain("ruff")
            [(2, "python"), (2, "pip"), (3, "ruff")]
        """
        chain = cls.get_devtool_chain(devtool)

        result: list[tuple[int, str]] = []

        # Add runtime (Strata 2a) if present
        runtime = chain.get("runtime")
        if runtime:
            result.append((2, runtime))

        # Add runtime_package_manager (Strata 2b) if present
        pkg_manager = chain.get("runtime_package_manager")
        if pkg_manager:
            result.append((2, pkg_manager))

        # Add devtool (Strata 3)
        result.append((3, devtool))

        return sorted(result, key=lambda x: x[0])

    @classmethod
    def validate_installation_order(
        cls, items: list[tuple[int, str]]
    ) -> list[tuple[int, str]]:
        """
        Sort items by strata to ensure proper installation order.

        This ensures that dependencies are installed before dependents:
        - Strata 1 (system_package_managers) first
        - Strata 2 (runtimes + runtime_package_managers) second
        - Strata 3 (devtools_dependencies) last

        Args:
            items: List of (strata, name) tuples

        Returns:
            Sorted list respecting hierarchy (Strata 1 → 2 → 3)

        Example:
            >>> items = [(3, "cspell"), (2, "node"), (2, "npm")]
            >>> validate_installation_order(items)
            [(2, "node"), (2, "npm"), (3, "cspell")]
        """
        return sorted(items, key=lambda x: x[0])

    @classmethod
    def get_strata_name(cls, strata_number: int) -> str | None:
        """
        Get the descriptive name for a strata number.

        Args:
            strata_number: Strata number (1, 2, or 3)

        Returns:
            Strata name or None if invalid strata number

        Example:
            >>> get_strata_name(1)
            "system_package_manager"

            >>> get_strata_name(2)
            "runtime"
        """
        strata_info = cls.STRATA.get(strata_number)
        if strata_info:
            name = strata_info.get("name")
            if isinstance(name, str):
                return name
        return None

    @classmethod
    def get_strata_number(cls, strata_name: str) -> int | None:
        """
        Get the strata number for a descriptive name.

        Args:
            strata_name: Strata name ("system_package_manager", "runtime", "runtime_package_manager", "devtools_dependencies")

        Returns:
            Strata number or None if invalid strata name

        Example:
            >>> get_strata_number("runtime")
            2

            >>> get_strata_number("devtools_dependencies")
            3
        """
        return cls.STRATA_NAMES.get(strata_name)

    @classmethod
    def validate_devtool_installation(
        cls,
        devtool: str,
        available_system_managers: list[str],
        installed_runtimes: list[str],
        installed_runtime_pkg_managers: list[str],
    ) -> dict[str, bool | list[str]]:
        """
        Validate if a devtool can be installed given current system state.

        Args:
            devtool: DevTool to install
            available_system_managers: system_package_managers available on platform
            installed_runtimes: Runtimes currently installed
            installed_runtime_pkg_managers: runtime_package_managers currently available

        Returns:
            Dictionary with:
                - can_install: bool
                - missing: list of missing dependencies
                - installation_path: step-by-step installation guide
        """
        chain = cls.get_devtool_chain(devtool)
        if not chain.get("runtime_package_manager"):
            return {
                "can_install": False,
                "missing": ["unknown_devtool"],
                "installation_path": [],
            }

        missing = []
        installation_path = []

        required_pkg_manager = chain.get("runtime_package_manager")
        required_runtime = chain.get("runtime")

        # Ensure we have valid values
        if not required_pkg_manager or not required_runtime:
            return {
                "can_install": False,
                "missing": ["invalid_chain"],
                "installation_path": [],
            }

        # Check Strata 2b: runtime_package_manager
        if required_pkg_manager not in installed_runtime_pkg_managers:
            missing.append(f"runtime_package_manager:{required_pkg_manager}")

            # Check if it's bundled or needs separate installation
            if cls.is_bundled_package_manager(required_pkg_manager):
                # Bundled → check runtime
                if required_runtime not in installed_runtimes:
                    missing.append(f"runtime:{required_runtime}")

                    # Check Strata 1: system_package_manager
                    runtime_installers = cls.get_runtime_installers(required_runtime)
                    has_installer = any(
                        inst in available_system_managers for inst in runtime_installers
                    )
                    if not has_installer:
                        missing.append(
                            f"system_package_manager:any_of_{runtime_installers}"
                        )
                    else:
                        installation_path.append(
                            f"1. Install {required_runtime} via system_package_manager"
                        )
                        installation_path.append(
                            f"2. {required_pkg_manager} will be bundled automatically"
                        )
            else:
                # Not bundled → need to install separately
                pkg_info = cls.RUNTIME_PACKAGE_MANAGERS.get(required_pkg_manager, {})
                install_method = pkg_info.get("install_method")
                if install_method and isinstance(install_method, str):
                    installation_path.append(
                        f"1. Install {required_pkg_manager} via {install_method}"
                    )

        installation_path.append(
            f"{'1' if not installation_path else len(installation_path) + 1}. Install {devtool} via {required_pkg_manager}"
        )

        return {
            "can_install": len(missing) == 0,
            "missing": missing,
            "installation_path": installation_path,
        }


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["DependenciesHierarchy"]
