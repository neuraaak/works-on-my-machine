#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM PATH UTILS - Pure System Path Utility Functions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Pure system path utility functions for Works On My Machine.

This module contains stateless utility functions for PATH management
that can be used independently without class instantiation.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import os

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# PATH EXTRACTION FUNCTIONS
# ///////////////////////////////////////////////////////////////


def extract_path_from_reg_output(output: str | bytes) -> str:
    """
    Extract PATH value from `reg query` output, supporting REG_SZ and REG_EXPAND_SZ.

    Args:
        output: Registry query output (string or bytes)

    Returns:
        str: Extracted PATH value or empty string if not found
    """
    if not output:
        return ""

    if isinstance(output, (bytes, bytearray)):
        output = output.decode("utf-8", errors="ignore")

    for line in str(output).splitlines():
        if "PATH" in line and ("REG_SZ" in line or "REG_EXPAND_SZ" in line):
            if "REG_EXPAND_SZ" in line:
                parts = line.split("REG_EXPAND_SZ")
            else:
                parts = line.split("REG_SZ")
            if len(parts) > 1:
                return parts[1].strip()

    return ""


# ///////////////////////////////////////////////////////////////
# PATH DEDUPLICATION FUNCTIONS
# ///////////////////////////////////////////////////////////////


def deduplicate_path_entries(path_value: str) -> str:
    """
    Deduplicate PATH entries preserving first occurrence and order.

    Comparison is done case-insensitively on expanded values with trailing
    slashes/backslashes trimmed. The original first textual form is kept.

    Args:
        path_value: Raw PATH string with semicolon-separated entries

    Returns:
        str: Deduplicated PATH string
    """
    if not path_value:
        return path_value

    seen: set[str] = set()
    result_parts: list[str] = []

    for raw_part in path_value.split(";"):
        part = raw_part.strip()
        if not part:
            continue
        try:
            key = os.path.expandvars(part).rstrip("/\\").lower()
            if key in seen:
                continue
            seen.add(key)
            result_parts.append(part)
        except Exception as e:
            # Log but continue processing other entries
            logger.warning(f"Failed to process PATH entry '{part}': {e}")
            continue

    return ";".join(result_parts)
