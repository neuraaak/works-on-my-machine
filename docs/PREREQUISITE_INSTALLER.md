# 🔧 Prerequisites Installation Guide

[🏠 Main](../README.md) > [📚 Documentation](README.md) > [🔧 Prerequisites Installation](PREREQUISITE_INSTALLER.md)

[← Back to Main Documentation](../README.md)

> **Automatic installation of required development tools**  
> Python, Node.js, Git, and other essential tools for development

## 📚 Documentation Navigation

**🏠 [Main Documentation](../README.md)**  
**📚 [Documentation Index](README.md)**  
**🔧 [Prerequisites Installation](PREREQUISITE_INSTALLER.md)** (You are here)  
**⚙️ [Environment Setup](ENVIRONMENT_SETUP.md)**  
**🔧 [Common Commands](COMMON_COMMANDS.md)**  
**📋 [Documentation Rules](DOCUMENTATION_RULES.md)**

## Table of Contents
- [Overview](#overview)
- [Automatic Detection](#automatic-detection)
- [Installation Commands](#installation-commands)
- [Supported Tools](#supported-tools)
- [Installation Methods](#installation-methods)
- [Platform Support](#platform-support)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Related Documentation](#related-documentation)

## Related Documentation
- **⚙️ [Environment Setup](ENVIRONMENT_SETUP.md)** - Development environment management
- **🔧 [Common Commands](COMMON_COMMANDS.md)** - Standard commands and workflows
- **📋 [Main README](../README.md)** - Project overview and installation

## 🎯 Overview

The Prerequisites Installer automatically detects and installs all required development tools for Python and JavaScript development. It supports multiple platforms and provides intelligent fallback options.

### ✅ **Automatically Detected Tools**
- **Python** - Python interpreter and pip
- **Node.js** - Node.js runtime and npm
- **Git** - Version control system
- **npm** - Node.js package manager
- **pip** - Python package manager

### 🤔 **Smart Detection**
- **System scan** - Detects installed tools and versions
- **Missing tools** - Identifies what needs to be installed
- **Version compatibility** - Checks for minimum required versions
- **Installation offers** - Suggests appropriate installation methods

## 🔍 Automatic Detection

### System Information Detection
```bash
# Detect all system information
womm system detect

# Output example:
🔍 System Detection Results:
  🖥️  OS: Windows 10 (64-bit)
  🐍  Python: 3.11.0 (✓ Installed)
  🟨  Node.js: 18.15.0 (✓ Installed)
  🔧  Git: 2.40.0 (✓ Installed)
  📦  npm: 9.5.0 (✓ Installed)
  📦  pip: 23.1.2 (✓ Installed)
```

### Missing Tools Detection
```bash
# Check for missing prerequisites
womm system check

# Output example:
❌ Missing tools detected:
  🐍  Python: Not found
  🟨  Node.js: Not found
  🔧  Git: Not found

💡 Run 'womm system install all' to install missing tools
```

## 🛠️ Installation Commands

### Install All Missing Tools
```bash
# Install all detected missing tools
womm system install all

# Interactive mode (recommended)
womm system install all --interactive
```

### Install Specific Tools
```bash
# Install individual tools
womm system install python
womm system install node
womm system install git
womm system install npm

# Install multiple tools
womm system install python node git npm
```

### Check Installation Status
```bash
# Check only (no installation)
womm system check

# Check with detailed information
womm system check --verbose
```

## 📦 Supported Tools

### 🐍 **Python**
- **Minimum version**: Python 3.8+
- **Installation methods**:
  - Official installer (Windows)
  - Package manager (Linux/macOS)
  - pyenv (cross-platform)
  - Microsoft Store (Windows)

### 🟨 **Node.js**
- **Minimum version**: Node.js 16+
- **Installation methods**:
  - Official installer (Windows/macOS)
  - Package manager (Linux)
  - nvm (cross-platform)
  - Microsoft Store (Windows)

### 🔧 **Git**
- **Minimum version**: Git 2.30+
- **Installation methods**:
  - Official installer (Windows/macOS)
  - Package manager (Linux)
  - Git for Windows (Windows)
  - Microsoft Store (Windows)

### 📦 **Package Managers**
- **npm** - Included with Node.js
- **pip** - Included with Python
- **Additional tools** - yarn, pnpm (optional)

## 🔄 Installation Methods

### 🖥️ **Windows Installation**

#### Automatic Installation
```bash
# Automatic detection and installation
womm system install all

# Uses best available method:
# 1. Microsoft Store (if available)
# 2. Official installers
# 3. Chocolatey (if installed)
# 4. Manual download links
```

#### Manual Installation Options
```bash
# Force specific installation method
womm system install python --method=store      # Microsoft Store
womm system install python --method=installer  # Official installer
womm system install python --method=choco      # Chocolatey
```

### 🐧 **Linux Installation**

#### Package Manager Detection
```bash
# Automatic package manager detection
womm system install all

# Detects and uses:
# - apt (Ubuntu/Debian)
# - yum (RHEL/CentOS)
# - dnf (Fedora)
# - pacman (Arch)
# - zypper (openSUSE)
```

#### Manual Package Manager
```bash
# Specify package manager
womm system install python --package-manager=apt
womm system install node --package-manager=snap
```

### 🍎 **macOS Installation**

#### Homebrew Integration
```bash
# Automatic Homebrew detection
womm system install all

# Uses Homebrew if available, otherwise:
# - Official installers
# - Package managers
```

#### Manual Installation
```bash
# Force Homebrew installation
womm system install python --method=brew
womm system install node --method=brew
```

## 🌐 Platform Support

### ✅ **Supported Operating Systems**
- **Windows**: 10, 11 (64-bit)
- **Linux**: Ubuntu, Debian, RHEL, CentOS, Fedora, Arch, openSUSE
- **macOS**: 10.15+ (Catalina and later)

### 🔧 **Supported Architectures**
- **x86_64**: Full support
- **ARM64**: Limited support (experimental)
- **ARM32**: Not supported

### 📦 **Package Manager Support**
- **Windows**: Microsoft Store, Chocolatey, Scoop
- **Linux**: apt, yum, dnf, pacman, zypper, snap
- **macOS**: Homebrew, MacPorts

## ✅ Verification

### Installation Verification
```bash
# Verify all installations
womm system verify

# Output example:
✅ Verification Results:
  🐍  Python: 3.11.0 ✓ (Minimum: 3.8)
  🟨  Node.js: 18.15.0 ✓ (Minimum: 16)
  🔧  Git: 2.40.0 ✓ (Minimum: 2.30)
  📦  npm: 9.5.0 ✓ (Included with Node.js)
  📦  pip: 23.1.2 ✓ (Included with Python)
```

### Version Compatibility Check
```bash
# Check version compatibility
womm system check-versions

# Output example:
🔍 Version Compatibility:
  🐍  Python: 3.11.0 ✓ (Compatible)
  🟨  Node.js: 18.15.0 ✓ (Compatible)
  🔧  Git: 2.40.0 ✓ (Compatible)
  ⚠️  npm: 9.5.0 ⚠️ (Update recommended)
```

## 🚨 Troubleshooting

### Common Installation Issues

#### Permission Errors
```bash
# Windows: Run as Administrator
# Linux/macOS: Use sudo
sudo womm system install python

# Alternative: User installation
womm system install python --user
```

#### Network Issues
```bash
# Offline mode (if tools already downloaded)
womm system install python --offline

# Use local mirrors
womm system install python --mirror=local
```

#### Python Not Found
```bash
# Check Python installation
python --version
python3 --version

# Alternative installation methods
womm system install python --method=pyenv
womm system install python --method=store
```

#### Node.js Not Found
```bash
# Check Node.js installation
node --version
npm --version

# Alternative installation methods
womm system install node --method=nvm
womm system install node --method=store
```

### Installation Conflicts

#### Multiple Python Versions
```bash
# Detect all Python installations
womm system detect python --all

# Use specific version
womm system use python --version=3.11
```

#### Multiple Node.js Versions
```bash
# Detect all Node.js installations
womm system detect node --all

# Use specific version
womm system use node --version=18.15.0
```

### Recovery Options

#### Rollback Installation
```bash
# Rollback last installation
womm system rollback

# Rollback specific tool
womm system rollback python
```

#### Clean Installation
```bash
# Remove and reinstall
womm system clean python
womm system install python
```

#### Manual Installation Guide
```bash
# Get manual installation instructions
womm system manual python
womm system manual node
womm system manual git
```

## 📈 Advanced Features

### Custom Installation Paths
```bash
# Install to custom location
womm system install python --path=/custom/python
womm system install node --path=/custom/node
```

### Proxy Configuration
```bash
# Use proxy for downloads
womm system install all --proxy=http://proxy:8080
womm system install all --proxy=https://proxy:8443
```

### Silent Installation
```bash
# Non-interactive installation
womm system install all --silent --accept-licenses
```

### Installation Logging
```bash
# Detailed installation logs
womm system install all --verbose --log-file=install.log
```

---

**🔧 This prerequisites installer ensures all required development tools are properly installed and configured for optimal development experience.**