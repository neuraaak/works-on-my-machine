#!/usr/bin/env python3
"""
Build script for WOMM executable installer.
This script creates a standalone executable using PyInstaller.
"""

import shutil
import subprocess
import sys
from pathlib import Path


def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller

        print(f"PyInstaller version: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        return True


def clean_build_dirs():
    """Clean build and dist directories."""
    dirs_to_clean = ["build", "dist", "*.spec"]

    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                print(f"Removing {path}")
                shutil.rmtree(path)
            elif path.name != "womm.spec":
                print(f"Removing {path}")
                path.unlink()


def build_executable():
    """Build the executable using PyInstaller."""
    print("Building WOMM executable...")

    # Clean previous builds
    clean_build_dirs()

    # Build using the spec file
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "womm.spec", "--clean"],
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


def test_executable():
    """Test the built executable."""
    exe_path = Path("dist") / "womm-installer.exe"

    if not exe_path.exists():
        print(f"Executable not found at {exe_path}")
        return False

    print(f"Testing executable: {exe_path}")

    # Test basic functionality
    result = subprocess.run(
        [str(exe_path), "--help"], capture_output=True, text=True, timeout=30
    )

    if result.returncode == 0:
        print("✅ Executable test passed!")
        print("Help output:")
        print(
            result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout
        )
        return True
    else:
        print("❌ Executable test failed:")
        print(result.stderr)
        return False


def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        print("WOMM Executable Builder")
        print("=" * 50)

        # Check PyInstaller
        if not check_pyinstaller():
            print("Failed to install PyInstaller")
            sys.exit(1)

        # Build executable
        if not build_executable():
            print("Build failed")
            sys.exit(1)

        # Test executable
        if not test_executable():
            print("Test failed")
            sys.exit(1)

        print("\n🎉 Build completed successfully!")
        print(f"Executable location: {Path('dist') / 'womm-installer.exe'}")
        print("\nYou can now distribute the executable as a standalone installer.")
    else:
        print("Usage: python build_exe.py build")
        print("  build  - Build the executable")


if __name__ == "__main__":
    main()
