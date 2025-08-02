#!/usr/bin/env python3
"""
Linting script for the works-on-my-machine project.

This script automates code quality checks:
- ruff for style checking and formatting
- bandit for security

Adapted from the original script in languages/python/scripts/lint.py
"""

import argparse
import sys
from pathlib import Path

# Import the new CLI manager
from shared.core.cli_manager import run_command_legacy as run_command


def is_security_excluded(path):
    """Check if a file or directory is excluded for security."""
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


def detect_project_dirs(base_path=None):
    """Detect Python directories in the works-on-my-machine project."""
    current_dir = Path(base_path) if base_path else Path.cwd()
    target_dirs = []

    # Specific directories for the works-on-my-machine project
    project_dirs = ["shared", "languages"]

    for dir_name in project_dirs:
        dir_path = current_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            # Check if it contains Python files (non-sensitive)
            has_python_files = False
            try:
                for py_file in dir_path.glob("**/*.py"):
                    if not is_security_excluded(py_file):
                        has_python_files = True
                        break
                if has_python_files:
                    target_dirs.append(str(dir_path))
            except OSError:
                # Ignore file access errors (includes PermissionError)
                pass

    # Add Python files at the root (init.py, etc.)
    root_python_files = []
    try:
        for py_file in current_dir.glob("*.py"):
            if not is_security_excluded(py_file):
                root_python_files.append(str(py_file))
    except OSError:
        pass

    if root_python_files:
        target_dirs.extend(root_python_files)

    return target_dirs


def main(target_path=None):
    """Main function of the linting script."""
    target_dir = Path(target_path) if target_path else Path.cwd()

    print("🎨 works-on-my-machine - Linting Script")
    print("=" * 50)
    print(f"📂 Target directory: {target_dir}")

    # Check that tools are installed
    tools = ["ruff", "bandit"]
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
        print("❌ No Python directory found")
        return 1

    print(f"📁 Analysis: {', '.join(target_dirs)}")

    success = True

    # 1. Check style and formatting with ruff
    ruff_success = run_command(
        ["ruff", "check"] + target_dirs,
        "Style and formatting check (ruff)",
        cwd=target_dir,
    )
    success = success and ruff_success

    # 2. Check security with bandit (JSON format to avoid encoding issues)
    bandit_success = run_command(
        ["bandit", "-r", "-f", "json"] + target_dirs,
        "Security check (bandit)",
        cwd=target_dir,
    )
    success = success and bandit_success

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
        print(f"   ruff check --fix {' '.join(target_dirs)}")
        print(f"   ruff format {' '.join(target_dirs)}")
        return 1


def fix_whitespace_issues(target_path=None):
    """Fix whitespace issues (W293, W291, W292)."""
    target_dir = Path(target_path) if target_path else Path.cwd()
    fixed_files = 0

    print("🧹 Fixing extra spaces...")

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
        print(f"🎉 {fixed_files} files fixed for spaces")
    else:
        print("✅ No whitespace issues found")

    return fixed_files


def fix_code(target_path=None):
    """Automatically fix code."""
    target_dir = Path(target_path) if target_path else Path.cwd()

    print("🔧 works-on-my-machine - Automatic Code Fixing")
    print("=" * 50)
    print(f"📂 Target directory: {target_dir}")

    # Detect directories
    target_dirs = detect_project_dirs(target_dir)
    if not target_dirs:
        print("❌ No Python directory found")
        return 1

    print(f"📁 Formatting: {', '.join(target_dirs)}")

    success = True

    # 0. Fix whitespace issues
    fix_whitespace_issues(target_dir)

    # 1. Fix and format with ruff
    ruff_success = run_command(
        ["ruff", "check", "--fix"] + target_dirs,
        "Automatic fixing (ruff)",
        cwd=target_dir,
    )
    success = success and ruff_success

    # 2. Format with ruff
    ruff_format_success = run_command(
        ["ruff", "format"] + target_dirs, "Automatic formatting (ruff)", cwd=target_dir
    )
    success = success and ruff_format_success

    # Summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 Automatic corrections completed!")
        print("✅ Code has been formatted and organized.")
        return 0
    else:
        print("⚠️  Some corrections failed.")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Linting script for works-on-my-machine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze the works-on-my-machine project
  python lint.py

  # Analyze a specific directory
  python lint.py /path/to/project

  # Automatically fix code
  python lint.py --fix

  # Fix a specific directory
  python lint.py /path/to/project --fix
        """,
    )

    parser.add_argument(
        "path",
        nargs="?",
        help="Project path to analyze (default: current directory)",
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
