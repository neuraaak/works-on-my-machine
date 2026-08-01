#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST CONTEXT RESULTS - Derived properties
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Tests for the derived properties of ``ContextEntriesResult``.

These replace the former ``ContextStatusResult``: a status is a projection
of a listing, not an operation of its own.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from womm.shared.results import ContextEntriesResult

# ///////////////////////////////////////////////////////////////
# DERIVED PROPERTIES
# ///////////////////////////////////////////////////////////////


def test_empty_result_counts_nothing():
    result = ContextEntriesResult(success=True)

    assert result.total_entries == 0
    assert result.entries_by_type == {}


def test_counts_entries_per_type():
    result = ContextEntriesResult(
        success=True,
        entries={
            "directory": [{"key_name": "a"}, {"key_name": "b"}],
            "background": [{"key_name": "c"}],
        },
    )

    assert result.entries_by_type == {"directory": 2, "background": 1}
    assert result.total_entries == 3


def test_an_empty_type_is_reported_as_zero():
    result = ContextEntriesResult(success=True, entries={"directory": []})

    assert result.entries_by_type == {"directory": 0}
    assert result.total_entries == 0


def test_the_type_list_is_not_hardcoded():
    """A type absent from ``ALL_TYPES`` today must still be counted.

    ``ALL_TYPES`` is knowingly incomplete (see the spec's "Défaut hors
    périmètre" section). These properties must follow it when it widens,
    so they read the keys they are given rather than a fixed list.
    """
    result = ContextEntriesResult(
        success=True,
        entries={"directory": [{"key_name": "a"}], "root": [{"key_name": "b"}]},
    )

    assert result.entries_by_type == {"directory": 1, "root": 1}
    assert result.total_entries == 2
