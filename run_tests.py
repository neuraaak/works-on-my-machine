#!/usr/bin/env python3
"""
Test runner script for Works On My Machine.

This script provides a unified interface to run all types of tests
with different options and configurations.

Usage:
    python run_tests.py [options] [test_paths...]

Options:
    --unit              Run unit tests only
    --integration       Run integration tests only
    --security          Run security tests only
    --coverage          Generate coverage report
    --fast              Fast tests (exclude slow tests)
    --parallel          Run tests in parallel
    --debug             Debug mode with more details
    --check-deps        Check test dependencies
    --summary           Display test summary
    --help              Show this help
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List


class TestRunner:
    """Test execution manager for Works On My Machine."""

    def __init__(self):
        """Initialize the test manager."""
        self.project_root = Path(__file__).parent
        self.tests_dir = self.project_root / "tests"
        self.unit_dir = self.tests_dir / "unit"
        self.integration_dir = self.tests_dir / "integration"

        # Check that pytest is available
        self.pytest_available = self._check_pytest()

    def _check_pytest(self) -> bool:
        """Check if pytest is available."""
        try:
            # Use a secure command list - pytest is a trusted dependency
            cmd = [sys.executable, "-m", "pytest", "--version"]
            subprocess.run(
                cmd, capture_output=True, check=True, timeout=10
            )  # noqa: S603
            return True
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            return False

    def _check_dependencies(self) -> bool:
        """Check test dependencies."""
        print("🔍 Checking test dependencies...")

        # Whitelist of allowed dependencies
        allowed_dependencies = ["pytest", "pytest-cov", "pytest-mock", "pytest-xdist"]

        missing_deps = []

        for dep in allowed_dependencies:
            try:
                # Security validation: check that dependency is allowed
                if dep not in allowed_dependencies:
                    print(f"   ❌ {dep} - NOT AUTHORIZED")
                    continue

                # Use a secure command list - trusted dependencies
                cmd = [sys.executable, "-m", dep, "--version"]
                subprocess.run(
                    cmd, capture_output=True, check=True, timeout=10
                )  # noqa: S603
                print(f"   ✅ {dep}")
            except (
                subprocess.CalledProcessError,
                FileNotFoundError,
                subprocess.TimeoutExpired,
            ):
                print(f"   ❌ {dep} - MISSING")
                missing_deps.append(dep)

        if missing_deps:
            print(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
            print(
                "💡 Install them with: pip install pytest pytest-cov pytest-mock pytest-xdist"
            )
            return False

        print("✅ All dependencies are installed")
        return True

    def _validate_test_path(self, path: str) -> bool:
        """Validate a test path for security."""
        try:
            test_path = Path(path).resolve()
            project_root = self.project_root.resolve()

            # Check that the path is in the project
            if not str(test_path).startswith(str(project_root)):
                return False

            # Check that it's a Python test file
            if test_path.suffix != ".py":
                return False

            # Check that the name starts with "test_"
            return test_path.name.startswith("test_")
        except Exception:
            return False

    def _build_pytest_command(self, args: argparse.Namespace) -> List[str]:
        """Build the pytest command based on arguments."""
        # Secure base command
        cmd = [sys.executable, "-m", "pytest"]

        # Whitelist of allowed pytest options (used in _validate_pytest_command)
        # allowed_options = {
        #     "-v",
        #     "--verbose",
        #     "-s",
        #     "--tb=long",
        #     "--tb=short",
        #     "--log-cli-level=DEBUG",
        #     "--durations=10",
        #     "--cov=shared",
        #     "--cov=languages",
        #     "--cov-report=term-missing",
        #     "--cov-report=html",
        #     "--cov-report=xml",
        #     "-m",
        #     "-n",
        # }

        # Add test paths with validation
        if args.test_paths:
            for path in args.test_paths:
                if self._validate_test_path(path):
                    cmd.append(path)
                else:
                    print(f"⚠️  Invalid test path ignored: {path}")
        elif args.unit:
            cmd.append(str(self.unit_dir))
        elif args.integration:
            cmd.append(str(self.integration_dir))
        elif args.security:
            cmd.extend(["-m", "security"])
        else:
            cmd.append(str(self.tests_dir))

        # Base options with validation
        if args.verbose:
            cmd.append("-v")

        if args.debug:
            cmd.extend(["-v", "-s", "--tb=long", "--log-cli-level=DEBUG"])

        # Markers with validation
        if args.fast:
            cmd.extend(["-m", "not slow"])

        # Coverage with validation
        if args.coverage:
            cmd.extend(
                [
                    "--cov=shared",
                    "--cov=languages",
                    "--cov-report=term-missing",
                    "--cov-report=html",
                    "--cov-report=xml",
                ]
            )

        # Parallelization with validation
        if args.parallel:
            cmd.extend(["-n", "auto"])

        # Summary with validation
        if args.summary:
            cmd.extend(["--tb=short", "--durations=10"])

        return cmd

    def _validate_pytest_command(self, cmd: List[str]) -> bool:
        """Validate the pytest command for security."""
        try:
            # Check that the command starts with python and pytest
            if len(cmd) < 3:
                return False

            if cmd[0] != sys.executable:
                return False

            if cmd[1] != "-m" or cmd[2] != "pytest":
                return False

            # Whitelist of allowed options
            allowed_options = {
                "-v",
                "--verbose",
                "-s",
                "--tb=long",
                "--tb=short",
                "--log-cli-level=DEBUG",
                "--durations=10",
                "--cov=shared",
                "--cov=languages",
                "--cov-report=term-missing",
                "--cov-report=html",
                "--cov-report=xml",
                "-m",
                "-n",
                "auto",
                "security",
                "not slow",
            }

            # Check each argument
            for arg in cmd[3:]:
                # Ignore file paths (they are validated separately)
                if arg.endswith(".py") or "/" in arg or "\\" in arg:
                    continue

                # Check options
                if arg not in allowed_options:
                    print(f"⚠️  Unauthorized pytest option ignored: {arg}")
                    return False

            return True
        except Exception:
            return False

    def run_tests(self, args: argparse.Namespace) -> int:
        """Execute tests according to provided arguments."""

        if not self.pytest_available:
            print("❌ pytest is not available")
            print("💡 Install it with: pip install pytest")
            return 1

        if args.check_deps:
            return 0 if self._check_dependencies() else 1

        # Build the pytest command
        cmd = self._build_pytest_command(args)

        print("🧪 Running tests...")
        print(f"📋 Command: {' '.join(cmd)}")
        print("-" * 60)

        try:
            # Final command validation
            if not self._validate_pytest_command(cmd):
                print("❌ Invalid pytest command detected")
                return 1

            # Execute tests with timeout - validated and secure command
            result = subprocess.run(
                cmd, cwd=self.project_root, timeout=300
            )  # noqa: S603  # 5 minutes max

            # Display summary
            if args.summary:
                self._print_summary()

            return result.returncode

        except subprocess.TimeoutExpired:
            print("❌ Timeout during test execution (5 minutes)")
            return 1
        except KeyboardInterrupt:
            print("\n⚠️  Tests interrupted by user")
            return 130
        except Exception as e:
            print(f"❌ Error during test execution: {e}")
            return 1

    def _print_summary(self):
        """Display a test summary."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)

        # Count test files
        unit_tests = len(list(self.unit_dir.glob("test_*.py")))
        integration_tests = len(list(self.integration_dir.glob("test_*.py")))

        print(f"📁 Unit tests: {unit_tests} files")
        print(f"🔗 Integration tests: {integration_tests} files")
        print("📈 Coverage: htmlcov/index.html")

        # Display available test types
        print("\n🎯 Available test types:")
        print("   • Unit tests: tests/unit/")
        print("   • Integration tests: tests/integration/")
        print("   • Security tests: -m security")
        print("   • Fast tests: --fast")

        # Display useful options
        print("\n🔧 Useful options:")
        print("   • python run_tests.py --coverage")
        print("   • python run_tests.py --parallel")
        print("   • python run_tests.py --debug")
        print("   • python run_tests.py tests/unit/test_security_validator.py")

    def print_help(self):
        """Display detailed help."""
        help_text = """
🧪 Works On My Machine - Test runner script

Usage:
    python run_tests.py [options] [test_paths...]

Main options:
    --unit              Run unit tests only
    --integration       Run integration tests only
    --security          Run security tests only
    --coverage          Generate HTML coverage report
    --fast              Fast tests (exclude slow tests)
    --parallel          Run tests in parallel
    --debug             Debug mode with more details
    --check-deps        Check test dependencies
    --summary           Display test summary

Examples:
    # All tests
    python run_tests.py

    # Unit tests only
    python run_tests.py --unit

    # Tests with coverage
    python run_tests.py --coverage

    # Tests in parallel
    python run_tests.py --parallel

    # Specific test
    python run_tests.py tests/unit/test_security_validator.py

    # Security tests
    python run_tests.py --security

    # Debug mode
    python run_tests.py --debug

Available pytest markers:
    • unit: Unit tests
    • integration: Integration tests
    • security: Security tests
    • slow: Slow tests
    • windows/linux/macos: OS-specific tests

Generated reports:
    • HTML coverage: htmlcov/index.html
    • XML coverage: coverage.xml
    • Terminal coverage: direct display
"""
        print(help_text)


def main():
    """Main entry point of the script."""
    parser = argparse.ArgumentParser(
        description="Test runner script for Works On My Machine",
        add_help=False,
    )

    # Test type options
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run integration tests only",
    )
    parser.add_argument(
        "--security",
        action="store_true",
        help="Run security tests only",
    )

    # Configuration options
    parser.add_argument(
        "--coverage", action="store_true", help="Generate coverage report"
    )
    parser.add_argument(
        "--fast", action="store_true", help="Fast tests (exclude slow tests)"
    )
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument(
        "--debug", action="store_true", help="Debug mode with more details"
    )

    # Utility options
    parser.add_argument(
        "--check-deps", action="store_true", help="Check test dependencies"
    )
    parser.add_argument("--summary", action="store_true", help="Display test summary")
    parser.add_argument("--help", "-h", action="store_true", help="Show this help")

    # Verbosity options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose mode")

    # Specific test paths
    parser.add_argument("test_paths", nargs="*", help="Specific paths to tests")

    args = parser.parse_args()

    # Show help if requested
    if args.help:
        runner = TestRunner()
        runner.print_help()
        return 0

    # Create and execute the test manager
    runner = TestRunner()
    return runner.run_tests(args)


if __name__ == "__main__":
    sys.exit(main())
