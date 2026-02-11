# Project Setup Guide

> **Complete guide to configuring existing projects with WOMM**
> Set up development tools, dependencies, and best practices for existing projects

## 🎯 Overview

WOMM's setup commands help you configure existing projects with modern development tools, dependencies, and best practices. The system automatically detects project types and provides appropriate configurations.

### ✅ **Supported Project Types**

- **🐍 Python** - Virtual environments, dependencies, testing
- **🟨 JavaScript** - Node.js setup, package management
- **⚛️ React** - Development server, build tools
- **💚 Vue** - Development server, build tools

### 🔄 **Setup Workflow**

```text
Project Detection → Type Identification → Tool Configuration → Dependency Installation → Development Setup
```

## 🚀 Quick Start

### **Auto-Detection Setup**

```bash
# Auto-detect and setup project
womm setup

# Auto-detect with interactive mode
womm setup --interactive
```

### **Specific Project Setup**

```bash
# Setup Python project
womm setup python

# Setup JavaScript project
womm setup javascript

# Setup React project
womm setup react

# Setup Vue project
womm setup vue
```

### **Custom Path Setup**

```bash
# Setup project in specific directory
womm setup --path ./my-project/

# Setup with custom configuration
womm setup python --path ./backend/ --virtual-env
```

## 🔍 Project Detection

### **Command Syntax**

```bash
womm setup detect [OPTIONS]
```

### **Options**

- `--path <PATH>` - Path to project directory (default: current)
- `--interactive` - Run in interactive mode

### **Detection Process**

WOMM automatically detects project types based on file signatures:

- **Python**: `pyproject.toml`, `requirements.txt`, `setup.py`
- **JavaScript**: `package.json`
- **React**: `package.json` with React dependencies
- **Vue**: `package.json` with Vue dependencies

### **Examples**

```bash
# Detect current directory
womm setup detect

# Detect specific project
womm setup detect --path ./my-project/

# Interactive detection
womm setup detect --interactive
```

### **Detection Output**

```text
🔍 Detected project type: python (confidence: 95%)
✅ Project setup completed successfully
📦 Installed 15 dependencies
🔧 Configured development tools
```

## 🐍 Python Setup

### **Command Syntax - Python**

```bash
womm setup python [OPTIONS]
```

### **Options - Python**

- `--path <PATH>` - Python project directory
- `--interactive` - Interactive mode
- `--virtual-env` - Create virtual environment
- `--install-deps` - Install dependencies
- `--dev-tools` - Install development tools

### **Python Setup Features**

- **Virtual Environment** - Isolated Python environment
- **Dependency Management** - pip/poetry integration
- **Testing Framework** - pytest configuration
- **Code Quality** - linting and formatting tools
- **Type Checking** - mypy integration

### **Examples - Python**

```bash
# Basic Python setup
womm setup python

# Python setup with virtual environment
womm setup python --virtual-env

# Python setup with all tools
womm setup python --virtual-env --install-deps --dev-tools

# Interactive Python setup
womm setup python --interactive
```

### **Python Setup Process**

1. **Environment Detection** - Check Python version and tools
2. **Virtual Environment** - Create isolated environment
3. **Dependency Installation** - Install project dependencies
4. **Development Tools** - Configure linting, testing, formatting
5. **Project Configuration** - Update project files

## 🟨 JavaScript Setup

### **Command Syntax - JavaScript**

```bash
womm setup javascript [OPTIONS]
```

### **Options - JavaScript**

- `--path <PATH>` - JavaScript project directory
- `--interactive` - Interactive mode
- `--install-deps` - Install dependencies
- `--dev-tools` - Install development tools
- `--package-manager <MANAGER>` - npm, yarn, or pnpm

### **JavaScript Setup Features**

- **Package Management** - npm/yarn/pnpm integration
- **Development Server** - Hot reload setup
- **Testing Framework** - Jest/Vitest configuration
- **Code Quality** - ESLint and Prettier
- **Build Tools** - Webpack/Vite configuration

### **Examples - JavaScript**

```bash
# Basic JavaScript setup
womm setup javascript

# JavaScript setup with specific package manager
womm setup javascript --package-manager yarn

# JavaScript setup with all tools
womm setup javascript --install-deps --dev-tools

# Interactive JavaScript setup
womm setup javascript --interactive
```

### **JavaScript Setup Process**

1. **Package Manager Detection** - Identify npm/yarn/pnpm
2. **Dependency Installation** - Install project dependencies
3. **Development Tools** - Configure linting and formatting
4. **Testing Setup** - Configure test framework
5. **Build Configuration** - Set up build tools

## ⚛️ React Setup

### **Command Syntax - React**

```bash
womm setup react [OPTIONS]
```

### **Options - React**

- `--path <PATH>` - React project directory
- `--interactive` - Interactive mode
- `--install-deps` - Install dependencies
- `--dev-tools` - Install development tools
- `--build-tool <TOOL>` - Vite, Create React App, or custom

### **React Setup Features**

- **Development Server** - Hot reload with Vite
- **Build Optimization** - Production build setup
- **Testing Framework** - React Testing Library
- **Code Quality** - ESLint and Prettier for React
- **TypeScript Support** - TypeScript configuration

### **Examples - React**

```bash
# Basic React setup
womm setup react

# React setup with TypeScript
womm setup react --typescript

# React setup with custom build tool
womm setup react --build-tool vite

# Interactive React setup
womm setup react --interactive
```

## 💚 Vue Setup

### **Command Syntax - Vue**

```bash
womm setup vue [OPTIONS]
```

### **Options - Vue**

- `--path <PATH>` - Vue project directory
- `--interactive` - Interactive mode
- `--install-deps` - Install dependencies
- `--dev-tools` - Install development tools
- `--vue-version <VERSION>` - Vue 2 or Vue 3

### **Vue Setup Features**

- **Development Server** - Hot reload with Vite
- **Build Optimization** - Production build setup
- **Testing Framework** - Vue Test Utils
- **Code Quality** - ESLint and Prettier for Vue
- **TypeScript Support** - TypeScript configuration

### **Examples - Vue**

```bash
# Basic Vue setup
womm setup vue

# Vue setup with TypeScript
womm setup vue --typescript

# Vue setup with specific version
womm setup vue --vue-version 3

# Interactive Vue setup
womm setup vue --interactive
```

## 🎨 Interactive Mode

### **Interactive Setup Process**

When using `--interactive`, WOMM guides you through:

1. **Project Detection** - Auto-detect or manual selection
2. **Setup Options** - Choose which tools to install
3. **Configuration** - Customize settings
4. **Dependencies** - Select additional packages
5. **Development Tools** - Choose linting and testing tools

### **Example Interactive Flow**

```text
🔍 Detected project type: python (confidence: 95%)
⚙️ Setup options:
  ☑ Create virtual environment
  ☑ Install dependencies
  ☑ Configure development tools
  ☐ Install additional packages

🔧 Development tools:
  ☑ pytest (testing)
  ☑ black (formatting)
  ☑ flake8 (linting)
  ☑ mypy (type checking)
```

## 🔧 Development Tools

### **Code Quality Tools**

- **Linters** - Find and fix code issues
- **Formatters** - Consistent code formatting
- **Type Checkers** - Static type analysis
- **Security Scanners** - Vulnerability detection

### **Testing Tools**

- **Unit Testing** - pytest, Jest, Vitest
- **Integration Testing** - Test frameworks
- **Coverage Reports** - Code coverage analysis
- **Test Runners** - Automated test execution

### **Build Tools**

- **Bundlers** - Webpack, Vite, Rollup
- **Compilers** - TypeScript, Babel
- **Optimizers** - Production builds
- **Asset Management** - Static file handling

## 📦 Dependency Management

### **Python Dependencies**

- **Package Managers** - pip, poetry, pipenv
- **Virtual Environments** - venv, virtualenv
- **Dependency Files** - requirements.txt, pyproject.toml
- **Development Dependencies** - Separate dev requirements

### **JavaScript Dependencies**

- **Package Managers** - npm, yarn, pnpm
- **Lock Files** - package-lock.json, yarn.lock
- **Scripts** - npm scripts for automation
- **Workspaces** - Monorepo support

### **Dependency Installation**

```bash
# Python dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# JavaScript dependencies
npm install
npm install --save-dev
```

## 💡 Best Practices

### **Project Structure**

- **Clear Organization** - Logical file and folder structure
- **Separation of Concerns** - Source, tests, docs separation
- **Configuration Files** - Centralized project configuration
- **Documentation** - README and inline documentation

### **Development Workflow**

- **Version Control** - Git setup and configuration
- **Code Quality** - Automated linting and formatting
- **Testing Strategy** - Unit, integration, and e2e tests
- **CI/CD Integration** - Automated testing and deployment

### **Environment Management**

- **Isolation** - Virtual environments and containers
- **Configuration** - Environment-specific settings
- **Security** - Secure dependency management
- **Reproducibility** - Lock files and version pinning

## 🔍 Troubleshooting

### **Common Issues**

**Detection failures:**

```bash
# Check project structure
ls -la

# Verify configuration files
cat package.json
cat pyproject.toml

# Manual project type specification
womm setup python --path ./my-project/
```

**Dependency installation errors:**

```bash
# Check network connectivity
ping npmjs.org

# Clear package manager cache
npm cache clean --force
pip cache purge

# Update package managers
npm install -g npm@latest
pip install --upgrade pip
```

**Permission errors:**

```bash
# Check directory permissions
ls -la /project/directory

# Fix permissions
chmod 755 /project/directory

# Use user installation
pip install --user package-name
```

### **Debug Mode**

Enable verbose output for troubleshooting:

```bash
# Set debug environment variable
export WOMM_DEBUG=1

# Run setup with debug output
womm setup python --path ./my-project/
```

### **Log Files**

WOMM creates detailed logs for troubleshooting:

```bash
# View setup logs
cat ~/.womm/logs/setup.log

# View error logs
cat ~/.womm/logs/errors.log
```

---

**⚙️ This project setup guide provides comprehensive instructions for configuring existing projects with modern development tools and best practices.**
