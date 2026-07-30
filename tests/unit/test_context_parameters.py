#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST CONTEXT PARAMETERS - Instance independence
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Tests for the per-call independence of context parameters.

The class used to be a process-wide singleton, so two successive
configurations accumulated each other's flags. These tests pin the fixed
behaviour: every call produces a configuration of its own.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from womm.services.context import ContextParameters, ContextType

# ///////////////////////////////////////////////////////////////
# INSTANCE INDEPENDENCE
# ///////////////////////////////////////////////////////////////


def test_two_instances_are_distinct_objects() -> None:
    assert ContextParameters() is not ContextParameters()


def test_mutating_one_instance_leaves_the_other_empty() -> None:
    first = ContextParameters()
    second = ContextParameters()

    first.add_context_type(ContextType.ROOT)

    assert first.context_types == {ContextType.ROOT}
    assert second.context_types == set()


# ///////////////////////////////////////////////////////////////
# FROM FLAGS
# ///////////////////////////////////////////////////////////////


def test_from_flags_does_not_accumulate_across_incompatible_calls() -> None:
    root_only = ContextParameters.from_flags(root=True)
    file_only = ContextParameters.from_flags(file=True)

    assert root_only.context_types == {ContextType.ROOT}
    assert file_only.context_types == {ContextType.FILE}


def test_from_flags_defaults_are_not_polluted_by_an_earlier_call() -> None:
    ContextParameters.from_flags(root=True, file=True, files=True)
    defaulted = ContextParameters.from_flags()

    assert defaulted.context_types == {ContextType.DIRECTORY, ContextType.BACKGROUND}


def test_from_flags_does_not_carry_file_types_over() -> None:
    ContextParameters.from_flags(file=True, file_types=["image"])
    plain = ContextParameters.from_flags(file=True)

    assert plain.file_types == set()
    assert plain.get_file_extensions() == set()
