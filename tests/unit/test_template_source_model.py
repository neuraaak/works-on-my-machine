"""Tests for the template source model."""

from pathlib import Path

import pytest

from womm.shared.models.template_source import TemplateEntry, TemplateOrigin
from womm.shared.results.template_results import (
    TemplateListResult,
    TemplateStoreResult,
)


def test_qualified_id_prefixes_with_origin():
    entry = TemplateEntry(
        id="python",
        origin=TemplateOrigin.OFFICIAL,
        source=Path("/assets/copier/official/python"),
    )
    assert entry.qualified_id == "official/python"


def test_user_entry_is_namespaced_under_user():
    entry = TemplateEntry(
        id="my-service",
        origin=TemplateOrigin.USER,
        source=Path("/home/me/tpl"),
    )
    assert entry.qualified_id == "user/my-service"


def test_entry_is_immutable():
    entry = TemplateEntry(
        id="python",
        origin=TemplateOrigin.OFFICIAL,
        source=Path("/x"),
    )
    with pytest.raises(AttributeError):
        entry.id = "other"  # type: ignore[misc]


def test_store_result_defaults_to_no_entry():
    result = TemplateStoreResult(success=True, message="ok")
    assert result.entry is None
    assert bool(result) is True


def test_list_result_defaults_to_no_entries():
    result = TemplateListResult(success=True)
    assert result.entries is None
