#!/usr/bin/env python3
"""
Works On My Machine (WOMM) - Main CLI Entry Point.
This is a root-level entry point that delegates to the package script.
"""

import sys
from pathlib import Path

# Get the path to the package script
package_script = Path(__file__).parent / "womm" / "scripts" / "womm.py"

if not package_script.exists():
    print("❌ Error: Could not find womm package script")
    print(f"💡 Expected location: {package_script}")
    sys.exit(1)

# Execute the package script with the same arguments
import subprocess

result = subprocess.run([sys.executable, str(package_script)] + sys.argv[1:])
sys.exit(result.returncode)
