#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DJANGO LINT - Django Project Linting Script
# ///////////////////////////////////////////////////////////////

"""
Django project linting script.

This script automates code quality checks:
- ruff for style and security verification (Django-aware)
- black for formatting
- isort for import organization (Django-aware)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import fnmatch
import shutil
import subprocess
import sys
from pathlib import Path

# ///////////////////////////////////////////////////////////////
# SECURITY UTILITIES
# ///////////////////////////////////////////////////////////////


def is_security_excluded(path: Path) -> bool:
    """Check if a file or directory is excluded for security reasons.

    Args:
        path: Path to check

    Returns:
        True if path should be excluded for security reasons
    """
    security_patterns = [
        ".env*",
        ".secret*",
        "*password*",
        "*secret*",
        "*.key",
        "*.pem",
        "*.crt",
        "credentials",
        "keys",
    ]

    path_str = str(path).lower()
    name = path.name.lower()

    for pattern in security_patterns:
        if fnmatch.fnmatch(name, pattern) or pattern in path_str:
            return True
    return False


def is_django_excluded(path: Path) -> bool:
    """Check if a path should be excluded for Django-specific reasons.

    Args:
        path: Path to check

    Returns:
        True if path should be excluded
    """
    django_exclude_patterns = [
        "migrations",
        "staticfiles",
        "static_collected",
        "media",
        "db.sqlite3",
        "manage.py",
    ]

    path_str = str(path).lower()
    name = path.name.lower()

    for pattern in django_exclude_patterns:
        if pattern in path_str or name == pattern:
            return True
    return False


# ///////////////////////////////////////////////////////////////
# PROJECT DETECTION
# ///////////////////////////////////////////////////////////////


def detect_project_dirs(base_path: Path | None = None) -> list[str]:
    """Detect Python directories while excluding sensitive files and Django-specific exclusions.

    Args:
        base_path: Base path to search from (default: current directory)

    Returns:
        List of directory paths to analyze
    """
    current_dir = Path(base_path) if base_path else Path.cwd()
    target_dirs = []

    # Search for directories with Python files
    for item in current_dir.iterdir():
        if (
            item.is_dir()
            and not item.name.startswith(".")
            and item.name
            not in ["build", "dist", "__pycache__", "htmlcov", "staticfiles", "media"]
            and not is_security_excluded(item)
            and not is_django_excluded(item)
        ):
            # Check if it contains Python files (non-sensitive, non-migrations)
            has_python_files = False
            try:
                for py_file in item.glob("*.py"):
                    if not is_security_excluded(py_file) and not is_django_excluded(
                        py_file
                    ):
                        has_python_files = True
                        break
                if not has_python_files:
                    for py_file in item.glob("**/*.py"):
                        # Skip migrations
                        if "migrations" in str(py_file):
                            continue
                        if not is_security_excluded(py_file) and not is_django_excluded(
                            py_file
                        ):
                            has_python_files = True
                            break
                if has_python_files:
                    target_dirs.append(str(item))
            except OSError:
                # Ignore file access errors
                pass

    # Add 'tests' if it exists and is not excluded
    tests_dir = current_dir / "tests"
    if tests_dir.exists() and not is_security_excluded(tests_dir):
        target_dirs.append("tests")

    # Add project root if manage.py exists (Django project)
    manage_py = current_dir / "manage.py"
    # Add main project directory (usually same as current_dir name or {{PROJECT_NAME}})
    # For Django, we typically lint the project root and apps
    if manage_py.exists() and "." not in target_dirs:
        target_dirs.append(".")

    # Fallback: analyze current directory if it contains safe .py files
    if not target_dirs:
        has_safe_python_files = False
        try:
            for py_file in current_dir.glob("*.py"):
                if not is_security_excluded(py_file) and not is_django_excluded(
                    py_file
                ):
                    has_safe_python_files = True
                    break
        except OSError:
            pass
        if has_safe_python_files:
            target_dirs.append(".")

    return target_dirs


# ///////////////////////////////////////////////////////////////
# COMMAND EXECUTION UTILITIES
# ///////////////////////////////////////////////////////////////


def check_tool_available(tool_name: str) -> bool:
    """Check if a linting tool is available in PATH.

    Args:
        tool_name: Name of the tool to check

    Returns:
        True if tool is available, False otherwise
    """
    return shutil.which(tool_name) is not None


def run_tool_check(
    tool_name: str, args: list[str], cwd: Path, _description: str
) -> bool:
    """Run a linting tool in check mode.

    Args:
        tool_name: Name of the tool to run
        args: Arguments to pass to the tool
        cwd: Working directory
        _description: Description of the operation (unused, kept for API consistency)

    Returns:
        True if check passed, False otherwise
    """
    try:
        cmd = [tool_name, *args]
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            # Print output for debugging
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            return False

        return True
    except FileNotFoundError:
        print(f"❌ Tool '{tool_name}' not found in PATH", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ Error running {tool_name}: {e}", file=sys.stderr)
        return False


def run_tool_fix(tool_name: str, args: list[str], cwd: Path, _description: str) -> bool:
    """Run a linting tool in fix mode.

    Args:
        tool_name: Name of the tool to run
        args: Arguments to pass to the tool
        cwd: Working directory
        _description: Description of the operation (unused, kept for API consistency)

    Returns:
        True if fix succeeded, False otherwise
    """
    try:
        cmd = [tool_name, *args]
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            # Print output for debugging
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            return False

        # Print output for user feedback
        if result.stdout:
            print(result.stdout)

        return True
    except FileNotFoundError:
        print(f"❌ Tool '{tool_name}' not found in PATH", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ Error running {tool_name}: {e}", file=sys.stderr)
        return False


# ///////////////////////////////////////////////////////////////
# MAIN LINTING FUNCTIONS
# ///////////////////////////////////////////////////////////////


def main(target_path: str | None = None) -> int:
    """Main linting script function.

    Args:
        target_path: Optional path to target directory (default: current directory)

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("🚀 Django linting script started!")
    target_dir = Path(target_path) if target_path else Path.cwd()

    print("🎯 Django Project - Linting Script")
    print("=" * 50)
    print(f"📂 Target directory: {target_dir}")

    # Check that tools are installed
    tools = ["ruff", "black", "isort"]
    missing_tools = [tool for tool in tools if not check_tool_available(tool)]

    if missing_tools:
        print(f"❌ Missing tools: {', '.join(missing_tools)}")
        print("Install them with: pip install ruff black isort")
        return 1

    # Automatically detect directories to analyze
    target_dirs = detect_project_dirs(target_dir)
    if not target_dirs:
        print("❌ No Python folders found")
        return 1

    print(f"📁 Analyzing folders: {', '.join(target_dirs)}")
    print("ℹ️  Note: Migrations are automatically excluded")

    success = True

    # 1. Check style with ruff (Django-aware)
    print("🔍 Checking style with ruff (Django-aware)...")
    ruff_args = ["check", *target_dirs, "--exclude", "*/migrations/*"]
    ruff_success = run_tool_check(
        "ruff",
        ruff_args,
        target_dir,
        "Style check (ruff)",
    )
    success = success and ruff_success

    # 2. Check formatting with black
    print("🔍 Checking formatting with black...")
    black_args = ["--check", "--diff", *target_dirs, "--exclude", "migrations"]
    black_success = run_tool_check(
        "black",
        black_args,
        target_dir,
        "Format check (black)",
    )
    success = success and black_success

    # 3. Check import organization with isort (Django-aware)
    print("🔍 Checking imports with isort (Django-aware)...")
    isort_args = [
        "--check-only",
        "--diff",
        *target_dirs,
        "--skip",
        "migrations",
    ]
    isort_success = run_tool_check(
        "isort",
        isort_args,
        target_dir,
        "Import check (isort)",
    )
    success = success and isort_success

    # Summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 All checks passed!")
        print("✅ Code meets quality standards.")
        return 0
    else:
        print("⚠️  Some checks failed.")
        print("💡 Use the following commands to fix:")
        print(f"   cd {target_dir}")
        print(f"   black {' '.join(target_dirs)} --exclude migrations")
        print(f"   isort {' '.join(target_dirs)} --skip migrations")
        print(f"   ruff check {' '.join(target_dirs)} --exclude */migrations/*")
        return 1


# ///////////////////////////////////////////////////////////////
# CODE FIXING FUNCTIONS
# ///////////////////////////////////////////////////////////////


def fix_whitespace_issues(target_path: str | None = None) -> int:
    """Fix whitespace issues (W293, W291, W292).

    Args:
        target_path: Optional path to target directory (default: current directory)

    Returns:
        Number of files fixed
    """
    target_dir = Path(target_path) if target_path else Path.cwd()
    fixed_files = 0

    print("🧹 Fixing whitespace issues...")

    for py_file in target_dir.rglob("*.py"):
        if is_security_excluded(py_file) or is_django_excluded(py_file):
            continue
        # Skip migrations
        if "migrations" in str(py_file):
            continue

        try:
            with open(py_file, encoding="utf-8") as f:
                lines = f.readlines()

            modified = False
            new_lines = []

            for line in lines:
                # Remove trailing spaces (W291)
                new_line = (
                    line.rstrip() + "\n" if line.endswith("\n") else line.rstrip()
                )
                if new_line != line:
                    modified = True
                new_lines.append(new_line)

            # Ensure empty line at end of file (W292)
            if new_lines and not new_lines[-1].endswith("\n"):
                new_lines[-1] += "\n"
                modified = True

            if modified:
                with open(py_file, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                fixed_files += 1
                print(f"  ✅ {py_file}")

        except Exception as e:
            print(f"  ❌ Error with {py_file}: {e}")

    if fixed_files > 0:
        print(f"🎉 {fixed_files} files fixed for whitespace")
    else:
        print("✅ No whitespace issues found")

    return fixed_files


def fix_code(target_path: str | None = None) -> int:
    """Automatically fix code.

    Args:
        target_path: Optional path to target directory (default: current directory)

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    target_dir = Path(target_path) if target_path else Path.cwd()

    print("🔧 Django Project - Automatic code fixing")
    print("=" * 50)
    print(f"📂 Target directory: {target_dir}")

    # Detect directories
    target_dirs = detect_project_dirs(target_dir)
    if not target_dirs:
        print("❌ No Python folders found")
        return 1

    print(f"📁 Formatting folders: {', '.join(target_dirs)}")
    print("ℹ️  Note: Migrations are automatically excluded")

    success = True

    # 0. Fix whitespace issues
    fix_whitespace_issues(str(target_dir))

    # 1. Format with black
    black_args = [*target_dirs, "--exclude", "migrations"]
    black_success = run_tool_fix(
        "black",
        black_args,
        target_dir,
        "Automatic formatting (black)",
    )
    success = success and black_success

    # 2. Organize imports with isort
    isort_args = [*target_dirs, "--skip", "migrations"]
    isort_success = run_tool_fix(
        "isort",
        isort_args,
        target_dir,
        "Import organization (isort)",
    )
    success = success and isort_success

    # Summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 Automatic fixes completed!")
        print("✅ Code has been formatted and organized.")
        return 0
    else:
        print("⚠️  Some fixes failed.")
        return 1


# ///////////////////////////////////////////////////////////////
# ENTRY POINT
# ///////////////////////////////////////////////////////////////


if __name__ == "__main__":
    # Check for --fix flag
    if "--fix" in sys.argv or "-f" in sys.argv:
        # Remove the flag from args
        args = [arg for arg in sys.argv[1:] if arg not in ["--fix", "-f"]]
        target_path = args[0] if args else None
        sys.exit(fix_code(target_path))
    else:
        args = sys.argv[1:] if len(sys.argv) > 1 else []
        target_path = args[0] if args else None
        sys.exit(main(target_path))
