#!/usr/bin/env python3
"""
Works On My Machine (WOMM) - Main CLI Entry Point.
Modular CLI interface for universal development tools.
"""

import sys
from pathlib import Path

# Add the womm package to the path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the CLI
from womm.cli import womm

if __name__ == "__main__":
    womm()
