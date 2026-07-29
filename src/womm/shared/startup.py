#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SHARED STARTUP - Early CLI Initialization
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""Run one-time startup tasks before UI and logging imports."""

from __future__ import annotations

# Local imports
from .migration import migrate_legacy_data_layout

# The UI logging bridge resolves its output directory at import time. Keep this
# import-time initialization before that bridge so legacy logs migrate first.
migrate_legacy_data_layout()
