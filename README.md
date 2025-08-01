# 🛠️ Works On My Machine - Multi-Language Development Environment

> **Universal development tools for Python and JavaScript**  
> Automatic installation, cross-platform configuration, global commands

## 🚀 Quick Installation

```bash
# 1. Download/extract works-on-my-machine anywhere
# 2. Run initialization
womm init        # or python init.py

# 3. Restart terminal
# 4. Use anywhere!
womm new python my-app     # Create Python project
womm new javascript my-app # Create JavaScript project
womm lint python          # Lint Python code
```

## 📁 Project Structure

```
works-on-my-machine/
├── 📋 README.md                     # This file
├── 🔧 womm.py                       # Main CLI entry point (Click)
├── 🔧 init.py, init.bat, init.ps1   # Initialization scripts
├── 📦 bin/                          # Global commands (added to PATH)
├── 🐍 languages/python/             # Python tools (→ see PYTHON.md)
├── 🟨 languages/javascript/         # JavaScript tools (→ see JAVASCRIPT.md)
├── 🔄 shared/                       # Shared utilities
├── 📄 ENVIRONMENT_SETUP.md          # Environment setup guide
└── 📄 PREREQUISITE_INSTALLER.md     # Prerequisites installation
```

## 🎯 Available Commands

After initialization, usable from any directory:

### 🆕 Project Creation
- `womm new python name` - Python project with complete environment
- `womm new javascript name` - JavaScript/Node.js project with tooling
- `womm new detect name` - Auto-detect project type and setup

### 🔍 Linting and Quality
- `womm lint python` - Lint Python code with flake8, black, isort
- `womm lint all` - Lint all supported code in project

### 📝 Spell Checking
- `womm spell install` - Install CSpell globally
- `womm spell setup project` - Setup CSpell for project
- `womm spell check` - Check spelling in files

### 🔧 System Management
- `womm system detect` - Detect system information and tools
- `womm system install python node git npm` - Install prerequisites

### 📦 Deployment
- `womm deploy tools` - Deploy tools to global directory

### 🖱️ Windows Context Menu
- `womm context register` - Register WOMM tools in context menu
- `womm context unregister` - Remove WOMM tools from context menu
- `womm context list` - List registered context menu entries

## 🔧 Architecture & CLI Management

### Modern Click CLI System
Works On My Machine uses a modern Click-based CLI system that provides:

- **Beautiful command interface** with automatic help generation
- **Command grouping** for organized functionality
- **Automatic argument parsing** and validation
- **Cross-platform compatibility** with consistent behavior
- **Integration** with system command execution via `shared/cli_manager.py`

### CLI Features
```bash
# Main help
womm --help

# Group help
womm new --help
womm system --help

# Command help
womm new python --help
womm system install --help
```

### System Command Integration
```python
from shared.cli_manager import run_command, run_silent, check_tool_available

# Execution with logging
result = run_command(["npm", "install"], "Installing dependencies")

# Silent execution
result = run_silent(["python", "--version"])

# Tool availability check
if check_tool_available("git"):
    print("Git available")
```

## 📚 Language-Specific Documentation

### 🐍 **Python** → [languages/python/PYTHON.md](languages/python/PYTHON.md)
- Complete configuration (Black, isort, flake8, pytest)
- PyProject.toml, pre-commit, VSCode templates
- Development scripts and Makefile

### 🟨 **JavaScript** → [languages/javascript/JAVASCRIPT.md](languages/javascript/JAVASCRIPT.md)
- Modern tools (ESLint, Prettier, TypeScript)
- package.json, tsconfig.json templates
- Support for Node.js, React, Vue, etc.

## 📖 Complete Documentation Index

### 🚀 **Getting Started**
- **📋 [README.md](README.md)** - Main documentation (this file)
- **⚙️ [Environment Setup](ENVIRONMENT_SETUP.md)** - Development environment management
- **🔧 [Prerequisites Installation](PREREQUISITE_INSTALLER.md)** - Required tools installation

### 🌐 **Language-Specific Guides**
- **🐍 [Python Development](languages/python/PYTHON.md)** - Python tools and configuration
- **🟨 [JavaScript Development](languages/javascript/JAVASCRIPT.md)** - JavaScript/Node.js tools

### 📚 **Quick Navigation**

| Topic | Description | File |
|-------|-------------|------|
| **Project Setup** | How to use Works On My Machine | [README.md](README.md) |
| **Environment Manager** | Automatic dev environment setup | [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) |
| **Prerequisites** | Install Python, Node.js, Git automatically | [PREREQUISITE_INSTALLER.md](PREREQUISITE_INSTALLER.md) |
| **Python Tools** | Black, flake8, pytest, pre-commit setup | [languages/python/PYTHON.md](languages/python/PYTHON.md) |
| **JavaScript Tools** | ESLint, Prettier, Jest, Husky setup | [languages/javascript/JAVASCRIPT.md](languages/javascript/JAVASCRIPT.md) |

### 🎯 **By Use Case**

**Setting up a new Python project:**
1. 📋 [Installation](README.md#-quick-installation) 
2. 🐍 [Python Guide](languages/python/PYTHON.md)
3. ⚙️ [Environment Setup](ENVIRONMENT_SETUP.md)

**Setting up a new JavaScript project:**
1. 📋 [Installation](README.md#-quick-installation)
2. 🟨 [JavaScript Guide](languages/javascript/JAVASCRIPT.md) 
3. ⚙️ [Environment Setup](ENVIRONMENT_SETUP.md)

**Installing prerequisites:**
1. 🔧 [Prerequisites Guide](PREREQUISITE_INSTALLER.md)
2. 📋 [Main Installation](README.md#-quick-installation)

## ⚙️ Features

### ✅ **Cross-Platform**
- **Windows**: Batch + PowerShell + Python
- **Linux/Mac**: Bash + Python
- Automatic PATH configuration

### ✅ **Intelligent**
- **Auto-relocation** to `%USER%/.womm`
- **Automatic project detection**
- **Adaptive configuration** based on OS

### ✅ **Professional**
- **Automatic pre-commit hooks**
- **Shared VSCode** configuration
- **Industry standards** (Black, ESLint, etc.)

## 🔧 Technical Architecture

### Installation
1. **Smart Init** detects location and relocates if necessary
2. **PATH Setup** permanently adds `{USER_HOME}/.womm/bin`
3. **Click CLI** provides modern command interface

### Usage
1. **Automatic detection** of project type (Python/JS)
2. **Selection** of appropriate tools
3. **Adapted configuration** and templates

## 📋 Version History

- **v1.0** - Modern Click CLI with full feature set
- **v0.9** - Multi-language restructuring (Python + JavaScript)
- **v0.8** - Initial release with Python support

---

**This system makes dev-tools entirely self-sufficient! 🎉**