# CLI Documentation

> **Complete CLI documentation for Works On My Machine**
> User guides, command references, and practical examples for all CLI commands

## Overview

The WOMM CLI provides a comprehensive set of commands for project management, development tools setup, and template management. All commands follow consistent patterns and provide both interactive and direct modes.

### ✅ **Key Features**

- **Interactive Mode** - Guided workflows with prompts
- **Direct Mode** - Command-line arguments for automation
- **Rich UI** - Beautiful terminal output with progress bars
- **Cross-platform** - Works on Windows, macOS, and Linux
- **Extensible** - Easy to add new commands and features

## 🚀 Getting Started

### **Installation**

```bash
# Install WOMM globally
pip install works-on-my-machine

# Or run directly from source
python womm.py --help
```

### **First Steps**

1. **Check system compatibility**: `womm system`
2. **Install prerequisites**: `womm install`
3. **Explore templates**: `womm template list`
4. **Create your first project**: `womm create official/python my-project`

## 📁 Command Categories

### **🏗️ Project Management**

- **[CREATE](create.md)** - Create new projects from a Copier template (Python, JavaScript with React/Vue support)
- **[SETUP](setup.md)** - Configure existing projects
- **[TEMPLATES](templates.md)** - Manage the Copier template catalog

### **🔧 Development Tools**

- **[LINT](lint.md)** - Code quality and linting
- **[SPELL](spell.md)** - Spell checking and dictionaries
- **[CONTEXT](context.md)** - Windows context menu integration

### **⚙️ System Management**

- **[INSTALL](install.md)** - Installation and uninstallation
- **[SYSTEM](system.md)** - System detection and validation

## 🔧 Quick Reference

### **Project Creation**

```bash
# Create Python project (interactive prompts)
womm create official/python my-project

# Create JavaScript project with defaults
womm create official/javascript my-app --defaults --data project_name=my-app

# Pre-fill an answer (e.g. React framework) and prompt for the rest
womm create official/javascript my-react-app --data framework=react

# Preview creation without writing anything
womm create official/python my-project --pretend

# Render and prepare the dev environment (venv, deps, git)
womm create official/python my-project --defaults --data project_name=my-project --setup
```

### **Template Management**

```bash
# List catalog templates
womm template list

# Show a single catalog entry
womm template show official/python

# Register a local template under the user namespace
womm template add my-template ./path/to/template

# Scaffold a new Copier template skeleton
womm template init ./my-new-template
```

### **Project Setup**

```bash
# Setup existing project
womm setup

# Setup specific project type
womm setup python
womm setup javascript

# Interactive setup with auto-detection
womm setup --interactive

# Preview setup (dry-run)
womm setup python --dry-run
```

## 📚 Detailed Guides

### **🚀 [Project Creation Guide](create.md)**

Complete guide to creating new projects with different frameworks and configurations.

### **⚙️ [Project Setup Guide](setup.md)**

Configure existing projects with development tools and best practices.

### **📋 [Template Management Guide](templates.md)**

Learn how to create, manage, and use project templates for rapid development.

### **🔍 [Linting Guide](lint.md)**

Code quality tools, linting, and formatting for all supported languages.

### **📝 [Spell Check Guide](spell.md)**

Documentation spell checking and dictionary management.

### **🖱️ [Context Menu Guide](context.md)**

Windows Explorer integration and context menu management.

### **⚙️ [Installation Guide](install.md)**

Install, configure, and manage WOMM across different platforms.

### **🖥️ [System Guide](system.md)**

System detection, validation, and environment checking.

### **🔧 [Common Commands Reference](commands.md)**

Quick reference for all available commands and their options.

## 🎨 UI Features

### **Rich Terminal Output**

- **Progress Bars** - Real-time progress tracking
- **Panels** - Structured information display
- **Tables** - Organized data presentation
- **Colors** - Syntax highlighting and status indicators

### **Interactive Forms**

- **File Selection** - Browse and select files/directories
- **Multi-selection** - Choose multiple items
- **Validation** - Real-time input validation
- **Confirmation** - Safe destructive operations

## 🔗 Related Documentation

- **🔌 [API Documentation](../api/index.md)** - Technical architecture and internals
- **🧪 [Tests Documentation](../tests/index.md)** - Testing framework and practices
- **📊 [Diagrams](../diagrams/architecture.md)** - Visual architecture and flow diagrams
- **📋 [Main Documentation](../index.md)** - Complete documentation index

---

**🔧 This CLI documentation provides comprehensive guides for all WOMM commands with practical examples and best practices.**
