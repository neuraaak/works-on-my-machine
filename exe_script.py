#!/usr/bin/env python3
"""
Simple script to run womm install using WOMM as a package.
"""

import sys
from pathlib import Path


def main():
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

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
