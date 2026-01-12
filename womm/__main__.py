#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# WOMM __MAIN__ - Package Entry Point
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Works On My Machine (WOMM) - Main CLI Entry Point.

This is the main entry point for the womm package.
Supports both direct execution and module execution.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys

# ///////////////////////////////////////////////////////////////
# MAIN FUNCTIONS
# ///////////////////////////////////////////////////////////////


def main() -> None:
    """Main entry point for the womm package."""
    try:
        # Import and run the CLI directly
        from .cli import womm

        womm()
    except ImportError as e:
        print("Error: Could not import womm package", file=sys.stderr)
        print("Make sure the womm package is properly installed", file=sys.stderr)
        print(f"Error details: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error running WOMM: {e}", file=sys.stderr)
        sys.exit(1)


# ///////////////////////////////////////////////////////////////
# EXECUTION ENTRY POINT
# ///////////////////////////////////////////////////////////////

if __name__ == "__main__":
    main()
