#!/usr/bin/env python3
"""
Final test for Questionary integration.
"""

import questionary


def test_direct_questionary():
    """Test Questionary directly."""
    print("Testing Questionary directly...")

    # Test selection
    choice = questionary.select(
        "Choose an option:",
        choices=["Option 1", "Option 2", "Option 3"],
        qmark="❓",
        pointer="→",
    ).ask()

    print(f"Selected: {choice}")

    # Test confirmation
    confirmed = questionary.confirm("Confirm your choice?").ask()
    print(f"Confirmed: {confirmed}")


if __name__ == "__main__":
    test_direct_questionary()
