#!/usr/bin/env python3
"""
Works On My Machine (WOMM) - Main CLI Entry Point.
This is a root-level entry point for git clone installations.
For PyPI installations, use 'womm' command directly.
"""

import sys
from pathlib import Path


def main():
    """Main entry point for git clone usage."""
    # Add the current directory to path to import womm package
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

    try:
        # Import and run the CLI directly
        from womm.cli import womm

        womm()
    except ImportError as e:
        print("❌ Error: Could not import womm package")
        print("💡 Make sure you're in the works-on-my-machine directory")
        print(f"🔧 Error details: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
