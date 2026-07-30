#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST SERVICES UI BOUNDARY - Layer guard
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Guard the rule that services never reach for the UI layer.

Services hold policy and must stay usable without a terminal; prompting and
rendering belong to the command/UI layer. The check reads the source rather
than the imported modules so that deferred, in-function imports are caught too.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import ast
from pathlib import Path

# Local imports
import womm.services

# ///////////////////////////////////////////////////////////////
# HELPERS
# ///////////////////////////////////////////////////////////////

SERVICES_ROOT = Path(womm.services.__file__).parent


def _ui_imports(source: str, depth: int) -> list[str]:
    """List the UI imports found in a module's source.

    Args:
        source: Python source code of a service module
        depth: Number of leading dots a relative import needs to reach the
            `womm` root from that module, i.e. its number of path components
            (`womm/services/project/x.py` needs `...`, so depth is 3)

    Returns:
        list[str]: Human-readable description of each offending import
    """
    offenders: list[str] = []

    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            reaches_root = node.level == depth
            if (reaches_root and module.startswith("ui")) or module.startswith(
                ("womm.ui", "ui.")
            ):
                offenders.append(f"from {'.' * node.level}{module}")
        elif isinstance(node, ast.Import):
            offenders.extend(
                f"import {alias.name}"
                for alias in node.names
                if alias.name.startswith("womm.ui")
            )

    return offenders


# ///////////////////////////////////////////////////////////////
# UI BOUNDARY
# ///////////////////////////////////////////////////////////////


def test_no_service_module_imports_the_ui_layer() -> None:
    offenders: list[str] = []

    for path in SERVICES_ROOT.rglob("*.py"):
        depth = len(path.relative_to(SERVICES_ROOT.parent).parts)
        offenders += [
            f"{path.name}: {found}"
            for found in _ui_imports(path.read_text(encoding="utf-8"), depth)
        ]

    assert offenders == [], f"services must not import the UI layer: {offenders}"


def test_the_guard_detects_a_ui_import_at_a_real_module_depth() -> None:
    # The depth is derived exactly as the scan above derives it, so an
    # off-by-one there cannot make this guard silently vacuous.
    module = SERVICES_ROOT / "project" / "conflict_resolution_service.py"
    depth = len(module.relative_to(SERVICES_ROOT.parent).parts)

    found = _ui_imports("from ...ui.common.prompts import confirm\n", depth)

    assert found == ["from ...ui.common.prompts"]


def test_the_guard_ignores_a_relative_import_that_stops_below_the_root() -> None:
    # `..ui` from womm/services/project/x.py points at womm.services.ui,
    # which is not the UI layer.
    assert _ui_imports("from ..ui import helper\n", depth=3) == []
