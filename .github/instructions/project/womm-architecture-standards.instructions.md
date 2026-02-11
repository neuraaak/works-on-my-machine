# WOMM Project Architecture Standards

Professional architecture and design standards for Works On My Machine (WOMM) project. This rule defines the specific patterns, structure, and conventions used throughout the codebase to maintain consistency and quality.

## Project Overview

**Works On My Machine (WOMM)** is a universal development tool for Python and JavaScript that automates:

- Project initialization and configuration
- Dependency detection and management
- Multi-language linting and spell checking
- Windows context menu configuration
- Cross-platform command execution with security validation

**Target Python**: 3.10+ | **License**: MIT

---

## Architecture Principles

### Three-Layer Architecture

WOMM strictly follows a three-layer architecture with clear separation of concerns:

```txt
Commands Layer (UI/CLI)
    ↓ orchestrates
Interfaces Layer (Façades/Orchestration)
    ↓ uses
Services Layer (Business Logic)
    ↓ depends on
Exceptions, Utils, Config (Infrastructure)
```

#### **Layer 1: Commands** (`womm/commands/`)

- **Responsibility**: CLI entry points, user interface, output formatting
- **Technology**: Click framework
- **No business logic**: All logic delegated to interfaces
- **Example**: `womm/commands/project/create.py` → handles user prompts, calls interface

#### **Layer 2: Interfaces** (`womm/interfaces/`)

- **Responsibility**: Orchestrate services, provide simplified high-level APIs
- **Pattern**: Façade pattern - one interface per major feature
- **Initialization**: Services lazy-loaded in `@property` methods
- **Example**: `ProjectCreateInterface` → orchestrates ProjectDetectionService + TemplateService + PythonProjectCreationService
- **Error Handling**: Catch service exceptions, wrap in interface-specific exceptions

#### **Layer 3: Services** (`womm/services/`)

- **Responsibility**: Business logic implementation
- **Pattern**: One service per business domain
- **Stateless**: Services should be stateless or lazily initialized
- **Error Handling**: Raise domain-specific service exceptions
- **Example**: `ProjectDetectionService` → detects project types, raises ProjectDetectionServiceError

### Separation of Concerns

Each module should have exactly one reason to change:

- **Commands**: Change when CLI interface changes
- **Interfaces**: Change when orchestration logic changes
- **Services**: Change when business logic changes
- **Exceptions**: Change when error categories change
- **Configs**: Change when constants change

---

## Exception Architecture

### Two-Level Exception Hierarchy

Every domain has TWO levels of exceptions:

#### **Service-Level Exceptions**

```python
# womm/exceptions/project/project_service.py
class ProjectServiceError(Exception):
    """Base exception for project services."""

    def __init__(self, message: str, operation: str = "", details: str | None = None) -> None:
        self.message = message
        self.operation = operation
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        parts = [self.message]
        if self.operation:
            parts.append(f"Operation: {self.operation}")
        if self.details:
            parts.append(f"Details: {self.details}")
        return " | ".join(parts)

class ProjectDetectionServiceError(ProjectServiceError):
    """Raised when project detection fails."""
```

#### **Interface-Level Exceptions**

```python
# womm/exceptions/project/project_interface.py
class ProjectInterfaceError(Exception):
    """Base exception for project interface errors."""

    # Same structure as service exceptions
    def __init__(self, message: str = "", operation: str = "", details: str = "") -> None:
        ...

class CreateInterfaceError(ProjectInterfaceError):
    """Raised when project creation fails."""
```

### Exception Usage Pattern

Services raise exceptions → Interfaces catch and wrap them:

```python
# In interface
try:
    detection_result = self._detection_service.detect_project(project_path)
except ProjectDetectionServiceError as e:
    logger.error(f"Failed to detect project: {e}", exc_info=True)
    raise CreateInterfaceError(
        message=f"Failed to initialize project creation: {e}",
        operation="project_detection",
        details=f"Exception type: {type(e).__name__}",
    ) from e
```

### Exception Domains

| Domain       | Service Base               | Interface Base               | Location                        |
| ------------ | -------------------------- | ---------------------------- | ------------------------------- |
| Common       | `CommandServiceError`      | N/A                          | `womm/exceptions/common/`       |
| Project      | `ProjectServiceError`      | `ProjectInterfaceError`      | `womm/exceptions/project/`      |
| System       | `SystemServiceError`       | `SystemInterfaceError`       | `womm/exceptions/system/`       |
| Dependencies | `DependenciesServiceError` | `DependenciesInterfaceError` | `womm/exceptions/dependencies/` |
| Lint         | `LintServiceError`         | `LintInterfaceError`         | `womm/exceptions/lint/`         |
| CSpell       | `CSpellServiceError`       | `CSpellInterfaceError`       | `womm/exceptions/cspell/`       |
| Context      | `ContextServiceError`      | `ContextInterfaceError`      | `womm/exceptions/context/`      |
| WOMM Setup   | `WommSetupServiceError`    | `WommSetupInterfaceError`    | `womm/exceptions/womm_setup/`   |

---

## Security Architecture

### Security Validation Pattern

All external command execution goes through `SecurityValidatorService` (singleton):

```python
# In CommandRunnerService
def _validate_command_security(self, command: list[str]) -> None:
    """Validate command security using SecurityValidator."""
    validator = SecurityValidatorService()
    validation_result = validator.validate_command(command)
    if not validation_result.is_valid:
        raise CommandValidationError(
            command=str(command),
            reason=f"Security validation failed: {validation_result.validation_reason}",
        )
```

### Security Validation Layers

1. **Whitelist Validation**: Command must be in `SecurityPatternsConfig.ALLOWED_COMMANDS`
2. **Pattern Detection**: Reject dangerous patterns (rm -rf /, DROP TABLE, eval(), etc.)
3. **Argument Validation**: Check arguments per command type
4. **Permission Command Validation**: Special handling for chmod/chown
5. **Path Traversal Protection**: `../../../` patterns rejected
6. **System Directory Protection**: Prevent modifications to system directories

---

## Click CLI Command Standards

### Help Option Requirement ⚡

**MANDATORY**: All Click command groups and commands MUST include `@click.help_option("-h", "--help")`

```python
@click.group(invoke_without_command=True)
@click.pass_context
def project_group(ctx: click.Context) -> None:
    """Project management commands."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

@project_group.command("create")
@click.help_option("-h", "--help")  # ← REQUIRED
@click.option("-f", "--force", is_flag=True, help="Force creation")
def create_project(force: bool) -> None:
    """Create a new project."""
```

### Command Structure Pattern

```python
# ///////////////////////////////////////////////////////////////
# [DOMAIN] - [Feature] Commands
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Module docstring describing the command group.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import sys
import click
from ezpl.types import LogLevel

from ...exceptions.[domain] import ...
from ...interfaces import ...
from ...ui.common import ezpl_bridge, ezprinter

# ///////////////////////////////////////////////////////////////
# COMMAND GROUPS
# ///////////////////////////////////////////////////////////////

@click.group(invoke_without_command=True)
@click.pass_context
def [domain]_group(ctx: click.Context) -> None:
    """Brief description."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

# ///////////////////////////////////////////////////////////////
# SUBCOMMANDS
# ///////////////////////////////////////////////////////////////

@[domain]_group.command("[name]")
@click.help_option("-h", "--help")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
def [domain]_[name](verbose: bool) -> None:
    """Detailed description."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    try:
        interface = [Domain]Interface()
        result = interface.operation()
        sys.exit(0 if result.success else 1)
    except [Domain]Error as e:
        ezprinter.error(f"Operation failed: {e}")
        sys.exit(1)
    except Exception as e:
        ezprinter.error(f"Unexpected error: {e}")
        sys.exit(1)
```

---

## Interface Design Patterns

### Interface Initialization

Interfaces use **lazy initialization** for services to minimize startup overhead:

```python
class ProjectCreateInterface:
    def __init__(self):
        """Initialize interface - services loaded lazily."""
        try:
            self._detection_service = None  # Will be lazy-loaded
            self._template_service = None
            self._python_service = None
        except Exception as e:
            raise CreateInterfaceError(
                message=f"Failed to initialize: {e}",
                operation="initialization",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    @property
    def detection_service(self) -> ProjectDetectionService:
        """Lazy load detection service."""
        if self._detection_service is None:
            self._detection_service = ProjectDetectionService()
        return self._detection_service

    def create_project(self, **kwargs) -> ProjectCreationResult:
        """Main operation using lazy-loaded services."""
        try:
            # Services accessed via property (lazy-loaded)
            detection_result = self.detection_service.detect(...)
            # ... more operations ...
            return ProjectCreationResult(success=True)
        except ProjectDetectionServiceError as e:
            raise CreateInterfaceError(
                message=f"Failed to create project: {e}",
                operation="project_creation",
                details=f"Exception: {type(e).__name__}",
            ) from e
```

### Interface Result Models

All interfaces return structured result models (NOT raw values):

```python
from womm.shared.results import ProjectCreationResult, OperationResult

# In interface method:
def create_project(self, ...) -> ProjectCreationResult:
    """Create project and return structured result."""
    # result_models.py contains all result classes
    return ProjectCreationResult(
        success=True,
        message="Project created successfully",
        project_path=Path(...),
        project_type="python",
    )
```

---

## Service Implementation Patterns

### Service Statelessness

Services should be stateless or have minimal state. Prefer dependency injection:

```python
class ProjectDetectionService:
    """Stateless service for project detection."""

    def __init__(self):
        """Initialize - no state stored."""
        self.logger = logging.getLogger(__name__)

    def detect_project(self, project_path: Path) -> ProjectDetectionResult:
        """Pure function - same input always produces same output."""
        # No internal state mutations
        # All dependencies passed as arguments or resolved internally
        ...
```

### Service Error Handling

Services raise specific, domain-focused exceptions with context:

```python
class ProjectDetectionService:
    def detect_project(self, project_path: Path) -> ProjectDetectionResult:
        try:
            # ... implementation ...
            if not project_path.exists():
                raise ProjectDetectionServiceError(
                    message=f"Project path does not exist: {project_path}",
                    operation="path_validation",
                    details=f"Path checked: {project_path}",
                )
        except ProjectDetectionServiceError:
            raise
        except Exception as e:
            raise ProjectDetectionServiceError(
                message=f"Failed to detect project: {e}",
                operation="detection",
                details=f"Exception type: {type(e).__name__}",
            ) from e
```

---

## Configuration & Constants

### Configuration Principles

- **Centralized**: All config in `womm/shared/configs/`
- **Typed**: Use dataclasses or `@dataclass` from `dataclasses`
- **Immutable**: Configs should not be modified at runtime
- **Documented**: Each config parameter documented

### Configuration Domains

```txt
womm/shared/configs/
├── security.py          # SecurityPatternsConfig
├── runtime.py           # RuntimeConfig (Python, Node, Git)
├── devtools.py          # DevToolsConfig
├── language.py          # LanguageConfig
└── [other_configs].py
```

### Configuration Usage

```python
from womm.shared.configs.security import SecurityPatternsConfig
from womm.shared.configs.runtime import RuntimeConfig

# Access config
allowed = SecurityPatternsConfig.ALLOWED_COMMANDS
python_versions = RuntimeConfig.RUNTIMES["python"]

# Config should be read-only
# Never modify config at runtime
```

---

## Code Organization Standards

### File Structure

```python
# ///////////////////////////////////////////////////////////////
# [MODULE_NAME] - [Brief Description]
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Module description.

Detailed explanation of module's purpose, key functionality,
and important usage patterns.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library
from pathlib import Path
from typing import Optional

# Third-party
import click

# Local imports
from ...exceptions.[domain] import ...
from ...interfaces import ...

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////
DEFAULT_TIMEOUT = 30

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////

class MyClass:
    """Class description."""

    # ///////////////////////////////////////////////////////////////
    # INIT
    # ///////////////////////////////////////////////////////////////

    def __init__(self) -> None:
        """Initialize the class."""

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def public_method(self) -> None:
        """Public method."""

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _private_method(self) -> None:
        """Private method."""

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////

def module_function() -> None:
    """Function description."""

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["MyClass", "module_function"]
```

### Import Organization

- **Standard library**: `os`, `sys`, `pathlib`, `typing`
- **Third-party**: `click`, `rich`, `InquirerPy`
- **Local**: Relative imports from modules
- **Separation**: Blank line between groups
- **Sorting**: Alphabetical within each group

---

## Dependency Injection & Service Access

### Direct Instantiation (Recommended)

Services are instantiated directly when needed:

```python
# In interface
class ProjectCreateInterface:
    def __init__(self):
        self._detection_service = ProjectDetectionService()
        self._template_service = TemplateService()
```

### Singleton Services

Only `CommandRunnerService` and `SecurityValidatorService` are singletons:

```python
class CommandRunnerService:
    _instance: ClassVar[CommandRunnerService | None] = None
    _lock = Lock()

    @classmethod
    def get_instance(cls) -> CommandRunnerService:
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance
```

---

## Testing & Validation

### Module Import Validation

When adding a new service/interface, ensure:

1. **Service module** exports in `womm/services/__init__.py`
2. **Interface module** exports in `womm/interfaces/__init__.py`
3. **Exception module** exports in `womm/exceptions/__init__.py`

### Validation Checklist

- ✓ All public APIs documented with docstrings
- ✓ All exceptions properly inherited and contextualized
- ✓ All commands include `@click.help_option("-h", "--help")`
- ✓ Services raise service-level exceptions
- ✓ Interfaces catch and wrap to interface-level exceptions
- ✓ No business logic in command layer
- ✓ No UI code in service layer
- ✓ Configuration centralized and immutable

---

## Anti-Patterns to Avoid

### ❌ DO NOT

1. **Business logic in commands**: Logic must be in services/interfaces
2. **Direct service access from commands**: Commands must use interfaces
3. **UI code in services**: Services are pure business logic
4. **Catch-all exceptions**: Use specific domain exceptions
5. **Mutable configuration**: Config should be read-only
6. **Global variables**: Use dependency injection or lazy initialization
7. **Circular imports**: Carefully organize imports, use `from __future__ import annotations`
8. **Missing help option**: ALL Click commands need `@click.help_option("-h", "--help")`

### ✅ DO

1. **Place logic in services**: Services implement business logic
2. **Use interfaces**: Commands use interfaces as entry points
3. **Separate concerns**: Clear boundaries between layers
4. **Domain-specific exceptions**: Each domain has its own exception hierarchy
5. **Type hints**: All public functions must have type hints
6. **Lazy initialization**: Initialize services when needed, not in constructor
7. **Security validation**: All commands go through security checks
8. **Comprehensive docstrings**: Document purpose, parameters, returns, exceptions

---

## Key Principles Summary

| Principle                     | Implementation                                          |
| ----------------------------- | ------------------------------------------------------- |
| **Single Responsibility**     | Each service/interface has one reason to change         |
| **Separation of Concerns**    | Commands → Interfaces → Services strictly enforced      |
| **Exception Hierarchy**       | Two-level exceptions (Service + Interface) per domain   |
| **Security First**            | All commands validated through SecurityValidatorService |
| **Type Safety**               | Full type hints, Python 3.10+ syntax                    |
| **Configuration Centralized** | All constants in `shared/configs/`                      |
| **Lazy Initialization**       | Services load only when needed                          |
| **Clear Documentation**       | Google-style docstrings throughout                      |

---

## Related Documentation

- **Architecture Overview**: See `docs/diagrams/architecture-globale.md`
- **Exception Architecture**: See `docs/EXCEPTION_ARCHITECTURE.md`
- **CLI Architecture**: See `docs/api/CLI_ARCHITECTURE.md`
- **Dependency Architecture**: See `docs/api/ARCHITECTURE.md`
- **Python Standards**: See `.cursor/rules/languages/python/python-development-standards.mdc`
- **Python Formatting**: See `.cursor/rules/languages/python/python-formatting-standards.mdc`
