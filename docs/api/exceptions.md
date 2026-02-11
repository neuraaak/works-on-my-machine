# Exception Architecture - WOMM Project

## 📋 **Overview**

The WOMM project uses a **hierarchical and specialized exception system** that follows the architecture of utility modules (`@utils/`) to ensure **consistent** and **contextual** error handling.

---

## 🏗️ **Architecture Structure**

### **📁 Exception Organization**

```text
womm/core/exceptions/
├── __init__.py                    # Centralized public API
├── common_exceptions.py           # Common exceptions
├── installation/                  # Installation exceptions
│   ├── __init__.py
│   ├── installation_exceptions.py
│   └── uninstallation_exceptions.py
├── system/                        # System exceptions
│   ├── __init__.py
│   └── user_path_exceptions.py
├── spell/                         # Spell checking exceptions
│   ├── __init__.py
│   └── spell_exceptions.py
├── project/                       # Project management exceptions
│   ├── __init__.py
│   └── project_exceptions.py
├── lint/                          # Linting exceptions
│   ├── __init__.py
│   └── lint_exceptions.py
├── security/                      # Security exceptions
│   ├── __init__.py
│   └── security_exceptions.py
├── cli/                           # CLI exceptions
│   ├── __init__.py
│   └── cli_exceptions.py
└── file/                          # File scanning exceptions
    ├── __init__.py
    └── file_exceptions.py
```

---

## 🎯 **Design Principles**

### **✅ Logical Hierarchy**

- **Base exceptions** for each domain
- **Specialized exceptions** for specific cases
- **Consistent** and **contextualized** inheritance

### **✅ Correspondence with Utils**

- **Mirror structure** of `womm/core/utils/`
- **Specialized exceptions** per utility module
- **Consistency** between utilities and exceptions

### **✅ Separation of Responsibilities**

- **Utility exceptions**: Errors from utility functions
- **Manager exceptions**: Process management errors
- **Specialized exceptions**: Domain-specific errors

---

## 📊 **Exception Types by Domain**

### **🔧 Installation (9 exceptions)**

```python
# Utilities
InstallationUtilityError
FileVerificationError
PathUtilityError
ExecutableVerificationError

# Managers
InstallationManagerError
InstallationFileError
InstallationPathError
InstallationVerificationError
InstallationSystemError
```

### **🗂️ Uninstallation (8 exceptions)**

```python
# Utilities
UninstallationUtilityError
FileScanError
DirectoryAccessError
UninstallationVerificationError

# Managers
UninstallationManagerError
UninstallationFileError
UninstallationPathError
UninstallationManagerVerificationError
```

### **💻 System (3 exceptions)**

```python
UserPathError
RegistryError
FileSystemError
```

### **🔍 Spell Checking (5 exceptions)**

```python
# Utilities
SpellUtilityError
CSpellError
DictionaryError

# Managers
SpellManagerError
SpellValidationError
```

### **📁 Project Management (6 exceptions)**

```python
# Utilities
ProjectUtilityError
ProjectDetectionError
ProjectValidationError
TemplateError
VSCodeConfigError

# Managers
ProjectManagerError
```

### **🔧 Linting (5 exceptions)**

```python
# Utilities
LintUtilityError
ToolExecutionError
ToolAvailabilityError

# Managers
LintManagerError
LintValidationError
```

### **🛡️ Security (5 exceptions)**

```python
SecurityUtilityError
ValidationError
CommandValidationError
PathValidationError
FileValidationError
```

### **💻 CLI (4 exceptions)**

```python
CLIUtilityError
CommandExecutionError
CommandValidationError
TimeoutError
```

### **📄 File Scanning (4 exceptions)**

```python
FileUtilityError
FileScanError
FileAccessError
SecurityFilterError
```

### **🔧 Common (5 exceptions)**

```python
CommonUtilityError
ImportUtilityError
PathResolutionError
SecurityError
CommandExecutionError
```

---

## 🎯 **Usage Patterns**

### **✅ Centralized Import**

```python
from womm.core.exceptions import (
    InstallationUtilityError,
    SpellUtilityError,
    ProjectValidationError,
    # ... other exceptions as needed
)
```

### **✅ Contextual Handling**

```python
try:
    # Specific operation
    result = some_operation()
except SpellUtilityError as e:
    # Specific handling for spell checking errors
    logger.error(f"Spell error: {e.message}")
    # Specific recovery logic
except ProjectValidationError as e:
    # Specific handling for project validation errors
    logger.error(f"Project validation error: {e.message}")
    # Specific recovery logic
```

### **✅ Integration with UI Logging System**

```python
from womm.core.exceptions import SpellUtilityError
from womm.core.ui.common.console import print_error

try:
    # Spell checking operation
    spell_result = run_spellcheck(file_path)
except SpellUtilityError as e:
    print_error(f"Spell checking failed: {e.message}")
    if e.details:
        print_debug(f"Details: {e.details}")
```

---

## 🔧 **Benefits of This Architecture**

### **✅ Consistency**

- **Mirror structure** with utilities
- **Consistent naming convention**
- **Standardized usage patterns**

### **✅ Maintainability**

- **Specialized exceptions** by domain
- **Clear separation** of responsibilities
- **Integrated documentation** in each exception

### **✅ Extensibility**

- **Easy addition** of new exceptions
- **Modular** and **evolving** structure
- **Simple integration** with new modules

### **✅ Debugging**

- **Contextual** and **informative** error messages
- **Technical details** for debugging
- **Traceability** of errors by domain

---

## 🚀 **Recommended Usage**

### **📋 For Developers**

1. **Identify the domain** of the operation
2. **Import appropriate exceptions**
3. **Use specialized exceptions** rather than generic ones
4. **Provide contextual messages** and technical details
5. **Integrate with UI logging system** for consistent UX

### **📋 For Managers**

1. **Use manager exceptions** for process errors
2. **Propagate utility exceptions** with context
3. **Handle errors** appropriately according to context
4. **Log errors** with UI system

---

## 🎯 **Conclusion**

This **complete and consistent** exception architecture ensures **robust** and **contextual** error handling in the WOMM project, facilitating **development**, **maintenance**, and **debugging** while providing an **optimal user experience**.
