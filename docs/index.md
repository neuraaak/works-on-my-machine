# Welcome to WOMM Documentation

[![PyPI](https://img.shields.io/badge/PyPI-works--on--my--machine-orange.svg)](https://pypi.org/project/works-on-my-machine/)
[![PyPI version](https://img.shields.io/pypi/v/works-on-my-machine)](https://pypi.org/project/works-on-my-machine/)
[![Python versions](https://img.shields.io/pypi/pyversions/works-on-my-machine)](https://pypi.org/project/works-on-my-machine/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/neuraaak/works-on-my-machine/blob/main/LICENSE)

![WOMM Logo](https://raw.githubusercontent.com/neuraaak/works-on-my-machine/refs/heads/main/docs/assets/logo-min.png)

**Works On My Machine (WOMM)** is a comprehensive development environment manager that eliminates the "it works on my machine" problem. It provides a unified CLI tool that automatically sets up professional development environments for Python and JavaScript projects.

## ✨ Key Features

- ✅ **One-Command Setup** - Complete project initialization with professional tooling
- ✅ **Cross-Platform** - Works seamlessly on Windows, macOS, and Linux
- ✅ **Smart Detection** - Automatically detects project types and applies appropriate configurations
- ✅ **Template System** - Create reusable project templates from existing projects
- ✅ **Professional Tooling** - Pre-configured with industry-standard tools (Black, ESLint, Prettier, etc.)
- ✅ **Interactive Mode** - Guided setup with beautiful CLI interfaces
- ✅ **Comprehensive Documentation** - Complete guides for every feature
- ✅ **Windows Integration** - Context menu integration for right-click project creation

## 🚀 Quick Start

### Installation

```bash
# From PyPI (recommended)
pip install works-on-my-machine
```

Or from source:

```bash
git clone https://github.com/neuraaak/works-on-my-machine.git
cd works-on-my-machine
python womm.py install
```

### First Project

```bash
# Create a Python project
womm new python my-awesome-app

# Create a React project
womm new javascript my-react-app --type react

# Interactive mode with auto-detection
womm new --interactive
```

### Setup Existing Project

```bash
# Setup Python project
womm setup python

# Auto-detect and setup
womm setup detect
```

## 📚 Documentation Structure

| Section                               | Description                                          |
| ------------------------------------- | ---------------------------------------------------- |
| [Getting Started](getting-started.md) | Installation, basic usage, and first steps           |
| [API Reference](api/index.md)         | Complete API documentation for all modules           |
| [CLI Reference](cli/index.md)         | Command-line interface documentation                 |
| [Examples](examples/index.md)         | Practical examples and use cases                     |
| [User Guides](guides/index.md)        | In-depth guides for configuration and best practices |
| [Diagrams](diagrams/architecture.md)  | Architecture and workflow visualizations             |

## 🎯 Main Components

WOMM is organized into **4 main layers**:

### Commands Layer

- **CLI Commands** – User-facing commands (new, setup, lint, spell, system)
- **Interactive Mode** – Guided workflows with rich prompts and validation
- **Context Menu** – Windows right-click integration for quick project creation

### Business Logic Layer

- **ProjectManager** – Project creation and setup orchestration
- **TemplateManager** – Template management, creation, and generation
- **DependencyManager** – Runtime and development tools management
- **ConfigManager** – Configuration loading and validation

### Execution Layer

- **InstallationManager** – Installation and uninstallation processes
- **EnvironmentManager** – Environment configuration and PATH management
- **UserPathManager** – System PATH modifications (Windows/Unix)
- **SecurityValidator** – Input validation and security checks

### Infrastructure Layer

- **UI Components** – Rich terminal output, progress tracking, and tables
- **File Operations** – Cross-platform file management and operations
- **System Detection** – Platform and tool detection utilities
- **Exception Handling** – Hierarchical exception system

For detailed documentation, see [API Reference](api/index.md).

## 🔧 Supported Project Types

### Python Projects

- **Tooling**: Virtual environments, Black, pytest, mypy, ruff, pylint
- **Configuration**: Pre-commit hooks, VSCode settings, pyproject.toml
- **Dependencies**: Automatic requirements.txt and requirements-dev.txt

### JavaScript Projects

- **Tooling**: npm/yarn, ESLint, Prettier, Jest
- **Frameworks**: React, Vue support with Vite
- **Configuration**: Webpack, Babel, TypeScript support

### Template System

- **Create templates** from existing projects
- **Reuse configurations** across multiple projects
- **Custom metadata** with variable substitution

## 🔧 CLI Commands

WOMM provides a comprehensive CLI interface:

```bash
# Project Management
womm new python <name>              # Create new Python project
womm new javascript <name>          # Create new JavaScript project
womm setup python                   # Setup existing Python project

# Code Quality
womm lint [path]                    # Run linting tools
womm spell [path]                   # Check spelling in code and docs

# Template Management
womm templates list                 # List available templates
womm templates create <name>        # Create template from project
womm templates use <name> <output>  # Use template for new project

# System Management
womm system info                    # Show system information
womm system detect                  # Detect installed tools

# Installation (Windows)
womm install                        # Install WOMM to system PATH
womm install --context-menu         # Add Windows context menu integration
womm uninstall                      # Remove WOMM from system
```

See the [CLI Reference](cli/index.md) for complete documentation.

## 📦 Core Dependencies

- **Python >= 3.10** – Modern Python with type hints support
- **Rich >= 13.0** – Terminal output and formatting
- **InquirerPy >= 0.3** – Interactive prompts
- **Click >= 8.0** – CLI framework

## 🎨 Architecture Layers

| Layer                                 | Components                               | Description                           |
| ------------------------------------- | ---------------------------------------- | ------------------------------------- |
| [Commands](cli/index.md)              | CLI, Interactive, Context Menu           | User-facing interfaces                |
| [Business Logic](api/architecture.md) | Managers (Project, Template, Dependency) | Core business logic and orchestration |
| [Execution](api/architecture.md)      | Installation, Environment, Security      | System operations and validation      |
| [Infrastructure](api/architecture.md) | UI, File Operations, System Detection    | Low-level utilities and helpers       |

## 📝 License

MIT License – See [LICENSE](https://github.com/neuraaak/works-on-my-machine/blob/main/LICENSE) file for details.

## 🔗 Links

- **Repository**: [https://github.com/neuraaak/works-on-my-machine](https://github.com/neuraaak/works-on-my-machine)
- **PyPI**: [https://pypi.org/project/works-on-my-machine/](https://pypi.org/project/works-on-my-machine/)
- **Issues**: [https://github.com/neuraaak/works-on-my-machine/issues](https://github.com/neuraaak/works-on-my-machine/issues)
- **Documentation**: [https://neuraaak.github.io/works-on-my-machine/](https://neuraaak.github.io/works-on-my-machine/)

---

**WOMM** – Universal development environment manager. 🚀
