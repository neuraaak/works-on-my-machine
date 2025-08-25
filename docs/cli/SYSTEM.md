# 🖥️ System Guide

[🏠 Main](../../README.md) > [📚 Documentation](../README.md) > [🔧 CLI Documentation](README.md) > [🖥️ System](SYSTEM.md)

[← Back to CLI Documentation](README.md)

> **Complete guide to system detection and validation with WOMM**  
> Check system compatibility, detect tools, and validate environment

## 📚 Documentation Navigation

**🏠 [Main Documentation](../../README.md)**  
**📚 [Documentation Index](../README.md)**  
**🔧 [CLI Documentation](README.md)**  
**🖥️ [System](SYSTEM.md)** (You are here)  
**🔌 [API Documentation](../api/README.md)**

## 📋 Table of Contents
- [🎯 Overview](#-overview)
- [🚀 Quick Start](#-quick-start)
- [🔍 System Detection](#-system-detection)
- [🐍 Python Environment](#-python-environment)
- [🟨 JavaScript Environment](#-javascript-environment)
- [🔧 Development Tools](#-development-tools)
- [📊 System Report](#-system-report)
- [🔍 Troubleshooting](#-troubleshooting)

## 🎯 Overview

WOMM's system commands help you check system compatibility, detect installed tools, and validate your development environment. This ensures all required dependencies are available.

### ✅ **Detection Features**
- **System Information** - OS, architecture, versions
- **Python Environment** - Python version, packages, virtual environments
- **JavaScript Environment** - Node.js, npm, yarn, pnpm
- **Development Tools** - Git, editors, build tools

### 🔄 **Detection Workflow**
```
System Scan → Tool Detection → Version Validation → Compatibility Check → Report Generation
```

## 🚀 Quick Start

### **Basic System Check**
```bash
# Check system compatibility
womm system

# Check with detailed output
womm system --verbose

# Generate system report
womm system --report
```

### **Environment Detection**
```bash
# Check Python environment
womm system python

# Check JavaScript environment
womm system javascript

# Check development tools
womm system tools
```

### **Compatibility Check**
```bash
# Check WOMM compatibility
womm system --compatibility

# Check project requirements
womm system --requirements

# Validate environment
womm system --validate
```

## 🔍 System Detection

### **Command Syntax**
```bash
womm system [OPTIONS]
```

### **Options**
- `--verbose` - Detailed output
- `--report` - Generate system report
- `--compatibility` - Check compatibility
- `--requirements` - Check project requirements
- `--validate` - Validate environment

### **System Information**
WOMM detects and reports:
- **Operating System** - Windows, macOS, Linux
- **Architecture** - x86_64, ARM64, etc.
- **System Resources** - CPU, memory, disk space
- **Network** - Internet connectivity, proxy settings

### **Examples**
```bash
# Basic system check
womm system

# Detailed system information
womm system --verbose

# Generate HTML report
womm system --report --format html

# Check specific components
womm system --components python,nodejs,git
```

### **System Output**
```
🖥️ System Information
├── OS: Windows 10 (10.0.19044)
├── Architecture: x86_64
├── Python: 3.9.7 (✓ Compatible)
├── Node.js: 16.14.0 (✓ Compatible)
├── Git: 2.35.1 (✓ Available)
└── Disk Space: 127.5 GB available

✅ System compatibility: PASSED
⚠️ Recommendations: Update Python to 3.10+
```

## 🐍 Python Environment

### **Python Detection**
```bash
# Check Python installation
womm system python

# Check Python version
womm system python --version

# Check Python packages
womm system python --packages

# Check virtual environments
womm system python --venv
```

### **Python Requirements**
- **Minimum Version**: Python 3.8
- **Recommended Version**: Python 3.10+
- **Required Packages**: pip, setuptools, wheel

### **Python Environment Check**
```bash
# Check Python environment
womm system python --environment

# Validate Python setup
womm system python --validate

# Check Python tools
womm system python --tools
```

### **Python Output**
```
🐍 Python Environment
├── Version: 3.9.7 (✓ Compatible)
├── Location: /usr/bin/python3
├── pip: 21.3.1 (✓ Available)
├── Virtual Environment: None (⚠️ Recommended)
├── Packages: 45 installed
└── Tools: black, flake8, pytest (✓ Available)

✅ Python environment: READY
⚠️ Recommendation: Create virtual environment
```

## 🟨 JavaScript Environment

### **JavaScript Detection**
```bash
# Check Node.js installation
womm system javascript

# Check Node.js version
womm system javascript --version

# Check package managers
womm system javascript --managers

# Check global packages
womm system javascript --packages
```

### **JavaScript Requirements**
- **Minimum Version**: Node.js 14.0
- **Recommended Version**: Node.js 16.0+
- **Package Managers**: npm, yarn, or pnpm

### **JavaScript Environment Check**
```bash
# Check JavaScript environment
womm system javascript --environment

# Validate JavaScript setup
womm system javascript --validate

# Check JavaScript tools
womm system javascript --tools
```

### **JavaScript Output**
```
🟨 JavaScript Environment
├── Node.js: 16.14.0 (✓ Compatible)
├── npm: 8.3.1 (✓ Available)
├── yarn: 1.22.17 (✓ Available)
├── pnpm: Not installed (ℹ️ Optional)
├── Global Packages: 12 installed
└── Tools: eslint, prettier (✓ Available)

✅ JavaScript environment: READY
ℹ️ Recommendation: Consider pnpm for faster installs
```

## 🔧 Development Tools

### **Tool Detection**
```bash
# Check development tools
womm system tools

# Check specific tools
womm system tools --git --editor --build

# Check tool versions
womm system tools --versions

# Validate tool setup
womm system tools --validate
```

### **Supported Tools**
- **Version Control**: Git, SVN
- **Editors**: VS Code, Vim, Emacs, Sublime Text
- **Build Tools**: Make, CMake, Gradle, Maven
- **Container Tools**: Docker, Podman

### **Tool Requirements**
- **Git**: Required for version control
- **Editor**: Recommended for development
- **Build Tools**: Project-specific requirements

### **Tools Output**
```
🔧 Development Tools
├── Git: 2.35.1 (✓ Available)
├── VS Code: 1.70.0 (✓ Available)
├── Docker: 20.10.17 (✓ Available)
├── Make: 4.3 (✓ Available)
└── Build Tools: cmake, gradle (✓ Available)

✅ Development tools: READY
ℹ️ Recommendation: Configure Git user info
```

## 📊 System Report

### **Report Generation**
```bash
# Generate system report
womm system --report

# Export report to file
womm system --report --output system-report.json

# Generate HTML report
womm system --report --format html

# Generate markdown report
womm system --report --format markdown
```

### **Report Content**
```json
{
  "system": {
    "os": "Windows 10",
    "architecture": "x86_64",
    "python": {
      "version": "3.9.7",
      "compatible": true,
      "packages": 45
    },
    "javascript": {
      "nodejs": "16.14.0",
      "npm": "8.3.1",
      "compatible": true
    },
    "tools": {
      "git": "2.35.1",
      "editor": "VS Code 1.70.0"
    },
    "compatibility": "PASSED",
    "recommendations": [
      "Update Python to 3.10+",
      "Create virtual environment"
    ]
  }
}
```

### **Report Formats**
- **JSON** - Machine-readable format
- **HTML** - Web-friendly report
- **Markdown** - Documentation format
- **Text** - Console output format

## 🔍 Troubleshooting

### **Common Issues**

**Python not found:**
```bash
# Check Python installation
python --version
python3 --version

# Install Python
# Windows: Download from python.org
# macOS: brew install python
# Linux: sudo apt install python3

# Add Python to PATH
export PATH="/usr/local/bin:$PATH"
```

**Node.js not found:**
```bash
# Check Node.js installation
node --version
npm --version

# Install Node.js
# Windows: Download from nodejs.org
# macOS: brew install node
# Linux: curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -

# Add Node.js to PATH
export PATH="/usr/local/bin:$PATH"
```

**Git not found:**
```bash
# Check Git installation
git --version

# Install Git
# Windows: Download from git-scm.com
# macOS: brew install git
# Linux: sudo apt install git

# Configure Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### **Environment Issues**

**Virtual environment problems:**
```bash
# Create virtual environment
python -m venv myenv

# Activate virtual environment
# Windows
myenv\Scripts\activate
# macOS/Linux
source myenv/bin/activate

# Install packages
pip install -r requirements.txt
```

**Package manager issues:**
```bash
# Update package managers
pip install --upgrade pip
npm install -g npm@latest

# Clear cache
pip cache purge
npm cache clean --force

# Reinstall packages
pip install --force-reinstall package-name
npm install package-name
```

### **System Compatibility**

**Unsupported OS:**
```bash
# Check OS compatibility
womm system --compatibility

# Update operating system
# Windows: Windows Update
# macOS: Software Update
# Linux: sudo apt update && sudo apt upgrade

# Use virtual machine or container
docker run -it ubuntu:20.04
```

**Insufficient resources:**
```bash
# Check system resources
womm system --resources

# Free up disk space
# Remove unnecessary files
# Clear package caches
# Uninstall unused applications

# Increase virtual memory
# Windows: System Properties > Advanced > Performance
# Linux: sudo sysctl vm.swappiness=10
```

### **Debug Mode**
Enable verbose output for troubleshooting:

```bash
# Set debug environment variable
export WOMM_DEBUG=1

# Run system check with debug output
womm system --verbose --debug

# Check logs
cat ~/.womm/logs/system.log
```

### **Log Files**
WOMM creates detailed logs for troubleshooting:

```bash
# View system logs
cat ~/.womm/logs/system.log

# View detection logs
cat ~/.womm/logs/detection.log

# View compatibility logs
cat ~/.womm/logs/compatibility.log
```

---

**🖥️ This system guide provides comprehensive instructions for checking system compatibility and validating development environments with WOMM.**
