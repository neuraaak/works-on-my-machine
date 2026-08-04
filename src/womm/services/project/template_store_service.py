#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEMPLATE STORE SERVICE - Copier template catalog
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""Catalog of Copier templates known to WOMM.

Official templates ship inside the wheel and are discovered at read time;
they are never written to the user catalog. ``catalog.json`` holds only
user-registered templates.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import yaml

from womm.exceptions.project import ProjectServiceError
from womm.shared.models.template_source import TemplateEntry, TemplateOrigin
from womm.shared.paths import (
    packaged_copier_official,
    template_catalog_file,
    user_templates_dir,
)

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

# Manifest a template root must expose to be considered valid.
TEMPLATE_MANIFEST = "copier.yml"

# Key carrying WOMM metadata inside a template manifest.
WOMM_METADATA_KEY = "_womm"

# Prefixes that mark a source as remote. Remote sources are out of scope
# until an explicit trust model exists.
REMOTE_PREFIXES = (
    "http://",
    "https://",
    "http:/",
    "https:/",
    "http:\\",
    "https:\\",
    "git@",
    "git+",
    "gh:",
    "gl:",
)

# ///////////////////////////////////////////////////////////////
# SERVICE
# ///////////////////////////////////////////////////////////////


class TemplateStoreService:
    """Read and write the template catalog."""

    # ///////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////

    def list_templates(self) -> list[TemplateEntry]:
        """List every known template, official first.

        Returns:
            list[TemplateEntry]: Entries sorted by qualified identifier.

        Raises:
            ProjectServiceError: If the user catalog cannot be read.
        """
        entries = self._discover_official() + self._load_user_entries()
        return sorted(entries, key=lambda entry: entry.qualified_id)

    def resolve(self, identifier: str) -> TemplateEntry:
        """Resolve an identifier to a single template.

        A qualified identifier (``official/python``) selects one origin. A
        short identifier resolves across origins and fails when ambiguous.

        Args:
            identifier: Qualified or short template identifier.

        Returns:
            TemplateEntry: The matching entry.

        Raises:
            ProjectServiceError: If unknown or ambiguous.
        """
        entries = self.list_templates()

        qualified = [e for e in entries if e.qualified_id == identifier]
        if qualified:
            return qualified[0]

        matches = [e for e in entries if e.id == identifier]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            names = ", ".join(e.qualified_id for e in matches)
            raise ProjectServiceError(
                operation="resolve_template",
                reason=f"Template identifier is ambiguous: {identifier}",
                details=f"Candidates: {names}. Use a qualified identifier.",
            )
        raise ProjectServiceError(
            operation="resolve_template",
            reason=f"Unknown template: {identifier}",
        )

    def add(self, identifier: str, source: Path) -> TemplateEntry:
        """Register a local template under the user namespace.

        Args:
            identifier: Short identifier, without any separator.
            source: Directory holding ``copier.yml``.

        Returns:
            TemplateEntry: The registered entry.

        Raises:
            ProjectServiceError: If the identifier or source is refused.
        """
        self._validate_identifier(identifier, operation="add_template")
        self._validate_source(source, operation="add_template")

        existing = self._load_user_entries()
        if any(entry.id == identifier for entry in existing):
            raise ProjectServiceError(
                operation="add_template",
                reason=f"Template already registered: {identifier}",
            )

        entry = self._build_user_entry(identifier, source)
        self._save_user_entries([*existing, entry])
        return entry

    def remove(self, identifier: str) -> TemplateEntry:
        """Unregister a user template.

        Args:
            identifier: Qualified or short identifier.

        Returns:
            TemplateEntry: The removed entry.

        Raises:
            ProjectServiceError: If unknown or not user-owned.
        """
        entry = self.resolve(identifier)
        if entry.origin is not TemplateOrigin.USER:
            raise ProjectServiceError(
                operation="remove_template",
                reason=f"Official templates cannot be removed: {identifier}",
            )
        remaining = [item for item in self._load_user_entries() if item.id != entry.id]
        self._save_user_entries(remaining)
        return entry

    def update(self, identifier: str, source: Path) -> TemplateEntry:
        """Point an existing user template at a new source.

        Args:
            identifier: Qualified or short identifier.
            source: New directory holding ``copier.yml``.

        Returns:
            TemplateEntry: The updated entry.

        Raises:
            ProjectServiceError: If unknown, not user-owned, or source invalid.
        """
        entry = self.resolve(identifier)
        if entry.origin is not TemplateOrigin.USER:
            raise ProjectServiceError(
                operation="update_template",
                reason=f"Official templates cannot be updated: {identifier}",
            )
        self._validate_source(source, operation="update_template")
        updated = self._build_user_entry(entry.id, source)
        remaining = [item for item in self._load_user_entries() if item.id != entry.id]
        self._save_user_entries([*remaining, updated])
        return updated

    # ///////////////////////////////////////////////////////////
    # PRIVATE METHODS - DISCOVERY
    # ///////////////////////////////////////////////////////////

    def _discover_official(self) -> list[TemplateEntry]:
        """Enumerate shipped templates, without persisting anything."""
        root = Path(str(packaged_copier_official()))
        if not root.is_dir():
            return []
        entries: list[TemplateEntry] = []
        for candidate in sorted(root.iterdir()):
            manifest = candidate / TEMPLATE_MANIFEST
            if not manifest.is_file():
                continue
            metadata = self._read_metadata(manifest)
            entries.append(
                TemplateEntry(
                    id=candidate.name,
                    origin=TemplateOrigin.OFFICIAL,
                    source=candidate,
                    version=str(metadata.get("version", "")),
                    description=str(metadata.get("description", "")),
                )
            )
        return entries

    def _read_metadata(self, manifest: Path) -> dict[str, Any]:
        """Read the ``_womm`` block of a template manifest, tolerantly."""
        try:
            payload = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError):
            return {}
        block = payload.get(WOMM_METADATA_KEY, {})
        return block if isinstance(block, dict) else {}

    # ///////////////////////////////////////////////////////////
    # PRIVATE METHODS - CATALOG IO
    # ///////////////////////////////////////////////////////////

    def _load_user_entries(self) -> list[TemplateEntry]:
        """Read the user catalog, treating absence as empty."""
        catalog = template_catalog_file()
        if not catalog.is_file():
            return []
        try:
            payload = json.loads(catalog.read_text(encoding="utf-8"))
            items = payload["templates"]
            return [
                TemplateEntry(
                    id=item["id"],
                    origin=TemplateOrigin.USER,
                    source=Path(item["source"]),
                    version=item.get("version", ""),
                    description=item.get("description", ""),
                )
                for item in items
            ]
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
            raise ProjectServiceError(
                operation="load_catalog",
                reason=f"Template catalog is unreadable: {catalog}",
                details=str(exc),
            ) from exc

    def _save_user_entries(self, entries: list[TemplateEntry]) -> None:
        """Write the user catalog atomically."""
        catalog = template_catalog_file()
        user_templates_dir()
        payload = {
            "templates": [
                {
                    "id": entry.id,
                    "source": str(entry.source),
                    "version": entry.version,
                    "description": entry.description,
                }
                for entry in sorted(entries, key=lambda item: item.id)
            ]
        }
        handle, temp_name = tempfile.mkstemp(dir=str(catalog.parent), suffix=".tmp")
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as stream:
                json.dump(payload, stream, indent=2)
            os.replace(temp_name, catalog)
        except OSError as exc:
            Path(temp_name).unlink(missing_ok=True)
            raise ProjectServiceError(
                operation="save_catalog",
                reason=f"Template catalog could not be written: {catalog}",
                details=str(exc),
            ) from exc

    # ///////////////////////////////////////////////////////////
    # PRIVATE METHODS - VALIDATION
    # ///////////////////////////////////////////////////////////

    def _validate_identifier(self, identifier: str, *, operation: str) -> None:
        """Reject namespaced, empty or path-like identifiers."""
        if not identifier or identifier != identifier.strip():
            raise ProjectServiceError(
                operation=operation,
                reason="Template identifier must not be empty",
            )
        if "/" in identifier or "\\" in identifier or identifier.startswith("."):
            raise ProjectServiceError(
                operation=operation,
                reason=f"Template identifier must be a plain name: {identifier}",
                details="The official/ namespace is reserved and separators "
                "are not allowed.",
            )

    def _validate_source(self, source: Path, *, operation: str) -> None:
        """Reject remote sources and sources without a manifest."""
        raw = str(source)
        if raw.startswith(REMOTE_PREFIXES):
            raise ProjectServiceError(
                operation=operation,
                reason=f"Remote template sources are not supported yet: {raw}",
            )
        resolved = source.expanduser().resolve()
        if not (resolved / TEMPLATE_MANIFEST).is_file():
            raise ProjectServiceError(
                operation=operation,
                reason=f"Not a Copier template: {source}",
                details=f"Expected a {TEMPLATE_MANIFEST} file at the root.",
            )

    def _build_user_entry(self, identifier: str, source: Path) -> TemplateEntry:
        """Build a user entry, reading metadata from the manifest."""
        resolved = source.expanduser().resolve()
        metadata = self._read_metadata(resolved / TEMPLATE_MANIFEST)
        return TemplateEntry(
            id=identifier,
            origin=TemplateOrigin.USER,
            source=resolved,
            version=str(metadata.get("version", "")),
            description=str(metadata.get("description", "")),
        )


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["TemplateStoreService"]
