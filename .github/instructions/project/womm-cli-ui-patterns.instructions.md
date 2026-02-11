# WOMM CLI & UI Patterns

Standards for Click CLI commands, user prompts, and UI components in WOMM. These patterns ensure consistent user experience, proper CLI design, and effective UI feedback across all commands.

---

## Click Command Structure

### Mandatory Help Option Pattern ⚡

**CRITICAL**: All Click command groups and subcommands MUST include `@click.help_option("-h", "--help")`

```python
# ✅ CORRECT: With help option
@click.group(invoke_without_command=True)
@click.pass_context
def project_group(ctx: click.Context) -> None:
    """Manage projects."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

@project_group.command("create")
@click.help_option("-h", "--help")  # ← MANDATORY
@click.argument("name")
@click.option("-p", "--path", default=".", help="Project path")
def create_project(name: str, path: str) -> None:
    """Create a new project."""
    ...

# ❌ INCORRECT: Missing help option
@project_group.command("create")  # ← NO help_option!
def create_project(name: str, path: str) -> None:
    ...
```

### Command Group Template

```python
#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# [DOMAIN] COMMANDS - [Feature Description]
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
[Domain] commands for WOMM CLI.

This module handles [domain] operations and provides commands for
[key operations]. All commands delegate business logic to interfaces.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import sys

import click
from ezpl.types import LogLevel

from ...exceptions.[domain] import [DomainInterfaceError]
from ...interfaces import [DomainInterface]
from ...ui.common import ezpl_bridge, ezprinter

# ///////////////////////////////////////////////////////////////
# COMMAND GROUPS
# ///////////////////////////////////////////////////////////////

@click.group(invoke_without_command=True)
@click.pass_context
def [domain]_group(ctx: click.Context) -> None:
    """[Brief group description]."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

# ///////////////////////////////////////////////////////////////
# SUBCOMMANDS
# ///////////////////////////////////////////////////////////////

@[domain]_group.command("operation1")
@click.help_option("-h", "--help")
@click.argument("argument1")
@click.option(
    "-f", "--force",
    is_flag=True,
    help="Force operation",
)
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def [domain]_operation1(argument1: str, force: bool, verbose: bool) -> None:
    """Perform operation 1."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    try:
        interface = [DomainInterface]()
        result = interface.operation1(argument1, force=force)

        if result.success:
            ezprinter.success(result.message)
            sys.exit(0)
        else:
            ezprinter.error(result.message)
            sys.exit(1)

    except [DomainInterfaceError] as e:
        ezprinter.error(f"Operation failed: {e}")
        sys.exit(1)
    except Exception as e:
        ezprinter.error(f"Unexpected error: {e}")
        sys.exit(1)

@[domain]_group.command("operation2")
@click.help_option("-h", "--help")
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def [domain]_operation2(verbose: bool) -> None:
    """Perform operation 2."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    try:
        interface = [DomainInterface]()
        result = interface.operation2()

        if result.success:
            ezprinter.success(result.message)
            sys.exit(0)
        else:
            ezprinter.error(result.message)
            sys.exit(1)

    except [DomainInterfaceError] as e:
        ezprinter.error(f"Operation failed: {e}")
        sys.exit(1)
    except Exception as e:
        ezprinter.error(f"Unexpected error: {e}")
        sys.exit(1)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["[domain]_group"]
```

---

## Click Options & Arguments Standards

### Option Conventions

```python
# ✅ GOOD: Clear option names and help text
@click.option(
    "-f", "--force",
    is_flag=True,
    help="Force operation without confirmation",
)
@click.option(
    "-p", "--path",
    type=click.Path(exists=True),
    default=".",
    help="Project path (default: current directory)",
)
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
@click.option(
    "-o", "--output",
    type=click.Path(),
    help="Output file path",
)

# ❌ BAD: Vague help text
@click.option("-f", "--force", help="Force it")  # Too vague
@click.option("-p", "--path", help="Where to put it")  # Unclear
@click.option("-o", "--output", help="Output")  # Not helpful

# ❌ BAD: Missing short flags
@click.option("--force", is_flag=True)  # No -f shortcut
@click.option("--verbose", is_flag=True)  # No -v shortcut
```

### Argument Conventions

```python
# ✅ GOOD: Clear argument names and help text
@click.argument("project-name")
@click.argument("project-path", type=click.Path())

# ❌ BAD: Unclear argument names
@click.argument("p")  # Too short
@click.argument("input-data")  # Too generic
```

### Standard Options

Every command should support these standard options when applicable:

```python
# Verbose output - for all commands
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)

# Force operation - when confirmation might be needed
@click.option(
    "-f", "--force",
    is_flag=True,
    help="Force operation without confirmation",
)

# Dry run - when operation might be destructive
@click.option(
    "--dry-run",
    is_flag=True,
    help="Simulate operation without making changes",
)

# Output path - when generating files
@click.option(
    "-o", "--output",
    type=click.Path(),
    help="Output file path",
)
```

---

## Error Handling in Commands

### Standard Error Handling Pattern

```python
def command_handler(argument: str, verbose: bool) -> None:
    """Handle command execution."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    try:
        # Initialize interface
        interface = MyInterface()

        # Execute operation
        result = interface.operation(argument)

        # Handle result
        if result.success:
            ezprinter.success(result.message)
            sys.exit(0)
        else:
            ezprinter.error(result.message)
            sys.exit(1)

    except MyInterfaceError as e:
        # Expected error - show to user
        ezprinter.error(f"Operation failed: {e}")
        sys.exit(1)

    except Exception as e:
        # Unexpected error - log and show
        logger.error(f"Unexpected error: {e}", exc_info=True)
        ezprinter.error(f"Unexpected error: {e}")
        sys.exit(1)
```

### Exit Codes

- **0**: Success
- **1**: Expected failure (user error, validation failure)
- **2**: Unexpected error (exception)

```python
# ✅ GOOD: Appropriate exit codes
if result.success:
    sys.exit(0)  # Success
else:
    sys.exit(1)  # Expected failure

# ✅ GOOD: Exceptions use exit(1) or exit(2) based on severity
except InterfaceError:
    sys.exit(1)  # Expected error from interface
except Exception:
    sys.exit(2)  # Unexpected error (or just 1 if not critical)
```

---

## UI Component Standards

### EZPrinter Usage

The `ezprinter` utility provides consistent formatted output:

```python
from womm.ui.common import ezprinter

# Headers
ezprinter.print_header("Project Creation")

# Success messages
ezprinter.success("Project created successfully!")

# Error messages
ezprinter.error("Failed to create project")

# Info messages
ezprinter.info("Processing...")

# Warning messages
ezprinter.warning("This action cannot be undone")

# Sections with proper formatting
ezprinter.section("Configuration")
```

### Rich Output Integration

WOMM uses the `rich` library for enhanced terminal output:

```python
from rich.console import Console
from rich.table import Table

console = Console()

# Tables for structured data
table = Table(title="System Information")
table.add_column("Component", style="cyan")
table.add_column("Version", style="magenta")
table.add_row("Python", "3.11.0")
console.print(table)

# Panels for emphasis
from rich.panel import Panel
console.print(Panel("Important message", style="bold red"))

# Progress tracking
from rich.progress import track
for item in track(items, description="Processing..."):
    process(item)
```

### Interactive Prompts

For user input, use `InquirerPy`:

```python
from InquirerPy import inquirer

# Simple text input
project_name = inquirer.text(message="Project name:").execute()

# Confirmation
confirm = inquirer.confirm(message="Continue?").execute()

# Multiple choice
language = inquirer.select(
    message="Select language:",
    choices=["Python", "JavaScript", "TypeScript"],
).execute()

# Checkbox (multiple selections)
tools = inquirer.checkbox(
    message="Select tools:",
    choices=["ESLint", "Prettier", "TypeScript"],
).execute()

# Path input with validation
path = inquirer.filepath(
    message="Project path:",
    validate=lambda p: len(p) > 0,
).execute()
```

### EZPLog Bridge

For logging with proper levels:

```python
from womm.ui.common import ezpl_bridge
from ezpl.types import LogLevel

# Set log level based on verbose flag
if verbose:
    ezpl_bridge.set_level(LogLevel.DEBUG.label)
else:
    ezpl_bridge.set_level(LogLevel.INFO.label)

# Logging
logger.debug("Detailed information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
```

---

## UI Component Organization

### UI Structure

```txt
womm/ui/
├── common/                      # Shared UI components
│   ├── ezpl_bridge.py          # EZPLog integration
│   ├── ezprinter.py            # Output formatting (success, error, etc.)
│   ├── interactive_menu.py     # Menu navigation
│   └── prompts.py              # User input prompts
│
├── project/                     # Project-specific UI
│   ├── project_wizard.py       # Project creation wizard
│   ├── create/
│   │   └── create_completion_summaries.py
│   ├── setup/
│   │   └── setup_completion_summaries.py
│   └── templates/
│       ├── template_selector.py
│       └── template_ui.py
│
├── system/                      # System UI components
│   └── display.py
│
├── dependencies/                # Dependencies UI
│   └── display.py
│
├── lint/                        # Linting UI
│   └── display.py
│
└── [other_domains]/            # Domain-specific UI
```

### UI Component Template

```python
#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# [DOMAIN] UI - [Component Description]
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
[Domain] UI components for user interaction.

Provides UI components for [functionality].
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import logging
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

from ...ui.common import ezprinter, ezpl_bridge

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)
console = Console()

# ///////////////////////////////////////////////////////////////
# DISPLAY FUNCTIONS
# ///////////////////////////////////////////////////////////////

def display_results(results: dict[str, Any]) -> None:
    """Display operation results to user."""
    ezprinter.section("Results")

    for key, value in results.items():
        ezprinter.info(f"{key}: {value}")

def display_table(data: list[dict[str, Any]], title: str) -> None:
    """Display data in table format."""
    table = Table(title=title)

    if not data:
        console.print("No data to display")
        return

    # Add columns from first row
    for column in data[0].keys():
        table.add_column(column, style="cyan")

    # Add rows
    for row in data:
        table.add_row(*[str(v) for v in row.values()])

    console.print(table)

def display_status(status: str, success: bool) -> None:
    """Display operation status."""
    if success:
        ezprinter.success(status)
    else:
        ezprinter.error(status)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["display_results", "display_table", "display_status"]
```

---

## Command Organization Best Practices

### Domain Command Files

Each domain has its own command file(s):

```txt
womm/commands/
├── cli.py              # Main CLI entry point (registers all groups)
├── core/
│   └── womm_setup.py   # Install/uninstall commands
├── project/
│   ├── create.py       # Project creation
│   ├── setup.py        # Project setup
│   └── template.py     # Template management
├── system/
│   ├── system.py       # System detection
│   ├── deps.py         # Dependency management
│   └── context.py      # Context menu management
└── tools/
    ├── lint.py         # Linting commands
    └── cspell.py       # Spell checking commands
```

### CLI Main Entry Point

The `cli.py` file registers all command groups:

```python
#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# WOMM CLI - Main CLI Entry Point
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""Works On My Machine (WOMM) - Main CLI Entry Point."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import click

from .core.womm_setup import setup_group
from .project.create import project_group as project_create_group
from .project.setup import project_setup_group
from .project.template import template_group
from .system.system import system_group
from .system.deps import deps_group
from .system.context import context_group
from .tools.lint import lint_group
from .tools.cspell import cspell_group

# ///////////////////////////////////////////////////////////////
# MAIN CLI GROUP
# ///////////////////////////////////////////////////////////////

@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
def main(ctx: click.Context) -> None:
    """Works On My Machine - Universal development tools."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

# ///////////////////////////////////////////////////////////////
# REGISTER COMMAND GROUPS
# ///////////////////////////////////////////////////////////////

# Core commands
main.add_command(setup_group, name="install")

# Project commands
main.add_command(project_create_group, name="project")
main.add_command(project_setup_group, name="setup")
main.add_command(template_group, name="template")

# System commands
main.add_command(system_group, name="system")
main.add_command(deps_group, name="deps")
main.add_command(context_group, name="context")

# Tools
main.add_command(lint_group, name="lint")
main.add_command(cspell_group, name="cspell")

if __name__ == "__main__":
    main()
```

---

## User Experience Best Practices

### Clear Help Text

```python
# ✅ GOOD: Clear, action-oriented help text
def project_create(name: str, path: str, force: bool) -> None:
    """Create a new project.

    Creates a new project structure with the specified NAME
    in the given PATH. Use --force to skip confirmation.
    """

# ❌ BAD: Vague help text
def project_create(name: str, path: str, force: bool) -> None:
    """Create something."""  # Too vague
```

### Consistent Messaging

Use consistent message patterns:

```python
# Operation start
ezprinter.info(f"Starting operation: {operation_name}")

# Progress
ezprinter.info(f"Processing {current}/{total}...")

# Success
ezprinter.success(f"{operation_name} completed successfully")

# Failure
ezprinter.error(f"Failed to {operation_name}: {reason}")

# Warning
ezprinter.warning(f"Be aware: {warning_message}")
```

### Progress Feedback

For long operations, provide progress updates:

```python
from rich.progress import track

items = get_items()
for item in track(items, description="Processing..."):
    process_item(item)
```

---

## Command Testing

### Test Command Execution

```python
# tests/unit/commands/test_project_commands.py

from click.testing import CliRunner
from womm.commands.project.create import create_project

def test_create_project_success():
    """Test successful project creation."""
    runner = CliRunner()
    result = runner.invoke(create_project, ["my-project"])

    assert result.exit_code == 0
    assert "created" in result.output.lower()

def test_create_project_force_flag():
    """Test force flag prevents confirmation."""
    runner = CliRunner()
    result = runner.invoke(create_project, ["my-project", "--force"])

    assert result.exit_code == 0

def test_create_project_help():
    """Test help option."""
    runner = CliRunner()
    result = runner.invoke(create_project, ["-h"])

    assert result.exit_code == 0
    assert "Create a new project" in result.output
```

---

## Anti-Patterns in CLI/UI

### ❌ DO NOT

1. **Use print() directly**: Use ezprinter or logging
2. **Missing help option**: All commands need `@click.help_option("-h", "--help")`
3. **Unclear option names**: Use clear, descriptive names
4. **No exit codes**: Always `sys.exit(0)` or `sys.exit(1)`
5. **Business logic in commands**: All logic in interfaces/services
6. **Direct exception output**: Format error messages for users
7. **No progress feedback**: Show progress for long operations
8. **Generic error messages**: Provide specific, actionable messages

### ✅ DO

1. **Use ezprinter**: For all user-facing output
2. **Include help**: All commands have `@click.help_option("-h", "--help")`
3. **Clear naming**: Descriptive option and argument names
4. **Explicit exits**: Always set appropriate exit code
5. **Delegate logic**: Commands orchestrate, don't implement
6. **Format errors**: User-friendly error messages
7. **Show progress**: Long operations have progress tracking
8. **Provide context**: Error messages explain what went wrong

---

## Summary

**Commands**:

- ✓ All include `@click.help_option("-h", "--help")`
- ✓ Clear, descriptive help text
- ✓ Consistent error handling
- ✓ Appropriate exit codes
- ✓ Delegate to interfaces

**UI**:

- ✓ Use ezprinter for output
- ✓ Rich tables for structured data
- ✓ InquirerPy for user input
- ✓ Progress tracking for long operations
- ✓ Consistent messaging patterns

**Organization**:

- ✓ Commands per domain
- ✓ UI components shared in `ui/common/`
- ✓ Domain-specific UI in `ui/[domain]/`
- ✓ Main CLI entry point in `cli.py`
