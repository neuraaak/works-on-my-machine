# WOMM Services & Interfaces Implementation Patterns

Detailed implementation patterns for services (business logic) and interfaces (orchestration) layers in WOMM. These patterns ensure consistency, maintainability, and proper separation of concerns across the project.

---

## Service Layer Architecture

### Service Class Structure

Every service follows this template:

```python
#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# [DOMAIN] SERVICE - [Service Description]
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
[Service name] implementation for Works On My Machine.

Handles [domain-specific functionality]. Provides [key methods].
Raises domain-specific [DomainNameServiceError] exceptions.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import logging
from pathlib import Path
from typing import Optional

from ...exceptions.[domain] import [DomainServiceError], [SpecificError]
from ...shared.configs import [RelevantConfig]
from ...utils import [utility_functions]

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# SERVICE CLASS
# ///////////////////////////////////////////////////////////////

class [DomainNameService]:
    """[Detailed service description].

    This service is responsible for [functionality].

    Raises:
        [SpecificError]: When [condition] occurs
        [OtherError]: When [condition] occurs

    Example:
        >>> service = [DomainNameService]()
        >>> result = service.operation(param)
        >>> if result.success:
        ...     print("Success:", result.data)
    """

    def __init__(self) -> None:
        """Initialize the service.

        Raises:
            [DomainNameServiceError]: If initialization fails
        """
        try:
            self.logger = logging.getLogger(__name__)
            # Initialize dependencies
        except Exception as e:
            logger.error(f"Failed to initialize [ServiceName]: {e}", exc_info=True)
            raise [DomainNameServiceError](
                message=f"Failed to initialize service: {e}",
                operation="initialization",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def main_operation(self, param: str) -> OperationResult:
        """Main public operation.

        Args:
            param: Description

        Returns:
            OperationResult: Success status and data

        Raises:
            [SpecificError]: When operation fails
        """
        try:
            self.logger.debug(f"Starting operation with param: {param}")

            # Validation
            self._validate_input(param)

            # Business logic
            result = self._perform_operation(param)

            self.logger.info("Operation completed successfully")
            return result

        except [SpecificError]:
            raise
        except Exception as e:
            self.logger.error(f"Operation failed: {e}", exc_info=True)
            raise [DomainNameServiceError](
                message=f"Operation failed: {e}",
                operation="main_operation",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _validate_input(self, param: str) -> None:
        """Validate input parameters.

        Args:
            param: Input to validate

        Raises:
            [SpecificError]: If validation fails
        """
        if not param:
            raise [SpecificError](
                message="Parameter cannot be empty",
                operation="validation",
                details="Empty parameter provided",
            )

    def _perform_operation(self, param: str) -> OperationResult:
        """Perform the actual business logic.

        Args:
            param: Input parameter

        Returns:
            OperationResult: Operation result
        """
        # Pure business logic - no side effects
        return OperationResult(success=True, data={"result": param})

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["[DomainNameService]"]
```

### Service Best Practices

#### 1. **Stateless Design**

Services should be stateless. If state is needed, use dependency injection:

```python
# ❌ BAD: Storing state
class ProjectService:
    def __init__(self):
        self.current_project = None  # Don't store state

    def process_project(self, project):
        self.current_project = project  # Modifying state

# ✅ GOOD: Stateless
class ProjectService:
    def process_project(self, project):
        # Return result, don't store state
        return ProjectResult(project_data=project)
```

#### 2. **Error Handling in Services**

Services raise service-level exceptions with context:

```python
# ✅ GOOD: Specific exception with context
try:
    result = external_operation()
except ExternalError as e:
    raise ProjectServiceError(
        message=f"Failed to process project: {e}",
        operation="external_operation",
        details=f"Exception type: {type(e).__name__}, Original: {str(e)}",
    ) from e

# ❌ BAD: Generic exception
except Exception as e:
    raise ProjectServiceError(f"Error: {e}")  # No operation or context
```

#### 3. **Logging Strategy**

Log at appropriate levels with context:

```python
# ✅ GOOD: Appropriate logging
logger.debug(f"Starting process with param: {param}")
logger.info("Process completed successfully")
logger.warning(f"Unexpected condition encountered: {condition}")
logger.error(f"Process failed with exception: {e}", exc_info=True)

# ❌ BAD: Excessive or incorrect logging
print("Starting...")  # Never use print in production code
logger.info("Started")  # Too vague
logger.error("Error")   # No context
```

#### 4. **Type Hints in Services**

All public methods must have complete type hints:

```python
# ✅ GOOD: Complete type hints
def process_file(self, file_path: Path, options: dict[str, Any] | None = None) -> ProcessResult:
    """Process a file with optional parameters."""
    options = options or {}
    ...

# ❌ BAD: Missing type hints
def process_file(self, file_path, options=None):
    """Process a file with optional parameters."""
    ...
```

#### 5. **Validation Before Processing**

Always validate input before business logic:

```python
# ✅ GOOD: Validation first
def detect_project(self, project_path: Path) -> DetectionResult:
    # Validate input first
    if not project_path.exists():
        raise ProjectServiceError(
            message=f"Project path does not exist",
            operation="path_validation",
            details=f"Path: {project_path}",
        )

    # Then process
    detection_result = self._analyze_project(project_path)
    return detection_result

# ❌ BAD: No validation
def detect_project(self, project_path: Path) -> DetectionResult:
    # Directly process - may fail with unclear errors
    return self._analyze_project(project_path)
```

---

## Interface Layer Architecture

### Interface Class Structure

```python
#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# [DOMAIN] INTERFACE - [Interface Description]
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
[Interface name] - Façade orchestrating [domain] services.

Provides high-level API for [domain] operations by orchestrating
multiple services. Handles UI interactions and error handling.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import logging
from pathlib import Path
from typing import Optional

from ...exceptions.[domain] import [InterfaceError], [ServiceError]
from ...services.[domain] import [DomainService1], [DomainService2]
from ...shared.results import [OperationResult]

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# INTERFACE CLASS
# ///////////////////////////////////////////////////////////////

class [DomainInterface]:
    """[Domain] interface (façade) orchestrating services.

    Provides simplified high-level API for [domain] operations by
    orchestrating multiple services and handling common patterns.

    Usage:
        >>> interface = [DomainInterface]()
        >>> result = interface.operation(param)
        >>> if result.success:
        ...     print("Operation successful")
    """

    def __init__(self) -> None:
        """Initialize the interface with lazy-loaded services.

        Services are lazy-loaded to minimize startup overhead.

        Raises:
            [InterfaceError]: If interface initialization fails
        """
        try:
            self._service1 = None
            self._service2 = None
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            logger.error(f"Failed to initialize [InterfaceClass]: {e}", exc_info=True)
            raise [InterfaceError](
                message=f"Failed to initialize interface: {e}",
                operation="initialization",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # SERVICE PROPERTIES (LAZY INITIALIZATION)
    # ///////////////////////////////////////////////////////////////

    @property
    def service1(self) -> [DomainService1]:
        """Lazy load service1 when needed."""
        if self._service1 is None:
            self._service1 = [DomainService1]()
        return self._service1

    @property
    def service2(self) -> [DomainService2]:
        """Lazy load service2 when needed."""
        if self._service2 is None:
            self._service2 = [DomainService2]()
        return self._service2

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def main_operation(self, param: str) -> [OperationResult]:
        """Main public operation orchestrating services.

        Args:
            param: Input parameter

        Returns:
            [OperationResult]: Structured result with success status

        Raises:
            [InterfaceError]: If operation fails
        """
        try:
            self.logger.debug(f"Starting operation with: {param}")

            # Orchestrate services
            result1 = self.service1.operation(param)
            result2 = self.service2.operation(result1.data)

            self.logger.info("Operation completed successfully")
            return [OperationResult](success=True, data=result2.data)

        except [ServiceError] as e:
            self.logger.error(f"Service operation failed: {e}", exc_info=True)
            raise [InterfaceError](
                message=f"Failed to complete operation: {e}",
                operation="main_operation",
                details=f"Service error: {type(e).__name__}",
            ) from e
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            raise [InterfaceError](
                message=f"Unexpected error during operation: {e}",
                operation="main_operation",
                details=f"Exception type: {type(e).__name__}",
            ) from e

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["[DomainInterface]"]
```

### Interface Best Practices

#### 1. **Lazy Service Initialization**

Load services only when needed using `@property`:

```python
# ✅ GOOD: Lazy initialization
@property
def project_service(self) -> ProjectService:
    if self._project_service is None:
        self._project_service = ProjectService()
    return self._project_service

def create_project(self, ...):
    # Service loaded only when this method is called
    result = self.project_service.create(...)

# ❌ BAD: Eager initialization
def __init__(self):
    self.project_service = ProjectService()  # Always initialized
    self.template_service = TemplateService()  # Always initialized
    # May be unused if interface method isn't called
```

#### 2. **Exception Wrapping Pattern**

Always catch service exceptions and wrap in interface exceptions:

```python
# ✅ GOOD: Proper exception wrapping
try:
    detection_result = self.detection_service.detect_project(project_path)
except ProjectDetectionServiceError as e:
    logger.error(f"Detection failed: {e}", exc_info=True)
    raise CreateInterfaceError(
        message=f"Failed to initialize project creation: {e}",
        operation="project_detection",
        details=f"Service exception: {type(e).__name__}",
    ) from e

# ❌ BAD: Not wrapping exceptions
detection_result = self.detection_service.detect_project(project_path)
# ServiceError propagates as-is (breaks abstraction)
```

#### 3. **Service Orchestration**

Interface coordinates multiple services:

```python
# ✅ GOOD: Clear orchestration
def create_project(self, name: str, path: Path) -> ProjectCreationResult:
    try:
        # Step 1: Detect project type
        detection = self.detection_service.detect_project(path)

        # Step 2: Validate project
        validation = self.validation_service.validate_project(name, path)

        # Step 3: Create project
        creation = self.creation_service.create_project(name, path, detection)

        return ProjectCreationResult(success=True, ...)
    except ...
```

#### 4. **Result Model Returns**

Always return structured result models, never raw values:

```python
# ✅ GOOD: Structured results
def detect_system(self) -> SystemDetectionResult:
    result = self.detector_service.detect()
    return SystemDetectionResult(
        success=True,
        message="System detection completed",
        system_info={...},
        available_tools=[...],
    )

# ❌ BAD: Raw return values
def detect_system(self) -> dict:
    result = self.detector_service.detect()
    return result.data  # Unstructured data
```

#### 5. **Logging in Interfaces**

Log operation flow at INFO level, details at DEBUG level:

```python
# ✅ GOOD: Appropriate logging
logger.debug(f"Starting project creation with: {name}, {path}")
logger.info("Project creation completed successfully")

# ❌ BAD: Missing logging
# No visibility into what interface is doing
```

---

## Common Service Patterns

### Pattern: Validation Service

```python
class [DomainValidationService]:
    """Validation service for [domain]."""

    def validate(self, input_data: str) -> ValidationResult:
        """Validate input data.

        Returns:
            ValidationResult with is_valid flag and errors list
        """
        errors = []

        if not input_data:
            errors.append("Input cannot be empty")

        if len(input_data) < 3:
            errors.append("Input must be at least 3 characters")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
        )
```

### Pattern: Detection Service

```python
class ProjectDetectionService:
    """Detect project type and configuration."""

    def detect_project(self, project_path: Path) -> DetectionResult:
        """Detect project type from path.

        Returns:
            DetectionResult with detected type and configuration
        """
        # Check for project files in order of specificity
        if (project_path / "pyproject.toml").exists():
            return DetectionResult(project_type="python", ...)

        if (project_path / "package.json").exists():
            return DetectionResult(project_type="javascript", ...)

        raise ProjectDetectionServiceError(
            message="Could not detect project type",
            operation="detection",
            details=f"Path: {project_path}",
        )
```

### Pattern: Manager Service

```python
class DependencyManager:
    """Manage system and project dependencies."""

    def get_installed_version(self, dependency: str) -> str | None:
        """Get installed version of dependency.

        Returns:
            Version string or None if not installed
        """
        try:
            result = CommandRunnerService.get_instance().run_silent(
                ["dependency", "--version"],
            )
            return self._parse_version(result.output)
        except CommandExecutionError:
            return None
```

---

## Configuration Access Patterns

### Config Usage in Services

```python
from womm.shared.configs.runtime import RuntimeConfig
from womm.shared.configs.security import SecurityPatternsConfig

class RuntimeService:
    def check_python_version(self, version: str) -> bool:
        """Check if Python version meets requirements."""
        # Access config (read-only)
        required = RuntimeConfig.RUNTIMES.get("python", {}).get("min_version")
        return self._compare_versions(version, required)

class SecurityValidatorService:
    def validate_command(self, command: list[str]) -> ValidationResult:
        """Validate command against whitelist."""
        base_command = command[0].lower()

        # Config is immutable, accessed directly
        if base_command not in SecurityPatternsConfig.ALLOWED_COMMANDS:
            return ValidationResult(is_valid=False, reason="Not allowed")

        return ValidationResult(is_valid=True)
```

---

## Result Model Pattern

All operations return structured result models:

```python
from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class OperationResult:
    """Standard operation result."""
    success: bool
    message: str = ""
    data: dict[str, Any] | None = None
    error_details: str | None = None
    operation: str = ""

# Usage in service
def my_operation(self) -> OperationResult:
    try:
        data = self._do_work()
        return OperationResult(
            success=True,
            message="Operation completed",
            data={"result": data},
        )
    except Exception as e:
        return OperationResult(
            success=False,
            message="Operation failed",
            error_details=str(e),
        )
```

---

## Anti-Patterns in Services/Interfaces

### ❌ DO NOT

1. **Store state in services**: Services should be stateless
2. **Print output**: Use logging framework only
3. **Direct UI operations**: UI code belongs in commands layer
4. **Share mutable state**: Use immutable configs and dependency injection
5. **Catch generic Exception**: Always catch specific exceptions
6. **Ignore exceptions**: Always log and handle appropriately
7. **Direct file I/O**: Use centralized file services
8. **Global variables**: Use dependency injection instead

### ✅ DO

1. **Inject dependencies**: Pass dependencies to services
2. **Use logging**: `logging.getLogger(__name__)`
3. **Return result models**: Structured results from interfaces
4. **Validate input**: Check before processing
5. **Log with context**: Include operation, details, exception type
6. **Type hint everything**: Full type hints on public methods
7. **Lazy initialize**: Load services in `@property` methods
8. **Wrap exceptions**: Service errors → Interface errors

---

## Testing Services & Interfaces

### Service Testing Pattern

```python
# tests/unit/test_project_detection_service.py

def test_detect_python_project():
    """Test detecting Python project."""
    service = ProjectDetectionService()

    # Mock or use fixture for project path
    result = service.detect_project(python_project_path)

    assert result.project_type == "python"
    assert result.has_pyproject_toml

def test_detect_nonexistent_project():
    """Test error handling for nonexistent project."""
    service = ProjectDetectionService()

    with pytest.raises(ProjectDetectionServiceError):
        service.detect_project(Path("/nonexistent/path"))
```

### Interface Testing Pattern

```python
# tests/unit/test_project_create_interface.py

def test_create_project_orchestration(mocker):
    """Test interface orchestrates services correctly."""
    interface = ProjectCreateInterface()

    # Mock services
    mocker.patch.object(interface, 'detection_service')
    mocker.patch.object(interface, 'template_service')

    result = interface.create_project("my-project", Path("/tmp"))

    # Verify service calls
    interface.detection_service.detect.assert_called_once()
    interface.template_service.load.assert_called_once()
```

---

## Summary

**Services** implement pure business logic with:

- ✓ Stateless design
- ✓ Service-level exceptions
- ✓ Input validation
- ✓ Complete type hints
- ✓ Appropriate logging

**Interfaces** orchestrate services with:

- ✓ Lazy service initialization
- ✓ Exception wrapping
- ✓ Multi-service coordination
- ✓ Structured result models
- ✓ Clear operation flow logging
