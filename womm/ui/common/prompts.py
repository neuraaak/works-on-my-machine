#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROMPTS - Interactive Prompt Components
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Interactive prompt components for user input.

This module provides convenient wrappers for common prompt scenarios,
including confirmations, path input, and choice selection.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Third-party imports
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from rich.prompt import Confirm, Prompt

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////


def confirm(prompt_text: str, **kwargs) -> bool:
    """
    Show a confirmation prompt.

    Args:
        prompt_text: The confirmation message to display
        **kwargs: Additional arguments passed to Confirm.ask()

    Returns:
        bool: True if user confirms, False otherwise
    """
    return Confirm.ask(prompt_text, **kwargs)


def prompt_path(message: str = "Enter path", **kwargs) -> str:
    """
    Prompt for a file path.

    Args:
        message: The prompt message to display
        **kwargs: Additional arguments passed to Prompt.ask()

    Returns:
        str: The entered path as a string
    """
    return Prompt.ask(message, **kwargs)


def prompt_choice(message: str, choices: list[str], **kwargs) -> str:
    """
    Show a selection prompt with multiple choices.

    Args:
        message: The prompt message to display
        choices: List of string choices to present to user
        **kwargs: Additional arguments passed to InquirerPy select

    Returns:
        str: The selected choice string

    Raises:
        KeyboardInterrupt: If user cancels the prompt
        ValueError: If choices list is empty
    """
    if not choices:
        raise ValueError("Choices list cannot be empty")

    choice_objects = [Choice(value=choice, name=choice) for choice in choices]
    result = inquirer.select(
        message=message,
        choices=choice_objects,
        **kwargs,
    ).execute()

    if result is None:
        raise KeyboardInterrupt("Selection cancelled")

    return result


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["confirm", "prompt_choice", "prompt_path"]
