# WOMM Exception & Security Patterns

Detailed patterns for exception architecture, security validation, and error handling in WOMM. These patterns ensure consistent error handling, security, and debugging capabilities across all domains.

---

## Exception Architecture Overview

### Two-Level Exception Hierarchy

WOMM uses a **two-level exception hierarchy** for every domain:

```txt
Exception (Python base)
    ├── [DomainServiceError] (Service-level base)
    │   ├── [SpecificServiceError1]
    │   ├── [SpecificServiceError2]
    │   └── [SpecificServiceError3]
    │
    └── [DomainInterfaceError] (Interface-level base)
        ├── [SpecificInterfaceError1]
        ├── [SpecificInterfaceError2]
        └── [SpecificInterfaceError3]
```

### Domains & Exception Locations

| Domain           | Service Base               | Interface Base               | Location                        |
| ---------------- | -------------------------- | ---------------------------- | ------------------------------- |
| **Common**       | `CommandServiceError`      | N/A                          | `womm/exceptions/common/`       |
| **Project**      | `ProjectServiceError`      | `ProjectInterfaceError`      | `womm/exceptions/project/`      |
| **System**       | `SystemServiceError`       | `SystemInterfaceError`       | `womm/exceptions/system/`       |
| **Dependencies** | `DependenciesServiceError` | `DependenciesInterfaceError` | `womm/exceptions/dependencies/` |
| **Lint**         | `LintServiceError`         | `LintInterfaceError`         | `womm/exceptions/lint/`         |
| **CSpell**       | `CSpellServiceError`       | `CSpellInterfaceError`       | `womm/exceptions/cspell/`       |
| **Context**      | `ContextServiceError`      | `ContextInterfaceError`      | `womm/exceptions/context/`      |
| **WOMM Setup**   | `WommSetupServiceError`    | `WommSetupInterfaceError`    | `womm/exceptions/womm_setup/`   |

---

## Service Exception Pattern

### Base Service Exception Template

```python
#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# [DOMAIN] SERVICE EXCEPTIONS
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Exception classes for [domain] service operations.

This module contains custom exceptions used by [domain] services.
All service-level exceptions inherit from [DomainServiceError].
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION
# ///////////////////////////////////////////////////////////////

class [DomainServiceError](Exception):
    """Base exception for all [domain] service errors.

    This is the main exception class for all [domain] service operations.
    All specific [domain] exceptions should inherit from this class.
    """

    def __init__(
        self,
        message: str,
        operation: str = "",
        details: str | None = None,
    ) -> None:
        """Initialize the exception with context.

        Args:
            message: Human-readable error message
            operation: Name of the operation that failed
            details: Optional technical details for debugging

        Example:
            >>> raise ProjectServiceError(
            ...     message="Failed to detect project",
            ...     operation="project_detection",
            ...     details="Path does not exist: /tmp/project"
            ... )
        """
        self.message = message
        self.operation = operation
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of error."""
        parts = [self.message]
        if self.operation:
            parts.append(f"Operation: {self.operation}")
        if self.details:
            parts.append(f"Details: {self.details}")
        return " | ".join(parts)

# ///////////////////////////////////////////////////////////////
# SPECIFIC EXCEPTIONS
# ///////////////////////////////////////////////////////////////

class [SpecificServiceError1]([DomainServiceError]):
    """Raised when [specific condition 1] occurs."""
    pass

class [SpecificServiceError2]([DomainServiceError]):
    """Raised when [specific condition 2] occurs."""
    pass

class [SpecificServiceError3]([DomainServiceError]):
    """Raised when [specific condition 3] occurs."""
    pass

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "[DomainServiceError]",
    "[SpecificServiceError1]",
    "[SpecificServiceError2]",
    "[SpecificServiceError3]",
]
```

### Real Example: Project Service Exceptions

```python
# womm/exceptions/project/project_service.py

class ProjectServiceError(Exception):
    """Base exception for project services."""

    def __init__(
        self,
        message: str,
        operation: str = "",
        details: str | None = None,
    ) -> None:
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
    pass

class TemplateServiceError(ProjectServiceError):
    """Raised when template operation fails."""
    pass

class ConflictResolutionServiceError(ProjectServiceError):
    """Raised when conflict resolution fails."""
    pass
```

---

## Interface Exception Pattern

### Base Interface Exception Template

```python
#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# [DOMAIN] INTERFACE EXCEPTIONS
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Exception classes for [domain] interface operations.

Interfaces catch service exceptions and raise interface exceptions
to maintain abstraction boundaries. All interface exceptions inherit
from [DomainInterfaceError].
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION
# ///////////////////////////////////////////////////////////////

class [DomainInterfaceError](Exception):
    """Base exception for [domain] interface errors.

    Interface-level exceptions wrap service exceptions to maintain
    abstraction. Interfaces should catch service exceptions and
    raise interface exceptions with context.
    """

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize the exception with context.

        Args:
            message: Human-readable error message
            operation: Operation that failed
            details: Additional error details
        """
        self.message = message or "[DomainName] interface error occurred"
        self.operation = operation
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of error."""
        parts = [self.message]
        if self.operation:
            parts.append(f"Operation: {self.operation}")
        if self.details:
            parts.append(f"Details: {self.details}")
        return " | ".join(parts)

# ///////////////////////////////////////////////////////////////
# SPECIALIZED EXCEPTIONS
# ///////////////////////////////////////////////////////////////

class [SpecificInterfaceError1]([DomainInterfaceError]):
    """Raised when [specific operation 1] fails."""
    pass

class [SpecificInterfaceError2]([DomainInterfaceError]):
    """Raised when [specific operation 2] fails."""
    pass

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "[DomainInterfaceError]",
    "[SpecificInterfaceError1]",
    "[SpecificInterfaceError2]",
]
```

---

## Exception Usage Patterns

### Pattern 1: Service Raises Exception

Services validate input and raise service-level exceptions:

```python
# In ProjectDetectionService
def detect_project(self, project_path: Path) -> DetectionResult:
    """Detect project type."""

    # Validate input first
    if not project_path.exists():
        raise ProjectDetectionServiceError(
            message=f"Project path does not exist: {project_path}",
            operation="path_validation",
            details=f"Attempted to access: {project_path.absolute()}",
        )

    if not project_path.is_dir():
        raise ProjectDetectionServiceError(
            message=f"Project path is not a directory: {project_path}",
            operation="type_validation",
            details=f"Path exists but is not a directory",
        )

    try:
        # Business logic
        detection_result = self._analyze_project(project_path)
        return detection_result
    except subprocess.CalledProcessError as e:
        raise ProjectDetectionServiceError(
            message=f"Failed to analyze project structure",
            operation="analysis",
            details=f"Process error: {e.stderr}",
        ) from e
```

### Pattern 2: Interface Wraps Exception

Interfaces catch service exceptions and wrap in interface exceptions:

```python
# In ProjectCreateInterface
def create_project(self, name: str, path: Path) -> ProjectCreationResult:
    """Create a new project."""

    try:
        # Step 1: Detect project type
        detection_result = self.detection_service.detect_project(path)

        # Step 2: Use result
        creation_result = self._create_with_type(name, path, detection_result)

        return ProjectCreationResult(success=True, ...)

    except ProjectDetectionServiceError as e:
        # Wrap service exception in interface exception
        logger.error(f"Service raised exception: {e}", exc_info=True)
        raise CreateInterfaceError(
            message=f"Failed to create project: {e}",
            operation="project_creation",
            details=f"Service exception: {type(e).__name__}",
        ) from e

    except Exception as e:
        # Unexpected exception - log and wrap
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise CreateInterfaceError(
            message=f"Unexpected error during project creation: {e}",
            operation="project_creation",
            details=f"Exception type: {type(e).__name__}",
        ) from e
```

### Pattern 3: Command Handles Interface Exception

Commands use interfaces and handle interface exceptions:

```python
# In womm/commands/project/create.py

@project_group.command("create")
@click.help_option("-h", "--help")
@click.argument("name")
@click.option("-p", "--path", type=click.Path(), default=".")
def create_project(name: str, path: str) -> None:
    """Create a new project."""

    try:
        # Initialize interface
        interface = ProjectCreateInterface()

        # Call interface method
        result = interface.create_project(name, Path(path))

        # Handle result
        if result.success:
            ezprinter.success(f"Project created: {result.project_path}")
            sys.exit(0)
        else:
            ezprinter.error(result.message)
            sys.exit(1)

    except CreateInterfaceError as e:
        # Interface error - expected, show to user
        ezprinter.error(f"Failed to create project: {e}")
        sys.exit(1)

    except Exception as e:
        # Unexpected error - internal error
        ezprinter.error(f"Internal error: {e}")
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
```

---

## Common Exceptions by Domain

### Common Service Exceptions

These are used by multiple services:

```python
# womm/exceptions/common/command_service.py
class CommandExecutionError(CommandServiceError):
    """Raised when command execution fails."""
    pass

class CommandUtilityError(CommandServiceError):
    """Raised when utility operation fails."""
    pass

class TimeoutError(CommandServiceError):
    """Raised when operation times out."""
    pass

# womm/exceptions/common/file_service.py
class FileAccessError(FileServiceError):
    """Raised when file access fails."""
    pass

class DirectoryAccessError(FileServiceError):
    """Raised when directory access fails."""
    pass

class FileScanError(FileServiceError):
    """Raised when file scanning fails."""
    pass

# womm/exceptions/common/security_service.py
class CommandValidationError(SecurityServiceError):
    """Raised when command validation fails."""
    pass

class PathValidationError(SecurityServiceError):
    """Raised when path validation fails."""
    pass
```

---

## Security Architecture

### SecurityValidatorService (Singleton)

The `SecurityValidatorService` is a **singleton** that validates all external command execution:

```python
class SecurityValidatorService:
    """Singleton service for security validation."""

    _instance: ClassVar[SecurityValidatorService | None] = None
    _lock = Lock()

    @classmethod
    def get_instance(cls) -> SecurityValidatorService:
        """Get singleton instance (thread-safe)."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def validate_command(self, command: list[str]) -> CommandValidationResult:
        """Validate command for dangerous patterns."""
        # Validation layers:
        # 1. Whitelist check
        # 2. Pattern detection
        # 3. Argument validation
        # 4. Permission checks
        ...
```

### Security Validation Layers

#### 1. **Whitelist Validation**

Only allowed commands can be executed:

```python
from womm.shared.configs.security import SecurityPatternsConfig

# In SecurityValidatorService
base_command = command[0].lower()

if base_command not in SecurityPatternsConfig.ALLOWED_COMMANDS:
    return CommandValidationResult(
        success=False,
        is_valid=False,
        validation_reason=f"Command '{base_command}' not in whitelist",
    )
```

Whitelist includes: `python`, `npm`, `git`, `pip`, `uv`, `node`, `npx`, etc.

#### 2. **Dangerous Pattern Detection**

Reject known dangerous patterns:

```python
# Dangerous patterns to reject:
# - "rm -rf /"
# - "DROP TABLE"
# - "eval()"
# - "; malicious_command"
# - "| tee /etc/passwd"

if has_dangerous_command_patterns(base_command):
    return CommandValidationResult(
        is_valid=False,
        validation_reason="Command contains dangerous patterns",
    )
```

#### 3. **Argument Validation**

Validate arguments per command:

```python
# Arguments are validated based on command type:
# - For 'pip': only allow install, list, show, freeze
# - For 'npm': only allow install, list, view
# - For 'git': reject commands that modify .git/config
# - For 'chmod': only allow safe permission modes

for arg in command[1:]:
    if is_dangerous_argument(base_command, arg):
        return CommandValidationResult(
            is_valid=False,
            validation_reason=f"Dangerous argument '{arg}'",
        )
```

#### 4. **Path Traversal Protection**

Prevent directory traversal attacks:

```python
# In validate_path function
if has_excessive_traversal(path):
    # Multiple ../ patterns indicate traversal attempt
    raise PathValidationError(
        message="Path contains excessive traversal patterns",
        operation="path_validation",
    )

if is_system_directory(path):
    # Prevent modifications to system directories
    raise PathValidationError(
        message="Cannot modify system directory",
        operation="system_protection",
    )
```

### Security Usage in CommandRunnerService

```python
class CommandRunnerService:
    """Execute commands with optional security validation."""

    def run_command(self, command: str | list[str]) -> CommandResult:
        """Run command with security validation."""

        # Parse command
        if isinstance(command, str):
            command_list = shlex.split(command)
        else:
            command_list = command

        # Validate command security
        self._validate_command_security(command_list)

        # Execute command
        return self._execute(command_list)

    def _validate_command_security(self, command: list[str]) -> None:
        """Validate using SecurityValidatorService."""
        validator = SecurityValidatorService()
        validation_result = validator.validate_command(command)
        if not validation_result.is_valid:
            raise CommandValidationError(
                command=str(command),
                reason=validation_result.validation_reason,
            )
```

---

## Exception Handling Checklist

### Creating New Exceptions

When creating new domain exceptions, follow this checklist:

- ✓ Create service exception in `womm/exceptions/[domain]/[domain]_service.py`
- ✓ Create interface exception in `womm/exceptions/[domain]/[domain]_interface.py`
- ✓ Export in `womm/exceptions/[domain]/__init__.py`
- ✓ Both inherit from respective base exceptions
- ✓ Include `message`, `operation`, `details` parameters
- ✓ Implement `__str__()` for readable output
- ✓ Add docstrings explaining when to raise

### Using Exceptions in Services

- ✓ Raise service-level exceptions in services
- ✓ Include `operation` parameter for context
- ✓ Include `details` for debugging information
- ✓ Use `raise ... from e` to preserve exception chain
- ✓ Log before raising for debugging

### Using Exceptions in Interfaces

- ✓ Catch service exceptions
- ✓ Wrap in interface exceptions
- ✓ Log original exception with `exc_info=True`
- ✓ Use `raise ... from e` to maintain chain

### Using Exceptions in Commands

- ✓ Catch interface exceptions
- ✓ Show user-friendly error messages
- ✓ Exit with appropriate status code (0 = success, 1 = failure)

---

## Security Best Practices

### DO ✅

1. **Always validate input**: Check before processing
2. **Use SecurityValidatorService**: For all command execution
3. **Use specific exceptions**: Domain-specific errors
4. **Log with context**: Include operation, details, exception type
5. **Preserve exception chain**: Use `from e` in raise statements
6. **Use whitelist approach**: Only allow known commands
7. **Validate paths**: Check for traversal, system directories
8. **Type hints**: Full type hints on all public functions

### DO NOT ❌

1. **Use generic Exception**: Always use specific exceptions
2. **Ignore exceptions**: Always handle or propagate with context
3. **Print output**: Use logging framework
4. **Execute user input directly**: Always validate first
5. **Hardcode secrets**: Use environment variables
6. **Catch and ignore**: Don't silently fail
7. **Use blacklist**: Use whitelist approach instead
8. **Modify exception message**: Preserve original information

---

## Exception Testing

### Test Service Exceptions

```python
# tests/unit/test_project_service_exceptions.py

def test_project_detection_invalid_path():
    """Test exception when path doesn't exist."""
    service = ProjectDetectionService()

    with pytest.raises(ProjectDetectionServiceError) as exc_info:
        service.detect_project(Path("/nonexistent"))

    exc = exc_info.value
    assert "does not exist" in exc.message
    assert exc.operation == "path_validation"
    assert exc.details is not None

def test_project_detection_not_directory():
    """Test exception when path is not directory."""
    service = ProjectDetectionService()

    with pytest.raises(ProjectDetectionServiceError) as exc_info:
        service.detect_project(Path("/tmp/file.txt"))

    exc = exc_info.value
    assert "not a directory" in exc.message
    assert exc.operation == "type_validation"
```

### Test Interface Exception Wrapping

```python
# tests/unit/test_project_interface_exceptions.py

def test_create_interface_wraps_service_exception(mocker):
    """Test interface wraps service exception."""
    interface = ProjectCreateInterface()

    # Mock service to raise exception
    mocker.patch.object(
        interface,
        'detection_service',
        side_effect=ProjectDetectionServiceError(
            message="Detection failed",
            operation="test_operation",
        )
    )

    with pytest.raises(CreateInterfaceError) as exc_info:
        interface.create_project("test", Path("/tmp"))

    exc = exc_info.value
    assert "Failed to create project" in exc.message
    assert exc.operation == "project_creation"
    # Check exception chain is preserved
    assert exc.__cause__ is not None
```

---

## Security Testing

### Test Security Validation

```python
# tests/unit/test_security_validator.py

def test_dangerous_command_rejected():
    """Test dangerous commands are rejected."""
    validator = SecurityValidatorService()

    result = validator.validate_command(["rm", "-rf", "/"])
    assert not result.is_valid
    assert "not allowed" in result.validation_reason.lower()

def test_command_not_in_whitelist():
    """Test non-whitelisted commands rejected."""
    validator = SecurityValidatorService()

    result = validator.validate_command(["eval", "malicious()"])
    assert not result.is_valid
    assert "eval" not in SecurityPatternsConfig.ALLOWED_COMMANDS

def test_valid_command_accepted():
    """Test valid commands are accepted."""
    validator = SecurityValidatorService()

    result = validator.validate_command(["python", "--version"])
    assert result.is_valid
```

---

## Summary

**Exception Architecture**:

- ✓ Two-level hierarchy (Service + Interface)
- ✓ Context-rich exceptions (message, operation, details)
- ✓ Proper exception chaining (`from e`)
- ✓ Domain-specific organization

**Security**:

- ✓ Whitelist-based validation
- ✓ Multi-layer protection (patterns, arguments, paths)
- ✓ Singleton SecurityValidatorService
- ✓ All commands validated before execution

**Error Handling**:

- ✓ Services raise service exceptions
- ✓ Interfaces wrap in interface exceptions
- ✓ Commands handle interface exceptions
- ✓ Comprehensive logging with exc_info=True
