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
CLI Commands → Project Manager → Template Store → Copier Rendering → File System
     ↓              ↓                ↓                ↓              ↓
UI Components → Validation → Security → Progress → Rich Output
```

## 🏗️ Architecture

### **High-Level Architecture**

```text
womm/
├── commands/           # CLI entry points
│   ├── create.py      # Project creation (Copier-backed)
│   ├── setup.py       # Project setup
│   ├── template.py    # Template catalog management
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
└── copier/            # Copier templates (official catalog + meta-template)
```

### **Manager Hierarchy**

```text
ProjectManager (Main Orchestrator)
├── TemplateStoreInterface   # Catalog CRUD (list, show, add, remove, update, init)
├── CopierProjectCreationService   # Renders a template via Copier
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

- `TemplateStoreInterface`
- `CopierProjectCreationService`
- `ProjectDetector`

### **TemplateStoreInterface / CopierProjectCreationService**

Project rendering is delegated entirely to [Copier](https://copier.readthedocs.io/).
`TemplateStoreInterface` manages the template *catalog* (list, show, add,
remove, update, init); `CopierProjectCreationService` renders a template
into a destination directory via `copier.run_copy`. No language, framework,
or variant mapping lives in Python code — those choices are declared in
each template's `copier.yml`.

**Location:** `womm/interfaces/project/template_store_interface.py`,
`womm/services/project/copier_project_creation_service.py`

**Key Methods:**

- `TemplateStoreInterface.list_templates()` - List catalog entries
- `TemplateStoreInterface.show_template()` - Show one catalog entry
- `TemplateStoreInterface.add_template()` / `remove_template()` / `update_template()` - Manage user templates
- `CopierProjectCreationService.create_project()` - Render a project from a template

### **ProjectDetector**

Auto-detects project types based on file signatures.

**Location:** `womm/core/utils/project/project_detector.py`

**Supported Types:**

- Python (pyproject.toml, requirements.txt)
- JavaScript (package.json)
- React (package.json with react dependency)
- Vue (package.json with vue dependency)

## 📋 Template System

Templates are standard [Copier](https://copier.readthedocs.io/) templates:
a `copier.yml` declaring the questions (name, type, choices, defaults) plus
a `template/` directory of Jinja-rendered files. WOMM does not implement its
own variable-substitution or content-generalization engine — Copier owns
that entirely, and no per-language/framework mapping lives in WOMM's Python
code.

### **Official Catalog**

- `official/python` — `src/womm/assets/copier/official/python/`
- `official/javascript` — `src/womm/assets/copier/official/javascript/`
- Meta-template used by `womm template init` — `src/womm/assets/copier/meta/`

### **User Templates**

Registered with `womm template add <identifier> <source>`; recorded under
`~/.womm/templates/` (or `%WOMM_HOME%` if set). See
[Template Management](../cli/templates.md) for the full CLI surface.

### **Rendering Pipeline**

```text
1. Resolve template identifier → catalog entry (source path)
   ↓
2. copier.run_copy(source, destination, data=answers, defaults=..., overwrite=...)
   ↓
3. Copier prompts for/consumes answers per copier.yml
   ↓
4. Files rendered into destination
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

### **Template Catalog Flow**

```text
User Input → CLI Command → TemplateStoreInterface → TemplateStoreService
     ↓              ↓                ↓                       ↓
Validation → Identifier Lookup → Catalog Read/Write → Result
```

### **Project Creation Flow**

```text
User Input → CLI Command → CopierProjectCreationService → copier.run_copy()
     ↓              ↓                    ↓                        ↓
Validation → Template Resolution → Answer Collection → File Rendering
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

### **Adding a New Template Question**

Template variables are Copier questions declared directly in the template's
`copier.yml` — no Python code changes are needed:

```yaml
# src/womm/assets/copier/official/<template>/copier.yml
custom_variable:
  type: str
  help: "Custom variable description"
  default: ""
```

Reference it from any file under `template/` using Jinja syntax
(`{{ custom_variable }}`), or in the template's filenames themselves.

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
