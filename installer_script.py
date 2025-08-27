#!/usr/bin/env python3
import os
import shutil
import sys
import tempfile
from pathlib import Path


def main():
    print("WOMM Installer")
    print("=" * 30)

    try:
        if install_womm():
            print("Installation successful!")
        else:
            print("Installation failed!")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def install_womm():
    print("Installing WOMM...")
    try:
        # Extract embedded WOMM files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Extract womm directory
            if not extract_womm_files(temp_path):
                return False

            # Run womm install using the package
            return run_womm_install(temp_path)

    except Exception as e:
        print(f"Installation error: {e}")
        return False


def extract_womm_files(temp_path):
    """Extract embedded WOMM files to temp directory."""
    print("Extracting WOMM files...")

    # Get the path to the executable
    if getattr(sys, "frozen", False):
        # Running as compiled executable
        base_path = Path(sys._MEIPASS)
    else:
        # Running as script
        base_path = Path(__file__).parent

    # Copy womm directory
    womm_source = base_path / "womm"
    womm_target = temp_path / "womm"

    if womm_source.exists():
        shutil.copytree(womm_source, womm_target)
        print(f"Extracted womm/ directory")
    else:
        print(f"womm/ directory not found at {womm_source}")
        return False

    return True


def run_womm_install(temp_path):
    """Run womm install using the package."""
    print("Running WOMM installation...")

    try:
        # Change to temp directory
        original_cwd = Path.cwd()
        os.chdir(temp_path)

        # Add temp directory to Python path
        sys.path.insert(0, str(temp_path))

        # Import and run womm install
        from womm.cli import womm

        # Set command line arguments for install
        sys.argv = ["womm", "install", "--force"]

        # Run the install command
        womm()

        # Restore original directory
        os.chdir(original_cwd)

        print("WOMM installation completed successfully")
        return True

    except Exception as e:
        print(f"Error running womm install: {e}")
        return False


if __name__ == "__main__":
    main()
