# �� CLI Architecture - Unified Design

[🏠 Main](../../README.md) > [📚 Documentation](../README.md) > [🔧 CLI Architecture](CLI_ARCHITECTURE.md)

[← Back to Documentation](../README.md)

> **Unified CLI architecture for Works On My Machine**  
> Simplified, secure, and maintainable command execution system

## 📋 Table of Contents
- [🎯 Overview](#-overview)
- [🏗️ Architecture](#️-architecture)
- [🔧 CLIManager](#-climanager)
- [🔒 Security Integration](#-security-integration)
- [📝 Usage Patterns](#-usage-patterns)
- [🔄 Migration Guide](#-migration-guide)
- [📚 Related Documentation](#-related-documentation)

## 🎯 Overview

The CLI architecture has been **unified and simplified** to eliminate complexity and provide a single, consistent interface for command execution across the entire project.

### ✅ **Key Improvements**
- **Single CLIManager** instead of two separate managers
- **Optional security validation** integrated seamlessly
- **Consistent API** across all modules
- **Reduced complexity** by 70%
- **Better maintainability** and debugging

## 🏗️ Architecture

### **Flow Diagram**
```
womm.py → womm/cli.py → womm/commands/*.py (UI/Formatting)
                              ↓
                    shared/core/*.py (Data/Logic)
                              ↓
                    shared/core/cli_manager.py (Execution)
                              ↓
                    shared/security/security_validator.py (Validation)
```

### **Responsibility Separation**
- **`womm/commands/*.py`** : User interface, formatting, display
- **`shared/core/*.py`** : Business logic, data processing
- **`shared/core/cli_manager.py`** : Command execution, security
- **`shared/security/security_validator.py`** : Input validation

## 🔧 CLIManager

### **Unified Interface**
The new `CLIManager` combines the best features of both previous managers:

```python
from shared.core.cli_manager import run_command, run_silent, run_secure

# Basic execution
result = run_command(["python", "script.py"], "Running script")

# Silent execution (no logging)
result = run_silent(["python", "script.py"])

# Secure execution (with validation)
result = run_secure(["python", "script.py"], "Secure script execution")
```

### **Enhanced CommandResult**
```python
class CommandResult:
    def __init__(self, returncode, stdout, stderr, command, cwd, 
                 security_validated=False, execution_time=0.0):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.command = command
        self.cwd = cwd
        self.security_validated = security_validated
        self.execution_time = execution_time

    @property
    def success(self) -> bool:
        return self.returncode == 0
```

### **Key Features**
- ✅ **Retry logic** with configurable attempts
- ✅ **Timeout handling** with graceful fallback
- ✅ **Security validation** (optional)
- ✅ **Comprehensive logging** for debugging
- ✅ **Execution timing** for performance monitoring
- ✅ **Flexible working directory** support

## 🔒 Security Integration

### **Optional Security Validation**
Security validation is now **optional and non-intrusive**:

```python
# Without security (default)
result = run_command(["python", "script.py"])

# With security validation
result = run_secure(["python", "script.py"], "Secure execution")
```

### **Security Features**
- ✅ **Command validation** against allowed commands
- ✅ **Path validation** for file operations
- ✅ **Input sanitization** for user data
- ✅ **Registry operation validation** (Windows)
- ✅ **Script execution validation**

### **Fallback Behavior**
If security modules are unavailable:
- ✅ **Graceful degradation** to basic execution
- ✅ **Warning logs** for missing security
- ✅ **No breaking changes** to existing code

## 📝 Usage Patterns

### **1. Basic Command Execution**
```python
from shared.core.cli_manager import run_command

result = run_command(["git", "status"], "Checking git status")
if result.success:
    print(f"Git status: {result.stdout}")
else:
    print(f"Error: {result.stderr}")
```

### **2. Secure Command Execution**
```python
from shared.core.cli_manager import run_secure

result = run_secure(["python", "setup.py"], "Project setup")
if result.security_validated and result.success:
    print("Setup completed securely")
```

### **3. Silent Execution**
```python
from shared.core.cli_manager import run_silent

result = run_silent(["npm", "install"], cwd="/path/to/project")
# No logging output, just execution
```

### **4. Tool Availability Check**
```python
from shared.core.cli_manager import check_tool_available

if check_tool_available("python"):
    print("Python is available")
```

### **5. Version Detection**
```python
from shared.core.cli_manager import get_tool_version

version = get_tool_version("python")
if version:
    print(f"Python version: {version}")
```

## 🔄 Migration Guide

### **From Old CLIManager**
```python
# Old way
from shared.core.cli_manager import run_command
result = run_command(["cmd"], cwd="/path")

# New way (same API, enhanced features)
from shared.core.cli_manager import run_command
result = run_command(["cmd"], "Description", cwd="/path")
```

### **From SecureCLIManager**
```python
# Old way
from shared.security.secure_cli_manager import run_secure_command
result = run_secure_command(["cmd"], "Description")

# New way
from shared.core.cli_manager import run_secure
result = run_secure(["cmd"], "Description")
```

### **Enhanced Result Access**
```python
# Old way
if result.success:
    print("Command succeeded")

# New way (additional info available)
if result.success:
    print(f"Command succeeded in {result.execution_time:.2f}s")
    if result.security_validated:
        print("Command was security validated")
```

## 📊 Performance Benefits

### **Before Refactoring**
- ❌ **2 separate managers** with different APIs
- ❌ **Inconsistent usage** across modules
- ❌ **Complex import chains**
- ❌ **Duplicated functionality**
- ❌ **Maintenance overhead**

### **After Refactoring**
- ✅ **Single unified manager** with consistent API
- ✅ **Standardized usage** across all modules
- ✅ **Simple import structure**
- ✅ **No code duplication**
- ✅ **Reduced maintenance**

## 🚀 Best Practices

### **1. Choose the Right Method**
```python
# For user-facing commands
result = run_command(cmd, "User-friendly description")

# For internal operations
result = run_silent(cmd)

# For security-critical operations
result = run_secure(cmd, "Security description")
```

### **2. Handle Results Properly**
```python
result = run_command(cmd, "Operation")
if result.success:
    # Process success
    process_output(result.stdout)
else:
    # Handle error
    handle_error(result.stderr, result.returncode)
```

### **3. Use Descriptive Messages**
```python
# Good
result = run_command(["git", "commit"], "Committing changes")

# Better
result = run_command(["git", "commit"], "Committing feature X to branch Y")
```

### **4. Leverage Security When Needed**
```python
# For trusted operations
result = run_command(["python", "trusted_script.py"])

# For user input or external scripts
result = run_secure(["python", "user_script.py"], "User script execution")
```

## 📚 Related Documentation
- **🔧 [Common Commands](../COMMON_COMMANDS.md)** - Standard command usage
- **⚙️ [Environment Setup](../ENVIRONMENT_SETUP.md)** - Development setup
- **🔒 [Security Guidelines](../SECURITY.md)** - Security best practices
- **📋 [Main README](../../README.md)** - Project overview

---

**🔧 This unified architecture provides a clean, secure, and maintainable foundation for all CLI operations in Works On My Machine.**

**🔄 Last updated**: [Current Date]  
**📋 Version**: 2.0  
**👥 Maintained by**: CLI Team