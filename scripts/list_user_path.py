#!/usr/bin/env python3
"""
List user PATH entries (Windows) using the same deduplication logic as PathManager.
Falls back to printing current session PATH on non-Windows.
"""

from __future__ import annotations

import os
import platform
import subprocess

from womm.core.installation.path_manager_utils import (
    deduplicate_path_entries,
    extract_path_from_reg_output,
)


def main() -> int:
    if platform.system() == "Windows":
        # Query user PATH from registry: HKCU\Environment\PATH
        proc = subprocess.run(
            ["reg", "query", r"HKCU\Environment", "/v", "PATH"],  # noqa: S607
            capture_output=True,
            text=True,
            check=False,
        )
        raw = proc.stdout or ""
        user_path = extract_path_from_reg_output(raw)
    else:
        # Non-Windows: use current session PATH (no registry equivalent)
        user_path = os.environ.get("PATH", "")

    deduped = deduplicate_path_entries(user_path)
    for part in [p.strip() for p in deduped.split(";") if p.strip()]:
        print(part)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
