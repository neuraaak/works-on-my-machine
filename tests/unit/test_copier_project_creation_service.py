"""Tests for the Copier-backed project creation service."""

from pathlib import Path

import pytest

from womm.exceptions.project import ProjectServiceError
from womm.services.project.copier_project_creation_service import (
    CopierProjectCreationService,
    ProjectCreationRequest,
)

TEMPLATE_YML = """\
project_name:
  type: str
  default: demo
"""


@pytest.fixture
def template(tmp_path: Path) -> Path:
    """Build a minimal on-disk Copier template."""
    root = tmp_path / "tpl"
    (root / "template").mkdir(parents=True)
    (root / "copier.yml").write_text(
        TEMPLATE_YML + "_subdirectory: template\n", encoding="utf-8"
    )
    (root / "template" / "README.md.jinja").write_text(
        "# {{ project_name }}\n", encoding="utf-8"
    )
    return root


def test_create_renders_the_template(template: Path, tmp_path: Path):
    destination = tmp_path / "out"
    service = CopierProjectCreationService()

    result = service.create(
        ProjectCreationRequest(
            template_source=template,
            destination=destination,
            answers={"project_name": "acme"},
            defaults=True,
        )
    )

    assert result == destination
    assert (destination / "README.md").read_text(encoding="utf-8") == "# acme\n"


def test_pretend_writes_nothing(template: Path, tmp_path: Path):
    destination = tmp_path / "out"
    service = CopierProjectCreationService()

    service.create(
        ProjectCreationRequest(
            template_source=template,
            destination=destination,
            answers={"project_name": "acme"},
            defaults=True,
            pretend=True,
        )
    )

    assert not (destination / "README.md").exists()


def test_defaults_are_used_when_answers_are_missing(template: Path, tmp_path: Path):
    destination = tmp_path / "out"
    service = CopierProjectCreationService()

    service.create(
        ProjectCreationRequest(
            template_source=template,
            destination=destination,
            answers={},
            defaults=True,
        )
    )

    assert (destination / "README.md").read_text(encoding="utf-8") == "# demo\n"


def test_non_empty_destination_is_refused(template: Path, tmp_path: Path):
    destination = tmp_path / "out"
    destination.mkdir()
    (destination / "keep.txt").write_text("x", encoding="utf-8")
    service = CopierProjectCreationService()

    with pytest.raises(ProjectServiceError) as excinfo:
        service.create(
            ProjectCreationRequest(
                template_source=template,
                destination=destination,
                answers={},
                defaults=True,
            )
        )

    assert excinfo.value.operation == "check_destination"


def test_force_allows_a_non_empty_destination(template: Path, tmp_path: Path):
    destination = tmp_path / "out"
    destination.mkdir()
    (destination / "keep.txt").write_text("x", encoding="utf-8")
    service = CopierProjectCreationService()

    service.create(
        ProjectCreationRequest(
            template_source=template,
            destination=destination,
            answers={"project_name": "acme"},
            defaults=True,
            force=True,
        )
    )

    assert (destination / "README.md").exists()
    assert (destination / "keep.txt").exists()


def test_pretend_bypasses_the_destination_guard(template: Path, tmp_path: Path):
    destination = tmp_path / "out"
    destination.mkdir()
    (destination / "keep.txt").write_text("x", encoding="utf-8")
    service = CopierProjectCreationService()

    service.create(
        ProjectCreationRequest(
            template_source=template,
            destination=destination,
            answers={},
            defaults=True,
            pretend=True,
        )
    )

    assert not (destination / "README.md").exists()


def test_missing_template_raises_a_service_error(tmp_path: Path):
    service = CopierProjectCreationService()

    with pytest.raises(ProjectServiceError) as excinfo:
        service.create(
            ProjectCreationRequest(
                template_source=tmp_path / "nope",
                destination=tmp_path / "out",
                answers={},
                defaults=True,
            )
        )

    assert excinfo.value.operation == "create_project"


def test_render_error_raises_a_service_error(tmp_path: Path):
    broken = tmp_path / "broken"
    (broken / "template").mkdir(parents=True)
    (broken / "copier.yml").write_text("_subdirectory: template\n", encoding="utf-8")
    (broken / "template" / "x.jinja").write_text(
        "{{ undefined_filter | nope }}", encoding="utf-8"
    )
    service = CopierProjectCreationService()

    with pytest.raises(ProjectServiceError) as excinfo:
        service.create(
            ProjectCreationRequest(
                template_source=broken,
                destination=tmp_path / "out",
                answers={},
                defaults=True,
            )
        )

    assert excinfo.value.operation == "create_project"
