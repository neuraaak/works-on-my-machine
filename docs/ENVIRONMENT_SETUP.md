# ⚙️ Environment Setup Guide

[🏠 Main](../README.md) > [📚 Documentation](README.md) > [⚙️ Environment Setup](ENVIRONMENT_SETUP.md)

[← Back to Main Documentation](../README.md)

> **Automatic development environment management**  
> Complete setup for Python and JavaScript projects with intelligent detection

## 📚 Documentation Navigation

**🏠 [Main Documentation](../README.md)**  
**📚 [Documentation Index](README.md)**  
**⚙️ [Environment Setup](ENVIRONMENT_SETUP.md)** (You are here)  
**🔧 [Common Commands](COMMON_COMMANDS.md)**  
**📋 [Documentation Rules](DOCUMENTATION_RULES.md)**  
**🔧 [Prerequisites Installation](PREREQUISITE_INSTALLER.md)**

## Table of Contents
- [Overview](#overview)
- [Automatic Integration](#automatic-integration)
- [Dedicated Commands](#dedicated-commands)
- [Python Environment](#python-environment)
- [JavaScript Environment](#javascript-environment)
- [Smart Detection](#smart-detection)
- [Security and Exclusions](#security-and-exclusions)
- [Error Handling](#error-handling)
- [Benefits](#benefits)
- [Related Documentation](#related-documentation)

## Related Documentation
- **🔧 [Common Commands](COMMON_COMMANDS.md)** - Standard commands and workflows
- **🔧 [Prerequisites Installation](PREREQUISITE_INSTALLER.md)** - Required tools installation
- **📋 [Main README](../README.md)** - Project overview and installation

## 🎯 Overview

The Environment Setup system provides **automatic development environment management** for both Python and JavaScript projects. It intelligently detects project types and configures the appropriate tools and dependencies.

### ✅ **Python - Complete Virtual Environment**
- **Virtual environment** creation and activation
- **Development tools** installation (Black, isort, flake8, pytest)
- **Pre-commit hooks** configuration
- **VSCode settings** and extensions

### ✅ **JavaScript - Complete npm Dependencies**
- **Package.json** generation with modern tools
- **Development dependencies** (ESLint, Prettier, Jest, Husky)
- **TypeScript support** when applicable
- **VSCode configuration** for JavaScript/TypeScript

### 🤔 **Smart Interactive Mode**
- **Automatic detection** of project type
- **User confirmation** before installation
- **Customizable options** for advanced users
- **Rollback capability** if needed

## 🔄 Automatic Integration

### When creating a project
- **Automatic prompt** to install environment
- **Creates venv** + installs all tools
- **Configures pre-commit** hooks
- **Sets up VSCode** settings

### When configuring existing projects
- **Automatic prompt** to install environment
- **npm install** + configures all tools
- **TypeScript setup** if applicable
- **Husky hooks** configuration

## 🛠️ Dedicated Commands

### Manual configuration of existing project
```bash
# Python project
womm env setup python

# JavaScript project
womm env setup javascript

# Auto-detect
womm env setup auto
```

### Test from any project
```bash
# Check environment status
womm env status

# Validate setup
womm env validate
```

## 🐍 Python Environment

### Automatically Installed Tools
- **black** - Code formatting
- **isort** - Import organization
- **ruff** - Linting and quality
- **pytest** - Testing framework
- **pre-commit** - Git hooks
- **bandit** - Security analysis

### Optional Tools (Bonus)
- **mypy** - Type checking
- **coverage** - Code coverage
- **tox** - Multi-environment testing

### Created Structure
```
project/
├── .venv/                    # Virtual environment
├── .pre-commit-config.yaml   # Git hooks
├── pyproject.toml           # Project configuration
├── .vscode/                 # VSCode settings
│   ├── settings.json
│   └── extensions.json
└── Makefile                 # Development commands
```

### Python Workflow
1. **Create the project**
   - → "Install development tools? (Y/n): [Enter]"
   - → ✅ venv created + tools installed

2. **Activate environment**
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Develop**
   ```bash
   make format    # Format code
   make lint      # Check quality
   make test      # Run tests
   ```

## 🟨 JavaScript Environment

### Automatically Installed Tools
- **ESLint** - Code linting
- **Prettier** - Code formatting
- **Jest** - Testing framework
- **Husky** - Git hooks
- **lint-staged** - Pre-commit linting

### Automatic TypeScript Support
- **TypeScript** configuration
- **@types** packages
- **tsconfig.json** setup
- **ESLint TypeScript** rules

### Created Structure
```
project/
├── package.json             # Dependencies and scripts
├── .eslintrc.json          # Linting rules
├── prettier.config.js      # Formatting rules
├── jest.config.js          # Testing configuration
├── .husky/                 # Git hooks
│   └── pre-commit
├── .vscode/                # VSCode settings
│   ├── settings.json
│   └── extensions.json
└── tsconfig.json           # TypeScript config (if applicable)
```

### JavaScript Workflow
1. **Create the project**
   - → "Install development tools? (Y/n): [Enter]"
   - → ✅ npm install + tools configured

2. **Develop**
   ```bash
   npm run dev          # Development server
   npm run lint         # Check code quality
   npm test             # Run tests
   ```

## 🔍 Smart Detection

### Project Type Detection
- **Python**: `pyproject.toml`, `requirements.txt`, `setup.py`
- **JavaScript**: `package.json`, `node_modules/`
- **Mixed**: Both Python and JavaScript files
- **Unknown**: Prompt user for choice

### Generated Activation Scripts
- **Python - activate.bat (Windows)**
- **JavaScript - dev.bat (Windows)**
- **Cross-platform shell scripts**

### Automatic Pre-commit Configuration
- **Python**: Black, isort, ruff, pytest
- **JavaScript**: ESLint, Prettier, Jest
- **Mixed**: Combined configuration

## 🔒 Security and Automatic Exclusions

### Sensitive Files Protection
- **Environment variables** (`.env*`)
- **Secrets and keys** (`*.key`, `*.pem`)
- **Database files** (`*.db`, `*.sqlite`)
- **Log files** (`*.log`)

### Automatically Excluded Files
- **Build artifacts** (`dist/`, `build/`, `*.pyc`)
- **Dependencies** (`node_modules/`, `.venv/`)
- **IDE files** (`.vscode/`, `.idea/`)
- **OS files** (`.DS_Store`, `Thumbs.db`)

### Applied Exclusions
```gitignore
# Python
__pycache__/
*.pyc
.venv/
dist/
build/

# JavaScript
node_modules/
dist/
build/
.env*

# IDE
.vscode/
.idea/
*.swp
```

### Exclusions Example
```bash
# These files are automatically excluded
.env.local          # Environment variables
secrets.json        # Sensitive data
*.log              # Log files
node_modules/      # Dependencies
```

### Why It's Important
- **Security**: Prevents accidental commit of secrets
- **Performance**: Excludes large dependency directories
- **Cleanliness**: Keeps repository focused on source code
- **Compliance**: Meets security best practices

## 🚨 Error Handling

### Common Issues
- **Permission errors**: Automatic retry with elevated privileges
- **Network issues**: Graceful fallback with offline mode
- **Tool conflicts**: Automatic resolution and user notification
- **Insufficient space**: Clear error messages with cleanup suggestions

### Recovery Options
- **Rollback**: Automatic cleanup if installation fails
- **Manual mode**: Step-by-step installation guide
- **Diagnostic mode**: Detailed error reporting
- **Skip options**: Continue without problematic tools

## 💡 Benefits

### For Developers
- **Zero configuration** - Works out of the box
- **Consistent environments** - Same setup across team
- **Time saving** - No manual tool installation
- **Best practices** - Industry-standard configurations

### For Teams
- **Onboarding speed** - New developers ready in minutes
- **Standardization** - Consistent development experience
- **Quality assurance** - Built-in linting and testing
- **Security** - Automatic exclusion of sensitive files

### For Projects
- **Professional setup** - Industry-standard tools
- **Maintainability** - Clear structure and configuration
- **Scalability** - Easy to extend and customize
- **Documentation** - Self-documenting configuration

## 📈 New Features & Improvements

### 🔐 Enhanced Security (Recent)
- **Automatic secret detection**
- **Sensitive file exclusion**
- **Environment variable protection**
- **Security scanning integration**

### 🔍 Improved Project Detection
- **Multi-language project support**
- **Framework-specific configurations**
- **Legacy project compatibility**
- **Custom project type definitions**

---

**⚙️ This environment setup system ensures every project starts with professional-grade development tools and configurations.**