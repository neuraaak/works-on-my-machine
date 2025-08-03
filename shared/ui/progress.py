#!/usr/bin/env python3
"""
Progress utilities using Rich for beautiful progress bars.
"""

from contextlib import contextmanager
from typing import Optional

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)

console = Console()


@contextmanager
def create_progress(
    description: str = "Working...",
    total: Optional[int] = None,
    transient: bool = False,
):
    """Create a progress bar context manager."""
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        transient=transient,
    )

    with progress:
        task = progress.add_task(description, total=total)
        yield progress, task


def create_spinner(description: str = "Working..."):
    """Create a simple spinner."""
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    )

    with progress:
        task = progress.add_task(description, total=None)
        yield progress, task


def track_installation_steps(steps: list, description: str = "Installation Progress"):
    """Track installation steps with progress bar."""
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    )

    with progress:
        task = progress.add_task(description, total=len(steps))

        for i, step in enumerate(steps):
            progress.update(task, description=f"Step {i + 1}/{len(steps)}: {step}")
            yield step
            progress.advance(task)


def create_download_progress(description: str = "Downloading..."):
    """Create a download progress bar."""
    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    )

    with progress:
        task = progress.add_task(description, total=100)
        yield progress, task
