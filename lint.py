#!/usr/bin/env python3
"""
Code quality check script for WOMM project.
Runs Black, isort, and Ruff on the codebase.

Usage:
    python lint.py [options]

Options:
    --check-only    Only check, don't fix
    --fix          Fix issues automatically (default)
    --verbose      Verbose output
    --help         Show this help
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List


class CodeQualityChecker:
    """Code quality checker for WOMM project."""

    def __init__(self, check_only: bool = False, verbose: bool = False):
        """Initialize the code quality checker."""
        self.check_only = check_only
        self.verbose = verbose
        self.project_root = Path(__file__).parent
        self.python_files = self._find_python_files()

    def _find_python_files(self) -> List[Path]:
        """Find all Python files in the project."""
        python_files = []

        # Directories to scan
        scan_dirs = [
            "womm",
            "tests",
            "build_package.py",
            "lint.py",
        ]

        # Directories to exclude
        exclude_dirs = {
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "build",
            "dist",
            "*.egg-info",
            ".venv",
            "venv",
            "node_modules",
            ".hooks",
        }

        for scan_dir in scan_dirs:
            scan_path = self.project_root / scan_dir
            if scan_path.is_file():
                if scan_path.suffix == ".py":
                    python_files.append(scan_path)
            elif scan_path.is_dir():
                for py_file in scan_path.rglob("*.py"):
                    # Skip excluded directories
                    if any(exclude in str(py_file) for exclude in exclude_dirs):
                        continue
                    python_files.append(py_file)

        return python_files

    def _run_command(self, command: List[str], description: str) -> bool:
        """Run a command and return success status."""
        if self.verbose:
            print(f"Running {description}...")
            print(f"   Command: {' '.join(command)}")

        try:
            result = subprocess.run(  # noqa: S603
                command,
                check=True,
                capture_output=not self.verbose,
                text=True,
                cwd=self.project_root,
            )

            if self.verbose and result.stdout:
                print(result.stdout)

            print(f"SUCCESS: {description} completed successfully")
            return True

        except subprocess.CalledProcessError as e:
            print(f"ERROR: {description} failed:")
            if e.stdout:
                print(f"STDOUT: {e.stdout}")
            if e.stderr:
                print(f"STDERR: {e.stderr}")
            return False

    def run_black(self) -> bool:
        """Run Black code formatter."""
        mode = "--check" if self.check_only else ""
        command = [
            sys.executable,
            "-m",
            "black",
            "--line-length=88",
            "--target-version=py38",
        ]

        if mode:
            command.append(mode)

        command.extend([str(f) for f in self.python_files])

        return self._run_command(command, "Black code formatting")

    def run_isort(self) -> bool:
        """Run isort import organizer."""
        mode = "--check-only" if self.check_only else ""
        command = [sys.executable, "-m", "isort", "--profile=black", "--line-length=88"]

        if mode:
            command.append(mode)

        command.extend([str(f) for f in self.python_files])

        return self._run_command(command, "isort import organization")

    def run_ruff(self) -> bool:
        """Run Ruff linter."""
        if self.check_only:
            command = [sys.executable, "-m", "ruff", "check", "--line-length=88"]
        else:
            command = [
                sys.executable,
                "-m",
                "ruff",
                "check",
                "--fix",
                "--line-length=88",
            ]

        command.extend([str(f) for f in self.python_files])

        return self._run_command(command, "Ruff linting")

    def run_ruff_format(self) -> bool:
        """Run Ruff formatter."""
        mode = "--check" if self.check_only else ""
        command = [sys.executable, "-m", "ruff", "format", "--line-length=88"]

        if mode:
            command.append(mode)

        command.extend([str(f) for f in self.python_files])

        return self._run_command(command, "Ruff formatting")

    def run_all_checks(self) -> bool:
        """Run all code quality checks."""
        print("Starting code quality checks...")
        print(f"Found {len(self.python_files)} Python files to check")
        print()

        checks = [
            ("Black", self.run_black),
            ("isort", self.run_isort),
            ("Ruff", self.run_ruff),
            ("Ruff Format", self.run_ruff_format),
        ]

        all_passed = True

        for name, check_func in checks:
            print(f"Running {name}...")
            if not check_func():
                all_passed = False
                print(f"ERROR: {name} failed")
            else:
                print(f"SUCCESS: {name} passed")
            print()

        if all_passed:
            print("SUCCESS: All code quality checks passed!")
        else:
            print("ERROR: Some code quality checks failed")
            sys.exit(1)

        return all_passed


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Code quality checker for WOMM project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python lint.py              # Fix all issues
  python lint.py --check-only # Only check, don't fix
  python lint.py --verbose    # Verbose output
        """,
    )

    parser.add_argument(
        "--check-only", action="store_true", help="Only check, don't fix issues"
    )

    parser.add_argument(
        "--fix", action="store_true", help="Fix issues automatically (default)"
    )

    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Default to fix mode unless check-only is specified
    check_only = args.check_only

    checker = CodeQualityChecker(check_only=check_only, verbose=args.verbose)
    checker.run_all_checks()


if __name__ == "__main__":
    main()
