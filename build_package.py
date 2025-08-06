#!/usr/bin/env python3
"""
Build script for WOMM PyPI package.
This script builds the package and optionally uploads it to PyPI.
"""

import shutil
import subprocess
import sys
from pathlib import Path


def clean_build_dirs():
    """Clean build and dist directories."""
    dirs_to_clean = ["build", "dist", "*.egg-info"]

    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                print(f"Removing {path}")
                shutil.rmtree(path)
            else:
                print(f"Removing {path}")
                path.unlink()


def build_package():
    """Build the package."""
    print("Building WOMM package...")

    # Clean previous builds
    clean_build_dirs()

    # Build the package
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "build", "--wheel", "--sdist"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("Build failed:")
        print(result.stderr)
        return False

    print("Build successful!")
    print(result.stdout)
    return True


def check_package():
    """Check the built package."""
    print("Checking package...")

    result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "twine", "check", "dist/*"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("Package check failed:")
        print(result.stderr)
        return False

    print("Package check passed!")
    print(result.stdout)
    return True


def upload_to_test_pypi():
    """Upload to Test PyPI."""
    print("Uploading to Test PyPI...")

    result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "twine", "upload", "--repository", "testpypi", "dist/*"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("Upload to Test PyPI failed:")
        print(result.stderr)
        return False

    print("Upload to Test PyPI successful!")
    print(result.stdout)
    return True


def upload_to_pypi():
    """Upload to PyPI."""
    print("Uploading to PyPI...")

    result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "twine", "upload", "dist/*"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("Upload to PyPI failed:")
        print(result.stderr)
        return False

    print("Upload to PyPI successful!")
    print(result.stdout)
    return True


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python build_package.py [build|check|test-upload|upload]")
        print("  build        - Build the package")
        print("  check        - Check the built package")
        print("  test-upload  - Upload to Test PyPI")
        print("  upload       - Upload to PyPI")
        return

    command = sys.argv[1]

    if command == "build":
        if not build_package():
            sys.exit(1)

    elif command == "check":
        if not check_package():
            sys.exit(1)

    elif command == "test-upload":
        if not build_package():
            sys.exit(1)
        if not check_package():
            sys.exit(1)
        if not upload_to_test_pypi():
            sys.exit(1)

    elif command == "upload":
        if not build_package():
            sys.exit(1)
        if not check_package():
            sys.exit(1)
        if not upload_to_pypi():
            sys.exit(1)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
