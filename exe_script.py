#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXE_SCRIPT - Executable Entry Point
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Simple script to run womm install using WOMM as a package.

This script is used as the entry point for the PyInstaller executable.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys
from pathlib import Path

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def main() -> None:
    """Main function for executable entry point."""
    try:
        # Add current directory to Python path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))

        # Import and run womm install
        from womm.cli import womm

        # Set command line arguments for install
        sys.argv = ["womm", "install", "--force"]

        # Run the install command
        womm()

        print("Installation completed successfully!")

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 This indicates missing dependencies in the executable build")
        print("🔧 Please rebuild the executable with the updated build script")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


# ///////////////////////////////////////////////////////////////
# MAIN
# ///////////////////////////////////////////////////////////////

if __name__ == "__main__":
    main()
