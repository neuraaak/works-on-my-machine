# 📋 Template System Reference

[🏠 Main](../../README.md) > [📚 Documentation](../README.md) > [🔌 API Documentation](README.md) > [📋 Template Reference](TEMPLATES_REFERENCE.md)

[← Back to API Documentation](README.md)

> **Complete technical reference for WOMM template system**  
> Detailed API documentation, file formats, and implementation details

## 📚 Documentation Navigation

**🏠 [Main Documentation](../../README.md)**  
**📚 [Documentation Index](../README.md)**  
**🔌 [API Documentation](README.md)**  
**📋 [Template Reference](TEMPLATES_REFERENCE.md)** (You are here)  
**🔧 [CLI Documentation](../cli/README.md)**

## 📋 Table of Contents
- [🎯 Overview](#-overview)
- [🏗️ Architecture](#️-architecture)
- [📁 File Formats](#-file-formats)
- [🔧 API Reference](#-api-reference)
- [🔄 Processing Pipeline](#-processing-pipeline)
- [🔍 Content Generalization](#-content-generalization)
- [📊 Template Metadata](#-template-metadata)
- [🔒 Security Considerations](#-security-considerations)
- [🐛 Error Handling](#-error-handling)
- [📈 Performance](#-performance)

## 🎯 Overview

The WOMM template system provides a complete solution for creating, managing, and using project templates. It features dynamic content generalization, variable substitution, and a robust storage system.

### ✅ **Core Features**
- **Dynamic Template Generation** - Create templates from any existing project
- **Content Generalization** - Automatic replacement of project-specific content
- **Variable Substitution** - Template variables with `{{VARIABLE}}` syntax
- **Path Generalization** - Dynamic folder and file path substitution
- **Metadata Management** - Comprehensive template information storage
- **Security Validation** - Safe template processing and validation

## 🏗️ Architecture

### **Component Architecture**
```
TemplateManager (Main Controller)
├── Template Creation
│   ├── ProjectScanner
│   ├── ContentGeneralizer
│   ├── PathGeneralizer
│   └── MetadataGenerator
├── Template Usage
│   ├── TemplateValidator
│   ├── VariableSubstitutor
│   ├── FileGenerator
│   └── ProjectCreator
└── Template Management
    ├── TemplateLister
    ├── TemplateDeleter
    └── TemplateInfo
```

### **Storage Architecture**
```
~/.womm/.templates/
├── template-name-1/
│   ├── template.json              # Metadata
│   ├── pyproject.toml.template    # Template files
│   ├── README.md.template
│   └── src/
│       └── {{PROJECT_NAME}}/
│           ├── __init__.py.template
│           └── main.py.template
├── template-name-2/
│   ├── template.json
│   └── ...
└── ...
```

## 📁 File Formats

### **Template File Format**
Template files use the `.template` extension and contain generalized content with variable placeholders.

**Example Template File:**
```python
# src/{{PROJECT_NAME}}/main.py.template
"""
{{PROJECT_NAME}} - Main application module.

Author: {{AUTHOR_NAME}}
Email: {{AUTHOR_EMAIL}}
Version: {{PROJECT_VERSION}}
"""

import sys
from pathlib import Path

def main():
    """Main application entry point."""
    print(f"Hello from {__project_name__}!")
    print(f"Version: {__version__}")
    print(f"Author: {__author__}")

if __name__ == "__main__":
    main()
```

### **Metadata File Format**
Each template includes a `template.json` file with comprehensive metadata.

**Complete Metadata Example:**
```json
{
  "name": "python-django-blog",
  "description": "Template Django blog complet",
  "version": "1.0.0",
  "author": "WOMM CLI",
  "project_type": "python",
  "source_project": "/path/to/original/project",
  "created": "2024-01-15T10:30:00Z",
  "last_modified": "2024-01-15T10:30:00Z",
  "variables": {
    "PROJECT_NAME": "Project name",
    "AUTHOR_NAME": "Author name",
    "AUTHOR_EMAIL": "Author email",
    "PROJECT_VERSION": "0.1.0",
    "PROJECT_DESCRIPTION": "Project description",
    "PROJECT_URL": "Project URL",
    "PROJECT_REPOSITORY": "Project repository"
  },
  "files": [
    "pyproject.toml",
    "src/{{PROJECT_NAME}}/__init__.py",
    "src/{{PROJECT_NAME}}/main.py",
    "tests/test_main.py",
    "README.md"
  ],
  "statistics": {
    "total_files": 10,
    "total_size": 15420,
    "generalized_variables": 15
  },
  "compatibility": {
    "womm_version": "2.6.0",
    "python_version": ">=3.8",
    "platforms": ["windows", "linux", "macos"]
  }
}
```

## 🔧 API Reference

### **TemplateManager Class**

**Location:** `womm/core/managers/project/templates/template_manager.py`

#### **Constructor**
```python
def __init__(self):
    """Initialize the template manager."""
    self.templates_dir = Path.home() / ".womm" / ".templates"
    self.templates_dir.mkdir(parents=True, exist_ok=True)
    self.template_cache: Dict[str, Dict] = {}
```

#### **Core Methods**

##### **create_template_from_project()**
```python
def create_template_from_project(
    self, 
    source_project_path: Path, 
    template_name: str, 
    **kwargs
) -> bool:
    """
    Create a template from an existing project.
    
    Args:
        source_project_path: Path to the existing project
        template_name: Name for the new template
        **kwargs: Additional template metadata
        
    Returns:
        True if template creation was successful, False otherwise
    """
```

**Parameters:**
- `source_project_path` (Path) - Path to source project
- `template_name` (str) - Template name
- `description` (str, optional) - Template description
- `author` (str, optional) - Template author
- `version` (str, optional) - Template version

**Returns:**
- `bool` - Success status

##### **generate_from_template()**
```python
def generate_from_template(
    self,
    template_name: str,
    target_path: Path,
    template_vars: Optional[Dict[str, str]] = None,
) -> bool:
    """
    Generate a project from a template.
    
    Args:
        template_name: Name of the template to use
        target_path: Path where to generate the project
        template_vars: Variables to substitute in templates
        
    Returns:
        True if generation was successful, False otherwise
    """
```

**Parameters:**
- `template_name` (str) - Template name
- `target_path` (Path) - Target directory
- `template_vars` (Dict[str, str], optional) - Variable substitutions

**Returns:**
- `bool` - Success status

##### **list_templates()**
```python
def list_templates(self) -> Dict[str, List[str]]:
    """
    List all available templates.
    
    Returns:
        Dictionary mapping project types to template lists
    """
```

**Returns:**
- `Dict[str, List[str]]` - Templates organized by project type

##### **delete_template()**
```python
def delete_template(self, template_name: str, show_summary: bool = True) -> bool:
    """
    Delete a template.
    
    Args:
        template_name: Name of the template
        show_summary: Whether to show deletion summary
        
    Returns:
        True if deletion was successful, False otherwise
    """
```

**Parameters:**
- `template_name` (str) - Template name
- `show_summary` (bool) - Show deletion summary

**Returns:**
- `bool` - Success status

#### **Private Methods**

##### **_scan_and_generalize_project()**
```python
def _scan_and_generalize_project(
    self, 
    source_path: Path, 
    template_dir: Path
) -> List[str]:
    """
    Scan project and create generalized template files.
    
    Args:
        source_path: Source project path
        template_dir: Template directory
        
    Returns:
        List of template file paths
    """
```

##### **_generalize_content()**
```python
def _generalize_content(self, content: str, source_project_name: str) -> str:
    """
    Generalize content by replacing specific values with template variables.
    
    Args:
        content: Original content
        source_project_name: Source project name
        
    Returns:
        Generalized content
    """
```

##### **_process_template_file()**
```python
def _process_template_file(
    self,
    template_file: str,
    template_dir: Path,
    target_path: Path,
    template_vars: Optional[Dict[str, str]] = None,
) -> bool:
    """
    Process a single template file.
    
    Args:
        template_file: Template file path
        template_dir: Template directory
        target_path: Target directory
        template_vars: Variable substitutions
        
    Returns:
        True if processing was successful, False otherwise
    """
```

## 🔄 Processing Pipeline

### **Template Creation Pipeline**

#### **1. Project Scanning**
```python
# Scan source project for files
for item in source_path.rglob("*"):
    if item.is_file() and not self._should_ignore(item):
        # Process file
        pass
```

#### **2. File Filtering**
**Ignore Patterns:**
- `__pycache__`, `.git`, `.venv`, `venv`
- `node_modules`, `.pytest_cache`, `.mypy_cache`
- `*.pyc`, `*.pyo`, `.DS_Store`, `Thumbs.db`
- `.vscode`, `.idea`

#### **3. Content Generalization**
```python
# Apply generalization patterns
generalizations = [
    (re.escape(source_project_name), "{{PROJECT_NAME}}"),
    (r"John Doe", "{{AUTHOR_NAME}}"),
    (r"john\.doe@example\.com", "{{AUTHOR_EMAIL}}"),
    # ... more patterns
]
```

#### **4. Path Generalization**
```python
# Generalize file paths
generalized_path = rel_path_str.replace(
    source_path.name, "{{PROJECT_NAME}}"
)
```

#### **5. Template Storage**
```python
# Create template file
template_file = template_dir / f"{generalized_path}.template"
template_file.write_text(generalized_content, encoding="utf-8")
```

#### **6. Metadata Generation**
```python
# Generate template.json
template_data = {
    "name": template_name,
    "description": description,
    "version": "1.0.0",
    "author": "WOMM CLI",
    "project_type": project_type,
    "source_project": str(source_project_path),
    "variables": self._extract_template_variables(template_dir),
    "files": template_files,
}
```

### **Template Usage Pipeline**

#### **1. Template Validation**
```python
# Validate template exists
if not template_dir.exists():
    raise TemplateNotFoundError(f"Template '{template_name}' not found")

# Validate template.json
if not self._validate_template(template_name):
    raise TemplateValidationError(f"Template '{template_name}' is invalid")
```

#### **2. Variable Substitution**
```python
# Substitute variables in content
for var_name, var_value in template_vars.items():
    content = content.replace(f"{{{{{var_name}}}}}", str(var_value))
```

#### **3. File Generation**
```python
# Generate output files
for template_file in template_files:
    if not self._process_template_file(
        template_file, template_dir, target_path, template_vars
    ):
        return False
```

#### **4. Path Substitution**
```python
# Substitute variables in file paths
target_file_path = template_file
for var_name, var_value in template_vars.items():
    target_file_path = target_file_path.replace(
        f"{{{{{var_name}}}}}", str(var_value)
    )
```

## 🔍 Content Generalization

### **Generalization Patterns**

#### **Project Name Patterns**
```python
# Source project name variations
patterns = [
    (re.escape(source_project_name), "{{PROJECT_NAME}}"),
    (re.escape(source_project_name.replace("-", "_")), "{{PROJECT_NAME}}"),
    (re.escape(source_project_name.replace("_", "-")), "{{PROJECT_NAME}}"),
]
```

#### **Author Information Patterns**
```python
# Author name patterns
patterns = [
    (r"John Doe", "{{AUTHOR_NAME}}"),
    (r"Jane Smith", "{{AUTHOR_NAME}}"),
    (r"Your Name", "{{AUTHOR_NAME}}"),
]

# Email patterns
patterns = [
    (r"john\.doe@example\.com", "{{AUTHOR_EMAIL}}"),
    (r"jane\.smith@example\.com", "{{AUTHOR_EMAIL}}"),
    (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "{{AUTHOR_EMAIL}}"),
]
```

#### **URL and Repository Patterns**
```python
# Repository patterns
patterns = [
    (r"https://github\.com/[a-zA-Z0-9-]+/[a-zA-Z0-9-]+", "{{PROJECT_REPOSITORY}}"),
    (r"https://gitlab\.com/[a-zA-Z0-9-]+/[a-zA-Z0-9-]+", "{{PROJECT_REPOSITORY}}"),
]

# Project URL patterns
patterns = [
    (r"https://example\.com", "{{PROJECT_URL}}"),
    (r"https://myproject\.com", "{{PROJECT_URL}}"),
]
```

#### **Version Patterns**
```python
# Version number patterns
patterns = [
    (r'"version":\s*"[0-9]+\.[0-9]+\.[0-9]+"', '"version": "{{PROJECT_VERSION}}"'),
    (r'__version__\s*=\s*"[0-9]+\.[0-9]+\.[0-9]+"', '__version__ = "{{PROJECT_VERSION}}"'),
]
```

### **Variable Extraction**

#### **Automatic Variable Detection**
```python
def _extract_template_variables(self, template_dir: Path) -> Dict[str, str]:
    """Extract template variables from template files."""
    variables = {}
    
    # Default variables
    default_vars = {
        "PROJECT_NAME": "Project name",
        "AUTHOR_NAME": "Author name",
        "AUTHOR_EMAIL": "Author email",
        "PROJECT_VERSION": "0.1.0",
        "PROJECT_DESCRIPTION": "Project description",
        "PROJECT_URL": "Project URL",
        "PROJECT_REPOSITORY": "Project repository",
    }
    
    # Scan template files for variables
    for template_file in template_dir.rglob("*.template"):
        content = template_file.read_text(encoding="utf-8")
        matches = re.findall(r"\{\{([^}]+)\}\}", content)
        for match in matches:
            if match not in variables:
                variables[match] = default_vars.get(match, f"{match} value")
    
    return variables
```

## 📊 Template Metadata

### **Metadata Schema**

#### **Required Fields**
- `name` (str) - Template name
- `project_type` (str) - Project type (python, javascript, etc.)
- `version` (str) - Template version

#### **Optional Fields**
- `description` (str) - Template description
- `author` (str) - Template author
- `source_project` (str) - Original project path
- `created` (str) - Creation timestamp
- `last_modified` (str) - Last modification timestamp
- `variables` (Dict[str, str]) - Template variables
- `files` (List[str]) - Template file list
- `statistics` (Dict) - Template statistics
- `compatibility` (Dict) - Compatibility information

### **Statistics Schema**
```json
{
  "statistics": {
    "total_files": 10,
    "total_size": 15420,
    "generalized_variables": 15,
    "template_files": 8,
    "binary_files": 2
  }
}
```

### **Compatibility Schema**
```json
{
  "compatibility": {
    "womm_version": "2.6.0",
    "python_version": ">=3.8",
    "platforms": ["windows", "linux", "macos"],
    "dependencies": ["rich", "click", "inquirerpy"]
  }
}
```

## 🔒 Security Considerations

### **Input Validation**

#### **Template Name Validation**
```python
def validate_template_name(name: str) -> Tuple[bool, str]:
    """Validate template name format."""
    if not name:
        return False, "Template name cannot be empty"
    
    if not re.match(r"^[a-zA-Z0-9_-]+$", name):
        return False, "Template name must contain only letters, numbers, hyphens, and underscores"
    
    if len(name) > 50:
        return False, "Template name must be 50 characters or less"
    
    return True, ""
```

#### **Path Validation**
```python
def validate_template_path(path: Path) -> Tuple[bool, str]:
    """Validate template path security."""
    try:
        # Resolve to absolute path
        abs_path = path.resolve()
        
        # Check for path traversal
        if ".." in str(abs_path):
            return False, "Path traversal not allowed"
        
        # Check permissions
        if not abs_path.exists():
            return False, "Path does not exist"
        
        if not abs_path.is_dir():
            return False, "Path must be a directory"
        
        return True, ""
    except Exception as e:
        return False, f"Path validation error: {e}"
```

### **Content Security**

#### **File Type Validation**
```python
def _is_safe_file_type(file_path: Path) -> bool:
    """Check if file type is safe for template processing."""
    safe_extensions = {
        '.py', '.js', '.ts', '.json', '.toml', '.yaml', '.yml',
        '.md', '.txt', '.cfg', '.ini', '.conf', '.env', '.gitignore'
    }
    
    return file_path.suffix.lower() in safe_extensions
```

#### **Content Sanitization**
```python
def _sanitize_content(content: str) -> str:
    """Sanitize template content for security."""
    # Remove potential script tags
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    
    # Remove potential command injection
    content = re.sub(r'\$\([^)]*\)', '', content)
    
    return content
```

## 🐛 Error Handling

### **Error Types**

#### **TemplateNotFoundError**
```python
class TemplateNotFoundError(Exception):
    """Raised when a template is not found."""
    pass
```

#### **TemplateValidationError**
```python
class TemplateValidationError(Exception):
    """Raised when template validation fails."""
    pass
```

#### **TemplateProcessingError**
```python
class TemplateProcessingError(Exception):
    """Raised when template processing fails."""
    pass
```

### **Error Recovery**

#### **Graceful Degradation**
```python
def _process_template_file(self, template_file: str, ...) -> bool:
    """Process template file with error recovery."""
    try:
        # Process file
        return self._process_file_safely(template_file, ...)
    except TemplateProcessingError as e:
        print_error(f"Error processing {template_file}: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error processing {template_file}: {e}")
        return False
```

#### **Partial Success Handling**
```python
def generate_from_template(self, ...) -> bool:
    """Generate project with partial success handling."""
    success_count = 0
    total_files = len(template_files)
    
    for template_file in template_files:
        if self._process_template_file(template_file, ...):
            success_count += 1
    
    if success_count == total_files:
        return True
    elif success_count > 0:
        print_warn(f"Generated {success_count}/{total_files} files successfully")
        return True
    else:
        return False
```

## 📈 Performance

### **Optimization Strategies**

#### **Template Caching**
```python
def _get_template_info(self, template_name: str) -> Optional[Dict]:
    """Get template info with caching."""
    if template_name in self.template_cache:
        return self.template_cache[template_name]
    
    # Load from file
    template_info = self._load_template_info(template_name)
    if template_info:
        self.template_cache[template_name] = template_info
    
    return template_info
```

#### **Lazy Loading**
```python
def _get_template_files(self, template_dir: Path) -> List[str]:
    """Get template files with lazy loading."""
    if not hasattr(self, '_template_files_cache'):
        self._template_files_cache = {}
    
    cache_key = str(template_dir)
    if cache_key not in self._template_files_cache:
        self._template_files_cache[cache_key] = self._scan_template_files(template_dir)
    
    return self._template_files_cache[cache_key]
```

#### **Batch Processing**
```python
def _process_template_files_batch(self, template_files: List[str], ...) -> bool:
    """Process template files in batches for better performance."""
    batch_size = 10
    for i in range(0, len(template_files), batch_size):
        batch = template_files[i:i + batch_size]
        if not self._process_batch(batch, ...):
            return False
    return True
```

### **Memory Management**

#### **Stream Processing**
```python
def _process_large_file(self, file_path: Path) -> str:
    """Process large files with streaming."""
    content = ""
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            content += self._generalize_line(line)
    return content
```

#### **Garbage Collection**
```python
def _cleanup_cache(self):
    """Clean up template cache to free memory."""
    import gc
    
    self.template_cache.clear()
    if hasattr(self, '_template_files_cache'):
        self._template_files_cache.clear()
    
    gc.collect()
```

---

**📋 This template system reference provides complete technical details for understanding and extending the WOMM template functionality.**
