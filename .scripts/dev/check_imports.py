#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CHECK_IMPORTS - import-linter wrapper for the src-layout
# ///////////////////////////////////////////////////////////////

"""Run import-linter from ``src/`` so that ``womm`` resolves to the package.

With the src-layout, a ``womm.py`` launcher still lives at the repo root and
shadows the ``src/womm`` package whenever import-linter is invoked from the
root (it then reports "'womm' is a module, not a package"). Running from
``src/`` removes the ambiguity; the config still lives in the root
``pyproject.toml``, so it is passed explicitly.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import subprocess
import sys
from pathlib import Path

# ///////////////////////////////////////////////////////////////
# ENTRY POINT
# ///////////////////////////////////////////////////////////////

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    """Run ``lint-imports`` from the src directory and return its exit code."""
    result = subprocess.run(  # noqa: S603
        ["lint-imports", "--config", str(PROJECT_ROOT / "pyproject.toml")],  # noqa: S607
        cwd=PROJECT_ROOT / "src",
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
