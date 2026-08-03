#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SHARED MODELS - Domain models shared across layers
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""Immutable domain models shared by services, interfaces and commands."""

from __future__ import annotations

from .template_source import TemplateEntry, TemplateOrigin

__all__ = ["TemplateEntry", "TemplateOrigin"]
