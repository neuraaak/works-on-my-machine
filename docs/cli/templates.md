# Template Management Guide

> **Complete guide to WOMM template management**
> Create, manage, and use project templates for rapid development

## 🎯 Overview

WOMM templates allow you to create reusable project skeletons from existing projects. Templates automatically generalize project-specific content (names, paths, configurations) and can be used to quickly bootstrap new projects with consistent structure and tooling.

### ✅ **Key Features**

- **Dynamic Generation** - Create templates from any existing project
- **Content Generalization** - Automatically replace project-specific content
- **Interactive Creation** - Guided template creation with prompts
- **Multi-selection Management** - Manage multiple templates efficiently
- **Rich UI** - Beautiful terminal interface with progress tracking

### 🔄 **Template Workflow**

```text
Existing Project → Template Creation → Content Generalization → Template Storage
                                    ↓
New Project ← Template Usage ← Variable Substitution ← Template Selection
```

## 🚀 Quick Start

### **1. Create Your First Template**

```bash
# From an existing project
womm template create --from-project ./my-python-project

# Interactive mode
womm template create --interactive
```

### **2. List Available Templates**

```bash
womm template list
```

### **3. Use a Template**

```bash
# Create new project from template
womm template use my-python-template --project-name new-project

# Specify target directory
womm template use my-template --project-name my-app --path ./projects/
```

### **4. Manage Templates**

```bash
# Get template information
womm template info my-template

# Delete template
womm template delete my-template

# Interactive deletion (multi-selection)
womm template delete --interactive
```

## 📋 Template Commands

### **📋 `womm template list`**

List all available templates with project types and descriptions.

**Output Example:**

```text
📋 Available Templates
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Project Type    ┃ Template Name             ┃ Description                              ┃  Files   ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ python          │ python-django-blog        │ Template Django blog complet             │    10    │
│ javascript      │ javascript-react-app      │ Template React application               │    9     │
└─────────────────┴───────────────────────────┴──────────────────────────────────────────┴──────────┘
```

### **🚀 `womm template create`**

Create a new template from an existing project.

**Syntax:**

```bash
womm template create [TEMPLATE_NAME] --from-project <PATH> [--description <DESC>]
womm template create --interactive
```

**Options:**

- `TEMPLATE_NAME` - Name for the template (auto-generated if not provided)
- `--from-project <PATH>` - Path to existing project
- `--description <DESC>` - Template description
- `--interactive` - Use interactive mode

**Examples:**

```bash
# Direct mode
womm template create --from-project ./my-project --description "My awesome template"

# With custom name
womm template create my-custom-template --from-project ./my-project

# Interactive mode
womm template create --interactive
```

### **🎯 `womm template use`**

Create a new project from a template.

**Syntax:**

```bash
womm template use <TEMPLATE_NAME> [--project-name <NAME>] [--path <PATH>] [--author-name <NAME>] [--author-email <EMAIL>]
```

**Options:**

- `TEMPLATE_NAME` - Name of template to use
- `--project-name <NAME>` - Name for the new project
- `--path <PATH>` - Target directory (default: current directory)
- `--author-name <NAME>` - Author name
- `--author-email <EMAIL>` - Author email
- `--project-url <URL>` - Project URL
- `--project-repository <URL>` - Repository URL

**Examples:**

```bash
# Basic usage
womm template use python-django-blog --project-name my-blog

# With custom path and author
womm template use react-app --project-name my-app --path ./projects/ --author-name "John Doe" --author-email "john@example.com"
```

### **🗑️ `womm template delete`**

Delete one or more templates.

**Syntax:**

```bash
womm template delete <TEMPLATE_NAME>
womm template delete --interactive
```

**Examples:**

```bash
# Delete single template
womm template delete my-template

# Interactive deletion (multi-selection)
womm template delete --interactive
```

### **ℹ️ `womm template info`**

Display detailed information about a template.

**Syntax:**

```bash
womm template info <TEMPLATE_NAME>
```

**Output Example:**

```text
📋 Template: python-django-blog
┌─────────────────────────────────────────────────────────────────────────────┐
│ Name: python-django-blog                                                    │
│ Description: Template Django blog complet                                   │
│ Project Type: python                                                        │
│ Version: 1.0.0                                                              │
│ Author: WOMM CLI                                                            │
│ Source Project: /path/to/original/project                                   │
│                                                                             │
│ Template Variables:                                                         │
│   • PROJECT_NAME: Project name                                              │
│   • AUTHOR_NAME: Author name                                                │
│   • AUTHOR_EMAIL: Author email                                              │
│                                                                             │
│ Files (10):                                                                 │
│   • pyproject.toml                                                          │
│   • src/{{PROJECT_NAME}}/main.py                                           │
│   • tests/test_main.py                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🎨 Interactive Mode

### **Template Creation Interactive**

When using `--interactive`, WOMM guides you through:

1. **Project Selection** - Browse and select source project
2. **Template Name** - Enter custom name or auto-generate
3. **Description** - Add template description

**Example Flow:**

```text
📁 Select the source project to create template from: [Browse...]
📝 Enter template name (leave empty for auto-generation):
📄 Enter template description: Template for Django blog projects
```

### **Template Deletion Interactive**

Interactive deletion provides:

1. **Multi-selection** - Choose multiple templates
2. **Confirmation** - Confirm before deletion
3. **Summary** - List of deleted templates

**Example Flow:**

```text
🗑️ Select templates to delete (use space to select/deselect):
  ☐ python-django-blog (python) - Template Django blog complet
  ☑ javascript-react-app (javascript) - Template React application
  ☐ python-simple (python) - Simple Python template

⚠️ Are you sure you want to delete the selected templates? Yes
```

## 🔧 Template Variables

### **Automatic Variables**

Templates automatically include these variables:

| Variable                 | Description     | Example                        |
| ------------------------ | --------------- | ------------------------------ |
| `{{PROJECT_NAME}}`       | Project name    | `my-awesome-app`               |
| `{{AUTHOR_NAME}}`        | Author name     | `John Doe`                     |
| `{{AUTHOR_EMAIL}}`       | Author email    | `john@example.com`             |
| `{{PROJECT_VERSION}}`    | Project version | `0.1.0`                        |
| `{{PROJECT_URL}}`        | Project URL     | `https://example.com`          |
| `{{PROJECT_REPOSITORY}}` | Repository URL  | `https://github.com/user/repo` |

### **Content Generalization**

WOMM automatically generalizes:

- **Project names** in file content and paths
- **Author information** in configuration files
- **URLs and repositories** in project files
- **Version numbers** in package files

**Example Generalization:**

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

## 📁 Template Storage

### **Storage Location**

Templates are stored in: `~/.womm/templates/`

### **Template Structure**

```text
~/.womm/templates/
├── template-name/
│   ├── template.json          # Template metadata
│   ├── file1.py.template      # Template files
│   ├── file2.txt.template
│   └── src/
│       └── {{PROJECT_NAME}}/
│           └── main.py.template
```

### **Template Metadata**

Each template includes a `template.json` file:

```json
{
  "name": "python-django-blog",
  "description": "Template Django blog complet",
  "version": "1.0.0",
  "author": "WOMM CLI",
  "project_type": "python",
  "source_project": "/path/to/original/project",
  "created": "2024-01-15T10:30:00Z",
  "variables": {
    "PROJECT_NAME": "Project name",
    "AUTHOR_NAME": "Author name",
    "AUTHOR_EMAIL": "Author email"
  },
  "files": [
    "pyproject.toml",
    "src/{{PROJECT_NAME}}/main.py",
    "tests/test_main.py"
  ]
}
```

## 💡 Use Cases

### **1. Standardize Project Structure**

Create templates for consistent project layouts across your team.

```bash
# Create template from well-structured project
womm template create --from-project ./standard-python-project --description "Standard Python project structure"

# Use template for new projects
womm template use standard-python --project-name new-feature
```

### **2. Framework Templates**

Create templates for different frameworks and configurations.

```bash
# Django template
womm template create --from-project ./django-blog --description "Django blog template"

# React template
womm template create --from-project ./react-app --description "React application template"

# FastAPI template
womm template create --from-project ./fastapi-service --description "FastAPI microservice template"
```

### **3. Team Onboarding**

Help new team members get started quickly.

```bash
# Create onboarding template
womm template create --from-project ./team-starter --description "Team onboarding template"

# New team member uses template
womm template use team-starter --project-name my-first-project
```

### **4. Microservices**

Create consistent microservice templates.

```bash
# Create microservice template
womm template create --from-project ./microservice --description "Standard microservice template"

# Use for new services
womm template use microservice --project-name user-service
womm template use microservice --project-name auth-service
```

## 🔍 Troubleshooting

### **Common Issues**

**Template not found:**

```bash
# Check available templates
womm template list

# Verify template name spelling
womm template info template-name
```

**Permission errors:**

```bash
# Check template directory permissions
ls -la ~/.womm/templates/

# Fix permissions if needed
chmod 755 ~/.womm/templates/
```

**Variable substitution issues:**

```bash
# Check template variables
womm template info template-name

# Verify variable syntax in template files
cat ~/.womm/templates/template-name/template.json
```

### **Debug Mode**

Enable verbose output for troubleshooting:

```bash
# Set debug environment variable
export WOMM_DEBUG=1

# Run template command
womm template create --from-project ./my-project
```

## 📚 Examples

### **Complete Workflow Example**

```bash
# 1. Create a well-structured Python project
womm new python my-standard-project --target ./templates/

# 2. Customize the project (add your standard tools, configs, etc.)
cd my-standard-project
# ... customize project ...

# 3. Create template from the project
womm template create --from-project ./my-standard-project --description "My standard Python project template"

# 4. List templates to verify
womm template list

# 5. Use template for new projects
womm template use my-standard-project --project-name feature-x
womm template use my-standard-project --project-name feature-y
```

### **React Template Example**

```bash
# 1. Create React project
womm new react my-react-template

# 2. Customize with your standard setup
cd my-react-template
# ... add standard components, configs, etc ...

# 3. Create template
womm template create --from-project ./my-react-template --description "Standard React app with my setup"

# 4. Use template
womm template use my-react-template --project-name new-app --path ./projects/
```

### **Team Template Example**

```bash
# 1. Create team standard project
womm new python team-standard

# 2. Add team-specific configurations
cd team-standard
# ... add team linting rules, testing setup, etc ...

# 3. Create team template
womm template create --from-project ./team-standard --description "Team standard Python project"

# 4. Share with team (templates are stored locally)
# Team members can copy ~/.womm/templates/team-standard/ to their machines
```

---

**📋 This template management guide provides everything you need to create, manage, and use project templates effectively with WOMM.**
