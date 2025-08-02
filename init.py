#!/usr/bin/env python3
"""
Initialize the Works On My Machine environment.

This is a compatibility wrapper that delegates to womm:install.
For direct installation, use: python womm.py install
"""

import sys
from pathlib import Path

# Add the current directory to Python path to import womm
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Call womm:install with the same arguments."""
    try:
        from womm import womm

        # Convert sys.argv to Click format
        # Skip the script name (init.py) and add 'install' command
        args = ["install"] + sys.argv[1:]

        # Call womm with install command
        womm(args)

    except ImportError as e:
        print(f"❌ Error importing womm module: {e}")
        print("💡 Make sure you're running this from the WOMM project directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during installation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
