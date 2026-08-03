#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEMPLATE RESULTS - Template catalog result types
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""Typed results returned by the template store."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from dataclasses import dataclass

from womm.shared.models.template_source import TemplateEntry

from .base import BaseResult

# ///////////////////////////////////////////////////////////////
# RESULTS
# ///////////////////////////////////////////////////////////////


@dataclass
class TemplateStoreResult(BaseResult):
    """Result of an operation targeting a single template."""

    entry: TemplateEntry | None = None


@dataclass
class TemplateListResult(BaseResult):
    """Result of listing the template catalog."""

    entries: list[TemplateEntry] | None = None


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["TemplateListResult", "TemplateStoreResult"]
