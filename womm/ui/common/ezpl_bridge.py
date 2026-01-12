#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EZPL BRIDGE - Ezpl Bridge for UI Compatibility
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Ezpl Bridge for Works On My Machine.

This module provides a bridge class that extends Ezpl with an ExtendedPrinter
that adds utility methods for WOMM-specific functionality.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from collections.abc import Generator
from contextlib import contextmanager, suppress
from typing import Any

# Third-party imports
from ezpl import EzLogger, Ezpl, LogLevel
from ezpl.handlers.console import ConsolePrinter
from ezpl.handlers.wizard.core import RichWizard
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table
from rich.text import Text

# Local imports
from ...shared.configs.logging_config import LoggingConfig

# ///////////////////////////////////////////////////////////////
# EXTENDED PRINTER CLASS
# ///////////////////////////////////////////////////////////////


class ExtendedPrinter(ConsolePrinter):
    """
    Extended printer with additional utility methods for WOMM.

    Inherits from ConsolePrinter and adds:
    - Header/separator utilities
    - Command/result display
    - Dry-run messages
    - Panel/Table creation (returning objects)
    - Progress context managers (delegated to wizard)
    """

    def __init__(
        self,
        level: str = "INFO",
        indent_step: int = 3,
        indent_symbol: str = ">",
        base_indent_symbol: str = "~",
    ) -> None:
        """
        Initialize the extended printer.

        Args:
            level: The desired logging level
            indent_step: Number of spaces for each indentation level
            indent_symbol: Symbol for indentation levels
            base_indent_symbol: Symbol for the base indentation
        """
        super().__init__(
            level=level,
            indent_step=indent_step,
            indent_symbol=indent_symbol,
            base_indent_symbol=base_indent_symbol,
        )

    # ///////////////////////////////////////////////////////////////
    # PROPERTIES
    # ///////////////////////////////////////////////////////////////

    @property
    def wizard(self) -> RichWizard:
        """Get the Rich Wizard instance (property for convenience)."""
        return self._wizard

    # ///////////////////////////////////////////////////////////////
    # UTILITY METHODS
    # ///////////////////////////////////////////////////////////////

    def print_header(self, title: str, **kwargs: Any) -> None:
        """
        Display a header with separators.

        Args:
            title: Header title
            **kwargs: Additional arguments (passed to console.print)
        """
        self._console.print(f"{':' * 80}", style="dim black", **kwargs)
        self._console.print(
            f"** {title} **",
            style="bold black",
            justify="center",
            width=80,
            **kwargs,
        )
        self._console.print(f"{':' * 80}", style="dim black", **kwargs)
        self._console.print("")

    def print_separator(self, separator: str = "-", **kwargs: Any) -> None:
        """
        Display a separation line.

        Args:
            separator: Separator character
            **kwargs: Additional arguments (passed to console.print)
        """
        self._console.print(separator * 80, style="dim white", **kwargs)

    def print_command(self, command: str, **kwargs: Any) -> None:
        """
        Display an executed command.

        Args:
            command: Command string
            **kwargs: Additional arguments (passed to console.print)
        """
        self._console.print(f"$ {command}", style="bold cyan", **kwargs)

    def print_result(self, result: str, success: bool = True, **kwargs: Any) -> None:
        """
        Display the result of an operation.

        Args:
            result: Result message
            success: Whether operation was successful
            **kwargs: Additional arguments (passed to console.print)
        """
        style = "bold green" if success else "bold red"
        self._console.print(result, style=style, **kwargs)

    def print_dry_run_message(self, operation: str, details: str = "") -> None:
        """
        Print a consistent dry-run message.

        Args:
            operation: The operation that would be performed
            details: Additional details about the operation
        """
        message = f"🔍 [DRY-RUN] Would {operation}"
        if details:
            message += f": {details}"
        self.info(message)

    def print_dry_run_success(self) -> None:
        """Print a consistent dry-run success message."""
        self.success("✅ Dry run completed successfully")

    def print_dry_run_warning(self) -> None:
        """Print a consistent dry-run warning message."""
        self.warning("⚠️  DRY-RUN MODE - No changes will be made")

    # ///////////////////////////////////////////////////////////////
    # PANEL CREATION METHODS (RETURN PANEL OBJECTS)
    # ///////////////////////////////////////////////////////////////

    def create_panel(
        self,
        content: Any,
        title: str | None = None,
        border_style: str = "blue",
        width: int = 80,
        **kwargs: Any,
    ) -> Panel:
        """
        Create a Rich panel with the given content (returns Panel object).

        Args:
            content: Panel content
            title: Optional panel title
            border_style: Panel border style
            width: Panel width
            **kwargs: Additional Panel arguments

        Returns:
            Panel object (not displayed)
        """
        return Panel(
            content, title=title, border_style=border_style, width=width, **kwargs
        )

    def create_info_panel(
        self,
        title: str,
        content: str,
        style: str = "cyan",
        border_style: str = "cyan",
        width: int = 80,
        **kwargs: Any,
    ) -> Panel:
        """
        Create an info panel with title and content (returns Panel object).

        Args:
            title: Panel title
            content: Panel content
            style: Content text style
            border_style: Panel border style
            width: Panel width
            **kwargs: Additional Panel arguments

        Returns:
            Panel object (not displayed)
        """
        text = Text(content, style=style)
        return Panel(
            Align(text, align="left"),
            title=f"ℹ️ {title}",
            border_style=border_style,
            width=width,
            **kwargs,
        )

    def create_success_panel(
        self,
        title: str,
        content: str,
        border_style: str = "green",
        width: int = 80,
        **kwargs: Any,
    ) -> Panel:
        """
        Create a success panel with green styling (returns Panel object).

        Args:
            title: Panel title
            content: Panel content
            border_style: Panel border style
            width: Panel width
            **kwargs: Additional Panel arguments

        Returns:
            Panel object (not displayed)
        """
        text = Text(content, style="green")
        return Panel(
            Align(text, align="left"),
            title=f"✅ {title}",
            border_style=border_style,
            width=width,
            **kwargs,
        )

    def create_error_panel(
        self,
        title: str,
        content: str,
        border_style: str = "red",
        width: int = 80,
        **kwargs: Any,
    ) -> Panel:
        """
        Create an error panel with red styling (returns Panel object).

        Args:
            title: Panel title
            content: Panel content
            border_style: Panel border style
            width: Panel width
            **kwargs: Additional Panel arguments

        Returns:
            Panel object (not displayed)
        """
        text = Text(content, style="red")
        return Panel(
            Align(text, align="left"),
            title=f"❌ {title}",
            border_style=border_style,
            width=width,
            **kwargs,
        )

    def create_warning_panel(
        self,
        title: str,
        content: str,
        border_style: str = "yellow",
        width: int = 80,
        **kwargs: Any,
    ) -> Panel:
        """
        Create a warning panel with yellow styling (returns Panel object).

        Args:
            title: Panel title
            content: Panel content
            border_style: Panel border style
            width: Panel width
            **kwargs: Additional Panel arguments

        Returns:
            Panel object (not displayed)
        """
        text = Text(content, style="yellow")
        return Panel(
            Align(text, align="left"),
            title=f"⚠️ {title}",
            border_style=border_style,
            width=width,
            **kwargs,
        )

    def create_installation_panel(
        self,
        step: str,
        description: str,
        status: str = "pending",
        border_style: str = "blue",
        width: int = 80,
        **kwargs: Any,
    ) -> Panel:
        """
        Create an installation step panel (returns Panel object).

        Args:
            step: Installation step name
            description: Step description
            status: Status ("success", "error", "warning", "pending")
            border_style: Panel border style
            width: Panel width
            **kwargs: Additional Panel arguments

        Returns:
            Panel object (not displayed)
        """
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

        text = Text(description, style=style)
        return Panel(
            Align(text, align="left"),
            title=f"{icon} {step}",
            border_style=border_style,
            width=width,
            **kwargs,
        )

    # ///////////////////////////////////////////////////////////////
    # TABLE CREATION METHODS (RETURN TABLE OBJECTS)
    # ///////////////////////////////////////////////////////////////

    def create_table(
        self,
        title: str,
        columns: list[str] | list[tuple[str, str | None, bool]],
        rows: list[list[Any]] | None = None,
        show_header: bool = True,
        **kwargs: Any,
    ) -> Table:
        """
        Create a Rich table with the given data (returns Table object).

        Args:
            title: Table title
            columns: List of column names (str) or list of tuples (name, style, no_wrap)
            rows: List of row data (optional, can be added later with add_row)
            show_header: Whether to show column headers
            **kwargs: Additional Table arguments

        Returns:
            Table object (not displayed)
        """
        table = Table(title=title, show_header=show_header, **kwargs)

        # Add columns
        for column in columns:
            if isinstance(column, tuple):
                # Custom column: (name, style, no_wrap)
                name, style, no_wrap = column
                table.add_column(name, style=style or "cyan", no_wrap=no_wrap)
            else:
                # Simple column name
                table.add_column(column, style="cyan", no_wrap=True)

        # Add rows if provided
        if rows:
            for row in rows:
                table.add_row(*[str(cell) for cell in row])

        return table

    def create_status_table(
        self,
        title: str,
        data: list[dict[str, Any]],
        status_column: str = "Status",
        **kwargs: Any,
    ) -> Table:
        """
        Create a status table with colored status indicators (returns Table object).

        Args:
            title: Table title
            data: List of dictionaries representing table rows
            status_column: Name of the status column
            **kwargs: Additional Table arguments

        Returns:
            Table object (not displayed)
        """
        if not data:
            return self.create_table(title, ["No data"], [[]])

        # Get columns from first row
        columns = list(data[0].keys())

        table = Table(title=title, show_header=True, **kwargs)

        # Add columns
        for column in columns:
            if column == status_column:
                table.add_column(column, style="bold", no_wrap=True)
            else:
                table.add_column(column, style="cyan", no_wrap=True)

        # Add rows with status styling
        for row_data in data:
            row = []
            for column in columns:
                value = str(row_data.get(column, ""))
                if column == status_column:
                    value_lower = value.lower()
                    if "success" in value_lower or "ok" in value_lower:
                        row.append(f"✅ {value}")
                    elif "error" in value_lower or "fail" in value_lower:
                        row.append(f"❌ {value}")
                    elif "warning" in value_lower:
                        row.append(f"⚠️ {value}")
                    else:
                        row.append(f"ℹ️ {value}")
                else:
                    row.append(value)
            table.add_row(*row)

        return table

    def create_dependency_table(self, dependencies: dict[str, str]) -> Table:
        """
        Create a table for displaying dependencies (returns Table object).

        Args:
            dependencies: Dictionary mapping tool names to versions

        Returns:
            Table object (not displayed)
        """
        table = Table(title="Dependencies", show_header=True)
        table.add_column("Tool", style="cyan", no_wrap=True)
        table.add_column("Version", style="green", no_wrap=True)
        table.add_column("Status", style="bold", no_wrap=True)

        for tool, version in dependencies.items():
            if version:
                table.add_row(tool, version, "✅ Available")
            else:
                table.add_row(tool, "N/A", "❌ Missing")

        return table

    def create_command_table(self, commands: list[dict[str, str]]) -> Table:
        """
        Create a table for displaying available commands (returns Table object).

        Args:
            commands: List of command dictionaries

        Returns:
            Table object (not displayed)
        """
        table = Table(title="Available Commands", show_header=True)
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description", style="green")
        table.add_column("Category", style="yellow", no_wrap=True)

        for cmd in commands:
            table.add_row(
                cmd.get("command", ""),
                cmd.get("description", ""),
                cmd.get("category", ""),
            )

        return table

    def create_dictionary_table(self, dictionaries: list[dict[str, Any]]) -> Table:
        """
        Create a table for displaying CSpell dictionaries (returns Table object).

        Args:
            dictionaries: List of dictionary information dictionaries

        Returns:
            Table object (not displayed)
        """
        table = Table(title="CSpell Dictionaries", show_header=True)
        table.add_column("File", style="cyan", no_wrap=True)
        table.add_column("Words", style="green", no_wrap=True)
        table.add_column("Size", style="yellow", no_wrap=True)
        table.add_column("Status", style="bold", no_wrap=True)

        for dict_info in dictionaries:
            file_name = dict_info.get("file", "")
            word_count = dict_info.get("words", 0)
            file_size = dict_info.get("size", "N/A")
            status = dict_info.get("status", "Available")

            # Format status with emoji
            if "available" in status.lower():
                status_display = "✅ Available"
            elif "error" in status.lower():
                status_display = "❌ Error"
            else:
                status_display = f"ℹ️ {status}"

            table.add_row(file_name, str(word_count), str(file_size), status_display)

        return table

    def create_backup_table(self, backups: list[dict[str, Any]]) -> Table:
        """
        Create a table for displaying PATH backup information (returns Table object).

        Args:
            backups: List of backup information dictionaries

        Returns:
            Table object (not displayed)
        """
        table = Table(title="PATH Backups", show_header=True)
        table.add_column("Backup File", style="cyan", no_wrap=True)
        table.add_column("Size", style="green", no_wrap=True)
        table.add_column("Modified", style="yellow", no_wrap=True)
        table.add_column("Description", style="white")

        for backup in backups:
            # Format size
            size = backup.get("size", 0)
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size // 1024} KB"
            else:
                size_str = f"{size // (1024 * 1024)} MB"

            # Truncate description if too long
            description = backup.get("description", "No description")
            if len(description) > 50:
                description = description[:47] + "..."

            table.add_row(
                backup.get("name", ""),
                size_str,
                backup.get("modified", ""),
                description,
            )

        return table

    # ///////////////////////////////////////////////////////////////
    # PROGRESS CONTEXT MANAGERS (DELEGATED TO WIZARD)
    # ///////////////////////////////////////////////////////////////

    @contextmanager
    def create_progress(
        self,
        description: str = "Working...",
        total: int | None = None,
        transient: bool = False,
    ) -> Generator[tuple[Progress, int], None, None]:
        """
        Create a progress bar context manager (delegated to wizard).

        Args:
            description: Progress description
            total: Total number of items (None for indeterminate)
            transient: Whether to clear progress on exit

        Yields:
            tuple of (Progress, task_id)
        """
        with self.wizard.progress(description, total, transient) as (progress, task):
            yield progress, task

    @contextmanager
    def create_spinner(
        self, description: str = "Working..."
    ) -> Generator[tuple[Progress, int], None, None]:
        """
        Create a simple spinner with description (delegated to wizard).

        Args:
            description: Spinner description

        Yields:
            tuple of (Progress, task_id)
        """
        with self.wizard.spinner(description) as (progress, task):
            yield progress, task

    @contextmanager
    def create_spinner_with_status(
        self, description: str = "Working..."
    ) -> Generator[tuple[Progress, int], None, None]:
        """
        Create a spinner that can update status messages (delegated to wizard).

        Args:
            description: Spinner description

        Yields:
            tuple of (Progress, task_id)
        """
        with self.wizard.spinner_with_status(description) as (progress, task):
            yield progress, task

    @contextmanager
    def create_download_progress(
        self, description: str = "Downloading..."
    ) -> Generator[tuple[Progress, int], None, None]:
        """
        Create a download progress bar (delegated to wizard).

        Args:
            description: Download description

        Yields:
            tuple of (Progress, task_id)
        """
        with self.wizard.download_progress(description) as (progress, task):
            yield progress, task

    @contextmanager
    def create_file_download_progress(
        self, filename: str, total_size: int, description: str = "Downloading file..."
    ) -> Generator[tuple[Progress, int], None, None]:
        """
        Create a progress bar for downloading a specific file (delegated to wizard).

        Args:
            filename: Name of the file being downloaded
            total_size: Total size in bytes
            description: Main description

        Yields:
            tuple of (Progress, task_id)
        """
        with self.wizard.file_download_progress(filename, total_size, description) as (
            progress,
            task,
        ):
            yield progress, task

    @contextmanager
    def create_dependency_progress(
        self, dependencies: list[str], description: str = "Installing dependencies..."
    ) -> Generator[tuple[Progress, int, str], None, None]:
        """
        Create a progress bar for dependency installation (delegated to wizard).

        Args:
            dependencies: List of dependency names
            description: Main description

        Yields:
            tuple of (Progress, task_id, dependency_name) for each dependency
        """
        with self.wizard.dependency_progress(dependencies, description) as (
            progress,
            task,
            dep,
        ):
            yield progress, task, dep

    @contextmanager
    def create_package_install_progress(
        self,
        packages: list[tuple[str, str]],
        description: str = "Installing packages...",
    ) -> Generator[tuple[Progress, int, str, str], None, None]:
        """
        Create a progress bar for package installation (delegated to wizard).

        Args:
            packages: List of tuples (package_name, version)
            description: Main description

        Yields:
            tuple of (Progress, task_id, package_name, version) for each package
        """
        with self.wizard.package_install_progress(packages, description) as (
            progress,
            task,
            pkg,
            ver,
        ):
            yield progress, task, pkg, ver

    @contextmanager
    def create_step_progress(
        self,
        steps: list[str],
        description: str = "Processing...",
        show_step_numbers: bool = True,
        show_time: bool = True,
    ) -> Generator[tuple[Progress, int, list[str]], None, None]:
        """
        Create a step-based progress bar (delegated to wizard).

        Args:
            steps: List of step names
            description: Main description
            show_step_numbers: Show step numbers (e.g., "Step 1/5")
            show_time: Show elapsed and remaining time

        Yields:
            tuple of (Progress, task_id, steps)
        """
        with self.wizard.step_progress(
            steps, description, show_step_numbers, show_time
        ) as (progress, task, steps_list):
            yield progress, task, steps_list

    @contextmanager
    def create_file_copy_progress(
        self,
        files: list[str],
        description: str = "Copying files...",
    ) -> Generator[tuple[Progress, int, list[str]], None, None]:
        """
        Create a progress bar for file copying (delegated to wizard).

        Args:
            files: List of file paths to copy
            description: Main description

        Yields:
            tuple of (Progress, task_id, files)
        """
        with self.wizard.file_copy_progress(files, description) as (
            progress,
            task,
            files_list,
        ):
            yield progress, task, files_list

    @contextmanager
    def create_installation_progress(
        self,
        steps: list[tuple[str, str]],
        description: str = "Installation in progress...",
    ) -> Generator[tuple[Progress, int, str, str], None, None]:
        """
        Create a progress bar for installation processes (delegated to wizard).

        Args:
            steps: List of tuples (step_name, step_description)
            description: Main description

        Yields:
            tuple of (Progress, task_id, step_name, step_description) for each step
        """
        with self.wizard.installation_progress(steps, description) as (
            progress,
            task,
            step_name,
            step_detail,
        ):
            yield progress, task, step_name, step_detail

    @contextmanager
    def create_build_progress(
        self,
        phases: list[tuple[str, int]],
        description: str = "Building project...",
    ) -> Generator[tuple[Progress, int, str, int], None, None]:
        """
        Create a progress bar for build processes (delegated to wizard).

        Args:
            phases: List of tuples (phase_name, weight_percentage)
            description: Main description

        Yields:
            tuple of (Progress, task_id, phase_name, weight) for each phase
        """
        with self.wizard.build_progress(phases, description) as (
            progress,
            task,
            phase,
            weight,
        ):
            yield progress, task, phase, weight

    @contextmanager
    def create_deployment_progress(
        self,
        stages: list[str],
        description: str = "Deploying...",
    ) -> Generator[tuple[Progress, int, str], None, None]:
        """
        Create a progress bar for deployment processes (delegated to wizard).

        Args:
            stages: List of deployment stage names
            description: Main description

        Yields:
            tuple of (Progress, task_id, stage) for each stage
        """
        with self.wizard.deployment_progress(stages, description) as (
            progress,
            task,
            stage,
        ):
            yield progress, task, stage

    @contextmanager
    def create_layered_progressbar(
        self,
        layers: list[dict[str, Any]],
        show_time: bool = True,
    ) -> Generator[tuple[Progress, dict[str, int]], None, None]:
        """
        Create a multi-level progress bar (delegated to wizard).

        Args:
            layers: List of layer configurations
            show_time: Show elapsed and remaining time

        Yields:
            tuple of (Progress, task_ids_dict)
        """
        with self.wizard.layered_progress(layers, show_time) as (progress, task_ids):
            yield progress, task_ids

    @contextmanager
    def create_dynamic_layered_progress(
        self,
        stages: list[dict[str, Any]],
    ) -> Generator[DynamicLayeredProgress, None, None]:
        """
        Create a dynamic layered progress bar for multi-stage installations.

        Args:
            stages: List of stage configurations with name, type, description, etc.

        Yields:
            DynamicLayeredProgress object with update_layer and complete_layer methods
        """
        progress_manager = DynamicLayeredProgress(self._console, stages)
        with progress_manager:
            yield progress_manager


# ///////////////////////////////////////////////////////////////
# DYNAMIC LAYERED PROGRESS WRAPPER
# ///////////////////////////////////////////////////////////////


class DynamicLayeredProgress:
    """
    Wrapper for managing multiple progress stages dynamically.

    Handles updates and completion of various stage types (spinner, steps, etc.).
    """

    def __init__(self, console: Console, stages: list[dict[str, Any]]) -> None:
        """Initialize the dynamic progress manager."""
        self.console = console
        self.stages = {stage["name"]: stage for stage in stages}
        self.progress = Progress(console=console)
        self.task_ids: dict[str, int] = {}
        self._completed_stages: set[str] = set()

    def __enter__(self) -> DynamicLayeredProgress:
        """Enter context manager."""
        self.progress.__enter__()
        # Add tasks for each stage
        for stage_name, stage in self.stages.items():
            description = stage.get("description", stage_name)
            self.task_ids[stage_name] = self.progress.add_task(description, total=100)
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context manager."""
        self.progress.__exit__(*args)

    def update_layer(
        self, layer_name: str, progress_value: int | None = None, message: str = ""
    ) -> None:
        """
        Update a specific layer's progress.

        Args:
            layer_name: Name of the layer to update
            progress_value: Progress value (percentage for bars, step index for main stages)
            message: Additional message to display
        """
        if layer_name not in self.task_ids:
            return

        task_id = self.task_ids[layer_name]
        stage = self.stages.get(layer_name, {})
        description = stage.get("description", layer_name)

        if message:
            self.progress.update(task_id, description=f"{description} - {message}")
        else:
            self.progress.update(task_id, description=description)

        if progress_value is not None:
            # For main stages with steps, calculate percentage based on step number
            if stage.get("type") == "main" and "steps" in stage:
                steps_count = len(stage["steps"])
                completed_percent = (
                    int((progress_value / steps_count) * 100) if steps_count > 0 else 0
                )
                self.progress.update(task_id, completed=completed_percent)
            # For progress bars with total, use value directly as percentage
            elif stage.get("type") == "progress":
                total = stage.get("total", 100)
                # Convert count to percentage
                completed_percent = (
                    int((progress_value / total) * 100) if total > 0 else 0
                )
                self.progress.update(task_id, completed=completed_percent)
            else:
                # For spinners and other types, use value as percentage directly
                self.progress.update(task_id, completed=progress_value)

    def complete_layer(self, layer_name: str) -> None:
        """
        Mark a layer as complete.

        Args:
            layer_name: Name of the layer to complete
        """
        if layer_name not in self.task_ids:
            return

        task_id = self.task_ids[layer_name]
        self.progress.update(task_id, completed=100)
        self._completed_stages.add(layer_name)

    def emergency_stop(self, _message: str = "Operation stopped") -> None:
        """
        Emergency stop the progress display.

        Args:
            message: Message to display before stopping
        """
        with suppress(Exception):
            self.progress.stop()


# ///////////////////////////////////////////////////////////////
# EZPL BRIDGE (WRAPPER FOR COMPATIBILITY)
# ///////////////////////////////////////////////////////////////


class EzplBridge:
    """
    Wrapper around Ezpl for backward compatibility.

    Provides access to Ezpl instance with additional convenience properties
    like console, wizard, etc.
    """

    def __init__(self, ezpl_instance: Ezpl) -> None:
        """Initialize the bridge with an Ezpl instance."""
        self._ezpl = ezpl_instance

    def __getattr__(self, name: str) -> Any:
        """Delegate all attribute access to the underlying Ezpl instance."""
        return getattr(self._ezpl, name)

    @property
    def console(self) -> Console:
        """Get the Rich Console for direct access."""
        return self._ezpl._printer._console  # type: ignore[attr-defined]

    @property
    def wizard(self) -> RichWizard:
        """Get the wizard."""
        return self._ezpl._printer._wizard  # type: ignore[attr-defined]

    @property
    def printer(self) -> ExtendedPrinter:
        """Get the extended printer."""
        return self._ezpl._printer  # type: ignore[attr-defined]


# ///////////////////////////////////////////////////////////////
# GLOBAL INSTANCE
# ///////////////////////////////////////////////////////////////

# Create global singleton instance with default logging configuration
# Check if Ezpl is already initialized by trying to access _instance
log_folder = LoggingConfig.get_log_dir()
log_folder.mkdir(parents=True, exist_ok=True)
first_init = Ezpl._instance is None
_ezpl_instance = Ezpl(log_file=LoggingConfig.get_log_file())
if first_init:
    # Configure logging settings
    _ezpl_instance.configure(
        log_file=str(LoggingConfig.get_log_file()),
        log_rotation=LoggingConfig.ROTATION,
        log_retention=LoggingConfig.RETENTION,
        log_compression=LoggingConfig.COMPRESSION,
        level=(
            LoggingConfig.DEFAULT_LEVEL.label
            if isinstance(LoggingConfig.DEFAULT_LEVEL, LogLevel)
            else str(LoggingConfig.DEFAULT_LEVEL)
        ),
        force=False,
    )
    # Override printer with ExtendedPrinter
    # Use set_printer_class if available, otherwise replace _printer directly
    if hasattr(_ezpl_instance, "set_printer_class"):
        _ezpl_instance.set_printer_class(ExtendedPrinter)
    else:
        # Fallback: replace _printer directly with ExtendedPrinter instance
        # Preserve current configuration
        current_level = _ezpl_instance._printer._level
        current_indent_step = _ezpl_instance._printer._indent_step
        current_indent_symbol = _ezpl_instance._printer._indent_symbol
        current_base_indent_symbol = _ezpl_instance._printer._base_indent_symbol
        _ezpl_instance._printer = ExtendedPrinter(
            level=current_level,
            indent_step=current_indent_step,
            indent_symbol=current_indent_symbol,
            base_indent_symbol=current_base_indent_symbol,
        )
        # Update the wrapper to use the new printer
        # The wrapper is created in ConsolePrinter.__init__, so we need to recreate it
        from ezpl.handlers.console import ConsolePrinterWrapper

        _ezpl_instance._printer._wrapper = ConsolePrinterWrapper(
            _ezpl_instance._printer
        )
    # Lock configuration if method exists
    if hasattr(_ezpl_instance, "lock_config"):
        _ezpl_instance.lock_config()
    elif hasattr(Ezpl, "lock_config"):
        Ezpl.lock_config()

# Create bridge wrapper for backward compatibility
ezpl_bridge = EzplBridge(_ezpl_instance)

# Get printer and logger instances
# After set_printer_class(), _printer is our ExtendedPrinter instance
ezprinter: ExtendedPrinter = _ezpl_instance._printer  # type: ignore[assignment]
ezlogger: EzLogger = _ezpl_instance.get_logger()  # type: ignore[attr-defined]
ezconsole: Console = ezprinter._console  # type: ignore[attr-defined]
ezwizard: RichWizard = ezprinter.wizard  # type: ignore[attr-defined]

# Export ezpl instance as 'ezpl' for backward compatibility
ezpl = _ezpl_instance

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "DynamicLayeredProgress",
    "ExtendedPrinter",
    "EzplBridge",
    "ezconsole",
    "ezlogger",
    "ezpl",
    "ezpl_bridge",
    "ezprinter",
    "ezwizard",
]
