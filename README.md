# 🛠️ Works On My Machine - Multi-Language Development Environment

> **Universal development tools for Python and JavaScript**  
> Automatic installation, cross-platform configuration, global commands

## 🚀 Quick Installation

```bash
# 1. Download/extract works-on-my-machine anywhere
# 2. Run initialization
python init.py        # or double-click init.bat (Windows)

# 3. Restart terminal
# 4. Use anywhere!
new-project my-app     # Project creation with auto-detection
lint-project          # Automatic linting based on project type
```

## 📁 Project Structure

```
works-on-my-machine/
├── 📋 README.md                     # This file
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
- `new-project` - Universal assistant (automatic detection)
- `new-python-project name` - Python project with complete environment
- `new-js-project name` - JavaScript/Node.js project with tooling

### 🔍 Linting and Quality
- `lint-project` - Automatic linting based on project type
- `spellcheck` - Spell checking with CSpell

### 🛠️ Utilities
- `vscode-config` - VSCode configuration setup
- `dev-tools-install` - Install development prerequisites
- `setup-dev-env` - Setup development environment

## 🔧 Architecture & CLI Management

### Standardized CLI System
Works On My Machine uses a centralized CLI system via `shared/cli_manager.py` that:

- **Standardizes execution** of all system commands
- **Handles errors** consistently
- **Automatically logs** commands and their results
- **Supports different modes**: silent, interactive, verbose
- **Cross-platform**: automatic adaptation for Windows/Linux/macOS

### CLI Features
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
- **Auto-relocation** to `%USER%/.dev-tools`
- **Automatic project detection**
- **Adaptive configuration** based on OS

### ✅ **Professional**
- **Automatic pre-commit hooks**
- **Shared VSCode** configuration
- **Industry standards** (Black, ESLint, etc.)

## 🔧 Technical Architecture

### Installation
1. **Smart Init** detects location and relocates if necessary
2. **PATH Setup** permanently adds `{USER_HOME}/.dev-tools/bin`
3. **Wrapper Scripts** create global commands

### Usage
1. **Automatic detection** of project type (Python/JS)
2. **Selection** of appropriate tools
3. **Adapted configuration** and templates

## 📋 Version History

- **v2.0** - Multi-language restructuring (Python + JavaScript)
- **v1.x** - Original Python-specific version

---

**Ready to code efficiently? Run `python init.py` and let's go! 🚀**