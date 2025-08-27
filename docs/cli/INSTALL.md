# ⚙️ Installation Guide

[🏠 Main](../../README.md) > [📚 Documentation](../README.md) > [🔧 CLI Documentation](README.md) > [⚙️ Installation](INSTALL.md)

[← Back to CLI Documentation](README.md)

> **Complete guide to installing and uninstalling WOMM**  
> Install, configure, and manage WOMM across different platforms

## 📚 Documentation Navigation

**🏠 [Main Documentation](../../README.md)**  
**📚 [Documentation Index](../README.md)**  
**🔧 [CLI Documentation](README.md)**  
**⚙️ [Installation](INSTALL.md)** (You are here)  
**🔌 [API Documentation](../api/README.md)**

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🚀 Quick Installation](#-quick-installation)
- [🐍 Python Installation](#-python-installation)
- [📦 Package Managers](#-package-managers)
- [🔧 Configuration](#-configuration)
- [🗑️ Uninstallation](#️-uninstallation)
- [🔄 Updates](#-updates)
- [🔍 Troubleshooting](#-troubleshooting)

## 🎯 Overview

WOMM can be installed using various methods depending on your system and preferences. The installation process includes dependency management and system configuration.

### ✅ **Installation Methods**

- **pip** - Python package manager
- **conda** - Anaconda package manager
- **Source** - Direct from repository
- **Docker** - Containerized installation

### 🔄 **Installation Workflow**

```
System Check → Method Selection → Installation → Configuration → Verification
```

## 🚀 Quick Installation

### **Using pip (Recommended)**

```bash
# Install from PyPI
pip install works-on-my-machine

# Install with user flag
pip install --user works-on-my-machine

# Install specific version
pip install works-on-my-machine==2.6.8

# Install without environment refresh (Windows only)
pip install works-on-my-machine --no-refresh-env
```

### **Using conda**

```bash
# Install from conda-forge
conda install -c conda-forge works-on-my-machine

# Install in specific environment
conda install -n myenv -c conda-forge works-on-my-machine
```

### **From Source**

```bash
# Clone repository
git clone https://github.com/your-repo/works-on-my-machine.git
cd works-on-my-machine

# Install in development mode
pip install -e .
```

## 🐍 Python Installation

### **Prerequisites**

- Python 3.8 or higher
- pip package manager
- Git (for source installation)

### **System Requirements**

- **Windows**: Windows 10 or higher
- **macOS**: macOS 10.15 or higher
- **Linux**: Ubuntu 18.04+, CentOS 7+, or equivalent

### **Installation Steps**

```bash
# 1. Check Python version
python --version

# 2. Upgrade pip
pip install --upgrade pip

# 3. Install WOMM
pip install works-on-my-machine

# 4. Verify installation
womm --version
```

### **Virtual Environment Installation**

```bash
# Create virtual environment
python -m venv womm-env

# Activate environment
# Windows
womm-env\Scripts\activate
# macOS/Linux
source womm-env/bin/activate

# Install WOMM
pip install works-on-my-machine
```

## 📦 Package Managers

### **pip Installation**

```bash
# Basic installation
pip install works-on-my-machine

# Installation with extras
pip install works-on-my-machine[dev]

# Installation with specific dependencies
pip install works-on-my-machine[full]
```

### **conda Installation**

```bash
# Add conda-forge channel
conda config --add channels conda-forge

# Install WOMM
conda install works-on-my-machine

# Create environment with WOMM
conda create -n womm-env works-on-my-machine
```

### **Homebrew (macOS)**

```bash
# Install via Homebrew
brew install works-on-my-machine

# Update via Homebrew
brew upgrade works-on-my-machine
```

### **Chocolatey (Windows)**

```bash
# Install via Chocolatey
choco install works-on-my-machine

# Update via Chocolatey
choco upgrade works-on-my-machine
```

## 🔧 Configuration

### **Post-Installation Setup**

```bash
# Initialize WOMM configuration
womm init

# Configure global settings
womm config --global

# Set up development environment
womm setup --global
```

### **Configuration Files**

```bash
# Global configuration
~/.womm/config.yaml

# Project-specific configuration
./.womm/config.yaml

# User preferences
~/.womm/preferences.json
```

### **Environment Variables**

```bash
# Set WOMM home directory
export WOMM_HOME=~/.womm

# Enable debug mode
export WOMM_DEBUG=1

# Set log level
export WOMM_LOG_LEVEL=INFO
```

### **Path Configuration**

```bash
# Add WOMM to PATH (Windows)
set PATH=%PATH%;%USERPROFILE%\AppData\Local\Programs\Python\Scripts

# Add WOMM to PATH (macOS/Linux)
export PATH="$HOME/.local/bin:$PATH"
```

## 🔄 Environment Refresh (Windows)

### **Automatic Refresh**

WOMM automatically refreshes environment variables after installation on Windows using the `RefreshEnv.cmd` script. This ensures that PATH changes are immediately available without restarting the terminal.

### **Manual Refresh**

```bash
# Refresh environment variables manually
womm refresh-env

# Refresh with custom target directory
womm refresh-env --target /custom/path
```

### **Disable Automatic Refresh**

```bash
# Install without automatic environment refresh
womm install --no-refresh-env

# This is useful in automated environments or when manual control is preferred
```

## 🗑️ Uninstallation

### **pip Uninstallation**

```bash
# Remove WOMM
pip uninstall works-on-my-machine

# Remove with dependencies
pip uninstall works-on-my-machine --yes

# Clean up cache
pip cache purge
```

### **conda Uninstallation**

```bash
# Remove from current environment
conda remove works-on-my-machine

# Remove from specific environment
conda remove -n myenv works-on-my-machine

# Remove environment entirely
conda env remove -n womm-env
```

### **Complete Cleanup**

```bash
# Remove configuration files
rm -rf ~/.womm

# Remove cache
rm -rf ~/.cache/womm

# Remove logs
rm -rf ~/.womm/logs
```

### **System-Specific Cleanup**

```bash
# Windows cleanup
rmdir /s /q "%USERPROFILE%\.womm"

# macOS cleanup
rm -rf ~/.womm

# Linux cleanup
rm -rf ~/.womm
```

## 🔄 Updates

### **Check for Updates**

```bash
# Check current version
womm --version

# Check for updates
womm update --check

# List available versions
pip index versions works-on-my-machine
```

### **Update WOMM**

```bash
# Update via pip
pip install --upgrade works-on-my-machine

# Update via conda
conda update works-on-my-machine

# Update from source
git pull origin main
pip install -e .
```

### **Automatic Updates**

```bash
# Enable auto-updates
womm config --set auto-update true

# Check update schedule
womm config --get update-schedule

# Run update check
womm update --auto
```

## 🔍 Troubleshooting

### **Installation Issues**

**Permission errors:**

```bash
# Use user installation
pip install --user works-on-my-machine

# Fix permissions
sudo chown -R $USER:$USER ~/.local

# Use virtual environment
python -m venv womm-env
source womm-env/bin/activate
pip install works-on-my-machine
```

**Network issues:**

```bash
# Use alternative index
pip install -i https://pypi.org/simple/ works-on-my-machine

# Use proxy
pip install --proxy http://proxy:port works-on-my-machine

# Offline installation
pip download works-on-my-machine
pip install works-on-my-machine-*.whl
```

**Dependency conflicts:**

```bash
# Check conflicts
pip check works-on-my-machine

# Install with --no-deps
pip install --no-deps works-on-my-machine

# Use isolated environment
python -m venv womm-isolated
source womm-isolated/bin/activate
pip install works-on-my-machine
```

### **Configuration Issues**

**Path not found:**

```bash
# Check installation location
pip show works-on-my-machine

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Create symlink
ln -s ~/.local/bin/womm /usr/local/bin/womm
```

**Configuration errors:**

```bash
# Reset configuration
womm config --reset

# Validate configuration
womm config --validate

# Create default config
womm config --init
```

### **Runtime Issues**

**Import errors:**

```bash
# Check Python environment
python -c "import womm"

# Reinstall dependencies
pip install --force-reinstall works-on-my-machine

# Check Python version compatibility
python --version
```

**Command not found:**

```bash
# Check installation
which womm

# Reinstall
pip uninstall works-on-my-machine
pip install works-on-my-machine

# Check PATH
echo $PATH
```

### **Debug Mode**

Enable verbose output for troubleshooting:

```bash
# Set debug environment variable
export WOMM_DEBUG=1

# Run with debug output
womm --debug

# Check logs
cat ~/.womm/logs/install.log
```

### **Log Files**

WOMM creates detailed logs for troubleshooting:

```bash
# View installation logs
cat ~/.womm/logs/install.log

# View error logs
cat ~/.womm/logs/errors.log

# View configuration logs
cat ~/.womm/logs/config.log
```

---

**⚙️ This installation guide provides comprehensive instructions for installing, configuring, and managing WOMM across different platforms and environments.**
