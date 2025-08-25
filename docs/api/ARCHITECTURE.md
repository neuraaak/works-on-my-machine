# 🏗️ Dependency Management Architecture

[🏠 Main](../README.md) > [📚 Documentation](README.md) > [🏗️ Dependency Architecture](DEPENDENCY_ARCHITECTURE.md)

[← Back to Main Documentation](../README.md)

> **Simplified and unified dependency management system**  
> Clear categorization and streamlined architecture for managing all project dependencies

## 📚 Documentation Navigation

**🏠 [Main Documentation](../README.md)**  
**📚 [Documentation Index](README.md)**  
**🏗️ [Dependency Architecture](DEPENDENCY_ARCHITECTURE.md)** (You are here)  
**🔧 [Prerequisites Installation](PREREQUISITE_INSTALLER.md)**  
**⚙️ [Environment Setup](ENVIRONMENT_SETUP.md)**

## Table of Contents
- [Overview](#overview)
- [Architecture Design](#architecture-design)
- [Dependency Categories](#dependency-categories)
- [Manager Classes](#manager-classes)
- [Usage Examples](#usage-examples)
- [Migration Guide](#migration-guide)
- [API Reference](#api-reference)

## 🎯 Overview

The new dependency management architecture provides a **simplified, unified approach** to managing all project dependencies. It eliminates the complexity and duplication of the previous system while maintaining full backward compatibility.

### ✅ **Key Improvements**
- **Clear categorization** of dependencies by type and purpose
- **Unified API** for all dependency operations
- **Eliminated duplication** between managers
- **Simplified architecture** without legacy wrappers
- **Extensible design** for future additions

## 🏗️ Architecture Design

### **Core Principles**
1. **Single Responsibility** - Each manager handles one type of dependency
2. **Unified Interface** - Consistent API across all operations
3. **Clear Hierarchy** - Logical dependency relationships
4. **Simplified Design** - No legacy wrappers or complex abstractions

### **Architecture Diagram**
```
DependencyManager (Main Interface)
├── RuntimesManager (Python, Node.js, Git)
├── DevToolsManager (Language-specific tools)
└── PackageManagersManager (System package managers)
```

## 📦 Dependency Categories

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

## 🔧 Manager Classes

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

## 💡 Usage Examples

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

## 🔄 Migration Guide

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

## 📋 API Reference

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

**Related Documentation**
- **🔧 [Prerequisites Installation](PREREQUISITE_INSTALLER.md)** - Installation procedures
- **⚙️ [Environment Setup](ENVIRONMENT_SETUP.md)** - Environment configuration
- **📚 [Main Documentation](README.md)** - Project overview 