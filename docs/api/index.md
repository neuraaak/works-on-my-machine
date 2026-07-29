# API Documentation

> **Technical architecture and internal API documentation**
> Deep dive into WOMM's internal structure, classes, and interfaces

## Overview

WOMM's API is built around a modular architecture with clear separation of concerns. The system is designed to be extensible, maintainable, and follows SOLID principles.

### ✅ **Architecture Principles**

- **Single Responsibility** - Each class has one clear purpose
- **Dependency Injection** - Loose coupling between components
- **Interface Segregation** - Small, focused interfaces
- **Open/Closed** - Open for extension, closed for modification
- **DRY** - Don't Repeat Yourself

### 🔄 **Component Flow**

```text
CLI Commands → Project Manager → Language Managers → Template Manager → File System
     ↓              ↓                ↓                ↓              ↓
UI Components → Validation → Security → Progress → Rich Output
```

## 🏗️ Architecture

### **High-Level Architecture**

```text
womm/
├── commands/           # CLI entry points
│   ├── new.py         # Project creation
│   ├── setup.py       # Project setup
│   ├── template.py    # Template management
│   └── ...
├── core/
│   ├── managers/      # Business logic managers
│   │   ├── project/   # Project management
│   │   └── ...
│   ├── ui/           # User interface components
│   │   ├── common/   # Shared UI utilities
│   │   └── project/  # Project-specific UI
│   └── utils/        # Utility functions
│       ├── security/ # Security validation
│       └── project/  # Project utilities
└── languages/        # Language-specific templates
```

### **Manager Hierarchy**

```text
ProjectManager (Main Orchestrator)
├── PythonProjectManager
├── JavaScriptProjectManager
├── TemplateManager
└── ProjectDetector
```

## 🔧 Core Components

### **ProjectManager**

Central orchestrator for all project operations.

**Location:** `womm/core/managers/project/project_manager.py`

**Key Methods:**

- `create_project()` - Create new projects
- `setup_project()` - Configure existing projects
- `detect_project_type()` - Auto-detect project type

**Dependencies:**

- `PythonProjectManager`
- `JavaScriptProjectManager`
- `TemplateManager`
- `ProjectDetector`

### **TemplateManager**

Handles template creation, storage, and generation.

**Location:** `womm/core/managers/project/templates/template_manager.py`

**Key Methods:**

- `create_template_from_project()` - Generate template from project
- `generate_from_template()` - Create project from template
- `list_templates()` - List available templates
- `delete_template()` - Remove template

### **ProjectDetector**

Auto-detects project types based on file signatures.

**Location:** `womm/core/utils/project/project_detector.py`

**Supported Types:**

- Python (pyproject.toml, requirements.txt)
- JavaScript (package.json)
- React (package.json with react dependency)
- Vue (package.json with vue dependency)

## 📋 Template System

### **Template Architecture**

#### **Storage Structure**

```text
~/.womm/templates/
├── template-name/
│   ├── template.json          # Metadata
│   ├── file1.py.template      # Template files
│   ├── file2.txt.template
│   └── src/
│       └── {{PROJECT_NAME}}/
│           └── main.py.template
```

#### **Template Metadata Format**

```json
{
  "name": "template-name",
  "description": "Template description",
  "version": "1.0.0",
  "author": "WOMM CLI",
  "project_type": "python",
  "source_project": "/path/to/original",
  "created": "2024-01-15T10:30:00Z",
  "variables": {
    "PROJECT_NAME": "Project name",
    "AUTHOR_NAME": "Author name",
    "AUTHOR_EMAIL": "Author email"
  },
  "files": ["pyproject.toml", "src/{{PROJECT_NAME}}/main.py"]
}
```

### **Content Generalization**

#### **Variable Substitution**

Templates use `{{VARIABLE_NAME}}` syntax for dynamic content:

| Variable                 | Description     | Example                        |
| ------------------------ | --------------- | ------------------------------ |
| `{{PROJECT_NAME}}`       | Project name    | `my-awesome-app`               |
| `{{AUTHOR_NAME}}`        | Author name     | `John Doe`                     |
| `{{AUTHOR_EMAIL}}`       | Author email    | `john@example.com`             |
| `{{PROJECT_VERSION}}`    | Project version | `0.1.0`                        |
| `{{PROJECT_URL}}`        | Project URL     | `https://example.com`          |
| `{{PROJECT_REPOSITORY}}` | Repository URL  | `https://github.com/user/repo` |

#### **Generalization Patterns**

```python
# Original content
project_name = "my-awesome-blog"
author = "John Doe"
email = "john@example.com"

# Generalized content
project_name = "{{PROJECT_NAME}}"
author = "{{AUTHOR_NAME}}"
email = "{{AUTHOR_EMAIL}}"
```

### **Template Processing Pipeline**

#### **Creation Pipeline**

```text
1. Source Project Scan
   ↓
2. File Filtering (ignore patterns)
   ↓
3. Content Generalization
   ↓
4. Path Generalization
   ↓
5. Template Storage
   ↓
6. Metadata Generation
```

#### **Usage Pipeline**

```text
1. Template Validation
   ↓
2. Variable Substitution
   ↓
3. File Generation
   ↓
4. Path Substitution
   ↓
5. Project Creation
```

## 🎨 UI Components

### **Rich Terminal Interface**

#### **Progress Tracking**

- **DynamicLayeredProgress** - Multi-layer progress bars
- **Real-time Updates** - Live progress feedback
- **Error Handling** - Graceful error display

#### **Interactive Forms**

- **InquirerPy Integration** - Interactive prompts
- **File Selection** - Directory/file browsing
- **Multi-selection** - Checkbox selections
- **Validation** - Real-time input validation

#### **Output Components**

- **Rich Panels** - Structured information display
- **Rich Tables** - Organized data presentation
- **Color Coding** - Status and type indicators

### **UI Component Hierarchy**

```text
UI Components
├── Console Output
│   ├── print_header()
│   ├── print_info()
│   ├── print_error()
│   └── print_success()
├── Progress Tracking
│   ├── DynamicLayeredProgress
│   ├── Progress Bars
│   └── Status Updates
├── Interactive Forms
│   ├── Template Creation
│   ├── Template Deletion
│   └── Project Configuration
└── Rich Display
    ├── Panels
    ├── Tables
    └── Lists
```

## 🔒 Security

### **Input Validation**

#### **SecurityValidator**

**Location:** `womm/core/utils/security/security_validator.py`

**Validation Rules:**

- **Project Names** - Alphanumeric, hyphens, underscores
- **File Paths** - Safe path traversal prevention
- **Template Names** - Valid identifier format
- **User Input** - Sanitization and validation

#### **Validation Methods**

```python
def validate_project_name(name: str) -> Tuple[bool, str]
def validate_project_path(path: Path) -> Tuple[bool, str]
def validate_template_name(name: str) -> Tuple[bool, str]
def validate_user_input(input_str: str, input_type: str) -> Tuple[bool, str]
```

### **File System Security**

- **Path Traversal Prevention** - Safe path handling
- **Permission Checks** - Read/write permission validation
- **Template Isolation** - Template sandboxing

## 📊 Data Flow

### **Template Creation Flow**

```text
User Input → CLI Command → ProjectManager → TemplateManager
     ↓              ↓              ↓              ↓
Validation → Project Detection → File Scanning → Generalization
     ↓              ↓              ↓              ↓
UI Feedback → Progress Tracking → Content Processing → Storage
```

### **Template Usage Flow**

```text
User Input → CLI Command → TemplateManager → File Generation
     ↓              ↓              ↓              ↓
Validation → Template Loading → Variable Substitution → File Creation
     ↓              ↓              ↓              ↓
UI Feedback → Progress Tracking → Path Processing → Project Setup
```

### **Enhanced Error Handling Flow**

```text
Exception → Specific Exception Type → Context-Aware Handling → User Feedback
     ↓              ↓                        ↓                    ↓
Logging → Detailed Error Context → Recovery Options → Progress Display
```

### **Exception Hierarchy**

The system uses a modular exception architecture with 20+ specific exception types:

#### **Installation Exceptions** (9 total)

- **Utility Level**: `FileVerificationError`, `PathUtilityError`, `ExecutableVerificationError`, `InstallationUtilityError`
- **Manager Level**: `InstallationFileError`, `InstallationPathError`, `InstallationSystemError`, `InstallationVerificationError`, `InstallationManagerError`

#### **Uninstallation Exceptions** (8 total)

- **Utility Level**: `FileScanError`, `DirectoryAccessError`, `UninstallationVerificationError`, `UninstallationUtilityError`
- **Manager Level**: `UninstallationFileError`, `UninstallationPathError`, `UninstallationManagerVerificationError`, `UninstallationManagerError`

#### **System Exceptions** (3 total)

- `UserPathError`, `RegistryError`, `FileSystemError`

### **Context-Aware Error Information**

All exceptions include detailed context for precise error handling:

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

## 🔧 Extension Guide

### **Adding New Project Types**

#### **1. Create Language Manager**

```python
class NewLanguageProjectManager(ProjectCreator):
    def create_project(self, project_name: str, project_path: Path, **kwargs) -> bool:
        # Implementation
        pass

    def setup_project(self, project_path: Path, **kwargs) -> bool:
        # Implementation
        pass
```

#### **2. Update ProjectDetector**

```python
def detect_project_type(self, project_path: Path) -> Dict[str, Any]:
    # Add detection logic
    if (project_path / "new-language.config").exists():
        return {"type": "new-language", "confidence": 0.9}
```

#### **3. Register in ProjectManager**

```python
def __init__(self):
    self.language_managers = {
        "python": PythonProjectManager(),
        "javascript": JavaScriptProjectManager(),
        "new-language": NewLanguageProjectManager(),  # Add here
    }
```

### **Adding New Template Variables**

#### **1. Update Generalization Patterns**

```python
def _generalize_content(self, content: str, source_project_name: str) -> str:
    generalizations = [
        # Add new patterns
        (r"custom-pattern", "{{CUSTOM_VARIABLE}}"),
    ]
```

#### **2. Update Variable Extraction**

```python
def _extract_template_variables(self, template_dir: Path) -> Dict[str, str]:
    default_vars = {
        # Add new variables
        "CUSTOM_VARIABLE": "Custom variable description",
    }
```

### **Adding New UI Components**

#### **1. Create UI Component**

```python
def print_custom_component(data: Dict) -> None:
    panel = Panel(
        content,
        title="Custom Component",
        border_style="blue"
    )
    console.print(panel)
```

#### **2. Register in UI Module**

```python
# In __init__.py
from .custom_ui import print_custom_component

__all__ = [
    # Add to exports
    "print_custom_component",
]
```

---

**🔌 This API documentation provides comprehensive technical details for extending and maintaining the WOMM system.**
