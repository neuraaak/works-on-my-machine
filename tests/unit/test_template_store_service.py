"""Tests for the template catalog store."""

import json
from pathlib import Path

import pytest

from womm.exceptions.project import ProjectServiceError
from womm.services.project.template_store_service import TemplateStoreService
from womm.shared.models.template_source import TemplateOrigin


@pytest.fixture(autouse=True)
def isolated_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect the WOMM data directory onto a throwaway location."""
    home = tmp_path / "home"
    monkeypatch.setenv("WOMM_HOME", str(home))
    return home


@pytest.fixture
def user_template(tmp_path: Path) -> Path:
    """Build a minimal valid on-disk template."""
    root = tmp_path / "my-service"
    root.mkdir()
    (root / "copier.yml").write_text("project_name:\n  type: str\n", encoding="utf-8")
    return root


def test_official_templates_are_discovered():
    store = TemplateStoreService()

    ids = {entry.id for entry in store.list_templates()}

    assert "python" in ids


def test_official_templates_are_not_persisted(isolated_home: Path):
    store = TemplateStoreService()
    store.list_templates()

    assert not (isolated_home / "templates" / "catalog.json").exists()


def test_add_registers_a_user_template(user_template: Path):
    store = TemplateStoreService()

    entry = store.add("my-service", user_template)

    assert entry.qualified_id == "user/my-service"
    assert entry.origin is TemplateOrigin.USER
    assert store.resolve("my-service").source == user_template


def test_add_persists_only_user_entries(isolated_home: Path, user_template: Path):
    store = TemplateStoreService()
    store.add("my-service", user_template)

    payload = json.loads(
        (isolated_home / "templates" / "catalog.json").read_text(encoding="utf-8")
    )

    assert [item["id"] for item in payload["templates"]] == ["my-service"]


def test_add_refuses_the_official_namespace(user_template: Path):
    store = TemplateStoreService()

    with pytest.raises(ProjectServiceError) as excinfo:
        store.add("official/python", user_template)

    assert excinfo.value.operation == "add_template"


def test_add_refuses_a_duplicate_user_id(user_template: Path):
    store = TemplateStoreService()
    store.add("my-service", user_template)

    with pytest.raises(ProjectServiceError):
        store.add("my-service", user_template)


def test_add_refuses_a_url_source():
    store = TemplateStoreService()

    with pytest.raises(ProjectServiceError) as excinfo:
        store.add("remote", Path("https://github.com/acme/tpl.git"))

    assert "not supported yet" in str(excinfo.value)


def test_add_refuses_a_source_without_copier_yml(tmp_path: Path):
    empty = tmp_path / "empty"
    empty.mkdir()
    store = TemplateStoreService()

    with pytest.raises(ProjectServiceError):
        store.add("empty", empty)


def test_add_refuses_an_identifier_with_path_separators(user_template: Path):
    store = TemplateStoreService()

    with pytest.raises(ProjectServiceError):
        store.add("../escape", user_template)


def test_short_id_prefers_official_and_collision_requires_qualification(
    user_template: Path,
):
    store = TemplateStoreService()
    store.add("python", user_template)

    with pytest.raises(ProjectServiceError) as excinfo:
        store.resolve("python")

    assert "ambiguous" in str(excinfo.value).lower()
    assert store.resolve("official/python").origin is TemplateOrigin.OFFICIAL
    assert store.resolve("user/python").origin is TemplateOrigin.USER


def test_resolve_unknown_identifier_fails():
    store = TemplateStoreService()

    with pytest.raises(ProjectServiceError) as excinfo:
        store.resolve("does-not-exist")

    assert excinfo.value.operation == "resolve_template"


def test_remove_deletes_a_user_entry(user_template: Path):
    store = TemplateStoreService()
    store.add("my-service", user_template)

    store.remove("my-service")

    with pytest.raises(ProjectServiceError):
        store.resolve("user/my-service")


def test_remove_refuses_an_official_entry():
    store = TemplateStoreService()

    with pytest.raises(ProjectServiceError) as excinfo:
        store.remove("official/python")

    assert excinfo.value.operation == "remove_template"


def test_update_replaces_the_source(user_template: Path, tmp_path: Path):
    store = TemplateStoreService()
    store.add("my-service", user_template)
    moved = tmp_path / "moved"
    moved.mkdir()
    (moved / "copier.yml").write_text("project_name:\n  type: str\n", encoding="utf-8")

    entry = store.update("my-service", moved)

    assert entry.source == moved
    assert store.resolve("user/my-service").source == moved


def test_corrupted_catalog_raises_a_service_error(isolated_home: Path):
    catalog = isolated_home / "templates" / "catalog.json"
    catalog.parent.mkdir(parents=True, exist_ok=True)
    catalog.write_text("{not json", encoding="utf-8")
    store = TemplateStoreService()

    with pytest.raises(ProjectServiceError) as excinfo:
        store.list_templates()

    assert excinfo.value.operation == "load_catalog"


def test_missing_catalog_yields_official_templates_only():
    store = TemplateStoreService()

    entries = store.list_templates()

    assert entries
    assert all(entry.origin is TemplateOrigin.OFFICIAL for entry in entries)


def test_catalog_write_is_atomic(isolated_home: Path, user_template: Path):
    store = TemplateStoreService()
    store.add("my-service", user_template)
    leftovers = list((isolated_home / "templates").glob("*.tmp"))

    assert leftovers == []
