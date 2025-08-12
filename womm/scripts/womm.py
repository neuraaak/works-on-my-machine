#!/usr/bin/env python3
"""
Works On My Machine (WOMM) - Main CLI Entry Point.
Modular CLI interface for universal development tools.
"""

import sys
from pathlib import Path

# Add the project root to the path to import womm package
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import and run the CLI
from womm.cli import womm  # noqa: E402

if __name__ == "__main__":
    womm()
