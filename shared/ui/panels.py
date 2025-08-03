#!/usr/bin/env python3
"""
Panel utilities using Rich for beautiful panel output.
"""

from typing import Any, Optional

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def create_panel(
    content: Any, title: Optional[str] = None, border_style: str = "blue", **kwargs
) -> Panel:
    """Create a Rich panel with the given content."""
    return Panel(content, title=title, border_style=border_style, **kwargs)


def create_info_panel(title: str, content: str, style: str = "cyan", **kwargs) -> Panel:
    """Create an info panel with title and content."""
    text = Text(content, style=style)
    return Panel(
        Align(text, align="left"), title=f"ℹ️ {title}", border_style="cyan", **kwargs
    )


def create_success_panel(title: str, content: str, **kwargs) -> Panel:
    """Create a success panel with green styling."""
    text = Text(content, style="green")
    return Panel(
        Align(text, align="left"), title=f"✅ {title}", border_style="green", **kwargs
    )


def create_error_panel(title: str, content: str, **kwargs) -> Panel:
    """Create an error panel with red styling."""
    text = Text(content, style="red")
    return Panel(
        Align(text, align="left"), title=f"❌ {title}", border_style="red", **kwargs
    )


def create_warning_panel(title: str, content: str, **kwargs) -> Panel:
    """Create a warning panel with yellow styling."""
    text = Text(content, style="yellow")
    return Panel(
        Align(text, align="left"), title=f"⚠️ {title}", border_style="yellow", **kwargs
    )


def create_installation_panel(
    step: str, description: str, status: str = "pending", **kwargs
) -> Panel:
    """Create an installation step panel."""
    if status == "success":
        icon = "✅"
        style = "green"
    elif status == "error":
        icon = "❌"
        style = "red"
    elif status == "warning":
        icon = "⚠️"
        style = "yellow"
    else:
        icon = "⏳"
        style = "blue"

    content = f"{description}"
    text = Text(content, style=style)

    return Panel(
        Align(text, align="left"), title=f"{icon} {step}", border_style=style, **kwargs
    )
