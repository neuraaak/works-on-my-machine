# Dependency Management Architecture

> **Simplified and unified dependency management system**
> Clear categorization and streamlined architecture for managing all project dependencies

## 🎯 Overview {#overview}

The new dependency management architecture provides a **simplified, unified approach** to managing all project dependencies. It eliminates the complexity and duplication of the previous system while maintaining full backward compatibility.

### ✅ **Key Improvements**

- **Clear categorization** of dependencies by type and purpose
- **Unified API** for all dependency operations
- **Eliminated duplication** between managers
- **Simplified architecture** without legacy wrappers
- **Extensible design** for future additions

## 🏗️ Architecture Design {#architecture-design}

### **Core Principles**

1. **Single Responsibility** - Each manager handles one type of dependency
2. **Unified Interface** - Consistent API across all operations
3. **Clear Hierarchy** - Logical dependency relationships
4. **Simplified Design** - No legacy wrappers or complex abstractions

### **Architecture Diagram**

```text
DependencyManager (Main Interface)
├── RuntimesManager (Python, Node.js, Git)
├── DevToolsManager (Language-specific tools)
└── PackageManagersManager (System package managers)
```

## 📦 Dependency Categories {#dependency-categories}

### 1. **Runtimes** (Infrastructure de base)

Core runtime environments required for development:

```python
RUNTIMES = {
    "python": {
        "version": "3.8+",
        "package_managers": ["winget", "chocolatey", "homebrew", "apt"],
        "package_names": {
            "winget": "Python.Python.3.11",
            "chocolatey": "python",
            "homebrew": "python@3.11",
            "apt": "python3",
        }
    },
    "node": {
        "version": "18+",
        "package_managers": ["winget", "chocolatey", "homebrew", "apt"],
        "package_names": {
            "winget": "OpenJS.NodeJS",
            "chocolatey": "nodejs",
            "homebrew": "node",
            "apt": "nodejs",
        }
    },
    "git": {
        "version": "2.30+",
        "package_managers": ["winget", "chocolatey", "homebrew", "apt"],
        "package_names": {
            "winget": "Git.Git",
            "chocolatey": "git",
            "homebrew": "git",
            "apt": "git",
        }
    },
}
```

### 2. **System Package Managers** (Gestionnaires de paquets système)

Platform-specific package managers with priority ordering:

```python
SYSTEM_PACKAGE_MANAGERS = {
    "winget": {"platform": "windows", "priority": 1},
    "chocolatey": {"platform": "windows", "priority": 2},
    "scoop": {"platform": "windows", "priority": 3},
    "homebrew": {"platform": "darwin", "priority": 1},
    "apt": {"platform": "linux", "priority": 1},
    "dnf": {"platform": "linux", "priority": 2},
    "pacman": {"platform": "linux", "priority": 3},
}
```

### 3. **Development Tools** (Outils de développement par langage)

Language-specific development tools organized by category:

```python
DEV_TOOLS = {
    "python": {
        "formatting": ["black", "isort"],
        "linting": ["ruff", "flake8"],
        "security": ["bandit"],
        "testing": ["pytest"],
        "type_checking": ["mypy"],
    },
    "javascript": {
        "formatting": ["prettier"],
        "linting": ["eslint"],
        "testing": ["jest"],
        "bundling": ["webpack", "vite"],
    },
    "universal": {
        "spell_checking": ["cspell"],
        "git_hooks": ["pre-commit"],
    }
}
```

## 🔧 Manager Classes {#manager-classes}

### **DependencyManager** (Main Interface)

Unified entry point for all dependency operations:

```python
class DependencyManager:
    def __init__(self):
        self.runtimes = RuntimesManager()
        self.dev_tools = DevToolsManager()

    def check_runtime(self, runtime: str) -> DependencyResult
    def install_runtime(self, runtime: str) -> DependencyResult
    def check_dev_tool(self, language: str, tool_type: str, tool: str) -> DependencyResult
    def install_dev_tool(self, language: str, tool_type: str, tool: str) -> DependencyResult
    def check_and_install_runtimes(self, runtimes: List[str]) -> InstallationResult
    def check_and_install_dev_tools(self, language: str) -> InstallationResult
```

### **RuntimesManager** (Runtime Dependencies)

Manages core runtime environments:

```python
class RuntimesManager:
    def check_runtime(self, runtime: str) -> Tuple[bool, Optional[str]]
    def install_runtime(self, runtime: str) -> bool
    def _get_best_package_manager(self) -> Optional[str]
    def _install_via_package_manager(self, package_manager: str, package_name: str) -> bool
```

### **DevToolsManager** (Development Tools)

Manages language-specific development tools:

```python
class DevToolsManager:
    def check_dev_tool(self, language: str, tool_type: str, tool: str) -> bool
    def install_dev_tool(self, language: str, tool_type: str, tool: str) -> bool
    def get_required_tools(self, language: str) -> List[str]
```

## 💡 Usage Examples {#usage-examples}

### **Basic Runtime Operations**

```python
from shared.core.dependency_manager import check_runtime, install_runtime

# Check if Python is installed
result = check_runtime("python")
if result.success:
    print(f"Python {result.version} is available")
else:
    print("Python not found")

# Install Node.js if needed
result = install_runtime("node")
if result.success:
    print("Node.js installed successfully")
```

### **Development Tools Management**

```python
from shared.core.dependency_manager import check_dev_tool, install_dev_tool

# Check if Black is installed
result = check_dev_tool("python", "formatting", "black")
if not result.success:
    # Install Black
    result = install_dev_tool("python", "formatting", "black")
```

### **Batch Operations**

```python
from shared.core.dependency_manager import check_and_install_runtimes, check_and_install_dev_tools

# Install all required runtimes
result = check_and_install_runtimes(["python", "node", "git"])
print(f"Installed: {result.installed}")
print(f"Skipped: {result.skipped}")
print(f"Failed: {result.failed}")

# Install all Python dev tools
result = check_and_install_dev_tools("python")
print(f"Python tools installed: {result.installed}")
```

### **Status Checking**

```python
from shared.core.dependency_manager import get_installation_status

# Get comprehensive status
status = get_installation_status(
    runtimes=["python", "node", "git"],
    languages=["python", "javascript"]
)

print(f"Python installed: {status['runtimes']['python']['installed']}")
print(f"Black available: {status['dev_tools']['python']['formatting']['black']['installed']}")
```

## 🚨 Exception Handling Architecture {#exception-handling-architecture}

### **Modular Exception System**

The exception handling system has been completely refactored to provide granular, context-specific error handling with a modular hierarchy:

```text
exceptions/
├── installation/
│   ├── installation_exceptions.py    # 9 installation exceptions
│   └── uninstallation_exceptions.py  # 8 uninstallation exceptions
└── system/
    └── user_path_exceptions.py       # 3 system-specific exceptions
```

### **Exception Categories**

#### **Installation Exceptions** (9 total)

- **4 Utility Exceptions** - For low-level operations
  - `FileVerificationError` - File verification failures
  - `PathUtilityError` - PATH utility operation failures
  - `ExecutableVerificationError` - Executable verification issues
  - `InstallationUtilityError` - General installation utility errors

- **5 Manager Exceptions** - For high-level business logic
  - `InstallationFileError` - File operation failures during installation
  - `InstallationPathError` - PATH configuration issues during installation
  - `InstallationSystemError` - System-level problems during installation
  - `InstallationVerificationError` - Installation verification failures
  - `InstallationManagerError` - General installation manager errors

#### **Uninstallation Exceptions** (8 total)

- **4 Utility Exceptions** - For low-level operations
  - `FileScanError` - File scanning and analysis errors
  - `DirectoryAccessError` - Directory access and permission issues
  - `UninstallationVerificationError` - Uninstallation verification failures
  - `UninstallationUtilityError` - General uninstallation utility errors

- **4 Manager Exceptions** - For high-level business logic
  - `UninstallationFileError` - File removal operation failures
  - `UninstallationPathError` - PATH cleanup issues
  - `UninstallationManagerVerificationError` - Manager-level verification failures
  - `UninstallationManagerError` - General uninstallation manager errors

#### **System Exceptions** (3 total)

- `UserPathError` - User PATH manipulation issues
- `RegistryError` - Windows registry operation problems
- `FileSystemError` - File system access and permission issues

### **Exception Design Principles**

#### **1. Granular Error Handling**

Each exception type represents a specific failure scenario, enabling precise error handling and recovery:

```python
try:
    # Installation operation
    installation_manager.install()
except InstallationFileError as e:
    # Handle file-specific installation errors
    print(f"File error: {e.message}")
except InstallationPathError as e:
    # Handle PATH-specific installation errors
    print(f"PATH error: {e.message}")
except InstallationSystemError as e:
    # Handle system-level installation errors
    print(f"System error: {e.message}")
```

#### **2. Context-Aware Error Information**

All exceptions include detailed context information:

```python
class InstallationFileError(Exception):
    def __init__(self, operation: str, file_path: str, reason: str, details: str):
        self.operation = operation    # e.g., "copy", "verify"
        self.file_path = file_path   # Path to the problematic file
        self.reason = reason         # Human-readable reason
        self.details = details       # Technical details for debugging
        self.message = f"{operation} failed for {file_path}: {reason}"
        super().__init__(self.message)
```

#### **3. Exception Hierarchy**

Exceptions follow a logical hierarchy that mirrors the system architecture:

```text
BaseException
└── Exception
    ├── InstallationUtilityError (Utility level)
    ├── InstallationManagerError (Manager level)
    │   ├── InstallationFileError
    │   ├── InstallationPathError
    │   ├── InstallationSystemError
    │   └── InstallationVerificationError
    ├── UninstallationUtilityError (Utility level)
    ├── UninstallationManagerError (Manager level)
    │   ├── UninstallationFileError
    │   ├── UninstallationPathError
    │   └── UninstallationManagerVerificationError
    └── System Exceptions
        ├── UserPathError
        ├── RegistryError
        └── FileSystemError
```

### **Error Handling Flow**

```text
Exception → Specific Exception Type → Context-Aware Handling → User Feedback
     ↓              ↓                        ↓                    ↓
Logging → Detailed Error Context → Recovery Options → Progress Display
```

### **Integration with Progress System**

Exceptions are seamlessly integrated with the progress display system:

```python
try:
    # Installation operation with progress
    with create_dynamic_layered_progress(stages) as progress:
        installation_manager.install(progress)
except (InstallationFileError, InstallationPathError, InstallationSystemError) as e:
    # Stop progress and display error
    progress.emergency_stop(f"Installation failed: {type(e).__name__}")
    print_error(f"Installation failed: {e.message}")
    if e.details:
        print_error(f"Details: {e.details}")
```

## 🔄 Migration Guide {#migration-guide}

### **From Old PrerequisiteManager**

The API has been simplified to use functions directly:

```python
# Old approach (no longer supported)
from shared.core.prerequisite_manager import PrerequisiteManager
manager = PrerequisiteManager()
results = manager.check_prerequisites(["python", "node"])

# New approach (recommended)
from shared.core.prerequisite_manager import check_prerequisites
results = check_prerequisites(["python", "node"])
```

### **From Old DependencyManager**

Update imports to use the new location:

```python
# Old import
from shared.dependency_manager import dependency_manager

# New import
from shared.core.dependency_manager import dependency_manager
```

### **Recommended Migration**

For new code, use the new unified API:

```python
# Recommended new approach
from shared.core.dependency_manager import (
    check_runtime,
    check_dev_tool,
    check_and_install_runtimes
)

# Check and install runtimes
result = check_and_install_runtimes(["python", "node"])
if result.success:
    print("All runtimes ready")
```

## 📋 API Reference {#api-reference}

### **Core Functions**

- `check_runtime(runtime: str) -> DependencyResult`
- `install_runtime(runtime: str) -> DependencyResult`
- `check_dev_tool(language: str, tool_type: str, tool: str) -> DependencyResult`
- `install_dev_tool(language: str, tool_type: str, tool: str) -> DependencyResult`
- `check_and_install_runtimes(runtimes: List[str]) -> InstallationResult`
- `check_and_install_dev_tools(language: str) -> InstallationResult`
- `get_installation_status(runtimes: List[str] = None, languages: List[str] = None) -> Dict`

### **Result Classes**

- `DependencyResult` - Result of a single dependency operation
- `InstallationResult` - Result of batch installation operations

### **Configuration Constants**

- `RUNTIMES` - Runtime definitions and package mappings
- `SYSTEM_PACKAGE_MANAGERS` - System package manager configurations
- `DEV_TOOLS` - Development tool definitions by language

## 🎯 Benefits

### **For Developers**

- **Simplified API** - One consistent interface for all dependencies
- **Clear categorization** - Easy to understand what each dependency is for
- **Better error handling** - Structured results with detailed information
- **Extensible design** - Easy to add new dependencies and languages

### **For Maintainers**

- **Reduced complexity** - Eliminated duplicate code and logic
- **Clear separation** - Each manager has a single responsibility
- **Better testing** - Modular design enables comprehensive testing
- **Future-proof** - Architecture supports easy expansion

### **For Users**

- **Consistent experience** - Same workflow for all dependency types
- **Better feedback** - Clear status and error messages
- **Reliable installation** - Intelligent fallback and retry mechanisms
- **Cross-platform** - Works consistently across all supported platforms

## 🔮 Future Enhancements

### **Planned Features**

- **Dependency version management** - Automatic version updates
- **Conflict resolution** - Handle dependency conflicts intelligently
- **Custom package sources** - Support for custom package repositories
- **Dependency graphs** - Visualize dependency relationships
- **Performance optimization** - Parallel installation and caching

### **Extension Points**

- **New runtime support** - Easy to add new runtime environments
- **Custom tool categories** - Extensible tool categorization
- **Plugin system** - Third-party dependency managers
- **CI/CD integration** - Automated dependency management in pipelines

---

## Related Documentation

- **📚 [Main Documentation](index.md)** - Project overview
