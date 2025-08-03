#!/usr/bin/env python3
"""
Python project linting script.

This script automates code quality checks:
- ruff for style and security verification
- black for formatting
- isort for import organization
"""

import argparse

# Import the new CLI manager
import sys
from pathlib import Path

# Add parent path to import shared
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from shared.core.cli_manager import run_command
except ImportError:
    # Fallback if import fails
    import subprocess

    def run_command(cmd, description=None, cwd=None):
        print(f"🔧 {description or ' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd, cwd=cwd, capture_output=True, text=True, timeout=30
            )
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


def is_security_excluded(path: Path) -> bool:
    """Check if a file or directory is excluded for security reasons."""
    import fnmatch

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


def detect_project_dirs(base_path: Path | None = None) -> list[str]:
    """Detect Python directories while excluding sensitive files."""
    current_dir = Path(base_path) if base_path else Path.cwd()
    target_dirs = []

    # Search for directories with Python files
    for item in current_dir.iterdir():
        if (
            item.is_dir()
            and not item.name.startswith(".")
            and item.name not in ["build", "dist", "__pycache__", "htmlcov"]
            and not is_security_excluded(item)
        ):
            # Check if it contains Python files (non-sensitive)
            has_python_files = False
            try:
                for py_file in item.glob("*.py"):
                    if not is_security_excluded(py_file):
                        has_python_files = True
                        break
                if not has_python_files:
                    for py_file in item.glob("**/*.py"):
                        if not is_security_excluded(py_file):
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

    # Fallback: analyze current directory if it contains safe .py files
    if not target_dirs:
        has_safe_python_files = False
        try:
            for py_file in current_dir.glob("*.py"):
                if not is_security_excluded(py_file):
                    has_safe_python_files = True
                    break
        except OSError:
            pass
        if has_safe_python_files:
            target_dirs.append(".")

    return target_dirs

    return target_dirs


def main(target_path=None):
    """Fonction principale du script de linting."""
    print("🚀 Script de linting démarré!")
    target_dir = Path(target_path) if target_path else Path.cwd()

    print("🎨 Python Project - Linting Script")
    print("=" * 50)
    print(f"📂 Target directory: {target_dir}")

    # Check that tools are installed
    tools = ["ruff", "black", "isort"]
    missing_tools = []

    from shared.core.cli_manager import run_silent

    for tool in tools:
        try:
            result = run_silent([tool, "--version"])
            if not result.success:
                raise Exception(f"Tool {tool} not available")
        except Exception:
            missing_tools.append(tool)

    if missing_tools:
        print(f"❌ Missing tools: {', '.join(missing_tools)}")
        print("Install them with: pip install -e '.[dev]'")
        return 1

    # Automatically detect directories to analyze
    target_dirs = detect_project_dirs(target_dir)
    if not target_dirs:
        print("❌ No Python folders found")
        return 1

    print(f"📁 Analyzing folders: {', '.join(target_dirs)}")

    success = True

    # 1. Check style with ruff
    print("🔍 Checking style with ruff...")
    ruff_success = run_command(
        ["ruff", "check"] + target_dirs,
        "Style check (ruff)",
        cwd=target_dir,
    )
    success = success and ruff_success

    # 2. Check formatting with black
    print("🔍 Checking formatting with black...")
    black_success = run_command(
        ["black", "--check", "--diff"] + target_dirs,
        "Format check (black)",
        cwd=target_dir,
    )
    success = success and black_success

    # 3. Check import organization with isort
    print("🔍 Checking imports with isort...")
    isort_success = run_command(
        ["isort", "--check-only", "--diff"] + target_dirs,
        "Import check (isort)",
        cwd=target_dir,
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
        print(f"   black {' '.join(target_dirs)}")
        print(f"   isort {' '.join(target_dirs)}")
        print(f"   ruff check {' '.join(target_dirs)}")
        return 1


def fix_whitespace_issues(target_path=None):
    """Fix whitespace issues (W293, W291, W292)."""
    target_dir = Path(target_path) if target_path else Path.cwd()
    fixed_files = 0

    print("🧹 Fixing whitespace issues...")

    for py_file in target_dir.rglob("*.py"):
        if is_security_excluded(py_file):
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


def fix_code(target_path=None):
    """Automatically fix code."""
    target_dir = Path(target_path) if target_path else Path.cwd()

    print("🔧 Python Project - Automatic code fixing")
    print("=" * 50)
    print(f"📂 Target directory: {target_dir}")

    # Detect directories
    target_dirs = detect_project_dirs(target_dir)
    if not target_dirs:
        print("❌ No Python folders found")
        return 1

    print(f"📁 Formatting folders: {', '.join(target_dirs)}")

    success = True

    # 0. Fix whitespace issues
    fix_whitespace_issues(target_dir)

    # 1. Format with black
    black_success = run_command(
        ["black"] + target_dirs, "Automatic formatting (black)", cwd=target_dir
    )
    success = success and black_success

    # 2. Organize imports with isort
    isort_success = run_command(
        ["isort"] + target_dirs, "Import organization (isort)", cwd=target_dir
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Linting script for Python projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Analyze current directory
  python lint.py

  # Analyze specific directory
  python lint.py /path/to/project

  # Automatically fix code
  python lint.py --fix

  # Fix specific directory
  python lint.py /path/to/project --fix
        """,
    )

    parser.add_argument(
        "path",
        nargs="?",
        help="Path to project to analyze (default: current directory)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix code instead of just analyzing it",
    )

    args = parser.parse_args()

    if args.fix:
        sys.exit(fix_code(args.path))
    else:
        sys.exit(main(args.path))
